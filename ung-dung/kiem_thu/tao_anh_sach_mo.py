"""Ảnh chụp tổng hợp sách mở hai trang (cặp trang) để thử lỗi "chỉ nhận 1/2 trang khi chụp sách" (góp ý 14/11/2026).

Hai trang lấy từ ảnh trang sách thật đã làm sạch (`trang_sach/*.jpg`, cắt từ PDF người dùng gửi), ghép thành cặp trang,
uốn cong như sách mở (lõm xuống ở gáy, có bóng gáy), có gáy bìa và chồng mép giấy, ngón tay giữ ở mép ngoài, đặt trên
nền đen, nền gỗ hoặc vải; chụp nghiêng nhiều góc, cầm máy dọc (cặp trang nằm dọc trong khung) hoặc ngang.
Đáp án `dap_an.json`: 4 góc thật của cả cặp trang (trên trái, trên phải, dưới phải, dưới trái theo ảnh).

Chạy:  python tao_anh_sach_mo.py            (tạo kiem_thu/anh_sach_mo/)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import cv2
import numpy as np
from scipy.interpolate import griddata

GOC = Path(__file__).parent
THU_MUC = GOC / "anh_sach_mo"
NGUON = GOC / "trang_sach"


def _nen(kieu: str, W: int, H: int, rng) -> np.ndarray:
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    if kieu == "go":
        van = np.sin(x / 9 + 3 * np.sin(y / 140)) * 14 + rng.normal(0, 7, (H, W))
        b = np.stack([45 + van, 75 + van, 115 + van], -1)
    elif kieu == "vai":
        b = np.stack([120 + 0 * x, 90 + 0 * x, 40 + 0 * x], -1) + (np.sin(x / 25) * np.sin(y / 25) * 30)[..., None]
    else:  # nền đen (tấm bìa, áo đen) có nếp vải mờ
        b = np.full((H, W, 3), 22, np.float32) + (np.sin(x / 60 + y / 90) * 6)[..., None] + rng.normal(0, 3, (H, W, 1))
    return np.clip(b, 0, 255).astype(np.float32)


def _cap_trang(trai: np.ndarray, phai: np.ndarray, rong: int = 1100) -> np.ndarray:
    """Ghép hai trang cùng cỡ thành một cặp trang (thêm lề giấy như trang sách in)."""
    cao = int(rong * 1.5)
    out = []
    for t, ben in ((trai, 0), (phai, 1)):
        s = min((rong - 140) / t.shape[1], (cao - 160) / t.shape[0])
        t = cv2.resize(t, (int(t.shape[1] * s), int(t.shape[0] * s)), interpolation=cv2.INTER_AREA)
        nen = np.full((cao, rong, 3), (226, 232, 236), np.uint8)
        x0 = 90 if ben == 0 else rong - 90 - t.shape[1]  # lề ngoài rộng hơn lề gáy
        x0 = max(0, min(rong - t.shape[1], x0 if ben == 1 else 50))
        y0 = 70
        nen[y0:y0 + t.shape[0], x0:x0 + t.shape[1]] = np.minimum(nen[y0:y0 + t.shape[0], x0:x0 + t.shape[1]], t)
        out.append(nen)
    return np.hstack(out)


def _chieu(cap: np.ndarray, W: int, H: int, goc_xoay, kc, cong, dich, doc: bool, f=1700.0, do_bong=0.45):
    """Chiếu cặp trang (rộng 300 đơn vị) qua máy ảnh lỗ kim. Mặt cong: thấp ở gáy, cao dần ra mép ngoài.
    doc=True: cặp trang quay 90° (máy cầm dọc, gáy nằm ngang)."""
    h, w = cap.shape[:2]
    rw, rh = 300.0, 300.0 * h / w
    nu, nv = 121, 81
    u, v = np.meshgrid(np.linspace(0, 1, nu), np.linspace(0, 1, nv))
    X = (u - 0.5) * rw
    Y = (v - 0.5) * rh
    a = np.abs(u - 0.5) * 2  # 0 ở gáy, 1 ở mép ngoài
    Z = cong * (1 - np.exp(-a * 5.0)) - 0.25 * cong * a ** 2
    if doc:
        X, Y = -Y, X
    P = np.stack([X, Y, -Z], -1).reshape(-1, 3)
    ax, ay, az = [math.radians(t) for t in goc_xoay]
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    Q = P @ (Rz @ Ry @ Rx).T + np.array([dich[0], dich[1], kc])
    x = f * Q[:, 0] / Q[:, 2] + W / 2
    y = f * Q[:, 1] / Q[:, 2] + H / 2
    xy = np.stack([x, y], -1)
    uv = np.stack([u.ravel() * (w - 1), v.ravel() * (h - 1)], -1)
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    m = griddata(xy, uv, (xx, yy), method="linear")
    mx = cv2.resize(m[..., 0].astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    my = cv2.resize(m[..., 1].astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    trong = np.isfinite(mx) & np.isfinite(my)
    mx[~trong], my[~trong] = -10, -10
    anh = cv2.remap(cap, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    mat = cv2.remap(np.ones((h, w), np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # bóng gáy theo tọa độ u của điểm ảnh
    uu = np.where(trong, mx / (w - 1), 0.5)
    bong = 1 - do_bong * np.exp(-((uu - 0.5) / 0.025) ** 2) - 0.12 * np.exp(-((uu - 0.5) / 0.08) ** 2)
    goc = xy.reshape(nv, nu, 2)
    goc4 = np.array([goc[0, 0], goc[0, -1], goc[-1, -1], goc[-1, 0]])
    gay = np.array([goc[0, nu // 2], goc[-1, nu // 2]])
    g = nu // 2
    mot = {"trai": np.array([goc[0, 0], goc[0, g], goc[-1, g], goc[-1, 0]]),
           "phai": np.array([goc[0, g], goc[0, -1], goc[-1, -1], goc[-1, g]])}
    return anh.astype(np.float32), mat, bong.astype(np.float32), goc4, gay, mot


# tên, nền, cầm máy dọc, góc xoay, khoảng cách, độ cong, dịch, ngón tay, bìa
MAU = [
    ("01-den-ngang", "den", False, (6, -4, 2), 520, 14, (0, 0), True, True),
    ("02-den-doc", "den", True, (8, 3, -3), 470, 16, (0, 0), True, True),
    ("03-den-nghieng", "den", False, (18, 8, 6), 540, 18, (0, 10), True, True),
    ("04-den-sat", "den", False, (4, 2, 1), 420, 12, (0, 0), True, False),
    ("05-den-doc-nghieng", "den", True, (14, -10, 8), 500, 20, (10, 0), False, True),
    ("06-go-ngang", "go", False, (10, 5, -4), 540, 16, (0, 0), True, True),
    ("07-vai-doc", "vai", True, (6, -6, 4), 480, 14, (0, 0), True, True),
    ("08-den-cong-manh", "den", False, (8, 4, 0), 520, 30, (0, 0), True, True),
    ("09-den-doc-sat", "den", True, (3, 2, -2), 400, 12, (0, 0), True, False),
    ("10-den-lech", "den", False, (12, -6, -10), 560, 18, (-20, 15), False, True),
    # gáy rất tối (rãnh gáy gần đen), trang cong mạnh, sách gần kín khung như ảnh chụp thật
    ("11-gay-toi-ngang", "den", False, (5, 3, 1), 400, 40, (0, 0), True, True, 0.85),
    ("12-gay-toi-doc", "den", True, (6, -3, 2), 380, 45, (0, 0), True, True, 0.85),
    ("13-gay-toi-kin", "den", False, (3, 2, 0), 330, 50, (0, 0), True, False, 0.9),
    ("14-gay-toi-doc-kin", "den", True, (4, 2, -1), 320, 50, (0, 0), True, False, 0.9),
    ("15-gay-toi-nghieng", "den", False, (15, 10, 5), 430, 45, (10, 0), True, True, 0.85),
    # chụp sát, mép ngoài một trang lọt ra ngoài khung (ảnh thật chỉ còn nửa cặp trang)
    ("16-tran-phai", "den", False, (4, 2, 1), 360, 30, (75, 0), True, True, 0.7),
    ("17-tran-doc", "den", True, (5, -2, 2), 340, 30, (0, 45), True, True, 0.7),
    ("18-sat-trai", "den", False, (6, 3, -2), 380, 30, (-25, 0), True, True, 0.7),
    # chụp từng trang (máy cầm dọc, ngắm một trang, trang bên cạnh lộ một phần): phải lấy đúng một trang
    ("19-tung-trang-trai", "den", False, (4, 2, 1), 300, 30, (75, 0), True, True, 0.7, "trai", "doc"),
    # 20, 21: tham khảo (bộ tìm mép từ 0.7.0 đã lấy cả mẩu trang bên cạnh / không thấy trang), không tính đạt
    ("20-tung-trang-phai", "den", False, (5, -3, 2), 290, 30, (-75, 0), True, True, 0.7, "phai", "doc"),
    ("21-tung-trang-go", "go", False, (8, 4, -3), 310, 25, (72, 5), True, True, 0.6, "trai", "doc"),
]


def _trang_nguon() -> list[np.ndarray]:
    ds = [cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR) for p in sorted(NGUON.glob("*.jpg"))]
    return [a for a in ds if a is not None]


def tao() -> None:
    THU_MUC.mkdir(exist_ok=True)
    rng = np.random.default_rng(3)
    trang = _trang_nguon()
    if len(trang) < 2:
        raise SystemExit(f"Cần ít nhất 2 ảnh trang sách trong {NGUON}")
    dap_an = {}
    for k, (ten, kieu, doc, goc, kc, cong, dich, tay, bia, *them) in enumerate(MAU):
        do_bong = them[0] if them else 0.45
        chi = them[1] if len(them) > 1 else None  # chụp từng trang: đáp án là trang này
        W, H = (1500, 2000) if (doc or (len(them) > 2 and them[2] == "doc")) else (2000, 1500)
        cap = _cap_trang(trang[(2 * k) % len(trang)], trang[(2 * k + 1) % len(trang)])
        b = _nen(kieu, W, H, rng)
        anh, mat, bong, goc4, gay, mot = _chieu(cap, W, H, goc, kc, cong, dich, doc, do_bong=do_bong)
        if bia:  # bìa sách tối màu lộ ra quanh cặp trang, chồng mép giấy ngà ở mép ngoài
            tam = goc4.mean(0)
            to = ((goc4 - tam) * 1.035 + tam).astype(np.int32)
            cv2.fillPoly(b, [to], (40, 55, 120))
            cv2.fillPoly(b, [((goc4 - tam) * 1.015 + tam).astype(np.int32)], (175, 190, 200))
        m = mat[..., None]
        img = b * (1 - m) + anh * bong[..., None] * m
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        img *= (0.85 + 0.2 * (1 - yy / H) * (xx / W))[..., None]
        if tay:  # ngón cái giữ hai mép ngoài
            for g1, g2 in ((goc4[0], goc4[3]), (goc4[1], goc4[2])):
                p = (g1 * 0.35 + g2 * 0.65)
                tam = goc4.mean(0)
                p = p + (tam - p) * 0.03
                cv2.ellipse(img, (int(p[0]), int(p[1])), (95, 45), float(rng.uniform(-30, 30)), 0, 360, (120, 150, 215), -1)
        img = cv2.GaussianBlur(img, (0, 0), 0.8) + rng.normal(0, 3, img.shape)
        img = np.clip(img, 0, 255).astype(np.uint8)
        (THU_MUC / f"{ten}.jpg").write_bytes(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tobytes())
        dap_an[ten] = {"goc": (mot[chi] if chi else goc4).round(1).tolist(), "gay": gay.round(1).tolist(), "doc": doc,
                       "mot_trang": bool(chi), "tham_khao": ten.startswith(("20-", "21-"))}
        print(ten, goc4.round().astype(int).tolist())
    (THU_MUC / "dap_an.json").write_text(json.dumps(dap_an, indent=1), encoding="utf-8")


if __name__ == "__main__":
    tao()
