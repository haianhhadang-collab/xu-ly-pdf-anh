"""Kiểm thử tách cặp trang sách mở thành hai trang: đường cắt phải đi giữa khe trắng ở gáy, không cắt qua chữ.

Góp ý 15/11/2026 (tệp Hồ sơ 15-11 19-33.pdf, 214 trang): trang trái dính một dải chữ đầu dòng của trang phải, trang
phải mất một hai chữ cái đầu dòng. Đo: số nét chữ chạm đường cắt (mép phải của nửa trái, mép trái của nửa phải). Cắt
đúng khe gáy thì không nét chữ nào chạm.

Ảnh thử: ảnh sách mở chụp thật (xlpdf_kiemthu/sach, sach2) và ảnh tổng hợp (anh_sach_mo, tao_anh_sach_mo.py).
Chạy:  python kiem_thu_tach_trang.py [thư mục ảnh khác…] [--ve]   (--ve: ghi hai nửa ra kiem_thu/ra_tach/)
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

GOC = Path(__file__).parent
sys.path.insert(0, str(GOC.parent))
from loi_xu_ly import chieu_chu, nan_phang  # noqa: E402

THU_MUC = [GOC / "anh_sach_mo", Path(r"D:\DevTools\src\xlpdf_kiemthu\sach"), Path(r"D:\DevTools\src\xlpdf_kiemthu\sach2")]


def _doc(p: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def nen_cham_mep(nua: np.ndarray, phia: str) -> int:
    """Số nét cỡ chữ chạm mép cắt ('phai' / 'trai') của một nửa trang."""
    xam = cv2.cvtColor(nua, cv2.COLOR_BGR2GRAY)
    h, w = xam.shape
    muc = cv2.adaptiveThreshold(xam, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 18)
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(muc, 8)
    x, y, cw, ch, dt = (tk[1:, i] for i in range(5))
    # xám trung bình từng nét: bóng gáy đen đặc (nêm đen) không phải chữ
    xam_tb = np.bincount(nhan.ravel(), xam.ravel().astype(float), minlength=n)[1:] / np.maximum(dt, 1)
    vua = (ch > 6) & (ch < 0.04 * h) & (dt > 15)
    if vua.sum() < 20:
        return 0
    cao = float(np.median(ch[vua]))
    # mảnh bóng gáy mảnh (rộng vài điểm ảnh) không tính
    chu = (ch > 0.4 * cao) & (ch < 2.5 * cao) & (cw < 4 * cao) & (dt > 0.1 * cao * cao) & (xam_tb > 45) & (cw >= 0.2 * cao)
    cham = (x + cw >= w - 2) if phia == "phai" else (x <= 1)
    # bỏ hai đầu trang (mép trên, dưới: nền, bóng)
    giua = (y > 0.04 * h) & (y + ch < 0.96 * h)
    return int((chu & cham & giua).sum())


def tach(anh: np.ndarray) -> list[np.ndarray]:
    """Giống quy trình: tìm mép → nắn phẳng (nới khung) → xoay chữ dọc → tách trang đôi."""
    khung = nan_phang.tim_mep_giay(anh)
    if khung is not None:
        anh = nan_phang.lam_phang(anh, khung, noi=nan_phang.NOI_KHUNG)
    if chieu_chu.chu_doc(anh):
        anh = nan_phang.xoay_90(anh, 90)
    return nan_phang.tach_trang_doi(anh)


def main() -> int:
    ve = "--ve" in sys.argv
    them = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    ra = GOC / "ra_tach"
    if ve:
        ra.mkdir(exist_ok=True)
    tong, loi = 0, []
    for tm in THU_MUC + them:
        if not tm.exists():
            continue
        for p in sorted(list(tm.glob("*.jpg")) + list(tm.glob("*.png"))):
            if "tung-trang" in p.stem:  # ảnh chụp từng trang: không tách
                continue
            cac = tach(_doc(p))
            if len(cac) != 2:
                print(f"{tm.name}/{p.stem:22s} không tách (một trang)")
                continue
            a, b = nen_cham_mep(cac[0], "phai"), nen_cham_mep(cac[1], "trai")
            tong += 1
            # tối đa 2 mảnh bóng gáy đen chạm mép; cắt qua chữ thì 18–24 nét chạm (cách tách cũ)
            dat = a <= 2 and b <= 2
            if not dat:
                loi.append(f"{tm.name}/{p.stem}")
            print(f"{tm.name}/{p.stem:22s} nét chạm đường cắt: trái {a:3d}, phải {b:3d}  {'đạt' if dat else 'TRƯỢT'}")
            if ve:
                for i, c in enumerate(cac):
                    cv2.imencode(".jpg", c)[1].tofile(str(ra / f"{tm.name}_{p.stem}_{i}.jpg"))
    print(f"KQ tách trang: đạt {tong - len(loi)}/{tong}; trượt: {loi}")
    return 0 if not loi else 1


if __name__ == "__main__":
    sys.exit(main())
