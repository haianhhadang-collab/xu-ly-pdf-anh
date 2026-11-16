"""Tài liệu để sửa: các trang lấy từ PDF có sẵn, ảnh, hoặc trang trắng; chèn, xóa, xoay, đảo thứ tự,
gộp nhiều tệp, tách trang ra tệp mới; sửa nội dung từng trang (sua_noi_dung) rồi lưu PDF.

Trang PDF chưa sửa nội dung được chép nguyên vào tệp mới (giữ chữ, hình vẽ, lớp chữ, chất lượng);
xoay chỉ đổi thuộc tính /Rotate. Trang đã sửa nội dung được dựng thành ảnh 300 dpi, áp các thao tác rồi
ghi lại thành trang ảnh cùng khổ, có thể thêm lớp chữ ẩn. Siêu dữ liệu PDF ghi rõ tệp đã chỉnh sửa nội dung.
Không dùng MuPDF (AGPL): đọc, dựng trang bằng PDFium, ghép bằng pypdf, ghi trang ảnh bằng reportlab.
"""
from __future__ import annotations

import copy
import io
import os
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from . import chu_thich as ct_, doc_ghi, nhan_dang
from .nan_phang import xoay_90
from .sua_noi_dung import ChenAnh, Che, SuaChu, ThemChu, ToSang, ap_tat_ca

DPI_SUA = 300  # độ phân giải dựng trang PDF để sửa nội dung; tọa độ thao tác tính theo ảnh này
A4 = doc_ghi.KHO_GIAY["a4"]


@dataclass(eq=False)
class TrangSua:
    loai: str                                   # pdf | anh | trang
    ten: str = ""
    tep: str | None = None                      # loai pdf: tệp nguồn
    so: int = 0                                 # loai pdf: thứ tự trang trong tệp (từ 0)
    anh: bytes | None = None                    # loai anh: ảnh gốc đã mã hóa
    kho_pt: tuple[float, float] = A4            # khổ trang khi đứng thẳng (chưa tính xoay thêm), điểm
    xoay: int = 0                               # xoay thêm cùng chiều kim đồng hồ
    dpi: float = DPI_SUA                        # độ phân giải dựng trang để sửa (trang ảnh scan: đúng độ phân giải ảnh)
    vi_tri_anh: tuple | None = None             # trang chỉ gồm một ảnh: chỗ đặt ảnh (trái, dưới, phải, trên, điểm)
    thao_tac: list = field(default_factory=list)
    da_gop: list = field(default_factory=list)  # tên các thao tác đã gộp vào ảnh (khi xoay trang đã sửa)
    _nen: np.ndarray | None = field(default=None, repr=False)  # ảnh nền đã dựng (chưa áp thao tác)

    @property
    def da_sua(self) -> bool:
        """Đã sửa nội dung trang (chú thích không tính: chúng không đụng vào trang)."""
        return any(not ct_.la_chu_thich(x) for x in self.thao_tac)

    @property
    def chu_thich(self) -> list:
        return [x for x in self.thao_tac if ct_.la_chu_thich(x)]

    @property
    def kho_ra(self) -> tuple[float, float]:
        w, h = self.kho_pt
        return (h, w) if self.xoay % 180 else (w, h)


