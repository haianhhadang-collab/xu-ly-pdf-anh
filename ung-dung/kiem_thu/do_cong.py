"""Đo độ cong dòng chữ trước và sau khi nắn trang cong (nan_cong.py) trên bộ ảnh `anh_mau_mep`.

Mỗi ảnh: cắt, nắn phối cảnh theo 4 góc đáp án, rồi đo độ võng của từng dòng chữ (khoảng lệch lớn nhất giữa đường
cong bậc 3 và đường thẳng khớp với dòng), lấy trung vị và lớn nhất theo % chiều cao trang.

Chạy:  python do_cong.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from loi_xu_ly import nan_cong, nan_phang  # noqa: E402

THU_MUC = Path(__file__).parent / "anh_mau_mep"
RA = Path(__file__).parent / "ket_qua"


def do_vong(anh: np.ndarray) -> tuple[float, float, int]:
    xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
    h, w = xam.shape
    vong = []
    for d in nan_cong._dong_chu(xam):
        hs = nan_cong._khop_dong(d, w)
        if hs is None:
            continue
        x = np.linspace(d[:, 0].min(), d[:, 0].max(), 50)
        y = np.polyval(hs, x / w)
        thang = np.polyval(np.polyfit(x, y, 1), x)
        vong.append(float(np.abs(y - thang).max()) / h * 100)
    if not vong:
        return 0.0, 0.0, 0
    return float(np.median(vong)), float(np.max(vong)), len(vong)


def main():
    dap_an = json.loads((THU_MUC / "dap_an.json").read_text(encoding="utf-8"))
    RA.mkdir(exist_ok=True)
    dat = tong = 0
    for ten, da in dap_an.items():
        anh = cv2.imdecode(np.fromfile(str(THU_MUC / f"{ten}.jpg"), np.uint8), cv2.IMREAD_COLOR)
        h, w = anh.shape[:2]
        g = np.clip(np.array(da["goc"], np.float32), [0, 0], [w - 1, h - 1])
        trang = nan_phang.lam_phang(anh, g)
        truoc = do_vong(trang)
        sau_anh = nan_cong.nan_trang_cong(trang)
        sau = do_vong(sau_anh)
        cong = da["cong"] > 0
        if cong:
            ok = sau[0] < 0.35 * max(truoc[0], 1e-6) or sau[0] < 0.15
        else:
            ok = sau_anh is trang or sau[0] <= truoc[0] + 0.05
        tong += 1
        dat += ok
        print(f"{ten:20s} {'ĐẠT' if ok else 'TRƯỢT':5s} võng trung vị {truoc[0]:.2f}% → {sau[0]:.2f}%  lớn nhất "
              f"{truoc[1]:.2f}% → {sau[1]:.2f}%  ({truoc[2]}→{sau[2]} dòng){'' if sau_anh is not trang else '  (không nắn)'}")
        if cong:
            ghep = np.hstack([cv2.resize(trang, (600, 850)), cv2.resize(sau_anh, (600, 850))])
            (RA / f"nan-cong-{ten}.jpg").write_bytes(cv2.imencode(".jpg", ghep)[1].tobytes())
    print(f"Đạt {dat}/{tong}")


if __name__ == "__main__":
    main()
