"""Ghi đáp án Python cho bộ kiểm thử cắt theo chữ của bản Android (integration_test/cat_chu_test.dart): kích thước ảnh
sau cat_sat_chu (lề mặc định "vua") và cột gáy, cho 8 trang `xlpdf_kiemthu/sach/goc*.png` và 11 trang
`xlpdf_kiemthu/sach2/doc*.jpg` (xoay 90° trước, như bộ thử). Ghi đè dap_an_python.json của hai thư mục.

Chạy:  python ghi_dap_an_cat.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from loi_xu_ly import cat_chu, chieu_chu, nan_cong, nan_phang  # noqa: E402

KT = Path(r"D:\DevTools\src\xlpdf_kiemthu")


def _doc(p: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def main() -> int:
    da = {}
    for i in range(8):
        a = _doc(KT / "sach" / f"goc{i}.png")
        b = cat_chu.cat_sat_chu(a)
        da[f"goc{i}"] = {"cat": [b.shape[1], b.shape[0]], "gay": nan_cong.tim_gay(a)}
        print(f"goc{i}", da[f"goc{i}"])
    (KT / "sach" / "dap_an_python.json").write_text(json.dumps(da, indent=1), encoding="utf-8")
    da = {}
    for i in range(11):
        nam = _doc(KT / "sach2" / f"doc{i}.jpg")
        a = nan_phang.xoay_90(nam, 90)
        b = cat_chu.cat_sat_chu(a)
        da[f"doc{i}"] = {"chu_doc": bool(chieu_chu.chu_doc(nam)), "cat": [b.shape[1], b.shape[0]], "gay": nan_cong.tim_gay(a)}
        print(f"doc{i}", da[f"doc{i}"])
    (KT / "sach2" / "dap_an_python.json").write_text(json.dumps(da, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
