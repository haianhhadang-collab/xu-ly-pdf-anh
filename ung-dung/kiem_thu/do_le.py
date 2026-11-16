"""Đo độ méo khối chữ (lề trái, lề phải xiên, cong) trước và sau quy trình xử lý, trên ảnh trang sách.

Mỗi ảnh: xoay về dòng chữ ngang nếu cần, tách hai trang ở gáy, đo độ lệch lớn nhất của lề so với hai đường thẳng
vuông góc dòng chữ (% bề ngang trang) bằng nan_cong.do_lech_le. Sau đó chạy cả quy trình (như nhập lại PDF vào ứng
dụng) và đo lại. Ảnh ra ghi vào <thư mục ảnh>/ra_le/.

Chạy:  python do_le.py <thư mục ảnh hoặc tệp PDF>     (mặc định: D:\\DevTools\\src\\xlpdf_kiemthu\\sach2)
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from loi_xu_ly import chieu_chu, nan_cong, quy_trinh  # noqa: E402


def _doc(p: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def _anh_tu_pdf(p: Path) -> list[tuple[str, np.ndarray]]:
    import pypdf
    ds = []
    for i, trang in enumerate(pypdf.PdfReader(str(p)).pages):
        for im in trang.images:
            ds.append((f"trang{i + 1:02d}", cv2.imdecode(np.frombuffer(im.data, np.uint8), cv2.IMREAD_COLOR)))
    return ds


def _do(anh: np.ndarray) -> list[float | None]:
    if chieu_chu.chu_doc(anh):
        anh = np.ascontiguousarray(np.rot90(anh, -1))
    gay = nan_cong.tim_gay(anh)
    cac = [anh[:, :gay], anh[:, gay:]] if gay else [anh]
    return [nan_cong.do_lech_le(np.ascontiguousarray(t)) for t in cac]


def _chu(v: list[float | None]) -> str:
    return " ".join("  —  " if x is None else f"{x:4.1f}%" for x in v)


def main() -> int:
    nguon = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:\DevTools\src\xlpdf_kiemthu\sach2")
    if nguon.suffix.lower() == ".pdf":
        ds = _anh_tu_pdf(nguon)
        ra = nguon.parent / (nguon.stem + "_ra_le")
    else:
        ds = [(p.stem, _doc(p)) for p in sorted(nguon.glob("*.jpg")) + sorted(nguon.glob("*.png"))]
        ra = Path(__file__).parent / "ra_le" / nguon.name
    ra.mkdir(parents=True, exist_ok=True)
    tc = quy_trinh.TuyChon()
    tong_truoc, tong_sau = [], []
    for ten, anh in ds:
        truoc = _do(anh)
        kq, _ = quy_trinh.xu_ly_anh(anh, tc)
        sau = []
        for k, r in enumerate(kq):
            sau += _do(r)
            (ra / f"{ten}_{k}.jpg").write_bytes(cv2.imencode(".jpg", r, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tobytes())
        print(f"{ten:10s} lệch lề trước {_chu(truoc):16s} sau {_chu(sau)}")
        tong_truoc += [x for x in truoc if x is not None]
        tong_sau += [x for x in sau if x is not None]
    if tong_truoc and tong_sau:
        print(f"KQ trung vị lệch lề: trước {np.median(tong_truoc):.2f}% (lớn nhất {max(tong_truoc):.1f}%), "
              f"sau {np.median(tong_sau):.2f}% (lớn nhất {max(tong_sau):.1f}%); ảnh ra ở {ra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
