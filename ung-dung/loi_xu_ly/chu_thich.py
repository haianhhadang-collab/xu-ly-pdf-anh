"""Chú thích không phá bản gốc: ghi chú, bút phê, tô sáng, hình (chữ nhật, elip, đường, mũi tên), dấu "ĐÃ XEM".

Chú thích nằm trong danh sách thao tác của trang (để chọn, dời, hoàn tác như đối tượng khác) nhưng không đụng vào ảnh
trang: khi lưu, trang PDF chưa sửa nội dung vẫn được chép nguyên, chú thích ghi thành chú thích PDF chuẩn (/Annots: Text,
FreeText, Highlight, Square, Circle, Line, Stamp) có hình hiển thị (/AP) vẽ bằng reportlab, nhúng phông tiếng Việt;
trình đọc PDF khác (Acrobat, Foxit, trình duyệt) hiện, ẩn, sửa, xóa được. Siêu dữ liệu không ghi "đã sửa nội dung" vì
nội dung trang không đổi. Trên màn hình, chú thích được vẽ chồng lên ảnh trang bằng chính hình hiển thị ấy (dựng bằng
PDFium) nên thấy sao lưu vậy. Cách làm tham khảo ONLYOFFICE (không dùng mã của họ).

Tọa độ: điểm ảnh của ảnh trang đang sửa (TaiLieu.anh_nen), như các thao tác khác.
"""
from __future__ import annotations

import datetime as _dt
import io
import uuid
from dataclasses import dataclass, field

import numpy as np

Hop = tuple[int, int, int, int]
TAC_GIA = "Xử lý PDF ảnh"
DO = (30, 30, 210)       # BGR
VANG = (0, 225, 255)

_PHONG = {"thuong": "times.ttf", "dam": "timesbd.ttf", "nghieng": "timesi.ttf"}
_DA_DANG_KY: set = set()


def _phong(kieu: str = "thuong") -> str:
    """Tên phông reportlab (Times New Roman của Windows, nhúng tập con vào PDF: đủ dấu tiếng Việt)."""
    ten = "XLPA-Times-" + kieu
    if ten not in _DA_DANG_KY:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        try:
            pdfmetrics.registerFont(TTFont(ten, "C:/Windows/Fonts/" + _PHONG[kieu]))
        except Exception:  # máy không có Times New Roman: dùng phông DejaVu đi kèm reportlab? không có thì Helvetica
            return {"thuong": "Helvetica", "dam": "Helvetica-Bold", "nghieng": "Helvetica-Oblique"}[kieu]
        _DA_DANG_KY.add(ten)
    return ten


def _rgb(mau):
    b, g, r = mau
    return r / 255, g / 255, b / 255


def _chuan(h) -> Hop:
    return int(min(h[0], h[2])), int(min(h[1], h[3])), int(max(h[0], h[2])), int(max(h[1], h[3]))


# ---------------------------------------------------------------------------------------------- các loại chú thích
@dataclass(eq=False)
class ChuThich:
    hop: Hop
    mau: tuple = DO
    noi_dung: str = ""
    ma: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    luc: str = field(default_factory=lambda: _dt.datetime.now().strftime("D:%Y%m%d%H%M%S"))

    ten = "Chú thích"
    loai_pdf = "/Text"
    doi_co = True        # kéo ô góc đổi cỡ được

    # --- như các đối tượng khác (doi_tuong.py)
    def khung(self) -> Hop:
        return self.hop

    def doi(self, dx, dy):
        x0, y0, x1, y1 = self.hop
        self.hop = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)

    def dat_khung(self, moi):
        if self.doi_co:
            self.hop = _chuan(moi)
        else:
            self.doi(moi[0] - self.hop[0], moi[1] - self.hop[1])

    def bien_doi(self, fn):
        """Đổi tọa độ theo hàm điểm → điểm (khi xoay trang, đổi độ phân giải ảnh trang)."""
        x0, y0, x1, y1 = self.hop
        a = fn(x0, y0)
        b = fn(x1, y1) if self.doi_co else (a[0] + x1 - x0, a[1] + y1 - y0)  # biểu tượng giữ cỡ, chỉ dời
        self.hop = _chuan((a[0], a[1], b[0], b[1]))

    def mo_ta(self) -> str:
        nd = self.noi_dung.replace("\n", " ")
        return f"Chú thích – {self.ten}" + (f": “{nd[:30]}{'…' if len(nd) > 30 else ''}”" if nd else "")

    # thao tác: không đổi ảnh trang (chú thích vẽ chồng riêng khi hiện, ghi riêng khi lưu)
    def ap(self, anh: np.ndarray) -> np.ndarray:
        return anh

    # --- hình hiển thị: vẽ trong khung (0, 0, rộng, cao) đơn vị = điểm ảnh × s, gốc ở góc dưới trái
    def ve(self, c, W: float, H: float, s: float):
        raise NotImplementedError

    def them_pdf(self, d: dict, f, s: float):
        """Thêm khóa riêng của loại chú thích vào từ điển /Annot (f: điểm ảnh → điểm PDF)."""


