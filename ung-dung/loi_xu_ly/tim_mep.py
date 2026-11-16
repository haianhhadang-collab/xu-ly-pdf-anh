"""Tìm mép giấy kiểu CamScanner: gom ứng viên tứ giác từ nhiều nguồn, chấm điểm theo độ bám cạnh, tinh chỉnh từng cạnh.

Bộ tìm mép cũ (`nan_phang.tim_mep_giay_cu`) chỉ lấy đường bao lớn nhất của ảnh cạnh hoặc vùng sáng ít màu, nên trượt khi
giấy nằm trên bàn trắng, nền lộn xộn, hay đường bao dính vào đồ vật bên cạnh. Cách làm ở đây:

1. Thu nhỏ ảnh (cạnh dài 640), xóa chữ bằng phép đóng hình thái (chữ tối trên giấy sáng biến mất, mép giấy còn),
   đổi sang Lab để thấy cả mép chỉ khác màu (giấy ngà trên bàn xám trắng).
2. Ứng viên tứ giác lấy từ: đường bao của ảnh cạnh Canny (hai mức ngưỡng), vùng Otsu sáng / tối, phân cụm màu k-means,
   và ghép 4 đường thẳng Hough (đường bao đứt đoạn vì ngón tay, bóng đổ vẫn ghép được).
3. Chấm điểm: rải điểm dọc từng cạnh, đo đạo hàm vuông góc với cạnh; cạnh thật có đạo hàm mạnh và cùng dấu
   (giấy sáng hơn nền, hoặc ngược lại) trên gần hết chiều dài. Cạnh nằm ngoài khung ảnh được điểm trung tính.
4. Tinh chỉnh ở ảnh lớn hơn (cạnh dài 1280): dò cực đại đạo hàm dọc pháp tuyến, khớp đường thẳng (Huber),
   giao các cạnh kề nhau ra 4 góc.
"""
from __future__ import annotations

import itertools
import math

import cv2
import numpy as np

CANH_NHO = 640
CANH_TINH = 1280
NGUONG_DOC = (8.0, 24.0)  # khoảng ngưỡng đạo hàm Sobel (thang Lab 0..255) để coi là có mép


def _nguong(gx: np.ndarray, gy: np.ndarray) -> float:
    """Ngưỡng mép theo độ nhiễu nền: giấy trên bàn trắng mép chỉ chênh ~15, giấy trên bàn gỗ chênh ~80 nhưng vân gỗ
    cũng có đạo hàm ~7. Lấy 2,5 lần phân vị 90 của độ dốc toàn ảnh (đã xóa chữ) cộng 4, kẹp trong NGUONG_DOC."""
    mag = np.sqrt(gx[::2, ::2] ** 2 + gy[::2, ::2] ** 2)
    return float(np.clip(2.5 * np.percentile(mag, 90) + 4, *NGUONG_DOC))


def _xoa_chu(anh: np.ndarray, k: int) -> np.ndarray:
    """Đóng hình thái (giãn rồi co) xóa nét chữ tối trên nền sáng, rồi lọc trung vị bớt vân nền."""
    nhan = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    return cv2.medianBlur(cv2.morphologyEx(anh, cv2.MORPH_CLOSE, nhan), 5)


def _lab(anh: np.ndarray) -> list[np.ndarray]:
    """Ba kênh Lab dạng float; a, b nhân 2 vì dải giá trị hẹp hơn L."""
    lab = cv2.cvtColor(anh, cv2.COLOR_BGR2LAB).astype(np.float32)
    return [lab[..., 0], (lab[..., 1] - 128) * 2 + 128, (lab[..., 2] - 128) * 2 + 128]


