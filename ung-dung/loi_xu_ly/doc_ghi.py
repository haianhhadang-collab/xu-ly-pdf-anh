"""Đọc ảnh và PDF thành ảnh trang; ghi PDF theo khổ giấy, lề, chất lượng, có lớp chữ."""
from __future__ import annotations

import io
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageSequence

from . import nhan_dang

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

DUOI_ANH = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".heic", ".heif"}
DUOI_PDF = {".pdf"}
DUOI_HO_TRO = DUOI_ANH | DUOI_PDF
CANH_TOI_DA = 3500  # cạnh dài tối đa của ảnh đưa vào xử lý, tránh tràn bộ nhớ

KHO_GIAY = {  # điểm (1/72 inch), khổ đứng
    "a4": (595.28, 841.89),
    "a5": (419.53, 595.28),
    "letter": (612.0, 792.0),
    "legal": (612.0, 1008.0),
}
TEN_KHO = {"theo_anh": "Theo tỉ lệ ảnh (rộng A4)", "a4": "A4", "a5": "A5", "letter": "Letter", "legal": "Legal"}
CHAT_LUONG = {"cao": (300, 90), "vua": (200, 80), "nho": (150, 65)}  # dpi, chất lượng JPEG
TEN_CHAT_LUONG = {"cao": "Cao (300 dpi)", "vua": "Vừa (200 dpi)", "nho": "Nhỏ gọn (150 dpi)"}


def gioi_han_kich_thuoc(anh: np.ndarray, canh: int = CANH_TOI_DA) -> np.ndarray:
    h, w = anh.shape[:2]
    if max(h, w) <= canh:
        return anh
    s = canh / max(h, w)
    return cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)


def pil_sang_bgr(img: Image.Image) -> np.ndarray:
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        nen = Image.new("RGB", img.size, (255, 255, 255))
        nen.paste(img, mask=img.split()[-1])
        img = nen
    elif img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    a = np.asarray(img)
    if a.ndim == 2:
        return cv2.cvtColor(a, cv2.COLOR_GRAY2BGR)
    return cv2.cvtColor(a, cv2.COLOR_RGB2BGR)


def doc_tep(duong_dan, dpi_pdf: int = 200) -> list[tuple[str, np.ndarray]]:
    """Đọc một tệp ảnh (kể cả TIFF nhiều trang) hoặc PDF; trả [(tên trang, ảnh BGR)]."""
    p = Path(duong_dan)
    duoi = p.suffix.lower()
    kq = []
    if duoi in DUOI_PDF:
        import pypdfium2 as pdfium
        tl = pdfium.PdfDocument(str(p))
        try:
            for i in range(len(tl)):
                bitmap = tl[i].render(scale=dpi_pdf / 72)
                kq.append((f"{p.name} – trang {i + 1}", gioi_han_kich_thuoc(pil_sang_bgr(bitmap.to_pil()))))
        finally:
            tl.close()
    elif duoi in DUOI_ANH:
        with Image.open(p) as img:
            khung = list(ImageSequence.Iterator(img)) if getattr(img, "n_frames", 1) > 1 else [img]
            for i, k in enumerate(khung):
                ten = p.name if len(khung) == 1 else f"{p.name} – trang {i + 1}"
                kq.append((ten, gioi_han_kich_thuoc(pil_sang_bgr(k.copy()))))
    else:
        raise ValueError(f"Không hỗ trợ định dạng {duoi}")
    return kq


def la_den_trang(anh: np.ndarray) -> bool:
    nho = anh[::4, ::4]
    return bool(np.all((nho == 0) | (nho == 255)))


def ma_hoa(anh: np.ndarray, chat_luong_jpeg: int = 95) -> bytes:
    """Mã hóa ảnh để giữ trong bộ nhớ hoặc nhúng PDF: đen trắng dùng PNG, còn lại JPEG."""
    if la_den_trang(anh):
        ok, buf = cv2.imencode(".png", cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY))
    else:
        ok, buf = cv2.imencode(".jpg", anh, [cv2.IMWRITE_JPEG_QUALITY, chat_luong_jpeg])
    if not ok:
        raise RuntimeError("Không mã hóa được ảnh")
    return buf.tobytes()


def giai_ma(du_lieu: bytes) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(du_lieu, np.uint8), cv2.IMREAD_COLOR)


def ghi_anh(anh: np.ndarray, duong_dan) -> None:
    """Ghi ảnh ra đường dẫn có dấu tiếng Việt (cv2.imwrite không làm được trên Windows)."""
    duoi = Path(duong_dan).suffix.lower() or ".png"
    ok, buf = cv2.imencode(duoi, anh)
    if not ok:
        raise RuntimeError(f"Không ghi được {duong_dan}")
    buf.tofile(str(duong_dan))


