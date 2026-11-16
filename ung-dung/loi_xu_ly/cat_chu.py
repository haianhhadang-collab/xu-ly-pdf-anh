"""Cắt sát vùng chữ và xóa vết bẩn ngoài vùng chữ (nền bàn, bìa sách, ngón tay giữ sách, góc đen sau khi nắn).

Sau khi cắt theo mép giấy, ảnh trang vẫn có thể còn: dải nền tối ở mép (mép giấy cong, trang sách bên cạnh), ô đen ở
góc, ngón tay giữ sách, vệt bóng. Cách làm (chạy trên ảnh đã làm sạch, đã sửa nghiêng):

1. Tìm nét mực (ngưỡng thích nghi) và vùng tối đặc (xám < 110). Chiều cao chữ = trung vị chiều cao các nét vừa cỡ.
2. Nét giống chữ: không chạm mép ảnh, không phải khối tối đặc lớn, không quá nhỏ. Nối chữ thành khối (giãn ngang 2,5,
   dọc 1,5 chiều cao chữ).
3. Khối chính: các khối có nhiều chữ; rồi gộp dần các khối ở gần (số trang, chú thích, chữ ký, con dấu) trong khoảng
   6% cạnh ngắn của trang.
4. Ảnh ra = vùng bao các khối giữ lại + lề trắng (1,5 chiều cao chữ, ít nhất 1,5% cạnh dài). Phần lề là nền trắng mới
   nên vết bẩn ngoài vùng chữ mất hết; trong vùng chữ, khối tối đặc lấn từ mép vùng vào (nền tối, góc đen) được tô trắng.

Trang không đủ chữ (ảnh, trang trắng) thì trả nguyên ảnh.
"""
from __future__ import annotations

import cv2
import numpy as np

CANH_XU_LY = 1600