class TaiLieu:
    def __init__(self):
        self.trang: list[TrangSua] = []

    # ------------------------------------------------------------ thêm trang
    def mo_tep(self, duong_dan, vi_tri: int | None = None) -> int:
        """Thêm mọi trang của một PDF hoặc ảnh (kể cả TIFF nhiều trang) vào vị trí `vi_tri` (mặc định cuối)."""
        p = Path(duong_dan)
        moi = []
        if p.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            doc = PdfReader(str(p))
            if doc.is_encrypted:
                raise ValueError(f"{p.name} có mật khẩu; hãy bỏ mật khẩu trước khi sửa.")
            for i, pg in enumerate(doc.pages):
                w, h = float(pg.mediabox.width), float(pg.mediabox.height)
                if (pg.rotation or 0) % 180:
                    w, h = h, w
                moi.append(TrangSua("pdf", f"{p.name} – {i + 1}", str(p), i, kho_pt=(w, h), dpi=_dpi_anh_trang(pg, w, h)))
        else:
            for ten, anh in doc_ghi.doc_tep(p):
                moi.append(self._trang_anh(anh, ten))
        vi_tri = len(self.trang) if vi_tri is None else vi_tri
        self.trang[vi_tri:vi_tri] = moi
        return len(moi)

    @staticmethod
    def _trang_anh(anh: np.ndarray, ten: str) -> TrangSua:
        h, w = anh.shape[:2]
        return TrangSua("anh", ten, anh=doc_ghi.ma_hoa(anh, 95), kho_pt=doc_ghi.kich_thuoc_trang("a4", w, h))

    def them_anh(self, anh: np.ndarray, ten: str, vi_tri: int | None = None) -> None:
        self.trang.insert(len(self.trang) if vi_tri is None else vi_tri, self._trang_anh(anh, ten))

    def them_trang_trang(self, vi_tri: int | None = None, kho_pt: tuple[float, float] = A4) -> None:
        self.trang.insert(len(self.trang) if vi_tri is None else vi_tri, TrangSua("trang", "Trang trắng", kho_pt=kho_pt))

    # ------------------------------------------------------------ thao tác trang
    def xoa(self, chi_so: list[int]) -> None:
        for i in sorted(set(chi_so), reverse=True):
            del self.trang[i]

    def doi_cho(self, tu: int, den: int) -> None:
        self.trang.insert(den, self.trang.pop(tu))

    def di_chuyen(self, chi_so: list[int], den: int) -> list[int]:
        """Kéo thả: đưa các trang `chi_so` (giữ thứ tự) tới trước trang đang ở vị trí `den` (len = cuối).
        Trả vị trí mới của chúng."""
        chi_so = sorted(set(chi_so))
        dem = [self.trang[i] for i in chi_so]
        con = [t for i, t in enumerate(self.trang) if i not in set(chi_so)]
        vt = den - sum(1 for i in chi_so if i < den)
        self.trang = con[:vt] + dem + con[vt:]
        return list(range(vt, vt + len(dem)))

    def chep(self, chi_so: list[int]) -> list[TrangSua]:
        """Bản sao độc lập của các trang (kể cả thao tác sửa, chú thích) để dán vào chỗ khác, tệp khác."""
        return [copy.deepcopy(self.trang[i]) for i in sorted(set(chi_so))]

    def dan(self, cac_trang: list[TrangSua], vi_tri: int) -> list[int]:
        moi = [copy.deepcopy(t) for t in cac_trang]  # dán nhiều lần không dùng chung một trang
        self.trang[vi_tri:vi_tri] = moi
        return list(range(vi_tri, vi_tri + len(moi)))

    def xoay(self, i: int, goc: int) -> None:
        """Xoay trang. Trang đã sửa nội dung: gộp các thao tác vào ảnh rồi xoay ảnh (tọa độ thao tác theo ảnh cũ)."""
        t = self.trang[i]
        goc %= 360
        if not goc:
            return
        cac_ct = t.chu_thich
        if cac_ct:
            h0, w0 = self.anh_nen(i).shape[:2]
        if t.da_sua:
            anh = xoay_90(self.anh_trang(i, chu_thich=False), goc)
            w, h = t.kho_ra
            # giữ dấu vết đã sửa nội dung để ghi siêu dữ liệu; chú thích vẫn là chú thích
            self.trang[i] = TrangSua("anh", t.ten, anh=doc_ghi.ma_hoa(anh, 95), kho_pt=(h, w) if goc % 180 else (w, h),
                                     da_gop=t.da_gop + [type(x).__name__ for x in t.thao_tac if not ct_.la_chu_thich(x)],
                                     thao_tac=cac_ct)
        else:
            t.xoay = (t.xoay + goc) % 360
            t._nen = None
        if cac_ct:  # đổi tọa độ chú thích theo ảnh trang mới (đã xoay, có thể khác độ phân giải)
            h1, w1 = self.anh_nen(i).shape[:2]
            ww, hh = (h0, w0) if goc % 180 else (w0, h0)

            def fn(u, v):
                a, b = ct_.xoay_diem(u, v, goc, w0, h0)
                return a * w1 / ww, b * h1 / hh
            for c in cac_ct:
                c.bien_doi(fn)

    # ------------------------------------------------------------ dựng ảnh
    def anh_nen(self, i: int) -> np.ndarray:
        """Ảnh trang (đã xoay) ở DPI_SUA, chưa áp thao tác; là hệ tọa độ của các thao tác sửa nội dung."""
        t = self.trang[i]
        if t._nen is None:
            if t.loai == "pdf":
                import pypdfium2 as pdfium
                doc = pdfium.PdfDocument(t.tep)
                try:
                    anh = None
                    if not t.xoay and not doc[t.so].get_rotation():
                        # trang bản scan, ảnh chụp (một ảnh phủ gần kín trang): lấy thẳng ảnh gốc, đúng từng điểm ảnh,
                        # nhớ chỗ đặt để khi lưu đặt lại đúng chỗ
                        pg = doc[t.so]
                        cac_anh = [o for o in pg.get_objects() if type(o).__name__ == "PdfImage"]
                        if len(cac_anh) == 1:
                            l, b, r, tr = cac_anh[0].get_bounds()
                            w, h = pg.get_size()
                            if (r - l) * (tr - b) >= 0.8 * w * h:
                                anh = doc_ghi.pil_sang_bgr(cac_anh[0].get_bitmap(render=False).to_pil())
                                t.vi_tri_anh = (l, b, r, tr)
                    if anh is None:
                        t.vi_tri_anh = None
                        anh = doc_ghi.pil_sang_bgr(doc[t.so].render(scale=t.dpi / 72, rotation=t.xoay).to_pil())
                finally:
                    doc.close()
            elif t.loai == "anh":
                anh = xoay_90(doc_ghi.giai_ma(t.anh), t.xoay)
            else:
                w, h = t.kho_ra
                anh = np.full((round(h / 72 * DPI_SUA), round(w / 72 * DPI_SUA), 3), 255, np.uint8)
            t._nen = anh
        return t._nen

    def anh_trang(self, i: int, chu_thich: bool = True) -> np.ndarray:
        """Ảnh trang đã áp các thao tác sửa; `chu_thich`: vẽ chồng chú thích (để xem; khi lưu chúng ghi riêng)."""
        t = self.trang[i]
        anh = ap_tat_ca(self.anh_nen(i), [x for x in t.thao_tac if not ct_.la_chu_thich(x)])
        return ct_.phu_len(anh, t.thao_tac) if chu_thich else anh

    def anh_nho(self, i: int, canh: int = 160) -> np.ndarray:
        t = self.trang[i]
        if t.loai == "pdf" and not t.thao_tac and t._nen is None:
            import pypdfium2 as pdfium
            doc = pdfium.PdfDocument(t.tep)
            try:
                pg = doc[t.so]
                s = canh / max(pg.get_size())
                return doc_ghi.pil_sang_bgr(pg.render(scale=s, rotation=t.xoay).to_pil())
            finally:
                doc.close()
        anh = self.anh_trang(i)
        s = canh / max(anh.shape[:2])
        return cv2.resize(anh, (max(1, round(anh.shape[1] * s)), max(1, round(anh.shape[0] * s))), interpolation=cv2.INTER_AREA)

    # ------------------------------------------------------------ lưu
    def tom_tat_sua(self, chi_so=None) -> str:
        dem = {}
        for i in (range(len(self.trang)) if chi_so is None else chi_so):
            t = self.trang[i]
            for ten in [type(x).__name__ for x in t.thao_tac if not ct_.la_chu_thich(x)] + t.da_gop:
                dem[ten] = dem.get(ten, 0) + 1
        ten_vn = {"SuaDong": "sửa ký tự", "SuaChu": "sửa chữ", "SuaKhoi": "viết lại khối chữ", "ThemChu": "thêm chữ",
                  "Che": "che", "ToSang": "tô sáng", "ChenAnh": "chèn ảnh",
                  "HinhVe": "vẽ hình", "DoiVung": "dời, xóa vùng"}
        return ", ".join(f"{n} chỗ {ten_vn.get(k, k)}" for k, n in dem.items())

    def luu(self, duong_dan, chi_so: list[int] | None = None, ocr: bool = True, ngon_ngu: str = "vie",
            bao_tien_trinh=None) -> None:
        """Ghi các trang (mặc định tất cả, theo thứ tự hiện tại) ra PDF.
        `ocr`: thêm lớp chữ ẩn cho trang dựng thành ảnh (trang sửa nội dung, trang ảnh)."""
        from pypdf import PdfReader, PdfWriter
        chi_so = list(range(len(self.trang))) if chi_so is None else list(chi_so)
        if not chi_so:
            raise ValueError("Không có trang nào để lưu")
        bao = bao_tien_trinh or (lambda *_: None)
        ocr = ocr and nhan_dang.CO_TESSERACT
        viet = PdfWriter()
        doc_mo: dict[str, PdfReader] = {}
        tieu_de = None
        so_ct = 0
        for k, i in enumerate(chi_so):
            t = self.trang[i]
            bao(k, len(chi_so), f"Ghi trang {k + 1}/{len(chi_so)}")
            if t.loai == "pdf" and not t.da_sua:
                if t.tep not in doc_mo:  # đọc hết vào bộ nhớ: lưu đè lên chính tệp nguồn vẫn được
                    doc_mo[t.tep] = PdfReader(io.BytesIO(Path(t.tep).read_bytes()))
                doc = doc_mo[t.tep]
                tieu_de = tieu_de or (doc.metadata or {}).get("/Title")
                pg = viet.add_page(doc.pages[t.so])
                if t.xoay:
                    pg.rotate(t.xoay)
            elif t.loai == "trang" and not t.da_sua:
                pg = viet.add_blank_page(*t.kho_ra)
            else:
                pg = viet.add_page(PdfReader(io.BytesIO(_pdf_trang_anh(self.anh_trang(i, chu_thich=False), t.kho_ra, ocr,
                                                                       ngon_ngu, t.vi_tri_anh))).pages[0])
            if t.chu_thich:
                so_ct += ct_.ghi_vao_trang(viet, pg, t.chu_thich, *self._toa_do_pdf(i, pg))
        tt = {"/Title": tieu_de or Path(duong_dan).stem, "/Producer": "Xử lý PDF ảnh (nguyên mẫu) – sửa PDF"}
        sua = self.tom_tat_sua(chi_so)
        if sua:  # chống lợi dụng sửa giấy tờ: ghi rõ đã chỉnh sửa nội dung
            tt["/Subject"] = f"Đã chỉnh sửa nội dung bằng Xử lý PDF ảnh: {sua}"
            tt["/XuLyPdfAnhDaSua"] = sua
        if so_ct:
            tt["/XuLyPdfAnhChuThich"] = f"{so_ct} chú thích (không sửa nội dung trang)"
        viet.add_metadata(tt)
        tam = Path(str(duong_dan) + ".dang-ghi")
        with open(tam, "wb") as f:
            viet.write(f)
        os.replace(tam, duong_dan)
        bao(len(chi_so), len(chi_so), "Xong")

    def _toa_do_pdf(self, i: int, pg):
        """Đổi điểm ảnh của ảnh trang `i` sang điểm PDF của trang đã ghi `pg`: trả (f, R, s) với f(u, v) → (x, y)
        trong hệ tọa độ trang chưa xoay, R góc /Rotate của trang, s số điểm PDF ứng với một điểm ảnh."""
        t = self.trang[i]
        h, w = self.anh_nen(i).shape[:2]
        if t.vi_tri_anh or t.da_sua or t.loai != "pdf":  # ảnh đặt đúng chỗ cũ, hoặc phủ kín trang mới (giữ tỉ lệ)
            x0, y0, dw, dh = _cho_dat(w, h, t.kho_ra, t.vi_tri_anh)
            return (lambda u, v: (x0 + u * dw / w, y0 + dh - v * dh / h)), 0, dw / w
        R = (pg.rotation or 0) % 360
        hop = pg.cropbox
        mx, my, w0, h0 = float(hop.left), float(hop.bottom), float(hop.width), float(hop.height)
        sx = (w0 if R % 180 == 0 else h0) / w
        sy = (h0 if R % 180 == 0 else w0) / h

        def f(u, v):
            U, V = u * sx, v * sy
            x, y = {0: (U, h0 - V), 90: (V, U), 180: (w0 - U, V), 270: (w0 - V, h0 - U)}[R]
            return mx + x, my + y
        return f, R, (sx + sy) / 2