def xoay_diem(u, v, goc, w, h):
    """Điểm (u, v) của ảnh rộng w, cao h sau khi ảnh xoay `goc` độ cùng chiều kim đồng hồ."""
    goc %= 360
    if goc == 90:
        return h - v, u
    if goc == 180:
        return w - u, h - v
    if goc == 270:
        return v, w - u
    return u, v


@dataclass(eq=False)
class GhiChu(ChuThich):
    """Ghi chú dán (biểu tượng tờ giấy nhỏ; bấm vào trong trình đọc PDF thì hiện nội dung)."""
    mau: tuple = VANG
    ten = "Ghi chú"
    loai_pdf = "/Text"
    doi_co = False

    def ve(self, c, W, H, s):
        c.setFillColorRGB(*_rgb(self.mau))
        c.setStrokeColorRGB(0.45, 0.35, 0.0)
        c.setLineWidth(max(0.5, W / 24))
        c.roundRect(W * 0.06, H * 0.06, W * 0.88, H * 0.88, W * 0.12, stroke=1, fill=1)
        c.setLineWidth(max(0.4, W / 30))
        for k in (0.68, 0.5, 0.32):
            c.line(W * 0.22, H * k, W * 0.78, H * k)

    def them_pdf(self, d, f, s):
        from pypdf.generic import BooleanObject, NameObject
        d[NameObject("/Name")] = NameObject("/Comment")
        d[NameObject("/Open")] = BooleanObject(False)


@dataclass(eq=False)
class ButPhe(ChuThich):
    """Bút phê: chữ nghiêng màu (mặc định đỏ) đặt thẳng trên trang, tự xuống dòng theo bề rộng khung."""
    co_px: float = 40.0
    ten = "Bút phê"
    loai_pdf = "/FreeText"

    def _dong(self, W, s):
        from reportlab.lib.utils import simpleSplit
        kq = []
        for doan in self.noi_dung.split("\n"):
            kq += simpleSplit(doan, _phong("nghieng"), self.co_px * s, W) or [""]
        return kq

    def ve(self, c, W, H, s):
        co = self.co_px * s
        c.setFillColorRGB(*_rgb(self.mau))
        c.setFont(_phong("nghieng"), co)
        y = H - co * 0.95
        for dong in self._dong(W, s):
            c.drawString(co * 0.1, y, dong)
            y -= co * 1.2

    def chieu_cao_vua(self) -> int:
        """Chiều cao khung (điểm ảnh) vừa đủ chứa hết chữ với bề rộng hiện tại."""
        n = len(self._dong(self.hop[2] - self.hop[0], 1.0))
        return int(self.co_px * (1.2 * n + 0.3))

    def them_pdf(self, d, f, s):
        from pypdf.generic import NameObject, TextStringObject
        r, g, b = _rgb(self.mau)
        d[NameObject("/DA")] = TextStringObject(f"/Helv {self.co_px * s:.1f} Tf {r:.3f} {g:.3f} {b:.3f} rg")