def _khung_noi_dung(nho: np.ndarray):
    """(x0, y0, x1, y1) vùng nội dung, chiều cao chữ, mặt nạ vết nên xóa; None nếu không đủ chữ."""
    xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY) if nho.ndim == 3 else nho
    hsv = cv2.cvtColor(nho, cv2.COLOR_BGR2HSV) if nho.ndim == 3 else None
    h, w = xam.shape
    muc = cv2.adaptiveThreshold(xam, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 15)
    toi = (xam < 110).astype(np.uint8) * 255
    tong = cv2.bitwise_or(muc, toi)
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(tong, 8)
    if n < 30:
        return None
    x, y, cw, ch, dt = (tk[1:, i] for i in range(5))
    vua = (ch > 4) & (ch < 0.05 * h)
    if vua.sum() < 20:
        return None
    cao_chu = float(np.median(ch[vua]))
    cham_mep = (x <= 1) | (y <= 1) | (x + cw >= w - 1) | (y + ch >= h - 1)
    lap_day = dt / np.maximum(cw * ch, 1)
    # trung bình xám, độ bão hòa, sắc độ của từng nét
    dem_px = np.maximum(np.bincount(nhan.ravel(), minlength=n)[1:], 1)
    xam_tb = np.bincount(nhan.ravel(), xam.ravel().astype(np.float64), minlength=n)[1:] / dem_px
    if hsv is not None:
        bh_tb = np.bincount(nhan.ravel(), hsv[..., 1].ravel().astype(np.float64), minlength=n)[1:] / dem_px
        sac_tb = np.bincount(nhan.ravel(), hsv[..., 0].ravel().astype(np.float64), minlength=n)[1:] / dem_px
    else:
        bh_tb = sac_tb = np.zeros(n - 1)
    cc2 = cao_chu ** 2
    # bán kính nét (khoảng cách xa nhất từ trong nét ra mép nét): chữ in, kể cả chữ đậm của tiêu đề, dưới 0,35 chiều
    # cao chữ; bóng ngón tay, vệt bóng cong ở mép, mẩu đen ở góc thì dày hơn nhiều
    kc = cv2.distanceTransform(tong, cv2.DIST_L2, 3)
    ban_kinh = np.zeros(n, np.float32)
    np.maximum.at(ban_kinh, nhan.ravel(), kc.ravel())
    ban_kinh = ban_kinh[1:]
    mo = (ban_kinh > 0.35 * cao_chu) & (xam_tb > 100) & (dt > 1.5 * cc2)
    sat_mep = np.minimum(np.minimum(x, y), np.minimum(w - x - cw, h - y - ch)) < 4 * cao_chu
    # vết (số đo trên ảnh sách người dùng chụp: nét chữ xám trung bình 85–110, bão hòa ~0; nêm đen ở gáy, góc đen
    # xám 16–22; ngón tay màu da bão hòa 50–95, sắc 8–35; dấu đỏ, chữ ký xanh bão hòa ~155 nên không bị tính):
    # - khối lớn lấp gần kín khung bao, hoặc rộng/cao quá nửa trang
    # - khối lớn rất tối (nền tối, nêm đen ở gáy sách, góc đen) — chữ đậm dính liền vẫn xám hơn 40
    # - khối lớn màu da, vàng nhạt (ngón tay giữ sách)
    # - vệt sáng dài (bóng mép giấy); đường kẻ bảng thì tối nên không tính
    dac = (((dt > 9 * cc2) & (lap_day > 0.45)) | (cw > 0.5 * w) | (ch > 0.5 * h)
           | ((dt > 4 * cc2) & (xam_tb < 40))
           | ((dt > 3 * cc2) & (bh_tb > 30) & (bh_tb < 125) & (sac_tb > 8) & (sac_tb < 35) & (xam_tb > 110))
           | (((ch > 6 * cao_chu) | (cw > 30 * cao_chu)) & (xam_tb > 150))
           # bóng mờ dày (ngón tay, vệt bóng cong ở mép trang): nét dày mà nhạt
           | mo
           # mẩu đen dày sát mép ảnh (góc đen, nêm đen ở đầu gáy)
           | ((ban_kinh > 0.5 * cao_chu) & (xam_tb < 70) & sat_mep))
    # đốm nhỏ (dưới 0,15 ô chữ: bụi, chấm lẻ) và nét rất nhạt (xám trung bình > 190: viền ngón tay, bóng) không tính là chữ
    nho = (dt < max(4.0, 0.15 * cc2)) | (xam_tb > 190)
    # vết: khối tối đặc, hoặc nét lớn chạm mép ảnh (viền nền, ngón tay giữ sách); chữ chạm mép (dòng bị cắt sát) thì
    # nhỏ nên không tính
    vet = dac | (cham_mep & ~nho & ((dt > 9 * cao_chu ** 2) | (ch > 3 * cao_chu) | (cw > 8 * cao_chu)))
    mat_vet = np.isin(nhan, np.flatnonzero(vet) + 1).astype(np.uint8)
    # mảnh vụn sát vết (cách dưới một chiều cao chữ) cũng là vết, không phải chữ
    gan_vet = cv2.dilate(mat_vet, cv2.getStructuringElement(cv2.MORPH_RECT, (int(2 * cao_chu) | 1,) * 2))
    cham_vet = np.zeros(n, bool)
    cham_vet[np.unique(nhan[gan_vet > 0])] = True
    chu = ~cham_mep & ~vet & ~nho & ~cham_vet[1:]
    if chu.sum() < 20:
        return None
    mat_chu = np.isin(nhan, np.flatnonzero(chu) + 1).astype(np.uint8)
    kx, ky = max(3, int(2.5 * cao_chu)), max(3, int(1.5 * cao_chu))
    khoi = cv2.dilate(mat_chu, cv2.getStructuringElement(cv2.MORPH_RECT, (kx, ky)))
    nk, nhan_k, tk_k, _ = cv2.connectedComponentsWithStats(khoi, 8)
    if nk < 2:
        return None
    # số nét chữ trong từng khối
    dem = np.bincount(nhan_k[mat_chu > 0], minlength=nk)
    hop = [(int(tk_k[i, 0]), int(tk_k[i, 1]), int(tk_k[i, 0] + tk_k[i, 2]), int(tk_k[i, 1] + tk_k[i, 3]), int(dem[i]))
           for i in range(1, nk)]
    lon_nhat = max(d for *_, d in hop)
    giu = [b for b in hop if b[4] >= 0.15 * lon_nhat]
    con = [b for b in hop if b[4] < 0.15 * lon_nhat and b[4] >= 2]
    x0, y0 = min(b[0] for b in giu), min(b[1] for b in giu)
    x1, y1 = max(b[2] for b in giu), max(b[3] for b in giu)
    gan = max(0.06 * min(w, h), 4 * cao_chu)
    # tiêu đề, chú thích cuối trang: khối có từ ba nét, nằm trong bề ngang vùng chữ, cách xa hơn (tới 12% chiều cao)
    gan_doc = max(0.12 * h, 10 * cao_chu)
    thay_doi = True
    while thay_doi:
        thay_doi = False
        for b in list(con):
            dx = max(x0 - b[2], b[0] - x1, 0)
            dy = max(y0 - b[3], b[1] - y1, 0)
            if max(dx, dy) <= gan or (b[4] >= 3 and dx == 0 and b[0] >= x0 - 2 * cao_chu
                                       and b[2] <= x1 + 2 * cao_chu and dy <= gan_doc):
                x0, y0, x1, y1 = min(x0, b[0]), min(y0, b[1]), max(x1, b[2]), max(y1, b[3])
                con.remove(b)
                thay_doi = True
    # khối giãn rộng hơn nét thật nửa nhân giãn mỗi bên: thu lại
    x0, x1 = x0 + kx // 2, x1 - kx // 2
    y0, y1 = y0 + ky // 2, y1 - ky // 2
    if x1 <= x0 or y1 <= y0:
        return None
    # nới vùng cho trọn mọi nét chạm vào hoặc sát vùng (dấu chấm, dấu thanh, đốm nhỏ bị bỏ khi dựng khối), trừ vết,
    # nét rất nhạt: không bao giờ cắt lẹm vào chữ
    sat = ~vet & (xam_tb <= 190) & ~cham_mep
    for _ in range(3):
        trong = sat & (x < x1 + cao_chu) & (x + cw > x0 - cao_chu) & (y < y1 + cao_chu) & (y + ch > y0 - cao_chu)
        if not trong.any():
            break
        nx0, ny0 = min(x0, int(x[trong].min())), min(y0, int(y[trong].min()))
        nx1, ny1 = max(x1, int((x + cw)[trong].max())), max(y1, int((y + ch)[trong].max()))
        if (nx0, ny0, nx1, ny1) == (x0, y0, x1, y1):
            break
        x0, y0, x1, y1 = nx0, ny0, nx1, ny1
    # vết chạm mép ảnh hoặc lấn vào từ ngoài vùng nội dung: xóa, tô kín cả phần bên trong viền (ngón tay, bóng);
    # khối tối nằm trọn trong vùng nội dung mà không chạm mép (ảnh minh họa) thì giữ
    xoa_id = [i + 1 for i in np.flatnonzero(vet)
              if cham_mep[i] or not (x[i] >= x0 and y[i] >= y0 and x[i] + cw[i] <= x1 and y[i] + ch[i] <= y1)]
    # bóng mờ nhỏ trong vùng chữ (vệt ngón tay, bóng xám): xóa; mảng lớn, kín (ảnh minh họa) thì giữ
    xoa_id += [i + 1 for i in np.flatnonzero(mo & (dt < 25 * cc2) & (lap_day < 0.6))]
    # gáy sách giữa hai trang (ảnh sách mở): dải dọc ở giữa không có chữ, hai bên đều có chữ. Bóng gáy, vệt đứt
    # quãng, mẩu đen ở đầu gáy nằm trọn trong dải thì xóa; nét màu (dấu, chữ ký) và nét vắt qua dải (bảng) thì giữ
    dai = _dai_gay(chu, x, cw, x0, x1, cao_chu)
    if dai is not None:
        g0, g1 = dai
        trong_dai = ~chu & (x >= g0 - cao_chu) & (x + cw <= g1 + cao_chu) & (bh_tb < 60)
        xoa_id += [i + 1 for i in np.flatnonzero(trong_dai)]
    xoa = np.isin(nhan, xoa_id).astype(np.uint8)
    if xoa.any():
        duong, _ = cv2.findContours(xoa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # tô kín lòng vết (ngón tay rỗng ruột…); vết hình khung bao quanh gần cả ảnh (dải nền bàn quanh trang khi nắn
        # phẳng có nới khung) thì lòng là cả trang: chỉ xóa chính vết
        h, w = xoa.shape
        duong = [c for c in duong if not (cv2.boundingRect(c)[2] > 0.9 * w and cv2.boundingRect(c)[3] > 0.9 * h)]
        cv2.drawContours(xoa, duong, -1, 1, cv2.FILLED)
    return (x0, y0, x1, y1), cao_chu, xoa


def _dai_gay(chu, x, cw, x0, x1, cao_chu):
    """(cột đầu, cột cuối) của dải không chữ ở giữa vùng chữ, rộng từ 4 chiều cao chữ; None nếu không có."""
    rong = x1 - x0
    if rong < 20 * cao_chu:
        return None
    co_chu = np.zeros(rong + 1, np.int32)
    for i in np.flatnonzero(chu):
        a, b = max(0, x[i] - x0), min(rong, x[i] + cw[i] - x0)
        if b > a:
            co_chu[a:b] += 1
    lo, hi = int(0.3 * rong), int(0.7 * rong)
    trong = co_chu[lo:hi] == 0
    tot, dau, i = (0, 0), None, 0
    for i, t in enumerate(list(trong) + [False]):
        if t and dau is None:
            dau = i
        elif not t and dau is not None:
            if i - dau > tot[1] - tot[0]:
                tot = (dau, i)
            dau = None
    if tot[1] - tot[0] < 4 * cao_chu:
        return None
    a, b = lo + tot[0], lo + tot[1]
    # hai bên đều phải có nhiều chữ (hai trang sách), không phải lề rộng của một trang
    if co_chu[:a].sum() < 0.2 * co_chu.sum() or co_chu[b:].sum() < 0.2 * co_chu.sum():
        return None
    return x0 + a, x0 + b


def xoa_da_tay(anh: np.ndarray) -> np.ndarray:
    """Ngón tay giữ sách (sau khi làm sạch thành mảng cam, hồng nhạt): tô trắng; nét chữ bị ngón tay đè thì giữ,
    chuyển về màu xám. Chỉ nhận mảng màu da đặc, đủ lớn, không quá lớn: vòng dấu đỏ (sắc đỏ, rỗng ruột), dòng tô
    sáng (mảnh), giấy ngả vàng (cả trang) không bị tính."""
    if anh.ndim != 3:
        return anh
    h, w = anh.shape[:2]
    s = min(1.0, 800 / max(h, w))
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    hsv = cv2.cvtColor(nho, cv2.COLOR_BGR2HSV)
    hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # số đo trên ảnh người dùng: ngón tay sau làm sạch sắc 6–29, bão hòa 40–140, sáng 170–250; dấu đỏ sắc 0–4, 170–180
    da = ((hh >= 5) & (hh <= 30) & (ss >= 35) & (ss <= 200) & (vv >= 120)).astype(np.uint8)
    da = cv2.morphologyEx(da, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    da = cv2.morphologyEx(da, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(da, 8)
    hn, wn = da.shape
    giu = []
    for i in range(1, n):
        cw, ch, dt = tk[i, cv2.CC_STAT_WIDTH], tk[i, cv2.CC_STAT_HEIGHT], tk[i, cv2.CC_STAT_AREA]
        if dt < 0.0015 * hn * wn or dt > 0.25 * hn * wn or min(cw, ch) < 0.025 * min(hn, wn):
            continue
        # mảng đặc (ngón tay lồi), không phải vòng dấu rỗng ruột: diện tích so với bao lồi
        duong, _ = cv2.findContours((nhan == i).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bao = cv2.contourArea(cv2.convexHull(np.vstack(duong)))
        if dt >= 0.6 * bao:
            giu.append(i)
    if not giu:
        return anh
    # nới theo phần màu da nhạt hơn nối liền (mép ngón tay, phần bị làm sáng gần hết)
    nhat = ((hh >= 3) & (hh <= 32) & (ss >= 18) & (vv >= 40)).astype(np.uint8)
    nhat = cv2.morphologyEx(cv2.bitwise_or(nhat, np.isin(nhan, giu).astype(np.uint8)), cv2.MORPH_CLOSE,
                            np.ones((7, 7), np.uint8))
    n2, nhan2 = cv2.connectedComponents(nhat, connectivity=8)
    giu2 = [int(v) for v in np.unique(nhan2[np.isin(nhan, giu)]) if v > 0]
    # phần nới tràn quá rộng (giấy ngả vàng chưa trắng hết) thì chỉ lấy lõi
    if np.isin(nhan2, giu2).sum() <= 0.3 * hn * wn:
        nhan, giu = nhan2, giu2
    mat = cv2.dilate(np.isin(nhan, giu).astype(np.uint8), np.ones((9, 9), np.uint8))
    mat = cv2.resize(mat, (w, h), interpolation=cv2.INTER_NEAREST) > 0
    xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
    # nền quanh từng điểm (lọc lấy sáng nhất): nét chữ là điểm tối hơn nền hẳn
    k = max(5, int(round(0.012 * max(h, w))) | 1)
    nen = cv2.dilate(xam, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    net = (mat & (xam.astype(np.int16) < nen.astype(np.int16) - 60)).astype(np.uint8)
    # chỉ giữ nét cỡ chữ; viền ngón tay (dải dài theo mép ngón) thì xóa
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(net, 8)
    gioi = 0.03 * max(h, w)
    nho_ = np.zeros(n, bool)
    nho_[1:] = (tk[1:, cv2.CC_STAT_WIDTH] <= gioi) & (tk[1:, cv2.CC_STAT_HEIGHT] <= gioi)
    net = nho_[nhan]
    ra = anh.copy()
    ra[mat] = 255
    ra[net] = xam[net][:, None]
    return ra


LE_VUA = 0.06  # lề "vừa": giữ lề thật của trang tới 6% cạnh dài (góp ý 15/11/2026: "lề không cần cắt sát quá")


def cat_sat_chu(anh: np.ndarray, le_chu: float = 1.5, le_toi_thieu: float = 0.015, le: str = "vua",
                giu_kho: bool = False) -> np.ndarray:
    """Cắt theo vùng chữ, chừa lề trắng; xóa vết tối lấn vào vùng chữ. Không đủ chữ thì trả nguyên ảnh.

    le: "sat" chừa lề hẹp (1,5 chiều cao chữ); "vua" giữ lề thật của trang (khoảng cách chữ tới mép ảnh), tối đa 6%
    cạnh dài, ít nhất như "sat"; "trang" giữ trọn lề tới mép ảnh. Lề luôn là nền trắng mới (vết ngoài vùng chữ mất).
    giu_kho: ảnh là một trang giấy đã cắt theo mép (có khung): trang ít chữ (cuối chương, trang tên) vẫn giữ khổ
    trang, không bị cắt còn một mẩu."""
    h, w = anh.shape[:2]
    s = min(1.0, CANH_XU_LY / max(h, w))
    nho = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else anh
    kq = _khung_noi_dung(nho)
    if kq is None:
        return anh
    (x0, y0, x1, y1), cao_chu, xoa = kq
    # quy về ảnh gốc
    x0, y0 = max(0, int(x0 / s) - 1), max(0, int(y0 / s) - 1)
    x1, y1 = min(w, int(np.ceil(x1 / s)) + 1), min(h, int(np.ceil(y1 / s)) + 1)
    if (x1 - x0) * (y1 - y0) > 0.97 * w * h:
        return anh
    # vùng chữ tìm trên ảnh gốc (ngón tay còn nguyên là một khối vết lớn); tô trắng ngón tay trên ảnh ra
    vung = xoa_da_tay(anh[y0:y1, x0:x1])
    if vung is anh[y0:y1, x0:x1]:
        vung = vung.copy()
    if xoa.any():
        xoa_goc = cv2.resize(cv2.dilate(xoa, np.ones((3, 3), np.uint8)), (w, h), interpolation=cv2.INTER_NEAREST)
        vung[xoa_goc[y0:y1, x0:x1] > 0] = 255
    toi_thieu = int(round(max(le_chu * cao_chu / s, le_toi_thieu * max(h, w))))
    if le == "sat":
        tran, duoi, trai, phai = (toi_thieu,) * 4
    else:
        tran_toi_da = max(h, w) if le == "trang" else max(toi_thieu, int(LE_VUA * max(h, w)))

        def le_that(d):
            return int(min(max(d, toi_thieu), tran_toi_da))

        # khoảng cách chữ tới mép ảnh (mép giấy sau khi nắn, trừ dải nới khung)
        tran, duoi, trai, phai = le_that(y0), le_that(h - y1), le_that(x0), le_that(w - x1)
        if giu_kho:
            # trang ít chữ: giữ khổ trang (bỏ dải nới khung 2,5% ở mép)
            bo_y, bo_x = int(0.03 * h), int(0.03 * w)
            if y1 - y0 < 0.6 * h:
                tran, duoi = max(tran, y0 - bo_y), max(duoi, h - bo_y - y1)
            if x1 - x0 < 0.5 * w:
                trai, phai = max(trai, x0 - bo_x), max(phai, w - bo_x - x1)
    return cv2.copyMakeBorder(vung, tran, duoi, trai, phai, cv2.BORDER_CONSTANT,
                              value=(255,) * (anh.shape[2] if anh.ndim == 3 else 1))