def kich_thuoc_trang(kho: str, rong_px: int, cao_px: int) -> tuple[float, float]:
    ngang = rong_px > cao_px
    if kho == "theo_anh":
        rong = KHO_GIAY["a4"][1] if ngang else KHO_GIAY["a4"][0]
        return rong, rong * cao_px / rong_px
    pw, ph = KHO_GIAY[kho]
    return (ph, pw) if ngang else (pw, ph)


def ghi_pdf(cac_anh: list[np.ndarray], duong_dan, kho: str = "a4", le_mm: float = 0.0,
            chat_luong: str = "vua", ocr: bool = False, ngon_ngu: str = "vie",
            tieu_de: str = "", bao_tien_trinh=None) -> None:
    """Ghi danh sách ảnh trang thành một PDF.

    Ảnh được đặt vừa trong vùng trừ lề, giữ tỉ lệ, căn giữa; giảm độ phân giải
    theo `chat_luong`. Nếu `ocr`, thêm lớp chữ ẩn để tìm kiếm và chép chữ.
    """
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    if not cac_anh:
        raise ValueError("Không có trang nào để ghi")
    dpi, q = CHAT_LUONG[chat_luong]
    bao = bao_tien_trinh or (lambda *_: None)
    tong = len(cac_anh) * (2 if ocr else 1)

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.setTitle(tieu_de or Path(duong_dan).stem)
    c.setCreator("Xử lý PDF ảnh (nguyên mẫu)")
    vi_tri = []
    le = le_mm / 25.4 * 72
    for i, anh in enumerate(cac_anh):
        h, w = anh.shape[:2]
        pw, ph = kich_thuoc_trang(kho, w, h)
        ty_le = min((pw - 2 * le) / w, (ph - 2 * le) / h)
        dw, dh = w * ty_le, h * ty_le
        x0, y0 = (pw - dw) / 2, (ph - dh) / 2
        px_toi_da = dw / 72 * dpi
        if w > px_toi_da * 1.05:
            anh = cv2.resize(anh, (round(px_toi_da), max(1, round(h * px_toi_da / w))), interpolation=cv2.INTER_AREA)
        c.setPageSize((pw, ph))
        c.drawImage(ImageReader(io.BytesIO(ma_hoa(anh, q))), x0, y0, dw, dh)
        c.showPage()
        vi_tri.append((anh, x0, y0, dw, dh))
        bao(i + 1, tong, f"Ghi trang {i + 1}/{len(cac_anh)}")
    c.save()
    buf.seek(0)

    tam = Path(str(duong_dan) + ".dang-ghi")
    if ocr:
        from pypdf import PdfReader, PdfWriter, Transformation
        ngon_ngu = nhan_dang.chon_ngon_ngu(ngon_ngu)
        viet = PdfWriter(clone_from=PdfReader(buf))
        for i, (anh, x0, y0, dw, dh) in enumerate(vi_tri):
            bao(len(cac_anh) + i, tong, f"Nhận dạng chữ trang {i + 1}/{len(cac_anh)}")
            lop = PdfReader(io.BytesIO(nhan_dang.lop_chu_pdf(anh, ngon_ngu, anh.shape[1] / (dw / 72)))).pages[0]
            tw, th = float(lop.mediabox.width), float(lop.mediabox.height)
            viet.pages[i].merge_transformed_page(lop, Transformation().scale(dw / tw, dh / th).translate(x0, y0))
        viet.add_metadata({"/Title": tieu_de or Path(duong_dan).stem, "/Creator": "Xử lý PDF ảnh (nguyên mẫu)"})
        with open(tam, "wb") as f:
            viet.write(f)
        bao(tong, tong, "Xong")
    else:
        tam.write_bytes(buf.getvalue())
    os.replace(tam, duong_dan)


def ghi_van_ban(cac_anh: list[np.ndarray], duong_dan, ngon_ngu: str = "vie", bao_tien_trinh=None) -> None:
    bao = bao_tien_trinh or (lambda *_: None)
    ngon_ngu = nhan_dang.chon_ngon_ngu(ngon_ngu)
    phan = []
    for i, anh in enumerate(cac_anh):
        bao(i, len(cac_anh), f"Nhận dạng chữ trang {i + 1}/{len(cac_anh)}")
        phan.append(f"===== Trang {i + 1} =====\n{nhan_dang.van_ban(anh, ngon_ngu).strip()}\n")
    Path(duong_dan).write_text("\n".join(phan), encoding="utf-8")
