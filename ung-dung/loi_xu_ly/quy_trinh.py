"""Ghép các bước thành luồng xử lý một ảnh, một tệp."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from . import chat_luong, cat_chu, chieu_chu, doc_ghi, lam_sach, nan_cong, nan_phang, nhan_dang


@dataclass
class TuyChon:
    """Tùy chọn xử lý ảnh trang."""
    tim_mep: bool = True
    tu_xoay: bool = True
    sua_nghieng: bool = True
    nan_cong: bool = True
    cat_sat_chu: bool = True
    le: str = "vua"  # lề khi cắt theo chữ: "sat", "vua", "trang" (xem cat_chu.cat_sat_chu)
    tach_trang_doi: bool = False
    che_do: str = "giu_mau"
    do_trang: float = 0.5
    do_dam: float = 0.5


@dataclass
class TuyChonXuat:
    """Tùy chọn ghi PDF."""
    kho: str = "a4"
    le_mm: float = 0.0
    chat_luong: str = "vua"
    ocr: bool = False
    ngon_ngu: str = "vie"
    xuat_txt: bool = False


def xu_ly_anh(anh: np.ndarray, tc: TuyChon, khung_tay=None, tu_xoay: bool | None = None):
    """Chạy luồng: tìm mép → nắn phối cảnh → xoay dòng chữ dọc về ngang → tách trang đôi → nắn trang cong → làm sạch
    → xoay đúng chiều (lật 180°) → sửa nghiêng → cắt sát chữ.

    Trả (danh sách ảnh kết quả, thông tin). Thông tin gồm `khung` (4 góc đã dùng,
    có thể None), `xoay`, `nghieng` của từng trang con.
    """
    tt = {"khung": None, "xoay": [], "nghieng": [], "canh_bao": []}
    khung = None
    if khung_tay is not None:
        khung = np.asarray(khung_tay, np.float32)
    elif tc.tim_mep:
        khung = nan_phang.tim_mep_giay(anh)
    if khung is not None:
        tt["khung"] = khung
        # khung máy tự tìm: nới ra một chút cho chữ ở mép trang cong không bị cắt lẹm (cắt sát chữ bỏ phần thừa);
        # khung người dùng tự kéo thì cắt đúng khung
        noi = nan_phang.NOI_KHUNG if (khung_tay is None and tc.cat_sat_chu and tc.che_do != "khong") else 0.0
        anh = nan_phang.lam_phang(anh, khung, noi=noi)

    xoay_tu_dong = tc.tu_xoay if tu_xoay is None else tu_xoay
    # ảnh chụp cầm máy ngang (dòng chữ chạy dọc): xoay về ngang trước, vì tìm gáy, nắn cong, sửa nghiêng, cắt sát
    # chữ đều dựa vào dòng chữ nằm ngang; xuôi hay ngược do bước đoán chiều bằng Tesseract bên dưới lo
    tt["xoay_doc"] = 0
    if xoay_tu_dong and chieu_chu.chu_doc(anh):
        anh = nan_phang.xoay_90(anh, 90)
        tt["xoay_doc"] = 90

    cac_trang = nan_phang.tach_trang_doi(anh) if tc.tach_trang_doi else [anh]
    ket_qua = []
    for trang in cac_trang:
        if tc.nan_cong:
            trang = nan_cong.nan_trang_cong(trang)
        # trang nên chụp lại: tay che trang (đo trên ảnh màu trước khi làm sạch), chữ nhòe (đo sau khi làm sạch)
        # (nhòe: độ rộng mép nét trên ảnh gốc, mọi chế độ; thêm lõi nét xám sau khi làm sạch Giữ màu / Xám)
        canh_bao = ["tay"] if chat_luong.do_tay(trang) > chat_luong.NGUONG_TAY else []
        nhoe = chat_luong.la_nhoe_goc(trang)
        sach = lam_sach.lam_sach(trang, tc.che_do, tc.do_trang, tc.do_dam)
        if nhoe or (tc.che_do in ("giu_mau", "xam") and chat_luong.la_nhoe(sach)):
            canh_bao.insert(0, "nhoe")
        tt["canh_bao"].append(canh_bao)
        if khung is not None and tc.che_do != "khong":
            sach = nan_phang.xoa_vien_toi(sach)
        goc = 0
        if xoay_tu_dong:
            goc, tin_cay = nhan_dang.huong_chu(sach)
            if goc and tin_cay >= 2.0:
                sach = nan_phang.xoay_90(sach, goc)
            else:
                goc = 0
        nghieng = 0.0
        if tc.sua_nghieng:
            nghieng = nan_phang.do_nghieng(sach)
            if nghieng:
                mau_nen = None if tc.che_do == "khong" else (255, 255, 255)
                sach = nan_phang.xoay_anh(sach, nghieng, mau_nen)
                if tc.che_do == "den_trang":  # nội suy khi xoay sinh điểm xám
                    sach = np.where(sach < 128, 0, 255).astype(np.uint8)
        if tc.cat_sat_chu and tc.che_do != "khong":
            # ảnh đã cắt theo mép giấy (hoặc là một nửa cặp trang): trang ít chữ vẫn giữ khổ trang
            sach = cat_chu.cat_sat_chu(sach, le=tc.le, giu_kho=khung is not None or len(cac_trang) == 2)
        tt["xoay"].append(goc)
        tt["nghieng"].append(nghieng)
        ket_qua.append(sach)
    return ket_qua, tt


def xu_ly_tep(duong_dan, tc: TuyChon, bao=None) -> list[np.ndarray]:
    """Đọc một tệp ảnh/PDF và xử lý mọi trang."""
    kq = []
    trang = doc_ghi.doc_tep(duong_dan)
    for i, (ten, anh) in enumerate(trang):
        if bao:
            bao(f"Xử lý {ten} ({i + 1}/{len(trang)})")
        kq.extend(xu_ly_anh(anh, tc)[0])
    return kq


def kiem_tra_anh_chup(anh: np.ndarray, tach_trang_doi: bool = False) -> list[str]:
    """Kiểm tra nhanh ảnh vừa chụp (màn camera): 'nhoe' (chữ nhòe), 'tay' (tay che trang); rỗng nếu ổn.

    Không nắn cong, không sửa nghiêng, không cắt chữ: chỉ tìm mép, nắn phối cảnh, tách cặp trang rồi đo như
    xu_ly_anh. Luôn làm sạch kiểu Giữ màu để đo nhòe (kể cả khi hồ sơ để chế độ Đen trắng), trên trang thu nhỏ
    cạnh dài 1600 px (do_nhoe cũng đo ở cỡ này). Nhòe đo thêm độ rộng mép nét trên ảnh gốc (la_nhoe_goc)."""
    h, w = anh.shape[:2]
    s = min(1.0, 3000 / max(h, w))
    if s < 1:
        anh = cv2.resize(anh, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    khung = nan_phang.tim_mep_giay(anh)
    if khung is not None:
        anh = nan_phang.lam_phang(anh, khung)
    cac_trang = nan_phang.tach_trang_doi(anh) if tach_trang_doi else [anh]
    kq: list[str] = []
    for trang in cac_trang:
        if "tay" not in kq and chat_luong.do_tay(trang) > chat_luong.NGUONG_TAY:
            kq.append("tay")
        if "nhoe" not in kq and (
            chat_luong.la_nhoe_goc(trang)
            or chat_luong.la_nhoe(lam_sach.lam_sach(chat_luong._thu_nho(trang, chat_luong.CANH)))
        ):
            kq.insert(0, "nhoe")
    return kq
