"""Kiểm thử chức năng sửa PDF: sửa chữ trên trang, thêm chữ, che, tô sáng, chèn ảnh; sửa trang của PDF có sẵn.

Chạy:  python kiem_thu_sua_pdf.py   (cần Tesseract có gói vie; ảnh mẫu tạo bằng tao_anh_mau.py)
Kết quả ảnh, PDF ghi vào kiem_thu/ket_qua/sua-*.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC.parent))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from pypdf import PdfReader  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

from loi_xu_ly import doc_ghi, nhan_dang  # noqa: E402
from loi_xu_ly import chu_thich as ct  # noqa: E402
from loi_xu_ly import doi_tuong as dt  # noqa: E402
from loi_xu_ly import sua_noi_dung as snd  # noqa: E402
from loi_xu_ly.quy_trinh import TuyChon, xu_ly_anh  # noqa: E402
from loi_xu_ly.tai_lieu_pdf import TaiLieu  # noqa: E402

RA = GOC / "ket_qua"
RA.mkdir(exist_ok=True)
loi: list[str] = []


def kiem(dk: bool, mo_ta: str) -> None:
    print(("  đạt  " if dk else "  SAI  ") + mo_ta)
    if not dk:
        loi.append(mo_ta)


def gon(s: str) -> str:
    return " ".join(s.replace("—", "–").split())


def trang_mau() -> np.ndarray:
    anh = doc_ghi.doc_tep(GOC / "anh_mau" / "mau1-chup-nghieng.jpg")[0][1]
    # trang mẫu đủ khổ (không cắt sát chữ): các mục đo vị trí dòng, lề theo trang gốc
    return xu_ly_anh(anh, TuyChon(tu_xoay=False, cat_sat_chu=False))[0][0]


def tim(cac_tu, chuoi):
    w = chuoi.split()
    for t in cac_tu:
        dong = snd.tu_cung_dong(cac_tu, t)
        j = dong.index(t)
        if [d.chu for d in dong[j:j + len(w)]] == w:
            return dong[j:j + len(w)]
    raise AssertionError(f"Không thấy “{chuoi}” trên trang")


def kiem_sua_chu(anh):
    print("1. Sửa chữ trên trang")
    cac_tu = snd.tim_tu(anh)
    W = anh.shape[1]
    for cu, moi, phong, kieu in [
        ("Thư viện Trường", "Trung tâm Thông tin – Thư viện Trường", "Times New Roman", "thuong"),
        ("15", "20", "Times New Roman", "thuong"),
        ("CÔNG VĂN", "TỜ TRÌNH", "Times New Roman", "dam"),
    ]:
        chon = tim(cac_tu, cu)
        tt = snd.chuan_bi_sua_chu(cac_tu, chon, moi, W)
        ra = tt.ap(anh)
        k = tt.kieu_chu
        x0, y0, x1, y1 = tt.hop
        cao = y1 - y0
        dong_cu = gon(nhan_dang.van_ban(anh[y0 - cao:y1 + cao], "vie"))
        dong_moi = gon(nhan_dang.van_ban(ra[y0 - cao:y1 + cao], "vie"))
        print(f"     “{cu}” → “{moi}”: đoán {k.mo_ta(W)}, nhòe {k.mo}; dòng sau sửa: {dong_moi}")
        kiem((k.ten, k.kieu) == (phong, kieu), f"đoán đúng phông {phong} {snd.TEN_KIEU[kieu]} cho “{cu}”")
        kiem(gon(moi) in dong_moi and gon(dong_cu).replace(gon(cu), gon(moi)) == dong_moi,
             f"dòng đọc lại đúng bằng dòng cũ thay “{cu}” → “{moi}”")
        # ngoài dải dòng đang sửa không đổi điểm ảnh nào
        ngoai = np.ones(anh.shape[0], bool)
        ngoai[max(0, y0 - cao // 2):y1 + cao // 2] = False
        kiem(int(np.abs(ra[ngoai].astype(int) - anh[ngoai].astype(int)).max()) == 0, "các dòng khác giữ nguyên")
        if tt.can_giua:
            xs = np.nonzero((cv2.cvtColor(ra[y0:y1], cv2.COLOR_BGR2GRAY) < 128).any(axis=0))[0]
            xs0 = np.nonzero((cv2.cvtColor(anh[y0:y1], cv2.COLOR_BGR2GRAY) < 128).any(axis=0))[0]
            lech = abs((xs[0] + xs[-1]) / 2 - (xs0[0] + xs0[-1]) / 2)
            kiem(lech <= 3, f"dòng căn giữa vẫn ở giữa (tâm lệch {lech:.1f} px)")
        doc_ghi.ghi_anh(np.vstack([anh[y0 - cao:y1 + cao], ra[y0 - cao:y1 + cao]]), RA / f"sua-chu-{len(loi)}-{cu[:6]}.png")


def kiem_sua_khoi(anh):
    print("1b. Sửa theo khối (dòng, đoạn)")
    cac_tu = snd.tim_tu(anh)
    H, W = anh.shape[:2]
    khoi = snd.tim_khoi(cac_tu, W)
    theo_chu = {k.chu.split()[0]: k for k in khoi}
    kiem(theo_chu["CỘNG"].can == "giua" and len(theo_chu["CỘNG"].dong) == 2, "quốc hiệu, tiêu ngữ: một khối 2 dòng căn giữa")
    kiem(theo_chu["CÔNG"].can == "giua", "tên công văn: khối căn giữa")
    kiem(theo_chu["Căn"].can == "trai" and len(theo_chu["Căn"].dong) == 2, "đoạn “Căn cứ…”: một khối 2 dòng căn trái")
    # đoạn viết dài thêm: dàn lại, dòng đầu ngắt đúng chỗ cũ, phần dưới dời xuống
    k = theo_chu["Căn"]
    them = " Phòng Hành chính sẽ cử cán bộ phối hợp kiểm đếm, bàn giao hồ sơ theo từng đợt và lập biên bản."
    tt = snd.chuan_bi_sua_khoi(k, k.chu + them, cac_tu)
    ra = tt.ap(anh)
    x0, y0, x1, y1 = k.hop
    print(f"     đoạn “Căn cứ…”: {tt.kieu_chu.mo_ta(W)}, {len(k.dong)} → {tt.so_dong_moi} dòng, dời dưới {tt.lech_duoi} px")
    kiem(tt.so_dong_moi == 4 and tt.lech_duoi > 0, "đoạn dài thêm thành 4 dòng, phần dưới dời xuống")
    vb = gon(nhan_dang.van_ban(ra[y0 - 20:y0 + 4 * round(tt.buoc)], "vie"))
    kiem(gon(them) in vb, f"đọc lại đoạn mới có câu thêm: …{vb[-60:]}")
    dong1 = gon(nhan_dang.van_ban(ra[y0 - 15:y0 + round(tt.buoc) - 10], "vie"))
    kiem(dong1.endswith("đề nghị"), f"dòng đầu ngắt đúng chỗ cũ: …{dong1[-30:]}")
    kiem(int(np.abs(ra[:y0 - 30].astype(int) - anh[:y0 - 30].astype(int)).max()) == 0, "phần trên khối giữ nguyên")
    duoi_cu, duoi_moi = anh[y1 + 20:H - tt.lech_duoi - 5], ra[y1 + 20 + tt.lech_duoi:H - 5]
    kiem(np.abs(duoi_moi.astype(int) - duoi_cu.astype(int)).mean() < 1.0, "phần dưới dời nguyên vẹn")
    # tiêu đề căn giữa dài hơn vẫn ở giữa trang
    k = theo_chu["CÔNG"]
    tt = snd.chuan_bi_sua_khoi(k, "TỜ TRÌNH VỀ VIỆC SỐ HÓA TÀI LIỆU LƯU TRỮ", cac_tu)
    ra = tt.ap(anh)
    x0, y0, x1, y1 = k.hop
    xs = np.nonzero((cv2.cvtColor(ra[y0:y1], cv2.COLOR_BGR2GRAY) < 128).any(axis=0))[0]
    lech = abs((xs[0] + xs[-1]) / 2 - (x0 + x1) / 2)
    kiem(tt.kieu_chu.kieu == "dam" and lech <= 3, f"tiêu đề mới đậm, vẫn căn giữa (tâm lệch {lech:.1f} px)")
    kiem("TỜ TRÌNH VỀ VIỆC" in gon(nhan_dang.van_ban(ra[y0 - 20:y1 + 20], "vie")), "đọc lại tiêu đề mới")
    doc_ghi.ghi_anh(ra[:1000], RA / "sua-khoi-tieu-de.png")


def trang_muc_luc() -> np.ndarray:
    """Trang mục lục tổng hợp: chữ, dãy chấm dẫn, số trang căn phải (Times, giấy hơi ngà)."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1240, 420), (248, 245, 236))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 30)
    for i, (chu, so) in enumerate([("1.1. Mục tiêu nghiên cứu", "12"), ("1.2. Phương pháp nghiên cứu", "156"),
                                   ("1.3. Kết quả đạt được và hạn chế", "27")]):
        y = 80 + i * 90
        d.text((120, y), chu, font=f, fill=(30, 30, 30), anchor="ls")
        x = d.textlength(chu, font=f) + 128
        while x < 1060:
            d.text((x, y), ".", font=f, fill=(30, 30, 30), anchor="ls")
            x += 10
        d.text((1120, y), so, font=f, fill=(30, 30, 30), anchor="rs")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def kiem_sua_ky_tu(anh):
    from loi_xu_ly import sua_ky_tu as sk
    print("1c. Sửa ký tự giữ nguyên bản gốc")
    cac_dong = sk.doc_dong(anh)
    d = next(d for d in cac_dong if "tháng 12" in d.chu)
    p = sk.PhienSuaDong(anh, cac_dong, d)
    so15 = next(i for i, m in enumerate(p.manh) if m.chu == "5" and p.manh[i - 1].chu == "1")
    p.con_tro = so15 + 1
    p.xoa_lui()
    p.xoa_lui()
    p.go("20")
    tt = p.thao_tac()
    ra = tt.ap(anh)
    y0, y1 = d.dai
    ngoai = np.ones(anh.shape[0], bool)
    ngoai[y0:y1] = False
    kiem(int(np.abs(ra[ngoai].astype(int) - anh[ngoai].astype(int)).max()) == 0, "ngoài dòng sửa không đổi điểm ảnh nào")
    x_sua = p.x0 + sum(m.rong for m in p.goc[:so15 - 1])
    kiem(np.array_equal(ra[y0:y1, :x_sua], anh[y0:y1, :x_sua]), "phần dòng trước chỗ sửa giữ nguyên từng điểm ảnh")
    kiem(all(m.loai == "chep" and not m.chua_chac for m in tt.manh if m.loai != "goc"), "“2”, “0” chép nguyên hình từ chính trang")
    vb = gon(nhan_dang.van_ban(ra[y0:y1], "vie"))
    kiem("ngày 20 tháng 12" in vb, f"đọc lại: {vb}")
    # phần sau chỗ sửa dời đúng bằng chênh lệch bề rộng ("20" so với "15"), giữ nguyên điểm ảnh
    x_sau = x_sua + sum(m.rong for m in p.goc[so15 - 1:so15 + 1])
    lech = sum(m.rong for m in tt.manh[so15 - 1:so15 + 1]) - (x_sau - x_sua)
    # chỉ nét mực của dòng được dời (nền giữ tại chỗ); dòng nghiêng thì dời cả theo độ dốc
    dy = int(round(d.nghieng * lech))
    cu, moi = anh[y0:y1, x_sau:p.x1_cu], ra[y0 + dy:y1 + dy, x_sau + lech:p.x1_cu + lech]
    net = cv2.cvtColor(cu, cv2.COLOR_BGR2GRAY) < 160
    kiem(moi.shape == cu.shape and np.array_equal(moi[net], cu[net]),
         f"phần sau chỗ sửa dời {lech:+d} px, nét chữ giữ nguyên từng điểm ảnh")
    doc_ghi.ghi_anh(np.vstack([anh[y0:y1], ra[y0:y1]]), RA / "sua-ky-tu-ngay.png")

    ml = trang_muc_luc()
    cac_dong = sk.doc_dong(ml)
    d = next(d for d in cac_dong if "Phương" in d.chu)
    p = sk.PhienSuaDong(ml, cac_dong, d)
    so_cham = sum(1 for m in p.goc if m.chu == ".")
    p.cuoi_dong()
    p.xoa_lui()  # 156 → 15
    tt = p.thao_tac()
    ra = tt.ap(ml)
    y0, y1 = d.dai

    def mep_phai(a):
        cot = np.nonzero((cv2.cvtColor(a[y0:y1], cv2.COLOR_BGR2GRAY) < 128).any(axis=0))[0]
        return int(cot.max())
    kiem(so_cham >= 20, f"nhận ra dãy chấm dẫn theo hình dạng ({so_cham} chấm)")
    kiem(abs(mep_phai(ra) - mep_phai(ml)) <= 2, f"bỏ số cuối, số trang vẫn căn phải (lệch {mep_phai(ra) - mep_phai(ml)} px)")
    kiem(sum(1 for m in tt.manh if m.chu == ".") > so_cham, "dãy chấm giãn ra lấp chỗ trống")
    # Tesseract bỏ qua số đứng lẻ ở mép phải khi đọc cả dòng: đọc riêng vùng số trang
    import pytesseract
    vb = pytesseract.image_to_string(nhan_dang._pil(ra[y0:y1, 1066:]), config="--psm 7 -c tessedit_char_whitelist=0123456789").strip()
    kiem(vb == "15", f"đọc lại số trang: {vb}")
    # chèn chữ trước dãy chấm: dãy chấm co lại, số trang đứng nguyên
    d = next(d for d in cac_dong if "Mục" in d.chu)
    p = sk.PhienSuaDong(ml, cac_dong, d)
    p.con_tro = next(i for i, m in enumerate(p.manh) if m.chu == "M")
    p.go("các ")
    ra2 = p.thao_tac().ap(ml)
    y0, y1 = d.dai
    kiem(abs(mep_phai(ra2) - mep_phai(ml)) <= 2, "chèn chữ trước dãy chấm, số trang đứng nguyên chỗ")
    vb = gon(nhan_dang.van_ban(ra2[y0:y1], "vie"))
    kiem("1.1. các Mục tiêu" in vb, f"đọc lại: {vb[:40]}")
    doc_ghi.ghi_anh(np.vstack([ml, ra, ra2]), RA / "sua-ky-tu-muc-luc.png")


