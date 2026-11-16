"""Kiểm thử báo trang nên chụp lại (loi_xu_ly/chat_luong.py).

- Nhòe: 12 trang kết quả trong hồ sơ 214 trang người dùng chụp bằng bản Android (xlpdf_kiemthu/chat_luong, tệp
  t<số thứ tự>.jpg). Chỉ t145, t146 (chụp lúc tay đang lật trang) bị báo; các trang chữ in nhạt (t027, t150, t118,
  t134, t140) và trang tốt không bị báo.
- Tay: ảnh sách mở tổng hợp (anh_sach_mo): ngón cái giữ mép sách không bị báo; ảnh tay đặt lên trang (21-tung-trang-go)
  bị báo.
- Kiểm tra ngay sau khi chụp (quy_trinh.kiem_tra_anh_chup): ảnh chụp thật (sach, sach2, mau1/3/4) không bị báo;
  các ảnh đó làm nhòe như rung tay, lấy nét hụt (xlpdf_kiemthu/mo_chup, tạo bằng tao_anh_rung.py) bị báo nhòe.
- Trùng trang (chat_luong.diem_khop): các đoạn trang của hồ sơ 214 trang có 11 cặp chụp trùng (xlpdf_kiemthu/trung);
  so mỗi trang với 3 trang trước, phải ra đúng 10 cặp (cặp 146–148: trang 146 có tay che nửa trang, dưới ngưỡng, đã
  có báo tay che).

Chạy:  python kiem_thu_chat_luong.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

GOC = Path(__file__).parent
sys.path.insert(0, str(GOC.parent))
from loi_xu_ly import chat_luong, nan_phang, quy_trinh  # noqa: E402
from tao_anh_rung import KT, anh_goc  # noqa: E402

TRANG = Path(r"D:\DevTools\src\xlpdf_kiemthu\chat_luong")
NHOE = {"t145", "t146"}
CAP_TRUNG = {(26, 27), (56, 58), (57, 59), (90, 92), (91, 93), (137, 139), (138, 140), (141, 143), (142, 144),
             (176, 177)}


def _doc(p: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def main() -> int:
    loi = []
    for p in sorted(TRANG.glob("*.jpg")):
        d = chat_luong.do_nhoe(_doc(p))
        bao = chat_luong.la_nhoe(_doc(p))
        dung = bao == (p.stem in NHOE)
        print(f"nhòe {p.stem}: ô lõi xám {d[0]:.2f}, lõi trung vị {d[1]:.0f} → {'BÁO' if bao else 'không'}"
              f" {'đạt' if dung else 'TRƯỢT'}" if d else f"nhòe {p.stem}: không đủ chữ")
        if not dung:
            loi.append(p.stem)
    for p in sorted((GOC / "anh_sach_mo").glob("*.jpg")):
        anh = _doc(p)
        khung = nan_phang.tim_mep_giay(anh)
        if khung is not None:
            anh = nan_phang.lam_phang(anh, khung, noi=nan_phang.NOI_KHUNG)
        tay = max(chat_luong.do_tay(c) for c in nan_phang.tach_trang_doi(anh))
        can = p.stem == "21-tung-trang-go"
        dung = (tay > chat_luong.NGUONG_TAY) == can
        print(f"tay {p.stem}: {tay:.3f} {'đạt' if dung else 'TRƯỢT'}")
        if not dung:
            loi.append(p.stem)
    for p, doi in anh_goc():
        kq = quy_trinh.kiem_tra_anh_chup(_doc(p), doi)
        print(f"chụp {p.name}: {kq or 'ổn'} {'đạt' if not kq else 'TRƯỢT'}")
        if kq:
            loi.append(p.name)
    for p in sorted((KT / "mo_chup").glob("*.jpg")):
        kq = quy_trinh.kiem_tra_anh_chup(_doc(p), "_doi" in p.stem)
        print(f"chụp {p.name}: {kq or 'ổn'} {'đạt' if 'nhoe' in kq else 'TRƯỢT'}")
        if "nhoe" not in kq:
            loi.append(p.name)
    ds = {int(p.stem[1:]): chat_luong.dac_trung(_doc(p)) for p in sorted((KT / "trung").glob("t*.jpg"))}
    thay = set()
    for i in ds:
        for j in range(i - 3, i):
            if j in ds:
                k = chat_luong.diem_khop(ds[i], ds[j])
                if k >= chat_luong.NGUONG_TRUNG:
                    thay.add((j, i))
                if k >= chat_luong.NGUONG_TRUNG or k >= 20:
                    print(f"trùng t{j:03d}–t{i:03d}: {k} điểm khớp")
    print(f"trùng: thấy {len(thay)} cặp, thiếu {sorted(CAP_TRUNG - thay)}, thừa {sorted(thay - CAP_TRUNG)}")
    if thay != CAP_TRUNG:
        loi.append("trung")
    print(f"KQ chất lượng: {'đạt hết' if not loi else 'trượt ' + ', '.join(loi)}")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