def _dao_ham(kenh: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Đạo hàm (gx, gy) của kênh có độ dốc lớn nhất tại từng điểm ảnh."""
    gx = [cv2.Sobel(c, cv2.CV_32F, 1, 0, ksize=3) / 4 for c in kenh]
    gy = [cv2.Sobel(c, cv2.CV_32F, 0, 1, ksize=3) / 4 for c in kenh]
    mag = np.stack([x * x + y * y for x, y in zip(gx, gy)])
    chon = mag.argmax(axis=0)
    gxs, gys = np.stack(gx), np.stack(gy)
    return np.take_along_axis(gxs, chon[None], 0)[0], np.take_along_axis(gys, chon[None], 0)[0]


# ---------- ứng viên ----------

def _bon_dinh(bao: np.ndarray) -> np.ndarray | None:
    """Tứ giác xấp xỉ một bao lồi: giảm dần độ mịn tới khi còn 4 đỉnh; còn thừa đỉnh thì chọn 4 đỉnh bao diện tích lớn nhất."""
    chu_vi = cv2.arcLength(bao, True)
    xx = None
    for eps in (0.01, 0.02, 0.03, 0.045, 0.06, 0.08):
        xx = cv2.approxPolyDP(bao, eps * chu_vi, True).reshape(-1, 2).astype(np.float32)
        if len(xx) == 4:
            return xx
        if len(xx) < 4:
            return None
        if len(xx) <= 8:
            break
    if xx is None or len(xx) > 12:
        return None
    tot, dt_tot = None, 0.0
    for chon in itertools.combinations(range(len(xx)), 4):
        q = xx[list(chon)]
        dt = cv2.contourArea(q)
        if dt > dt_tot:
            tot, dt_tot = q, dt
    return tot


def _tu_mat_na(mat_na: np.ndarray, dt: float, toi_da: int = 4, loai: int = cv2.RETR_EXTERNAL) -> list[np.ndarray]:
    duong, _ = cv2.findContours(mat_na, loai, cv2.CHAIN_APPROX_SIMPLE)
    kq = []
    for c in sorted(duong, key=cv2.contourArea, reverse=True)[:toi_da]:
        bao = cv2.convexHull(c)
        if cv2.contourArea(bao) < 0.08 * dt:
            break
        q = _bon_dinh(bao)
        if q is not None:
            kq.append(q)
    return kq


def _giao(d1, d2):
    """Giao hai đường thẳng dạng (điểm, hướng)."""
    (p, u), (q, v) = d1, d2
    det = u[0] * v[1] - u[1] * v[0]
    if abs(det) < 1e-6:
        return None
    t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / det
    return np.array([p[0] + t * u[0], p[1] + t * u[1]], np.float32)


def _tu_duong_thang(canh: np.ndarray, h: int, w: int) -> list[np.ndarray]:
    """Ghép 4 đường thẳng Hough thành tứ giác: hai cặp gần song song, hai cặp lệch hướng nhau nhiều."""
    ngan = min(h, w)
    ds = cv2.HoughLinesP(canh, 1, math.pi / 180, threshold=50, minLineLength=int(0.12 * ngan), maxLineGap=int(0.03 * ngan))
    if ds is None:
        return []
    ds = sorted(ds.reshape(-1, 4).astype(np.float32), key=lambda l: -math.hypot(l[2] - l[0], l[3] - l[1]))
    # gộp đoạn gần trùng nhau (cùng hướng, cách nhau < 1,5% cạnh ngắn)
    duong = []
    for x1, y1, x2, y2 in ds:
        u = np.array([x2 - x1, y2 - y1], np.float32)
        u /= max(float(np.linalg.norm(u)), 1e-6)
        n = np.array([-u[1], u[0]])
        p = np.array([(x1 + x2) / 2, (y1 + y2) / 2], np.float32)
        trung = False
        for p2, u2, _ in duong:
            if abs(float(u @ u2)) > math.cos(math.radians(4)) and abs(float((p - p2) @ n)) < 0.015 * ngan:
                trung = True
                break
        if not trung:
            duong.append((p, u, math.hypot(x2 - x1, y2 - y1)))
        if len(duong) >= 16:
            break
    cap = []
    for (i, a), (j, b) in itertools.combinations(enumerate(duong), 2):
        if abs(float(a[1] @ b[1])) < math.cos(math.radians(30)):
            continue
        n = np.array([-a[1][1], a[1][0]])
        if abs(float((b[0] - a[0]) @ n)) < 0.2 * ngan:
            continue
        cap.append((a, b))
    kq = []
    for (a, b), (c, d) in itertools.combinations(cap, 2):
        huong = abs(float(a[1] @ c[1]))
        if huong > math.cos(math.radians(50)):
            continue
        g = [_giao(a[:2], c[:2]), _giao(c[:2], b[:2]), _giao(b[:2], d[:2]), _giao(d[:2], a[:2])]
        if any(x is None for x in g):
            continue
        q = np.array(g, np.float32)
        if np.any(q[:, 0] < -0.15 * w) or np.any(q[:, 0] > 1.15 * w) or np.any(q[:, 1] < -0.15 * h) or np.any(q[:, 1] > 1.15 * h):
            continue
        kq.append(q)
    return kq


def _ung_vien(sach: np.ndarray, kenh: list[np.ndarray]) -> list[np.ndarray]:
    h, w = sach.shape[:2]
    dt = float(h * w)
    L = kenh[0].astype(np.uint8)
    u8 = [np.clip(c, 0, 255).astype(np.uint8) for c in kenh]
    kq = []
    # 1. đường bao của ảnh cạnh (hai mức ngưỡng), gộp ba kênh Lab
    for thap, cao in ((10, 30), (20, 60), (40, 120)):
        canh = np.zeros((h, w), np.uint8)
        for c in u8:
            canh |= cv2.Canny(c, thap, cao)
        gian = cv2.dilate(canh, np.ones((3, 3), np.uint8), iterations=2)
        kq += _tu_mat_na(gian, dt, 6, cv2.RETR_LIST)
        if thap == 20:
            kq += _tu_duong_thang(cv2.dilate(canh, np.ones((2, 2), np.uint8)), h, w)
    # 2. vùng sáng / tối theo Otsu
    _, sang = cv2.threshold(cv2.GaussianBlur(L, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    nhan = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    for m in (sang, 255 - sang):
        m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, nhan), cv2.MORPH_CLOSE, nhan)
        kq += _tu_mat_na(m, dt, 3)
    # 3. phân cụm màu k-means (2 và 3 cụm) trên ảnh rất nhỏ
    s = 160 / max(h, w)
    be = cv2.resize(np.dstack(kenh).astype(np.float32), (max(1, round(w * s)), max(1, round(h * s))), interpolation=cv2.INTER_AREA)
    du_lieu = be.reshape(-1, 3)
    for k in (2, 3):
        _, nhan_cum, _ = cv2.kmeans(du_lieu, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0), 2,
                                    cv2.KMEANS_PP_CENTERS)
        nhan_cum = nhan_cum.reshape(be.shape[:2])
        for i in range(k):
            m = cv2.resize((nhan_cum == i).astype(np.uint8) * 255, (w, h), interpolation=cv2.INTER_NEAREST)
            m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, nhan), cv2.MORPH_CLOSE, nhan)
            kq += _tu_mat_na(m, dt, 2)
    return kq


# ---------- chấm điểm ----------

def _sap_xep(q: np.ndarray) -> np.ndarray:
    tam = q.mean(axis=0)
    q = q[np.argsort(np.arctan2(q[:, 1] - tam[1], q[:, 0] - tam[0]))]
    return np.roll(q, -int(np.argmin(q.sum(axis=1))), axis=0)


def _hop_le(q: np.ndarray, h: int, w: int) -> bool:
    if not cv2.isContourConvex(q.reshape(-1, 1, 2).astype(np.float32)):
        return False
    dt = cv2.contourArea(q)
    if dt < 0.08 * h * w:
        return False
    ngan = min(h, w)
    for i in range(4):
        a, b, c = q[i - 1], q[i], q[(i + 1) % 4]
        if np.linalg.norm(c - b) < 0.12 * ngan:
            return False
        u, v = a - b, c - b
        cos = float(u @ v) / max(float(np.linalg.norm(u) * np.linalg.norm(v)), 1e-6)
        if not (-0.77 < cos < 0.77):  # góc trong 40°..140°
            return False
    return True


def _bam_canh(a, b, gx, gy, nguong, so_diem=48, tam_do=2):
    """Độ bám cạnh của đoạn a→b: (tỉ lệ điểm có mép rõ, dấu chủ đạo của đạo hàm); None nếu cạnh gần hết ngoài ảnh."""
    h, w = gx.shape
    u = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
    n = np.array([u[1], -u[0]], np.float32)  # pháp tuyến (hướng ra ngoài với tứ giác thuận chiều kim đồng hồ)
    t = np.linspace(0.06, 0.94, so_diem)
    p = a[None] + (b - a)[None] * t[:, None]
    gia_tri = np.full((so_diem, 2 * tam_do + 1), 0.0, np.float32)
    trong = np.zeros(so_diem, bool)
    for k, d in enumerate(range(-tam_do, tam_do + 1)):
        x = np.round(p[:, 0] + n[0] * d).astype(int)
        y = np.round(p[:, 1] + n[1] * d).astype(int)
        ok = (x >= 2) & (x < w - 2) & (y >= 2) & (y < h - 2)
        if d == 0:
            trong = ok
        xx, yy = np.clip(x, 0, w - 1), np.clip(y, 0, h - 1)
        gia_tri[:, k] = np.where(ok, gx[yy, xx] * n[0] + gy[yy, xx] * n[1], 0)
    if trong.sum() < 0.3 * so_diem:
        return None
    # ngưỡng riêng của cạnh theo độ nhiễu hai bên mép (cách mép 5..9 điểm ảnh): giấy trắng trên giấy trắng mép chỉ
    # chênh ~12 nhưng hai bên rất phẳng; vân gỗ, vải thì hai bên nhiễu nên đòi mép rõ hơn
    nhieu = []
    for d in (-9, -7, -5, 5, 7, 9):
        x = np.clip(np.round(p[:, 0] + n[0] * d).astype(int), 0, w - 1)
        y = np.clip(np.round(p[:, 1] + n[1] * d).astype(int), 0, h - 1)
        nhieu.append(np.hypot(gx[y, x], gy[y, x])[trong])
    nguong = float(np.clip(2.5 * np.percentile(np.concatenate(nhieu), 75) + 3, 4.0, nguong))
    duong = gia_tri.max(axis=1)[trong]
    am = -gia_tri.min(axis=1)[trong]
    dau = 1 if (duong > nguong).sum() >= (am > nguong).sum() else -1
    manh = duong if dau > 0 else am
    return float((manh > nguong).mean()), dau, nguong


def _giong_giay(kenh: list[np.ndarray]) -> np.ndarray:
    """Mặt nạ 0/1 điểm ảnh giống giấy (đã xóa chữ): sáng hơn ngưỡng Otsu của L và ít màu."""
    L = np.clip(kenh[0], 0, 255).astype(np.uint8)
    nguong, _ = cv2.threshold(L, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    sac = np.abs(kenh[1] - 128) + np.abs(kenh[2] - 128)  # a, b đã nhân 2
    return ((L > min(nguong, 200)) & (sac < 60)).astype(np.uint8)


def _ti_le_giay(q: np.ndarray, giay: np.ndarray) -> float:
    m = np.zeros(giay.shape, np.uint8)
    cv2.fillConvexPoly(m, np.round(q).astype(np.int32), 1)
    n = int(m.sum())
    return float((giay & m).sum()) / n if n else 0.0


def _cham(q: np.ndarray, gx, gy, nguong: float, giay: np.ndarray | None = None) -> float:
    """Điểm của tứ giác: độ bám cạnh, cộng phần diện tích và phần giống giấy bên trong; -1 nếu không phải tờ giấy."""
    h, w = gx.shape
    if not _hop_le(q, h, w):
        return -1.0
    f, dau = [], []
    for i in range(4):
        r = _bam_canh(q[i], q[(i + 1) % 4], gx, gy, nguong)
        if r is None:
            f.append(0.55)
        else:
            f.append(r[0])
            dau.append(r[1])
    if len(dau) < 2:  # quá nửa chu vi nằm ngoài ảnh (khung trùng toàn ảnh): không đủ chứng cứ
        return -1.0
    f = np.array(f)
    if f.min() < 0.3 or f.mean() < 0.5:
        return -1.0
    # giấy sáng hơn nền thì cả 4 cạnh cùng dấu; lệch dấu là ghép nhầm mép đồ vật
    dong_dau = 1.0 if len(set(dau)) <= 1 else 0.8
    diem = (0.6 * f.mean() + 0.4 * f.min()) * dong_dau + 0.45 * cv2.contourArea(q) / (h * w)
    if giay is not None:
        diem += 0.2 * _ti_le_giay(q, giay)
    return diem


# ---------- tinh chỉnh ----------

def _tinh_chinh(q: np.ndarray, gx, gy, nguong: float) -> np.ndarray:
    """Dò mép thật dọc pháp tuyến từng cạnh, khớp đường thẳng, giao lại ra 4 góc."""
    h, w = gx.shape
    r = max(4, int(0.012 * max(h, w)))
    duong = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        bam = _bam_canh(a, b, gx, gy, nguong, so_diem=16, tam_do=3)
        u = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
        n = np.array([u[1], -u[0]], np.float32)
        if bam is None:
            duong.append((a, u))
            continue
        dau, nguong_canh = bam[1], bam[2]
        diem = []
        for t in np.linspace(0.05, 0.95, 60):
            p = a + (b - a) * t
            tot, gtot = None, nguong_canh
            for d in range(-r, r + 1):
                x, y = int(round(p[0] + n[0] * d)), int(round(p[1] + n[1] * d))
                if not (1 <= x < w - 1 and 1 <= y < h - 1):
                    continue
                g = dau * (gx[y, x] * n[0] + gy[y, x] * n[1])
                if g > gtot:
                    tot, gtot = d, g
            if tot is not None:
                diem.append(p + n * tot)
        if len(diem) < 12:
            duong.append((a, u))
            continue
        vx, vy, x0, y0 = cv2.fitLine(np.array(diem, np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        duong.append((np.array([x0, y0], np.float32), np.array([vx, vy], np.float32)))
    moi = []
    for i in range(4):
        g = _giao(duong[i - 1], duong[i])
        moi.append(q[i] if g is None else g)
    moi = np.array(moi, np.float32)
    if np.linalg.norm(moi - q, axis=1).max() > 0.03 * math.hypot(h, w) or not _hop_le(moi, h, w):
        return q
    return moi


def _chuan_bi(anh: np.ndarray, canh: int):
    h, w = anh.shape[:2]
    s = min(1.0, canh / max(h, w))
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    sach = _xoa_chu(nho, max(5, round(9 * max(nho.shape[:2]) / CANH_NHO)) | 1)
    kenh = _lab(sach)
    gx, gy = _dao_ham([cv2.GaussianBlur(c, (0, 0), 1.0) for c in kenh])
    return s, nho, sach, kenh, gx, gy, _nguong(gx, gy)


def _muc(nho: np.ndarray) -> np.ndarray:
    """Mặt nạ 0/1 nét mực (chữ, hình) trên ảnh nhỏ chưa xóa chữ."""
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY)
    return cv2.adaptiveThreshold(xam, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 12)


def _mat_do_muc(muc: np.ndarray, ngoai: np.ndarray, trong: np.ndarray | None) -> tuple[float, float]:
    """Mật độ mực trong vành giữa tứ giác ngoài và tứ giác trong, và trong tứ giác trong."""
    m_ngoai = np.zeros(muc.shape, np.uint8)
    cv2.fillConvexPoly(m_ngoai, ngoai.astype(np.int32), 1)
    m_trong = np.zeros(muc.shape, np.uint8)
    cv2.fillConvexPoly(m_trong, trong.astype(np.int32), 1)
    # bỏ dải sát mép (bóng, vệt mép giấy) khỏi cả hai vùng
    nhan = np.ones((15, 15), np.uint8)
    vanh = cv2.erode(m_ngoai, nhan) & (1 - cv2.dilate(m_trong, nhan))
    lui = cv2.erode(m_trong, nhan)
    return float(muc[vanh > 0].mean()) if vanh.any() else 0.0, float(muc[lui > 0].mean()) if lui.any() else 0.0


def _canh_ro(q: np.ndarray, gx, gy, nguong: float) -> bool:
    """Cả 4 cạnh đều bám mép rõ (≥ 70% chiều dài) và cùng dấu: tờ giấy thật, không phải khối chữ hay mảnh ghép."""
    dau = set()
    for i in range(4):
        r = _bam_canh(q[i], q[(i + 1) % 4], gx, gy, nguong)
        if r is None:
            continue
        if r[0] < 0.7:
            return False
        dau.add(r[1])
    return len(dau) <= 1


def _chon_trong(tot: np.ndarray, diem_tot: float, ds: list[tuple[np.ndarray, float]], muc: np.ndarray, gx, gy,
                nguong: float):
    """Tứ giác tốt nhất có thể là vật bao quanh tờ giấy (tờ giấy trắng nằm dưới, bìa sổ). Có tứ giác nằm trong nó,
    bám cạnh khá tốt, mà vành giữa hai tứ giác gần như không có mực còn bên trong có chữ thì tờ giấy là tứ giác trong."""
    while True:
        dt_tot = cv2.contourArea(tot)
        chon = None
        for q, d in sorted(ds, key=lambda x: -cv2.contourArea(x[0])):
            if d < 0.75 * (diem_tot - 0.45 * dt_tot / muc.size - 0.2) or cv2.contourArea(q) > 0.92 * dt_tot:
                continue
            if any(cv2.pointPolygonTest(tot.reshape(-1, 1, 2), (float(x), float(y)), True) < -3 for x, y in q):
                continue
            if not _canh_ro(q, gx, gy, nguong):
                continue
            vanh, trong = _mat_do_muc(muc, tot, q)
            if trong > 0.02 and vanh < 0.25 * trong:
                chon = (q, d)
                break
        if chon is None:
            return tot, diem_tot
        tot, diem_tot = chon


TRANG_KE_TOI_THIEU = 0.5  # phần trang bên kia gáy thấy được (so với bề rộng trang) để coi là chụp cả cặp trang


def _toi_bien(p: np.ndarray, d: np.ndarray, h: int, w: int) -> float:
    """Quãng đường từ p theo hướng đơn vị d tới biên ảnh."""
    t = np.inf
    for k, gioi in ((0, w - 1), (1, h - 1)):
        if d[k] > 1e-6:
            t = min(t, (gioi - p[k]) / d[k])
        elif d[k] < -1e-6:
            t = min(t, -p[k] / d[k])
    return max(float(t), 0.0)


def _canh_noi(q: np.ndarray, nho: np.ndarray, kenh: list[np.ndarray]) -> tuple[int, float] | None:
    """Sách mở chụp sát, trang bên kia gáy lọt một phần ra ngoài khung: tứ giác tìm được chỉ là một trang (trang còn
    nguyên), bên kia một cạnh của nó (gáy) là giấy có chữ chạy tới biên ảnh. Trả (chỉ số cạnh i: q[i]→q[i+1], phần
    trang bên kia thấy được so với bề rộng trang) nếu thấy được từ TRANG_KE_TOI_THIEU trở lên; None nếu không (chụp
    từng trang thì trang bên cạnh thường chỉ lộ một mẩu, không nối)."""
    h, w = nho.shape[:2]
    if min(q[:, 0].min(), q[:, 1].min(), w - 1 - q[:, 0].max(), h - 1 - q[:, 1].max()) < 3:
        return None  # chính trang này đã chạm biên
    giay = _giong_giay(kenh)
    muc = _muc(nho)
    m_trong = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(m_trong, np.round(q).astype(np.int32), 1)
    lui = cv2.erode(m_trong, np.ones((15, 15), np.uint8))
    if not lui.any():
        return None
    muc_trong = float(muc[lui > 0].mean())
    if muc_trong < 0.02:
        return None
    tot = None
    for i in range(4):
        a, b, c, d = q[i], q[(i + 1) % 4], q[(i + 2) % 4], q[(i + 3) % 4]
        # hai cạnh kề kéo dài qua a, b; bề rộng trang theo từng cạnh kề
        da, db = a - d, b - c
        la, lb = float(np.linalg.norm(da)), float(np.linalg.norm(db))
        if la < 10 or lb < 10:
            continue
        da, db = da / la, db / lb
        ta, tb = _toi_bien(a, da, h, w), _toi_bien(b, db, h, w)
        thay = min(ta / la, tb / lb)  # phần trang bên kia thấy được
        # thấy quá ít (chụp từng trang), hoặc trang bên kia đủ trong khung (không phải bị cắt); trang gần máy trông
        # rộng hơn (phối cảnh) nên cho một bên tới 1,3 lần, bên kia phải bị cắt (≤ 1,02)
        if thay < TRANG_KE_TOI_THIEU or thay > 1.02 or max(ta / la, tb / lb) > 1.3:
            continue
        # dải bên kia gáy: bỏ 8% sát gáy (bóng gáy), lấy tới 60% bề rộng trang hoặc tới biên
        u0, u1 = 0.08, min(0.6, thay - 0.02)
        dai = np.array([a + da * la * u0, b + db * lb * u0, b + db * lb * u1, a + da * la * u1])
        m = np.zeros((h, w), np.uint8)
        cv2.fillConvexPoly(m, np.round(dai).astype(np.int32), 1)
        if m.sum() < 200:
            continue
        ti_giay = float(giay[m > 0].mean())
        muc_dai = float(muc[m > 0].mean())
        if ti_giay > 0.6 and muc_dai > 0.35 * muc_trong and (tot is None or thay > tot[1]):
            tot = (i, thay)
    return tot


def _noi_canh(q: np.ndarray, i: int, H: int, W: int) -> np.ndarray:
    """Kéo cạnh q[i]→q[i+1] ra tới biên ảnh dọc theo hai cạnh kề (giữ thứ tự góc)."""
    q = q.astype(np.float32).copy()
    a, b, c, d = i, (i + 1) % 4, (i + 2) % 4, (i + 3) % 4
    for g, k in ((a, d), (b, c)):
        hg = q[g] - q[k]
        hg /= max(float(np.linalg.norm(hg)), 1e-6)
        q[g] = q[g] + hg * _toi_bien(q[g], hg, H, W)
    return q


def tim_tu_giac(anh: np.ndarray, tinh: bool = True, canh: int = CANH_NHO) -> tuple[np.ndarray, float] | None:
    """[canh]: cạnh dài ảnh dò (640; xem trước lúc chụp dùng 400). 4 góc (trên trái, trên phải, dưới phải, dưới trái, tọa độ ảnh gốc) và điểm tin cậy; None nếu không thấy."""
    s, nho, sach, kenh, gx, gy, nguong = _chuan_bi(anh, canh)
    tot, diem_tot = None, 0.0
    da_xet, tot_ds = [], []
    giay = _giong_giay(kenh)
    for q in _ung_vien(sach, kenh):
        q = _sap_xep(q.astype(np.float32))
        if any(np.abs(q - x).max() < 3 for x in da_xet):
            continue
        da_xet.append(q)
        d = _cham(q, gx, gy, nguong, giay)
        if d > 0:
            tot_ds.append((q, d))
        if d > diem_tot:
            tot, diem_tot = q, d
    if tot is None:
        return None
    tot, diem_tot = _chon_trong(tot, diem_tot, tot_ds, _muc(nho), gx, gy, nguong)
    noi = _canh_noi(tot, nho, kenh)
    if tinh:
        s2, _, _, _, gx2, gy2, ng2 = _chuan_bi(anh, CANH_TINH)
        tot = _tinh_chinh(tot * (s2 / s), gx2, gy2, ng2) / s2
    else:
        tot = tot / s
    H, W = anh.shape[:2]
    if noi is not None:  # nửa cặp trang: lấy cả phần trang bên kia gáy tới biên ảnh
        tot = _noi_canh(tot, noi[0], H, W)
    tot[:, 0] = np.clip(tot[:, 0], 0, W - 1)
    tot[:, 1] = np.clip(tot[:, 1], 0, H - 1)
    return tot, diem_tot
