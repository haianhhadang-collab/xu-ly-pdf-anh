"""Kiểm thử chế độ tự động chụp trên chuỗi khung hình camera mô phỏng.

Dựng một "đoạn phim" 15 khung/giây: đưa trang vào khung, giữ yên (vài khung đầu
còn mờ do máy đang lấy nét), va máy rồi về lại trang cũ, lật trang (tay che),
trang thiếu sáng, bị lóa, bị cắt mép, cầm nghiêng, chụp kín hai trang sách.
Kiểm tra: mỗi trang mới chụp đúng một lần, không chụp khi chưa đủ điều kiện,
không chụp lại trang cũ, ảnh chụp là khung nét nhất.

Chạy:  python kiem_thu_tu_chup.py        (thêm --chi-tiet để in số liệu từng đoạn)
"""
from __future__ import annotations

import math
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from loi_xu_ly.tu_chup import BoTuChup  # noqa: E402

FONT = "C:/Windows/Fonts/times.ttf"
RONG, CAO, FPS = 960, 720, 15
TU = ("thư viện tài liệu số hóa trang sách lưu trữ hồ sơ công văn quyết định biên bản năm học "
      "nghiên cứu giáo trình bản đồ lịch sử văn hóa xã hội kinh tế the library archive document "
      "chapter history culture của và các những được trong cho với không này đã là một có").split()
loi: list[str] = []


def kiem(dk: bool, mo_ta: str):
    print(("ĐẠT  " if dk else "LỖI  ") + mo_ta)
    if not dk:
        loi.append(mo_ta)


