"""Công cụ "Chọn, dời" của cửa sổ Sửa PDF: chọn đối tượng (chữ thêm, ảnh chèn, khung che, tô sáng, hình vẽ, vùng đã
dời) hoặc vùng có sẵn trên bản scan; kéo để dời, kéo ô vuông ở góc, cạnh để đổi cỡ, Delete để xóa, mũi tên để nhích,
Ctrl+C / Ctrl+V để nhân bản, bấm đúp vào chữ thêm để sửa chữ; đổi phông, kiểu, cỡ, màu ở khung Chữ áp ngay cho chữ đang
chọn. Cách làm tham khảo trình sửa PDF ONLYOFFICE (không dùng mã của họ). Lõi: loi_xu_ly/doi_tuong.py.
Lớp trộn (mixin) dùng trong CuaSoSuaPdf (sua_pdf.py)."""
from __future__ import annotations

import copy

from tkinter import messagebox

from loi_xu_ly import chu_thich as ct_
from loi_xu_ly import doi_tuong as dt
from loi_xu_ly import sua_noi_dung as snd

CO_NUM = 5  # nửa cạnh ô vuông kéo đổi cỡ (điểm màn hình)


class DoiTuongMixin:
    # trạng thái (khởi tạo trong _khoi_tao_doi_tuong)
    def _khoi_tao_doi_tuong(self):
        self.cac_vung: list | None = None   # [(khung, bị khóa)] vùng có sẵn trên ảnh đang hiện
        self.dang_chon = None               # ("tt", chỉ số thao tác) | ("vung", khung)
        self._ban_sao = None                # đối tượng đã chép (Ctrl+C)
        self.lam_lai: dict[int, list] = {}  # thao tác đã hoàn tác của từng trang (để làm lại)

    # ------------------------------------------------------------------ tìm, vẽ
    def _doi_tuong_trang(self):
        """[(chỉ số thao tác, khung)] các đối tượng của trang đang hiện, trên cùng (thêm sau) đứng trước."""
        if self.hien_tai is None:
            return []
        kq = []
        for i, tt in enumerate(self.tl.trang[self.hien_tai].thao_tac):
            if dt.la_doi_tuong(tt):
                kq.append((i, dt.khung(tt)))
        return kq[::-1]

    def _tim_vung(self):
        if self.cac_vung is None and self.anh_hien is not None:
            # tìm trên bản scan (đã sửa ký tự, đã dời vùng) nhưng chưa có chữ thêm, hình, ảnh chèn…: các thứ ấy là đối
            # tượng riêng, không được gộp vào vùng của bản scan
            phu = (snd.ThemChu, snd.ChenAnh, snd.Che, snd.ToSang, dt.HinhVe, ct_.ChuThich)
            ds = self.tl.trang[self.hien_tai].thao_tac
            anh = self.anh_hien
            if any(isinstance(tt, phu) for tt in ds):
                anh = snd.ap_tat_ca(self.tl.anh_nen(self.hien_tai), [tt for tt in ds if not isinstance(tt, phu)])
            self.cac_vung = dt.tim_vung(anh)
        return self.cac_vung or []

    def _khung_dang_chon(self):
        c = self.dang_chon
        if not c:
            return None
        if c[0] == "tt":
            tt = self.tl.trang[self.hien_tai].thao_tac[c[1]]
            return dt.khung(tt)
        return c[1]

    def _ve_doi_tuong(self):
        self.cv.delete("dt")
        if self.v_cong_cu.get() != "chon" or self.anh_hien is None:
            return
        for hop, khoa in self._tim_vung():
            a0, b0 = self._ra_man(hop[0], hop[1])
            a1, b1 = self._ra_man(hop[2], hop[3])
            self.cv.create_rectangle(a0 - 2, b0 - 2, a1 + 2, b1 + 2, outline="#d0021b" if khoa else "#8aa4bd",
                                     dash=(2, 3), tags="dt")
        for _, hop in self._doi_tuong_trang():
            a0, b0 = self._ra_man(hop[0], hop[1])
            a1, b1 = self._ra_man(hop[2], hop[3])
            self.cv.create_rectangle(a0, b0, a1, b1, outline="#7b4fd6", tags="dt")
        hop = self._khung_dang_chon()
        if hop:
            a0, b0 = self._ra_man(hop[0], hop[1])
            a1, b1 = self._ra_man(hop[2], hop[3])
            self.cv.create_rectangle(a0, b0, a1, b1, outline="#e07a00", width=2, tags="dt")
            for (px, py) in self._cac_nut(a0, b0, a1, b1).values():
                self.cv.create_rectangle(px - CO_NUM, py - CO_NUM, px + CO_NUM, py + CO_NUM, fill="white",
                                         outline="#e07a00", tags="dt")

    @staticmethod
    def _cac_nut(a0, b0, a1, b1):
        am, bm = (a0 + a1) / 2, (b0 + b1) / 2
        return {"tt": (a0, b0), "t": (am, b0), "tp": (a1, b0), "p": (a1, bm), "dp": (a1, b1), "d": (am, b1),
                "dt": (a0, b1), "tr": (a0, bm)}

    # ------------------------------------------------------------------ chuột
    def _chon_bam(self, e, x, y):
        self.cv.focus_set()
        # 1) ô kéo đổi cỡ của đối tượng đang chọn
        hop = self._khung_dang_chon()
        if hop:
            a0, b0 = self._ra_man(hop[0], hop[1])
            a1, b1 = self._ra_man(hop[2], hop[3])
            mx, my = self.cv.canvasx(e.x), self.cv.canvasy(e.y)
            for ten, (px, py) in self._cac_nut(a0, b0, a1, b1).items():
                if abs(mx - px) <= CO_NUM + 2 and abs(my - py) <= CO_NUM + 2:
                    self._keo = ("dt_co", ten, hop, x, y)
                    return
        # 2) đối tượng (trên cùng trước), 3) vùng có sẵn, 4) kéo khung chọn vùng tùy ý
        for i, h in self._doi_tuong_trang():
            if h[0] - 3 <= x <= h[2] + 3 and h[1] - 3 <= y <= h[3] + 3:
                self.dang_chon = ("tt", i)
                self._keo = ("dt_doi", h, x, y)
                self._bao_chon()
                self._ve_doi_tuong()
                return
        for h, khoa in self._tim_vung():
            if h[0] - 2 <= x <= h[2] + 2 and h[1] - 2 <= y <= h[3] + 2:
                if khoa:
                    self.dang_chon = None
                    self.v_trang_thai.set("Vùng này có mực màu (con dấu, chữ ký, bút phê): khóa, không dời, không xóa "
                                          "để tránh làm sai lệch giấy tờ.")
                    self._ve_doi_tuong()
                    return
                self.dang_chon = ("vung", h)
                self._keo = ("dt_doi", h, x, y)
                self._bao_chon()
                self._ve_doi_tuong()
                return
        self.dang_chon = None
        self._keo = ("dt_khung", x, y, self.cv.create_rectangle(e.x, e.y, e.x, e.y, outline="#e07a00", dash=(4, 2)))
        self._ve_doi_tuong()

    def _chon_keo(self, e) -> bool:
        k = self._keo
        if not k or k[0] not in ("dt_doi", "dt_co", "dt_khung"):
            return False
        x, y = self._ra_anh(e)
        if k[0] == "dt_khung":
            a0, b0 = self._ra_man(k[1], k[2])
            a1, b1 = self._ra_man(x, y)
            self.cv.coords(k[3], a0, b0, a1, b1)
            self._keo = k[:4] + (x, y)
            return True
        moi = self._khung_moi(k, x, y)
        self.cv.delete("dt_xem")
        a0, b0 = self._ra_man(moi[0], moi[1])
        a1, b1 = self._ra_man(moi[2], moi[3])
        self.cv.create_rectangle(a0, b0, a1, b1, outline="#e07a00", dash=(5, 3), width=2, tags="dt_xem")
        self._keo = k[:5] + (x, y) if k[0] == "dt_co" else k[:4] + (x, y)
        return True

    @staticmethod
    def _khung_moi(k, x, y):
        if k[0] == "dt_doi":
            h, x0, y0 = k[1], k[2], k[3]
            dx, dy = round(x - x0), round(y - y0)
            return h[0] + dx, h[1] + dy, h[2] + dx, h[3] + dy
        ten, h = k[1], k[2]
        x0, y0, x1, y1 = h
        if "t" in ten[:1] and ten != "tr":
            y0 = round(y)
        if ten.startswith("d"):
            y1 = round(y)
        if ten in ("tp", "p", "dp"):
            x1 = round(x)
        if ten in ("tt", "tr", "dt"):
            x0 = round(x)
        return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)

    def _chon_tha(self) -> bool:
        k, self._keo = self._keo, None
        if not k or k[0] not in ("dt_doi", "dt_co", "dt_khung"):
            self._keo = k
            return False
        self.cv.delete("dt_xem")
        if k[0] == "dt_khung":
            self.cv.delete(k[3])
            if len(k) < 6:
                return True
            hop = (round(min(k[1], k[4])), round(min(k[2], k[5])), round(max(k[1], k[4])), round(max(k[2], k[5])))
            if hop[2] - hop[0] < 5 or hop[3] - hop[1] < 5:
                return True
            if snd.co_muc_mau(self.anh_hien, hop):
                self.v_trang_thai.set("Vùng chọn có mực màu (con dấu, chữ ký): khóa, không dời, không xóa.")
                return True
            self.dang_chon = ("vung", hop)
            self._bao_chon()
            self._ve_doi_tuong()
            return True
        if len(k) < (7 if k[0] == "dt_co" else 6):
            return True  # bấm không kéo
        moi = self._khung_moi(k, k[-2], k[-1])
        self._dat_khung_chon(moi, doi_cho=k[0] == "dt_doi")
        return True

    def _dat_khung_chon(self, moi, doi_cho: bool):
        """Dời / đổi cỡ thứ đang chọn tới khung `moi`: đối tượng thì sửa thao tác, vùng có sẵn thì thêm thao tác dời vùng."""
        c = self.dang_chon
        if not c or self.hien_tai is None:
            return
        if c[0] == "tt":
            tt = self.tl.trang[self.hien_tai].thao_tac[c[1]]
            cu = dt.khung(tt)
            if doi_cho:
                dt.doi(tt, moi[0] - cu[0], moi[1] - cu[1])
            else:
                dt.dat_khung(tt, moi)
            self.lam_lai.pop(self.hien_tai, None)
            self._sau_khi_doi(self.hien_tai)
        else:
            vung = dt.DoiVung(c[1], moi)
            self._them_thao_tac(vung)
            self.dang_chon = ("tt", len(self.tl.trang[self.hien_tai].thao_tac) - 1)
        self._bao_chon()
        self._ve_doi_tuong()

    def _bao_chon(self):
        c = self.dang_chon
        if not c:
            return
        if c[0] == "tt":
            tt = self.tl.trang[self.hien_tai].thao_tac[c[1]]
            nhan = f"Đang chọn: {tt.mo_ta()}. Kéo để dời, kéo ô vuông để đổi cỡ, Delete để xóa, mũi tên để nhích"
            if isinstance(tt, (ct_.GhiChu, ct_.ButPhe)):
                nhan += ", bấm đúp để sửa lời"
            if isinstance(tt, snd.ThemChu):
                nhan += ", bấm đúp để sửa chữ; đổi phông, cỡ, màu ở khung Chữ"
                self._nap_dinh_dang = True
                try:
                    self.v_phong.set(tt.ten)
                    self.v_kieu.set(snd.TEN_KIEU[tt.kieu])
                    self.v_co.set(round(tt.co_px * snd.diem_anh_sang_pt(self.anh_hien.shape[1]) * 2) / 2)
                    self.mau_chu = tt.mau
                    b, g, r = tt.mau
                    self.nut_mau.configure(bg=f"#{r:02x}{g:02x}{b:02x}", fg="white" if r + g + b < 380 else "black")
                finally:
                    self._nap_dinh_dang = False
        else:
            nhan = ("Đang chọn vùng trên bản scan. Kéo để dời, kéo ô vuông để đổi cỡ, Delete để xóa (vá nền chỗ cũ); "
                    "nét gốc giữ nguyên")
        self.v_trang_thai.set(nhan + ".")

    def _chon_bam_dup(self, x, y):
        """Bấm đúp vào chữ đã thêm: mở ô sửa chữ đặt ngay trên trang; vào ghi chú, bút phê: sửa lời."""
        for i, h in self._doi_tuong_trang():
            tt = self.tl.trang[self.hien_tai].thao_tac[i]
            if isinstance(tt, (ct_.GhiChu, ct_.ButPhe)) and h[0] <= x <= h[2] and h[1] <= y <= h[3]:
                self.dang_chon = ("tt", i)
                nd = self._hoi_noi_dung(tt.ten, tt.noi_dung)
                if nd and nd != tt.noi_dung:
                    tt.noi_dung = nd
                    if isinstance(tt, ct_.ButPhe):
                        tt.hop = (tt.hop[0], tt.hop[1], tt.hop[2], max(tt.hop[3], tt.hop[1] + tt.chieu_cao_vua()))
                    self._sau_khi_doi(self.hien_tai)
                    self._ve_doi_tuong()
                return
            if isinstance(tt, snd.ThemChu) and h[0] <= x <= h[2] and h[1] <= y <= h[3]:
                self.dang_chon = ("tt", i)
                self._mo_o_sua("them", x=h[0], y=h[1], tt_cu=tt)
                return

    # ------------------------------------------------------------------ phím
    def _phim_doi_tuong(self, e):
        c = self.dang_chon
        if not c or self.hien_tai is None:
            return None
        k = e.keysym
        ctrl = bool(e.state & 0x4)
        if k in ("Delete", "BackSpace"):
            self._xoa_chon()
            return "break"
        if k == "Escape":
            self.dang_chon = None
            self._ve_doi_tuong()
            return "break"
        buoc = 10 if e.state & 0x1 else 1
        dich = {"Left": (-buoc, 0), "Right": (buoc, 0), "Up": (0, -buoc), "Down": (0, buoc)}.get(k)
        if dich:
            hop = self._khung_dang_chon()
            self._dat_khung_chon((hop[0] + dich[0], hop[1] + dich[1], hop[2] + dich[0], hop[3] + dich[1]), doi_cho=True)
            return "break"
        if ctrl and k.lower() == "c" and c[0] == "tt":
            self._ban_sao = copy.deepcopy(self.tl.trang[self.hien_tai].thao_tac[c[1]])
            self.v_trang_thai.set("Đã chép đối tượng. Ctrl+V để dán (trang này hoặc trang khác).")
            return "break"
        return None

    def dan_doi_tuong(self):
        if self._ban_sao is None or self.hien_tai is None:
            return
        tt = copy.deepcopy(self._ban_sao)
        dt.doi(tt, 20, 20)
        self._them_thao_tac(tt)
        self.dang_chon = ("tt", len(self.tl.trang[self.hien_tai].thao_tac) - 1)
        self._bao_chon()
        self._ve_doi_tuong()

    def _xoa_chon(self):
        c = self.dang_chon
        if not c:
            return
        if c[0] == "tt":
            del self.tl.trang[self.hien_tai].thao_tac[c[1]]
            self.dang_chon = None
            self._sau_khi_doi(self.hien_tai)
        else:
            if not messagebox.askyesno("Sửa PDF", "Xóa vùng đã chọn khỏi trang (vá nền chỗ cũ)?", parent=self.w):
                return
            self.dang_chon = None
            self._them_thao_tac(dt.DoiVung(c[1], None))
        self.v_trang_thai.set("Đã xóa. Ctrl+Z để hoàn tác.")

    # ------------------------------------------------------------------ định dạng chữ đang chọn
    def _ap_dinh_dang_chon(self, *_):
        """Đổi phông, kiểu, cỡ, màu ở khung Chữ: áp ngay cho chữ đã thêm đang được chọn (như thanh định dạng); khi
        đang sửa ký tự thì áp cho đoạn chữ bôi chọn trên dòng."""
        if self._phien is not None and self.v_cong_cu.get() == "sua_ky_tu":
            self._ap_kieu_doan_chon()
            return
        c = self.dang_chon
        if not c or c[0] != "tt" or self.hien_tai is None or self.v_cong_cu.get() != "chon":
            return
        tt = self.tl.trang[self.hien_tai].thao_tac[c[1]]
        if not isinstance(tt, snd.ThemChu):
            return
        ten, kieu = self._phong_kieu(True)
        try:
            co = float(self.v_co.get()) / snd.diem_anh_sang_pt(self.anh_hien.shape[1])
        except (ValueError, TypeError):
            return
        if (tt.ten, tt.kieu, round(tt.co_px, 2), tt.mau) == (ten, kieu, round(co, 2), self.mau_chu):
            return
        tt.ten, tt.kieu, tt.co_px, tt.mau = ten, kieu, co, self.mau_chu
        self._sau_khi_doi(self.hien_tai)
        self._ve_doi_tuong()

    # ------------------------------------------------------------------ hoàn tác, làm lại
    def lam_lai_tt(self):
        i = self.hien_tai
        if i is None or not self.lam_lai.get(i):
            return
        self.tl.trang[i].thao_tac.append(self.lam_lai[i].pop())
        self.dang_chon = None
        self._sau_khi_doi(i)
