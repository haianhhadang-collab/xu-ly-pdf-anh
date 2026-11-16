"""Tạo bộ ảnh chụp tổng hợp khó để thử tìm mép giấy, nắn phẳng (kiểu CamScanner).

Mỗi ảnh là trang giấy (phẳng hoặc cong như sách mở) chụp bằng máy ảnh lỗ kim, đặt trên nhiều kiểu nền:
bàn gỗ, bàn trắng sáng gần màu giấy, nền lộn xộn, giấy gần kín khung, ngón tay đè mép, bóng đổ, góc ra ngoài khung.
Kèm tệp đáp án `dap_an.json`: 4 góc thật của trang trên ảnh, độ cong.

Chạy:  python tao_anh_mep.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import cv2
import numpy as np
from scipy.interpolate import griddata

from tao_anh_mau import tao_trang

THU_MUC = Path(__file__).parent / "anh_mau_mep"
W, H = 1500, 2000  # ảnh chụp (dọc), cỡ 3 MP như ảnh điện thoại đã thu nhỏ


def nen(kieu: str, rng) -> np.ndarray:
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    if kieu == "go":
        van = np.sin(x / 9 + 3 * np.sin(y / 140)) * 14 + rng.normal(0, 7, (H, W))
        b = np.stack([45 + van, 75 + van, 115 + van], -1)
    elif kieu == "trang":  # bàn trắng xám, sáng gần bằng giấy
        b = np.stack([200 + 0 * x, 203 + 0 * x, 205 + 0 * x], -1) + rng.normal(0, 4, (H, W, 1))
        b += (x / W * 18 - 9)[..., None]
    elif kieu == "lon_xon":
        b = np.full((H, W, 3), (70, 80, 90), np.float32) + rng.normal(0, 5, (H, W, 1))
        for _ in range(18):
            mau = rng.integers(20, 235, 3).tolist()
            p = rng.integers(0, [W, H], 2)
            if rng.random() < 0.5:
                cv2.rectangle(b, tuple(int(v) for v in p), tuple(int(v) for v in p + rng.integers(60, 500, 2)), mau, -1)
            else:
                cv2.line(b, tuple(int(v) for v in p), tuple(int(v) for v in rng.integers(0, [W, H], 2)), mau, int(rng.integers(3, 25)))
        # bàn phím: nhiều phím sáng
        for i in range(12):
            for j in range(4):
                cv2.rectangle(b, (60 + i * 110, 1750 + j * 60), (150 + i * 110, 1800 + j * 60), (215, 215, 215), -1)
    elif kieu == "vai":  # khăn trải bàn xanh hoa văn
        b = np.stack([120 + 0 * x, 90 + 0 * x, 40 + 0 * x], -1) + (np.sin(x / 25) * np.sin(y / 25) * 30)[..., None]
    else:
        b = np.full((H, W, 3), 30, np.float32)
    return np.clip(b, 0, 255).astype(np.float32)


def chieu(trang: np.ndarray, goc_xoay, kc, cong, dich, f=1700.0):
    """Chiếu trang (rộng 210 đơn vị) qua máy ảnh. cong: độ võng (đơn vị) kiểu sách, gáy ở mép trái."""
    h, w = trang.shape[:2]
    rw, rh = 210.0, 210.0 * h / w
    nu, nv = 61, 81
    u, v = np.meshgrid(np.linspace(0, 1, nu), np.linspace(0, 1, nv))
    X = (u - 0.5) * rw
    Y = (v - 0.5) * rh
    # mặt cong: võng lên gần gáy (u=0) như trang sách bên phải
    Z = -cong * np.exp(-u * 2.6) * (1 - 0.15 * (v - 0.5) ** 2)
    P = np.stack([X, Y, Z], -1).reshape(-1, 3)
    ax, ay, az = [math.radians(a) for a in goc_xoay]
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    Q = P @ (Rz @ Ry @ Rx).T + np.array([dich[0], dich[1], kc])
    x = f * Q[:, 0] / Q[:, 2] + W / 2
    y = f * Q[:, 1] / Q[:, 2] + H / 2
    xy = np.stack([x, y], -1)
    uv = np.stack([u.ravel() * (w - 1), v.ravel() * (h - 1)], -1)
    # đảo: điểm ảnh chụp -> tọa độ trang
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    m = griddata(xy, uv, (xx, yy), method="linear")
    mx = cv2.resize(m[..., 0].astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    my = cv2.resize(m[..., 1].astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    trong = np.isfinite(mx) & np.isfinite(my)
    mx[~trong], my[~trong] = -10, -10
    anh = cv2.remap(trang, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    mat = cv2.remap(np.ones((h, w), np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    goc = xy.reshape(nv, nu, 2)
    goc4 = [goc[0, 0], goc[0, -1], goc[-1, -1], goc[-1, 0]]
    # chiều cao mặt cong theo x ảnh (để làm bóng gáy)
    return anh.astype(np.float32), mat, [list(map(float, g)) for g in goc4]


MAU = [
    # tên, nền, góc xoay (x,y,z), khoảng cách, độ cong, dịch, bóng, ngón tay
    ("01-go-nghieng", "go", (18, -8, 6), 430, 0, (0, 0), False, False),
    ("02-ban-trang", "trang", (10, 6, -4), 420, 0, (0, 10), False, False),
    ("03-gan-kin", "go", (6, 4, 2), 292, 0, (0, 0), False, False),
    ("04-lon-xon", "lon_xon", (22, 10, -12), 470, 0, (10, -60), False, False),
    ("05-ngon-tay", "vai", (14, -6, 3), 410, 0, (0, 0), False, True),
    ("06-sach-cong", "toi", (8, 4, 2), 400, 45, (0, 0), True, False),
    ("07-cong-ban-trang", "trang", (12, -5, -3), 410, 32, (0, 0), True, False),
    ("08-bong-do", "go", (16, 8, 8), 420, 0, (0, 0), True, False),
    ("09-goc-ra-ngoai", "vai", (10, -10, 5), 335, 0, (25, 20), False, False),
    ("10-xoay-ngang", "go", (5, 20, 30), 470, 6, (0, 0), False, False),
    ("11-kin-khung", "go", (2, 1, 0), 240, 0, (0, 0), False, False),
    ("12-cong-nhe", "go", (10, -4, 4), 420, 18, (0, 0), False, False),
    ("13-giay-chong", "go", (12, 5, -6), 450, 0, (0, 0), False, False),
    ("14-toi-mo", "vai", (15, -7, 4), 420, 10, (0, 0), True, False),
    ("15-so-tay", "trang", (8, 8, 3), 400, 0, (0, 0), False, False),
    ("16-sach-cong-manh", "toi", (16, 3, 1), 330, 90, (20, 0), True, False),
    ("17-sach-cong-lech", "go", (-14, 8, -5), 340, 70, (0, 20), True, False),
]


def tao():
    THU_MUC.mkdir(exist_ok=True)
    rng = np.random.default_rng(7)
    trang = tao_trang()
    trang = cv2.copyMakeBorder(trang, 0, 0, 0, 0, cv2.BORDER_CONSTANT)
    dap_an = {}
    for ten, kieu, goc, kc, cong, dich, bong, tay in MAU:
        b = nen(kieu, rng)
        if ten == "13-giay-chong":  # tờ giấy trắng khác nằm dưới, lệch góc
            cv2.fillPoly(b, [np.array([[150, 150], [1350, 260], [1300, 1900], [90, 1820]], np.int32)], (232, 236, 238))
        if ten == "15-so-tay":  # bìa sổ tối màu, gáy lò xo
            cv2.fillPoly(b, [np.array([[180, 210], [1300, 190], [1330, 1800], [170, 1830]], np.int32)], (60, 40, 30))
        anh, mat, goc4 = chieu(trang, goc, kc, cong, dich)
        m = mat[..., None]
        img = b * (1 - m) + anh * m
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        # ánh sáng không đều
        img *= (0.85 + 0.2 * (1 - yy / H) * (xx / W))[..., None]
        if bong:
            # bóng gáy / bóng tay chụp
            img *= (1 - 0.35 * np.exp(-((xx - goc4[0][0]) / 120) ** 2))[..., None] if cong else \
                (1 - 0.35 * (((xx - 300) ** 2 + (yy - 600) ** 2) < 500 ** 2))[..., None]
            img = cv2.GaussianBlur(img, (0, 0), 1.2)
        if tay:
            cv2.ellipse(img, (int(goc4[3][0]) + 260, int(goc4[3][1]) + 20), (70, 170), 20, 0, 360, (120, 150, 215), -1)
            cv2.ellipse(img, (int(goc4[1][0]) - 40, int(goc4[1][1]) + 300), (150, 60), 0, 0, 360, (110, 140, 205), -1)
        if ten == "14-toi-mo":
            img = cv2.GaussianBlur(img * 0.45, (0, 0), 2.5) + rng.normal(0, 7, img.shape)
        img = img + rng.normal(0, 3, img.shape)
        img = np.clip(img, 0, 255).astype(np.uint8)
        (THU_MUC / f"{ten}.jpg").write_bytes(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tobytes())
        dap_an[ten] = {"goc": goc4, "cong": cong}
        print(ten, [tuple(round(v) for v in g) for g in goc4])
    (THU_MUC / "dap_an.json").write_text(json.dumps(dap_an, indent=1), encoding="utf-8")


if __name__ == "__main__" and len(__import__("sys").argv) <= 2:
    tao()


def tao_ngau_nhien(so: int, hat: int = 11) -> None:
    """Bộ ảnh ngẫu nhiên (nền, góc chụp, độ cong, bóng, mờ) để kiểm tra bộ tìm mép không chỉ khớp bộ mẫu cố định."""
    global THU_MUC
    THU_MUC = Path(__file__).parent / "anh_mau_mep_nn"
    rng = np.random.default_rng(hat)
    ds = []
    for i in range(so):
        kieu = ["go", "trang", "lon_xon", "vai", "toi"][i % 5]
        goc = (float(rng.uniform(-20, 20)), float(rng.uniform(-15, 15)), float(rng.uniform(-35, 35)))
        ds.append((f"nn{i:02d}-{kieu}", kieu, goc, float(rng.uniform(330, 500)), float(rng.choice([0, 0, 10, 25, 40])),
                   (float(rng.uniform(-30, 30)), float(rng.uniform(-30, 30))), bool(rng.random() < 0.4), bool(rng.random() < 0.25)))
    global MAU
    MAU = ds


if __name__ == "__main__" and len(__import__("sys").argv) > 2:
    tao_ngau_nhien(int(__import__("sys").argv[2]), int(__import__("sys").argv[3]) if len(__import__("sys").argv) > 3 else 11)
    tao()
