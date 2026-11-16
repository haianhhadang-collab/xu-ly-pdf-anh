"""Đối tượng trên trang (tham khảo cách làm của trình sửa PDF ONLYOFFICE; không dùng mã của họ).

- Các thao tác có khung (chữ thêm, ảnh chèn, khung che, tô sáng, hình vẽ, vùng đã dời) là đối tượng: chọn lại được
  để dời, đổi cỡ, xóa, vì ảnh trang luôn được dựng lại từ ảnh gốc + danh sách thao tác.
- Vùng có sẵn trên bản scan (đoạn chữ, ảnh, bảng) được tự đánh dấu; dời, đổi cỡ, xóa vùng giữ nguyên nét gốc
  (chép điểm mực, vá nền chỗ cũ). Vùng có mực màu (con dấu, chữ ký) bị khóa.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from . import chu_thich as ct_
from . import sua_noi_dung as snd

Hop = tuple[int, int, int, int]


# ---------------------------------------------------------------- hình vẽ

TEN_HINH = {"chu_nhat": "Hình chữ nhật", "elip": "Hình elip", "duong": "Đường thẳng", "mui_ten": "Mũi tên"}


@dataclass
class HinhVe:
    loai: str                       # chu_nhat | elip | duong | mui_ten
    diem: tuple[int, int, int, int]  # (x0, y0) → (x1, y1); đường, mũi tên giữ chiều vẽ
    mau: tuple[int, int, int] = (40, 40, 200)  # BGR
    day: int = 3

    def mo_ta(self) -> str:
        return TEN_HINH.get(self.loai, "Hình vẽ")

    def ap(self, anh: np.ndarray) -> np.ndarray:
        anh = anh.copy()
        x0, y0, x1, y1 = self.diem
        if self.loai == "chu_nhat":
            cv2.rectangle(anh, (min(x0, x1), min(y0, y1)), (max(x0, x1), max(y0, y1)), self.mau, self.day, cv2.LINE_AA)
        elif self.loai == "elip":
            tam = ((x0 + x1) // 2, (y0 + y1) // 2)
            cv2.ellipse(anh, tam, (abs(x1 - x0) // 2, abs(y1 - y0) // 2), 0, 0, 360, self.mau, self.day, cv2.LINE_AA)
        elif self.loai == "mui_ten":
            dai = max(1.0, float(np.hypot(x1 - x0, y1 - y0)))
            cv2.arrowedLine(anh, (x0, y0), (x1, y1), self.mau, self.day, cv2.LINE_AA, tipLength=min(0.4, 18 * self.day / 3 / dai))
        else:
            cv2.line(anh, (x0, y0), (x1, y1), self.mau, self.day, cv2.LINE_AA)
        return anh


# ---------------------------------------------------------------- dời, xóa vùng có sẵn

@dataclass
class DoiVung:
    """Dời (hoặc đổi cỡ) nét mực của vùng `nguon` sang `dich`; `dich` None là xóa vùng. Chỉ nét mực được chép,
    nền giấy chỗ mới giữ nguyên; chỗ cũ được vá nền."""
    nguon: Hop
    dich: Hop | None

    def mo_ta(self) -> str:
        return "Xóa vùng" if self.dich is None else "Dời vùng"

    def ap(self, anh: np.ndarray) -> np.ndarray:
        H, W = anh.shape[:2]
        x0, y0, x1, y1 = _cat_vao(self.nguon, W, H)
        if x1 - x0 < 2 or y1 - y0 < 2:
            return anh
        cat = anh[y0:y1, x0:x1].copy()
        xam = cv2.cvtColor(cat, cv2.COLOR_BGR2GRAY).astype(np.float32)
        nen, muc = float(np.percentile(xam, 90)), float(np.percentile(xam, 2))
        t, _ = cv2.threshold(xam.astype(np.uint8), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if nen - muc < 25:  # vùng trống (chỉ có nền giấy): không có gì để dời
            mat_net = np.zeros(xam.shape, np.uint8)
        else:
            mat_net = cv2.dilate((xam < max(t, nen - 25)).astype(np.uint8), np.ones((3, 3), np.uint8))
        a = np.clip((nen - xam) / max(nen - muc, 1), 0, 1) * mat_net
        mat = np.zeros((H, W), np.uint8)
        mat[y0:y1, x0:x1] = mat_net
        ra = snd.xoa_net(anh.copy(), mat, (x0, y0, x1, y1)) if mat_net.any() else anh.copy()
        if self.dich is None or not mat_net.any():
            return ra
        dx0, dy0, dx1, dy1 = self.dich
        w, h = max(1, dx1 - dx0), max(1, dy1 - dy0)
        if (w, h) != (x1 - x0, y1 - y0):
            cat = cv2.resize(cat, (w, h), interpolation=cv2.INTER_CUBIC)
            a = cv2.resize(a, (w, h), interpolation=cv2.INTER_LINEAR)
        cx0, cy0, cx1, cy1 = max(0, dx0), max(0, dy0), min(W, dx0 + w), min(H, dy0 + h)
        if cx0 >= cx1 or cy0 >= cy1:
            return ra
        aa = a[cy0 - dy0:cy1 - dy0, cx0 - dx0:cx1 - dx0, None]
        mm = cat[cy0 - dy0:cy1 - dy0, cx0 - dx0:cx1 - dx0].astype(np.float32)
        dich = ra[cy0:cy1, cx0:cx1].astype(np.float32)
        ra[cy0:cy1, cx0:cx1] = np.clip(dich * (1 - aa) + mm * aa, 0, 255).astype(np.uint8)
        return ra


def _cat_vao(hop: Hop, W: int, H: int) -> Hop:
    x0, y0, x1, y1 = hop
    return max(0, min(x0, x1)), max(0, min(y0, y1)), min(W, max(x0, x1)), min(H, max(y0, y1))


def tim_vung(anh: np.ndarray) -> list[tuple[Hop, bool]]:
    """Tự đánh dấu vùng trên bản scan (dòng chữ, ảnh, bảng, con dấu): nét mực gần nhau gộp lại theo cỡ chữ; các dòng
    để riêng (muốn lấy nhiều dòng thì kéo khung chọn). Trả [(khung, có mực màu = bị khóa)], sắp từ trên xuống."""
    H, W = anh.shape[:2]
    xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
    t, toi = cv2.threshold(xam, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if 255 - t < 30:  # trang trắng
        return []
    n, _, tk, _ = cv2.connectedComponentsWithStats(toi, connectivity=8)
    cao = tk[1:, cv2.CC_STAT_HEIGHT]
    vua = cao[(tk[1:, cv2.CC_STAT_AREA] >= 12) & (cao >= 5)]
    h = float(np.median(vua)) if len(vua) else 20.0
    # nối chữ thành dòng (ngang), nét trên dưới của cùng dòng (dấu thanh) gộp lại, dòng liền nhau vẫn tách; bỏ đốm nhỏ
    sach = np.zeros_like(toi)
    for i in range(1, n):
        if tk[i, cv2.CC_STAT_AREA] >= 6:
            x, y, w, hh = tk[i, :4]
            sach[y:y + hh, x:x + w] |= toi[y:y + hh, x:x + w]
    gop = cv2.dilate(sach, cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, int(1.5 * h)), max(3, int(0.35 * h)))))
    so, _, tk2, _ = cv2.connectedComponentsWithStats(gop, connectivity=8)
    kq = []
    for i in range(1, so):
        x, y, w, hh, dt = (int(v) for v in tk2[i])
        # khung gộp đã nới: thu lại sát nét mực
        con = sach[y:y + hh, x:x + w]
        ys, xs = np.nonzero(con)
        if len(xs) == 0:
            continue
        hop = (x + int(xs.min()), y + int(ys.min()), x + int(xs.max()) + 1, y + int(ys.max()) + 1)
        if min(hop[2] - hop[0], hop[3] - hop[1]) < 0.5 * h or (hop[2] - hop[0]) * (hop[3] - hop[1]) < h * h:
            continue  # vết bẩn, mép giấy, nét kẻ lẻ
        kq.append((hop, snd.co_muc_mau(anh, hop)))
    return sorted(kq, key=lambda v: (v[0][1], v[0][0]))


# ---------------------------------------------------------------- khung, dời, đổi cỡ đối tượng

DOI_TUONG = (snd.ThemChu, snd.ChenAnh, snd.Che, snd.ToSang, HinhVe, DoiVung)


def la_doi_tuong(tt) -> bool:
    return (isinstance(tt, DOI_TUONG) and not (isinstance(tt, DoiVung) and tt.dich is None)) or ct_.la_chu_thich(tt)


def khung(tt) -> Hop | None:
    """Khung bao của đối tượng trên ảnh trang; None nếu thao tác không phải đối tượng (sửa ký tự, sửa khối…)."""
    if ct_.la_chu_thich(tt):
        return tt.khung()
    if isinstance(tt, snd.ThemChu):
        kq = None
        for i, dong in enumerate(tt.chu.split("\n")):
            l, t, r, b = snd.khung_chu(dong or " ", tt.ten, tt.kieu, tt.co_px)
            gx, gy = tt.goc[0], tt.goc[1] + i * tt.co_px * 1.25
            hop = (gx + min(l, 0), gy + t, gx + max(r, tt.co_px * 0.3), gy + max(b, tt.co_px * 0.2))
            kq = hop if kq is None else (min(kq[0], hop[0]), min(kq[1], hop[1]), max(kq[2], hop[2]), max(kq[3], hop[3]))
        return tuple(int(round(v)) for v in kq)
    if isinstance(tt, HinhVe):
        x0, y0, x1, y1 = tt.diem
        le = tt.day + 2
        return min(x0, x1) - le, min(y0, y1) - le, max(x0, x1) + le, max(y0, y1) + le
    if isinstance(tt, DoiVung):
        return tt.dich
    if isinstance(tt, (snd.ChenAnh, snd.Che, snd.ToSang)):
        return tt.hop
    return None


def doi(tt, dx: int, dy: int):
    """Dời đối tượng."""
    if ct_.la_chu_thich(tt):
        return tt.doi(dx, dy)
    if isinstance(tt, snd.ThemChu):
        tt.goc = (tt.goc[0] + dx, tt.goc[1] + dy)
    elif isinstance(tt, HinhVe):
        x0, y0, x1, y1 = tt.diem
        tt.diem = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)
    elif isinstance(tt, DoiVung) and tt.dich is not None:
        x0, y0, x1, y1 = tt.dich
        tt.dich = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)
    elif isinstance(tt, (snd.ChenAnh, snd.Che, snd.ToSang)):
        x0, y0, x1, y1 = tt.hop
        tt.hop = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)


def dat_khung(tt, moi: Hop):
    """Đổi cỡ đối tượng cho vừa khung `moi` (chữ thêm: phóng cỡ chữ theo chiều cao)."""
    if ct_.la_chu_thich(tt):
        return tt.dat_khung(moi)
    cu = khung(tt)
    if cu is None:
        return
    x0, y0, x1, y1 = min(moi[0], moi[2]), min(moi[1], moi[3]), max(moi[0], moi[2]), max(moi[1], moi[3])
    if x1 - x0 < 3 or y1 - y0 < 3:
        return
    if isinstance(tt, snd.ThemChu):
        s = (y1 - y0) / max(1, cu[3] - cu[1])
        tt.co_px = max(4.0, tt.co_px * s)
        tt.goc = (x0 + (tt.goc[0] - cu[0]) * s, y0 + (tt.goc[1] - cu[1]) * s)
    elif isinstance(tt, HinhVe):
        le = tt.day + 2
        a0, b0, a1, b1 = cu[0] + le, cu[1] + le, cu[2] - le, cu[3] - le
        sx = (x1 - x0 - 2 * le) / max(1, a1 - a0)
        sy = (y1 - y0 - 2 * le) / max(1, b1 - b0)
        p0, q0, p1, q1 = tt.diem
        tt.diem = tuple(int(round(v)) for v in (x0 + le + (p0 - a0) * sx, y0 + le + (q0 - b0) * sy,
                                                x0 + le + (p1 - a0) * sx, y0 + le + (q1 - b0) * sy))
    elif isinstance(tt, DoiVung):
        tt.dich = (x0, y0, x1, y1)
    elif isinstance(tt, (snd.ChenAnh, snd.Che, snd.ToSang)):
        tt.hop = (x0, y0, x1, y1)
