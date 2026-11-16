"""Đo chất lượng trang để báo trang nên chụp lại: ảnh nhòe (rung tay, đang lật trang, lấy nét hụt) và tay, ngón tay
che vào trang.

Góp ý 15/11/2026 (Hồ sơ 15-11 19-33.pdf, 214 trang): hai trang chụp lúc tay đang lật trang, chữ nhòe, ngón tay che
chữ. Xử lý không cứu được, nhưng ứng dụng không báo nên người dùng không biết để chụp lại.

- Nhòe (đo trên ảnh đã làm sạch kiểu Giữ màu / Xám, nền trắng, chữ đã kéo tương phản): chữ in nét thì lõi nét đạt gần
  đen (điểm tối nhất của mỗi ô chữ 0–30); chữ nhòe loang mực ra nên lõi chỉ còn xám (60–150). Chia trang thành ô
  chừng 6 dòng chữ; trang nhòe khi trên 45% ô có chữ có lõi xám, hoặc lõi trung vị trên 55. Trên 214 trang của người
  dùng: hai trang nhòe 0,58 và 0,64 (lõi trung vị 76, 96); trang tốt trung vị 0,05, cao nhất 0,36 (chữ in nhạt).
  Ảnh Đen trắng (đã nhị phân) không đo được.
- Nhòe trên ảnh gốc (chưa làm sạch, đo được ở mọi chế độ, dùng cả ở màn camera ngay sau khi chụp): độ rộng mép nét
  chữ theo từng hướng (0°, 45°, 90°, 135°). Mỗi ô chữ 96 px (trang thu về 1600 px): độ rộng = tương phản / độ dốc
  lớn nhất (phân vị 99) theo hướng đó, lấy hướng rộng nhất (rung tay chỉ nhòe theo một hướng, nét chạy theo hướng
  rung vẫn sắc). Ảnh chụp nét 2,4–2,9 px; rung 10 px (chừng nửa cỡ chữ) 5,1–8,8 px. Báo khi độ rộng trung vị quá
  4,8 px (dùng trung vị vì ô có bóng gáy, mép trang, hình cũng có mép mềm). Phép đo lõi xám ở trên chỉ bắt được nhòe rất nặng (bước làm sạch kéo đậm lại nét), giữ lại vì đã
  kiểm trên trang 145, 146 thật.
- Trùng trang: so đặc trưng ORB (1000 px, 2000 điểm) của hai trang kết quả, đếm cặp khớp theo một phép đồng dạng
  (dời, co giãn 0,7–1,4 lần, xoay tới 15°), thử mọi cặp trong 50 cặp khớp tốt nhất (tất định, bản Dart ra cùng số;
  không dùng findHomography vì bản Android không dựng mô-đun calib3d). Trên 214 trang của người dùng: 10 cặp chụp
  trùng 110–573 điểm khớp; cặp trang 146–148 (trang 146 có tay che nửa trang) 36; các trang khác nhau tối đa 26.
  Ngưỡng 40: báo nhầm thì người dùng có thể xóa mất trang thật, nên chọn chặt.
- Tay: phần vùng giữa trang (thu vào 8% mỗi phía) có màu da thuộc mảng chạm dải mép (tay luôn thò từ ngoài vào), như
  tu_chup.ti_le_tay. Ngón tay giữ sách ở lề không tính. Đo trên ảnh màu trước khi làm sạch.
"""
from __future__ import annotations

import cv2
import numpy as np

from .tu_chup import ti_le_tay

CANH = 1600
LOI_XAM = 60          # điểm tối nhất của ô chữ trên mức này: lõi nét xám (nhòe)
NGUONG_O_XAM = 0.45   # phần ô chữ có lõi xám
NGUONG_LOI_TV = 55    # lõi trung vị
NGUONG_TAY = 0.05     # phần vùng giữa trang có tay (ngón cái giữ mép sách: 0–3,4%; tay đặt lên trang: 5–30%)
O_MEP = 96            # ô đo độ rộng mép (px, trang 1600 px)
NGUONG_MEP = 4.8      # độ rộng mép nét chữ trung vị (px) quá mức này: trang nhòe
CANH_TRUNG = 1000     # cỡ trang khi so trùng
NGUONG_TRUNG = 40     # số điểm khớp từ mức này: hai trang là một (chụp trùng)


def _thu_nho(anh: np.ndarray, canh: int) -> np.ndarray:
    h, w = anh.shape[:2]
    s = min(1.0, canh / max(h, w))
    return cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh


