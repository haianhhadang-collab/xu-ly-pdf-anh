"""Cửa sổ Sửa PDF: sửa trang của PDF có sẵn (chèn, xóa, xoay, đảo thứ tự, gộp, tách) và sửa nội dung trang
(sửa chữ khớp phông, thêm chữ, che, tô sáng, chèn ảnh chữ ký, con dấu).

Mở từ nút "✏ Sửa PDF…" của giao diện chính, hoặc chạy riêng:  python sua_pdf.py [tệp PDF, ảnh ...]
Lõi: loi_xu_ly/tai_lieu_pdf.py, loi_xu_ly/sua_noi_dung.py.
"""
from __future__ import annotations

import queue
import sys
import threading
from pathlib import Path

import cv2
import numpy as np
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loi_xu_ly import doc_ghi, nhan_dang  # noqa: E402
from loi_xu_ly import sua_ky_tu as sk  # noqa: E402
from loi_xu_ly import sua_noi_dung as snd  # noqa: E402
from loi_xu_ly import chu_thich as ct_  # noqa: E402
from loi_xu_ly import doi_tuong as dt  # noqa: E402
from loi_xu_ly.tai_lieu_pdf import TaiLieu  # noqa: E402
from sua_pdf_doi_tuong import DoiTuongMixin  # noqa: E402
from sua_pdf_trang import TrangMixin  # noqa: E402

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None

CO_ANH_NHO = 96
CONG_CU = {"xem": "Xem, cuộn", "chon": "Chọn, dời, đổi cỡ (đối tượng, vùng có sẵn)",
           "sua_ky_tu": "Sửa ký tự (giữ nguyên bản gốc)", "them_chu": "Thêm chữ",
           "che": "Che thông tin", "to_sang": "Tô sáng", "hinh": "Vẽ hình (chữ nhật, elip, mũi tên…)",
           "chen_anh": "Chèn ảnh (chữ ký, con dấu)",
           "chu_thich": "Chú thích (không sửa bản gốc)",
           "sua_chu": "Viết lại cả khối chữ (vẽ lại bằng phông)"}
GOI_Y = {
    "xem": "Lăn chuột để cuộn, giữ Ctrl + lăn chuột để phóng to, thu nhỏ.",
    "sua_ky_tu": "Bấm vào chỗ cần sửa trên một dòng (con trỏ đỏ). ← → di chuyển, Backspace / Delete xóa ký tự, gõ để chèn: "
                 "ký tự chèn được chép nguyên hình từ chính trang, chữ cũ giữ nguyên. Enter để xong, Esc để hủy. "
                 "Ký tự viền vàng là mẫu chưa chắc: bấm chuột phải lên một ký tự đúng trên trang để dùng làm mẫu. "
                 "Kéo chuột hoặc Shift + ← → để bôi chọn một đoạn rồi đổi Cỡ (pt) ở khung Chữ (phóng, thu chính nét chữ "
                 "gốc), hoặc chọn Phông, Kiểu để vẽ lại đoạn đó bằng phông; Ctrl+] / Ctrl+[ tăng, giảm 1 pt.",
    "sua_chu": "Bấm vào một khối chữ (khung xanh: một dòng hoặc cả đoạn) rồi gõ sửa ngay trên trang. "
               "Ctrl+Enter hoặc bấm ra ngoài để áp, Esc để hủy. Không sửa được chỗ có con dấu, chữ ký.",
    "them_chu": "Bấm vào chỗ muốn thêm chữ (góc trên trái của chữ), gõ ngay trên trang; Ctrl+Enter để xong.",
    "chon": "Bấm vào đối tượng (viền tím: chữ thêm, ảnh, hình, khung che…) hoặc vùng có sẵn trên bản scan (viền xám) để "
            "chọn; kéo để dời, kéo ô vuông để đổi cỡ, Delete để xóa, mũi tên để nhích, Ctrl+C / Ctrl+V để nhân bản. "
            "Kéo trên chỗ trống để khoanh vùng tùy ý. Bấm đúp vào chữ đã thêm để sửa. Vùng viền đỏ (con dấu, chữ ký) bị khóa.",
    "hinh": "Chọn loại hình, độ dày ở khung Hình; kéo chuột để vẽ (mũi tên vẽ theo chiều kéo). Màu theo nút Màu chữ.",
    "che": "Kéo chuột quanh vùng cần che. Thông tin bị che xóa hẳn khỏi trang khi lưu.",
    "to_sang": "Kéo chuột quanh đoạn cần tô sáng.",
    "chen_anh": "Chọn ảnh, rồi kéo chuột để đặt ảnh lên trang (giữ tỉ lệ ảnh).",
    "chu_thich": "Chọn loại ở khung Chú thích. Ghi chú, dấu Đã xem: bấm vào chỗ đặt. Bút phê, tô sáng, hình: kéo chuột. "
                 "Chú thích lưu thành chú thích PDF chuẩn, trang gốc giữ nguyên; trình đọc PDF khác ẩn, sửa, xóa được. "
                 "Dùng công cụ Chọn để dời, đổi cỡ, xóa; bấm đúp ghi chú, bút phê để sửa lời.",
}
TEN_KIEU_NGUOC = {v: k for k, v in snd.TEN_KIEU.items()}


