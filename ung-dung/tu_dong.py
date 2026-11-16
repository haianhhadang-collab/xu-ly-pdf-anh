"""Tính năng 4: tự động xử lý ảnh và PDF nhận được, theo lô hoặc theo thư mục theo dõi.

Ví dụ:
  python tu_dong.py xu-ly anh1.jpg cong-van.pdf thu-muc-anh -o ket-qua
  python tu_dong.py xu-ly thu-muc-anh --gop ho-so.pdf --ocr
  python tu_dong.py theo-doi "D:/May scan" -o "D:/Da xu ly" --ocr
"""
from __future__ import annotations

import argparse
import queue
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loi_xu_ly import doc_ghi  # noqa: E402
from loi_xu_ly.quy_trinh import TuyChon, TuyChonXuat, xu_ly_tep  # noqa: E402


def liet_ke_tep(dau_vao: list[str]) -> list[Path]:
    kq = []
    for d in dau_vao:
        p = Path(d)
        if p.is_dir():
            kq += sorted(f for f in p.iterdir() if f.suffix.lower() in doc_ghi.DUOI_HO_TRO)
        elif p.suffix.lower() in doc_ghi.DUOI_HO_TRO:
            kq.append(p)
    return kq


def ten_khong_trung(p: Path) -> Path:
    if not p.exists():
        return p
    i = 1
    while (q := p.with_name(f"{p.stem}_{i}{p.suffix}")).exists():
        i += 1
    return q


def xuat(cac_anh, duong_dan: Path, tcx: TuyChonXuat, bao=print):
    doc_ghi.ghi_pdf(cac_anh, duong_dan, tcx.kho, tcx.le_mm, tcx.chat_luong, tcx.ocr, tcx.ngon_ngu)
    if tcx.xuat_txt:
        doc_ghi.ghi_van_ban(cac_anh, duong_dan.with_suffix(".txt"), tcx.ngon_ngu)
    bao(f"  → {duong_dan}")


class TheoDoi:
    """Theo dõi một thư mục; tệp ảnh/PDF mới được xử lý và ghi PDF vào thư mục ra."""

    def __init__(self, thu_muc, thu_muc_ra, tc: TuyChon, tcx: TuyChonXuat, bao=print, ca_tep_cu=False):
        self.thu_muc = Path(thu_muc)
        self.ra = Path(thu_muc_ra) if thu_muc_ra else self.thu_muc / "da-xu-ly"
        self.tc, self.tcx, self.bao = tc, tcx, bao
        self.ca_tep_cu = ca_tep_cu
        self.hang = queue.Queue()
        self.dung_lai = threading.Event()
        self.quan_sat = None

    def bat_dau(self):
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

        self.ra.mkdir(parents=True, exist_ok=True)
        hang = self.hang

        class XuLySuKien(FileSystemEventHandler):
            def on_created(self, e):
                if not e.is_directory:
                    hang.put(Path(e.src_path))

            def on_moved(self, e):
                if not e.is_directory:
                    hang.put(Path(e.dest_path))

        if self.ca_tep_cu:
            for f in liet_ke_tep([str(self.thu_muc)]):
                self.hang.put(f)
        self.quan_sat = Observer()
        self.quan_sat.schedule(XuLySuKien(), str(self.thu_muc), recursive=False)
        self.quan_sat.start()
        threading.Thread(target=self._vong, daemon=True).start()
        self.bao(f"Đang theo dõi {self.thu_muc} → {self.ra}")

    def dung(self):
        self.dung_lai.set()
        if self.quan_sat:
            self.quan_sat.stop()
            self.quan_sat.join(timeout=3)
        self.bao("Đã dừng theo dõi")

    def _cho_ghi_xong(self, p: Path, cho_toi_da: float = 120) -> bool:
        """Đợi đến khi tệp thôi thay đổi kích thước (máy scan, Zalo đang ghi)."""
        cu, han = -1, time.time() + cho_toi_da
        while time.time() < han and not self.dung_lai.is_set():
            try:
                moi = p.stat().st_size
                with open(p, "rb"):
                    pass
            except OSError:
                moi = -2
            if moi == cu and moi > 0:
                return True
            cu = moi
            time.sleep(1.0)
        return False

    def _vong(self):
        da_lam = set()
        while not self.dung_lai.is_set():
            try:
                p = self.hang.get(timeout=0.5)
            except queue.Empty:
                continue
            if p.suffix.lower() not in doc_ghi.DUOI_HO_TRO or p.name.endswith(".dang-ghi") or p in da_lam:
                continue
            if not self._cho_ghi_xong(p):
                continue
            da_lam.add(p)
            try:
                self.bao(f"Xử lý {p.name}…")
                cac_anh = xu_ly_tep(p, self.tc)
                xuat(cac_anh, ten_khong_trung(self.ra / f"{p.stem}.pdf"), self.tcx, self.bao)
            except Exception as e:  # một tệp hỏng không được làm dừng cả hàng đợi
                self.bao(f"Lỗi với {p.name}: {e}")