@dataclass(eq=False)
class ToSangCT(ChuThich):
    """Tô sáng dạng chú thích (Highlight): không đổi ảnh trang, bỏ được trong trình đọc PDF."""
    mau: tuple = VANG
    ten = "Tô sáng"
    loai_pdf = "/Highlight"

    def ve(self, c, W, H, s):
        c.setFillColorRGB(*_rgb(self.mau))
        c.setFillAlpha(0.38)
        c.rect(0, 0, W, H, stroke=0, fill=1)

    def them_pdf(self, d, f, s):
        from pypdf.generic import ArrayObject, FloatObject, NameObject
        x0, y0, x1, y1 = self.hop
        q = []
        for u, v in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):  # trên trái, trên phải, dưới trái, dưới phải
            q += f(u, v)
        d[NameObject("/QuadPoints")] = ArrayObject(FloatObject(round(v, 3)) for v in q)


@dataclass(eq=False)
class HinhCT(ChuThich):
    """Hình dạng chú thích: chữ nhật (Square), elip (Circle), đường, mũi tên (Line). `diem` giữ chiều vẽ."""
    loai: str = "chu_nhat"
    diem: tuple = (0, 0, 0, 0)
    day: int = 3
    ten = "Hình"

    def __post_init__(self):
        if self.diem == (0, 0, 0, 0):
            self.diem = tuple(self.hop)
        self._cap_nhat_hop()

    def _cap_nhat_hop(self):
        x0, y0, x1, y1 = self.diem
        le = self.day + (self.day * 3 + 6 if self.loai == "mui_ten" else 2)
        self.hop = (int(min(x0, x1) - le), int(min(y0, y1) - le), int(max(x0, x1) + le), int(max(y0, y1) + le))

    @property
    def loai_pdf(self):
        return {"chu_nhat": "/Square", "elip": "/Circle"}.get(self.loai, "/Line")

    def mo_ta(self):
        from .doi_tuong import TEN_HINH
        return f"Chú thích – {TEN_HINH.get(self.loai, self.loai)}" + (f": “{self.noi_dung[:30]}”" if self.noi_dung else "")

    def doi(self, dx, dy):
        x0, y0, x1, y1 = self.diem
        self.diem = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)
        self._cap_nhat_hop()

    def dat_khung(self, moi):
        moi = _chuan(moi)
        cu = self.hop
        sx = (moi[2] - moi[0]) / max(1, cu[2] - cu[0])
        sy = (moi[3] - moi[1]) / max(1, cu[3] - cu[1])
        p0, q0, p1, q1 = self.diem
        self.diem = tuple(int(round(v)) for v in (moi[0] + (p0 - cu[0]) * sx, moi[1] + (q0 - cu[1]) * sy,
                                                  moi[0] + (p1 - cu[0]) * sx, moi[1] + (q1 - cu[1]) * sy))
        self._cap_nhat_hop()

    def bien_doi(self, fn):
        x0, y0, x1, y1 = self.diem
        a, b = fn(x0, y0), fn(x1, y1)
        self.diem = tuple(int(round(v)) for v in (a[0], a[1], b[0], b[1]))
        self._cap_nhat_hop()

    def _dia_phuong(self, s):
        """Hai đầu mút trong hệ tọa độ của khung hình hiển thị."""
        x0, y0, x1, y1 = self.diem
        u0, _, _, v1 = self.hop
        return (x0 - u0) * s, (v1 - y0) * s, (x1 - u0) * s, (v1 - y1) * s

    def ve(self, c, W, H, s):
        c.setStrokeColorRGB(*_rgb(self.mau))
        c.setFillColorRGB(*_rgb(self.mau))
        c.setLineWidth(self.day * s)
        c.setLineCap(1)
        c.setLineJoin(1)
        a0, b0, a1, b1 = self._dia_phuong(s)
        if self.loai == "chu_nhat":
            c.rect(min(a0, a1), min(b0, b1), abs(a1 - a0), abs(b1 - b0), stroke=1, fill=0)
        elif self.loai == "elip":
            c.ellipse(a0, b0, a1, b1, stroke=1, fill=0)
        else:
            c.line(a0, b0, a1, b1)
            if self.loai == "mui_ten":
                import math
                goc = math.atan2(b1 - b0, a1 - a0)
                dai = (self.day * 3 + 6) * s
                for lech in (2.7, -2.7):
                    c.line(a1, b1, a1 + dai * math.cos(goc + lech), b1 + dai * math.sin(goc + lech))

    def them_pdf(self, d, f, s):
        from pypdf.generic import ArrayObject, DictionaryObject, FloatObject, NameObject
        d[NameObject("/BS")] = DictionaryObject({NameObject("/W"): FloatObject(round(self.day * s, 2))})
        if self.loai in ("duong", "mui_ten"):
            x0, y0, x1, y1 = self.diem
            d[NameObject("/L")] = ArrayObject(FloatObject(round(v, 3)) for v in (*f(x0, y0), *f(x1, y1)))
            d[NameObject("/LE")] = ArrayObject([NameObject("/None"),
                                                NameObject("/OpenArrow" if self.loai == "mui_ten" else "/None")])


