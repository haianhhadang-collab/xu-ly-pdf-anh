"""Nắn trang cong (sách mở, giấy cong vênh) theo dòng chữ.

Trang đã cắt và nắn phối cảnh theo 4 góc vẫn còn cong nếu giấy không phẳng: dòng chữ võng lên gần gáy sách. Cách làm:

1. Nhị phân hóa chữ, nối các chữ cùng dòng bằng phép đóng ngang, giữ các khối dài và mảnh (dòng chữ).
2. Mỗi dòng: lấy đường giữa (trung bình tung độ nét mực theo từng cột), khớp đa thức bậc 3 có loại điểm lạc.
3. Độ lệch D = tung độ đường cong − đường thẳng chung (cùng độ dốc trung vị của mọi dòng, đặt ở độ cao trung bình
   của dòng). Khớp một mặt trơn D(x, y) (đa thức bậc 4 theo x, bậc 2 theo y) cho cả trang.
4. Ánh xạ ngược: điểm (x, y) của ảnh ra lấy từ (x, y + D(x, y)) của ảnh vào. Không cắt bớt: ảnh ra cùng cỡ, phần
   thiếu ở mép lấy theo điểm ảnh mép.

Trang phẳng (độ lệch nhỏ hơn 0,3% chiều cao), quá ít dòng, hoặc mặt khớp không tin cậy thì trả nguyên ảnh.
"""
from __future__ import annotations

import math

import cv2
import numpy as np

CANH_XU_LY = 1400


