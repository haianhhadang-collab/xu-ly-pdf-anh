"""Tự động chụp: theo dõi luồng khung hình camera, tự chụp khi trang đủ điều kiện.

Dùng khi chụp liên tục nhiều trang (lật từng trang sách, đặt lần lượt từng tờ
công văn): người dùng chỉ cần giữ máy, ứng dụng tự chụp mỗi khi thấy một trang
mới đứng yên, rõ nét, đủ sáng. Điều kiện xét theo thứ tự:

  1. thấy trang giấy (có mép giấy, hoặc giấy phủ kín khung hình như khi chụp sát sách mở);
  2. trang đủ lớn, không bị cắt mép, máy không quá nghiêng so với trang;
  3. đủ sáng, không bị lóa;
  4. máy và trang đứng yên;
  5. ảnh đủ nét;
  6. khác trang vừa chụp (chống chụp trùng khi chưa lật trang);
  7. giữ được cả 6 điều kiện trên trong `thoi_gian_giu` giây; chụp khung nét nhất trong khoảng đó.

Mỗi khung hình chỉ phân tích ảnh thu nhỏ (cạnh dài 640 px), nên chạy kịp thời
gian thực. Mã viết để chuyển thẳng sang C++ cho bản Android, iOS: lớp
`BoTuChup` nhận khung hình xem trước, trả trạng thái và lời nhắc cho giao diện.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import cv2
import numpy as np

from . import nan_phang

LOI_NHAC = {
    "khong_thay": "Chưa thấy trang giấy",
    "xa": "Đưa máy lại gần trang",
    "cat_mep": "Lùi máy ra cho thấy đủ trang",
    "nghieng": "Cầm máy song song với trang",
    "toi": "Thiếu sáng, bật thêm đèn",
    "loa": "Bị lóa, nghiêng máy một chút",
    "rung": "Giữ yên máy",
    "tay": "Bỏ tay ra khỏi trang",
    "mo": "Chưa nét, giữ yên để máy lấy nét",
    "cho_trang_moi": "Đã chụp trang này, lật sang trang mới",
    "dang_giu": "Giữ yên, sắp chụp…",
    "da_chup": "Đã chụp",
}

CO_CHU_KY = (48, 64)  # rộng, cao của ảnh thu nhỏ dùng so hai trang


@dataclass
class CauHinhTuChup:
    canh_phan_tich: int = 640        # cạnh dài ảnh dùng để phân tích (px)
    dien_tich_toi_thieu: float = 0.20  # trang chiếm ít nhất từng này phần khung hình
    le_mep: float = 0.01             # góc trang cách mép khung hình ít nhất (tỉ lệ cạnh dài)
    lech_canh_toi_da: float = 1.45   # tỉ số hai cạnh đối diện; lớn hơn là cầm máy quá nghiêng
    giay_kin_khung: float = 0.75     # tỉ lệ giấy trong khung để coi là chụp kín, không thấy mép
    sang_toi_thieu: float = 70.0     # độ sáng trung vị của trang (0–255)
    loa_toi_da: float = 0.015        # tỉ lệ điểm cháy sáng trên trang
    # máy xê dịch giữa hai khung liên tiếp, điểm ảnh của ảnh 160 px (chênh lệch chia độ tương phản cảnh): tay cầm
    # run nhẹ 0,7–1,4; va máy, lật trang trên 3. Trước đây đo chênh lệch thô (ngưỡng 5): sách trên nền đen tương
    # phản mạnh, tay run nhẹ đã vượt ngưỡng
    chuyen_dong_toi_da: float = 2.5
    # tay vuốt, lật trang chỉ chiếm một phần khung hình: xét thêm độ dời trong từng ô lưới 4×4 (video chụp thật: tay
    # di chuyển trên trang 7–35, sách nằm yên dưới 4; tay cầm máy run dưới 4–6)
    chuyen_dong_o_toi_da: float = 5.0
    tay_toi_da: float = 0.005        # phần trang bị tay che (màu da thò vào từ mép trang)
    xe_dich_toi_da: float = 0.03     # góc trang lệch so với khung trung bình lúc đang giữ (tỉ lệ đường chéo)
    do_net_toi_thieu: float = 6.0    # trung bình |Laplace| trên trang
    thoi_gian_giu: float = 0.5       # giây giữ yên trước khi chụp
    thoi_gian_chiu: float = 0.4      # khung hỏng thoáng qua lúc đang giữ (tìm mép trượt, rung, mờ) không làm chạy lại
    khac_trang: float = 0.24         # độ khác tối thiểu so với trang vừa chụp (xem khac_nhau)
    # hai cặp trang sách in cùng khổ chỉ khác nhau 0,22–0,33 (video chụp thật): đã thấy động tác lật trang (trang ra
    # khỏi khung, bị che, dịch chuyển mạnh, cộng lại `thoi_gian_lat` giây) thì chỉ cần khác `khac_trang_sau_lat`
    khac_trang_sau_lat: float = 0.18
    thoi_gian_lat: float = 1.0      # lật trang thật 1,2–4 giây; tay chạm vuốt trang 0,7 giây
    che_trang: float = 0.45          # khác trang vừa chụp hơn mức này: tay đang che hay đang lật trang


@dataclass
class TrangThai:
    ma: str                          # một khóa của LOI_NHAC
    loi_nhac: str
    khung: np.ndarray | None = None  # 4 góc trang trong khung hình hiện tại (None nếu kín khung)
    kin_khung: bool = False
    tien_do: float = 0.0             # 0–1, phần thời gian giữ yên đã qua
    anh: np.ndarray | None = None    # ảnh vừa chụp (chỉ có khi ma == "da_chup")
    khung_chup: np.ndarray | None = None
    so_trang: int = 0                # số trang đã tự chụp
    so_lieu: dict = field(default_factory=dict)


def _ti_le_giay(nho: np.ndarray, xam: np.ndarray) -> float:
    """Phần khung hình là giấy có chữ: sáng, ít màu, có nét mực."""
    hsv = cv2.cvtColor(nho, cv2.COLOR_BGR2HSV)
    _, sang = cv2.threshold(cv2.GaussianBlur(xam, (5, 5), 0), 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    giay = (sang > 0) & (hsv[..., 1] < 70)
    giay = cv2.morphologyEx(giay.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    muc = cv2.adaptiveThreshold(xam, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 12)
    ti_le = float(giay.mean())
    return ti_le if 0.005 < muc.mean() < 0.4 else 0.0


def chu_ky_trang(xam: np.ndarray, khung: np.ndarray) -> np.ndarray:
    """Bản đồ mật độ mực của trang, cỡ CO_CHU_KY, không phụ thuộc độ sáng; dùng so hai lần chụp."""
    rong, cao = CO_CHU_KY
    dich = np.float32([[0, 0], [rong * 2 - 1, 0], [rong * 2 - 1, cao * 2 - 1], [0, cao * 2 - 1]])
    m = cv2.getPerspectiveTransform(np.float32(khung), dich)
    to = cv2.warpPerspective(xam, m, (rong * 2, cao * 2), flags=cv2.INTER_LINEAR).astype(np.float32)
    muc = np.clip(1.0 - to / (cv2.GaussianBlur(to, (0, 0), 8) + 1.0), 0, 1)
    # làm mờ trước khi thu nhỏ: dòng chữ dày hơn ô lưới, xê dịch nửa điểm ảnh không đổi kết quả
    muc = cv2.GaussianBlur(muc, (0, 0), 2)
    return cv2.resize(muc, (rong, cao), interpolation=cv2.INTER_AREA) * 255.0


def khac_nhau(a: np.ndarray | None, b: np.ndarray | None, dich: int = 2) -> float:
    """Độ khác của hai trang, so với lượng mực trung bình. Trên ảnh mô phỏng: cùng một
    trang chụp lại (kể cả va máy, xoay 1°) dưới 0,16; hai trang sách khác nhau trên 0,33."""
    if a is None or b is None:
        return 9.0
    # khung trang tìm được xê dịch vài điểm ảnh giữa hai lần chụp: thử dịch ±`dich` ô, lấy nhỏ nhất
    h, w = b.shape
    giua = a[dich:h - dich, dich:w - dich]
    lech = min(float(np.abs(giua - b[dich + dy:h - dich + dy, dich + dx:w - dich + dx]).mean())
               for dy in range(-dich, dich + 1) for dx in range(-dich, dich + 1))
    return lech / max((float(a.mean()) + float(b.mean())) / 2, 1.0)


def ti_le_tay(nho: np.ndarray, khung: np.ndarray) -> float:
    """Phần trang (thu vào 8% mỗi phía) bị tay che: điểm màu da (sắc 6–25, bỏ đỏ của mực dấu; bão hòa cao hơn giấy
    30) thuộc mảng chạm dải mép trang, vì tay luôn thò vào từ ngoài; con dấu, hình minh họa trong trang không tính."""
    h, w = nho.shape[:2]
    c = khung.mean(axis=0)
    ngoai = np.zeros((h, w), np.uint8)
    trong = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(ngoai, khung.astype(np.int32), 1)
    cv2.fillConvexPoly(trong, (c + (khung - c) * 0.84).astype(np.int32), 1)
    if trong.sum() < 100:
        return 0.0
    hsv = cv2.cvtColor(nho, cv2.COLOR_BGR2HSV)
    hh, ss, vv = hsv[..., 0], hsv[..., 1].astype(int), hsv[..., 2]
    s_giay = float(np.median(ss[trong > 0]))
    da = ((hh >= 6) & (hh <= 25) & (ss > max(45.0, s_giay + 30)) & (vv >= 80) & (ngoai > 0)).astype(np.uint8)
    da = cv2.morphologyEx(da, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, nhan = cv2.connectedComponents(da, connectivity=8)
    if n < 2:
        return 0.0
    cham = np.zeros(n, bool)
    cham[np.unique(nhan[(trong == 0) & (nhan > 0)])] = True
    dt = np.bincount(nhan[trong > 0], minlength=n)
    dt[0] = 0
    return float(dt[cham].sum()) / float(trong.sum())


class BoTuChup:
    """Nhận lần lượt các khung hình camera; báo trạng thái và tự chụp khi đủ điều kiện."""

    def __init__(self, cau_hinh: CauHinhTuChup | None = None):
        self.ch = cau_hinh or CauHinhTuChup()
        self.so_trang = 0
        self._vi_truoc = None
        self._chu_ky_cuoi = None
        self._t_khung = None
        self._t_lat = self._chuoi_lat = 0.0
        self._huy_giu()

    def _ghi_lat(self, xao_tron: bool, buoc: float):
        if xao_tron:
            self._chuoi_lat += buoc
        else:
            if self._chuoi_lat >= 0.25:
                self._t_lat += self._chuoi_lat
            self._chuoi_lat = 0.0

    def dat_lai(self, quen_trang_cuoi: bool = True):
        """Bắt đầu lượt chụp mới. `quen_trang_cuoi` cho phép chụp lại trang vừa chụp."""
        self._huy_giu()
        self._vi_truoc = None
        self._t_khung = None
        if quen_trang_cuoi:
            self._chu_ky_cuoi = None
            self._t_lat = 0.0
        self._chuoi_lat = 0.0

    def _huy_giu(self):
        self._t0 = None
        self._t_tot = None
        self._tt_tot = None
        self._khung0 = None
        self._tot_nhat = None  # (độ nét, ảnh, khung, chữ ký)

    # ------------------------------------------------------------------ phân tích một khung hình
    def phan_tich(self, anh: np.ndarray) -> tuple[str, dict]:
        """Xét các điều kiện trên một khung hình. Trả (mã điều kiện đầu tiên chưa đạt
        hoặc "dat", số liệu)."""
        ch = self.ch
        h, w = anh.shape[:2]
        s = min(1.0, ch.canh_phan_tich / max(h, w))
        nho = cv2.resize(anh, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1 else anh
        hn, wn = nho.shape[:2]
        xam = cv2.cvtColor(nho, cv2.COLOR_BGR2GRAY)
        sl: dict = {"ti_le": s}

        vi = cv2.GaussianBlur(cv2.resize(xam, (160, max(1, round(160 * hn / wn))), interpolation=cv2.INTER_AREA),
                              (5, 5), 0).astype(np.int16)
        truoc, self._vi_truoc = self._vi_truoc, vi
        sl["chuyen_dong"] = sl["chuyen_dong_o"] = 0.0
        if truoc is not None and truoc.shape == vi.shape:
            gx, gy, d = np.abs(np.diff(vi, axis=1)), np.abs(np.diff(vi, axis=0)), np.abs(vi - truoc)
            # chênh lệch ≈ độ dời × độ dốc sáng: chia độ dốc trung bình ra độ dời (điểm ảnh)
            sl["chuyen_dong"] = float(d.mean()) / max(float(gx.sum() + gy.sum()) / (gx.size + gy.size), 0.5)
            oh, ow = vi.shape[0] // 4, 40
            for i in range(4):
                for j in range(4):
                    ys = slice(i * oh, (i + 1) * oh if i < 3 else None)
                    xs = slice(j * ow, (j + 1) * ow)
                    g = (gx[ys, xs].sum() + gy[ys, xs].sum()) / (2 * d[ys, xs].size)
                    sl["chuyen_dong_o"] = max(sl["chuyen_dong_o"], float(d[ys, xs].mean()) / max(float(g), 2.0))

        khung = nan_phang.tim_mep_giay(nho)
        if khung is not None:
            le = ch.le_mep * max(wn, hn)
            cham = [khung[:, 0].min() < le, khung[:, 1].min() < le,
                    khung[:, 0].max() > wn - 1 - le, khung[:, 1].max() > hn - 1 - le]
            if sum(cham) >= 3:  # khung chạm 3–4 mép: giấy phủ kín, đó không phải mép giấy thật
                khung = None
        kin_khung = False
        if khung is None:
            sl["giay"] = _ti_le_giay(nho, xam)
            if sl["giay"] < ch.giay_kin_khung:
                # có ít giấy nhưng không tìm được mép: thường là trang ở quá xa
                return ("xa" if sl["giay"] > 0.02 else "khong_thay"), sl
            kin_khung = True
            khung = np.float32([[0, 0], [wn - 1, 0], [wn - 1, hn - 1], [0, hn - 1]])
        sl["kin_khung"] = kin_khung
        sl["khung_nho"] = khung
        sl["khung"] = None if kin_khung else khung / s

        if not kin_khung:
            sl["dien_tich"] = float(cv2.contourArea(khung)) / (wn * hn)
            sl["cach_mep"] = float(min(khung[:, 0].min(), khung[:, 1].min(),
                                       wn - 1 - khung[:, 0].max(), hn - 1 - khung[:, 1].max())) / max(wn, hn)
            d = np.linalg.norm(khung - np.roll(khung, -1, axis=0), axis=1) + 1e-6
            sl["lech_canh"] = float(max(d[0] / d[2], d[2] / d[0], d[1] / d[3], d[3] / d[1]))

        mat_na = np.zeros(xam.shape, np.uint8)
        cv2.fillConvexPoly(mat_na, khung.astype(np.int32), 1)
        mat_na = cv2.erode(mat_na, np.ones((7, 7), np.uint8))
        diem = xam[mat_na > 0]
        if diem.size < 100:
            return "khong_thay", sl
        trung_vi = float(np.median(diem))
        sl["sang"] = trung_vi
        nguong_loa = max(248.0, trung_vi + 15.0)
        sl["loa"] = float((diem >= nguong_loa).mean()) if nguong_loa <= 255 else 0.0
        lap = np.abs(cv2.Laplacian(xam, cv2.CV_16S, ksize=3))
        sl["do_net"] = float(lap[mat_na > 0].mean())
        sl["chu_ky"] = chu_ky_trang(xam, khung)

        if not kin_khung:
            if sl["dien_tich"] < ch.dien_tich_toi_thieu:
                return "xa", sl
            if sl["cach_mep"] < ch.le_mep:
                return "cat_mep", sl
            if sl["lech_canh"] > ch.lech_canh_toi_da:
                return "nghieng", sl
        if trung_vi < ch.sang_toi_thieu:
            return "toi", sl
        if sl["loa"] > ch.loa_toi_da:
            return "loa", sl
        # phủ kín khung: không có mép trang để biết tay thò vào
        sl["tay"] = 0.0 if kin_khung else ti_le_tay(nho, khung)
        if sl["tay"] > ch.tay_toi_da:
            return "tay", sl
        if sl["chuyen_dong"] > ch.chuyen_dong_toi_da or sl["chuyen_dong_o"] > ch.chuyen_dong_o_toi_da:
            return "rung", sl
        if sl["do_net"] < ch.do_net_toi_thieu:
            return "mo", sl
        return "dat", sl

    # ------------------------------------------------------------------ máy trạng thái
    def nhan_khung(self, anh: np.ndarray, thoi_diem: float | None = None) -> TrangThai:
        """Đưa vào một khung hình (BGR). `thoi_diem` tính bằng giây; bỏ trống thì lấy đồng hồ máy."""
        t = time.monotonic() if thoi_diem is None else thoi_diem
        ma, sl = self.phan_tich(anh)
        buoc = 0.0 if self._t_khung is None else min(max(t - self._t_khung, 0.0), 0.3)
        self._t_khung = t
        # trang ra khỏi khung, bị che, dịch chuyển mạnh, có tay: dấu hiệu đang lật trang. Khung lỗi lẻ (tìm mép trượt)
        # không tính: chỉ cộng chuỗi khung xáo trộn liền nhau từ 0,25 giây
        xao_tron = ma in ("khong_thay", "xa", "cat_mep", "nghieng", "rung", "tay")
        tt = TrangThai(ma, LOI_NHAC.get(ma, ""), khung=sl.get("khung"), kin_khung=bool(sl.get("kin_khung")),
                       so_trang=self.so_trang, so_lieu=sl)
        if ma != "dat":
            self._ghi_lat(xao_tron, buoc)
            if ma not in ("rung", "tay") and self._t0 is not None and self._t_tot is not None and t - self._t_tot <= self.ch.thoi_gian_chiu:
                # còn trong thời gian chịu: coi như vẫn giữ (khung, tiến độ cũ), không chụp ở khung này
                tt.ma, tt.loi_nhac = "dang_giu", LOI_NHAC["dang_giu"]
                tt.khung, tt.kin_khung = self._tt_tot
                tt.tien_do = min(0.99, (t - self._t0) / max(self.ch.thoi_gian_giu, 1e-6))
                return tt
            self._huy_giu()
            return tt

        sl["khac_trang_cuoi"] = khac_nhau(sl["chu_ky"], self._chu_ky_cuoi)
        self._ghi_lat(sl["khac_trang_cuoi"] > self.ch.che_trang, buoc)
        da_lat = self._t_lat + (self._chuoi_lat if self._chuoi_lat >= 0.25 else 0) >= self.ch.thoi_gian_lat
        if sl["khac_trang_cuoi"] < (self.ch.khac_trang_sau_lat if da_lat else self.ch.khac_trang):
            if da_lat and self._t0 is not None and self._t_tot is not None                     and t - self._t_tot <= self.ch.thoi_gian_chiu:
                tt.ma, tt.loi_nhac = "dang_giu", LOI_NHAC["dang_giu"]
                tt.khung, tt.kin_khung = self._tt_tot
                tt.tien_do = min(0.99, (t - self._t0) / max(self.ch.thoi_gian_giu, 1e-6))
                return tt
            self._huy_giu()
            tt.ma, tt.loi_nhac = "cho_trang_moi", LOI_NHAC["cho_trang_moi"]
            return tt

        khung_nho = sl["khung_nho"]
        cheo = float(np.hypot(*anh.shape[:2][::-1])) * sl["ti_le"]
        if self._t0 is None or np.abs(khung_nho - self._khung0).max() / cheo > self.ch.xe_dich_toi_da:
            self._huy_giu()
            self._t0, self._khung0 = t, khung_nho
        else:  # khung trung bình trượt theo tay trôi chậm; khung tìm được rung vài điểm ảnh
            self._khung0 = 0.8 * self._khung0 + 0.2 * khung_nho
        self._t_tot, self._tt_tot = t, (sl.get("khung"), bool(sl.get("kin_khung")))
        if self._tot_nhat is None or sl["do_net"] > self._tot_nhat[0]:
            self._tot_nhat = (sl["do_net"], anh.copy(), sl["khung"], sl["chu_ky"])

        tt.tien_do = min(1.0, (t - self._t0) / max(self.ch.thoi_gian_giu, 1e-6))
        if tt.tien_do < 1.0:
            tt.ma, tt.loi_nhac = "dang_giu", LOI_NHAC["dang_giu"]
            return tt

        _, tt.anh, tt.khung_chup, self._chu_ky_cuoi = self._tot_nhat
        self._t_lat = self._chuoi_lat = 0.0
        self._huy_giu()
        self.so_trang += 1
        tt.so_trang = self.so_trang
        tt.ma, tt.loi_nhac = "da_chup", f"Đã chụp trang {self.so_trang}"
        return tt