def do_nhoe(anh: np.ndarray) -> tuple[float, float] | None:
    """(phần ô chữ có lõi xám, lõi trung vị) của trang đã làm sạch; None nếu không đủ chữ."""
    nho = _thu_nho(anh, CANH)
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    muc = cv2.adaptiveThreshold(xam, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 15)
    _, _, tk, _ = cv2.connectedComponentsWithStats(muc, 8)
    ch = tk[1:, 3]
    vua = ch[(ch > 4) & (ch < 0.05 * xam.shape[0])]
    if len(vua) < 40:
        return None
    cao = float(np.median(vua))
    o = max(int(6 * cao), 32)
    hn, wn = xam.shape
    loi = []
    for y in range(0, hn - o // 2, o):
        for x in range(0, wn - o // 2, o):
            v = xam[y:y + o, x:x + o]
            p1, p3, p90 = np.percentile(v, (1, 3, 90))
            # ô có chữ: đủ tương phản, đủ điểm mực
            if p90 - p3 < 40 or (v < p3 + 0.4 * (p90 - p3)).mean() < 0.02:
                continue
            loi.append(p1)
    if len(loi) < 6:
        return None
    loi = np.array(loi)
    return float((loi > LOI_XAM).mean()), float(np.median(loi))


def la_nhoe(anh: np.ndarray) -> bool:
    d = do_nhoe(anh)
    return d is not None and (d[0] > NGUONG_O_XAM or d[1] > NGUONG_LOI_TV)


def _phan_vi_hist(hist: np.ndarray, buoc: float, q: float) -> float:
    """Phân vị q (0..100) từ biểu đồ tần số (nội suy kiểu numpy); giống bản Dart."""
    tong = int(hist.sum())
    vt = q / 100 * (tong - 1)
    cs = np.cumsum(hist)
    a = int(np.searchsorted(cs, int(np.floor(vt)), side="right"))
    b = int(np.searchsorted(cs, int(np.ceil(vt)), side="right"))
    return (a + (b - a) * (vt - np.floor(vt))) * buoc


def do_mo_mep(anh: np.ndarray) -> tuple[float, float] | None:
    """(phần ô chữ có mép nhòe, độ rộng mép trung vị px) của trang chưa làm sạch; None nếu không đủ chữ."""
    nho = _thu_nho(anh, CANH)
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    gx = cv2.Sobel(xam, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(xam, cv2.CV_32F, 0, 1, ksize=3) / 8
    c = np.float32(np.sqrt(0.5))
    huong = [np.abs(gx), np.abs(c * (gx + gy)), np.abs(gy), np.abs(c * (gx - gy))]
    # độ dốc lượng tử 0,25 (1024 mức) để tính phân vị bằng biểu đồ như bản Dart
    huong = [np.minimum(d * 4, 1023).astype(np.int32) for d in huong]
    o = O_MEP
    hn, wn = xam.shape
    rong = []
    for y in range(0, hn - o // 2, o):
        for x in range(0, wn - o // 2, o):
            v = xam[y:y + o, x:x + o]
            hist = np.bincount(v.ravel(), minlength=256)
            p3, p90 = _phan_vi_hist(hist, 1, 3), _phan_vi_hist(hist, 1, 90)
            if p90 - p3 < 40 or hist[: int(np.ceil(p3 + 0.4 * (p90 - p3)))].sum() < 0.02 * v.size:
                continue
            r = 0.0
            for d in huong:
                p99 = _phan_vi_hist(np.bincount(d[y:y + o, x:x + o].ravel(), minlength=1024), 0.25, 99)
                r = max(r, (p90 - p3) / max(p99, 0.25))
            rong.append(r)
    if len(rong) < 6:
        return None
    rong = np.array(rong)
    return float((rong > NGUONG_MEP).mean()), float(np.median(rong))


def la_nhoe_goc(anh: np.ndarray) -> bool:
    d = do_mo_mep(anh)
    return d is not None and d[1] > NGUONG_MEP


def dac_trung(anh: np.ndarray):
    """Điểm đặc trưng ORB của một trang kết quả, để so trùng."""
    nho = _thu_nho(anh, CANH_TRUNG)
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    return cv2.ORB_create(2000).detectAndCompute(xam, None)


def diem_khop(a, b) -> int:
    """Số điểm khớp theo một phép đồng dạng giữa hai trang (đặc trưng từ dac_trung)."""
    (ka, da), (kb, db) = a, b
    if da is None or db is None or len(ka) < 20 or len(kb) < 20:
        return 0
    cap = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(da, db, k=2)
    tot = [m[0] for m in cap if len(m) == 2 and m[0].distance < 0.75 * m[1].distance]
    if len(tot) < 8:
        return len(tot)
    tot.sort(key=lambda m: (m.distance, m.queryIdx))
    p = np.array([complex(*ka[m.queryIdx].pt) for m in tot])
    q = np.array([complex(*kb[m.trainIdx].pt) for m in tot])
    tot_nhat = 0
    n = min(50, len(tot))
    for i in range(n):
        for j in range(i + 1, n):
            dp = p[j] - p[i]
            if abs(dp) < 50:
                continue
            z = (q[j] - q[i]) / dp  # co giãn và xoay
            if not 0.7 < abs(z) < 1.4 or abs(np.angle(z)) > 0.26:
                continue
            t = q[i] - z * p[i]
            tot_nhat = max(tot_nhat, int((np.abs(z * p + t - q) < 8.0).sum()))
    return tot_nhat


def do_tay(anh: np.ndarray) -> float:
    """Phần vùng giữa trang bị tay, ngón tay che (ảnh màu)."""
    if anh.ndim == 2:
        return 0.0
    nho = _thu_nho(anh, 640)
    hn, wn = nho.shape[:2]
    khung = np.array([[0, 0], [wn - 1, 0], [wn - 1, hn - 1], [0, hn - 1]], np.float32)
    return ti_le_tay(nho, khung)