def trang_nghieng(goc: float = 2.5) -> np.ndarray:
    """Trang chụp lệch: năm dòng chữ sát nhau (dấu thanh dòng dưới gần chạm dòng trên), xoay 2,5°."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1500, 700
    img = Image.new("RGB", (W, H), (246, 244, 238))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 44)
    for i, t in enumerate(["Tên hàng: Cờ tướng lớn loại một.", "Thành phẩm: nhựa Melamine cao cấp.",
                           "Ngày sản xuất: tháng mười năm nay.", "Sản xuất tại Việt Nam, xưởng số hai.",
                           "Địa chỉ: Số 2909 Quốc lộ một, phường Tân Thới."]):
        d.text((120, 120 + i * 52), t, font=f, fill=(25, 25, 30))
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), goc, 1.0)
    return cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=(238, 244, 246))


def kiem_dong_nghieng():
    from loi_xu_ly import sua_ky_tu as sk
    print("1d. Sửa ký tự trên dòng nghiêng (ảnh chụp lệch, dòng sát nhau)")
    anh = trang_nghieng()
    cac_dong = sk.doc_dong(anh)
    d = next(d for d in cac_dong if "Melamine" in d.chu)
    kiem(abs(d.nghieng + np.tan(np.radians(2.5))) < 0.004, f"đo được độ nghiêng dòng {d.nghieng:.4f} (thật −0,0437)")
    p = sk.PhienSuaDong(anh, cac_dong, d)
    p.con_tro = next(i for i, m in enumerate(p.manh) if m.chu == ":") + 1
    p.go(" nhựa ăn")
    tt = p.thao_tac()
    ra = tt.ap(anh)
    y0, y1 = d.dai
    doi = np.any(ra != anh, axis=2)
    _, khac = sk.net_cua_dong(anh, cac_dong, d, 0, anh.shape[1])
    kiem(not doi[:y0].any() and not doi[y1:].any() and not (doi[y0:y1] & khac).any(),
         "nét dòng trên, dòng dưới lọt vào dải dòng sửa không đổi điểm ảnh nào")
    x_sua = p.x0 + sum(m.rong for m in p.goc[:p.con_tro - len(" nhựa ăn")])
    kiem(not doi[:, :x_sua].any(), "phần dòng trước chỗ sửa giữ nguyên từng điểm ảnh")
    moi = sk.doc_dong(ra)
    dm = next(e for e in moi if "Melamine" in e.chu)
    kiem("nhựa ăn nhựa Melamine" in dm.chu, f"đọc lại: {dm.chu}")
    # ký tự chèn (không nét xuống) đứng trên đường chân xiên của dòng tại chỗ chèn
    x_het = x_sua + sum(m.rong for m in tt.manh[p.con_tro - len(" nhựa ăn"):p.con_tro])
    lech = [c.hop[3] - d.chan_tai((c.hop[0] + c.hop[2]) / 2) for c in dm.ky_tu
            if x_sua <= c.hop[0] and c.hop[2] <= x_het and c.chu in "nhaăn"]
    kiem(len(lech) >= 4 and max(map(abs, lech)) <= 2.5, f"ký tự chèn đúng đường chân dòng nghiêng (lệch {[round(v, 1) for v in lech]} px)")
    doc_ghi.ghi_anh(np.vstack([anh[60:420], ra[60:420]]), RA / "sua-ky-tu-dong-nghieng.png")


def trang_dam_nhat() -> np.ndarray:
    """Nhãn hàng chụp mờ: dòng chữ thường xen dòng chữ đậm (Times New Roman, Times đậm), làm mờ như ảnh chụp.
    Chữ "é" chỉ có ở dòng đậm; "ộ" không có ở đâu."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1500, 520
    img = Image.new("RGB", (W, H), (240, 238, 230))
    d = ImageDraw.Draw(img)
    thuong = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 44)
    dam = ImageFont.truetype("C:/Windows/Fonts/timesbd.ttf", 44)
    for i, (t, f) in enumerate([("Tên hàng: Cờ tướng lớn loại một.", thuong),
                                ("CẢNH BÁO: không cho bé dưới ba tuổi dùng.", dam),
                                ("Thành phẩm: nhựa Melamine cao cấp.", thuong),
                                ("Sản xuất tại Việt Nam, bao bì giấy đồ dùng.", thuong)]):
        d.text((100, 80 + i * 90), t, font=f, fill=(35, 35, 40))
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return cv2.GaussianBlur(a, (3, 3), 0.8)


