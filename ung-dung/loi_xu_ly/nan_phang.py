"""Tính năng 3: tìm mép giấy, sửa phối cảnh, sửa nghiêng, tách trang đôi."""
from __future__ import annotations

import math

import cv2
import numpy as np

from . import tim_mep

TI_LE_A4 = math.sqrt(2)


def sap_xep_goc(diem) -> np.ndarray:
    """Sắp 4 điểm theo thứ tự: trên trái, trên phải, dưới phải, dưới trái."""
    p = np.asarray(diem, np.float32).reshape(4, 2)
    tam = p.mean(axis=0)
    goc = np.arctan2(p[:, 1] - tam[1], p[:, 0] - tam[0])
    p = p[np.argsort(goc)]  # theo chiều kim đồng hồ (trục y hướng xuống)
    dau = int(np.argmin(p.sum(axis=1)))
    return np.roll(p, -dau, axis=0)


def _tu_giac(mat_na: np.ndarray, dien_tich: float) -> list[np.ndarray]:
    duong, _ = cv2.findContours(mat_na, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    kq = []
    for c in sorted(duong, key=cv2.contourArea, reverse=True)[:5]:
        if cv2.contourArea(c) < 0.15 * dien_tich:
            break
        bao = cv2.convexHull(c)
        chu_vi = cv2.arcLength(bao, True)
        for eps in (0.02, 0.03, 0.05, 0.08):
            xap_xi = cv2.approxPolyDP(bao, eps * chu_vi, True)
            if len(xap_xi) == 4:
                kq.append(xap_xi.reshape(4, 2).astype(np.float32))
                break
    return kq


def tim_mep_giay(anh: np.ndarray) -> np.ndarray | None:
    """Tìm 4 góc tờ giấy trong ảnh chụp (bộ tìm mép kiểu CamScanner, xem tim_mep.py). Trả None nếu giấy đã chiếm
    gần hết ảnh, khung chỉ là một phần tài liệu, hoặc không tìm được."""
    kq = tim_mep.tim_tu_giac(anh)
    if kq is None:
        return None
    goc, _ = kq
    h, w = anh.shape[:2]
    khung_anh = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
    if np.linalg.norm(goc - khung_anh, axis=1).max() < 0.015 * math.hypot(w, h):
        return None
    s = min(1.0, 800 / max(h, w))
    nho = cv2.resize(anh, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY)
    mo = cv2.GaussianBlur(xam, (5, 5), 0)
    hsv = cv2.cvtColor(nho, cv2.COLOR_BGR2HSV)
    _, sang = cv2.threshold(mo, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    giong_giay = sang & np.where(hsv[..., 1] < 70, 255, 0).astype(np.uint8)
    if _ngoai_khung_con_chu(goc * s, giong_giay, xam):
        return None
    return sap_xep_goc(goc)


def tim_mep_giay_cu(anh: np.ndarray) -> np.ndarray | None:
    """Bộ tìm mép cũ (đến 2026-11): đường bao lớn nhất của ảnh cạnh hoặc vùng sáng ít màu. Giữ để so sánh."""
    h, w = anh.shape[:2]
    s = min(1.0, 800 / max(h, w))
    nho = cv2.resize(anh, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    dien_tich = nho.shape[0] * nho.shape[1]
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY)
    mo = cv2.GaussianBlur(xam, (5, 5), 0)

    ung_vien = []
    # Cách 1: theo cạnh. Đường bao nằm ngoài mép thật một khoảng bằng độ giãn,
    # nên kéo các góc vào trong một chút.
    canh = cv2.dilate(cv2.Canny(mo, 40, 120), np.ones((3, 3), np.uint8), iterations=2)
    for q in _tu_giac(canh, dien_tich):
        tam = q.mean(axis=0)
        huong = tam - q
        q = q + huong / np.maximum(np.linalg.norm(huong, axis=1, keepdims=True), 1e-6) * 2.5
        ung_vien.append(q)

    # Cách 2: vùng sáng, ít màu (giấy trên nền bàn tối hoặc sặc sỡ).
    hsv = cv2.cvtColor(nho, cv2.COLOR_BGR2HSV)
    _, sang = cv2.threshold(mo, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    it_mau = np.where(hsv[..., 1] < 70, 255, 0).astype(np.uint8)
    mat_na = cv2.bitwise_and(sang, it_mau)
    mat_na = cv2.morphologyEx(mat_na, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    mat_na = cv2.morphologyEx(mat_na, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    ung_vien += _tu_giac(mat_na, dien_tich)

    hop_le = [q for q in ung_vien if cv2.contourArea(q) < 0.95 * dien_tich]
    if not hop_le:
        return None
    tot = max(hop_le, key=cv2.contourArea)
    if _ngoai_khung_con_chu(tot, sang & it_mau, xam):
        return None
    return sap_xep_goc(tot / s)


def _ngoai_khung_con_chu(khung: np.ndarray, giong_giay: np.ndarray, xam: np.ndarray) -> bool:
    """Vùng ngoài khung cũng là giấy có chữ (ví dụ chụp kín hai trang sách) thì
    khung chỉ là một phần tài liệu; cắt theo nó sẽ mất nội dung.

    Chỉ đếm mực nằm trên vùng giấy ngoài khung (đã lấp chữ, lùi khỏi mép vùng) và cách khung một dải: mép bìa sổ,
    mép tờ giấy lót bên dưới, bóng sát mép không bị tính là chữ."""
    trong = np.zeros(xam.shape, np.uint8)
    cv2.fillConvexPoly(trong, sap_xep_goc(khung).astype(np.int32), 1)
    ngoai = cv2.dilate(trong, np.ones((15, 15), np.uint8)) == 0
    if ngoai.mean() < 0.03:
        return False
    nhan = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    giay = cv2.erode(cv2.morphologyEx(giong_giay, cv2.MORPH_CLOSE, nhan), np.ones((9, 9), np.uint8)) > 0
    vung = ngoai & giay
    if vung.sum() < 0.5 * ngoai.sum():
        return False
    muc = cv2.adaptiveThreshold(xam, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 12)
    muc_ngoai = muc[vung].mean()
    muc_trong = muc[cv2.erode(trong, np.ones((15, 15), np.uint8)) > 0].mean()
    return bool(muc_ngoai > 0.3 * max(muc_trong, 1e-4))


def la_toan_anh(khung: np.ndarray, anh: np.ndarray) -> bool:
    h, w = anh.shape[:2]
    goc = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
    return bool(np.abs(sap_xep_goc(khung) - goc).max() <= 1.5)


def ti_le_phoi_canh(goc: np.ndarray, rong_anh: int, cao_anh: int) -> float | None:
    """Tỉ lệ cao/rộng thật của tờ giấy, suy từ 4 góc trong ảnh chụp.

    Theo Zhang & He (2007), "Whiteboard scanning and image enhancement": coi tâm
    ảnh là điểm chính, giải tiêu cự rồi tính tỉ lệ. Trả None khi ảnh chụp gần
    như thẳng góc (không giải được tiêu cự) để dùng cách đo cạnh.
    """
    u0, v0 = rong_anh / 2, cao_anh / 2
    tl, tr, br, bl = [np.array([x, y, 1.0]) for x, y in goc]
    m1, m2, m3, m4 = tl, tr, bl, br
    k2 = np.dot(np.cross(m1, m4), m3) / np.dot(np.cross(m2, m4), m3)
    k3 = np.dot(np.cross(m1, m4), m2) / np.dot(np.cross(m3, m4), m2)
    n2, n3 = k2 * m2 - m1, k3 * m3 - m1
    if abs(n2[2]) < 1e-9 or abs(n3[2]) < 1e-9:
        return None
    f2 = -((n2[0] * n3[0] - (n2[0] * n3[2] + n2[2] * n3[0]) * u0 + n2[2] * n3[2] * u0 * u0)
           + (n2[1] * n3[1] - (n2[1] * n3[2] + n2[2] * n3[1]) * v0 + n2[2] * n3[2] * v0 * v0)) / (n2[2] * n3[2])
    if not np.isfinite(f2) or f2 <= 0:
        return None
    f = math.sqrt(f2)
    a_inv = np.linalg.inv(np.array([[f, 0, u0], [0, f, v0], [0, 0, 1.0]]))
    q = a_inv.T @ a_inv
    rong2 = float(n2 @ q @ n2)
    cao2 = float(n3 @ q @ n3)
    if rong2 <= 0 or cao2 <= 0:
        return None
    r = math.sqrt(cao2 / rong2)
    # Ước lượng vô lý (tiêu cự quá nhỏ, tứ giác méo) thì bỏ
    return r if 0.25 < r < 4 and f > 0.3 * max(rong_anh, cao_anh) else None


NOI_KHUNG = 0.025  # nới khung khi nắn phẳng (phần mỗi cạnh): mép trang cong phình ra ngoài đường nối hai góc


def lam_phang(anh: np.ndarray, khung, khop_a4: bool = True, noi: float = 0.0) -> np.ndarray:
    """Biến đổi phối cảnh đưa tứ giác `khung` về hình chữ nhật. noi > 0: lấy thêm một dải quanh tứ giác (theo phần
    bề ngang, bề cao trang) để chữ ở chỗ mép trang cong phình ra ngoài đường nối hai góc không bị cắt lẹm; dải thừa
    (nền bàn) do bước cắt sát chữ bỏ đi."""
    if la_toan_anh(np.asarray(khung, np.float32), anh):
        return anh
    tl, tr, br, bl = sap_xep_goc(khung)
    rong = max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl))
    cao = max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))
    r = ti_le_phoi_canh(np.array([tl, tr, br, bl]), anh.shape[1], anh.shape[0])
    if r is not None:  # giữ diện tích, chỉnh lại tỉ lệ theo hình học phối cảnh
        dt = rong * cao
        rong, cao = math.sqrt(dt / r), math.sqrt(dt * r)
    if khop_a4:
        r = cao / rong
        for dich in (TI_LE_A4, 1 / TI_LE_A4):
            if abs(r / dich - 1) < 0.06:
                cao = rong * dich
    rong, cao = max(int(round(rong)), 10), max(int(round(cao)), 10)
    nx, ny = int(round(noi * rong)), int(round(noi * cao))
    dich = np.array([[nx, ny], [nx + rong - 1, ny], [nx + rong - 1, ny + cao - 1], [nx, ny + cao - 1]], np.float32)
    m = cv2.getPerspectiveTransform(np.array([tl, tr, br, bl], np.float32), dich)
    ra = cv2.warpPerspective(anh, m, (rong + 2 * nx, cao + 2 * ny), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    if (nx or ny) and ra.ndim == 3:
        ra = _xoa_nen_noi(ra, nx, ny)
    return ra


def _xoa_nen_noi(anh: np.ndarray, nx: int, ny: int) -> np.ndarray:
    """Dải nới quanh trang (ngoài tứ giác mép giấy) có nền bàn, bìa sách, ngón tay: tô màu giấy những mảng lớn, tối
    hoặc có màu, chạm mép ảnh. Nét chữ (mảnh) ở chỗ mép trang cong phình ra ngoài thì giữ."""
    h, w = anh.shape[:2]
    trong = anh[ny:h - ny, nx:w - nx]
    hsv = cv2.cvtColor(anh, cv2.COLOR_BGR2HSV)
    giay_v = float(np.median(cv2.cvtColor(trong, cv2.COLOR_BGR2HSV)[..., 2]))
    khac = ((hsv[..., 2] < giay_v - 45) | (hsv[..., 1] > 70)).astype(np.uint8)
    # chỉ xét dải nới (và một chút vào trong, chỗ mép giấy bị bóng)
    dai = np.ones((h, w), np.uint8)
    dai[ny + max(2, ny // 3):h - ny - max(2, ny // 3), nx + max(2, nx // 3):w - nx - max(2, nx // 3)] = 0
    khac &= dai
    k = max(5, int(0.012 * min(h, w))) | 1
    lon = cv2.morphologyEx(khac, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(lon, 8)
    xoa = np.zeros((h, w), np.uint8)
    for i in range(1, n):
        x, y, cw, ch = tk[i, :4]
        if x == 0 or y == 0 or x + cw >= w or y + ch >= h:
            xoa[nhan == i] = 1
    if not xoa.any():
        return anh
    xoa = cv2.dilate(xoa, np.ones((5, 5), np.uint8))
    mau = np.median(trong.reshape(-1, 3), axis=0)
    ra = anh.copy()
    ra[xoa > 0] = mau
    return ra


def xoay_anh(anh: np.ndarray, goc_do: float, mau_nen=None) -> np.ndarray:
    """Xoay ngược chiều kim đồng hồ `goc_do` độ, nới khung để không mất nội dung."""
    if abs(goc_do) < 1e-6:
        return anh
    h, w = anh.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), goc_do, 1.0)
    cos, sin = abs(m[0, 0]), abs(m[0, 1])
    rong, cao = int(h * sin + w * cos + 0.5), int(h * cos + w * sin + 0.5)
    m[0, 2] += rong / 2 - w / 2
    m[1, 2] += cao / 2 - h / 2
    if mau_nen is None:
        mau_nen = np.median(anh.reshape(-1, anh.shape[2]), axis=0)
    return cv2.warpAffine(anh, m, (rong, cao), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=tuple(float(x) for x in mau_nen))


def xoay_90(anh: np.ndarray, goc_cung_kim: int) -> np.ndarray:
    goc_cung_kim %= 360
    if goc_cung_kim == 90:
        return cv2.rotate(anh, cv2.ROTATE_90_CLOCKWISE)
    if goc_cung_kim == 180:
        return cv2.rotate(anh, cv2.ROTATE_180)
    if goc_cung_kim == 270:
        return cv2.rotate(anh, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return anh


def do_nghieng(anh: np.ndarray, gioi_han: float = 6.0) -> float:
    """Góc (độ, ngược chiều kim đồng hồ) cần xoay để dòng chữ nằm ngang.

    Dùng phép chiếu ngang: dòng chữ thẳng cho đường chiếu có các đỉnh sắc nhất.
    """
    xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY) if anh.ndim == 3 else anh
    s = min(1.0, 1500 / max(xam.shape))
    xam = cv2.resize(xam, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    nhi_phan = cv2.adaptiveThreshold(xam, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 15)
    if nhi_phan.mean() / 255 < 0.003:
        return 0.0
    h, w = nhi_phan.shape
    tam = (w / 2, h / 2)

    def diem(a: float) -> float:
        m = cv2.getRotationMatrix2D(tam, a, 1.0)
        xoay = cv2.warpAffine(nhi_phan, m, (w, h), flags=cv2.INTER_NEAREST)
        chieu = xoay.sum(axis=1, dtype=np.float64)
        return float(np.sum(np.diff(chieu) ** 2))

    tho = np.arange(-gioi_han, gioi_han + 1e-6, 0.5)
    tot = max(tho, key=diem)
    min_ = np.arange(tot - 0.5, tot + 0.5 + 1e-6, 0.1)
    tot = float(max(min_, key=diem))
    return 0.0 if abs(tot) < 0.1 else round(tot, 2)


def xoa_vien_toi(anh: np.ndarray, be_rong: float = 0.02) -> np.ndarray:
    """Tô trắng dải nền bàn sót lại ở mép trang sau khi cắt (dùng cho ảnh đã làm sạch).

    Viền là vùng tối chạm mép, mảnh (dày không quá `be_rong` kích thước) và
    dài dọc theo mép (≥ 10% cạnh); chữ ở lề ngắn hơn nhiều nên được giữ.
    """
    toi = ((anh.min(axis=2) if anh.ndim == 3 else anh) < 200).astype(np.uint8)
    h, w = toi.shape
    dh, dw = max(3, int(h * be_rong)), max(3, int(w * be_rong))
    mat_na = np.zeros_like(toi)
    # Xét riêng từng dải mép, vì viền bốn cạnh thường nối liền qua các góc.
    for lat, doc, ngoai in ((np.s_[:dh, :], False, 0), (np.s_[h - dh:, :], False, 1),
                            (np.s_[:, :dw], True, 2), (np.s_[:, w - dw:], True, 3)):
        dai = toi[lat]
        # nối các đoạn viền đứt quãng dọc theo mép
        k = max(3, int(0.03 * (h if doc else w)))
        noi = cv2.morphologyEx(dai, cv2.MORPH_CLOSE, np.ones((k, 1) if doc else (1, k), np.uint8))
        n, nhan, tk, _ = cv2.connectedComponentsWithStats(noi, connectivity=8)
        chieu_dai = tk[1:, cv2.CC_STAT_HEIGHT if doc else cv2.CC_STAT_WIDTH]
        rh, rw = dai.shape
        l, t, cw, ch = (tk[1:, c] for c in (cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP, cv2.CC_STAT_WIDTH, cv2.CC_STAT_HEIGHT))
        # vệt nền dài dọc mép, hoặc mảnh nền chạm sát mép ảnh (mép trang cong để lại vệt đứt đoạn)
        cham_mep = (t == 0, t + ch == rh, l == 0, l + cw == rw)[ngoai]
        xoa = np.concatenate([[False], (chieu_dai >= 0.1 * (h if doc else w)) | cham_mep])
        mat_na[lat] |= xoa[nhan].astype(np.uint8) & dai
    if not mat_na.any():
        return anh
    mat_na = cv2.dilate(mat_na, np.ones((3, 3), np.uint8))
    kq = anh.copy()
    kq[mat_na > 0] = 255
    return kq


def _khe_gay(anh: np.ndarray):
    """Đường cắt giữa hai trang sách mở: (x ở mép trên, x ở mép dưới) theo tọa độ ảnh, đi giữa khe trắng giữa hai khối
    chữ (không theo bóng gáy: bóng thường lệch sang một trang, cắt theo bóng thì phạm vào chữ đầu dòng). Khe xiên khi
    cặp trang nghiêng: đo khe theo từng dải ngang rồi khớp một đường thẳng. None nếu không thấy khe rõ."""
    h, w = anh.shape[:2]
    s = min(1.0, 1000 / w)
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    hn, wn = xam.shape
    muc = cv2.adaptiveThreshold(xam, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 15)
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(muc, 8)
    if n < 40:
        return None
    x, y, cw, ch, dt = (tk[1:, i] for i in range(5))
    vua = (ch >= 3) & (ch < 0.05 * hn) & (cw < 0.1 * wn)
    if vua.sum() < 30:
        return None
    cao = float(np.median(ch[vua]))
    # nét chữ: cỡ chữ, không chạm mép ảnh; nếp gáy, mép giấy (dài, mảnh) và đốm nhỏ không tính
    chu = vua & (ch <= 3 * cao) & (cw <= 6 * cao) & (dt >= 3) & (x > 1) & (x + cw < wn - 1)
    mat = np.isin(nhan, np.flatnonzero(chu) + 1)
    lo, hi = int(0.3 * wn), int(0.7 * wn)

    def khe(cot, toi_thieu):
        """Các đoạn cột không mực (từ toi_thieu cột) trong vùng giữa: [(đầu, cuối)]."""
        trong = cot[lo:hi] == 0
        ra, bd = [], None
        for k, t in enumerate(trong):
            if t and bd is None:
                bd = k
            if (not t or k == len(trong) - 1) and bd is not None:
                kt = k if not t else k + 1
                if kt - bd >= toi_thieu:
                    ra.append((lo + bd, lo + kt))
                bd = None
        return ra

    # khe chung cả trang: đoạn trắng rộng nhất ở giữa (lề trong hai trang cộng lại, rộng hơn mọi khoảng cách chữ)
    cot = mat.sum(axis=0)
    # cho phép vài điểm mực lẻ (dấu, bụi) trong khe
    cot = np.where(cot <= max(1, int(0.002 * hn)), 0, cot)
    chung = khe(cot, max(3, int(1.5 * cao)))
    if not chung:
        return None
    g0, g1 = max(chung, key=lambda d: d[1] - d[0])
    # hai bên khe đều phải có chữ (cặp trang thật)
    if cot[:g0].sum() < 0.2 * cot.sum() or cot[g1:].sum() < 0.2 * cot.sum():
        return None
    # theo dải ngang: tâm khe ở từng dải (dải có chữ cả hai bên, khe không quá rộng do dòng ngắn)
    so_dai = 12
    tam, yy, rong = [], [], []
    for b in range(so_dai):
        y0, y1 = b * hn // so_dai, (b + 1) * hn // so_dai
        c = mat[y0:y1].sum(axis=0)
        cac = khe(c, 2)
        if not cac:
            continue
        # đoạn trắng chồng lên khe chung nhiều nhất
        d = max(cac, key=lambda d: min(d[1], g1 + 2 * (g1 - g0)) - max(d[0], g0 - 2 * (g1 - g0)))
        if d[1] <= g0 - (g1 - g0) or d[0] >= g1 + (g1 - g0):
            continue
        if c[:d[0]].sum() < 3 or c[d[1]:].sum() < 3:
            continue
        tam.append((d[0] + d[1]) / 2)
        yy.append((y0 + y1) / 2)
        rong.append(d[1] - d[0])
    x_tren = x_duoi = (g0 + g1) / 2
    if len(tam) >= 4:
        tam, yy, rong = np.array(tam), np.array(yy), np.array(rong, float)
        # bỏ dải có khe quá rộng (dòng cuối đoạn ngắn, dải trống một bên)
        giu = rong <= 1.6 * np.median(rong)
        if giu.sum() >= 4:
            tam, yy = tam[giu], yy[giu]
            k, c0 = np.polyfit(yy, tam, 1)
            for _ in range(2):
                du = np.abs(tam - (k * yy + c0))
                giu = du <= max(2.0, 2.5 * np.median(du))
                if giu.sum() < 4:
                    break
                k, c0 = np.polyfit(yy[giu], tam[giu], 1)
            k = float(np.clip(k, -0.1, 0.1))  # gáy nghiêng tối đa ~6°
            x_tren, x_duoi = c0, k * hn + c0
    return x_tren / s, x_duoi / s


def cat_theo_duong(anh: np.ndarray, x_tren: float, x_duoi: float) -> tuple[np.ndarray, np.ndarray]:
    """Cắt ảnh làm hai theo đường thẳng (x_tren ở mép trên, x_duoi ở mép dưới). Phần của nửa này nằm bên kia đường
    cắt (đường xiên) được lấp bằng chính điểm ảnh trên đường cắt (nền khe gáy kéo dài), không lẫn chữ trang bên."""
    h, w = anh.shape[:2]
    yy = np.arange(h, dtype=np.float32)
    duong = (x_tren + (x_duoi - x_tren) * yy / max(h - 1, 1)).astype(np.float32)
    a = int(np.clip(np.ceil(duong.max()), 1, w - 1))
    b = int(np.clip(np.floor(duong.min()), 1, w - 1))
    xt = np.arange(a, dtype=np.float32)
    mx = np.minimum(xt[None, :], duong[:, None])
    my = np.repeat(yy[:, None], a, axis=1)
    trai = cv2.remap(anh, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    xp = np.arange(b, w, dtype=np.float32)
    mx = np.maximum(xp[None, :], duong[:, None])
    my = np.repeat(yy[:, None], w - b, axis=1)
    phai = cv2.remap(anh, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return trai, phai


def tach_trang_doi(anh: np.ndarray) -> list[np.ndarray]:
    """Tách ảnh hai trang sách mở thành hai trang, cắt giữa khe trắng ở gáy (đường thẳng, có thể xiên)."""
    h, w = anh.shape[:2]
    if w < h:
        return [anh]
    # khổ gần vuông (không tìm được mép, cặp trang hẹp) vẫn tách nếu thấy rõ khe gáy giữa hai khối chữ
    duong = _khe_gay(anh)
    if duong is not None:
        return list(cat_theo_duong(anh, *duong))
    if w < 1.15 * h:
        return [anh]
    # không thấy khe chữ rõ (trang ít chữ, ảnh): theo bóng gáy hoặc cột ít mực nhất
    s = 800 / w
    xam = cv2.cvtColor(cv2.resize(anh, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    cot = cv2.GaussianBlur(xam.mean(axis=0).reshape(1, -1), (0, 0), 5).ravel()
    lo, hi = int(0.35 * len(cot)), int(0.65 * len(cot))
    vung = cot[lo:hi]
    i = int(np.argmin(vung))
    if vung[i] < np.median(cot) - 12:
        x = lo + i  # bóng tối ở gáy
    else:
        muc = cv2.GaussianBlur((xam < 128).mean(axis=0).reshape(1, -1), (0, 0), 5).ravel()
        x = lo + int(np.argmin(muc[lo:hi]))  # khe trắng giữa hai trang
    x = int(round(x / s))
    return [anh[:, :x], anh[:, x:]]
