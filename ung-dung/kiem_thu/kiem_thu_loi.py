"""Kiểm thử lõi xử lý trên ảnh mẫu tổng hợp (chạy tao_anh_mau.py trước).

Chạy:  python kiem_thu_loi.py
Kết quả ảnh và PDF ghi vào kiem_thu/ket_qua/.
"""
from __future__ import annotations

import json
import sys
import time
import unicodedata
from pathlib import Path

import cv2
import numpy as np

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC.parent))
from loi_xu_ly import doc_ghi, nan_phang, nhan_dang  # noqa: E402
from loi_xu_ly.quy_trinh import TuyChon, xu_ly_anh, xu_ly_tep  # noqa: E402

MAU = GOC / "anh_mau"
RA = GOC / "ket_qua"
loi = []


def kiem(dk: bool, mo_ta: str):
    print(("  ĐẠT  " if dk else "  HỎNG ") + mo_ta)
    if not dk:
        loi.append(mo_ta)


def chuan(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower()


def mau_sac(anh):
    """Số điểm đỏ, xanh và sắc độ trung bình của điểm đỏ (độ, 0..360)."""
    hsv = cv2.cvtColor(anh, cv2.COLOR_BGR2HSV_FULL).astype(np.float32)
    b, g, r = [anh[..., i].astype(int) for i in range(3)]
    do = (r > g + 60) & (r > b + 60)
    xanh = (b > r + 60) & (b > g + 30)
    h = hsv[..., 0][do] / 255 * 360
    goc = np.degrees(np.angle(np.mean(np.exp(1j * np.radians(h))))) % 360 if do.any() else float("nan")
    return int(do.sum()), int(xanh.sum()), goc


def main():
    RA.mkdir(exist_ok=True)
    tc = TuyChon()

    print("Mẫu 1: chụp nghiêng trên bàn")
    anh = doc_ghi.doc_tep(MAU / "mau1-chup-nghieng.jpg")[0][1]
    goc_dung = np.array(json.loads((MAU / "dap_an.json").read_text("utf-8"))["mau1_goc"], np.float32)
    t = time.time()
    khung = nan_phang.tim_mep_giay(anh)
    kiem(khung is not None, "tìm thấy mép giấy")
    if khung is not None:
        sai = float(np.abs(khung - goc_dung).max())
        kiem(sai < 25, f"sai số góc giấy {sai:.1f} px (< 25)")
    # tỉ lệ trang A4, nền trắng cả trang: đo khi không cắt sát chữ
    kq, tt = xu_ly_anh(anh, TuyChon(cat_sat_chu=False))
    print(f"  thời gian {time.time() - t:.2f} s, xoay {tt['xoay']}, nghiêng {tt['nghieng']}")
    trang = kq[0]
    doc_ghi.ghi_anh(trang, RA / "mau1-ket-qua.jpg")
    h, w = trang.shape[:2]
    kiem(abs(h / w - 2 ** 0.5) < 0.03, f"tỉ lệ trang {h / w:.3f} ≈ A4")
    le_duoi = trang[int(h * 0.82):int(h * 0.95), int(w * 0.1):int(w * 0.9)]
    ti_le_trang = float((le_duoi.min(axis=2) >= 245).mean())
    kiem(ti_le_trang > 0.95, f"vùng nền trắng {ti_le_trang:.1%} (> 95%), kể cả chỗ bóng đổ")
    so_do, so_xanh, sac_do = mau_sac(trang)
    kiem(so_do > 2000, f"giữ dấu đỏ: {so_do} điểm")
    kiem(so_xanh > 300, f"giữ chữ ký xanh: {so_xanh} điểm")
    _, _, sac_goc = mau_sac(anh)
    lech = abs((sac_do - sac_goc + 180) % 360 - 180)
    kiem(lech <= 10, f"sắc độ dấu đỏ lệch {lech:.1f}° (≤ 10°)")
    # cắt sát chữ (mặc định): bỏ lề trống, giữ trọn chữ, dấu đỏ, chữ ký
    sat = xu_ly_anh(anh, tc)[0][0]
    doc_ghi.ghi_anh(sat, RA / "mau1-cat-sat-chu.jpg")
    kiem(sat.shape[0] * sat.shape[1] < 0.75 * h * w, f"cắt sát chữ: còn {sat.shape[0] * sat.shape[1] / (h * w):.0%} diện tích trang")
    so_do2, so_xanh2, _ = mau_sac(sat)
    kiem(so_do2 >= 0.98 * so_do and so_xanh2 >= 0.98 * so_xanh, f"cắt sát chữ giữ đủ dấu đỏ ({so_do2}/{so_do}), chữ ký ({so_xanh2}/{so_xanh})")
    xam = cv2.cvtColor(sat, cv2.COLOR_BGR2GRAY)
    mep = np.concatenate([xam[:4].ravel(), xam[-4:].ravel(), xam[:, :4].ravel(), xam[:, -4:].ravel()])
    kiem((mep < 200).mean() < 0.001, "cắt sát chữ không lẹm vào chữ (mép ảnh trắng)")
    vb = chuan(nhan_dang.van_ban(trang, "vie"))
    kiem("cộng hòa xã hội chủ nghĩa" in vb, "OCR đọc được dòng quốc hiệu có dấu")
    kiem("searchable" in vb, "OCR đọc được dòng tiếng Anh")

    print("Mẫu 2: quét lộn ngược, nghiêng 2°")
    anh = doc_ghi.doc_tep(MAU / "mau2-lon-nguoc.jpg")[0][1]
    kq, tt = xu_ly_anh(anh, tc)
    doc_ghi.ghi_anh(kq[0], RA / "mau2-ket-qua.jpg")
    print(f"  xoay {tt['xoay']}, nghiêng {tt['nghieng']}")
    kiem(tt["xoay"][0] == 180, "tự xoay 180°")
    kiem(abs(nan_phang.do_nghieng(kq[0])) < 0.5, "độ nghiêng còn lại < 0,5°")
    kiem("độc lập" in chuan(nhan_dang.van_ban(kq[0], "vie")), "OCR đọc đúng chiều sau khi xoay")

    print("Mẫu 2b: chụp cầm máy ngang (trang nằm ngang, dòng chữ chạy dọc)")
    for goc in (90, 270):
        anh = cv2.rotate(doc_ghi.doc_tep(MAU / "mau1-chup-nghieng.jpg")[0][1],
                         cv2.ROTATE_90_CLOCKWISE if goc == 90 else cv2.ROTATE_90_COUNTERCLOCKWISE)
        kq, tt = xu_ly_anh(anh, tc)
        h, w = kq[0].shape[:2]
        print(f"  lệch {goc}°: xoay dọc {tt['xoay_doc']}, lật {tt['xoay']}, {w}x{h}")
        kiem(tt["xoay_doc"] == 90 and h > w, f"lệch {goc}°: tự xoay dòng chữ về ngang, trang đứng")
        kiem("độc lập" in chuan(nhan_dang.van_ban(kq[0], "vie")), f"lệch {goc}°: OCR đọc đúng chiều")

    print("Mẫu 3: hai trang sách")
    anh = doc_ghi.doc_tep(MAU / "mau3-trang-doi.jpg")[0][1]
    kiem(nan_phang.tim_mep_giay(anh) is None, "không cắt mất một trang khi ảnh chụp kín hai trang")
    kq, _ = xu_ly_anh(anh, TuyChon(tach_trang_doi=True))
    kiem(len(kq) == 2, f"tách thành {len(kq)} trang")
    if len(kq) == 2:
        r = kq[0].shape[1] / (kq[0].shape[1] + kq[1].shape[1])
        kiem(abs(r - 0.5) < 0.03, f"chỗ cắt ở {r:.1%} chiều rộng (gáy ở 50%)")
        for i, k in enumerate(kq):
            doc_ghi.ghi_anh(k, RA / f"mau3-trang-{i + 1}.jpg")

    print("Mẫu 4: đọc PDF, ghi PDF có lớp chữ")
    cac = xu_ly_tep(MAU / "mau4.pdf", tc)
    kiem(len(cac) == 1, "đọc được 1 trang PDF")
    pdf = RA / "mau-gop-co-lop-chu.pdf"
    tat_ca = cac + [doc_ghi.giai_ma(doc_ghi.ma_hoa(trang))]
    doc_ghi.ghi_pdf(tat_ca, pdf, kho="a4", le_mm=10, chat_luong="vua", ocr=True)
    from pypdf import PdfReader
    doc = PdfReader(pdf)
    kiem(len(doc.pages) == 2, "PDF gộp có 2 trang")
    chu = chuan(doc.pages[1].extract_text())
    kiem("thư viện" in chu, "tìm được chữ tiếng Việt trong PDF")
    mb = doc.pages[0].mediabox
    kiem(abs(float(mb.width) - 595.28) < 1, "khổ A4")
    print(f"  dung lượng {pdf.stat().st_size / 1024:.0f} KB")

    for che_do in ("xam", "den_trang"):
        k, _ = xu_ly_anh(anh=doc_ghi.doc_tep(MAU / "mau1-chup-nghieng.jpg")[0][1], tc=TuyChon(che_do=che_do))
        doc_ghi.ghi_anh(k[0], RA / f"mau1-{che_do}.png")
    kiem(doc_ghi.la_den_trang(k[0]), "chế độ đen trắng chỉ còn hai mức")

    print()
    print("TẤT CẢ ĐẠT" if not loi else f"{len(loi)} mục hỏng: " + "; ".join(loi))
    return 0 if not loi else 1


if __name__ == "__main__":
    sys.exit(main())
