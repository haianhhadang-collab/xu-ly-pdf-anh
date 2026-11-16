"""Ghi đáp án Python cho bộ kiểm thử tách trang của bản Android (integration_test/tach_trang_test.dart): với mỗi ảnh
sách mở, đường cắt gáy (x mép trên, x mép dưới, theo ảnh đã nắn phẳng) và kích thước hai nửa.
Ghi ra D:\\DevTools\\src\\xlpdf_kiemthu\\tach_trang_python.json.

Chạy:  python ghi_dap_an_tach.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

GOC = Path(__file__).parent
sys.path.insert(0, str(GOC.parent))
from kiem_thu_tach_trang import THU_MUC, _doc  # noqa: E402
from loi_xu_ly import chieu_chu, nan_phang  # noqa: E402

KQ = Path(r"D:\DevTools\src\xlpdf_kiemthu\tach_trang_python.json")


def main() -> int:
    da = {}
    for tm in THU_MUC:
        for p in sorted(list(tm.glob("*.jpg")) + list(tm.glob("*.png"))):
            if "tung-trang" in p.stem:
                continue
            anh = _doc(p)
            khung = nan_phang.tim_mep_giay(anh)
            if khung is not None:
                anh = nan_phang.lam_phang(anh, khung, noi=nan_phang.NOI_KHUNG)
            if chieu_chu.chu_doc(anh):
                anh = nan_phang.xoay_90(anh, 90)
            duong = nan_phang._khe_gay(anh) if anh.shape[1] >= anh.shape[0] else None
            cac = nan_phang.tach_trang_doi(anh)
            da[f"{tm.name}/{p.name}"] = {
                "kt": [anh.shape[1], anh.shape[0]],
                "duong": None if duong is None else [round(duong[0], 1), round(duong[1], 1)],
                "nua": [[c.shape[1], c.shape[0]] for c in cac],
            }
            print(p.name, da[f"{tm.name}/{p.name}"])
    KQ.write_text(json.dumps(da, ensure_ascii=False, indent=1), encoding="utf-8")
    print("đã ghi", KQ)
    return 0


if __name__ == "__main__":
    sys.exit(main())
