"""Tính năng 2: làm sáng nền, tăng tương phản, giữ màu mực.

Cách làm:
1. Ước lượng nền bằng phép đóng hình thái học trên ảnh thu nhỏ (xóa nét chữ,
   chỉ còn nền gồm cả bóng đổ).
2. Chia ảnh gốc cho nền theo từng kênh: nền thành trắng đều, mất bóng đổ,
   mất cả màu ngả vàng của giấy.
3. Điểm ít màu (chữ in đen) đi qua đường cong tương phản: nền về trắng, chữ
   về đen đậm, bỏ ám màu.
4. Điểm có màu (dấu đỏ, mực xanh, hình màu) chỉ được làm đậm và tăng độ bão
   hòa, giữ nguyên tỉ lệ giữa các kênh nên giữ được sắc độ.
"""
from __future__ import annotations

import cv2
import numpy as np

CHE_DO = {
    "giu_mau": "Giữ màu (khuyên dùng)",
    "xam": "Thang xám",
    "den_trang": "Đen trắng",
    "khong": "Không làm sạch",
}


def uoc_luong_nen(anh: np.ndarray) -> np.ndarray:
    """Trả về ảnh nền (float32, cùng kích thước) đã xóa nét chữ."""
    h, w = anh.shape[:2]
    ti_le = min(1.0, 1000 / max(h, w))
    nho = cv2.resize(anh, None, fx=ti_le, fy=ti_le, interpolation=cv2.INTER_AREA) if ti_le < 1 else anh
    nhan = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    nen = cv2.morphologyEx(nho, cv2.MORPH_CLOSE, nhan)
    nen = cv2.medianBlur(nen, 21)
    # Vùng ảnh màu lớn (hình minh họa) không xóa được bằng phép đóng; chặn dưới
    # để những vùng đó không bị chia thành trắng bệch.
    sang = np.percentile(nen.reshape(-1, nen.shape[2]), 95, axis=0)
    nen = np.maximum(nen.astype(np.float32), sang.astype(np.float32) * 0.45)
    nen = cv2.GaussianBlur(nen, (0, 0), 3)
    return cv2.resize(nen, (w, h), interpolation=cv2.INTER_CUBIC)


def _do_sang(a: np.ndarray) -> np.ndarray:
    # BGR
    return a[..., 0] * 0.114 + a[..., 1] * 0.587 + a[..., 2] * 0.299


def _chuyen_mem(x: np.ndarray, a: float, b: float) -> np.ndarray:
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def lam_sach(anh: np.ndarray, che_do: str = "giu_mau", do_trang: float = 0.5, do_dam: float = 0.5) -> np.ndarray:
    """Làm sạch ảnh trang (BGR uint8).

    do_trang: 0..1, càng lớn nền càng được đẩy về trắng mạnh.
    do_dam:   0..1, càng lớn chữ càng đậm.
    """
    if che_do == "khong":
        return anh
    nen = uoc_luong_nen(anh)
    chuan = np.clip(anh.astype(np.float32) / np.maximum(nen, 1.0), 0, 1)
    y = _do_sang(chuan)

    diem_trang = 0.97 - 0.15 * do_trang
    diem_den = min(float(np.percentile(y, 0.5)), 0.35)
    gamma = 1.0 + do_dam
    xam = np.clip((y - diem_den) / (diem_trang - diem_den), 0, 1) ** gamma

    if che_do == "den_trang":
        u8 = (xam * 255).astype(np.uint8)
        _, nhi_phan = cv2.threshold(u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.cvtColor(nhi_phan, cv2.COLOR_GRAY2BGR)
    if che_do == "xam":
        return cv2.cvtColor((xam * 255 + 0.5).astype(np.uint8), cv2.COLOR_GRAY2BGR)

    # Giữ màu: trộn giữa nhánh xám và nhánh màu theo độ đậm màu tuyệt đối.
    do_mau = chuan.max(axis=2) - chuan.min(axis=2)
    trong_so = _chuyen_mem(do_mau, 0.10, 0.22)[..., None]

    y_mau = np.clip(y, 0, 1) ** (1.0 + 0.5 * do_dam)
    mau = chuan * (y_mau / np.maximum(y, 1e-3))[..., None]
    mau = y_mau[..., None] + (mau - y_mau[..., None]) * 1.25

    ket_qua = xam[..., None] * (1 - trong_so) + mau * trong_so
    return (np.clip(ket_qua, 0, 1) * 255 + 0.5).astype(np.uint8)