def trang_sach(hat: int, rong=620, cao=877) -> np.ndarray:
    """Một trang sách chữ in, bố cục (độ dài dòng, chỗ xuống đoạn) khác nhau theo `hat`."""
    rng = np.random.default_rng(hat)
    img = Image.new("RGB", (rong, cao), (238, 232, 214))
    d = ImageDraw.Draw(img)
    f, ft = ImageFont.truetype(FONT, 17), ImageFont.truetype(FONT, 26)
    d.text((rong // 2, 60), f"CHƯƠNG {hat}", font=ft, fill=(30, 30, 30), anchor="mm")
    y = 110
    while y < cao - 70:
        if rng.random() < 0.12:  # xuống đoạn
            y += 22
        x, dai = 60 + (30 if rng.random() < 0.15 else 0), rng.integers(330, rong - 120)
        dong = []
        while len(" ".join(dong)) * 8 < dai:
            dong.append(TU[rng.integers(len(TU))])
        d.text((x, y), " ".join(dong), font=f, fill=(25, 25, 25))
        y += 24
    d.text((rong // 2, cao - 35), str(hat), font=f, fill=(30, 30, 30), anchor="mm")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def nen_ban() -> np.ndarray:
    rng = np.random.default_rng(7)
    van = np.sin(np.linspace(0, 40, RONG))[None, :] * 10 + rng.normal(0, 5, (CAO, RONG))
    nen = np.zeros((CAO, RONG, 3), np.float32)
    nen[..., 0], nen[..., 1], nen[..., 2] = 45 + van, 70 + van, 110 + van
    return nen


NEN = nen_ban()
yy, xx = np.mgrid[0:CAO, 0:RONG]
ANH_SANG = (1 - 0.3 * np.clip((xx / RONG + yy / CAO - 0.8) / 1.2, 0, 1))[..., None]


def tu_giac(cx, cy, cao, xoay=0.0, nghieng=0.0, ti_le=1 / math.sqrt(2)) -> np.ndarray:
    """4 góc trang: tâm, chiều cao (px), góc xoay (độ), độ nghiêng phối cảnh (mép trên co lại)."""
    w, h = cao * ti_le / 2, cao / 2
    p = np.float32([[-w * (1 - nghieng), -h], [w * (1 - nghieng), -h], [w * (1 + nghieng), h], [-w * (1 + nghieng), h]])
    a = math.radians(xoay)
    r = np.float32([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return p @ r.T + np.float32([cx, cy])


def ve(trang, goc, mo=0.0, toi=1.0, loa=None, tay=None, rng=None) -> np.ndarray:
    h, w = trang.shape[:2]
    m = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(goc))
    anh = NEN.copy()
    if trang is not None:
        cong = cv2.warpPerspective(trang, m, (RONG, CAO), flags=cv2.INTER_LINEAR).astype(np.float32)
        mat = cv2.warpPerspective(np.ones((h, w), np.float32), m, (RONG, CAO))[..., None]
        anh = cong * mat + anh * (1 - mat)
    anh = anh * ANH_SANG
    if loa is not None:
        x0, y0 = loa
        anh += 160 * np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * 45.0 ** 2))[..., None]
    if tay is not None:
        cv2.ellipse(anh, (int(tay[0]), int(tay[1])), (150, 95), 30, 0, 360, (120, 150, 205), -1)
    if mo:
        anh = cv2.GaussianBlur(anh, (0, 0), mo)
    anh = anh * toi + rng.normal(0, 2.0, anh.shape)
    return np.clip(anh, 0, 255).astype(np.uint8)


def kich_ban():
    """Sinh (tên đoạn, khung hình). Mỗi đoạn là một tình huống."""
    rng = np.random.default_rng(3)
    t1, t2, t3 = trang_sach(1), trang_sach(2), trang_sach(3)
    doi = np.concatenate([trang_sach(4), trang_sach(5)], axis=1)
    o = tu_giac(480, 360, 640)

    def rung(g, bien=0.4):
        return g + rng.normal(0, bien, g.shape).astype(np.float32)

    def doan(ten, giay, ham):
        n = round(giay * FPS)
        for i in range(n):
            yield ten, ham(i, n)

    yield from doan("ban_trong", 0.6, lambda i, n: ve(t1, tu_giac(-900, -900, 10), rng=rng))
    yield from doan("dua_vao", 0.8, lambda i, n: ve(t1, tu_giac(480 + 400 * (1 - i / n), 360, 640, 8 * (1 - i / n)),
                                                    mo=2.0, rng=rng))
    # giữ yên trang 1; 4 khung đầu mờ (máy đang lấy nét)
    yield from doan("giu_trang1", 2.5, lambda i, n: ve(t1, rung(o), mo=2.2 if i < 4 else 0, rng=rng))
    yield from doan("va_may", 0.4, lambda i, n: ve(t1, o + np.float32([40 * math.sin(i), 25]), mo=1.5, rng=rng))
    yield from doan("ve_trang1", 1.5, lambda i, n: ve(t1, rung(o + np.float32([3, -2])), rng=rng))
    yield from doan("lat_trang", 0.7, lambda i, n: ve(t1 if i < n // 2 else t2, rung(o),
                                                      tay=(900 - 1000 * i / n, 380), mo=1.2, rng=rng))
    yield from doan("giu_trang2", 1.8, lambda i, n: ve(t2, rung(o), rng=rng))
    yield from doan("lat_trang_3", 0.5, lambda i, n: ve(t3, rung(o), tay=(900 - 1000 * i / n, 380), mo=1.2, rng=rng))
    yield from doan("toi", 1.5, lambda i, n: ve(t3, rung(o), toi=0.22, rng=rng))
    yield from doan("loa", 1.5, lambda i, n: ve(t3, rung(o), loa=(470, 300), rng=rng))
    yield from doan("cat_mep", 1.5, lambda i, n: ve(t3, rung(tu_giac(480, 470, 640)), rng=rng))
    yield from doan("xa", 1.5, lambda i, n: ve(t3, rung(tu_giac(480, 360, 220)), rng=rng))
    yield from doan("nghieng", 1.5, lambda i, n: ve(t3, rung(tu_giac(480, 360, 600, nghieng=0.3)), rng=rng))
    yield from doan("giu_trang3", 1.8, lambda i, n: ve(t3, rung(o), rng=rng))
    # chụp sát sách mở: hai trang phủ kín khung hình, không thấy mép
    kin = np.float32([[-40, -60], [RONG + 40, -60], [RONG + 40, CAO + 300], [-40, CAO + 300]])
    yield from doan("kin_khung", 1.8, lambda i, n: ve(doi, rung(kin), rng=rng))


def main():
    chi_tiet = "--chi-tiet" in sys.argv
    bo = BoTuChup()
    ma_theo_doan: dict[str, Counter] = {}
    so_lieu: dict[str, list] = {}
    chup: list[tuple[str, np.ndarray]] = []
    mau_mo = None
    thoi_gian = []
    for k, (ten, kh) in enumerate(kich_ban()):
        if ten == "giu_trang1" and mau_mo is None:
            mau_mo = kh
        t0 = time.perf_counter()
        tt = bo.nhan_khung(kh, thoi_diem=k / FPS)
        thoi_gian.append(time.perf_counter() - t0)
        ma_theo_doan.setdefault(ten, Counter())[tt.ma] += 1
        so_lieu.setdefault(ten, []).append(tt.so_lieu)
        if tt.ma == "da_chup":
            chup.append((ten, tt.anh))

    if chi_tiet:
        for ten, dem in ma_theo_doan.items():
            sl = so_lieu[ten]
            tb = {kh: np.mean([s[kh] for s in sl if isinstance(s.get(kh), (int, float))])
                  for kh in ("chuyen_dong", "dien_tich", "lech_canh", "sang", "loa", "do_net", "giay", "khac_trang_cuoi")
                  if any(isinstance(s.get(kh), (int, float)) for s in sl)}
            print(f"{ten:12s} {dict(dem)}  " + "  ".join(f"{a}={b:.3g}" for a, b in tb.items()))

    doan_chup = [ten for ten, _ in chup]
    kiem(doan_chup == ["giu_trang1", "giu_trang2", "giu_trang3", "kin_khung"],
         f"chụp đúng 4 trang mới, mỗi trang một lần (đã chụp ở: {doan_chup})")
    for ten, ma in (("ban_trong", "khong_thay"), ("toi", "toi"), ("loa", "loa"), ("cat_mep", "cat_mep"),
                    ("xa", "xa"), ("nghieng", "nghieng")):
        dem = ma_theo_doan[ten]
        # 0,4 giây đầu đoạn còn trong thời gian chịu của lần giữ trước (báo 'dang_giu', không chụp)
        kiem(dem[ma] >= 0.7 * sum(dem.values()) and dem["da_chup"] == 0, f"đoạn '{ten}' báo '{ma}' ({dict(dem)})")
    cu = max(s.get("khac_trang_cuoi", 0) for s in so_lieu["ve_trang1"])
    moi = min(s["khac_trang_cuoi"] for s in so_lieu["giu_trang2"][:5] if "khac_trang_cuoi" in s)
    kiem(ma_theo_doan["ve_trang1"]["cho_trang_moi"] > 0 and "ve_trang1" not in doan_chup,
         f"va máy rồi về trang cũ: không chụp lại (độ khác trang cũ ≤ {cu:.2f}, trang mới ≥ {moi:.2f})")
    kiem(ma_theo_doan["va_may"]["rung"] > 0 or ma_theo_doan["va_may"]["cho_trang_moi"] > 0, "đang va máy: không chụp")

    def net(a):
        return float(np.abs(cv2.Laplacian(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.CV_16S)).mean())
    if chup:
        kiem(net(chup[0][1]) > 1.5 * net(mau_mo), f"ảnh chụp là khung nét (độ nét {net(chup[0][1]):.1f} "
                                                   f"so với khung mờ {net(mau_mo):.1f})")
        Path(__file__).with_name("ket_qua").mkdir(exist_ok=True)
        for i, (ten, a) in enumerate(chup, 1):
            ok, buf = cv2.imencode(".jpg", a)
            buf.tofile(str(Path(__file__).with_name("ket_qua") / f"tu-chup-{i}-{ten}.jpg"))
    tb = 1000 * float(np.median(thoi_gian))
    kiem(tb < 60, f"phân tích một khung hình 960×720 mất {tb:.0f} ms (trung vị)")

    print("\nTẤT CẢ ĐẠT" if not loi else f"\n{len(loi)} mục LỖI")
    sys.exit(1 if loi else 0)


if __name__ == "__main__":
    main()
