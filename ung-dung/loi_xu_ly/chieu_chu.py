"""Nhận ra trang có dòng chữ chạy dọc (ảnh chụp khi cầm máy ngang, trang sách mở chụp xoay) để xoay về ngang
trước các bước cần dòng chữ nằm ngang (tìm gáy, nắn cong, sửa nghiêng, cắt sát chữ).

Chỉ phân biệt dòng ngang / dòng dọc, không phân biệt xuôi / ngược: bước đoán chiều bằng Tesseract sau khi xử lý lo
việc lật 180°. Cách làm: lấy các nét cỡ chữ, nối chữ theo chiều ngang rồi theo chiều dọc; chiều nào nối ra nhiều dải
dài, mảnh (dòng chữ) hơn hẳn thì đó là chiều dòng chữ.
"""
from __future__ import annotations

import cv2
import numpy as np

CANH_XU_LY = 1000


def _do_dai_dong(chu: np.ndarray, cao_chu: float, ngang: bool) -> float:
    """Tổng chiều dài các dải dài, mảnh khi nối chữ theo một chiều."""
    k = max(3, int(1.6 * cao_chu))
    nhan = (k, 1) if ngang else (1, k)
    dong = cv2.morphologyEx(chu, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, nhan),
                            borderType=cv2.BORDER_REPLICATE)
    n, _, tk, _ = cv2.connectedComponentsWithStats(dong, 8)
    dai = tk[1:, cv2.CC_STAT_WIDTH if ngang else cv2.CC_STAT_HEIGHT].astype(np.float64)
    day = tk[1:, cv2.CC_STAT_HEIGHT if ngang else cv2.CC_STAT_WIDTH].astype(np.float64)
    giu = (dai > 6 * day) & (dai > 8 * cao_chu) & (day < 3 * cao_chu)
    return float(dai[giu].sum())


def chu_doc(anh: np.ndarray) -> bool:
    """True nếu dòng chữ của trang chạy dọc (cần xoay 90°)."""
    h, w = anh.shape[:2]
    s = min(1.0, CANH_XU_LY / max(h, w))
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    muc = cv2.adaptiveThreshold(xam, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 15)
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(muc, 8)
    if n < 40:
        return False
    cw, ch, dt = tk[1:, cv2.CC_STAT_WIDTH], tk[1:, cv2.CC_STAT_HEIGHT], tk[1:, cv2.CC_STAT_AREA]
    gioi = 0.05 * max(xam.shape)
    vua = (cw >= 2) & (ch >= 2) & (cw < gioi) & (ch < gioi) & (dt >= 4)
    if vua.sum() < 40:
        return False
    # cỡ chữ: trung vị cạnh lớn của nét (không phụ thuộc chiều dòng)
    cao_chu = float(np.median(np.maximum(cw, ch)[vua]))
    giu = np.zeros(n, np.uint8)
    giu[1:][vua & (np.maximum(cw, ch) <= 3 * cao_chu)] = 255
    chu = giu[nhan]
    ngang = _do_dai_dong(chu, cao_chu, True)
    doc = _do_dai_dong(chu, cao_chu, False)
    return doc > 1.5 * ngang and doc > 30 * cao_chu
