"""Sửa nội dung một trang ảnh: sửa chữ theo khối (dòng, đoạn) hoặc theo từ (tính năng 5, hướng A),
thêm chữ, che, chèn ảnh, tô sáng.

Mỗi thao tác là một đối tượng; ảnh trang = ảnh gốc + các thao tác áp lần lượt, nên hoàn tác hay xóa
từng thao tác chỉ cần dựng lại.

Sửa chữ: lấy nét mực của chữ cũ (thành phần liên thông chạm khung từ), đoán phông trong tập giới hạn
(Times New Roman, Arial × thường, đậm, nghiêng, đậm nghiêng) bằng cách vẽ thử chính chữ cũ rồi so hình,
đo cỡ, màu, độ nhòe; vá nền chỗ chữ cũ; dồn phần sau của dòng nếu chữ mới dài, ngắn hơn; vẽ chữ mới.
Không cho sửa vùng có mực màu (con dấu, chữ ký).
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field, replace
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import nhan_dang

PHONG = {
    "Times New Roman": {"thuong": "times.ttf", "dam": "timesbd.ttf", "nghieng": "timesi.ttf", "dam_nghieng": "timesbi.ttf"},
    "Arial": {"thuong": "arial.ttf", "dam": "arialbd.ttf", "nghieng": "ariali.ttf", "dam_nghieng": "arialbi.ttf"},
}
TEN_KIEU = {"thuong": "thường", "dam": "đậm", "nghieng": "nghiêng", "dam_nghieng": "đậm nghiêng"}
THU_MUC_PHONG = "C:/Windows/Fonts/"
SIEU_MAU = 4  # vẽ chữ ở 4× rồi thu nhỏ: khử răng cưa, đặt chữ chính xác tới 1/4 điểm ảnh


@lru_cache(maxsize=64)
def _phong(ten: str, kieu: str, co_sieu: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(THU_MUC_PHONG + PHONG[ten][kieu], co_sieu)


def diem_anh_sang_pt(rong_trang_px: int) -> float:
    """Hệ số đổi cỡ chữ điểm ảnh → pt, ước theo trang rộng bằng A4 (210 mm)."""
    return 72 * 8.2677 / rong_trang_px


# ---------------------------------------------------------------- tìm từ

@dataclass
class Tu:
    chu: str
    hop: tuple[int, int, int, int]  # x0, y0, x1, y1
    dong: tuple[int, int, int]      # (khối, đoạn, dòng) của Tesseract
    thu_tu: int                     # thứ tự từ trong dòng
    tin_cay: float


def tim_tu(anh: np.ndarray, ngon_ngu: str = "vie") -> list[Tu]:
    """Nhận dạng các từ trên trang kèm khung (Tesseract psm 3)."""
    if not nhan_dang.CO_TESSERACT:
        raise RuntimeError("Chưa cài Tesseract OCR nên không tìm được chữ trên trang.")
    import pytesseract
    d = pytesseract.image_to_data(nhan_dang._pil(anh), lang=nhan_dang.chon_ngon_ngu(ngon_ngu), config="--psm 3",
                                  output_type=pytesseract.Output.DICT)
    kq = []
    for i, chu in enumerate(d["text"]):
        chu = (chu or "").strip()
        if not chu or d["width"][i] <= 0:
            continue
        x, y, w, h = d["left"][i], d["top"][i], d["width"][i], d["height"][i]
        kq.append(Tu(chu, (x, y, x + w, y + h), (d["block_num"][i], d["par_num"][i], d["line_num"][i]),
                     d["word_num"][i], float(d["conf"][i])))
    return kq


def tu_cung_dong(cac_tu: list[Tu], tu: Tu) -> list[Tu]:
    return sorted((t for t in cac_tu if t.dong == tu.dong), key=lambda t: t.thu_tu)


# ---------------------------------------------------------------- đo nét mực

def _xam(anh):
    return cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY) if anh.ndim == 3 else anh


def mat_na_muc(anh: np.ndarray, hop, le: int = 2) -> tuple[np.ndarray, tuple[int, int, int, int]]:
    """Mặt nạ nét mực (toàn trang, uint8 0/1) của chữ trong `hop`: các thành phần tối chạm khung,
    lấy trọn nét (dấu thanh nhô ra ngoài khung vẫn lấy), bỏ thành phần chủ yếu nằm ngoài (thuộc dòng khác).
    Trả kèm khung bao của nét mực."""
    H, W = anh.shape[:2]
    x0, y0, x1, y1 = hop
    cao = y1 - y0
    # vùng xét rộng hơn khung để lấy trọn nét
    vx0, vy0 = max(0, x0 - cao), max(0, y0 - cao)
    vx1, vy1 = min(W, x1 + cao), min(H, y1 + cao)
    vung = _xam(anh[vy0:vy1, vx0:vx1])
    t, _ = cv2.threshold(vung[max(0, y0 - vy0):y1 - vy0, max(0, x0 - vx0):x1 - vx0], 0, 255,
                         cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    toi = (vung < t).astype(np.uint8)
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(toi, connectivity=8)
    kx0, ky0, kx1, ky1 = x0 - vx0 - le, y0 - vy0 - le, x1 - vx0 + le, y1 - vy0 + le
    giu = np.zeros(n, bool)
    for i in range(1, n):
        cx, cy, cw, ch, dt = tk[i]
        # phần diện tích khung bao thành phần nằm trong khung từ
        gx = max(0, min(cx + cw, kx1) - max(cx, kx0))
        gy = max(0, min(cy + ch, ky1) - max(cy, ky0))
        if gx * gy >= 0.4 * cw * ch:
            giu[i] = True
        # dấu thanh, dấu nặng: Tesseract có khi để ngoài khung từ. Nhận nét nhỏ nằm trọn trong bề ngang từ,
        # sát ngay trên hoặc dưới khung (trong 1/4 chiều cao chữ) để không lấy nhầm nét của dòng bên cạnh
        elif (cx >= kx0 - 2 and cx + cw <= kx1 + 2 and ch < 0.5 * cao and cw < 0.8 * cao
              and (ky0 - 0.25 * cao <= cy + ch <= ky0 + 2 or ky1 - 2 <= cy <= ky1 + 0.25 * cao)):
            giu[i] = True
    mat = np.zeros((H, W), np.uint8)
    mat[vy0:vy1, vx0:vx1] = giu[nhan].astype(np.uint8)
    ys, xs = np.nonzero(mat)
    if len(xs) == 0:
        return mat, hop
    return mat, (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def mau_nen(anh: np.ndarray, mat: np.ndarray, hop, le: int = 6) -> np.ndarray:
    """Màu nền quanh vùng chữ (trung vị các điểm không phải mực)."""
    H, W = anh.shape[:2]
    x0, y0, x1, y1 = hop
    vx0, vy0, vx1, vy1 = max(0, x0 - le), max(0, y0 - le), min(W, x1 + le), min(H, y1 + le)
    vung = anh[vy0:vy1, vx0:vx1].reshape(-1, 3)
    m = cv2.dilate(mat, np.ones((5, 5), np.uint8))[vy0:vy1, vx0:vx1].reshape(-1) == 0
    return np.median(vung[m], axis=0) if m.any() else np.array([255, 255, 255], float)


def co_muc_mau(anh: np.ndarray, hop, nguong: float = 0.12) -> bool:
    """Vùng có mực màu (đỏ con dấu, xanh chữ ký) chiếm đáng kể trong số điểm tối hay không."""
    x0, y0, x1, y1 = [int(v) for v in hop]
    vung = anh[max(0, y0):y1, max(0, x0):x1]
    if vung.size == 0:
        return False
    hsv = cv2.cvtColor(vung, cv2.COLOR_BGR2HSV)
    toi = hsv[..., 2] < 200
    if toi.sum() < 20:
        toi = hsv[..., 1] > 60
    mau = (hsv[..., 1] > 70) & (hsv[..., 2] < 235)
    return bool((mau & (toi | mau)).sum() > nguong * max(1, (toi | mau).sum()))


# ---------------------------------------------------------------- vẽ chữ

def khung_chu(chu: str, ten: str, kieu: str, co_px: float) -> tuple[float, float, float, float]:
    """Khung nét chữ (trái, trên, phải, dưới) tính từ gốc đường chân chữ, theo điểm ảnh."""
    l, t, r, b = _phong(ten, kieu, co_px * SIEU_MAU).getbbox(chu, anchor="ls")
    return l / SIEU_MAU, t / SIEU_MAU, r / SIEU_MAU, b / SIEU_MAU


def do_rong(chu: str, ten: str, kieu: str, co_px: float) -> float:
    return _phong(ten, kieu, co_px * SIEU_MAU).getlength(chu) / SIEU_MAU


def alpha_chu(cao_trang: int, rong_trang: int, chu: str, ten: str, kieu: str, co_px: float,
              goc: tuple[float, float], mo: float = 0.0) -> tuple[np.ndarray, tuple[int, int]]:
    """Độ phủ (0..1) của chữ đặt tại gốc đường chân `goc`; trả mảng nhỏ và góc trên trái của nó trên trang."""
    l, t, r, b = khung_chu(chu, ten, kieu, co_px)
    le = 3 + int(np.ceil(mo * 3))
    ax0 = int(np.floor(goc[0] + l)) - le
    ay0 = int(np.floor(goc[1] + t)) - le
    ax1 = int(np.ceil(goc[0] + r)) + le
    ay1 = int(np.ceil(goc[1] + b)) + le
    w, h = max(1, ax1 - ax0), max(1, ay1 - ay0)
    img = Image.new("L", (w * SIEU_MAU, h * SIEU_MAU), 0)
    ImageDraw.Draw(img).text(((goc[0] - ax0) * SIEU_MAU, (goc[1] - ay0) * SIEU_MAU), chu,
                             font=_phong(ten, kieu, co_px * SIEU_MAU), fill=255, anchor="ls")
    a = cv2.resize(np.asarray(img, np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    if mo > 0:
        a = cv2.GaussianBlur(a, (0, 0), mo)
    return a, (ax0, ay0)


def ve_alpha(anh: np.ndarray, a: np.ndarray, goc_tren_trai: tuple[int, int], mau) -> np.ndarray:
    """Phủ màu `mau` theo độ phủ `a` lên ảnh (sửa tại chỗ, cắt phần ra ngoài trang)."""
    H, W = anh.shape[:2]
    x0, y0 = goc_tren_trai
    h, w = a.shape
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if cx0 >= cx1 or cy0 >= cy1:
        return anh
    aa = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0, None]
    vung = anh[cy0:cy1, cx0:cx1].astype(np.float32)
    anh[cy0:cy1, cx0:cx1] = np.clip(vung * (1 - aa) + np.asarray(mau, np.float32) * aa, 0, 255).astype(np.uint8)
    return anh


# ---------------------------------------------------------------- đoán phông

@dataclass
class KieuChu:
    ten: str = "Times New Roman"
    kieu: str = "thuong"
    co_px: float = 40.0
    mau: tuple[int, int, int] = (20, 20, 20)  # BGR
    mo: float = 0.0
    goc: tuple[float, float] = (0.0, 0.0)     # gốc đường chân của chữ cũ
    diem: float = 0.0                          # độ khớp hình (0..1)

    def mo_ta(self, rong_trang_px: int) -> str:
        pt = self.co_px * diem_anh_sang_pt(rong_trang_px)
        b, g, r = self.mau
        return f"{self.ten} {TEN_KIEU[self.kieu]}, {pt:.1f} pt, màu #{r:02x}{g:02x}{b:02x}"


def _co_theo_cao(chu, ten, kieu, cao_muc):
    co = 40.0
    for _ in range(3):
        _, t, _, b = khung_chu(chu, ten, kieu, co)
        if b - t <= 0:
            return None
        co *= cao_muc / (b - t)
    return co


def doan_kieu_chu(anh: np.ndarray, chu: str, mat: np.ndarray, hop_muc, chi_phong: str | None = None,
                  chi_kieu: str | None = None) -> KieuChu:
    """Đoán phông, kiểu, cỡ, màu, độ nhòe của `chu` đang in trong `hop_muc` bằng cách vẽ thử và so hình."""
    x0, y0, x1, y1 = hop_muc
    H, W = anh.shape[:2]
    rong_muc, cao_muc = x1 - x0, y1 - y0
    xam = _xam(anh).astype(np.float32)
    nen = float(np.median(mau_nen(anh, mat, hop_muc))) if mat.any() else 255.0
    phu = xam[y0:y1, x0:x1]
    m = mat[y0:y1, x0:x1].astype(bool)
    dam = float(np.percentile(phu[m], 10)) if m.any() else 0.0
    # độ phủ thật của mực (0..1) trong vùng mở rộng
    le = 4
    vx0, vy0, vx1, vy1 = max(0, x0 - le), max(0, y0 - le), min(W, x1 + le), min(H, y1 + le)
    that_tho = np.clip((nen - xam[vy0:vy1, vx0:vx1]) / max(nen - dam, 1), 0, 1)
    that = that_tho * cv2.dilate(mat, np.ones((3, 3), np.uint8))[vy0:vy1, vx0:vx1]

    def dat(a, ax0, ay0):
        """Chép độ phủ `a` (góc trên trái ax0, ay0 trên trang) vào hệ tọa độ vùng so."""
        ve = np.zeros_like(that)
        sx0, sy0 = max(ax0, vx0), max(ay0, vy0)
        sx1, sy1 = min(ax0 + a.shape[1], vx1), min(ay0 + a.shape[0], vy1)
        if sx0 < sx1 and sy0 < sy1:
            ve[sy0 - vy0:sy1 - vy0, sx0 - vx0:sx1 - vx0] = a[sy0 - ay0:sy1 - ay0, sx0 - ax0:sx1 - ax0]
        return ve

    # 1) phông, kiểu: so hình nét (giao / hợp), chưa nhòe
    tot = None
    for ten in ([chi_phong] if chi_phong else PHONG):
        for kieu in ([chi_kieu] if chi_kieu else PHONG[ten]):
            co = _co_theo_cao(chu, ten, kieu, cao_muc)
            if co is None:
                continue
            l, t, r, b = khung_chu(chu, ten, kieu, co)
            lech_rong = abs((r - l) - rong_muc) / max(rong_muc, 1)
            if lech_rong > 0.35:
                continue
            # đặt sao cho khung nét khớp khung mực (căn giữa theo chiều ngang)
            goc = ((x0 + x1) / 2 - (l + r) / 2, y0 - t)
            a, (ax0, ay0) = alpha_chu(H, W, chu, ten, kieu, co, goc)
            ve = dat(a, ax0, ay0)
            diem = np.minimum(ve, that).sum() / max(np.maximum(ve, that).sum(), 1e-6) - 0.5 * lech_rong
            if tot is None or diem > tot.diem:
                tot = KieuChu(ten, kieu, co, (0, 0, 0), 0.0, goc, diem)
    # 1b) dòng dài: chỉnh cỡ theo bề rộng nét cả dòng (chính xác hơn chiều cao, vốn chỉ vài chục điểm ảnh)
    if tot is not None and len(chu) >= 8:
        l, t, r, b = khung_chu(chu, tot.ten, tot.kieu, tot.co_px)
        if r - l > 0:
            tot.co_px *= rong_muc / (r - l)
            l, t, r, b = khung_chu(chu, tot.ten, tot.kieu, tot.co_px)
            tot.goc = ((x0 + x1) / 2 - (l + r) / 2, y1 - b)
    # 2) độ nhòe: so độ sắc cạnh nét (độ dốc trung bình / độ phủ trung bình), không phụ thuộc chỗ đặt chữ
    if tot is not None:
        vung = cv2.dilate(mat, np.ones((7, 7), np.uint8))[vy0:vy1, vx0:vx1] > 0

        def do_sac(p):
            gx, gy = cv2.Sobel(p, cv2.CV_32F, 1, 0), cv2.Sobel(p, cv2.CV_32F, 0, 1)
            return float(np.sqrt(gx ** 2 + gy ** 2)[vung].mean() / max(p[vung].mean(), 1e-6))

        sac_that = do_sac(that_tho)
        lech_tot = None
        for mo in (0.0, 0.3, 0.6, 1.0):
            a, (ax0, ay0) = alpha_chu(H, W, chu, tot.ten, tot.kieu, tot.co_px, tot.goc, mo)
            lech = abs(do_sac(dat(a, ax0, ay0)) - sac_that)
            if lech_tot is None or lech < lech_tot:
                lech_tot, tot.mo = lech, mo
    if tot is None:  # chữ máy đọc sai quá: dùng Times thường theo chiều cao mực
        co = _co_theo_cao(chu or "H", "Times New Roman", "thuong", cao_muc) or cao_muc
        _, t, _, _ = khung_chu(chu or "H", "Times New Roman", "thuong", co)
        tot = KieuChu(co_px=co, goc=(x0, y0 - t))
    # màu: trung vị các điểm lõi nét (đậm nhất 40%)
    if m.any():
        loi = m & (phu <= np.percentile(phu[m], 40))
        tot.mau = tuple(int(v) for v in np.median(anh[y0:y1, x0:x1][loi], axis=0))
    return tot


# ---------------------------------------------------------------- thao tác

@dataclass
class SuaChu:
    """Thay chữ trong khung `hop` (khung các từ đã chọn, cùng một dòng) bằng `chu_moi`."""
    hop: tuple[int, int, int, int]
    chu_cu: str
    chu_moi: str
    hop_sau: tuple[int, int, int, int] | None = None  # phần còn lại của dòng bên phải, để dồn
    hop_truoc: tuple[int, int, int, int] | None = None  # phần đầu dòng bên trái (chỉ dời khi dòng căn giữa)
    can_giua: bool = False  # dòng căn giữa trang: chênh độ dài chia đều hai bên
    ten: str | None = None   # None: tự đoán
    kieu: str | None = None
    kieu_chu: KieuChu | None = field(default=None, repr=False)  # kết quả đoán, điền khi áp lần đầu
    lech_dong: float = 0.0   # đã dồn phần sau của dòng bao nhiêu điểm ảnh

    def mo_ta(self) -> str:
        return f"Sửa chữ: “{self.chu_cu}” → “{self.chu_moi}”"

    def ap(self, anh: np.ndarray) -> np.ndarray:
        anh = anh.copy()
        mat, hop_muc = mat_na_muc(anh, self.hop)
        if self.kieu_chu is None or (self.ten and self.kieu_chu.ten != self.ten) or (self.kieu and self.kieu_chu.kieu != self.kieu):
            self.kieu_chu = doan_kieu_chu(anh, self.chu_cu, mat, hop_muc, self.ten, self.kieu)
        k = self.kieu_chu
        anh = xoa_net(anh, mat, hop_muc)
        # dồn phần sau của dòng; dòng căn giữa thì chia đều sang hai bên
        rong_cu = do_rong(self.chu_cu, k.ten, k.kieu, k.co_px)
        rong_moi = do_rong(self.chu_moi, k.ten, k.kieu, k.co_px)
        lech = rong_moi - rong_cu
        self.lech_dong = lech
        goc = k.goc
        if abs(lech) >= 1:
            if self.can_giua:
                trai = int(round(-lech / 2))
                if self.hop_truoc is not None:
                    anh = _doi_vung(anh, self.hop_truoc, trai)
                if self.hop_sau is not None:
                    anh = _doi_vung(anh, self.hop_sau, int(round(lech)) + trai)
                goc = (goc[0] + trai, goc[1])
            elif self.hop_sau is not None:
                anh = _doi_vung(anh, self.hop_sau, int(round(lech)))
        a, goc_tt = alpha_chu(*anh.shape[:2], self.chu_moi, k.ten, k.kieu, k.co_px, goc, k.mo)
        return ve_alpha(anh, a, goc_tt, k.mau)


def xoa_net(anh: np.ndarray, mat: np.ndarray, hop_muc) -> np.ndarray:
    """Xóa nét mực theo mặt nạ: phủ màu nền rồi vá viền cho liền vân giấy."""
    nen = mau_nen(anh, mat, hop_muc)
    mat_xoa = cv2.dilate(mat, np.ones((5, 5), np.uint8))
    anh[mat_xoa > 0] = nen.astype(np.uint8)
    return cv2.inpaint(anh, cv2.dilate(mat_xoa, np.ones((3, 3), np.uint8)) - mat_xoa, 3, cv2.INPAINT_TELEA)


def _doi_vung(anh: np.ndarray, hop, dx: int) -> np.ndarray:
    """Dời nét mực của các từ trong `hop` (phần sau của dòng) theo chiều ngang `dx` điểm ảnh.
    Chỉ dời nét mực (không dời cả khung) để không kéo theo nét của dòng trên, dòng dưới."""
    H, W = anh.shape[:2]
    if dx == 0:
        return anh
    mat, (x0, y0, x1, y1) = mat_na_muc(anh, hop)
    if not mat.any():
        return anh
    mat = cv2.dilate(mat, np.ones((3, 3), np.uint8))  # lấy cả viền nhòe của nét
    y0, y1 = max(0, y0 - 1), min(H, y1 + 1)
    x0, x1 = max(0, x0 - 1), min(W, x1 + 1)
    cat = anh[y0:y1, x0:x1].copy()
    m = mat[y0:y1, x0:x1].astype(bool)
    nen = mau_nen(anh, mat, (x0, y0, x1, y1)).astype(np.uint8)
    anh[mat > 0] = nen
    nx0 = x0 + dx
    cx0, cx1 = max(0, nx0), min(W, nx0 + (x1 - x0))
    if cx0 < cx1:
        dich = anh[y0:y1, cx0:cx1]
        nguon, mm = cat[:, cx0 - nx0:cx1 - nx0], m[:, cx0 - nx0:cx1 - nx0]
        # "tối hơn thì lấy" để không đè mất nét có sẵn ở chỗ mới
        dich[mm] = np.minimum(dich[mm], nguon[mm])
    return anh


@dataclass
class ThemChu:
    goc: tuple[float, float]  # gốc đường chân chữ (trái, chân)
    chu: str
    ten: str = "Times New Roman"
    kieu: str = "thuong"
    co_px: float = 40.0
    mau: tuple[int, int, int] = (0, 0, 0)

    def mo_ta(self) -> str:
        return f"Thêm chữ: “{self.chu}”"

    def ap(self, anh: np.ndarray) -> np.ndarray:
        anh = anh.copy()
        for i, dong in enumerate(self.chu.split("\n")):
            g = (self.goc[0], self.goc[1] + i * self.co_px * 1.25)
            a, tt = alpha_chu(*anh.shape[:2], dong, self.ten, self.kieu, self.co_px, g)
            ve_alpha(anh, a, tt, self.mau)
        return anh


@dataclass
class Che:
    hop: tuple[int, int, int, int]
    mau: tuple[int, int, int] = (255, 255, 255)

    def mo_ta(self) -> str:
        return "Che vùng " + ("trắng" if self.mau[0] > 128 else "đen")

    def ap(self, anh: np.ndarray) -> np.ndarray:
        anh = anh.copy()
        x0, y0, x1, y1 = self.hop
        anh[max(0, y0):y1, max(0, x0):x1] = self.mau
        return anh


@dataclass
class ToSang:
    hop: tuple[int, int, int, int]
    mau: tuple[int, int, int] = (90, 240, 255)  # vàng nhạt (BGR)

    def mo_ta(self) -> str:
        return "Tô sáng"

    def ap(self, anh: np.ndarray) -> np.ndarray:
        anh = anh.copy()
        x0, y0, x1, y1 = self.hop
        v = anh[max(0, y0):y1, max(0, x0):x1].astype(np.float32)
        anh[max(0, y0):y1, max(0, x0):x1] = (v * np.asarray(self.mau, np.float32) / 255).astype(np.uint8)  # nhân màu như bút dạ
        return anh


@dataclass
class ChenAnh:
    hop: tuple[int, int, int, int]
    du_lieu: bytes = field(repr=False)  # tệp ảnh gốc (PNG, JPG)
    bo_nen_trang: bool = True           # chữ ký, con dấu chụp trên giấy trắng: bỏ nền, nhân màu

    def mo_ta(self) -> str:
        return "Chèn ảnh" + (" (bỏ nền trắng)" if self.bo_nen_trang else "")

    def ap(self, anh: np.ndarray) -> np.ndarray:
        anh = anh.copy()
        H, W = anh.shape[:2]
        x0, y0, x1, y1 = self.hop
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return anh
        img = Image.open(io.BytesIO(self.du_lieu)).convert("RGBA")
        img = img.resize((w, h), Image.LANCZOS)
        rgba = np.asarray(img, np.float32)
        mau = rgba[..., 2::-1]  # RGB → BGR
        a = rgba[..., 3:4] / 255
        cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if cx0 >= cx1 or cy0 >= cy1:
            return anh
        mau, a = mau[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0], a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        nen = anh[cy0:cy1, cx0:cx1].astype(np.float32)
        if self.bo_nen_trang:  # nhân màu: nền trắng của ảnh thành trong suốt, nét mực in lên giấy
            ra = nen * (1 - a) + nen * (mau / 255) * a
        else:
            ra = nen * (1 - a) + mau * a
        anh[cy0:cy1, cx0:cx1] = np.clip(ra, 0, 255).astype(np.uint8)
        return anh


# ---------------------------------------------------------------- khối chữ (đoạn)

TEN_CAN = {"trai": "căn trái", "giua": "căn giữa", "deu": "căn đều", "phai": "căn phải"}


@dataclass
class KhoiChu:
    """Một khối chữ: các từ cùng dòng gộp thành dòng, các dòng cùng đoạn (Tesseract) gộp thành khối."""
    dong: list[list[Tu]]
    can: str = "trai"          # trai | giua | deu | phai
    thut_dau: int = 0          # thụt đầu dòng của dòng đầu (điểm ảnh)

    @property
    def hop_dong(self) -> list[tuple[int, int, int, int]]:
        return [(min(t.hop[0] for t in d), min(t.hop[1] for t in d), max(t.hop[2] for t in d), max(t.hop[3] for t in d))
                for d in self.dong]

    @property
    def hop(self) -> tuple[int, int, int, int]:
        h = self.hop_dong
        return min(x[0] for x in h), min(x[1] for x in h), max(x[2] for x in h), max(x[3] for x in h)

    @property
    def chu_dong(self) -> list[str]:
        return [" ".join(t.chu for t in d) for d in self.dong]

    @property
    def chu(self) -> str:
        """Chữ để sửa: khối căn giữa (tiêu đề) giữ ngắt dòng, đoạn văn nối thành một dòng để tự dàn lại."""
        return ("\n" if self.can == "giua" else " ").join(self.chu_dong)


def tim_khoi(cac_tu: list[Tu], rong_trang: int) -> list[KhoiChu]:
    """Gộp các từ thành khối theo đoạn của Tesseract; đoán căn lề, thụt đầu dòng."""
    doan: dict[tuple[int, int], dict[int, list[Tu]]] = {}
    for t in cac_tu:
        doan.setdefault(t.dong[:2], {}).setdefault(t.dong[2], []).append(t)
    kq = []
    sai = 0.012 * rong_trang
    for _, cac_dong in sorted(doan.items()):
        dong = [sorted(d, key=lambda t: t.thu_tu) for _, d in sorted(cac_dong.items())]
        k = KhoiChu(dong)
        h = k.hop_dong
        x0 = [b[0] for b in h]
        x1 = [b[2] for b in h]
        tam = [(b[0] + b[2]) / 2 for b in h]
        L, R = min(x0), max(x1)
        if len(h) == 1:
            if abs(tam[0] - rong_trang / 2) < 0.02 * rong_trang and (x1[0] - x0[0]) < 0.8 * rong_trang:
                k.can = "giua"
        elif max(tam) - min(tam) < sai and max(x0) - min(x0) > sai:
            k.can = "giua"
        elif _can_deu(dong, x1, R, rong_trang) and all(v <= L + sai for v in x0[1:]):
            k.can = "deu"
        elif all(v >= R - sai for v in x1) and max(x0) - min(x0) > sai:
            k.can = "phai"
        if k.can in ("trai", "deu") and len(h) > 1 and x0[0] - L > sai and all(v <= L + sai for v in x0[1:]):
            k.thut_dau = x0[0] - L
        kq.append(k)
    return kq


def _khoang_tu(d: list[Tu]) -> float | None:
    """Khoảng trống trung bình giữa các từ của một dòng, tính theo chiều cao dòng."""
    if len(d) < 2:
        return None
    cao = max(t.hop[3] for t in d) - min(t.hop[1] for t in d)
    return float(np.mean([b.hop[0] - a.hop[2] for a, b in zip(d, d[1:])])) / max(cao, 1)


def _can_deu(dong: list[list[Tu]], x1: list[int], R: int, rong_trang: int) -> bool:
    """Căn đều hai bên: các dòng trừ dòng cuối kết thúc cùng một chỗ, và khoảng trống giữa các từ ở các dòng đó
    giãn rộng hơn dòng cuối (căn trái thì khoảng trống như nhau, đuôi dòng chỉ tình cờ gần nhau)."""
    if len(dong) < 2 or any(v < R - 0.006 * rong_trang for v in x1[:-1]):
        return False
    gian = [g for g in (_khoang_tu(d) for d in dong[:-1]) if g is not None]
    cuoi = _khoang_tu(dong[-1])
    if not gian:
        return False
    if cuoi is None:
        return len(dong) >= 3
    return float(np.mean(gian)) >= 1.12 * cuoi


def _chan_dong(mat: np.ndarray, hop_muc) -> float:
    """Đường chân chữ của một dòng: hàng dưới cùng còn đậm nét (nét chân như g, p, y mảnh nên bị loại)."""
    x0, y0, x1, y1 = hop_muc
    hang = mat[y0:y1, x0:x1].sum(axis=1)
    if not hang.any():
        return float(y1)
    nguong = 0.25 * hang.max()
    return float(y0 + np.nonzero(hang >= nguong)[0][-1] + 1)


@dataclass
class SuaKhoi:
    """Thay chữ cả khối (đoạn hoặc dòng) bằng `chu_moi`, dàn lại trong bề rộng khối như cũ.
    Xuống dòng trong `chu_moi` là ngắt dòng cứng. Khối nhiều, ít dòng hơn thì dời phần trang bên dưới."""
    hop_dong: list[tuple[int, int, int, int]]
    chu_dong: list[str]
    chu_moi: str
    can: str = "trai"
    thut_dau: int = 0
    le_trang: tuple[int, int] | None = None  # mép trái, phải của chữ trên trang (dòng căn giữa được rộng tới đây)
    doi_duoi: bool = True
    ten: str | None = None
    kieu: str | None = None
    kieu_chu: KieuChu | None = field(default=None, repr=False)
    buoc: float = 0.0          # khoảng cách dòng đo được (điểm ảnh)
    so_dong_moi: int = 0
    lech_duoi: int = 0

    @property
    def chu_cu(self) -> str:
        return " ".join(self.chu_dong)

    def mo_ta(self) -> str:
        cu, moi = self.chu_cu, self.chu_moi.replace("\n", " ")
        rut = lambda x: x if len(x) <= 40 else x[:38] + "…"  # noqa: E731
        return f"Sửa khối: “{rut(cu)}” → “{rut(moi)}”"

    def doan(self, anh: np.ndarray):
        """Đoán phông, cỡ, màu (theo dòng dài nhất) và khoảng cách dòng; không đổi ảnh.
        Trả (nét mực từng dòng, chỉ số dòng đã khớp phông, đường chân từng dòng)."""
        net = [mat_na_muc(anh, h) for h in self.hop_dong]
        j = max(range(len(net)), key=lambda i: len(self.chu_dong[i]))
        if self.kieu_chu is None or (self.ten and self.kieu_chu.ten != self.ten) or (self.kieu and self.kieu_chu.kieu != self.kieu):
            self.kieu_chu = doan_kieu_chu(anh, self.chu_dong[j], net[j][0], net[j][1], self.ten, self.kieu)
        chan = [_chan_dong(m, h) for m, h in net]
        self.buoc = float(np.median(np.diff(chan))) if len(chan) > 1 else self.kieu_chu.co_px * 1.25
        return net, j, chan

    def ap(self, anh: np.ndarray) -> np.ndarray:
        anh = anh.copy()
        H, W = anh.shape[:2]
        net, j, chan = self.doan(anh)
        k, buoc = self.kieu_chu, self.buoc
        # neo đường chân theo dòng đã khớp phông
        dau = k.goc[1] - (chan[j] - chan[0])
        mat = np.zeros((H, W), np.uint8)
        for m, _ in net:
            mat |= m
        hop_muc = (min(h[0] for _, h in net), min(h[1] for _, h in net), max(h[2] for _, h in net), max(h[3] for _, h in net))
        anh = xoa_net(anh, mat, hop_muc)

        L, R = min(h[0] for h in self.hop_dong), max(h[2] for h in self.hop_dong)
        if self.can == "giua" and self.le_trang:
            rong = max(R - L, self.le_trang[1] - self.le_trang[0])
            L, R = (L + R) / 2 - rong / 2, (L + R) / 2 + rong / 2
        elif self.can in ("trai", "deu") and self.le_trang:
            R = max(R, self.le_trang[1])  # dàn tới mép phải vùng chữ của trang
        dong_moi = dan_dong(self.chu_moi, k, R - L, self.thut_dau if self.can in ("trai", "deu") else 0)
        self.so_dong_moi = len(dong_moi)
        # số dòng đổi: dời phần trang bên dưới khối
        self.lech_duoi = int(round((len(dong_moi) - len(self.hop_dong)) * buoc))
        if self.lech_duoi and self.doi_duoi:
            y_cat = int(max(h[3] for _, h in net)) + 2
            anh = _doi_doc(anh, y_cat, self.lech_duoi)
        for i, (chu, cuoi_doan) in enumerate(dong_moi):
            y = dau + i * buoc
            thut = self.thut_dau if (i == 0 and self.can in ("trai", "deu")) else 0
            rong_dong = do_rong(chu, k.ten, k.kieu, k.co_px)
            if self.can == "giua":
                x = (L + R) / 2 - rong_dong / 2
            elif self.can == "phai":
                x = R - rong_dong
            else:
                x = L + thut
            if self.can == "deu" and not cuoi_doan and " " in chu:
                tu = chu.split(" ")
                rong_tu = [do_rong(t, k.ten, k.kieu, k.co_px) for t in tu]
                gian = (R - L - thut - sum(rong_tu)) / (len(tu) - 1)
                for t, r in zip(tu, rong_tu):
                    a, tt = alpha_chu(H, W, t, k.ten, k.kieu, k.co_px, (x, y), k.mo)
                    ve_alpha(anh, a, tt, k.mau)
                    x += r + gian
            else:
                a, tt = alpha_chu(H, W, chu, k.ten, k.kieu, k.co_px, (x, y), k.mo)
                ve_alpha(anh, a, tt, k.mau)
        return anh


def dan_dong(chu: str, k: KieuChu, rong: float, thut_dau: float = 0) -> list[tuple[str, bool]]:
    """Ngắt `chu` thành các dòng vừa bề rộng `rong` (dòng đầu trừ thụt đầu dòng).
    Trả [(dòng, là dòng cuối đoạn)]; xuống dòng trong `chu` là ngắt dòng cứng."""
    kq = []
    for so, doan in enumerate(chu.split("\n")):
        tu = doan.split()
        if not tu:
            kq.append(("", True))
            continue
        dong = tu[0]
        gioi_han = rong - (thut_dau if so == 0 else 0)
        for t in tu[1:]:
            thu = dong + " " + t
            if do_rong(thu, k.ten, k.kieu, k.co_px) <= gioi_han + 0.5:
                dong = thu
            else:
                kq.append((dong, False))
                dong, gioi_han = t, rong
        kq.append((dong, True))
    return kq


def _doi_doc(anh: np.ndarray, y: int, dy: int) -> np.ndarray:
    """Dời phần trang từ hàng `y` trở xuống `dy` điểm ảnh (âm: lên); chỗ trống tô màu nền (trung vị hàng cuối)."""
    H = anh.shape[0]
    y = max(0, min(H, y))
    if dy == 0 or y >= H:
        return anh
    nen = np.median(anh[max(0, H - 8):H].reshape(-1, 3), axis=0).astype(np.uint8)
    phan = anh[y:].copy()
    anh[y:] = nen
    if dy > 0:
        anh[min(H, y + dy):] = phan[:max(0, H - y - dy)]
    else:
        dich = max(0, y + dy)
        anh[dich:dich + len(phan)] = phan
    return anh


def chuan_bi_sua_khoi(khoi: KhoiChu, chu_moi: str, cac_tu: list[Tu] | None = None) -> SuaKhoi:
    le = (min(t.hop[0] for t in cac_tu), max(t.hop[2] for t in cac_tu)) if cac_tu else None
    return SuaKhoi(khoi.hop_dong, khoi.chu_dong, chu_moi, khoi.can, khoi.thut_dau, le)


THAO_TAC = (SuaChu, SuaKhoi, ThemChu, Che, ToSang, ChenAnh)


def ap_tat_ca(anh: np.ndarray, thao_tac: list) -> np.ndarray:
    for tt in thao_tac:
        anh = tt.ap(anh)
    return anh


def chuan_bi_sua_chu(cac_tu: list[Tu], chon: list[Tu], chu_moi: str, rong_trang: int) -> SuaChu:
    """Tạo thao tác sửa chữ từ các từ đã chọn (phải liền nhau trên cùng một dòng)."""
    if not chon:
        raise ValueError("Chưa chọn chữ nào")
    dong = tu_cung_dong(cac_tu, chon[0])
    so = sorted({dong.index(t) for t in chon if t in dong})
    if len(so) != len(chon) or so != list(range(so[0], so[-1] + 1)):
        raise ValueError("Các từ chọn phải liền nhau trên cùng một dòng")
    chon = [dong[i] for i in so]
    hop = (min(t.hop[0] for t in chon), min(t.hop[1] for t in chon),
           max(t.hop[2] for t in chon), max(t.hop[3] for t in chon))
    def bao(ds):
        return (min(t.hop[0] for t in ds), min(t.hop[1] for t in ds), max(t.hop[2] for t in ds), max(t.hop[3] for t in ds)) if ds else None

    truoc, sau = dong[:so[0]], dong[so[-1] + 1:]
    # dòng căn giữa: tâm dòng gần tâm trang, và dòng ngắn (không chạy hết bề rộng như dòng thân bài)
    x0, x1 = dong[0].hop[0], dong[-1].hop[2]
    can_giua = abs((x0 + x1) / 2 - rong_trang / 2) < 0.02 * rong_trang and (x1 - x0) < 0.8 * rong_trang
    return SuaChu(hop, " ".join(t.chu for t in chon), chu_moi, bao(sau), bao(truoc), can_giua)