def _them_tuy_chon(ps: argparse.ArgumentParser):
    ps.add_argument("-o", "--ra", help="thư mục ghi PDF kết quả")
    ps.add_argument("--che-do", default="giu_mau", choices=["giu_mau", "xam", "den_trang", "khong"])
    ps.add_argument("--kho", default="a4", choices=["theo_anh", "a4", "a5", "letter", "legal"])
    ps.add_argument("--le", type=float, default=0.0, help="lề (mm)")
    ps.add_argument("--chat-luong", default="vua", choices=["cao", "vua", "nho"])
    ps.add_argument("--ocr", action="store_true", help="thêm lớp chữ tìm kiếm được")
    ps.add_argument("--txt", action="store_true", help="xuất kèm tệp văn bản .txt")
    ps.add_argument("--ngon-ngu", default="vie")
    ps.add_argument("--tach-trang-doi", action="store_true")
    ps.add_argument("--khong-tim-mep", action="store_true")
    ps.add_argument("--khong-xoay", action="store_true")
    ps.add_argument("--khong-sua-nghieng", action="store_true")


def main():
    sys.stdout.reconfigure(line_buffering=True)  # nhật ký hiện ngay cả khi chuyển hướng ra tệp
    ps = argparse.ArgumentParser(description="Tự động xử lý ảnh, PDF tài liệu")
    con = ps.add_subparsers(dest="lenh", required=True)
    p1 = con.add_parser("xu-ly", help="xử lý theo lô các tệp, thư mục")
    p1.add_argument("dau_vao", nargs="+")
    p1.add_argument("--gop", help="gộp tất cả vào một PDF có tên này")
    _them_tuy_chon(p1)
    p2 = con.add_parser("theo-doi", help="theo dõi thư mục, tự xử lý tệp mới")
    p2.add_argument("thu_muc")
    p2.add_argument("--ca-tep-cu", action="store_true", help="xử lý cả tệp đã có sẵn")
    _them_tuy_chon(p2)
    a = ps.parse_args()

    tc = TuyChon(tim_mep=not a.khong_tim_mep, tu_xoay=not a.khong_xoay, sua_nghieng=not a.khong_sua_nghieng,
                 tach_trang_doi=a.tach_trang_doi, che_do=a.che_do)
    tcx = TuyChonXuat(kho=a.kho, le_mm=a.le, chat_luong=a.chat_luong, ocr=a.ocr, ngon_ngu=a.ngon_ngu, xuat_txt=a.txt)

    if a.lenh == "theo-doi":
        td = TheoDoi(a.thu_muc, a.ra, tc, tcx, ca_tep_cu=a.ca_tep_cu)
        td.bat_dau()
        print("Bấm Ctrl+C để dừng.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            td.dung()
        return

    tep = liet_ke_tep(a.dau_vao)
    if not tep:
        sys.exit("Không có tệp ảnh/PDF nào.")
    gop = []
    for f in tep:
        print(f"Xử lý {f.name}…")
        try:
            cac_anh = xu_ly_tep(f, tc)
        except Exception as e:
            print(f"  Lỗi: {e}")
            continue
        if a.gop:
            gop += cac_anh
        else:
            thu_muc = Path(a.ra) if a.ra else f.parent
            thu_muc.mkdir(parents=True, exist_ok=True)
            xuat(cac_anh, ten_khong_trung(thu_muc / f"{f.stem}_da-xu-ly.pdf"), tcx)
    if a.gop and gop:
        dich = Path(a.gop)
        if a.ra and not dich.is_absolute():
            Path(a.ra).mkdir(parents=True, exist_ok=True)
            dich = Path(a.ra) / dich
        xuat(gop, dich, tcx)


if __name__ == "__main__":
    main()