@dataclass(eq=False)
class DauCT(ChuThich):
    """Dấu "ĐÃ XEM" (Stamp): khung bo tròn, chữ đậm, ngày xem; kéo góc để đổi cỡ."""
    chu: str = "ĐÃ XEM"
    ngay: str = field(default_factory=lambda: _dt.date.today().strftime("%d/%m/%Y"))
    ten = "Dấu đã xem"
    loai_pdf = "/Stamp"

    def mo_ta(self):
        return f"Chú thích – dấu “{self.chu}” {self.ngay}"

    def ve(self, c, W, H, s):
        c.setStrokeColorRGB(*_rgb(self.mau))
        c.setFillColorRGB(*_rgb(self.mau))
        day = max(1.0, H * 0.05)
        c.setLineWidth(day)
        c.roundRect(day, day, W - 2 * day, H - 2 * day, H * 0.15, stroke=1, fill=0)
        co = H * 0.36
        dam = _phong("dam")
        from reportlab.pdfbase.pdfmetrics import stringWidth
        co = min(co, (W - 4 * day) * 0.9 / max(1, stringWidth(self.chu, dam, 1)))
        c.setFont(dam, co)
        c.drawCentredString(W / 2, H * 0.47, self.chu)
        if self.ngay:
            c.setFont(_phong("thuong"), H * 0.2)
            c.drawCentredString(W / 2, H * 0.17, self.ngay)

    def them_pdf(self, d, f, s):
        from pypdf.generic import NameObject
        d[NameObject("/Name")] = NameObject("/DaXem")


LOAI = {"ghi_chu": "Ghi chú", "but_phe": "Bút phê", "to_sang": "Tô sáng", "chu_nhat": "Chữ nhật", "elip": "Elip",
        "mui_ten": "Mũi tên", "dau": "Dấu “Đã xem”"}


def la_chu_thich(tt) -> bool:
    return isinstance(tt, ChuThich)


# ---------------------------------------------------------------------------------------------- vẽ, hiện trên màn hình
def _pdf_hinh(ct: ChuThich, s: float) -> tuple[bytes, float, float]:
    from reportlab.pdfgen import canvas
    x0, y0, x1, y1 = ct.hop
    W, H = max(1.0, (x1 - x0) * s), max(1.0, (y1 - y0) * s)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    ct.ve(c, W, H, s)
    c.showPage()
    c.save()
    return buf.getvalue(), W, H


