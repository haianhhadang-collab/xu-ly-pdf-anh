"""Tạo bộ ảnh thử báo nhòe ngay sau khi chụp (xlpdf_kiemthu/mo_chup) và bộ trang chụp trùng (xlpdf_kiemthu/trung).

- mo_chup: ảnh chụp thật của người dùng (sach/goc*.png, sach2/doc*.jpg, mau1, mau3, mau4) làm nhòe như rung tay lúc
  chụp: vệt rung 12 px nghiêng 20° (tính ở cỡ trang 1600 px, chừng 0,7 cỡ chữ), và vài ảnh lấy nét hụt (mờ Gauss
  sigma 3,3 px). Ảnh gốc phải không bị báo, ảnh làm nhòe phải bị báo.
- trung: các đoạn trang của hồ sơ 214 trang người dùng gửi (Hồ sơ 15-11 19-33.pdf) có trang chụp trùng; tên tệp
  t<số thứ tự trong hồ sơ>.jpg. Đối chiếu ở kiem_thu_chat_luong.py.

Chạy:  python tao_anh_rung.py [thư mục ảnh trang của hồ sơ 214 trang]
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

KT = Path(r"D:\DevTools\src\xlpdf_kiemthu")
DOAN_TRUNG = [(25, 29), (55, 60), (89, 94), (136, 149), (175, 178)]


def _doc(p: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def rung(anh: np.ndarray, dai: float, goc: float = 20) -> np.ndarray:
    n = max(int(round(dai)), 2)
    k = np.zeros((n, n), np.float32)
    k[n // 2, :] = 1
    k = cv2.warpAffine(k, cv2.getRotationMatrix2D((n / 2 - 0.5, n / 2 - 0.5), goc, 1), (n, n))
    return cv2.filter2D(anh, -1, k / k.sum())


def anh_goc() -> list[tuple[Path, bool]]:
    """(ảnh chụp thật, có phải cặp trang sách mở)."""
    ds = [(p, True) for p in sorted((KT / "sach").glob("goc*.png"))]
    ds += [(p, False) for p in sorted((KT / "sach2").glob("doc*.jpg"))]
    ds += [(KT / "mau1-chup-nghieng.jpg", False), (KT / "mau4-chup-kem.jpg", False), (KT / "mau3-trang-doi.jpg", True)]
    return ds


def main() -> None:
    ra = KT / "mo_chup"
    ra.mkdir(exist_ok=True)
    for i, (p, doi) in enumerate(anh_goc()):
        a = _doc(p)
        s = max(1.0, max(a.shape[:2]) / 1600 / (2 if doi else 1))
        ten = p.stem + ("_doi" if doi else "")
        cv2.imencode(".jpg", rung(a, 12 * s), [cv2.IMWRITE_JPEG_QUALITY, 92])[1].tofile(str(ra / f"{ten}_rung.jpg"))
        if i % 4 == 0:
            m = cv2.GaussianBlur(a, (0, 0), 3.3 * s)
            cv2.imencode(".jpg", m, [cv2.IMWRITE_JPEG_QUALITY, 92])[1].tofile(str(ra / f"{ten}_mo.jpg"))
    if len(sys.argv) > 1:
        vao, dich = Path(sys.argv[1]), KT / "trung"
        dich.mkdir(exist_ok=True)
        for a, b in DOAN_TRUNG:
            for n in range(a, b + 1):
                shutil.copyfile(vao / f"t{n:03d}.jpg", dich / f"t{n:03d}.jpg")
    print("xong")


if __name__ == "__main__":
    main()