def _cho_dat(w: int, h: int, kho_pt, vi_tri=None):
    """Chỗ đặt ảnh rộng w, cao h trên trang khổ `kho_pt`: (trái, dưới, rộng, cao) điểm PDF."""
    if vi_tri:
        return vi_tri[0], vi_tri[1], vi_tri[2] - vi_tri[0], vi_tri[3] - vi_tri[1]
    pw, ph = kho_pt
    s = min(pw / w, ph / h)
    return (pw - w * s) / 2, (ph - h * s) / 2, w * s, h * s


def _dpi_anh_trang(pg, w_pt: float, h_pt: float) -> float:
    """Trang PDF chỉ gồm một ảnh (bản scan, ảnh chụp): dựng đúng độ phân giải của ảnh để sửa không phóng ảnh lên
    (giữ nguyên hình chữ, tệp không phình); trang khác dựng DPI_SUA."""
    try:
        xo = pg["/Resources"]["/XObject"]
        anh = [xo[k].get_object() for k in xo if xo[k].get_object().get("/Subtype") == "/Image"]
        if len(anh) == 1:
            dai = max(int(anh[0]["/Width"]), int(anh[0]["/Height"]))
            return float(np.clip(dai / (max(w_pt, h_pt) / 72), 100, DPI_SUA))
    except Exception:
        pass
    return DPI_SUA