def phu_len(anh: np.ndarray, ds) -> np.ndarray:
    """Ảnh có vẽ chồng các chú thích (để hiện trên màn hình, ảnh nhỏ); không đổi `anh`."""
    ds = [ct for ct in ds if la_chu_thich(ct)]
    if not ds:
        return anh
    import pypdfium2 as pdfium
    ra = anh.copy()
    Hh, Ww = ra.shape[:2]
    for ct in ds:
        du_lieu, W, H = _pdf_hinh(ct, 1.0)
        doc = pdfium.PdfDocument(du_lieu)
        try:
            bgra = doc[0].render(scale=1, fill_color=(0, 0, 0, 0), rev_byteorder=False).to_numpy()
        finally:
            doc.close()
        x0, y0 = ct.hop[0], ct.hop[1]
        a0, b0 = max(0, x0), max(0, y0)
        a1, b1 = min(Ww, x0 + bgra.shape[1]), min(Hh, y0 + bgra.shape[0])
        if a1 <= a0 or b1 <= b0:
            continue
        m = bgra[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
        al = m[..., 3:4].astype(np.float32) / 255
        # PDFium trả màu đã nhân alpha: ảnh = màu + nền × (1 − alpha)
        nen = ra[b0:b1, a0:a1].astype(np.float32)
        ra[b0:b1, a0:a1] = np.clip(m[..., :3].astype(np.float32) + nen * (1 - al), 0, 255).astype(np.uint8)
    return ra


# ---------------------------------------------------------------------------------------------- ghi vào PDF
def _form(viet, du_lieu: bytes, W: float, H: float, R: int):
    """Biến trang PDF do reportlab vẽ thành Form XObject (hình hiển thị /AP) trong tệp đang ghi."""
    from pypdf import PdfReader
    from pypdf.generic import ArrayObject, DecodedStreamObject, FloatObject, NameObject, NumberObject
    pg = PdfReader(io.BytesIO(du_lieu)).pages[0]
    fx = DecodedStreamObject()
    fx.set_data(pg.get_contents().get_data())
    fx[NameObject("/Type")] = NameObject("/XObject")
    fx[NameObject("/Subtype")] = NameObject("/Form")
    fx[NameObject("/BBox")] = ArrayObject([NumberObject(0), NumberObject(0), FloatObject(round(W, 3)), FloatObject(round(H, 3))])
    # trang hiện xoay R độ cùng chiều kim đồng hồ: hình hiển thị xoay ngược lại để người đọc thấy thẳng
    m = {0: (1, 0, 0, 1), 90: (0, 1, -1, 0), 180: (-1, 0, 0, -1), 270: (0, -1, 1, 0)}[R]
    fx[NameObject("/Matrix")] = ArrayObject([NumberObject(v) for v in m] + [NumberObject(0), NumberObject(0)])
    fx[NameObject("/Resources")] = pg["/Resources"].get_object().clone(viet)
    return viet._add_object(fx)


def ghi_vao_trang(viet, pg, ds, f, R: int, s: float) -> int:
    """Ghi các chú thích `ds` vào trang `pg` (đã nằm trong `viet`). f(u, v) → (x, y) điểm PDF của trang (chưa xoay);
    R: góc trang hiện xoay (/Rotate); s: số điểm PDF ứng với một điểm ảnh. Trả số chú thích đã ghi."""
    from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject, NameObject, NumberObject, TextStringObject)
    n = 0
    for ct in ds:
        if not la_chu_thich(ct):
            continue
        du_lieu, W, H = _pdf_hinh(ct, s)
        x0, y0, x1, y1 = ct.hop
        goc = [f(u, v) for u, v in ((x0, y0), (x1, y0), (x0, y1), (x1, y1))]
        xs, ys = [p[0] for p in goc], [p[1] for p in goc]
        d = DictionaryObject({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject(ct.loai_pdf),
            NameObject("/Rect"): ArrayObject(FloatObject(round(v, 3)) for v in (min(xs), min(ys), max(xs), max(ys))),
            NameObject("/F"): NumberObject(4),  # in được
            NameObject("/T"): TextStringObject(TAC_GIA),
            NameObject("/NM"): TextStringObject("xlpa-" + ct.ma),
            NameObject("/M"): TextStringObject(ct.luc),
            NameObject("/CreationDate"): TextStringObject(ct.luc),
            NameObject("/Contents"): TextStringObject(ct.noi_dung or (getattr(ct, "chu", "") + " " + getattr(ct, "ngay", "")).strip()),
            NameObject("/C"): ArrayObject(FloatObject(round(v, 3)) for v in _rgb(ct.mau)),
            NameObject("/AP"): DictionaryObject({NameObject("/N"): _form(viet, du_lieu, W, H, R)}),
        })
        if isinstance(ct, ToSangCT):
            d[NameObject("/CA")] = FloatObject(1)
        ct.them_pdf(d, f, s)
        viet.add_annotation(pg, d)
        n += 1
    return n


__all__ = ["ChuThich", "GhiChu", "ButPhe", "ToSangCT", "HinhCT", "DauCT", "LOAI", "la_chu_thich", "phu_len",
           "ghi_vao_trang", "xoay_diem"]
