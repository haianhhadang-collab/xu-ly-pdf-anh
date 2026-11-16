"""Ứng dụng xử lý PDF ảnh – giao diện máy tính (Windows).

Mở ảnh/PDF (nút Mở, kéo thả, hoặc truyền đường dẫn khi chạy), chụp từ webcam,
tự nắn phẳng và làm sạch từng trang, chỉnh khung cắt bằng chuột, sắp xếp trang,
xuất một PDF gộp có lớp chữ tìm kiếm được; theo dõi thư mục để tự xử lý tệp mới.

Chạy:  python giao_dien.py [tệp ...]
"""
from __future__ import annotations

import os
import queue
import sys
import threading
from dataclasses import dataclass, field, replace
from pathlib import Path

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loi_xu_ly import __version__, chat_luong, doc_ghi, lam_sach, nan_phang, nhan_dang, tim_mep  # noqa: E402
from loi_xu_ly.tu_chup import BoTuChup  # noqa: E402
from loi_xu_ly.quy_trinh import TuyChon, TuyChonXuat, kiem_tra_anh_chup, xu_ly_anh  # noqa: E402

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None

TEN_UNG_DUNG = "Xử lý PDF ảnh"
CAO_DONG = 84
CO_ANH_NHO = 72

TEN_LE = {"sat": "Sát chữ", "vua": "Vừa", "trang": "Giữ cả trang"}


@dataclass
class Trang:
    ten: str
    goc: bytes                      # ảnh gốc đã mã hóa
    xoay_tay: int = 0               # độ, theo chiều kim đồng hồ, áp lên ảnh gốc
    khung_tay: np.ndarray | None = None
    khung_tu_dong: np.ndarray | None = None
    tat_tu_xoay: bool = False       # người dùng đã tự xoay thì không đoán hướng nữa
    ket_qua: list[bytes] = field(default_factory=list)
    trang_thai: str = "Chờ xử lý"
    phien_ban: int = 0
    thong_tin: dict | None = None
    dac_trung: list | None = None   # đặc trưng ORB từng trang kết quả, để dò trang chụp trùng
    trung_voi: str | None = None    # mã trang đứng trước mà trang này giống hệt (chụp trùng)


def anh_sang_tk(anh: np.ndarray, rong: int, cao: int) -> tuple[ImageTk.PhotoImage, float]:
    h, w = anh.shape[:2]
    s = min(rong / w, cao / h)
    nho = cv2.resize(anh, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_AREA)
    return ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(nho, cv2.COLOR_BGR2RGB))), s