def _dong_chu(xam: np.ndarray) -> list[np.ndarray]:
    """Các dòng chữ: mỗi dòng là mảng (x, y_giữa) theo từng cột có mực."""
    h, w = xam.shape
    muc = cv2.adaptiveThreshold(xam, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 15)
    # bỏ đốm nhỏ, bỏ khối lớn (con dấu, ảnh, khung bảng) để chỉ còn nét chữ
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(muc, 8)
    cao = tk[1:, cv2.CC_STAT_HEIGHT]
    if n < 20:
        return []
    cao_chu = float(np.median(cao[(cao > 3) & (cao < 0.05 * h)])) if np.any((cao > 3) & (cao < 0.05 * h)) else 10.0
    giu = np.zeros(n, np.uint8)
    for i in range(1, n):
        ch, cw, dt = tk[i, cv2.CC_STAT_HEIGHT], tk[i, cv2.CC_STAT_WIDTH], tk[i, cv2.CC_STAT_AREA]
        if 2 <= ch <= 3 * cao_chu and cw <= 6 * cao_chu and dt >= 4:
            giu[i] = 255
    chu = giu[nhan]
    # nối chữ trong dòng: đóng ngang cỡ ~1,5 chiều cao chữ, rồi mở dọc nhẹ để tách dòng sát nhau
    kx = max(5, int(1.6 * cao_chu))
    dong = cv2.morphologyEx(chu, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (kx, 1)))
    dong = cv2.morphologyEx(dong, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, kx // 2), 1)))
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(dong, 8)
    kq = []
    for i in range(1, n):
        x0, y0, cw, ch = tk[i, :4]
        if cw < 0.15 * w or ch > 3.5 * cao_chu or cw < 8 * ch:
            continue
        vung = (nhan[y0:y0 + ch, x0:x0 + cw] == i) & (chu[y0:y0 + ch, x0:x0 + cw] > 0)
        cot = vung.sum(axis=0)
        ys = np.arange(ch, dtype=np.float32)[:, None]
        co = cot >= 2
        if co.sum() < 0.3 * cw:
            continue
        yg = (vung * ys).sum(axis=0)[co] / cot[co] + y0
        xs = np.arange(cw)[co] + x0
        # gộp theo ô 4 cột cho bớt nhiễu
        o = xs // 4
        _, chi_so, dem = np.unique(o, return_inverse=True, return_counts=True)
        kq.append(np.stack([np.bincount(chi_so, xs) / dem, np.bincount(chi_so, yg) / dem], 1))
    return kq


def _khop_dong(d: np.ndarray, w: int) -> np.ndarray | None:
    """Khớp y = f(x) bậc 3 (bậc 2 nếu dòng ngắn), loại điểm lạc; trả hệ số theo x chuẩn hóa x/w."""
    x, y = d[:, 0] / w, d[:, 1]
    bac = 3 if (x.max() - x.min()) > 0.4 else 2
    giu = np.ones(len(x), bool)
    for _ in range(3):
        if giu.sum() < bac + 4:
            return None
        hs = np.polyfit(x[giu], y[giu], bac)
        sai = np.abs(np.polyval(hs, x) - y)
        nguong = max(1.5, 2.5 * float(np.median(sai[giu])))
        giu = sai < nguong
    return hs


def tinh_do_lech(anh: np.ndarray):
    """Mặt độ lệch dọc D trên lưới thô (theo ảnh vào) và độ lệch lớn nhất (px); None nếu trang coi như phẳng."""
    h, w = anh.shape[:2]
    s = min(1.0, CANH_XU_LY / max(h, w))
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    hn, wn = xam.shape
    dong = _dong_chu(xam)
    if len(dong) < 3:
        return None
    mau = []
    for d in dong:
        hs = _khop_dong(d, wn)
        if hs is None:
            continue
        x = np.linspace(d[:, 0].min(), d[:, 0].max(), 24)
        mau.append((x, np.polyval(hs, x / wn)))
    if len(mau) < 3:
        return None
    # độ dốc chung của dòng (trung vị), để chỉ nắn phần cong, phần nghiêng để bước sửa nghiêng xoay
    doc = float(np.median([np.polyfit(x, y, 1)[0] for x, y in mau]))
    X, Y, D = [], [], []
    for x, y in mau:
        goc = float(np.mean(y - doc * x))
        thang = goc + doc * x
        X.append(x)
        Y.append(thang)
        D.append(y - thang)
    X, Y, D = (np.concatenate(v) for v in (X, Y, D))
    # mặt trơn D(x, y): đa thức bậc 4 theo x, bậc 2 theo y (bậc y giảm nếu dòng ít)
    by = 2 if len(mau) >= 6 else (1 if len(mau) >= 4 else 0)
    u, v = X / wn * 2 - 1, Y / hn * 2 - 1
    cot = [(j, k) for j in range(5) for k in range(by + 1)]
    A = np.stack([u ** j * v ** k for j, k in cot], 1)
    hs, *_ = np.linalg.lstsq(A, D, rcond=None)
    du = A @ hs - D
    lech_mau = float(np.abs(D).max())
    if lech_mau < 0.003 * hn or float(np.sqrt(np.mean(du ** 2))) > 0.45 * float(np.sqrt(np.mean(D ** 2))):
        return None
    # lưới thô 48 × 64 trên ảnh vào; ngoài vùng có dòng chữ thì giữ độ lệch ở mép vùng (không ngoại suy đa thức)
    gx, gy = np.meshgrid(np.linspace(0, wn - 1, 48), np.linspace(0, hn - 1, 64))
    gu = np.clip(gx / wn * 2 - 1, X.min() / wn * 2 - 1, X.max() / wn * 2 - 1)
    gv = np.clip(gy / hn * 2 - 1, Y.min() / hn * 2 - 1, Y.max() / hn * 2 - 1)
    luoi = sum(c * gu ** j * gv ** k for c, (j, k) in zip(hs, cot))
    luoi = np.clip(luoi, -1.5 * lech_mau, 1.5 * lech_mau)
    return (luoi / s).astype(np.float32), lech_mau / s


def tim_gay(anh: np.ndarray) -> int | None:
    """Cột gáy sách nếu ảnh là hai trang mở (khổ ngang, giữa ảnh có một dải gần như không có chữ); None nếu không."""
    h, w = anh.shape[:2]
    if w < 0.95 * h:
        return None
    s = min(1.0, 1000 / w)
    xam = cv2.cvtColor(cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)         if anh.ndim == 3 else cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    muc = cv2.adaptiveThreshold(xam, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 15).sum(axis=0).astype(float)
    m = np.convolve(muc, np.ones(15) / 15, "same")
    lo, hi = int(0.35 * len(m)), int(0.65 * len(m))
    x = lo + int(np.argmin(m[lo:hi]))
    # ảnh trang sách người dùng chụp: mực ở gáy 0,05–0,15 lần trung bình; trang đơn: > 1
    if m[x] > 0.3 * max(m.mean(), 1e-6):
        return None
    return int(round(x / s))


def nan_trang_cong(anh: np.ndarray) -> np.ndarray:
    """Nắn trang cong theo dòng chữ; trang phẳng hoặc không đủ dòng chữ thì trả nguyên ảnh. Ảnh hai trang sách mở
    (hai mặt cong ngược nhau, một mặt khớp chung không được) thì tách ở gáy, nắn từng trang rồi ghép lại."""
    gay = tim_gay(anh)
    if gay is not None:
        from .nan_phang import _khe_gay, cat_theo_duong

        # cắt giữa khe trắng ở gáy (đường có thể xiên), không cắt qua chữ đầu dòng
        duong = _khe_gay(anh)
        if duong is not None:
            trai, phai = cat_theo_duong(anh, *duong)
        else:
            trai, phai = anh[:, :gay], anh[:, gay:]
        # mỗi trang nắn và xoay thẳng riêng theo dòng chữ của nó
        trai = _xoay_thang(_nan_mot(np.ascontiguousarray(trai)))
        phai = _xoay_thang(_nan_mot(np.ascontiguousarray(phai)))
        return _ghep_ngang(trai, phai)
    return _nan_mot(anh)


def _nan_mot(anh: np.ndarray) -> np.ndarray:
    kq = tinh_do_lech(anh)
    if kq is not None:
        luoi, _ = kq
        h, w = anh.shape[:2]
        D = cv2.resize(luoi, (w, h), interpolation=cv2.INTER_CUBIC)
        mx, my = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        anh = cv2.remap(anh, mx, my + D, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return nan_le(anh)


def _xoay_thang(anh: np.ndarray) -> np.ndarray:
    """Xoay một trang cho dòng chữ nằm ngang theo độ dốc trung vị của chính nó (cặp trang sách mở: mỗi trang nghiêng
    một kiểu, bước sửa nghiêng chung cho cả ảnh chỉ thẳng được một trang). Nới khung, tô màu nền: không đẩy chữ sát
    mép ra ngoài ảnh (cắt lẹm)."""
    from .nan_phang import xoay_anh

    h, w = anh.shape[:2]
    s = min(1.0, CANH_XU_LY / max(h, w))
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    doc = [np.polyfit(d[:, 0], d[:, 1], 1)[0] for d in _dong_chu(xam) if len(d) >= 4]
    if len(doc) < 5:
        return anh
    goc = math.degrees(math.atan(float(np.median(doc))))
    if abs(goc) < 0.3 or abs(goc) > 6:
        return anh
    return xoay_anh(anh, goc)


def _ghep_ngang(trai: np.ndarray, phai: np.ndarray) -> np.ndarray:
    """Ghép hai trang cạnh nhau; trang thấp hơn được đệm màu nền trên dưới cho bằng chiều cao."""
    h = max(trai.shape[0], phai.shape[0])
    ra = []
    for t in (trai, phai):
        d = h - t.shape[0]
        if d:
            nen = tuple(float(x) for x in np.median(t.reshape(-1, t.shape[2]), axis=0)) if t.ndim == 3 else float(np.median(t))
            t = cv2.copyMakeBorder(t, d // 2, d - d // 2, 0, 0, cv2.BORDER_CONSTANT, value=nen)
        ra.append(t)
    return np.hstack(ra)


def _khop_le(y: np.ndarray, x: np.ndarray, phia: int, cao_chu: float, h: int):
    """Khớp đường lề x = f(y) (bậc 2, bậc 1 nếu ít dòng) qua đầu (phia=+1: lề trái, loại dòng thụt vào) hoặc cuối dòng
    (phia=-1: lề phải, loại dòng ngắn). Trả (hệ số theo y/h, số dòng giữ) hoặc None."""
    giu = np.ones(len(y), bool)
    hs = None
    for _ in range(4):
        if giu.sum() < 5:
            return None
        bac = 2 if giu.sum() >= 9 else 1
        hs = np.polyfit(y[giu] / h, x[giu], bac)
        r = (x - np.polyval(hs, y / h)) * phia  # > 0: thụt vào trong khối (dòng đầu đoạn, dòng cuối đoạn, tiêu đề)
        giu = (r < max(0.6 * cao_chu, 2.5 * float(np.median(np.abs(r[giu]))))) & (r > -2.5 * cao_chu)
    if giu.sum() < 5 or np.ptp(y[giu]) < 0.35 * h:
        return None
    return hs, int(giu.sum())


def _le_khoi(anh: np.ndarray):
    """Hai lề của khối chữ trên ảnh thu nhỏ: (s, hn, wn, hệ số lề trái, hệ số lề phải, độ dốc lề đích k, y0, y1,
    lề trái đích tại giữa, bề ngang đích, độ lệch lề lớn nhất px ảnh nhỏ); None nếu không đo được."""
    h, w = anh.shape[:2]
    s = min(1.0, CANH_XU_LY / max(h, w))
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    hn, wn = xam.shape
    dong = _dong_chu(xam)
    if len(dong) < 6:
        return None
    dau, cuoi, doc = [], [], []
    for d in dong:
        hs = _khop_dong(d, wn)
        if hs is None:
            continue
        x0, x1 = float(d[:, 0].min()), float(d[:, 0].max())
        dau.append((float(np.polyval(hs, x0 / wn)), x0))
        cuoi.append((float(np.polyval(hs, x1 / wn)), x1))
        doc.append((np.polyval(hs, x1 / wn) - np.polyval(hs, x0 / wn)) / max(x1 - x0, 1.0))
    if len(dau) < 6:
        return None
    dau, cuoi = np.array(dau), np.array(cuoi)
    # chiều cao chữ ước theo khoảng cách dòng (dòng chữ cách nhau ~1,6–2 lần chiều cao chữ)
    yy = np.sort(dau[:, 0])
    cao_chu = float(np.median(np.diff(yy))) / 1.8
    trai = _khop_le(dau[:, 0], dau[:, 1], +1, cao_chu, hn)
    phai = _khop_le(cuoi[:, 0], cuoi[:, 1], -1, cao_chu, hn)
    if trai is None or phai is None:
        return None
    y0 = max(min(dau[:, 0].min(), cuoi[:, 0].min()), 0.0)
    y1 = min(max(dau[:, 0].max(), cuoi[:, 0].max()), hn - 1.0)
    ys = np.linspace(y0, y1, 64)
    xl, xr = np.polyval(trai[0], ys / hn), np.polyval(phai[0], ys / hn)
    rong = xr - xl
    if rong.min() < 0.3 * wn or rong.min() < 0.8 * rong.max():
        return None  # khối chữ hẹp bất thường hoặc hai lề lệch nhau quá nhiều: không tin
    k = -float(np.median(doc))  # lề đích vuông góc với dòng chữ: x giảm theo độ dốc dòng
    ym = 0.5 * (y0 + y1)
    xl0, rong0 = float(np.median(xl)), float(np.median(rong))
    xl_dich = xl0 + k * (ys - ym)
    lech = float(max(np.abs(xl - xl_dich).max(), np.abs(xr - (xl_dich + rong0)).max()))
    return s, hn, wn, trai[0], phai[0], k, y0, y1, xl0, rong0, lech


def do_lech_le(anh: np.ndarray) -> float | None:
    """Độ lệch lớn nhất của lề khối chữ so với hai đường thẳng vuông góc dòng chữ, theo % bề ngang ảnh (kiểm thử)."""
    kq = _le_khoi(anh)
    return None if kq is None else 100.0 * kq[-1] / kq[2]


def nan_le(anh: np.ndarray) -> np.ndarray:
    """Nắn vuông khối chữ: lề trái, lề phải của khối chữ (đầu và cuối các dòng) xiên hay cong do trang cong, chụp lệch,
    thì kéo ngang từng hàng điểm ảnh cho hai lề thành đường thẳng vuông góc với dòng chữ, bề ngang dòng bằng nhau.
    Chỉ dời theo chiều ngang (dòng chữ đã nắn thẳng ở bước trước). Lề đã thẳng, quá ít dòng, khối chữ lệch bất thường
    thì trả nguyên ảnh. Chỗ lệch đột ngột trên vài dòng liền (bậc) không nắn: không phân biệt được với đoạn thụt lề."""
    kq = _le_khoi(anh)
    if kq is None:
        return anh
    s, hn, wn, trai, phai, k, y0, y1, xl0, rong0, lech = kq
    if lech < max(1.5, 0.004 * wn) or lech > 0.08 * wn:
        return anh  # lề đã thẳng, hoặc lệch quá lớn (khớp sai)
    h, w = anh.shape[:2]
    ym = 0.5 * (y0 + y1)
    # ánh xạ ngược theo từng hàng: x đích → x nguồn; ngoài khoảng có dòng chữ thì giữ như hàng mép
    yh = np.clip(np.arange(h, dtype=np.float64) * s, y0, y1)
    xl_h = np.polyval(trai, yh / hn)
    tl_h = (np.polyval(phai, yh / hn) - xl_h) / rong0
    dich_h = xl0 + k * (yh - ym)
    # nới khung hai bên bằng độ dời lớn nhất, tô màu nền: chữ sát mép không bị đẩy ra ngoài ảnh (cắt lẹm)
    nl = int(math.ceil(lech / s)) + 4
    x = (np.arange(w + 2 * nl, dtype=np.float64) - nl) * s
    mx = ((xl_h[:, None] + (x[None, :] - dich_h[:, None]) * tl_h[:, None]) / s).astype(np.float32)
    my = np.repeat(np.arange(h, dtype=np.float32)[:, None], w + 2 * nl, 1)
    nen = tuple(float(v) for v in np.median(anh.reshape(-1, anh.shape[2]), axis=0)) if anh.ndim == 3 else float(np.median(anh))
    return cv2.remap(anh, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=nen)