def _pdf_trang_anh(anh: np.ndarray, kho_pt: tuple[float, float], ocr: bool, ngon_ngu: str, vi_tri=None) -> bytes:
    """Một trang PDF khổ `kho_pt` phủ kín bằng ảnh (giữ tỉ lệ, căn giữa), hoặc đặt ảnh đúng `vi_tri`
    (trái, dưới, phải, trên) như trang gốc; có thể kèm lớp chữ ẩn."""
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    pw, ph = kho_pt
    h, w = anh.shape[:2]
    x0, y0, dw, dh = _cho_dat(w, h, kho_pt, vi_tri)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(pw, ph))
    c.drawImage(ImageReader(io.BytesIO(doc_ghi.ma_hoa(anh, 90))), x0, y0, dw, dh)
    c.showPage()
    c.save()
    if not ocr:
        return buf.getvalue()
    from pypdf import PdfReader, PdfWriter, Transformation
    viet = PdfWriter(clone_from=PdfReader(io.BytesIO(buf.getvalue())))
    lop = PdfReader(io.BytesIO(nhan_dang.lop_chu_pdf(anh, nhan_dang.chon_ngon_ngu(ngon_ngu), w / (dw / 72)))).pages[0]
    tw, th = float(lop.mediabox.width), float(lop.mediabox.height)
    viet.pages[0].merge_transformed_page(lop, Transformation().scale(dw / tw, dh / th).translate(x0, y0))
    ra = io.BytesIO()
    viet.write(ra)
    return ra.getvalue()


__all__ = ["TaiLieu", "TrangSua", "DPI_SUA", "SuaChu", "ThemChu", "Che", "ToSang", "ChenAnh"]