class UngDung:
    def __init__(self, goc: tk.Tk):
        self.goc = goc
        goc.title(TEN_UNG_DUNG)
        goc.geometry("1280x820")
        goc.minsize(980, 640)
        try:
            goc.state("zoomed")
        except tk.TclError:
            pass

        self.trang: dict[str, Trang] = {}
        self.thu_tu: list[str] = []
        self.dem = 0
        self.anh_nho: dict[str, ImageTk.PhotoImage] = {}
        self.dang_chon: str | None = None
        self.hang_xu_ly: queue.Queue = queue.Queue()
        self.hang_giao_dien: queue.Queue = queue.Queue()
        self.theo_doi = None
        self._xem = None  # (PhotoImage, tỉ lệ, dx, dy)
        self._keo = None

        self._tao_bien()
        self._dung_giao_dien()
        for _ in range(min(4, max(1, (os.cpu_count() or 2) // 4))):
            threading.Thread(target=self._vong_xu_ly, daemon=True).start()
        goc.after(100, self._nhan_tin)
        goc.protocol("WM_DELETE_WINDOW", self._dong)

    # ------------------------------------------------------------------ dựng giao diện
    def _tao_bien(self):
        self.v_tim_mep = tk.BooleanVar(value=True)
        self.v_tu_xoay = tk.BooleanVar(value=nhan_dang.CO_TESSERACT)
        self.v_sua_nghieng = tk.BooleanVar(value=True)
        self.v_nan_cong = tk.BooleanVar(value=True)
        self.v_cat_sat = tk.BooleanVar(value=True)
        self.v_le = tk.StringVar(value="Vừa")
        self.v_tach_doi = tk.BooleanVar(value=False)
        self.v_che_do = tk.StringVar(value=lam_sach.CHE_DO["giu_mau"])
        self.v_do_trang = tk.DoubleVar(value=0.5)
        self.v_do_dam = tk.DoubleVar(value=0.5)
        self.v_kho = tk.StringVar(value=doc_ghi.TEN_KHO["a4"])
        self.v_le = tk.DoubleVar(value=0.0)
        self.v_chat_luong = tk.StringVar(value=doc_ghi.TEN_CHAT_LUONG["vua"])
        self.v_ocr = tk.BooleanVar(value=nhan_dang.CO_TESSERACT)
        self.v_txt = tk.BooleanVar(value=False)
        self.v_xem = tk.StringVar(value="ket_qua")
        self.v_trang_thai = tk.StringVar(value="Mở ảnh hoặc PDF, kéo thả tệp vào cửa sổ, hoặc chụp từ camera.")

    def _dung_giao_dien(self):
        kieu = ttk.Style(self.goc)
        if "vista" in kieu.theme_names():
            kieu.theme_use("vista")
        kieu.configure("Treeview", rowheight=CAO_DONG)
        kieu.configure("Nhan.TButton", font=("Segoe UI", 10, "bold"))

        thanh = ttk.Frame(self.goc, padding=(8, 6))
        thanh.pack(fill="x")
        for chu, lenh in (("📂 Mở ảnh, PDF…", self.chon_tep), ("📷 Chụp camera", self.mo_camera),
                          ("🔁 Xử lý lại tất cả", self.xu_ly_lai_tat_ca)):
            ttk.Button(thanh, text=chu, command=lenh).pack(side="left", padx=(0, 6))
        ttk.Button(thanh, text="💾 Xuất PDF…", style="Nhan.TButton", command=self.xuat_pdf).pack(side="left", padx=(0, 6))
        ttk.Button(thanh, text="✏ Sửa PDF…", command=self.mo_sua_pdf).pack(side="left", padx=(0, 6))
        ttk.Button(thanh, text="👁 Thư mục theo dõi…", command=self.mo_theo_doi).pack(side="left", padx=(0, 6))
        ttk.Button(thanh, text="?", width=3, command=self.gioi_thieu).pack(side="right")

        than = ttk.PanedWindow(self.goc, orient="horizontal")
        than.pack(fill="both", expand=True, padx=8)

        # Cột trái: danh sách trang
        trai = ttk.Frame(than)
        self.ds = ttk.Treeview(trai, columns=("tt",), show="tree headings", selectmode="extended")
        self.ds.heading("#0", text="Trang")
        self.ds.heading("tt", text="Trạng thái")
        self.ds.column("#0", width=200)
        self.ds.column("tt", width=110)
        cuon = ttk.Scrollbar(trai, orient="vertical", command=self.ds.yview)
        self.ds.configure(yscrollcommand=cuon.set)
        nut = ttk.Frame(trai)
        nut.pack(side="bottom", fill="x", pady=4)
        for chu, lenh, goi_y in (("▲", lambda: self.doi_cho(-1), "Đưa lên"), ("▼", lambda: self.doi_cho(1), "Đưa xuống"),
                                 ("⟲", lambda: self.xoay(-90), "Xoay trái"), ("⟳", lambda: self.xoay(90), "Xoay phải"),
                                 ("✕", self.xoa_trang, "Xóa trang")):
            b = ttk.Button(nut, text=chu, width=4, command=lenh)
            b.pack(side="left", padx=2)
            GoiY(b, goi_y)
        cuon.pack(side="right", fill="y")
        self.ds.pack(fill="both", expand=True)
        self.ds.bind("<<TreeviewSelect>>", self._khi_chon)
        self.ds.bind("<Delete>", lambda e: self.xoa_trang())
        than.add(trai, weight=1)

        # Giữa: xem trước
        giua = ttk.Frame(than)
        chon_xem = ttk.Frame(giua)
        chon_xem.pack(fill="x", pady=(0, 4))
        ttk.Radiobutton(chon_xem, text="Kết quả", value="ket_qua", variable=self.v_xem,
                        command=self._ve_xem_truoc).pack(side="left")
        ttk.Radiobutton(chon_xem, text="Ảnh gốc và khung cắt", value="goc", variable=self.v_xem,
                        command=self._ve_xem_truoc).pack(side="left", padx=8)
        self.nut_khung = ttk.Frame(chon_xem)
        self.nut_khung.pack(side="right")
        ttk.Button(self.nut_khung, text="Tự tìm lại khung", command=self.dat_lai_khung).pack(side="left", padx=2)
        ttk.Button(self.nut_khung, text="Giữ nguyên ảnh (không cắt)", command=self.khong_cat).pack(side="left", padx=2)
        self.xem = tk.Canvas(giua, background="#3b3f45", highlightthickness=0)
        self.xem.pack(fill="both", expand=True)
        self.xem.bind("<Configure>", lambda e: self._ve_xem_truoc())
        self.xem.bind("<ButtonPress-1>", self._bat_dau_keo)
        self.xem.bind("<B1-Motion>", self._keo_goc)
        self.xem.bind("<ButtonRelease-1>", self._tha_goc)
        than.add(giua, weight=4)

        # Cột phải: tùy chọn
        phai = ttk.Frame(than, padding=(8, 0, 0, 0))
        self._khung_tuy_chon(phai)
        than.add(phai, weight=1)

        day = ttk.Frame(self.goc, padding=(8, 4))
        day.pack(fill="x")
        self.tien_trinh = ttk.Progressbar(day, length=200, mode="determinate")
        self.tien_trinh.pack(side="right")
        ttk.Label(day, textvariable=self.v_trang_thai).pack(side="left")

        if TkinterDnD is not None:
            self.goc.drop_target_register(DND_FILES)
            self.goc.dnd_bind("<<Drop>>", lambda e: self.mo_tep(self.goc.tk.splitlist(e.data)))

    def _khung_tuy_chon(self, cha):
        n1 = ttk.LabelFrame(cha, text="Nắn phẳng", padding=8)
        n1.pack(fill="x", pady=(0, 8))
        ttk.Checkbutton(n1, text="Tự tìm mép giấy, sửa phối cảnh", variable=self.v_tim_mep).pack(anchor="w")
        cb = ttk.Checkbutton(n1, text="Tự xoay đúng chiều chữ", variable=self.v_tu_xoay)
        cb.pack(anchor="w")
        if not nhan_dang.CO_TESSERACT:
            cb.state(["disabled"])
        ttk.Checkbutton(n1, text="Sửa nghiêng", variable=self.v_sua_nghieng).pack(anchor="w")
        ttk.Checkbutton(n1, text="Nắn trang cong (theo dòng chữ)", variable=self.v_nan_cong).pack(anchor="w")
        ttk.Checkbutton(n1, text="Cắt theo chữ, xóa vết ngoài vùng chữ", variable=self.v_cat_sat).pack(anchor="w")
        dong_le = ttk.Frame(n1)
        dong_le.pack(anchor="w", padx=(20, 0))
        ttk.Label(dong_le, text="Lề trang:").pack(side="left")
        ttk.Combobox(dong_le, textvariable=self.v_le, values=list(TEN_LE.values()), state="readonly", width=12).pack(side="left", padx=4)
        ttk.Checkbutton(n1, text="Tách trang đôi (sách mở)", variable=self.v_tach_doi).pack(anchor="w")

        n2 = ttk.LabelFrame(cha, text="Làm sạch", padding=8)
        n2.pack(fill="x", pady=(0, 8))
        ttk.Combobox(n2, textvariable=self.v_che_do, values=list(lam_sach.CHE_DO.values()),
                     state="readonly").pack(fill="x")
        ttk.Label(n2, text="Độ trắng nền").pack(anchor="w", pady=(6, 0))
        ttk.Scale(n2, from_=0, to=1, variable=self.v_do_trang).pack(fill="x")
        ttk.Label(n2, text="Độ đậm chữ").pack(anchor="w", pady=(6, 0))
        ttk.Scale(n2, from_=0, to=1, variable=self.v_do_dam).pack(fill="x")
        hang = ttk.Frame(n2)
        hang.pack(fill="x", pady=(8, 0))
        ttk.Button(hang, text="Áp dụng trang chọn", command=self.xu_ly_lai_trang_chon).pack(side="left", expand=True, fill="x")
        ttk.Button(hang, text="Tất cả", command=self.xu_ly_lai_tat_ca).pack(side="left", padx=(4, 0))

        n3 = ttk.LabelFrame(cha, text="Xuất PDF", padding=8)
        n3.pack(fill="x", pady=(0, 8))
        ttk.Label(n3, text="Khổ giấy").pack(anchor="w")
        ttk.Combobox(n3, textvariable=self.v_kho, values=list(doc_ghi.TEN_KHO.values()), state="readonly").pack(fill="x")
        ttk.Label(n3, text="Lề (mm)").pack(anchor="w", pady=(6, 0))
        ttk.Spinbox(n3, from_=0, to=40, increment=1, textvariable=self.v_le, width=6).pack(anchor="w")
        ttk.Label(n3, text="Chất lượng ảnh").pack(anchor="w", pady=(6, 0))
        ttk.Combobox(n3, textvariable=self.v_chat_luong, values=list(doc_ghi.TEN_CHAT_LUONG.values()),
                     state="readonly").pack(fill="x")
        c1 = ttk.Checkbutton(n3, text="Thêm lớp chữ (tìm kiếm, chép chữ)", variable=self.v_ocr)
        c1.pack(anchor="w", pady=(6, 0))
        c2 = ttk.Checkbutton(n3, text="Xuất kèm văn bản .txt", variable=self.v_txt)
        c2.pack(anchor="w")
        if not nhan_dang.CO_TESSERACT:
            c1.state(["disabled"])
            c2.state(["disabled"])
            ttk.Label(n3, text="Chưa cài Tesseract OCR", foreground="#b00").pack(anchor="w")

        self.nhan_thong_tin = ttk.Label(cha, text="", wraplength=230, justify="left", foreground="#555")
        self.nhan_thong_tin.pack(fill="x", pady=(4, 0))

    # ------------------------------------------------------------------ tùy chọn
    def tuy_chon(self) -> TuyChon:
        nguoc = {v: k for k, v in lam_sach.CHE_DO.items()}
        return TuyChon(tim_mep=self.v_tim_mep.get(), tu_xoay=self.v_tu_xoay.get(),
                       sua_nghieng=self.v_sua_nghieng.get(), nan_cong=self.v_nan_cong.get(), cat_sat_chu=self.v_cat_sat.get(),
                       tach_trang_doi=self.v_tach_doi.get(),
                       le={v: k for k, v in TEN_LE.items()}.get(self.v_le.get(), "vua"),
                       che_do=nguoc.get(self.v_che_do.get(), "giu_mau"),
                       do_trang=float(self.v_do_trang.get()), do_dam=float(self.v_do_dam.get()))

    def tuy_chon_xuat(self) -> TuyChonXuat:
        kho = {v: k for k, v in doc_ghi.TEN_KHO.items()}.get(self.v_kho.get(), "a4")
        cl = {v: k for k, v in doc_ghi.TEN_CHAT_LUONG.items()}.get(self.v_chat_luong.get(), "vua")
        try:
            le = max(0.0, float(self.v_le.get()))
        except (tk.TclError, ValueError):
            le = 0.0
        return TuyChonXuat(kho=kho, le_mm=le, chat_luong=cl, ocr=self.v_ocr.get(), xuat_txt=self.v_txt.get())

    # ------------------------------------------------------------------ mở tệp, camera
    def chon_tep(self):
        tep = filedialog.askopenfilenames(title="Chọn ảnh hoặc PDF", filetypes=[
            ("Ảnh và PDF", " ".join(f"*{d}" for d in sorted(doc_ghi.DUOI_HO_TRO))), ("Tất cả", "*.*")])
        if tep:
            self.mo_tep(tep)

    def mo_tep(self, tep):
        tep = [t for t in tep if Path(t).suffix.lower() in doc_ghi.DUOI_HO_TRO or Path(t).is_dir()]
        if not tep:
            return
        self.v_trang_thai.set("Đang đọc tệp…")

        def doc():
            for t in tep:
                cac = [Path(t)] if not Path(t).is_dir() else sorted(
                    f for f in Path(t).iterdir() if f.suffix.lower() in doc_ghi.DUOI_HO_TRO)
                for f in cac:
                    try:
                        for ten, anh in doc_ghi.doc_tep(f):
                            self.hang_giao_dien.put(("them", ten, doc_ghi.ma_hoa(anh)))
                    except Exception as e:
                        self.hang_giao_dien.put(("bao", f"Không đọc được {f.name}: {e}"))
            self.hang_giao_dien.put(("bao", "Đã đọc xong tệp."))
        threading.Thread(target=doc, daemon=True).start()

    def them_trang(self, ten: str, du_lieu: bytes) -> str:
        self.dem += 1
        tid = f"t{self.dem}"
        self.trang[tid] = Trang(ten=ten, goc=du_lieu)
        self.thu_tu.append(tid)
        self.ds.insert("", "end", iid=tid, text="", values=("",))
        self._cap_nhat_dong(tid)
        self.yeu_cau_xu_ly(tid)
        if self.dang_chon is None:
            self.ds.selection_set(tid)
        return tid

    def thay_anh(self, tid: str, du_lieu: bytes):
        """Chụp lại một trang: ảnh mới thay ảnh gốc, trang giữ chỗ."""
        tr = self.trang.get(tid)
        if tr is None:
            return
        tr.goc, tr.xoay_tay, tr.khung_tay, tr.khung_tu_dong, tr.tat_tu_xoay = du_lieu, 0, None, None, False
        tr.ket_qua, tr.thong_tin, tr.dac_trung, tr.trung_voi = [], None, None, None
        self._cap_nhat_dong(tid, doi_anh=True)
        self.yeu_cau_xu_ly(tid)

    def mo_camera(self):
        CuaSoCamera(self.goc, lambda anh: self.them_trang(f"Ảnh chụp {self.dem + 1}", doc_ghi.ma_hoa(anh)),
                    khi_thay=lambda tid, anh: self.thay_anh(tid, doc_ghi.ma_hoa(anh)),
                    tach=lambda: self.tuy_chon().tach_trang_doi)

    # ------------------------------------------------------------------ xử lý nền
    def anh_goc(self, tr: Trang) -> np.ndarray:
        return nan_phang.xoay_90(doc_ghi.giai_ma(tr.goc), tr.xoay_tay)

    def yeu_cau_xu_ly(self, tid: str, tc: TuyChon | None = None):
        tr = self.trang[tid]
        tr.phien_ban += 1
        tr.trang_thai = "Đang chờ…"
        self._cap_nhat_dong(tid)
        self.hang_xu_ly.put((tid, tr.phien_ban, tc or self.tuy_chon()))

    def _vong_xu_ly(self):
        while True:
            tid, pb, tc = self.hang_xu_ly.get()
            tr = self.trang.get(tid)
            if tr is None or tr.phien_ban != pb:
                continue
            self.hang_giao_dien.put(("dang", tid, pb))
            try:
                anh = self.anh_goc(tr)
                kq, tt = xu_ly_anh(anh, tc, khung_tay=tr.khung_tay, tu_xoay=False if tr.tat_tu_xoay else None)
                dt = [chat_luong.dac_trung(k) for k in kq]
                self.hang_giao_dien.put(("xong", tid, pb, [doc_ghi.ma_hoa(k) for k in kq], tt, dt,
                                         self._tim_trung(tid, dt)))
            except Exception as e:
                self.hang_giao_dien.put(("loi", tid, pb, str(e)))

    def _tim_trung(self, tid: str, dt: list) -> list[str]:
        """Các trang trong khoảng 3 trang hai bên giống hệt trang vừa xử lý (chụp trùng). Chạy ở luồng xử lý."""
        thu_tu = list(self.thu_tu)
        if tid not in thu_tu:
            return []
        i = thu_tu.index(tid)
        kq = []
        for j in range(max(0, i - 3), min(len(thu_tu), i + 4)):
            khac = self.trang.get(thu_tu[j])
            if j == i or khac is None or not khac.dac_trung:
                continue
            if any(chat_luong.diem_khop(a, b) >= chat_luong.NGUONG_TRUNG for a in dt for b in khac.dac_trung):
                kq.append(thu_tu[j])
        return kq

    def _nhan_tin(self):
        try:
            while True:
                tin = self.hang_giao_dien.get_nowait()
                loai = tin[0]
                if loai == "them":
                    self.them_trang(tin[1], tin[2])
                elif loai == "bao":
                    self.v_trang_thai.set(tin[1])
                elif loai == "tien_trinh":
                    self.tien_trinh.configure(maximum=tin[2], value=tin[1])
                    self.v_trang_thai.set(tin[3])
                elif loai == "xuat_xong":
                    self.tien_trinh.configure(value=0)
                    self.v_trang_thai.set(tin[1])
                    if messagebox.askyesno(TEN_UNG_DUNG, f"{tin[1]}\n\nMở tệp PDF ngay?"):
                        os.startfile(tin[2])
                elif loai in ("dang", "xong", "loi"):
                    tid, pb = tin[1], tin[2]
                    tr = self.trang.get(tid)
                    if tr is None or tr.phien_ban != pb:
                        continue
                    if loai == "dang":
                        tr.trang_thai = "Đang xử lý…"
                    elif loai == "xong":
                        tr.ket_qua, tt = tin[3], tin[4]
                        if tr.khung_tay is None:
                            tr.khung_tu_dong = tt["khung"]
                        tr.trang_thai = "Xong" + (f" ({len(tr.ket_qua)} trang)" if len(tr.ket_qua) > 1 else "")
                        tr.thong_tin = tt
                        tr.dac_trung = tin[5]
                        # trang đứng sau trong cặp trùng được đánh dấu
                        tr.trung_voi = None
                        for khac in tin[6]:
                            if khac not in self.thu_tu:
                                continue
                            if self.thu_tu.index(khac) < self.thu_tu.index(tid):
                                tr.trung_voi = khac
                            else:
                                self.trang[khac].trung_voi = tid
                                self._cap_nhat_dong(khac)
                        self._cap_nhat_dong(tid, doi_anh=True)
                    else:
                        tr.trang_thai = "Lỗi"
                        self.v_trang_thai.set(f"Lỗi xử lý {tr.ten}: {tin[3]}")
                    self._cap_nhat_dong(tid)
                    if tid == self.dang_chon:
                        self._ve_xem_truoc()
                self._cap_nhat_dem()
        except queue.Empty:
            pass
        self.goc.after(100, self._nhan_tin)

    def _cap_nhat_dem(self):
        con = sum(1 for t in self.trang.values() if t.trang_thai.startswith("Đang"))
        if con:
            self.v_trang_thai.set(f"Đang xử lý {con} trang…")
            self._dang_ban = True
        elif getattr(self, "_dang_ban", False):
            self._dang_ban = False
            self.v_trang_thai.set(f"Đã xử lý xong {len(self.trang)} trang. Bấm 'Xuất PDF…' để lưu.")

    def _cap_nhat_dong(self, tid: str, doi_anh: bool = False):
        tr = self.trang[tid]
        if doi_anh or tid not in self.anh_nho:
            anh = doc_ghi.giai_ma(tr.ket_qua[0]) if tr.ket_qua else self.anh_goc(tr)
            self.anh_nho[tid] = anh_sang_tk(anh, CO_ANH_NHO, CO_ANH_NHO)[0]
        so = self.thu_tu.index(tid) + 1
        trang_thai = tr.trang_thai
        if self._trung(tr):
            trang_thai += " · trùng?"
        elif tr.thong_tin and any(tr.thong_tin.get("canh_bao", [])):
            trang_thai += " · chụp lại?"
        self.ds.item(tid, text=f"  {so}. {tr.ten}", image=self.anh_nho[tid], values=(trang_thai,))

    def _trung(self, tr: Trang) -> str | None:
        """Mã trang mà trang này giống hệt, nếu trang đó còn trong danh sách."""
        return tr.trung_voi if tr.trung_voi in self.trang else None

    def _danh_so_lai(self):
        for tid in self.thu_tu:
            tr = self.trang[tid]
            self.ds.item(tid, text=f"  {self.thu_tu.index(tid) + 1}. {tr.ten}")

    # ------------------------------------------------------------------ thao tác trang
    def _chon(self) -> list[str]:
        return [t for t in self.thu_tu if t in self.ds.selection()]

    def _khi_chon(self, _e=None):
        chon = self._chon()
        self.dang_chon = chon[0] if chon else None
        self._ve_xem_truoc()

    def doi_cho(self, buoc: int):
        chon = self._chon()
        if not chon:
            return
        thu_tu = self.thu_tu
        cac_vi_tri = [thu_tu.index(t) for t in chon]
        if (buoc < 0 and min(cac_vi_tri) == 0) or (buoc > 0 and max(cac_vi_tri) == len(thu_tu) - 1):
            return
        for i in sorted(cac_vi_tri, reverse=buoc > 0):
            thu_tu[i], thu_tu[i + buoc] = thu_tu[i + buoc], thu_tu[i]
        for i, tid in enumerate(thu_tu):
            self.ds.move(tid, "", i)
        self._danh_so_lai()

    def xoay(self, goc: int):
        for tid in self._chon():
            tr = self.trang[tid]
            tr.xoay_tay = (tr.xoay_tay + goc) % 360
            tr.khung_tay = None
            tr.tat_tu_xoay = True
            self._cap_nhat_dong(tid, doi_anh=True)
            self.yeu_cau_xu_ly(tid)

    def xoa_trang(self):
        chon = self._chon()
        if not chon:
            return
        for tid in chon:
            self.ds.delete(tid)
            self.thu_tu.remove(tid)
            del self.trang[tid]
            self.anh_nho.pop(tid, None)
        self.dang_chon = None
        self._danh_so_lai()
        self._ve_xem_truoc()

    def xu_ly_lai_trang_chon(self):
        for tid in self._chon():
            self.yeu_cau_xu_ly(tid)

    def xu_ly_lai_tat_ca(self):
        tc = self.tuy_chon()
        for tid in self.thu_tu:
            self.yeu_cau_xu_ly(tid, tc)

    def dat_lai_khung(self):
        if self.dang_chon:
            self.trang[self.dang_chon].khung_tay = None
            self.yeu_cau_xu_ly(self.dang_chon)

    def khong_cat(self):
        if self.dang_chon:
            tr = self.trang[self.dang_chon]
            h, w = self.anh_goc(tr).shape[:2]
            tr.khung_tay = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
            self.yeu_cau_xu_ly(self.dang_chon)

    # ------------------------------------------------------------------ xem trước, kéo góc
    def _khung_hien(self, tr: Trang, anh: np.ndarray) -> np.ndarray:
        if tr.khung_tay is not None:
            return tr.khung_tay
        if tr.khung_tu_dong is not None:
            return tr.khung_tu_dong
        h, w = anh.shape[:2]
        return np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)

    def _ve_xem_truoc(self):
        c = self.xem
        c.delete("all")
        self._xem = None
        rong, cao = c.winfo_width(), c.winfo_height()
        if rong < 20 or not self.dang_chon or self.dang_chon not in self.trang:
            c.create_text(rong / 2, cao / 2, fill="#ccc", font=("Segoe UI", 12),
                          text="Kéo thả ảnh hoặc PDF vào đây" if not self.trang else "Chọn một trang để xem")
            self.nhan_thong_tin.configure(text="")
            return
        tr = self.trang[self.dang_chon]
        xem_goc = self.v_xem.get() == "goc"
        if xem_goc or not tr.ket_qua:
            anh = self.anh_goc(tr)
        elif len(tr.ket_qua) == 1:
            anh = doc_ghi.giai_ma(tr.ket_qua[0])
        else:  # trang đôi đã tách: xem cạnh nhau
            phan = [doc_ghi.giai_ma(k) for k in tr.ket_qua]
            h = max(p.shape[0] for p in phan)
            phan = [cv2.copyMakeBorder(p, 0, h - p.shape[0], 0, 20, cv2.BORDER_CONSTANT, value=(69, 63, 59)) for p in phan]
            anh = np.concatenate(phan, axis=1)
        anh_tk, s = anh_sang_tk(anh, rong - 20, cao - 20)
        dx, dy = (rong - anh_tk.width()) / 2, (cao - anh_tk.height()) / 2
        c.create_image(dx, dy, anchor="nw", image=anh_tk)
        self._xem = (anh_tk, s, dx, dy)
        if xem_goc:
            self._ve_khung(self._khung_hien(tr, anh))
        tt = getattr(tr, "thong_tin", None)
        dong = [tr.ten, f"Trạng thái: {tr.trang_thai}"]
        if tt:
            if any(tt["xoay"]):
                dong.append(f"Đã tự xoay: {', '.join(f'{g}°' for g in tt['xoay'])}")
            canh_bao = {c for ds in tt.get("canh_bao", []) for c in ds}
            if canh_bao:
                ten = {"nhoe": "chữ nhòe", "tay": "tay che trang"}
                dong.append("NÊN CHỤP LẠI: " + ", ".join(ten[c] for c in sorted(canh_bao)))
            trung = self._trung(tr)
            if trung:
                dong.append(f"CÓ THỂ CHỤP TRÙNG: giống hệt trang {self.thu_tu.index(trung) + 1} "
                            f"({self.trang[trung].ten}); xóa một trang nếu thừa.")
            if any(tt["nghieng"]):
                dong.append(f"Đã sửa nghiêng: {', '.join(f'{g:+.1f}°' for g in tt['nghieng'])}")
            dong.append("Khung cắt: " + ("chỉnh tay" if tr.khung_tay is not None else
                                         "tự tìm" if tt["khung"] is not None else "không cắt"))
        if xem_goc:
            dong.append("Kéo 4 góc màu cam để chỉnh khung; thả chuột là trang được xử lý lại.")
        self.nhan_thong_tin.configure(text="\n".join(dong))

    def _ve_khung(self, khung: np.ndarray):
        _, s, dx, dy = self._xem
        p = [(x * s + dx, y * s + dy) for x, y in nan_phang.sap_xep_goc(khung)]
        self.xem.create_polygon(*[v for d in p for v in d], outline="#ff8c1a", fill="", width=2, tags="khung")
        for i, (x, y) in enumerate(p):
            self.xem.create_oval(x - 9, y - 9, x + 9, y + 9, fill="#ff8c1a", outline="white", width=2, tags=("goc", f"g{i}"))

    def _bat_dau_keo(self, e):
        if self.v_xem.get() != "goc" or not self._xem or not self.dang_chon:
            return
        tr = self.trang[self.dang_chon]
        anh = self.anh_goc(tr)
        _, s, dx, dy = self._xem
        khung = nan_phang.sap_xep_goc(self._khung_hien(tr, anh)).copy()
        kc = [np.hypot(x * s + dx - e.x, y * s + dy - e.y) for x, y in khung]
        i = int(np.argmin(kc))
        if kc[i] <= 20:
            self._keo = (i, khung, anh.shape[1], anh.shape[0])

    def _keo_goc(self, e):
        if not self._keo:
            return
        i, khung, w, h = self._keo
        _, s, dx, dy = self._xem
        khung[i] = (min(max((e.x - dx) / s, 0), w - 1), min(max((e.y - dy) / s, 0), h - 1))
        self.xem.delete("khung")
        self.xem.delete("goc")
        self._ve_khung(khung)

    def _tha_goc(self, _e):
        if not self._keo:
            return
        _, khung, _, _ = self._keo
        self._keo = None
        tr = self.trang[self.dang_chon]
        tr.khung_tay = khung
        self.yeu_cau_xu_ly(self.dang_chon)

    # ------------------------------------------------------------------ xuất
    def mo_sua_pdf(self):
        """Mở cửa sổ Sửa PDF; nếu đang có trang đã xử lý thì hỏi có đưa sang không."""
        from loi_xu_ly.tai_lieu_pdf import TaiLieu
        from sua_pdf import mo_cua_so
        tl = TaiLieu()
        xong = [self.trang[t] for t in self.thu_tu if self.trang[t].ket_qua]
        so = sum(len(tr.ket_qua) for tr in xong)
        if xong and messagebox.askyesno(TEN_UNG_DUNG, f"Đưa {so} trang đã xử lý sang cửa sổ Sửa PDF?\n\n"
                                        "Chọn Không để mở cửa sổ trống rồi mở PDF có sẵn."):
            for tr in xong:
                for k in tr.ket_qua:
                    tl.them_anh(doc_ghi.giai_ma(k), tr.ten)
        mo_cua_so(self.goc, tl)

    def xuat_pdf(self):
        if not self.thu_tu:
            messagebox.showinfo(TEN_UNG_DUNG, "Chưa có trang nào.")
            return
        chua = [self.trang[t].ten for t in self.thu_tu if not self.trang[t].ket_qua]
        if chua:
            messagebox.showwarning(TEN_UNG_DUNG, f"Còn {len(chua)} trang chưa xử lý xong, đợi thêm một chút.")
            return
        ten_dau = Path(self.trang[self.thu_tu[0]].ten.split(" – ")[0]).stem
        duong_dan = filedialog.asksaveasfilename(title="Lưu PDF", defaultextension=".pdf",
                                                 initialfile=f"{ten_dau}_da-xu-ly.pdf", filetypes=[("PDF", "*.pdf")])
        if not duong_dan:
            return
        cac_byte = [k for t in self.thu_tu for k in self.trang[t].ket_qua]
        tcx = self.tuy_chon_xuat()

        def chay():
            try:
                cac_anh = [doc_ghi.giai_ma(b) for b in cac_byte]
                bao = lambda i, n, chu: self.hang_giao_dien.put(("tien_trinh", i, n, chu))  # noqa: E731
                doc_ghi.ghi_pdf(cac_anh, duong_dan, tcx.kho, tcx.le_mm, tcx.chat_luong, tcx.ocr, tcx.ngon_ngu,
                                bao_tien_trinh=bao)
                if tcx.xuat_txt:
                    doc_ghi.ghi_van_ban(cac_anh, Path(duong_dan).with_suffix(".txt"), tcx.ngon_ngu, bao)
                kb = Path(duong_dan).stat().st_size / 1024
                co = f"{kb / 1024:.1f} MB" if kb > 1024 else f"{kb:.0f} KB"
                self.hang_giao_dien.put(("xuat_xong", f"Đã lưu {len(cac_anh)} trang vào {Path(duong_dan).name} ({co})",
                                         duong_dan))
            except Exception as e:
                self.hang_giao_dien.put(("bao", f"Lỗi khi xuất PDF: {e}"))
        self.v_trang_thai.set("Đang xuất PDF…")
        threading.Thread(target=chay, daemon=True).start()

    # ------------------------------------------------------------------ theo dõi thư mục
    def mo_theo_doi(self):
        CuaSoTheoDoi(self)

    def gioi_thieu(self):
        ngon_ngu = ", ".join(nhan_dang.ngon_ngu_co_san()) or "chưa có"
        messagebox.showinfo(TEN_UNG_DUNG, (
            f"{TEN_UNG_DUNG} – nguyên mẫu {__version__}\n\n"
            "Mọi xử lý chạy trên máy này, không gửi dữ liệu đi đâu.\n\n"
            "• Mở ảnh/PDF, kéo thả tệp, hoặc chụp camera\n"
            "• Tự nắn phẳng theo mép giấy, xoay đúng chiều, sửa nghiêng\n"
            "• Làm trắng nền, giữ màu dấu đỏ, chữ ký, mực xanh\n"
            "• Chỉnh khung cắt: chọn 'Ảnh gốc và khung cắt', kéo 4 góc\n"
            "• Xuất PDF gộp theo khổ giấy, lề; lớp chữ tìm kiếm được\n"
            "• Thư mục theo dõi: tự xử lý tệp mới (máy scan, tệp tải về)\n\n"
            f"Gói ngôn ngữ OCR: {ngon_ngu}"))

    def _dong(self):
        if self.theo_doi:
            self.theo_doi.dung()
        self.goc.destroy()


class GoiY:
    """Chú thích nhỏ khi rê chuột lên nút."""

    def __init__(self, w, chu):
        self.w, self.chu, self.tw = w, chu, None
        w.bind("<Enter>", self.hien)
        w.bind("<Leave>", self.an)

    def hien(self, _e):
        self.tw = tk.Toplevel(self.w)
        self.tw.wm_overrideredirect(True)
        self.tw.geometry(f"+{self.w.winfo_rootx() + 10}+{self.w.winfo_rooty() + self.w.winfo_height() + 4}")
        tk.Label(self.tw, text=self.chu, background="#ffffe0", relief="solid", borderwidth=1,
                 font=("Segoe UI", 9)).pack()

    def an(self, _e):
        if self.tw:
            self.tw.destroy()
            self.tw = None


class CuaSoCamera(tk.Toplevel):
    """Chụp ảnh tài liệu từ webcam hoặc camera tài liệu; khung giấy hiện trực tiếp.

    Chế độ tự động chụp: tự chụp mỗi khi thấy một trang mới đứng yên, rõ nét, đủ sáng
    (xem loi_xu_ly/tu_chup.py); người dùng chỉ việc lật trang hoặc thay tờ giấy.
    """

    def __init__(self, cha, khi_chup, khi_thay=None, tach=lambda: False):
        super().__init__(cha)
        self.title("Chụp từ camera")
        self.geometry("960x720")
        self.khi_chup = khi_chup      # khi_chup(ảnh) -> mã trang
        self.khi_thay = khi_thay      # khi_thay(mã trang, ảnh): chụp lại trang đó
        self.tach = tach              # hồ sơ sách: kiểm tra từng trang của cặp trang
        self.tid_cuoi = None          # trang vừa chụp
        self.thay_tid = None          # lần chụp tới thay ảnh của trang này
        self.hang_kt: queue.Queue = queue.Queue()  # kết quả kiểm tra ảnh vừa chụp (luồng nền)
        self.cam = None
        self.khung_hinh = None
        self.dem_khung = 0
        self.khung_giay = None
        self.so_anh = 0
        self.bo_tu_chup = BoTuChup()
        self.trang_thai = None

        tren = ttk.Frame(self, padding=6)
        tren.pack(fill="x")
        ttk.Label(tren, text="Camera số").pack(side="left")
        self.v_so = tk.IntVar(value=0)
        ttk.Spinbox(tren, from_=0, to=5, width=4, textvariable=self.v_so, command=self.mo).pack(side="left", padx=4)
        ttk.Button(tren, text="📸 Chụp (Space)", command=self.chup).pack(side="left", padx=8)
        self.v_tu_dong = tk.BooleanVar(value=True)
        ttk.Checkbutton(tren, text="Tự động chụp", variable=self.v_tu_dong,
                        command=self.bo_tu_chup.dat_lai).pack(side="left", padx=4)
        ttk.Button(tren, text="Xong", command=self.dong).pack(side="right")
        self.v_bao = tk.StringVar(value="")
        ttk.Label(tren, textvariable=self.v_bao).pack(side="left", padx=8)
        # báo ảnh vừa chụp bị nhòe, có tay che: nút chụp lại (lần chụp tới thay ảnh đó)
        self.thanh_bao = tk.Frame(self, background="#b45309")
        self.v_canh_bao = tk.StringVar(value="")
        tk.Label(self.thanh_bao, textvariable=self.v_canh_bao, background="#b45309", foreground="white",
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=10, pady=6)
        ttk.Button(self.thanh_bao, text="Bỏ qua", command=self._an_bao).pack(side="right", padx=6)
        self.nut_chup_lai = ttk.Button(self.thanh_bao, text="Chụp lại ảnh này (R)", command=self.chup_lai)
        self.nut_chup_lai.pack(side="right", padx=6)
        self.bind("r", lambda e: self.chup_lai())
        self.nen = tk.Canvas(self, background="black", highlightthickness=0)
        self.nen.pack(fill="both", expand=True)
        self.bind("<space>", lambda e: self.chup())
        self.protocol("WM_DELETE_WINDOW", self.dong)
        self.mo()
        self.after(30, self.cap_nhat)

    def mo(self):
        if self.cam is not None:
            self.cam.release()
        self.cam = cv2.VideoCapture(int(self.v_so.get()), cv2.CAP_DSHOW)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        if not self.cam.isOpened():
            self.v_bao.set("Không mở được camera này. Thử số khác.")
        else:
            w, h = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH), self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.v_bao.set(f"Camera {self.v_so.get()}: {int(w)}×{int(h)}")

    def cap_nhat(self):
        if not self.winfo_exists():
            return
        try:
            while True:
                self._khi_kiem_tra(*self.hang_kt.get_nowait())
        except queue.Empty:
            pass
        if self.cam is not None and self.cam.isOpened():
            ok, kh = self.cam.read()
            if ok:
                self.khung_hinh = kh
                self.dem_khung += 1
                self.trang_thai = None
                if self.v_tu_dong.get():
                    self.trang_thai = tt = self.bo_tu_chup.nhan_khung(kh)
                    self.khung_giay = tt.khung
                    if tt.anh is not None:
                        self.chup(tt.anh)
                elif self.dem_khung % 15 == 0:
                    # bộ tìm mép mới chậm hơn (~0,2 s): xem trước chỉ cần khung thô, không tinh chỉnh
                    kq = tim_mep.tim_tu_giac(kh, tinh=False)
                    self.khung_giay = None if kq is None else kq[0]
                rong, cao = self.nen.winfo_width(), self.nen.winfo_height()
                if rong > 20:
                    self._anh, s = anh_sang_tk(kh, rong, cao)
                    dx, dy = (rong - self._anh.width()) / 2, (cao - self._anh.height()) / 2
                    self.nen.delete("all")
                    self.nen.create_image(dx, dy, anchor="nw", image=self._anh)
                    tt = self.trang_thai
                    mau = "#3cf060" if tt is None or tt.ma in ("dang_giu", "da_chup") else "#ffa030"
                    if self.khung_giay is not None:
                        p = [v for x, y in self.khung_giay for v in (x * s + dx, y * s + dy)]
                        self.nen.create_polygon(*p, outline=mau, fill="", width=3)
                    if tt is not None:
                        self._ve_loi_nhac(tt, rong, cao)
        self.after(30, self.cap_nhat)

    def _ve_loi_nhac(self, tt, rong, cao):
        """Lời nhắc ở cuối khung hình, kèm vòng tiến độ khi đang giữ yên chờ chụp."""
        chu = tt.loi_nhac + (f"   ·   đã chụp {self.so_anh}" if self.so_anh else "")
        y = cao - 36
        o = self.nen.create_text(rong / 2, y, text=chu, fill="white", font=("Segoe UI", 15, "bold"))
        x0, y0, x1, y1 = self.nen.bbox(o)
        nen = self.nen.create_rectangle(x0 - 16, y0 - 8, x1 + 16, y1 + 8, fill="#202020", outline="")
        self.nen.tag_lower(nen, o)
        if tt.ma == "dang_giu":
            r, cx = 13, x0 - 40
            self.nen.create_oval(cx - r, y - r, cx + r, y + r, outline="#555555", width=4)
            self.nen.create_arc(cx - r, y - r, cx + r, y + r, start=90, extent=-359.9 * tt.tien_do,
                                style="arc", outline="#3cf060", width=4)

    def chup(self, anh=None):
        anh = self.khung_hinh if anh is None else anh
        if anh is None:
            return
        anh = anh.copy()
        if self.thay_tid is not None and self.khi_thay is not None:
            tid = self.thay_tid
            self.khi_thay(tid, anh)
            self.thay_tid = None
            self.v_bao.set("Đã chụp lại ảnh")
        else:
            tid = self.khi_chup(anh)
            self.so_anh += 1
            self.v_bao.set(f"Đã chụp {self.so_anh} ảnh")
        self.tid_cuoi = tid
        self._an_bao()
        self.nen.configure(background="white")
        self.after(120, lambda: self.nen.configure(background="black"))
        tach = self.tach()
        # kiểm tra nhanh ảnh vừa chụp ở luồng nền: nhòe, tay che thì báo ngay trên cửa sổ camera
        threading.Thread(target=lambda: self.hang_kt.put((tid, kiem_tra_anh_chup(anh, tach))), daemon=True).start()

    def _khi_kiem_tra(self, tid, loi):
        if not loi or tid is None or tid != self.tid_cuoi:
            return
        ten = {"nhoe": "chữ nhòe", "tay": "tay che trang"}
        self.v_canh_bao.set("Ảnh vừa chụp: " + ", ".join(ten[c] for c in loi) + ". Nên chụp lại.")
        self.nut_chup_lai.configure(state="normal" if self.khi_thay else "disabled")
        self.thanh_bao.pack(fill="x", before=self.nen)
        self.bell()

    def _an_bao(self):
        self.thanh_bao.pack_forget()

    def chup_lai(self):
        """Lần chụp tới thay ảnh vừa chụp (bị nhòe, có tay)."""
        if self.tid_cuoi is None or self.khi_thay is None:
            return
        self.thay_tid = self.tid_cuoi
        self.bo_tu_chup.dat_lai()
        self._an_bao()
        self.v_bao.set("Đặt lại trang vừa rồi; lần chụp tới sẽ thay ảnh đó")

    def dong(self):
        if self.cam is not None:
            self.cam.release()
        self.destroy()


class CuaSoTheoDoi(tk.Toplevel):
    """Bật, tắt thư mục theo dõi: tệp mới vào thư mục được tự xử lý thành PDF."""

    def __init__(self, ung_dung: UngDung):
        super().__init__(ung_dung.goc)
        self.ud = ung_dung
        self._hang: list[str] = []
        self.title("Thư mục theo dõi")
        self.geometry("640x420")
        k = ttk.Frame(self, padding=10)
        k.pack(fill="both", expand=True)
        self.v_vao = tk.StringVar()
        self.v_ra = tk.StringVar()
        for hang, (nhan, bien) in enumerate((("Thư mục nhận tệp", self.v_vao), ("Thư mục ghi PDF", self.v_ra))):
            ttk.Label(k, text=nhan).grid(row=hang, column=0, sticky="w", pady=3)
            ttk.Entry(k, textvariable=bien).grid(row=hang, column=1, sticky="ew", padx=6)
            ttk.Button(k, text="Chọn…", command=lambda b=bien: self._chon(b)).grid(row=hang, column=2)
        k.columnconfigure(1, weight=1)
        ttk.Label(k, text="Để trống thư mục ghi PDF thì dùng thư mục con 'da-xu-ly'. Tệp mới được xử lý "
                          "theo tùy chọn đang đặt ở cửa sổ chính.", wraplength=600, foreground="#555").grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(4, 6))
        self.v_cu = tk.BooleanVar(value=False)
        ttk.Checkbutton(k, text="Xử lý cả tệp đã có sẵn trong thư mục", variable=self.v_cu).grid(
            row=3, column=0, columnspan=3, sticky="w")
        self.nut = ttk.Button(k, text="Bắt đầu theo dõi", command=self.bat_tat)
        self.nut.grid(row=4, column=0, columnspan=3, sticky="w", pady=6)
        self.nhat_ky = tk.Text(k, height=12, font=("Consolas", 9), state="disabled")
        self.nhat_ky.grid(row=5, column=0, columnspan=3, sticky="nsew")
        k.rowconfigure(5, weight=1)
        if self.ud.theo_doi:
            self.v_vao.set(str(self.ud.theo_doi.thu_muc))
            self.v_ra.set(str(self.ud.theo_doi.ra))
            self.nut.configure(text="Dừng theo dõi")
        self._kiem_tra()

    def _chon(self, bien):
        d = filedialog.askdirectory(parent=self)
        if d:
            bien.set(d)

    def ghi(self, chu):  # gọi từ luồng theo dõi
        self.ud.hang_giao_dien.put(("bao", chu))
        self._hang.append(chu)

    def _kiem_tra(self):
        if not self.winfo_exists():
            return
        if self._hang:
            self.nhat_ky.configure(state="normal")
            while self._hang:
                self.nhat_ky.insert("end", self._hang.pop(0) + "\n")
            self.nhat_ky.see("end")
            self.nhat_ky.configure(state="disabled")
        self.after(300, self._kiem_tra)

    def bat_tat(self):
        from tu_dong import TheoDoi
        if self.ud.theo_doi:
            self.ud.theo_doi.dung()
            self.ud.theo_doi = None
            self.nut.configure(text="Bắt đầu theo dõi")
            return
        vao = self.v_vao.get().strip()
        if not vao or not Path(vao).is_dir():
            messagebox.showwarning("Thư mục theo dõi", "Chọn thư mục nhận tệp.", parent=self)
            return
        self.ud.theo_doi = TheoDoi(vao, self.v_ra.get().strip() or None, replace(self.ud.tuy_chon()),
                                   self.ud.tuy_chon_xuat(), bao=self.ghi, ca_tep_cu=self.v_cu.get())
        self.ud.theo_doi.bat_dau()
        self.nut.configure(text="Dừng theo dõi")


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    goc = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    ud = UngDung(goc)
    if len(sys.argv) > 1:
        goc.after(300, lambda: ud.mo_tep(sys.argv[1:]))
    goc.mainloop()


if __name__ == "__main__":
    main()
