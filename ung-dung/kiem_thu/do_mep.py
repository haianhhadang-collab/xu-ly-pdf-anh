"""Đo độ chính xác tìm mép giấy trên bộ ảnh tổng hợp `anh_mau_mep` (tạo bằng tao_anh_mep.py).

Chạy:  python do_mep.py [cu]      (cu: đo bộ tìm mép cũ để so)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from loi_xu_ly import nan_phang  # noqa: E402

THU_MUC = Path(__file__).parent / ("anh_mau_mep_nn" if "nn" in sys.argv else "anh_mau_mep")


def doc(p):
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def do(ham, in_ra=True):
    dap_an = json.loads((THU_MUC / "dap_an.json").read_text(encoding="utf-8"))
    dat = bo = 0
    for ten, da in dap_an.items():
        anh = doc(THU_MUC / f"{ten}.jpg")
        h, w = anh.shape[:2]
        t = time.perf_counter()
        k = ham(anh)
        ms = (time.perf_counter() - t) * 1000
        g = np.array(da["goc"])
        ra_ngoai = (g[:, 0] < -0.03 * w) | (g[:, 0] > 1.03 * w) | (g[:, 1] < -0.03 * h) | (g[:, 1] > 1.03 * h)
        if ten != "11-kin-khung" and ra_ngoai.any():
                if in_ra:
                    print(f"{ten:20s} bỏ qua (góc giấy ra ngoài khung quá xa)")
                bo += 1
                continue
        that = np.clip(g, [0, 0], [w - 1, h - 1])
        if k is None:
            # chỉ chấp nhận khi trang tràn khung (không cần cắt)
            ok = np.abs(that - np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])).max() < 0.02 * h
            sai = None
        else:
            k = nan_phang.sap_xep_goc(np.array(k, np.float32))
            sai = float(np.linalg.norm(k - that, axis=1).max())
            ok = sai < 0.012 * np.hypot(w, h)
        dat += ok
        if in_ra:
            print(f"{ten:20s} {'ĐẠT' if ok else 'TRƯỢT':5s} sai lệch góc lớn nhất {('-' if sai is None else f'{sai:6.1f} px'):>10s}  {ms:5.0f} ms")
    tong = sum(1 for _ in dap_an) - bo
    print(f"Đạt {dat}/{tong}")
    return dat, tong


if __name__ == "__main__":
    do(nan_phang.tim_mep_giay_cu if "cu" in sys.argv and hasattr(nan_phang, "tim_mep_giay_cu") else nan_phang.tim_mep_giay)