def kiem_go_tieng_viet():
    from loi_xu_ly import sua_ky_tu as sk
    print("1e. Gõ tiếng Việt: chữ chèn cùng kiểu nét, đậm nhạt với chữ quanh; chữ có dấu thiếu thì ghép dấu")
    anh = trang_dam_nhat()
    cac_dong = sk.doc_dong(anh)
    d = next(d for d in cac_dong if "Melamine" in d.chu)
    p = sk.PhienSuaDong(anh, cac_dong, d)
    p.con_tro = next(i for i, m in enumerate(p.manh) if m.chu == ":") + 1
    # gõ kiểu tổ hợp (dấu rời) như bộ gõ đặt Unicode tổ hợp: phải ra đúng chữ dựng sẵn
    p.go(" bé dưới bộ")
    moi = [m for m in p.manh if m.loai != "goc" and m.chu.strip()]
    kiem("".join(m.chu for m in moi) == "bédướibộ", f"gõ dấu rời ghép đúng chữ: {''.join(m.chu for m in moi)}")
    kiem(all(m.loai == "chep" for m in moi), f"mọi chữ chép từ trang, không vẽ bằng phông: {[(m.chu, m.loai) for m in moi]}")
    tt = p.thao_tac()
    ra = tt.ap(anh)
    # bề dày nét chữ chèn so với chữ thường của dòng
    moi_dong = sk.doc_dong(ra)
    dm = next(e for e in moi_dong if "Melamine" in e.chu)
    x_sua = p.x0 + sum(m.rong for m in tt.manh[:p.con_tro - len(moi) - 2])
    x_het = p.x0 + sum(m.rong for m in tt.manh[:p.con_tro])
    chen = [c for c in dm.ky_tu if x_sua <= (c.hop[0] + c.hop[2]) / 2 <= x_het and c.chu.isalpha()]
    cu = [c for c in dm.ky_tu if (c.hop[0] + c.hop[2]) / 2 > x_het + 5 and c.chu.isalpha()]
    dam = [sk.dam_ky_tu(ra, dm, c) for c in chen]
    chuan = float(np.median([sk.dam_ky_tu(ra, dm, c) for c in cu]))
    dong_dam = next(e for e in cac_dong if "BÁO" in e.chu)
    net_dam = sk.dam_dong(anh, dong_dam)
    # đo một chữ lẻ dao động theo dáng chữ: so trung vị các chữ chèn, và không chữ nào đậm như dòng đậm
    tv = float(np.median(dam))
    kiem(len(dam) >= 6 and abs(tv / chuan - 1) <= 0.12 and max(dam) < 0.9 * net_dam,
         f"nét chữ chèn {[round(v, 1) for v in dam]} px (trung vị {tv:.1f}) so với chữ thường {chuan:.1f} px, dòng đậm {net_dam:.1f} px")
    vb = gon(dm.chu)
    # "ớ" chỉ có ở chữ dính nét chữ bên cạnh ("lớn", "tướng" nhòe dính nhau) nên móc có thể ngắn, máy đọc thành "ó"
    kiem("bé dư" in vb and "bộ nhựa" in vb, f"đọc lại: {vb}")
    doc_ghi.ghi_anh(np.vstack([anh, ra]), RA / "sua-ky-tu-go-tieng-viet.png")


