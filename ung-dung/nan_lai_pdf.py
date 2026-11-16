"""Nắn lại PDF đã có (ảnh chụp sách, tài liệu): xoay đúng chiều, nắn cong dòng chữ, nắn vuông khối chữ (lề trái, lề
phải thẳng), xoay thẳng từng trang của cặp trang sách mở, làm sạch nền, cắt theo chữ (lề vừa). Ghi ra PDF mới cạnh tệp gốc
(<tên>_nan.pdf), tệp gốc giữ nguyên.

Chạy:  python nan_lai_pdf.py <tệp.pdf> [tệp khác…] [--tach] [--le=sat|vua|trang]
       --tach: tách cặp trang sách mở thành hai trang riêng (cắt giữa khe gáy)
       --le:   lề trang: sat (sát chữ), vua (mặc định, giữ lề thật tới 6%), trang (giữ cả trang)
       Kéo thả tệp PDF vào nan-lai-pdf.bat cũng được.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from loi_xu_ly import doc_ghi, quy_trinh  # noqa: E402


def nan_lai(vao: Path, tach: bool, le: str = "vua") -> Path:
    tc = quy_trinh.TuyChon(tach_trang_doi=tach, le=le)
    ra = vao.with_name(vao.stem + "_nan.pdf")
    trang = quy_trinh.xu_ly_tep(vao, tc, bao=lambda s: print("  " + s, flush=True))
    doc_ghi.ghi_pdf(trang, ra, kho="theo_anh", tieu_de=vao.stem)
    return ra


def main() -> int:
    tach = "--tach" in sys.argv
    le = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--le=")), "vua")
    tep = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    if not tep:
        print(__doc__)
        return 1
    for p in tep:
        if not p.exists():
            print(f"Không thấy tệp {p}")
            continue
        print(f"Đang nắn {p.name}…")
        print(f"Xong: {nan_lai(p, tach, le)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
