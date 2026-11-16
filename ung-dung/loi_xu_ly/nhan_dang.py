"""Nhận dạng chữ (OCR) Việt–Anh bằng Tesseract: xoay đúng chiều, lớp chữ PDF, xuất văn bản."""
from __future__ import annotations

import os
import shutil

import cv2
import numpy as np
from PIL import Image

try:
    import pytesseract
except ImportError:  # vẫn chạy được các tính năng không cần OCR
    pytesseract = None


def _tim_tesseract() -> bool:
    if pytesseract is None:
        return False
    if shutil.which("tesseract"):
        return True
    for p in (r"C:\Program Files\Tesseract-OCR\tesseract.exe",
              r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            return True
    return False


CO_TESSERACT = _tim_tesseract()


def ngon_ngu_co_san() -> list[str]:
    if not CO_TESSERACT:
        return []
    try:
        return pytesseract.get_languages(config="")
    except Exception:
        return []


def chon_ngon_ngu(mong_muon: str = "vie") -> str:
    co = set(ngon_ngu_co_san())
    chon = [l for l in mong_muon.split("+") if l in co]
    return "+".join(chon) or "eng"


def _pil(anh: np.ndarray) -> Image.Image:
    if anh.ndim == 2:
        return Image.fromarray(anh)
    return Image.fromarray(cv2.cvtColor(anh, cv2.COLOR_BGR2RGB))


def huong_chu(anh: np.ndarray) -> tuple[int, float]:
    """(góc cần xoay theo chiều kim đồng hồ, độ tin cậy). (0, 0) nếu không đoán được."""
    if not CO_TESSERACT:
        return 0, 0.0
    xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY) if anh.ndim == 3 else anh
    s = min(1.0, 2000 / max(xam.shape))
    if s < 1:
        xam = cv2.resize(xam, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    try:
        osd = pytesseract.image_to_osd(_pil(xam), config="--psm 0 -c min_characters_to_try=10",
                                       output_type=pytesseract.Output.DICT)
    except Exception:  # quá ít chữ để đoán
        return 0, 0.0
    return int(osd.get("rotate", 0)) % 360, float(osd.get("orientation_conf", 0.0))


def lop_chu_pdf(anh: np.ndarray, ngon_ngu: str, dpi: float) -> bytes:
    """Trang PDF chỉ chứa lớp chữ ẩn (để tìm kiếm, chép chữ), kích thước theo dpi."""
    if not CO_TESSERACT:
        raise RuntimeError("Chưa cài Tesseract OCR nên không tạo được lớp chữ.")
    return pytesseract.image_to_pdf_or_hocr(
        _pil(anh), lang=ngon_ngu, extension="pdf",
        config=f"--dpi {max(int(round(dpi)), 70)} -c textonly_pdf=1")


def van_ban(anh: np.ndarray, ngon_ngu: str = "vie") -> str:
    if not CO_TESSERACT:
        raise RuntimeError("Chưa cài Tesseract OCR.")
    return pytesseract.image_to_string(_pil(anh), lang=ngon_ngu, config="--psm 3")