def kiem_doi_co_phong():
    from loi_xu_ly import sua_ky_tu as sk
    print("1f. Đổi cỡ, đổi phông đoạn chữ bôi chọn (dòng nghiêng)")
    anh = trang_nghieng()
    xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
    cac_dong = sk.doc_dong(anh)
    d = next(d for d in cac_dong if "Melamine" in d.chu)
    p = sk.PhienSuaDong(anh, cac_dong, d)
    vt, k = d.chu.index("nhựa"), 0
    for i, m in enumerate(p.manh):
        if k == vt:
            a = i
        k += len(m.chu)
    p.dat_con_tro(p.x0 + sum(m.rong for m in p.manh[:a]))
    for _ in range(4):
        p.phai(chon=True)
    kiem("".join(m.chu for m in p.manh[slice(*p.doan_chon())]) == "nhựa", "Shift + → bôi chọn đúng từ “nhựa”")
    kc, tl, ve = p.kieu_doan_chon()
    kiem(not ve and tl == 1.0 and kc.co_px > 0, f"đoán định dạng đoạn chọn: {kc.mo_ta(anh.shape[1])}")
    xa0, xa1 = p.x_doan_chon()
    # chỗ chữ của dòng khác: mực trên trang gốc ngoài nét của dòng đang sửa
    net_dong = np.zeros(xam.shape, bool)
    y0, y1 = d.dai
    net_dong[y0:y1, p.x0:p.x1_cu] = cv2.dilate(p.net.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    muc_khac = (xam < 140) & ~net_dong

    def cao_muc(ra, x0, x1):
        cot = (cv2.cvtColor(ra, cv2.COLOR_BGR2GRAY)[:, x0:x1] < 140) & ~muc_khac[:, x0:x1]
        ys = np.nonzero(cot.any(axis=1))[0]
        ys = ys[(ys > y0 - 60) & (ys < y1 + 30)]
        return ys.max() - ys.min() if len(ys) else 0

    p.dinh_dang_chon(1.5)
    tt = p.thao_tac()
    ra = tt.ap(anh)
    xb0, xb1 = p.x_doan_chon()
    h0, h1 = cao_muc(anh, xa0, xa1), cao_muc(ra, xb0, xb1)
    kiem(all(m.loai == "chep" and m.co_doi == 1.5 for m in p.manh[slice(*p.doan_chon())]),
         "đổi cỡ giữ nét gốc: các ký tự chép chính nét của chúng, phóng 1,5 lần")
    kiem(1.3 <= h1 / max(h0, 1) <= 1.7 and 1.3 <= (xb1 - xb0) / (xa1 - xa0) <= 1.7,
         f"chữ cao {h0} → {h1} px, rộng {xa1 - xa0} → {xb1 - xb0} px")
    kiem(np.array_equal(ra[y0:y1, :xa0 - 2], anh[y0:y1, :xa0 - 2]), "phần dòng trước đoạn chọn giữ nguyên từng điểm ảnh")
    lech = int((np.abs(ra.astype(int) - anh.astype(int)).max(axis=2)[muc_khac] > 40).sum())
    kiem(lech <= 30, f"chữ dòng khác không bị đụng ({lech} điểm mực đổi)")
    p.dinh_dang_chon(1.0)
    kiem(not p.da_doi, "trả cỡ về 1 thì dòng như chưa sửa")
    k_arial = snd.KieuChu("Arial", "dam", kc.co_px, kc.mau, kc.mo)
    p.dinh_dang_chon(kieu=k_arial)
    kiem(all(m.loai == "ve" and m.kieu_ve is k_arial for m in p.manh[slice(*p.doan_chon())]), "đổi phông: đoạn chọn vẽ bằng Arial đậm")
    p.phai()
    p.go("X")
    kiem(p.manh[p.con_tro - 1].kieu_ve is k_arial, "chữ gõ ngay sau đoạn đổi phông theo phông đó")
    ra = p.thao_tac().ap(anh)
    dm = [e for e in sk.doc_dong(ra) if "Melamine" in e.chu]
    vb = gon(dm[0].chu) if dm else ""
    kiem("nhựaX Melamine" in vb, f"đọc lại: {vb}")
    kiem(np.array_equal(ra[y0:y1, :xa0 - 2], anh[y0:y1, :xa0 - 2]), "đổi phông: phần trước đoạn chọn vẫn giữ nguyên")
    doc_ghi.ghi_anh(np.vstack([anh[y0 - 60:y1 + 60], ra[y0 - 60:y1 + 60]]), RA / "sua-ky-tu-doi-co-phong.png")


def kiem_bao_ve(anh):
    print("2. Không cho sửa đè con dấu, chữ ký")
    # con dấu đỏ ở nửa dưới trang (tìm vùng nhiều điểm đỏ nhất)
    hsv = cv2.cvtColor(anh, cv2.COLOR_BGR2HSV)
    do = ((hsv[..., 1] > 90) & ((hsv[..., 0] < 10) | (hsv[..., 0] > 165))).astype(np.uint8)
    ys, xs = np.nonzero(do)
    tam = (int(np.median(xs)), int(np.median(ys)))
    hop_dau = (tam[0] - 60, tam[1] - 30, tam[0] + 60, tam[1] + 30)
    kiem(snd.co_muc_mau(anh, hop_dau), "vùng con dấu bị nhận ra là có mực màu")
    cac_tu = snd.tim_tu(anh)
    chon = tim(cac_tu, "Thư viện Trường")
    kiem(not snd.co_muc_mau(anh, chon[0].hop), "chữ đen thân bài không bị chặn")


def kiem_them(anh):
    print("3. Thêm chữ, che, tô sáng, chèn ảnh")
    H, W = anh.shape[:2]
    them = snd.ThemChu((150, H - 120), "Đã nhận bản chính ngày 30/10/2026", co_px=40, mau=(160, 40, 0))
    ra = them.ap(anh)
    vb = gon(nhan_dang.van_ban(ra[H - 190:H - 90], "vie"))
    kiem("Đã nhận bản chính ngày 30/10/2026" in vb, f"chữ thêm đọc lại được: {vb}")
    che = snd.Che((100, 100, 400, 160), (0, 0, 0))
    kiem(int(che.ap(anh)[100:160, 100:400].max()) == 0, "che đen phủ kín vùng")
    to = snd.ToSang((100, 300, 600, 360)).ap(anh)
    kiem(to[330, 120, 0] < anh[330, 120, 0] - 100 and to[330, 120, 2] >= anh[330, 120, 2] - 5, "tô sáng nhuộm vàng nền")
    # chữ ký: ảnh nét xanh trên nền trắng
    ky = np.full((120, 300, 3), 255, np.uint8)
    cv2.putText(ky, "Ky ten", (10, 85), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.2, (160, 60, 20), 4)
    ok, buf = cv2.imencode(".png", ky)
    hop = (800, 1600, 1100, 1720)
    chen = snd.ChenAnh(hop, buf.tobytes(), bo_nen_trang=True).ap(anh)
    vung, vung0 = chen[1600:1720, 800:1100].astype(int), anh[1600:1720, 800:1100].astype(int)
    nen_giu = (np.abs(vung - vung0).max(axis=2) <= 3).mean()
    kiem(nen_giu > 0.6, f"bỏ nền trắng ảnh chèn: {nen_giu:.0%} điểm nền giữ nguyên")
    kiem(((vung[..., 0] > vung[..., 2] + 40)).sum() > 500, "nét chữ ký xanh in lên trang")
    tl = snd.ap_tat_ca(anh, [them, che])
    kiem(np.array_equal(tl, che.ap(them.ap(anh))), "áp lần lượt nhiều thao tác")
    doc_ghi.ghi_anh(snd.ap_tat_ca(anh, [them, snd.ToSang((100, 300, 600, 360)), snd.ChenAnh(hop, buf.tobytes())]),
                    RA / "sua-them-chu-to-sang-chen-anh.jpg")


def tao_pdf_nguon(duong_dan, so_trang=3):
    pdfmetrics.registerFont(TTFont("Times", "C:/Windows/Fonts/times.ttf"))
    c = canvas.Canvas(str(duong_dan))
    c.setTitle("Tệp nguồn kiểm thử")
    for i in range(so_trang):
        c.setFont("Times", 28)
        c.drawString(72, 760, f"Trang nguồn số {i + 1}")
        c.setFont("Times", 14)
        c.drawString(72, 720, "Công văn kiểm thử chức năng sửa PDF có sẵn.")
        c.showPage()
    c.save()


def chu_trang(pdf, i):
    return gon(pdf.pages[i].extract_text() or "")


def kiem_tai_lieu(anh):
    print("4. Sửa trang của PDF có sẵn")
    nguon, nguon2 = RA / "sua-nguon.pdf", RA / "sua-nguon-2.pdf"
    tao_pdf_nguon(nguon, 3)
    tao_pdf_nguon(nguon2, 2)
    goc = PdfReader(str(nguon))
    tl = TaiLieu()
    tl.mo_tep(nguon)
    kiem(len(tl.trang) == 3, "mở PDF 3 trang")
    tl.mo_tep(nguon2)  # gộp
    tl.xoay(1, 90)
    tl.xoa([2])
    tl.doi_cho(3, 0)  # đưa trang 2 của tệp thứ hai lên đầu
    tl.them_trang_trang(1)
    tl.them_anh(anh, "Ảnh công văn")
    # thứ tự mong đợi: [nguồn2-2, trắng, nguồn-1, nguồn-2 (xoay), nguồn2-1, ảnh]
    ra = RA / "sua-ket-qua.pdf"
    tl.luu(ra, ocr=False)
    kq = PdfReader(str(ra))
    kiem(len(kq.pages) == 6, f"số trang sau gộp, xóa, chèn: {len(kq.pages)}")
    kiem([chu_trang(kq, i)[:16] for i in (0, 2, 3, 4)] == ["Trang nguồn số 2", "Trang nguồn số 1", "Trang nguồn số 2", "Trang nguồn số 1"],
         "thứ tự trang đúng, chữ gốc vẫn chép được")
    kiem(chu_trang(kq, 1) == "", "trang trắng chèn đúng chỗ")
    kiem((kq.pages[3].rotation or 0) == 90, "trang xoay giữ /Rotate 90")
    kiem(kq.pages[2].get_contents().get_data() == goc.pages[0].get_contents().get_data(),
         "trang chưa sửa chép nguyên nội dung (không dựng lại ảnh)")
    kiem("/Subject" not in (kq.metadata or {}), "chưa sửa nội dung thì không ghi dấu đã chỉnh sửa")

    # sửa nội dung trang 3 (nguồn-1): dựng ảnh 300 dpi, thay chữ, lưu có lớp chữ
    nen = tl.anh_nen(2)
    kiem(abs(nen.shape[1] - 2480) <= 2, f"dựng trang PDF ở 300 dpi: {nen.shape[1]}×{nen.shape[0]}")
    cac_tu = snd.tim_tu(nen)
    tt = snd.chuan_bi_sua_chu(cac_tu, tim(cac_tu, "kiểm thử"), "thử nghiệm", nen.shape[1])
    tl.trang[2].thao_tac.append(tt)
    tl.trang[2].thao_tac.append(snd.Che((0, 0, 200, 200)))
    print(f"     đoán phông chữ vector: {tt.kieu_chu.mo_ta(nen.shape[1]) if tt.kieu_chu else '(chưa áp)'}")
    ra2 = RA / "sua-ket-qua-da-sua.pdf"
    tl.luu(ra2, ocr=True)
    kq2 = PdfReader(str(ra2))
    print(f"     đoán phông sau khi áp: {tt.kieu_chu.mo_ta(nen.shape[1])}")
    kiem(tt.kieu_chu.ten == "Times New Roman", "đoán ra Times New Roman cho chữ vector của PDF")
    vb = chu_trang(kq2, 2)
    kiem("thử nghiệm" in vb and "kiểm thử" not in vb, f"lớp chữ trang đã sửa có chữ mới: {vb[:70]}")
    kiem(abs(float(kq2.pages[2].mediabox.width) - 595.3) < 1, "trang đã sửa giữ khổ A4")
    kiem("sửa chữ" in (kq2.metadata or {}).get("/Subject", ""), f"siêu dữ liệu ghi đã chỉnh sửa: {(kq2.metadata or {}).get('/Subject')}")
    # xoay trang đã sửa: gộp thao tác vào ảnh, vẫn giữ dấu vết đã sửa
    tl.xoay(2, 180)
    kiem(not tl.trang[2].thao_tac and tl.trang[2].da_gop == ["SuaChu", "Che"], "xoay trang đã sửa: gộp thao tác vào ảnh")
    # tách: lưu riêng 2 trang
    ra3 = RA / "sua-tach.pdf"
    tl.luu(ra3, chi_so=[0, 4], ocr=False)
    kq3 = PdfReader(str(ra3))
    kiem(len(kq3.pages) == 2 and chu_trang(kq3, 1).startswith("Trang nguồn số 1"), "tách 2 trang ra tệp mới")


def kiem_doi_tuong(anh):
    print("5. Đối tượng chọn lại được, dời vùng có sẵn (tham khảo ONLYOFFICE)")
    chu = snd.ThemChu((100, 80), "Bản sao", "Times New Roman", "dam", 40.0, (0, 0, 200))
    k0 = dt.khung(chu)
    dt.doi(chu, 50, 30)
    kiem(dt.khung(chu) == (k0[0] + 50, k0[1] + 30, k0[2] + 50, k0[3] + 30), "dời chữ đã thêm")
    k1 = dt.khung(chu)
    dt.dat_khung(chu, (k1[0], k1[1], k1[2] + (k1[2] - k1[0]), k1[3] + (k1[3] - k1[1])))
    kiem(abs(chu.co_px - 80) < 3, f"kéo góc gấp đôi khung: cỡ chữ 40 → {chu.co_px:.1f} px")
    hinh = dt.HinhVe("mui_ten", (500, 100, 300, 200), (0, 0, 200), 4)
    dt.doi(hinh, 10, 10)
    kiem(hinh.diem == (510, 110, 310, 210), "dời mũi tên, giữ chiều")
    vung = dt.tim_vung(anh)
    kiem(len(vung) >= 8, f"tự đánh dấu vùng trên bản scan: {len(vung)} vùng, {sum(k for _, k in vung)} vùng khóa")
    dau = [h for h, k in vung if k]
    kiem(bool(dau) and all(snd.co_muc_mau(anh, h) for h in dau), "vùng có con dấu bị khóa")
    h = next(h for h, k in vung if not k and h[1] > anh.shape[0] * 0.3)
    ra = dt.DoiVung(h, (h[0] + 40, h[1], h[2] + 40, h[3])).ap(anh)
    khac = np.any(ra != anh, axis=2)
    khac[h[1] - 6:h[3] + 7, h[0] - 6:h[2] + 47] = False
    kiem(int(khac.sum()) == 0, "dời một vùng: ngoài vùng cũ và mới không đổi điểm ảnh nào")
    xoa = dt.DoiVung(h, None).ap(anh)
    kiem(int((255 - cv2.cvtColor(xoa[h[1]:h[3], h[0]:h[2]], cv2.COLOR_BGR2GRAY)).max()) < 80, "xóa vùng: chỗ cũ vá nền")


def kiem_chu_thich():
    print("6. Chú thích không phá bản gốc (chú thích PDF chuẩn)")
    import pypdfium2 as pdfium
    from pypdf import PdfWriter
    nguon = RA / "ct-nguon.pdf"
    tao_pdf_nguon(nguon, 2)
    v = PdfWriter(clone_from=str(nguon))
    v.pages[1].rotate(90)
    v.write(str(nguon))
    tl = TaiLieu()
    tl.mo_tep(nguon)
    tl.them_trang_trang()
    for i in range(3):
        w = tl.anh_nen(i).shape[1]
        k = w / 1000
        ds = tl.trang[i].thao_tac
        ds += [ct.GhiChu((int(80 * k), int(60 * k), int(120 * k), int(100 * k)), noi_dung="Kiểm tra lại số liệu"),
               ct.ButPhe((int(400 * k), int(80 * k), int(900 * k), int(200 * k)), noi_dung="Đồng ý, chuyển phòng Tổng hợp", co_px=30 * k),
               ct.ToSangCT((int(100 * k), int(300 * k), int(700 * k), int(340 * k))),
               ct.HinhCT((0, 0, 0, 0), loai="mui_ten", diem=(int(800 * k), int(400 * k), int(600 * k), int(560 * k)), day=int(4 * k)),
               ct.DauCT((int(120 * k), int(620 * k), int(470 * k), int(760 * k)))]
    kiem(not any(t.da_sua for t in tl.trang), "chú thích không tính là sửa nội dung trang")
    xem = [tl.anh_trang(i) for i in range(3)]
    goc = [tl.anh_trang(i, chu_thich=False) for i in range(3)]
    ra = RA / "ct-ra.pdf"
    tl.luu(ra, ocr=False)
    kq, g = PdfReader(str(ra)), PdfReader(str(nguon))
    kiem([a.get_object()["/Subtype"] for a in kq.pages[0]["/Annots"]] == ["/Text", "/FreeText", "/Highlight", "/Line", "/Stamp"],
         "ghi đủ 5 loại chú thích PDF chuẩn")
    kiem(all(kq.pages[i].get_contents().get_data() == g.pages[i].get_contents().get_data() for i in range(2)),
         "nội dung trang chép nguyên, không dựng lại ảnh")
    kiem("/Subject" not in (kq.metadata or {}), "không ghi dấu đã chỉnh sửa nội dung")
    doc = pdfium.PdfDocument(str(ra))
    for i in range(3):
        pg = doc[i]
        h, w = goc[i].shape[:2]
        sc = w / pg.get_width()
        co = pg.render(scale=sc, draw_annots=True).to_numpy()[:h, :w, :3]
        khong = pg.render(scale=sc, draw_annots=False).to_numpy()[:h, :w, :3]
        hh, ww = co.shape[:2]
        m_xem = np.abs(xem[i][:hh, :ww].astype(int) - goc[i][:hh, :ww].astype(int)).max(axis=2) > 40
        m_luu = np.abs(co.astype(int) - khong.astype(int)).max(axis=2) > 40
        d_xem = cv2.dilate(m_xem.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        trung = (m_luu & d_xem).sum() / max(1, m_luu.sum())
        kiem(trung > 0.9, f"trang {i + 1} (/Rotate {pg.get_rotation()}): chú thích lưu ra trùng chỗ xem trước ({trung:.0%})")
    doc.close()
    truoc = [c.hop for c in tl.trang[0].chu_thich]
    tl.xoay(0, 90)
    tl.xoay(0, 270)
    kiem([c.hop for c in tl.trang[0].chu_thich] == truoc, "xoay trang đi rồi về: chú thích về đúng chỗ")


def kiem_thao_tac_trang():
    print("7. Thao tác trang kiểu ONLYOFFICE")
    nguon = RA / "tt-nguon.pdf"
    tao_pdf_nguon(nguon, 5)
    tl = TaiLieu()
    tl.mo_tep(nguon)
    so = lambda: [t.so + 1 for t in tl.trang]  # noqa: E731
    moi = tl.di_chuyen([3, 4], 1)
    kiem(so() == [1, 4, 5, 2, 3] and moi == [1, 2], f"kéo trang 4, 5 lên trước trang 2: {so()}")
    moi = tl.di_chuyen([0], 5)
    kiem(so() == [4, 5, 2, 3, 1] and moi == [4], f"kéo trang đầu xuống cuối: {so()}")
    ban = tl.chep([0, 1])
    tl2 = TaiLieu()
    tl2.mo_tep(nguon)
    tl2.dan(ban, 1)
    tl2.dan(ban, 0)
    kiem([t.so + 1 for t in tl2.trang] == [4, 5, 1, 4, 5, 2, 3, 4, 5], "chép 2 trang, dán hai lần sang tài liệu khác")
    kiem(tl2.trang[0] is not tl2.trang[3], "mỗi lần dán là trang riêng")
    ra = RA / "tt-ra.pdf"
    tl2.luu(ra, ocr=False)
    kq, g = PdfReader(str(ra)), PdfReader(str(nguon))
    kiem(len(kq.pages) == 9 and kq.pages[0].get_contents().get_data() == g.pages[3].get_contents().get_data(),
         "trang dán chép nguyên chất lượng")


if __name__ == "__main__":
    if not nhan_dang.CO_TESSERACT:
        raise SystemExit("Cần Tesseract OCR có gói vie")
    anh = trang_mau()
    kiem_sua_chu(anh)
    kiem_sua_khoi(anh)
    kiem_sua_ky_tu(anh)
    kiem_dong_nghieng()
    kiem_go_tieng_viet()
    kiem_doi_co_phong()
    kiem_bao_ve(anh)
    kiem_them(anh)
    kiem_tai_lieu(anh)
    kiem_doi_tuong(anh)
    kiem_chu_thich()
    kiem_thao_tac_trang()
    print("\nTẤT CẢ ĐẠT" if not loi else f"\n{len(loi)} mục SAI:\n- " + "\n- ".join(loi))
    sys.exit(1 if loi else 0)