class CuaSoSuaPdf(DoiTuongMixin, TrangMixin):
    def __init__(self, cua_so: tk.Misc, tai_lieu: TaiLieu | None = None):
        self.w = cua_so
        self.w.title("Sửa PDF – Xử lý PDF ảnh")
        self.w.geometry("1280x820")
        self.w.minsize(980, 640)
        try:
            self.w.state("zoomed")
        except tk.TclError:
            pass
        self.tl = tai_lieu or TaiLieu()
        self.hien_tai: int | None = None
        self.ty_le = 1.0
        self.anh_hien: np.ndarray | None = None       # ảnh trang đang sửa (đã áp thao tác)
        self.cac_tu: list[snd.Tu] | None = None       # chữ tìm được trên ảnh đang hiện
        self.cac_khoi: list[snd.KhoiChu] = []         # các khối chữ (dòng, đoạn) gộp từ cac_tu
        self._sua: dict | None = None                 # ô đang sửa ngay trên trang
        self.cac_dong: list[sk.DongAnh] | None = None  # dòng, khung từng ký tự trên ảnh đang hiện (Sửa ký tự)
        self._phien: sk.PhienSuaDong | None = None    # dòng đang sửa ký tự
        self.anh_xem: np.ndarray | None = None        # xem trước khi đang sửa ký tự
        self._dong_trang: dict[int, tuple] = {}       # các trang khác đã nhận dạng: chỗ tìm ký tự mẫu
        self._dang_doc_trang = False
        self.anh_chen: bytes | None = None
        self.mau_chu = (0, 0, 0)  # BGR
        self.anh_nho: dict[int, ImageTk.PhotoImage] = {}
        self._tk_anh = None
        self._keo = None
        self.hang: queue.Queue = queue.Queue()
        self._phien_tim = 0

        self.v_cong_cu = tk.StringVar(value="xem")
        self.v_phong = tk.StringVar(value="Tự đoán")
        self.v_kieu = tk.StringVar(value="Tự đoán")
        self.v_co = tk.DoubleVar(value=13.0)
        self.v_che_den = tk.BooleanVar(value=False)
        self.v_bo_nen = tk.BooleanVar(value=True)
        self.v_ocr = tk.BooleanVar(value=nhan_dang.CO_TESSERACT)
        self.v_trang_thai = tk.StringVar(value="Mở PDF hoặc ảnh để bắt đầu (nút Mở, hoặc kéo thả tệp vào cửa sổ).")
        self.v_hinh = tk.StringVar(value=dt.TEN_HINH["chu_nhat"])
        self.v_day = tk.IntVar(value=3)
        self.v_loai_ct = tk.StringVar(value=ct_.LOAI["ghi_chu"])
        self.anh_ve: np.ndarray | None = None        # ảnh trang đang hiện: ảnh đã sửa + chú thích vẽ chồng
        self._nap_dinh_dang = False
        self._khoi_tao_doi_tuong()
        self._hen_kieu = None  # hẹn đoán phông, cỡ đoạn bôi chọn (Sửa ký tự)
        self._dung()
        self.w.after(100, self._nhan_tin)
        self._lam_moi_ds()
        if self.tl.trang:
            self.chon_trang(0)

    # ------------------------------------------------------------------ giao diện
    def _dung(self):
        w = self.w
        thanh = ttk.Frame(w, padding=(8, 6))
        thanh.pack(fill="x")
        for chu, lenh in (("📂 Mở, thêm PDF / ảnh…", self.them_tep), ("➕ Trang trắng", self.them_trang_trang)):
            ttk.Button(thanh, text=chu, command=lenh).pack(side="left", padx=(0, 6))
        ttk.Separator(thanh, orient="vertical").pack(side="left", fill="y", padx=6)
        for chu, lenh in (("⟲", lambda: self.xoay(270)), ("⟳", lambda: self.xoay(90)), ("▲", lambda: self.dich(-1)),
                          ("▼", lambda: self.dich(1)), ("🗑 Xóa trang", self.xoa_trang)):
            ttk.Button(thanh, text=chu, width=3 if len(chu) == 1 else None, command=lenh).pack(side="left", padx=(0, 4))
        ttk.Separator(thanh, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(thanh, text="💾 Lưu PDF…", command=lambda: self.luu(False)).pack(side="left", padx=(0, 6))
        ttk.Button(thanh, text="✂ Lưu trang đang chọn ra tệp mới…", command=lambda: self.luu(True)).pack(side="left", padx=(0, 6))
        c = ttk.Checkbutton(thanh, text="Lớp chữ cho trang đã sửa", variable=self.v_ocr)
        c.pack(side="left", padx=6)
        if not nhan_dang.CO_TESSERACT:
            c.state(["disabled"])

        than = ttk.Frame(w)
        than.pack(fill="both", expand=True)
        # danh sách trang
        trai = ttk.Frame(than, padding=(8, 0, 4, 8))
        trai.pack(side="left", fill="y")
        ttk.Label(trai, text="Các trang (chọn nhiều bằng Ctrl, Shift)").pack(anchor="w")
        kieu = ttk.Style(w)
        kieu.configure("SuaPdf.Treeview", rowheight=CO_ANH_NHO + 8)
        self.ds = ttk.Treeview(trai, style="SuaPdf.Treeview", show="tree", selectmode="extended", height=8)
        self.ds.column("#0", width=230)
        thanh_cuon = ttk.Scrollbar(trai, orient="vertical", command=self.ds.yview)
        self.ds.configure(yscrollcommand=thanh_cuon.set)
        self.ds.pack(side="left", fill="y", expand=True)
        thanh_cuon.pack(side="left", fill="y")
        self.ds.bind("<<TreeviewSelect>>", self._khi_chon_ds)
        self._khoi_tao_trang()

        # công cụ bên phải
        phai = ttk.Frame(than, padding=(4, 0, 8, 8), width=300)
        phai.pack(side="right", fill="y")
        n1 = ttk.LabelFrame(phai, text="Công cụ", padding=8)
        n1.pack(fill="x")
        for ma, ten in CONG_CU.items():
            ttk.Radiobutton(n1, text=ten, value=ma, variable=self.v_cong_cu, command=self._doi_cong_cu).pack(anchor="w")
        self.nhan_goi_y = ttk.Label(n1, text=GOI_Y["xem"], wraplength=270, foreground="#555", justify="left")
        self.nhan_goi_y.pack(anchor="w", pady=(6, 0))

        n2 = ttk.LabelFrame(phai, text="Chữ", padding=8)
        n2.pack(fill="x", pady=(8, 0))
        ttk.Label(n2, text="Phông").grid(row=0, column=0, sticky="w")
        ttk.Combobox(n2, textvariable=self.v_phong, values=["Tự đoán", *snd.PHONG], state="readonly", width=20).grid(row=0, column=1, sticky="w")
        ttk.Label(n2, text="Kiểu").grid(row=1, column=0, sticky="w")
        ttk.Combobox(n2, textvariable=self.v_kieu, values=["Tự đoán", *snd.TEN_KIEU.values()], state="readonly", width=20).grid(row=1, column=1, sticky="w", pady=2)
        ttk.Label(n2, text="Cỡ (pt)").grid(row=2, column=0, sticky="w")
        ttk.Spinbox(n2, from_=6, to=72, increment=0.5, textvariable=self.v_co, width=6).grid(row=2, column=1, sticky="w")
        self.nut_mau = tk.Button(n2, text="Màu chữ", width=10, command=self._chon_mau, bg="#000000", fg="white")
        self.nut_mau.grid(row=3, column=1, sticky="w", pady=(4, 0))
        ttk.Label(n2, text="“Tự đoán” dùng cho Sửa chữ: lấy phông, cỡ, màu của chính chữ cũ. Thêm chữ dùng "
                           "Times New Roman thường nếu để Tự đoán. Sửa ký tự: bôi chọn một đoạn rồi đổi Cỡ (Phông, "
                           "Kiểu để Tự đoán: phóng, thu nét gốc) hoặc chọn Phông, Kiểu để vẽ lại đoạn đó.",
                  wraplength=270, foreground="#555").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))

        n3 = ttk.LabelFrame(phai, text="Hình, che, chèn ảnh", padding=8)
        n3.pack(fill="x", pady=(8, 0))
        h = ttk.Frame(n3)
        h.pack(anchor="w", pady=(0, 4))
        ttk.Combobox(h, textvariable=self.v_hinh, values=list(dt.TEN_HINH.values()), state="readonly", width=14).pack(side="left")
        ttk.Label(h, text=" dày").pack(side="left")
        ttk.Spinbox(h, from_=1, to=20, textvariable=self.v_day, width=4).pack(side="left")
        ttk.Checkbutton(n3, text="Che bằng màu đen (bỏ chọn: màu trắng)", variable=self.v_che_den).pack(anchor="w")
        ttk.Button(n3, text="Chọn ảnh để chèn…", command=self._chon_anh_chen).pack(anchor="w", pady=(6, 0))
        self.nhan_anh_chen = ttk.Label(n3, text="Chưa chọn ảnh", foreground="#555")
        self.nhan_anh_chen.pack(anchor="w")
        ttk.Checkbutton(n3, text="Bỏ nền trắng (ảnh chữ ký, con dấu chụp trên giấy)", variable=self.v_bo_nen).pack(anchor="w")

        n5 = ttk.LabelFrame(phai, text="Chú thích (không sửa bản gốc)", padding=8)
        n5.pack(fill="x", pady=(8, 0))
        ttk.Combobox(n5, textvariable=self.v_loai_ct, values=list(ct_.LOAI.values()), state="readonly", width=18).pack(
            anchor="w")
        ttk.Label(n5, text="Màu bút phê, hình theo nút Màu chữ; cỡ bút phê theo Cỡ (pt); độ dày hình theo ô dày.",
                  wraplength=270, foreground="#555").pack(anchor="w", pady=(4, 0))

        n4 = ttk.LabelFrame(phai, text="Thao tác trên trang này", padding=8)
        n4.pack(fill="both", expand=True, pady=(8, 0))
        self.ds_thao_tac = tk.Listbox(n4, height=8, activestyle="none")
        self.ds_thao_tac.pack(fill="both", expand=True)
        h = ttk.Frame(n4)
        h.pack(fill="x", pady=(6, 0))
        ttk.Button(h, text="Xóa thao tác chọn", command=self.xoa_thao_tac).pack(side="left")
        ttk.Button(h, text="Hoàn tác (Ctrl+Z)", command=self.hoan_tac).pack(side="right")
        ttk.Button(h, text="Làm lại (Ctrl+Y)", command=self.lam_lai_tt).pack(side="right", padx=4)

        # vùng xem trang
        giua = ttk.Frame(than, padding=(4, 0, 4, 8))
        giua.pack(side="left", fill="both", expand=True)
        h = ttk.Frame(giua)
        h.pack(fill="x")
        ttk.Button(h, text="Vừa khung", command=self.vua_khung).pack(side="left")
        ttk.Button(h, text="100%", command=lambda: self.dat_ty_le(1.0)).pack(side="left", padx=4)
        ttk.Button(h, text="−", width=3, command=lambda: self.dat_ty_le(self.ty_le / 1.25)).pack(side="left")
        ttk.Button(h, text="+", width=3, command=lambda: self.dat_ty_le(self.ty_le * 1.25)).pack(side="left", padx=4)
        self.nhan_trang = ttk.Label(h, text="")
        self.nhan_trang.pack(side="left", padx=8)
        khung = ttk.Frame(giua)
        khung.pack(fill="both", expand=True)
        self.cv = tk.Canvas(khung, bg="#5d6670", highlightthickness=0, cursor="arrow")
        cx, cy = ttk.Scrollbar(khung, orient="horizontal", command=self.cv.xview), ttk.Scrollbar(khung, orient="vertical", command=self.cv.yview)
        self.cv.configure(xscrollcommand=cx.set, yscrollcommand=cy.set)
        self.cv.grid(row=0, column=0, sticky="nsew")
        cy.grid(row=0, column=1, sticky="ns")
        cx.grid(row=1, column=0, sticky="ew")
        khung.rowconfigure(0, weight=1)
        khung.columnconfigure(0, weight=1)
        self.cv.bind("<ButtonPress-1>", self._bam)
        self.cv.bind("<B1-Motion>", self._keo_chuot)
        self.cv.bind("<ButtonRelease-1>", self._tha)
        self.cv.bind("<MouseWheel>", self._lan)
        self.cv.bind("<Key>", self._phim)
        self.cv.bind("<Button-3>", self._bam_phai)
        self.cv.bind("<Double-Button-1>", self._bam_dup)
        w.bind("<Control-z>", lambda _e: self.hoan_tac())
        w.bind("<Control-y>", lambda _e: self.lam_lai_tt())
        for bien in (self.v_phong, self.v_kieu, self.v_co):
            bien.trace_add("write", lambda *_: None if self._nap_dinh_dang else self._ap_dinh_dang_chon())

        ttk.Label(w, textvariable=self.v_trang_thai, padding=(8, 3), relief="sunken", anchor="w").pack(fill="x", side="bottom")
        if TkinterDnD is not None:
            try:
                w.drop_target_register(DND_FILES)
                w.dnd_bind("<<Drop>>", lambda e: self._them_cac_tep(w.tk.splitlist(e.data)))
            except Exception:
                pass

    # ------------------------------------------------------------------ danh sách trang
    def _lam_moi_ds(self, chon: list[int] | None = None):
        self.ds.delete(*self.ds.get_children())
        self.anh_nho.clear()
        for i, t in enumerate(self.tl.trang):
            try:
                nho = self.tl.anh_nho(i, CO_ANH_NHO)
                self.anh_nho[i] = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(nho, cv2.COLOR_BGR2RGB)))
            except Exception:
                self.anh_nho[i] = None
            nhan = f"  {i + 1}. {t.ten}" + ("\n  ✏ đã sửa nội dung" if t.da_sua or t.da_gop else "") + (f"\n  ⟳ {t.xoay}°" if t.xoay else "")
            self.ds.insert("", "end", iid=str(i), text=nhan, image=self.anh_nho[i] or "")
        if chon:
            self.ds.selection_set([str(i) for i in chon if i < len(self.tl.trang)])
        if not self.tl.trang:
            self.hien_tai = None
            self.cv.delete("all")
            self.nhan_trang.configure(text="")
            self.ds_thao_tac.delete(0, "end")

    def _chon_ds(self) -> list[int]:
        return sorted(int(x) for x in self.ds.selection())

    def _khi_chon_ds(self, _e=None):
        chon = self._chon_ds()
        if chon and chon[0] != self.hien_tai:
            self.chon_trang(chon[0], cap_nhat_ds=False)

    def chon_trang(self, i: int, cap_nhat_ds: bool = True):
        self._dong_sua(ap=True)
        self._xong_phien(ap=True)
        self.dang_chon = None
        self.hien_tai = i
        if cap_nhat_ds:
            self.ds.selection_set(str(i))
            self.ds.see(str(i))
        self._dung_lai_anh(vua=True)

    # ------------------------------------------------------------------ hiển thị
    def _dung_lai_anh(self, vua: bool = False):
        i = self.hien_tai
        if i is None:
            return
        t = self.tl.trang[i]
        self.v_trang_thai.set("Đang dựng trang…")
        self.w.update_idletasks()
        try:
            self.anh_hien = self.tl.anh_trang(i, chu_thich=False)
            self.anh_ve = ct_.phu_len(self.anh_hien, t.thao_tac)
        except Exception as e:
            messagebox.showerror("Sửa PDF", f"Không dựng được trang: {e}", parent=self.w)
            return
        self.cac_tu, self.cac_khoi, self.cac_dong, self.cac_vung = None, [], None, None
        self.ds_thao_tac.delete(0, "end")
        for tt in t.thao_tac:
            self.ds_thao_tac.insert("end", tt.mo_ta())
        h, w = self.anh_hien.shape[:2]
        self.nhan_trang.configure(text=f"Trang {i + 1}/{len(self.tl.trang)} · {w}×{h} điểm ảnh" + (" · trang PDF gốc" if t.loai == "pdf" and not t.da_sua else ""))
        if vua:
            self.vua_khung()
        else:
            self._ve()
        if self.v_cong_cu.get() in ("sua_chu", "sua_ky_tu"):
            self._tim_chu()
        else:
            self.v_trang_thai.set(GOI_Y[self.v_cong_cu.get()])

    def vua_khung(self):
        if self.anh_hien is None:
            return
        self.w.update_idletasks()
        cw, ch = max(200, self.cv.winfo_width()), max(200, self.cv.winfo_height())
        h, w = self.anh_hien.shape[:2]
        self.dat_ty_le(min((cw - 20) / w, (ch - 20) / h))

    def dat_ty_le(self, s: float):
        self.ty_le = max(0.05, min(4.0, s))
        self._ve()

    def _ve(self):
        self.cv.delete("all")
        if self.anh_hien is None:
            return
        anh = self.anh_xem if (self._phien and self.anh_xem is not None) else (
            self.anh_ve if self.anh_ve is not None else self.anh_hien)
        h, w = anh.shape[:2]
        s = self.ty_le
        nho = cv2.resize(anh, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
        self._tk_anh = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(nho, cv2.COLOR_BGR2RGB)))
        self.cv.create_image(10, 10, image=self._tk_anh, anchor="nw")
        self.cv.configure(scrollregion=(0, 0, w * s + 20, h * s + 20))
        self._ve_tu()
        self._dat_o_sua()
        self._ve_phien()
        self._ve_doi_tuong()

    def _ra_man(self, x, y):
        return x * self.ty_le + 10, y * self.ty_le + 10

    def _ra_anh(self, e) -> tuple[float, float]:
        return (self.cv.canvasx(e.x) - 10) / self.ty_le, (self.cv.canvasy(e.y) - 10) / self.ty_le

    def _ve_tu(self):
        """Vẽ khung các khối chữ (Viết lại khối) hoặc các dòng (Sửa ký tự)."""
        self.cv.delete("tu")
        if self.v_cong_cu.get() == "sua_ky_tu" and self.cac_dong:
            for d in self.cac_dong:
                if self._phien and d is self._phien.dong:
                    continue
                self.cv.create_polygon(*self._khung_dong(d, d.hop[0] - 2, d.hop[2] + 2), fill="", outline="#4a90d9",
                                       dash=(2, 3), tags="tu")
            return
        if self.v_cong_cu.get() != "sua_chu" or not self.cac_khoi:
            return
        dang = self._sua["khoi"] if self._sua and self._sua["loai"] == "khoi" else None
        for k in self.cac_khoi:
            x0, y0, x1, y1 = k.hop
            a0, b0 = self._ra_man(x0, y0)
            a1, b1 = self._ra_man(x1, y1)
            self.cv.create_rectangle(a0 - 3, b0 - 3, a1 + 3, b1 + 3, outline="#e07a00" if k is dang else "#4a90d9",
                                     width=2, dash=() if k is dang else (3, 2), tags="tu")

    def _lan(self, e):
        if e.state & 0x4:  # Ctrl
            self.dat_ty_le(self.ty_le * (1.15 if e.delta > 0 else 1 / 1.15))
        else:
            self.cv.yview_scroll(-1 if e.delta > 0 else 1, "units")

    # ------------------------------------------------------------------ tìm chữ (nền)
    def _tim_chu(self):
        ky_tu = self.v_cong_cu.get() == "sua_ky_tu"
        if self.anh_hien is None or (self.cac_dong if ky_tu else self.cac_tu) is not None:
            return
        if not nhan_dang.CO_TESSERACT:
            self.v_trang_thai.set("Chưa cài Tesseract OCR nên không sửa chữ được.")
            return
        self._phien_tim += 1
        phien, anh = self._phien_tim, self.anh_hien
        self.v_trang_thai.set("Đang tìm chữ trên trang…")

        def lam():
            try:
                if ky_tu:
                    self.hang.put(("dong", phien, sk.doc_dong(anh)))
                else:
                    self.hang.put(("tu", phien, snd.tim_tu(anh)))
            except Exception as e:
                self.hang.put(("loi", phien, str(e)))
        threading.Thread(target=lam, daemon=True).start()

    def _doc_trang_khac(self):
        """Nhận dạng dần các trang khác (ở nền) để có thêm chỗ tìm ký tự mẫu. Dựng ảnh trên luồng chính
        (PDFium không an toàn khi chạy nhiều luồng), nhận dạng trên luồng nền, mỗi lần một trang."""
        if self._dang_doc_trang:
            return
        for j, t in enumerate(self.tl.trang):
            khoa = (id(t), len(t.thao_tac))
            if j == self.hien_tai or (j in self._dong_trang and self._dong_trang[j][0] == khoa):
                continue
            try:
                anh = self.tl.anh_trang(j)
            except Exception:
                continue
            self._dang_doc_trang = True

            def lam(j=j, khoa=khoa, anh=anh):
                try:
                    self.hang.put(("trang_khac", j, (khoa, anh, sk.doc_dong(anh))))
                except Exception:
                    self.hang.put(("trang_khac", j, None))
            threading.Thread(target=lam, daemon=True).start()
            return

    def _nhan_tin(self):
        try:
            while True:
                tin = self.hang.get_nowait()
                if tin[0] == "dong" and tin[1] == self._phien_tim:
                    self.cac_dong = tin[2]
                    self.v_trang_thai.set(f"Tìm được {len(self.cac_dong)} dòng chữ. " + GOI_Y["sua_ky_tu"])
                    self._ve_tu()
                    self._doc_trang_khac()
                elif tin[0] == "trang_khac":
                    self._dang_doc_trang = False
                    if tin[2] is not None:
                        self._dong_trang[tin[1]] = tin[2]
                    self._doc_trang_khac()
                elif tin[0] == "tu" and tin[1] == self._phien_tim:
                    self.cac_tu = tin[2]
                    self.cac_khoi = snd.tim_khoi(self.cac_tu, self.anh_hien.shape[1])
                    self.v_trang_thai.set(f"Tìm được {len(self.cac_khoi)} khối chữ. " + GOI_Y["sua_chu"])
                    self._ve_tu()
                elif tin[0] == "loi" and tin[1] == self._phien_tim:
                    self.v_trang_thai.set(f"Không tìm được chữ: {tin[2]}")
                elif tin[0] == "luu":
                    self.v_trang_thai.set(tin[1])
                elif tin[0] == "luu_xong":
                    self.v_trang_thai.set(f"Đã lưu {tin[1]}")
                    messagebox.showinfo("Sửa PDF", f"Đã lưu {tin[1]}" + (f"\n\nTệp ghi rõ đã chỉnh sửa nội dung: {tin[2]}." if tin[2] else ""), parent=self.w)
                elif tin[0] == "luu_loi":
                    self.v_trang_thai.set("Lưu không được")
                    messagebox.showerror("Sửa PDF", f"Lưu không được: {tin[1]}", parent=self.w)
        except queue.Empty:
            pass
        self.w.after(100, self._nhan_tin)

    # ------------------------------------------------------------------ chuột trên trang
    def _doi_cong_cu(self):
        cc = self.v_cong_cu.get()
        self.nhan_goi_y.configure(text=GOI_Y[cc])
        self.v_trang_thai.set(GOI_Y[cc])
        self.cv.configure(cursor={"xem": "arrow", "chon": "arrow", "sua_chu": "hand2", "them_chu": "xterm",
                                  "sua_ky_tu": "xterm"}.get(cc, "crosshair"))
        self._dong_sua(ap=True)
        self._xong_phien(ap=True)
        if cc != "chon":
            self.dang_chon = None
        self._ve_doi_tuong()
        if cc in ("sua_chu", "sua_ky_tu"):
            self._tim_chu()
        self._ve_tu()

    def _bam(self, e):
        if self.anh_hien is None:
            return
        cc = self.v_cong_cu.get()
        x, y = self._ra_anh(e)
        if self._sua:  # bấm ra ngoài ô đang sửa: áp chỗ đang sửa
            self._dong_sua(ap=True)
            return
        if cc == "xem":
            self.cv.scan_mark(e.x, e.y)
            self._keo = ("xem",)
        elif cc == "chon":
            self._chon_bam(e, x, y)
        elif cc == "sua_ky_tu":
            self._bam_ky_tu(x, y, bool(e.state & 0x1))
        elif cc == "sua_chu":
            self._bam_khoi(x, y)
        elif cc == "them_chu":
            self._mo_o_sua("them", x=x, y=y)
        else:
            self._keo = ("hop", x, y, self.cv.create_rectangle(e.x, e.y, e.x, e.y, outline="#e07a00", width=2, dash=(4, 2)))

    def _keo_chuot(self, e):
        if self._keo and self._keo[0] == "ky_tu":
            if self._phien:
                self._phien.chon_x(self._keo[1], self._ra_anh(e)[0])
                self._ve_phien()
            return
        if not self._keo or self._chon_keo(e):
            return
        if self._keo[0] == "xem":
            self.cv.scan_dragto(e.x, e.y, gain=1)
            return
        _, x0, y0, ma = self._keo[:4]
        x1, y1 = self._ra_anh(e)
        if self.v_cong_cu.get() == "chen_anh" and self.anh_chen:
            y1 = y0 + abs(x1 - x0) * self._ty_le_anh_chen() * (1 if y1 >= y0 else -1)
        a0, b0 = self._ra_man(x0, y0)
        a1, b1 = self._ra_man(x1, y1)
        self.cv.coords(ma, a0, b0, a1, b1)
        self._keo = ("hop", x0, y0, ma, x1, y1)

    def _tha(self, _e):
        if self._keo and self._keo[0] == "ky_tu":
            self._keo = None
            self._hen_kieu_chon()
            return
        if self._chon_tha():
            return
        k, self._keo = self._keo, None
        if k and k[0] == "hop" and len(k) < 6 and self.v_cong_cu.get() == "chu_thich":  # bấm, không kéo
            k = k + (k[1], k[2])
        if not k or k[0] != "hop" or len(k) < 6:
            if k and k[0] == "hop":
                self.cv.delete(k[3])
            return
        _, x0, y0, ma, x1, y1 = k
        self.cv.delete(ma)
        hop = (int(min(x0, x1)), int(min(y0, y1)), int(max(x0, x1)), int(max(y0, y1)))
        cc = self.v_cong_cu.get()
        if cc == "chu_thich":
            self._tao_chu_thich(x0, y0, x1, y1)
            return
        if cc == "hinh":
            if max(hop[2] - hop[0], hop[3] - hop[1]) >= 6:
                loai = next(k for k, v in dt.TEN_HINH.items() if v == self.v_hinh.get())
                self._them_thao_tac(dt.HinhVe(loai, (int(x0), int(y0), int(x1), int(y1)), self.mau_chu, int(self.v_day.get())))
            return
        if hop[2] - hop[0] < 4 or hop[3] - hop[1] < 4:
            return
        if cc == "che":
            self._them_thao_tac(snd.Che(hop, (0, 0, 0) if self.v_che_den.get() else (255, 255, 255)))
        elif cc == "to_sang":
            self._them_thao_tac(snd.ToSang(hop))
        elif cc == "chen_anh":
            if not self.anh_chen:
                messagebox.showinfo("Sửa PDF", "Bấm “Chọn ảnh để chèn…” trước.", parent=self.w)
                return
            self._them_thao_tac(snd.ChenAnh(hop, self.anh_chen, self.v_bo_nen.get()))

    # ------------------------------------------------------------------ chú thích
    def _tao_chu_thich(self, x0, y0, x1, y1):
        loai = next(k for k, v in ct_.LOAI.items() if v == self.v_loai_ct.get())
        W = self.anh_hien.shape[1]
        hop = (int(min(x0, x1)), int(min(y0, y1)), int(max(x0, x1)), int(max(y0, y1)))
        bam = hop[2] - hop[0] < 6 and hop[3] - hop[1] < 6
        x, y = int(x0), int(y0)
        if loai == "ghi_chu":
            nd = self._hoi_noi_dung("Ghi chú")
            if nd:
                k = int(W * 0.035)
                self._them_thao_tac(ct_.GhiChu((x, y, x + k, y + k), noi_dung=nd))
        elif loai == "but_phe":
            nd = self._hoi_noi_dung("Bút phê")
            if not nd:
                return
            co = float(self.v_co.get()) / snd.diem_anh_sang_pt(W)
            if bam:
                hop = (x, y, min(W - 4, x + int(W * 0.45)), y + int(co * 1.5))
            bp = ct_.ButPhe(hop, self.mau_chu if any(self.mau_chu) else ct_.DO, nd, co_px=co)  # mực đen: đổi sang đỏ
            bp.hop = (hop[0], hop[1], hop[2], max(hop[3], hop[1] + bp.chieu_cao_vua()))
            self._them_thao_tac(bp)
        elif loai == "dau":
            w, h = int(W * 0.26), int(W * 0.09)
            self._them_thao_tac(ct_.DauCT((x - w // 2, y - h // 2, x + w // 2, y + h // 2)) if bam else ct_.DauCT(hop))
        elif bam:
            self.v_trang_thai.set("Kéo chuột để vẽ " + self.v_loai_ct.get().lower() + ".")
        elif loai == "to_sang":
            self._them_thao_tac(ct_.ToSangCT(hop))
        else:
            self._them_thao_tac(ct_.HinhCT(hop, self.mau_chu, loai=loai, diem=(int(x0), int(y0), int(x1), int(y1)),
                                           day=int(self.v_day.get())))

    def _hoi_noi_dung(self, tieu_de: str, cu: str = "") -> str | None:
        """Hộp nhập lời ghi chú, bút phê (nhiều dòng). Trả None nếu hủy."""
        hop = tk.Toplevel(self.w)
        hop.title(tieu_de)
        hop.transient(self.w)
        o = tk.Text(hop, width=48, height=6, wrap="word", font=("Segoe UI", 11))
        o.pack(fill="both", expand=True, padx=8, pady=8)
        o.insert("1.0", cu)
        kq = {"nd": None}

        def xong(_e=None):
            kq["nd"] = o.get("1.0", "end").strip()
            hop.destroy()
            return "break"
        h = ttk.Frame(hop)
        h.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(h, text="Hủy", command=hop.destroy).pack(side="right")
        ttk.Button(h, text="Xong (Ctrl+Enter)", command=xong).pack(side="right", padx=6)
        o.bind("<Control-Return>", xong)
        hop.bind("<Escape>", lambda _e: hop.destroy())
        o.focus_set()
        hop.grab_set()
        self.w.wait_window(hop)
        return kq["nd"] or None

    # ------------------------------------------------------------------ sửa ký tự (giữ nguyên bản gốc)
    def _dong_tai(self, x, y) -> sk.DongAnh | None:
        """Dòng ở điểm bấm: dải xiên theo dòng (ảnh chụp nghiêng) chứa điểm đó; nhiều dòng thì lấy dòng có lõi chữ gần
        nhất."""
        if not self.cac_dong:
            return None
        trong = [d for d in self.cac_dong if d.dai_tai(x)[0] <= y <= d.dai_tai(x)[1] and d.hop[0] - 15 <= x <= d.hop[2] + 15]
        return min(trong, key=lambda d: abs(d.chan_tai(x) - 0.35 * d.co - y)) if trong else None

    def _khung_dong(self, d: sk.DongAnh, x0: float, x1: float) -> list[float]:
        """Bốn góc (tọa độ màn hình) của dải dòng từ cột x0 tới x1, nghiêng theo dòng."""
        (t0, d0), (t1, d1) = d.dai_tai(x0), d.dai_tai(x1)
        return [v for x, y in ((x0, t0), (x1, t1), (x1, d1), (x0, d0)) for v in self._ra_man(x, y)]

    def _bam_ky_tu(self, x, y, shift: bool = False):
        self.cv.focus_set()
        if self.cac_dong is None:
            self.v_trang_thai.set("Đang tìm chữ trên trang, chờ một chút…")
            return
        d = self._dong_tai(x, y)
        if self._phien and d is self._phien.dong:
            p = self._phien
            if shift:  # Shift + bấm: mở rộng đoạn chọn tới chỗ bấm
                p.dat_con_tro(x, chon=True)
                self._hen_kieu_chon()
            else:
                p.dat_con_tro(x)
                self._keo = ("ky_tu", x)  # kéo chuột để bôi chọn
            self._ve_phien()
            return
        self._xong_phien(ap=True)
        if d is None:
            return
        if snd.co_muc_mau(self.anh_hien, (d.hop[0], d.dai[0], d.hop[2], d.dai[1])):
            messagebox.showwarning("Sửa PDF", "Dòng này có mực màu (con dấu, chữ ký, bút phê). Ứng dụng không cho sửa "
                                   "chữ đè lên con dấu, chữ ký để tránh làm sai lệch giấy tờ.", parent=self.w)
            return
        khac = [(v[1], v[2]) for j, v in sorted(self._dong_trang.items()) if j != self.hien_tai]
        self._phien = sk.PhienSuaDong(self.anh_hien, self.cac_dong, d, x, trang_khac=khac)
        self._keo = ("ky_tu", x)
        self._cap_nhat_phien()

    def _cap_nhat_phien(self):
        p = self._phien
        if not p:
            return
        tt = p.thao_tac()
        self.anh_xem = tt.ap(self.anh_hien) if p.da_doi else self.anh_hien
        chua_chac = sorted({m.chu for m in tt.manh if m.chua_chac and m.chu.strip()})
        nhan = ("Đang sửa dòng. ← → di chuyển, Backspace / Delete xóa, gõ để chèn; kéo chuột, Shift + ← → bôi chọn để "
                "đổi cỡ, phông ở khung Chữ; Enter để xong, Esc để hủy.")
        if chua_chac:
            nhan += (f" Ký tự {', '.join('“' + c + '”' for c in chua_chac)} chưa có mẫu tốt trên trang (viền vàng): "
                     "bấm chuột phải lên một ký tự đúng như vậy trên trang để dùng làm mẫu.")
        if self.cac_dong and p.vuot_le(max(d.hop[2] for d in self.cac_dong)):
            nhan += " CHÚ Ý: dòng đã dài quá lề phải."
        self.v_trang_thai.set(nhan)
        self._ve()
        self._hien_con_tro()

    def _hien_con_tro(self):
        """Cuộn khung nhìn cho con trỏ đang sửa luôn hiện ra (màn hình hẹp, phóng to)."""
        p = self._phien
        if not p:
            return
        vung = [float(v) for v in self.cv.cget("scrollregion").split()]
        if len(vung) < 4 or vung[2] <= 0:
            return
        xc, yc = self._ra_man(p.x_con_tro(), sum(p.dong.dai_tai(p.x_con_tro())) / 2)
        rong, cao = self.cv.winfo_width(), self.cv.winfo_height()
        trai, tren = self.cv.canvasx(0), self.cv.canvasy(0)
        if not (trai + 40 <= xc <= trai + rong - 40):
            self.cv.xview_moveto(max(0.0, (xc - rong / 2) / vung[2]))
        if not (tren + 30 <= yc <= tren + cao - 30):
            self.cv.yview_moveto(max(0.0, (yc - cao / 2) / vung[3]))

    def _ve_phien(self):
        """Dải dòng đang sửa, con trỏ, khung vàng quanh ký tự mẫu chưa chắc."""
        self.cv.delete("phien")
        p = self._phien
        if not p:
            return
        tt = p.thao_tac()
        if p.co_chon:
            a, b = p.x_doan_chon()
            self.cv.create_polygon(*self._khung_dong(p.dong, a, b), fill="#3d8bfd", stipple="gray25", outline="#3d8bfd",
                                   tags="phien")
        x = tt.x0
        for m in tt.manh:
            if m.chua_chac:
                self.cv.create_polygon(*self._khung_dong(p.dong, x, x + m.rong), fill="", outline="#f2b705", width=2,
                                       tags="phien")
            x += m.rong
        self.cv.create_polygon(*self._khung_dong(p.dong, p.x0 - 3, max(p.x1_cu, x) + 3), fill="", outline="#e07a00",
                               width=1, dash=(4, 2), tags="phien")
        xc = p.x_con_tro()
        t, b = p.dong.dai_tai(xc)
        self.cv.create_line(*self._ra_man(xc, t + 1), *self._ra_man(xc, b - 1), fill="#d0021b", width=2, tags="phien")

    def _phim(self, e):
        p = self._phien
        if not p:
            if self.v_cong_cu.get() == "chon":
                if (e.state & 0x4) and e.keysym.lower() == "v":
                    self.dan_doi_tuong()
                    return "break"
                return self._phim_doi_tuong(e)
            return None
        k = e.keysym
        if k in ("Return", "KP_Enter"):
            self._xong_phien(ap=True)
            return "break"
        if k == "Escape":
            self._xong_phien(ap=False)
            return "break"
        ctrl, shift = bool(e.state & 0x4), bool(e.state & 0x1)
        di = {"Left": p.trai, "Right": p.phai, "Home": p.dau_dong, "End": p.cuoi_dong}.get(k)
        viec = {"BackSpace": p.xoa_lui, "Delete": p.xoa_toi}.get(k)
        if di:
            di(chon=shift)
            if shift:
                self._hen_kieu_chon()
        elif viec:
            viec()
        elif ctrl and k.lower() == "a":
            p.chon_ca_dong()
            self._hen_kieu_chon()
        elif ctrl and k in ("bracketright", "bracketleft"):
            if p.co_chon:
                try:
                    co = float(self.v_co.get())
                except (ValueError, tk.TclError):
                    return "break"
                self.v_co.set(max(4.0, co + (1 if k == "bracketright" else -1)))  # áp qua theo dõi biến
            return "break"
        elif e.char and e.char.isprintable() and not ctrl:
            p.go(e.char)
        else:
            return None
        self._cap_nhat_phien()
        return "break"

    def _bam_phai(self, e):
        """Chuột phải lên một ký tự trên trang khi đang sửa dòng: dùng ký tự đó làm mẫu cho ký tự vừa chèn."""
        p = self._phien
        if not p or not self.cac_dong:
            return
        x, y = self._ra_anh(e)
        d = self._dong_tai(x, y)
        c = next((c for c in (d.ky_tu if d else []) if c.hop[0] - 1 <= x <= c.hop[2] + 1), None)
        if c is None:
            return
        chen = sorted({m.chu for m in p.manh if m.loai != "goc" and m.chu.strip()})
        if not chen:
            self.v_trang_thai.set("Chưa chèn ký tự nào để chọn mẫu.")
            return
        menu = tk.Menu(self.w, tearoff=0)
        for ch in chen:
            menu.add_command(label=f"Dùng ký tự này làm mẫu cho “{ch}”",
                             command=lambda ch=ch: (p.dat_mau(ch, self.anh_hien, d, c), self._cap_nhat_phien()))
        menu.tk_popup(e.x_root, e.y_root)

    def _hen_kieu_chon(self):
        """Bôi chọn xong (thả chuột, Shift + phím): một lúc sau mới đoán phông, cỡ của đoạn chọn để nạp lên khung Chữ."""
        if self._hen_kieu:
            self.w.after_cancel(self._hen_kieu)
        self._hen_kieu = self.w.after(250, self._nap_kieu_chon)

    def _nap_kieu_chon(self):
        """Nạp phông, kiểu, cỡ của đoạn chọn lên khung Chữ. Đoạn còn nét gốc thì Phông, Kiểu để "Tự đoán" (đổi cỡ là
        phóng, thu nét gốc), cỡ là cỡ đoán được nhân tỉ lệ đã đổi."""
        self._hen_kieu = None
        p = self._phien
        if not p or not p.co_chon:
            return
        k, tl, ve = p.kieu_doan_chon()
        f = snd.diem_anh_sang_pt(self.anh_hien.shape[1])
        self._nap_dinh_dang = True
        try:
            self.v_phong.set(k.ten if ve else "Tự đoán")
            self.v_kieu.set(snd.TEN_KIEU[k.kieu] if ve else "Tự đoán")
            self.v_co.set(round(k.co_px * tl * f * 2) / 2)
        finally:
            self._nap_dinh_dang = False
        a, b = p.doan_chon()
        doan = "".join(m.chu for m in p.manh[a:b])
        kieu = f"phông {k.ten} {snd.TEN_KIEU[k.kieu]}" if ve else f"nét gốc (giống {k.ten} {snd.TEN_KIEU[k.kieu]})"
        self.v_trang_thai.set(f"Đoạn chọn “{doan[:30]}”: {kieu}, khoảng {k.co_px * tl * f:.1f} pt. Đổi Cỡ (pt) để phóng, "
                              "thu nét gốc; chọn Phông, Kiểu để vẽ lại đoạn chọn bằng phông (soát lại chữ máy đọc).")

    def _ap_kieu_doan_chon(self):
        """Áp phông, kiểu, cỡ ở khung Chữ cho đoạn bôi chọn của dòng đang sửa."""
        p = self._phien
        if not p or not p.co_chon:
            return
        try:
            pt = float(self.v_co.get())
        except (ValueError, tk.TclError):
            return
        if pt < 2:
            return
        f = snd.diem_anh_sang_pt(self.anh_hien.shape[1])
        ten, kieu = self._phong_kieu(False)
        if ten is None and kieu is None:
            goc, _, _ = p.kieu_doan_chon(bo_phong=True)
            p.dinh_dang_chon(ti_le=pt / (goc.co_px * f))
        else:
            k, _, _ = p.kieu_doan_chon()
            p.dinh_dang_chon(kieu=snd.KieuChu(ten or k.ten, kieu or k.kieu, pt / f, k.mau, k.mo))
        self._cap_nhat_phien()

    def _xong_phien(self, ap: bool):
        p, self._phien = self._phien, None
        self.anh_xem = None
        if not p:
            return
        if ap and p.da_doi:
            tt = p.thao_tac()
            self._them_thao_tac(tt)
            self.v_trang_thai.set(f"Đã sửa: {tt.mo_ta()}")
        else:
            self._ve()
            self.v_trang_thai.set(GOI_Y[self.v_cong_cu.get()])

    # ------------------------------------------------------------------ sửa ngay trên trang
    def _bam_khoi(self, x, y):
        if self.cac_tu is None:
            self.v_trang_thai.set("Đang tìm chữ trên trang, chờ một chút…")
            return
        khoi = next((k for k in self.cac_khoi
                     if k.hop[0] - 4 <= x <= k.hop[2] + 4 and k.hop[1] - 4 <= y <= k.hop[3] + 4), None)
        if khoi is None:
            return
        if snd.co_muc_mau(self.anh_hien, khoi.hop):
            messagebox.showwarning("Sửa PDF", "Khối này có mực màu (con dấu, chữ ký, bút phê). Ứng dụng không cho sửa "
                                   "chữ đè lên con dấu, chữ ký để tránh làm sai lệch giấy tờ.", parent=self.w)
            return
        self._mo_o_sua("khoi", khoi=khoi)

    def _phong_kieu(self, mac_dinh: bool):
        ten = None if self.v_phong.get() == "Tự đoán" else self.v_phong.get()
        kieu = None if self.v_kieu.get() == "Tự đoán" else TEN_KIEU_NGUOC[self.v_kieu.get()]
        if mac_dinh:
            return ten or "Times New Roman", kieu or "thuong"
        return ten, kieu

    def _bam_dup(self, e):
        if self.anh_hien is not None and self.v_cong_cu.get() == "chon":
            x, y = self._ra_anh(e)
            self._keo = None
            self._chon_bam_dup(x, y)

    def _mo_o_sua(self, loai: str, khoi: snd.KhoiChu | None = None, x: float = 0, y: float = 0, tt_cu=None):
        """Mở ô gõ chữ đặt ngay trên trang: sửa một khối (cùng phông, cỡ, màu, căn lề đã đoán), thêm chữ mới, hoặc sửa
        chữ đã thêm (`tt_cu`)."""
        self._dong_sua(ap=True)
        W = self.anh_hien.shape[1]
        if loai == "khoi":
            tt = snd.chuan_bi_sua_khoi(khoi, khoi.chu, self.cac_tu)
            tt.ten, tt.kieu = self._phong_kieu(False)
            self.v_trang_thai.set("Đang đoán phông, cỡ chữ của khối…")
            self.w.update_idletasks()
            tt.doan(self.anh_hien)
            k = tt.kieu_chu
            L, T, R, B = khoi.hop
            if khoi.can == "giua":
                le = tt.le_trang or (L, R)
                rong = max(R - L, le[1] - le[0])
                x0 = (L + R) / 2 - rong / 2
            else:
                x0 = L
                rong = (max(R, tt.le_trang[1]) if tt.le_trang and khoi.can in ("trai", "deu") else R) - L
            ten, kieu, co_px, mau, buoc = k.ten, k.kieu, k.co_px, k.mau, tt.buoc
            chu, can, thut = khoi.chu, khoi.can, khoi.thut_dau if khoi.can in ("trai", "deu") else 0
            y0 = T - 0.2 * co_px
            mo_ta = k.mo_ta(W) + f", {snd.TEN_CAN[can]}"
        elif tt_cu is not None:
            ten, kieu, co_px, mau = tt_cu.ten, tt_cu.kieu, tt_cu.co_px, tt_cu.mau
            buoc, can, thut, chu, tt = co_px * 1.25, "trai", 0, tt_cu.chu, tt_cu
            x0, y0 = x, y
            rong = max(W * 0.3, W - x - W * 0.05)
            mo_ta = f"{ten} {snd.TEN_KIEU[kieu]}, {co_px * snd.diem_anh_sang_pt(W):.1f} pt"
        else:
            ten, kieu = self._phong_kieu(True)
            co_px = float(self.v_co.get()) / snd.diem_anh_sang_pt(W)
            mau, buoc, can, thut, chu, tt, khoi = self.mau_chu, co_px * 1.25, "trai", 0, "", None, None
            x0, y0 = x, y
            rong = max(W * 0.3, W - x - W * 0.05)
            mo_ta = f"{ten} {snd.TEN_KIEU[kieu]}, {float(self.v_co.get()):.1f} pt"
        b, g, r = mau
        phong = tkfont.Font(family=ten, size=-max(6, round(co_px * self.ty_le)),
                            weight="bold" if "dam" in kieu else "normal", slant="italic" if "nghieng" in kieu else "roman")
        o = tk.Text(self.cv, wrap="word", font=phong, fg=f"#{r:02x}{g:02x}{b:02x}", bg="white", bd=0, padx=2, pady=0,
                    highlightthickness=2, highlightcolor="#e07a00", highlightbackground="#e07a00", undo=True)
        o.insert("1.0", chu)
        o.tag_add("can", "1.0", "end")
        o.tag_configure("can", justify={"giua": "center", "phai": "right"}.get(can, "left"))
        thanh = ttk.Frame(self.cv)
        ttk.Button(thanh, text="✓ Áp dụng (Ctrl+Enter)", command=lambda: self._dong_sua(ap=True)).pack(side="left")
        ttk.Button(thanh, text="✕ Hủy (Esc)", command=lambda: self._dong_sua(ap=False)).pack(side="left", padx=4)
        ttk.Label(thanh, text=mo_ta, foreground="#555").pack(side="left", padx=6)
        self._sua = {"loai": loai, "khoi": khoi, "tt": tt, "x": x0, "y": y0, "rong": rong, "co_px": co_px,
                     "buoc": buoc, "thut": thut, "phong": phong, "o": o, "thanh": thanh, "chu_dau": chu,
                     "ten": ten, "kieu": kieu, "mau": mau, "tt_cu": tt_cu}
        o.bind("<Control-Return>", lambda _e: (self._dong_sua(ap=True), "break")[1])
        o.bind("<Escape>", lambda _e: (self._dong_sua(ap=False), "break")[1])
        # chữ gõ thêm ở cuối không tự nhận thẻ căn lề: gắn lại sau mỗi phím
        o.bind("<KeyRelease>", lambda _e: (o.tag_add("can", "1.0", "end"), self._dat_o_sua(chi_cao=True)))
        self._ve_tu()
        self._dat_o_sua()
        o.focus_set()
        o.mark_set("insert", "end-1c")
        self.v_trang_thai.set(("Đang sửa khối: " if loai == "khoi" else "Thêm chữ: ") + mo_ta +
                              ". Gõ ngay trên trang; Ctrl+Enter hoặc bấm ra ngoài để áp, Esc để hủy.")

    def _dat_o_sua(self, chi_cao: bool = False):
        """Đặt (lại) ô sửa đúng chỗ, đúng cỡ theo tỉ lệ phóng hiện tại; cao theo số dòng đang gõ."""
        sd = self._sua
        if not sd:
            return
        s = self.ty_le
        o = sd["o"]
        if not chi_cao:
            sd["phong"].configure(size=-max(6, round(sd["co_px"] * s)))
            them = max(0, round(sd["buoc"] * s - sd["phong"].metrics("linespace")))
            o.configure(spacing2=them, spacing3=them)
            o.tag_configure("can", lmargin1=round(sd["thut"] * s))
        x, y = self._ra_man(sd["x"], sd["y"])
        rong = sd["rong"] * s + 8
        self.w.update_idletasks()
        try:
            so_dong = int(o.count("1.0", "end", "displaylines")[0] or 1)
        except (tk.TclError, TypeError):
            so_dong = 1
        cao = max(1, so_dong) * sd["buoc"] * s + 10
        if chi_cao and self.cv.find_withtag("o_sua"):
            self.cv.itemconfigure("o_sua_o", height=cao)
            self.cv.coords("o_sua_thanh", x - 4, y - 4 + cao + 4)
            return
        self.cv.delete("o_sua")
        self.cv.create_window(x - 4, y - 4, window=o, anchor="nw", width=rong, height=cao, tags=("o_sua", "o_sua_o"))
        self.cv.create_window(x - 4, y - 4 + cao + 4, window=sd["thanh"], anchor="nw", tags=("o_sua", "o_sua_thanh"))

    def _dong_sua(self, ap: bool):
        """Đóng ô sửa; `ap`: chữ đã đổi thì thêm thao tác sửa khối / thêm chữ."""
        sd, self._sua = self._sua, None
        if not sd:
            return
        chu = sd["o"].get("1.0", "end-1c")
        self.cv.delete("o_sua")
        sd["o"].destroy()
        sd["thanh"].destroy()
        self._ve_tu()
        if sd.get("tt_cu") is not None and ap and chu.strip() != sd["chu_dau"].strip():
            # sửa chữ đã thêm: đổi nội dung (xóa hết chữ là xóa đối tượng)
            ds = self.tl.trang[self.hien_tai].thao_tac
            if chu.strip():
                sd["tt_cu"].chu = chu.strip("\n")
            elif sd["tt_cu"] in ds:
                ds.remove(sd["tt_cu"])
                self.dang_chon = None
            self._sau_khi_doi(self.hien_tai)
            return
        if not ap or not chu.strip() or chu.strip() == sd["chu_dau"].strip():
            self.v_trang_thai.set(GOI_Y[self.v_cong_cu.get()])
            return
        W = self.anh_hien.shape[1]
        if sd["loai"] == "them":
            _, t, _, _ = snd.khung_chu("Ắ", sd["ten"], sd["kieu"], sd["co_px"])
            self._them_thao_tac(snd.ThemChu((sd["x"], sd["y"] - t), chu.strip("\n"), sd["ten"], sd["kieu"], sd["co_px"], sd["mau"]))
            return
        tt = sd["tt"]
        tt.chu_moi = chu.strip()
        self._them_thao_tac(tt)
        nhan = f"Đã sửa khối ({tt.so_dong_moi} dòng): {tt.kieu_chu.mo_ta(W)}"
        if tt.lech_duoi:
            nhan += f" · phần trang bên dưới đã dời {'xuống' if tt.lech_duoi > 0 else 'lên'} {abs(tt.lech_duoi)} điểm ảnh"
            day = max((t.hop[3] for t in (self.cac_tu or [])), default=0)
            if tt.lech_duoi > 0 and day + tt.lech_duoi > self.anh_hien.shape[0] - 4:
                nhan += " · CHÚ Ý: chữ cuối trang có thể bị đẩy ra ngoài, nên rút ngắn."
        self.v_trang_thai.set(nhan)

    def _them_thao_tac(self, tt):
        i = self.hien_tai
        if i is None:
            return
        self.tl.trang[i].thao_tac.append(tt)
        self.lam_lai.pop(i, None)
        self._sau_khi_doi(i)

    def _sau_khi_doi(self, i):
        y = self.cv.yview()[0]
        self._dung_lai_anh()
        self.cv.yview_moveto(y)
        self._cap_nhat_nho(i)

    def _cap_nhat_nho(self, i):
        t = self.tl.trang[i]
        try:
            nho = self.tl.anh_nho(i, CO_ANH_NHO)
            self.anh_nho[i] = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(nho, cv2.COLOR_BGR2RGB)))
        except Exception:
            pass
        self.ds.item(str(i), image=self.anh_nho.get(i) or "",
                     text=f"  {i + 1}. {t.ten}" + ("\n  ✏ đã sửa nội dung" if t.da_sua or t.da_gop else "") + (f"\n  ⟳ {t.xoay}°" if t.xoay else ""))

    def hoan_tac(self):
        i = self.hien_tai
        if i is not None and self.tl.trang[i].thao_tac:
            self.lam_lai.setdefault(i, []).append(self.tl.trang[i].thao_tac.pop())
            self.dang_chon = None
            self._sau_khi_doi(i)

    def xoa_thao_tac(self):
        i = self.hien_tai
        chon = self.ds_thao_tac.curselection()
        if i is None or not chon:
            return
        del self.tl.trang[i].thao_tac[chon[0]]
        self._sau_khi_doi(i)

    def _chon_mau(self):
        b, g, r = self.mau_chu
        kq = colorchooser.askcolor(color=f"#{r:02x}{g:02x}{b:02x}", parent=self.w, title="Màu chữ")
        if kq and kq[0]:
            r, g, b = (int(v) for v in kq[0])
            self.mau_chu = (b, g, r)
            self.nut_mau.configure(bg=kq[1], fg="white" if r + g + b < 380 else "black")
            self._ap_dinh_dang_chon()

    def _chon_anh_chen(self):
        tep = filedialog.askopenfilename(parent=self.w, title="Chọn ảnh chữ ký, con dấu",
                                         filetypes=[("Ảnh", "*.png *.jpg *.jpeg *.bmp *.webp"), ("Mọi tệp", "*.*")])
        if tep:
            self.anh_chen = Path(tep).read_bytes()
            self.nhan_anh_chen.configure(text=Path(tep).name)
            self.v_cong_cu.set("chen_anh")
            self._doi_cong_cu()

    def _ty_le_anh_chen(self) -> float:
        import io
        with Image.open(io.BytesIO(self.anh_chen)) as img:
            return img.height / img.width

    # ------------------------------------------------------------------ thao tác trang
    def them_tep(self):
        tep = filedialog.askopenfilenames(parent=self.w, title="Mở, thêm PDF hoặc ảnh",
                                          filetypes=[("PDF, ảnh", "*.pdf *.png *.jpg *.jpeg *.tif *.tiff *.bmp *.webp *.heic"), ("Mọi tệp", "*.*")])
        if tep:
            self._them_cac_tep(tep)

    def _them_cac_tep(self, cac_tep, vi_tri: int | None = None):
        chon = self._chon_ds()
        if vi_tri is None:
            vi_tri = chon[-1] + 1 if chon else len(self.tl.trang)
        dau = vi_tri
        for tep in cac_tep:
            try:
                vi_tri += self.tl.mo_tep(tep, vi_tri)
            except Exception as e:
                messagebox.showerror("Sửa PDF", f"Không mở được {Path(tep).name}: {e}", parent=self.w)
        self._lam_moi_ds(list(range(dau, vi_tri)))
        if vi_tri > dau:
            self.chon_trang(dau)
            self.v_trang_thai.set(f"Đã thêm {vi_tri - dau} trang. Tổng {len(self.tl.trang)} trang.")

    def them_trang_trang(self):
        chon = self._chon_ds()
        vi_tri = chon[-1] + 1 if chon else len(self.tl.trang)
        self.tl.them_trang_trang(vi_tri)
        self._lam_moi_ds([vi_tri])
        self.chon_trang(vi_tri)

    def xoay(self, goc):
        chon = self._chon_ds()
        if not chon:
            return
        if any(self.tl.trang[i].da_sua for i in chon) and not messagebox.askyesno(
                "Sửa PDF", "Trang đã sửa nội dung sẽ được gộp các thao tác vào ảnh trước khi xoay "
                           "(không hoàn tác từng thao tác được nữa). Tiếp tục?", parent=self.w):
            return
        for i in chon:
            self.tl.xoay(i, goc)
        self._lam_moi_ds(chon)
        self.chon_trang(chon[0], cap_nhat_ds=False)

    def dich(self, buoc):
        chon = self._chon_ds()
        if not chon:
            return
        n = len(self.tl.trang)
        if (buoc < 0 and chon[0] == 0) or (buoc > 0 and chon[-1] == n - 1):
            return
        for i in (chon if buoc < 0 else reversed(chon)):
            self.tl.doi_cho(i, i + buoc)
        moi = [i + buoc for i in chon]
        self._lam_moi_ds(moi)
        self.hien_tai = moi[0]
        self.ds.see(str(moi[0]))

    def xoa_trang(self):
        chon = self._chon_ds()
        if not chon or not messagebox.askyesno("Sửa PDF", f"Xóa {len(chon)} trang đã chọn khỏi tài liệu?", parent=self.w):
            return
        self.tl.xoa(chon)
        self._lam_moi_ds()
        if self.tl.trang:
            self.chon_trang(min(chon[0], len(self.tl.trang) - 1))

    def luu(self, chi_chon: bool):
        if not self.tl.trang:
            return
        chi_so = self._chon_ds() if chi_chon else None
        if chi_chon and not chi_so:
            messagebox.showinfo("Sửa PDF", "Chọn các trang cần tách trong danh sách bên trái.", parent=self.w)
            return
        tep = filedialog.asksaveasfilename(parent=self.w, title="Lưu PDF", defaultextension=".pdf",
                                           filetypes=[("PDF", "*.pdf")], initialfile="tai-lieu-da-sua.pdf")
        if not tep:
            return
        ocr = self.v_ocr.get()
        sua = self.tl.tom_tat_sua(chi_so)

        def lam():
            try:
                self.tl.luu(tep, chi_so, ocr=ocr, bao_tien_trinh=lambda k, n, s: self.hang.put(("luu", f"Đang lưu: {s}")))
                self.hang.put(("luu_xong", tep, sua))
            except Exception as e:
                self.hang.put(("luu_loi", str(e)))
        self.v_trang_thai.set("Đang lưu…")
        threading.Thread(target=lam, daemon=True).start()


def mo_cua_so(cha: tk.Misc, tai_lieu: TaiLieu | None = None) -> CuaSoSuaPdf:
    return CuaSoSuaPdf(tk.Toplevel(cha), tai_lieu)


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    goc = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    kieu = ttk.Style(goc)
    if "vista" in kieu.theme_names():
        kieu.theme_use("vista")
    tl = TaiLieu()
    for tep in sys.argv[1:]:
        try:
            tl.mo_tep(tep)
        except Exception as e:
            print(f"Không mở được {tep}: {e}", file=sys.stderr)
    CuaSoSuaPdf(goc, tl)
    goc.mainloop()


if __name__ == "__main__":
    main()
