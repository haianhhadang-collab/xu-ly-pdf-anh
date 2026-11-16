"""Thao tác trang kiểu ONLYOFFICE cho cửa sổ Sửa PDF: kéo thả ảnh trang để đổi thứ tự, menu chuột phải trên ảnh trang
(xoay, chèn trang trắng trước / sau, nhân đôi, chép, cắt, dán, chèn tệp, lưu ra tệp mới, xóa), Ctrl+C / Ctrl+X / Ctrl+V
chép, cắt, dán trang, kể cả giữa hai cửa sổ Sửa PDF (hai tệp) đang mở. Lớp trộn (mixin) dùng trong CuaSoSuaPdf."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog

BO_NHO_TRANG: list = []  # trang đã chép (dùng chung mọi cửa sổ Sửa PDF trong cùng chương trình)


class TrangMixin:
    def _khoi_tao_trang(self):
        self._keo_trang = None
        self._vach = tk.Frame(self.ds, height=3, bg="#e07a00")
        d = self.ds
        d.bind("<ButtonPress-1>", self._trang_bam, add="+")
        d.bind("<B1-Motion>", self._trang_keo, add="+")
        d.bind("<ButtonRelease-1>", self._trang_tha, add="+")
        d.bind("<Button-3>", self._menu_trang)
        d.bind("<Control-c>", lambda _e: self.chep_trang())
        d.bind("<Control-x>", lambda _e: self.chep_trang(cat=True))
        d.bind("<Control-v>", lambda _e: self.dan_trang(sau=True))
        d.bind("<Delete>", lambda _e: self.xoa_trang())

    # ------------------------------------------------------------------ kéo thả đổi thứ tự
    def _trang_bam(self, e):
        hang = self.ds.identify_row(e.y)
        if not hang:
            self._keo_trang = None
            return
        truoc = self._chon_ds()  # gắn ở widget nên chạy trước lớp Treeview: còn thấy các trang đã chọn từ trước
        i = int(hang)
        self._keo_trang = {"y": e.y, "trang": truoc if i in truoc and not e.state & 0x5 else [i], "dang": False}

    def _vi_tri_tha(self, y) -> int:
        hang = self.ds.identify_row(y)
        if not hang:
            return len(self.tl.trang) if y > 10 else 0
        x, y0, w, h = self.ds.bbox(hang)
        return int(hang) + (1 if y > y0 + h / 2 else 0)

    def _trang_keo(self, e):
        k = self._keo_trang
        if not k or (not k["dang"] and abs(e.y - k["y"]) < 8):
            return
        k["dang"] = True
        den = self._vi_tri_tha(e.y)
        if den < len(self.tl.trang):
            vach_y = self.ds.bbox(str(den))[1] if self.ds.bbox(str(den)) else 0
        else:
            cuoi = self.ds.bbox(str(len(self.tl.trang) - 1))
            vach_y = cuoi[1] + cuoi[3] if cuoi else 0
        self._vach.place(x=0, y=max(0, vach_y - 1), relwidth=1)
        self._vach.lift()
        self.ds.configure(cursor="sb_v_double_arrow")
        self.v_trang_thai.set(f"Thả để đưa {len(k['trang'])} trang tới vị trí {den + 1}.")
        if e.y < 20:
            self.ds.yview_scroll(-1, "units")
        elif e.y > self.ds.winfo_height() - 20:
            self.ds.yview_scroll(1, "units")

    def _trang_tha(self, e):
        k, self._keo_trang = self._keo_trang, None
        self._vach.place_forget()
        self.ds.configure(cursor="")
        if not k or not k["dang"]:
            return
        den = self._vi_tri_tha(e.y)
        chon = k["trang"]
        if chon[0] <= den <= chon[-1] + 1 and chon == list(range(chon[0], chon[-1] + 1)):
            self.ds.selection_set([str(i) for i in chon])
            return  # thả ngay tại chỗ
        moi = self.tl.di_chuyen(chon, den)
        self._lam_moi_ds(moi)
        self.chon_trang(moi[0], cap_nhat_ds=False)
        self.ds.see(str(moi[0]))
        self.v_trang_thai.set(f"Đã chuyển {len(moi)} trang tới vị trí {moi[0] + 1}.")

    # ------------------------------------------------------------------ menu chuột phải
    def _menu_trang(self, e):
        hang = self.ds.identify_row(e.y)
        if hang and hang not in self.ds.selection():
            self.ds.selection_set(hang)
            self._khi_chon_ds()
        chon = self._chon_ds()
        co = "normal" if chon else "disabled"
        n = len(chon)
        m = tk.Menu(self.ds, tearoff=False)
        m.add_command(label=f"Xoay phải 90° ({n} trang)" if n > 1 else "Xoay phải 90°", state=co, command=lambda: self.xoay(90))
        m.add_command(label="Xoay trái 90°", state=co, command=lambda: self.xoay(-90))
        m.add_command(label="Xoay 180°", state=co, command=lambda: self.xoay(180))
        m.add_separator()
        m.add_command(label="Chèn trang trắng trước", state=co, command=lambda: self.chen_trang_trang(sau=False))
        m.add_command(label="Chèn trang trắng sau", command=lambda: self.chen_trang_trang(sau=True))
        m.add_command(label="Chèn tệp PDF, ảnh trước…", state=co, command=lambda: self.chen_tep(sau=False))
        m.add_command(label="Chèn tệp PDF, ảnh sau…", command=lambda: self.chen_tep(sau=True))
        m.add_separator()
        m.add_command(label="Nhân đôi trang", state=co, command=self.nhan_doi_trang)
        m.add_command(label="Chép trang  (Ctrl+C)", state=co, command=self.chep_trang)
        m.add_command(label="Cắt trang  (Ctrl+X)", state=co, command=lambda: self.chep_trang(cat=True))
        dan = "normal" if BO_NHO_TRANG else "disabled"
        m.add_command(label=f"Dán {len(BO_NHO_TRANG)} trang trước" if BO_NHO_TRANG else "Dán trang trước", state=dan,
                      command=lambda: self.dan_trang(sau=False))
        m.add_command(label="Dán trang sau  (Ctrl+V)", state=dan, command=lambda: self.dan_trang(sau=True))
        m.add_separator()
        m.add_command(label="Lưu trang đã chọn ra tệp mới…", state=co, command=lambda: self.luu(chi_chon=True))
        m.add_command(label="Xóa trang  (Delete)", state=co, command=self.xoa_trang)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    # ------------------------------------------------------------------ các lệnh
    def _vi_tri_chen(self, sau: bool) -> int:
        chon = self._chon_ds()
        if not chon:
            return len(self.tl.trang)
        return chon[-1] + 1 if sau else chon[0]

    def chen_trang_trang(self, sau: bool = True):
        self._dong_sua(ap=True)
        self._xong_phien(ap=True)
        chon = self._chon_ds()
        vt = self._vi_tri_chen(sau)
        kho = self.tl.trang[chon[0]].kho_ra if chon else None  # cùng khổ, cùng chiều với trang bên cạnh
        if kho:
            self.tl.them_trang_trang(vt, kho_pt=kho)
        else:
            self.tl.them_trang_trang(vt)
        self._lam_moi_ds([vt])
        self.chon_trang(vt)

    def chen_tep(self, sau: bool = True):
        tep = filedialog.askopenfilenames(parent=self.w, title="Chèn PDF hoặc ảnh",
                                          filetypes=[("PDF, ảnh", "*.pdf *.png *.jpg *.jpeg *.tif *.tiff *.bmp *.webp *.heic"),
                                                     ("Mọi tệp", "*.*")])
        if tep:
            self._them_cac_tep(tep, self._vi_tri_chen(sau))

    def nhan_doi_trang(self):
        chon = self._chon_ds()
        if not chon:
            return
        self._dong_sua(ap=True)
        self._xong_phien(ap=True)
        moi = self.tl.dan(self.tl.chep(chon), chon[-1] + 1)
        self._lam_moi_ds(moi)
        self.chon_trang(moi[0], cap_nhat_ds=False)
        self.v_trang_thai.set(f"Đã nhân đôi {len(moi)} trang.")

    def chep_trang(self, cat: bool = False):
        chon = self._chon_ds()
        if not chon:
            return "break"
        self._dong_sua(ap=True)
        self._xong_phien(ap=True)
        BO_NHO_TRANG[:] = self.tl.chep(chon)
        if cat:
            self.tl.xoa(chon)
            self._lam_moi_ds()
            if self.tl.trang:
                self.chon_trang(min(chon[0], len(self.tl.trang) - 1))
        self.v_trang_thai.set(f"Đã {'cắt' if cat else 'chép'} {len(chon)} trang. Ctrl+V để dán sau trang đang chọn "
                              "(dán được sang cửa sổ Sửa PDF khác).")
        return "break"

    def dan_trang(self, sau: bool = True):
        if not BO_NHO_TRANG:
            return "break"
        moi = self.tl.dan(BO_NHO_TRANG, self._vi_tri_chen(sau))
        self._lam_moi_ds(moi)
        self.chon_trang(moi[0], cap_nhat_ds=False)
        self.ds.see(str(moi[0]))
        self.v_trang_thai.set(f"Đã dán {len(moi)} trang vào vị trí {moi[0] + 1}.")
        return "break"
