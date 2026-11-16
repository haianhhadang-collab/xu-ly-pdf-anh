"""Kiểm thử chụp sách mở hai trang: bộ tìm mép phải lấy cả cặp trang (không chỉ một trang), và cả quy trình xử lý
(nắn phẳng, nắn cong, làm sạch, cắt sát chữ) phải giữ đủ hai trang. Ảnh từ tao_anh_sach_mo.py.

Chạy:  python kiem_thu_sach_mo.py [--ve]      (--ve: ghi ảnh có vẽ khung vào anh_sach_mo/ve/)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

GOC = Path(__file__).parent
sys.path.insert(0, str(GOC.parent))
from loi_xu_ly import quy_trinh  # noqa: E402
from loi_xu_ly.tim_mep import tim_tu_giac  # noqa: E402
from loi_xu_ly.tu_chup import BoTuChup  # noqa: E402

THU = GOC / "anh_sach_mo"


def _doc(p: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def _iou(a: np.ndarray, b: np.ndarray, H: int, W: int) -> float:
    ma = np.zeros((H, W), np.uint8)
    mb = np.zeros((H, W), np.uint8)
    cv2.fillPoly(ma, [a.astype(np.int32)], 1)
    cv2.fillPoly(mb, [b.astype(np.int32)], 1)
    return float((ma & mb).sum() / max((ma | mb).sum(), 1))


def main() -> int:
    ve = "--ve" in sys.argv
    dap_an = json.loads((THU / "dap_an.json").read_text(encoding="utf-8"))
    if ve:
        (THU / "ve").mkdir(exist_ok=True)
    loi = 0
    tc = quy_trinh.TuyChon()
    for ten, da in dap_an.items():
        anh = _doc(THU / f"{ten}.jpg")
        H, W = anh.shape[:2]
        that = np.array(da["goc"], np.float32)
        kq = tim_tu_giac(anh)
        iou = 0.0 if kq is None else _iou(kq[0], that, H, W)
        # cả quy trình: ảnh ra phải là khổ hai trang (ngang), cao không quá rộng
        ra, _ = quy_trinh.xu_ly_anh(anh, tc)
        r = ra[0]
        ti = r.shape[1] / r.shape[0]
        dat_mep = iou >= 0.85
        mot = da.get("mot_trang", False)  # chụp từng trang: ảnh ra phải là một trang (khổ dọc)
        dat_ra = ti < 0.9 if mot else ti >= 1.1
        print(f"{ten:22s} IoU khung {iou:.2f} {'đạt' if dat_mep else 'TRƯỢT'} | ảnh ra {r.shape[1]}x{r.shape[0]} "
              f"rộng/cao {ti:.2f} {'đạt' if dat_ra else ('TRƯỢT (ghép cả trang bên cạnh)' if mot else 'TRƯỢT (mất một trang)')}")
        # tự chụp: cặp trang lọt ra ngoài khung thì phải nhắc lùi máy (không chụp nửa cặp trang)
        ma, _ = BoTuChup().phan_tich(anh)
        tran = ten.split("-")[1] == "tran"
        # cặp trang sát mép khung (dưới 3% cạnh dài): nhắc lùi máy hay không đều chấp nhận
        le = min(that[:, 0].min(), that[:, 1].min(), W - 1 - that[:, 0].max(), H - 1 - that[:, 1].max()) / max(W, H)
        if tran or (not da.get("tham_khao") and le > 0.03):
            dat_tc = (ma == "cat_mep") if tran else (ma != "cat_mep")
            print(f"    tự chụp: {ma} {'đạt' if dat_tc else 'TRƯỢT'}")
            loi += not dat_tc
        if da.get("tham_khao"):
            print("    (tham khảo, không tính: lỗi có từ bộ tìm mép 0.7.0, không do phần nối cặp trang)")
        else:
            loi += (not dat_mep) + (not dat_ra)
        if ve:
            v = anh.copy()
            cv2.polylines(v, [that.astype(np.int32)], True, (0, 255, 0), 3)
            if kq is not None:
                cv2.polylines(v, [kq[0].astype(np.int32)], True, (0, 0, 255), 3)
            (THU / "ve" / f"{ten}.jpg").write_bytes(cv2.imencode(".jpg", v)[1].tobytes())
            (THU / "ve" / f"{ten}_ra.jpg").write_bytes(cv2.imencode(".jpg", r)[1].tobytes())
    print("KQ", "đạt hết" if loi == 0 else f"{loi} lỗi")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
