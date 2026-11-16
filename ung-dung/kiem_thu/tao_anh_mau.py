"""Tạo ảnh tài liệu mẫu tổng hợp để thử luồng xử lý.

Mẫu 1: công văn có dấu đỏ, chữ ký xanh, chụp nghiêng trên bàn gỗ, có bóng đổ, giấy ngả vàng.
Mẫu 2: cùng trang nhưng quét lộn ngược 180° và nghiêng 2°.
Mẫu 3: hai trang sách mở, có bóng ở gáy.
Mẫu 4: PDF một trang chứa mẫu 2 (thử đọc PDF).

Chạy:  python tao_anh_mau.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

THU_MUC = Path(__file__).parent / "anh_mau"
FONT = "C:/Windows/Fonts/times.ttf"
FONT_DAM = "C:/Windows/Fonts/timesbd.ttf"

NOI_DUNG = [
    "Kính gửi: Thư viện Trường Đại học Hà Nội",
    "Căn cứ kế hoạch công tác năm học 2026–2027, phòng Hành chính đề nghị",
    "Thư viện phối hợp số hóa toàn bộ hồ sơ lưu trữ giai đoạn 2010–2020.",
    "Tài liệu gồm công văn, quyết định, biên bản họp có đóng dấu đỏ và chữ ký.",
    "Yêu cầu bản số hóa giữ nguyên màu con dấu, chữ ký, bút phê; nền trắng rõ.",
    "The scanned files must be searchable in both Vietnamese and English.",
    "Đề nghị hoàn thành trước ngày 15 tháng 12 năm 2026 và báo cáo kết quả.",
    "Trân trọng cảm ơn sự phối hợp của quý đơn vị.",
]


def tao_trang(rong=1240, cao=1754) -> np.ndarray:
    img = Image.new("RGB", (rong, cao), (246, 240, 222))
    d = ImageDraw.Draw(img)
    f, fd, fn = ImageFont.truetype(FONT, 30), ImageFont.truetype(FONT_DAM, 32), ImageFont.truetype(FONT, 26)
    d.text((620, 110), "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", font=fd, fill=(20, 20, 20), anchor="mm")
    d.text((620, 155), "Độc lập – Tự do – Hạnh phúc", font=fd, fill=(20, 20, 20), anchor="mm")
    d.text((620, 260), "CÔNG VĂN ĐỀ NGHỊ SỐ HÓA TÀI LIỆU", font=fd, fill=(20, 20, 20), anchor="mm")
    y = 360
    for dong in NOI_DUNG:
        d.text((130, y), dong, font=f, fill=(25, 25, 25))
        y += 62
    d.text((800, y + 60), "TRƯỞNG PHÒNG", font=fd, fill=(20, 20, 20), anchor="mm")
    d.text((800, y + 330), "Nguyễn Văn An", font=f, fill=(20, 20, 20), anchor="mm")
    # bút phê màu đỏ ở lề trái
    d.text((130, y + 120), "Đồng ý, giao Thư viện", font=fn, fill=(200, 20, 30))
    anh = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # con dấu đỏ, trộn trong suốt đè lên chữ
    dau = np.zeros_like(anh)
    tam = (720, y + 200)
    cv2.circle(dau, tam, 115, (40, 30, 205), 7)
    cv2.circle(dau, tam, 95, (40, 30, 205), 3)
    cv2.putText(dau, "*", (tam[0] - 30, tam[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 3.5, (40, 30, 205), 8)
    mat_na = dau.any(axis=2)
    anh[mat_na] = (anh[mat_na] * 0.25 + dau[mat_na] * 0.75).astype(np.uint8)

    # chữ ký xanh
    t = np.linspace(0, 1, 300)
    x = 740 + 220 * t + 25 * np.sin(t * 18)
    yk = y + 230 + 40 * np.sin(t * 9) * (1 - t)
    diem = np.stack([x, yk], axis=1).astype(np.int32)
    cv2.polylines(anh, [diem], False, (170, 60, 30), 3, cv2.LINE_AA)
    return anh


def chup_tren_ban(trang: np.ndarray, rng) -> tuple[np.ndarray, list]:
    H, W = 2600, 2000
    nen = np.zeros((H, W, 3), np.float32)
    van = (np.sin(np.linspace(0, 60, W))[None, :] * 12 + rng.normal(0, 6, (H, W)))
    nen[..., 0], nen[..., 1], nen[..., 2] = 40 + van, 65 + van, 100 + van
    h, w = trang.shape[:2]
    goc_dich = np.float32([[330, 300], [1650, 380], [1760, 2250], [230, 2330]])
    m = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), goc_dich)
    cong = cv2.warpPerspective(trang, m, (W, H), flags=cv2.INTER_LINEAR)
    mat = cv2.warpPerspective(np.ones((h, w), np.float32), m, (W, H))[..., None]
    anh = cong.astype(np.float32) * mat + nen * (1 - mat)
    # bóng đổ chéo góc dưới phải
    yy, xx = np.mgrid[0:H, 0:W]
    bong = 1 - 0.45 * np.clip((xx / W + yy / H - 0.9) / 1.1, 0, 1)
    anh = anh * bong[..., None] + rng.normal(0, 3, anh.shape)
    anh = np.clip(anh, 0, 255).astype(np.uint8)
    return anh, goc_dich.tolist()


def trang_sach(rng) -> np.ndarray:
    trai, phai = tao_trang(), tao_trang()
    doi = np.concatenate([trai, phai], axis=1).astype(np.float32)
    w = doi.shape[1]
    x = np.arange(w)
    bong = 1 - 0.55 * np.exp(-((x - w / 2) / 60.0) ** 2)
    doi = doi * bong[None, :, None] + rng.normal(0, 3, doi.shape)
    return np.clip(doi, 0, 255).astype(np.uint8)


def ghi(anh, ten):
    ok, buf = cv2.imencode(".jpg", anh, [cv2.IMWRITE_JPEG_QUALITY, 88])
    buf.tofile(str(THU_MUC / ten))


def main():
    THU_MUC.mkdir(exist_ok=True)
    rng = np.random.default_rng(1)
    trang = tao_trang()
    anh1, goc = chup_tren_ban(trang, rng)
    ghi(anh1, "mau1-chup-nghieng.jpg")

    h, w = trang.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), 182, 1.0)
    anh2 = cv2.warpAffine(trang, m, (w, h), borderValue=(246, 240, 222))
    ghi(anh2, "mau2-lon-nguoc.jpg")

    ghi(trang_sach(rng), "mau3-trang-doi.jpg")

    Image.fromarray(cv2.cvtColor(anh2, cv2.COLOR_BGR2RGB)).save(THU_MUC / "mau4.pdf", resolution=150)
    (THU_MUC / "dap_an.json").write_text(json.dumps({"mau1_goc": goc}, indent=1), encoding="utf-8")
    print("Đã tạo ảnh mẫu trong", THU_MUC)


if __name__ == "__main__":
    main()
