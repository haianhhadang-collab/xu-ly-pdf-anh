"""Sửa ký tự giữ nguyên bản gốc: thêm, bớt ký tự trên ảnh scan, ảnh chụp mà không vẽ lại chữ.

Mỗi dòng chữ được chia thành các mảnh nằm liền nhau: mỗi ký tự, mỗi khoảng trắng là một dải điểm ảnh gốc
(khung ký tự lấy từ Tesseract, hOCR có `hocr_char_boxes`). Sửa dòng = xếp lại các mảnh:
- ký tự không đụng tới giữ nguyên từng điểm ảnh (chỉ dời ngang khi có chèn, xóa phía trước);
- xóa ký tự = bỏ mảnh;
- chèn ký tự = chép nguyên hình ký tự đó từ chỗ khác trên cùng trang (cùng cỡ, cùng nét, cùng độ nhòe);
  trang không có ký tự đó thì mới vẽ bằng phông đoán được (sua_noi_dung.doan_kieu_chu);
- dòng có dãy dấu chấm dẫn (mục lục) thì dãy chấm co giãn để phần sau (số trang) đứng nguyên chỗ.
Nhận dạng chữ chỉ dùng để biết ranh giới ký tự và tìm ký tự mẫu; máy đọc sai cũng không làm đổi chỗ không sửa.
Ảnh chụp, bản scan lệch làm dòng nghiêng: đường chân chữ là đường xiên đo riêng từng dòng; khi dời, chép chỉ đụng tới
nét mực của chính dòng (nét dòng trên, dòng dưới lọt vào cùng dải giữ nguyên), mảnh dời đi theo độ dốc của dòng.
"""
from __future__ import annotations

import html
import math
import re
import unicodedata as ud
from dataclasses import dataclass, field, replace

import cv2
import numpy as np

from . import nhan_dang
from . import sua_noi_dung as snd


@dataclass
class KyTu:
    chu: str
    hop: tuple[int, int, int, int]  # x0, y0, x1, y1 (x1, y1 không tính)
    tin_cay: float
    dam: float = field(default=0.0, repr=False, compare=False)                # độ đậm nét riêng ký tự, đo khi cần
    hinh: np.ndarray | None = field(default=None, repr=False, compare=False)  # hình thu nhỏ 16×16 (so dáng chữ)
    chia: bool = False  # khung ước lượng: chữ dính nét chữ bên cạnh, chia đôi nét (kém tin khi làm mẫu chép)


@dataclass
class DongAnh:
    hop: tuple[int, int, int, int]  # khung dòng của Tesseract
    chan: float                     # đường chân chữ (y) ở giữa dòng
    tu: list[list[KyTu]]
    dai: tuple[int, int] = (0, 0)   # dải dọc chứa trọn dòng (cả phần xiên); chỉ nét của dòng mới bị dời, chép
    dam: float = 0.0                # độ đậm nét (bề dày nét / cỡ chữ), đo khi cần
    nghieng: float = 0.0            # độ dốc đường chân chữ (dy/dx): ảnh chụp, bản scan lệch
    x_chan: float = 0.0             # `chan` đo tại cột này
    tren: float = 0.0               # dòng chiếm từ chan_tai(x) - tren tới chan_tai(x) + duoi (cả dấu, nét xuống)
    duoi: float = 0.0

    def chan_tai(self, x: float) -> float:
        """Đường chân chữ tại cột x (dòng nghiêng)."""
        return self.chan + self.nghieng * (x - self.x_chan)

    def dai_tai(self, x: float) -> tuple[float, float]:
        """Mép trên, mép dưới của dòng tại cột x (dải xiên; dòng chưa đo độ nghiêng thì là dải dọc)."""
        if not self.tren:
            return float(self.dai[0]), float(self.dai[1])
        c = self.chan_tai(x)
        return c - self.tren, c + self.duoi

    @property
    def ky_tu(self) -> list[KyTu]:
        return [c for w in self.tu for c in w]

    @property
    def chu(self) -> str:
        return " ".join("".join(c.chu for c in w) for w in self.tu)

    @property
    def co_x(self) -> float | None:
        """Chiều cao chữ thường không dấu, không nét lên xuống (a, c, e, m, n, o…): so cỡ chữ hai dòng ổn định hơn `co`,
        vốn dao động theo tỉ lệ chữ hoa, chữ có dấu trong dòng. None nếu dòng có ít hơn 3 chữ như vậy."""
        cao = [c.hop[3] - c.hop[1] for c in self.ky_tu if c.chu in "acemnorsuvwxz" and c.tin_cay >= 70]
        return float(np.median(cao)) if len(cao) >= 3 else None

    @property
    def co(self) -> float:
        """Cỡ chữ của dòng: trung vị chiều cao khung các ký tự cỡ chữ thường (bỏ dấu chấm, dấu phẩy)."""
        chac = [c for c in self.ky_tu if c.tin_cay >= 60] or self.ky_tu  # bỏ "chữ" máy đọc nhầm từ chấm, vết bẩn
        cao = np.sort(np.array([c.hop[3] - c.hop[1] for c in chac], float))
        # dòng mục lục có hàng chục "ký tự" máy đọc từ dấu chấm: lấy theo nhóm ký tự lớn nhất
        dinh = cao[-3:].mean()
        return float(np.median(cao[cao >= 0.6 * dinh]))


# ---------------------------------------------------------------- đọc dòng, ký tự

_THE = re.compile(r"""<span class=['"](ocr_line|ocr_header|ocr_textfloat|ocr_caption|ocrx_word|ocrx_cinfo)['"][^>]*?title=(['"])(.*?)\2[^>]*>""", re.S)


def doc_dong(anh: np.ndarray, ngon_ngu: str = "vie") -> list[DongAnh]:
    """Nhận dạng trang, trả các dòng kèm khung từng ký tự."""
    if not nhan_dang.CO_TESSERACT:
        raise RuntimeError("Chưa cài Tesseract OCR nên không tìm được chữ trên trang.")
    import pytesseract
    # ảnh chụp, PDF nén thường chỉ 100–150 dpi, chữ cao chưa tới 10 điểm ảnh: Tesseract đọc rất sai.
    # Phóng tới cỡ trang A4 300 dpi chỉ để nhận dạng, rồi quy khung về ảnh gốc.
    phong = min(3.0, max(1.0, 2480 / max(1, min(anh.shape[:2]))))
    vao = cv2.resize(anh, None, fx=phong, fy=phong, interpolation=cv2.INTER_CUBIC) if phong > 1.05 else anh
    hocr = pytesseract.image_to_pdf_or_hocr(nhan_dang._pil(vao), lang=nhan_dang.chon_ngon_ngu(ngon_ngu), extension="hocr",
                                            config="--psm 3 -c hocr_char_boxes=1").decode("utf-8")
    dong = gop_dong_cung_hang(anh, doc_hocr(hocr, anh.shape[0], phong if phong > 1.05 else 1.0))
    dong = thay_cham_dan(anh, noi_dai_dong(anh, dong))
    for d in dong:
        _tinh_chan(d, anh.shape[0])
        nan_khung(anh, d)
        _tinh_chan(d, anh.shape[0])
    return dong


def nan_khung(anh: np.ndarray, d: DongAnh) -> None:
    """Nắn khung ký tự theo nét mực thật. Khung ký tự của Tesseract (LSTM) chỉ đúng thứ tự, hay lệch ngang nửa ký tự
    (khung "ư" trùm sang "t", khung "ộ" lấn sang "m"): chia mảnh, chép mẫu theo khung lệch là cắt đôi chữ, chép nhầm
    nét chữ bên cạnh ("lỗi phông" khi gõ chữ mới). Từng từ: các nét chính (thành phần liên thông cao từ nửa chiều cao
    chữ thường) xếp theo thứ tự rồi ghép với các chữ, số của từ theo thứ tự (quy hoạch động: một chữ có thể gồm vài
    nét đứt, vài chữ dính chung một nét thì chia nét theo bề rộng khung cũ); nét nhỏ trên thân chữ, dưới đường chân
    (dấu thanh, chấm i, móc ơ ư, dấu nặng) theo chữ đứng dưới, trên nó; nét nhỏ ngang thân chữ theo dấu câu gần nhất."""
    y0, y1 = d.dai
    x0, x1 = max(0, d.hop[0] - 2), min(anh.shape[1], d.hop[2] + 2)
    if y1 <= y0 or x1 <= x0 or not d.tren:
        return
    _, toi = cv2.threshold(cv2.cvtColor(anh[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, _, tk, _ = cv2.connectedComponentsWithStats(toi, connectivity=8)
    xh, co = x_cao(d), d.co
    chinh, nho = [], []
    for i in range(1, n):
        gx, gy, gw, gh, dt = (int(v) for v in tk[i])
        gx, gy = gx + x0, gy + y0
        ct = d.chan_tai(gx + gw / 2)
        if dt < 2 or gh > 2.6 * co or not (ct - d.tren <= gy + gh / 2 <= ct + d.duoi):
            continue  # vết bẩn, khung bảng, nét dòng khác
        # nét chính: đủ cao và chạm đường chân (móc ơ, ư, dấu thanh tách rời thì không)
        la_chinh = gh >= 0.5 * xh and gy + gh >= ct - 0.25 * xh
        (chinh if la_chinh else nho).append((gx, gy, gx + gw, gy + gh))
    if not chinh:
        return
    tu = [w for w in d.tu if any(c.chu.isalnum() and c.tin_cay > 0 for c in w)]
    if not tu:
        return
    nhip = [(min(c.hop[0] for c in w), max(c.hop[2] for c in w)) for w in tu]
    cua_tu: list[list] = [[] for _ in tu]
    for g in sorted(chinh):
        cx = (g[0] + g[2]) / 2
        gan = [(abs(cx - (a + b) / 2), k) for k, (a, b) in enumerate(nhip) if a - 0.3 * co <= cx <= b + 0.3 * co]
        if gan:
            cua_tu[min(gan)[1]].append(g)
    phat = 1.0 * co  # phạt mỗi chữ (nét) ghép thêm: khung máy đọc lệch cả chữ, chỉ ghép khi số nét, số chữ không khớp
    moi: dict[int, list[int]] = {}  # id(ký tự) → khung mới
    chia: set[int] = set()          # ký tự chia chung một nét (dính chữ bên cạnh): khung ước lượng, kém tin làm mẫu
    for w, gs in zip(tu, cua_tu):
        chu = [c for c in w if c.chu.isalnum() and c.tin_cay > 0]
        if not gs:
            continue
        nc, ng = len(chu), len(gs)

        def lech(a: list, b: list) -> float:
            # độ lệch hai mép trái, phải: khung nhóm nét so với khung nhóm chữ (so tâm thì ba chữ dính một nét rộng vẫn
            # "khớp" như hai chữ)
            return abs(min(g[0] for g in a) - min(c.hop[0] for c in b)) + abs(max(g[2] for g in a) - max(c.hop[2] for c in b))
        INF = float("inf")
        dp = [[INF] * (ng + 1) for _ in range(nc + 1)]
        tu_dau = [[None] * (ng + 1) for _ in range(nc + 1)]
        dp[0][0] = 0.0
        for i in range(nc + 1):
            for j in range(ng + 1):
                if dp[i][j] == INF or (i == nc and j == ng):
                    continue
                if i < nc:  # chữ i nhận k nét liền nhau
                    for k in range(1, min(3, ng - j) + 1):
                        cp = dp[i][j] + lech(gs[j:j + k], chu[i:i + 1]) + phat * (k - 1)
                        if cp < dp[i + 1][j + k]:
                            dp[i + 1][j + k], tu_dau[i + 1][j + k] = cp, (i, j)
                if j < ng:  # k chữ dính chung nét j
                    for k in range(2, min(4, nc - i) + 1):
                        cp = dp[i][j] + lech(gs[j:j + 1], chu[i:i + k]) + phat * (k - 1)
                        if cp < dp[i + k][j + 1]:
                            dp[i + k][j + 1], tu_dau[i + k][j + 1] = cp, (i, j)
        if dp[nc][ng] == INF:
            continue
        i, j = nc, ng
        while (i, j) != (0, 0):
            pi, pj = tu_dau[i][j]
            nhom = gs[pj:j]
            hop = [min(g[0] for g in nhom), min(g[1] for g in nhom), max(g[2] for g in nhom), max(g[3] for g in nhom)]
            if i - pi == 1:
                moi[id(chu[pi])] = hop
            else:  # nhiều chữ dính một nét: chia theo bề rộng khung cũ; khung ước lượng nên kém tin khi làm mẫu
                rong = [max(1, c.hop[2] - c.hop[0]) for c in chu[pi:i]]
                x = float(hop[0])
                for c, r in zip(chu[pi:i], rong):
                    x2 = x + (hop[2] - hop[0]) * r / sum(rong)
                    moi[id(c)] = [int(round(x)), hop[1], int(round(x2)), hop[3]]
                    chia.add(id(c))
                    x = x2
            i, j = pi, pj
    if not moi:
        return
    tat = d.ky_tu
    chu_so = [c for c in tat if id(c) in moi]
    dau_cau = [c for c in tat if not c.chu.isalnum() and c.chu.strip()]
    nho_dau: dict[int, list] = {}
    for g in nho:
        cx, cy = (g[0] + g[2]) / 2, (g[1] + g[3]) / 2
        ct = d.chan_tai(cx)
        if cy < ct - 0.6 * xh or cy > ct + 0.1 * xh:  # dấu thanh, chấm i, dấu nặng: theo chữ đứng dưới, trên
            ung = [(0 if moi[id(c)][0] - 1 <= cx <= moi[id(c)][2] + 1 else 1, abs(cx - (moi[id(c)][0] + moi[id(c)][2]) / 2), id(c))
                   for c in chu_so]
            tot = min(ung)
            if tot[0] == 0 or tot[1] <= 0.6 * co:
                moi[tot[2]] = [min(moi[tot[2]][0], g[0]), min(moi[tot[2]][1], g[1]), max(moi[tot[2]][2], g[2]),
                               max(moi[tot[2]][3], g[3])]
        elif dau_cau:  # nét nhỏ ngang thân chữ: dấu câu
            c = min(dau_cau, key=lambda c: abs(cx - (c.hop[0] + c.hop[2]) / 2))
            if abs(cx - (c.hop[0] + c.hop[2]) / 2) <= 0.8 * co:
                nho_dau.setdefault(id(c), []).append(g)
    for c in dau_cau:
        if id(c) in nho_dau:
            gs = nho_dau[id(c)]
            moi[id(c)] = [min(g[0] for g in gs), min(g[1] for g in gs), max(g[2] for g in gs), max(g[3] for g in gs)]
    for w in d.tu:
        for k, c in enumerate(w):
            if id(c) in moi:
                w[k] = KyTu(c.chu, tuple(moi[id(c)]), c.tin_cay, chia=id(c) in chia)


# ký tự có nét, dấu xuống dưới đường chân: không dùng để đo đường chân
_DUOI_CHAN = set("gjpqyQ,;()[]{}|/ạặậẹệịọộợụựỵẠẶẬẸỆỊỌỘỢỤỰỴ")


def _tinh_chan(d: DongAnh, cao_trang: int | None = None):
    """Đường chân chữ: đường xiên qua đáy khung các ký tự thật, cỡ chữ thường (bỏ dấu chấm, ký tự chưa biết tên, ký tự
    có nét xuống, chữ máy đọc không chắc), sau khi đã gộp dòng và thay dãy chấm. Độ dốc theo Theil–Sen (trung vị độ
    dốc từng cặp ký tự cách xa nhau) nên vài khung máy đọc lệch không kéo lệch cả đường. Rồi tính dải xiên của dòng."""
    co = d.co
    chon = [c for c in d.ky_tu if c.chu not in ".?" and c.chu not in _DUOI_CHAN and c.tin_cay >= 60
            and c.hop[3] - c.hop[1] >= 0.6 * co]
    d.x_chan = (d.hop[0] + d.hop[2]) / 2
    if not chon:
        return
    x = np.array([(c.hop[0] + c.hop[2]) / 2 for c in chon])
    y = np.array([c.hop[3] for c in chon], float)
    doc = []
    for i in range(len(x)):
        dx = x[i + 1:] - x[i]
        xa = np.abs(dx) >= co
        doc.extend(((y[i + 1:] - y[i])[xa] / dx[xa]).tolist())
    d.nghieng = float(np.clip(np.median(doc), -0.2, 0.2)) if len(doc) >= 3 else 0.0
    d.chan = float(np.median(y - d.nghieng * (x - d.x_chan)))
    # dải xiên: phủ trọn khung các ký tự (dấu thanh, nét xuống) quanh đường chân
    tren = max(d.chan_tai((c.hop[0] + c.hop[2]) / 2) - c.hop[1] for c in d.ky_tu)
    duoi = max(c.hop[3] - d.chan_tai((c.hop[0] + c.hop[2]) / 2) for c in d.ky_tu)
    d.tren = float(np.clip(tren + 2, 0.8 * co, 1.8 * co))
    d.duoi = float(np.clip(duoi + 2, 0.25 * co, 0.8 * co))
    if cao_trang is not None:
        a, b = d.chan_tai(d.hop[0]), d.chan_tai(d.hop[2])
        d.dai = (max(0, min(d.dai[0], int(np.floor(min(a, b) - d.tren)))),
                 min(cao_trang, max(d.dai[1], int(np.ceil(max(a, b) + d.duoi)))))


def doc_hocr(hocr: str, cao_trang: int, phong: float = 1.0) -> list[DongAnh]:
    """Đọc hOCR có khung ký tự; `phong`: ảnh đưa vào Tesseract đã phóng bao nhiêu lần (tọa độ chia lại)."""
    def q(v):
        return int(round(int(v) / phong))
    dong: list[DongAnh] = []
    for m in _THE.finditer(hocr):
        loai, tieu_de = m.group(1), m.group(3)
        if loai == "ocrx_cinfo":
            k = re.search(r"x_bboxes (-?\d+) (-?\d+) (-?\d+) (-?\d+)", tieu_de)
            cuoi = hocr.find("<", m.end())
            chu = html.unescape(hocr[m.end():cuoi]).strip()
            tc = re.search(r"x_conf ([\d.]+)", tieu_de)
            if k and chu and dong and dong[-1].tu:
                x0, y0, x1, y1 = (q(v) for v in k.groups())
                dong[-1].tu[-1].append(KyTu(chu, (x0, y0, max(x0 + 1, q(int(k.group(3)) + 1)), max(y0 + 1, q(int(k.group(4)) + 1))),
                                            float(tc.group(1)) if tc else 0.0))
        elif loai == "ocrx_word":
            if dong:
                dong[-1].tu.append([])
        else:
            k = re.search(r"bbox (\d+) (\d+) (\d+) (\d+)", tieu_de)
            if not k:
                continue
            x0, y0, x1, y1 = (int(v) for v in k.groups())
            b = re.search(r"baseline (-?[\d.]+) (-?[\d.]+)", tieu_de)
            chan = (y1 + (float(b.group(2)) + float(b.group(1)) * (x1 - x0) / 2 if b else 0.0)) / phong
            x0, y0, x1, y1 = q(x0), q(y0), q(x1), q(y1)
            dong.append(DongAnh((x0, y0, x1, y1), chan, []))
    kq = []
    for d in dong:
        d.tu = [w for w in d.tu if w]
        if d.tu:
            # đường chân chữ: trung vị đáy khung các ký tự cỡ thường (số liệu baseline của Tesseract hay lệch)
            co = d.co
            day = [c.hop[3] for c in d.ky_tu if c.hop[3] - c.hop[1] >= 0.6 * co]
            if day:
                d.chan = float(np.median(day))
            kq.append(d)
    # dải dọc mỗi dòng: nới khỏi khung một chút nhưng không quá nửa khoảng cách tới dòng trên, dưới
    for d in kq:
        x0, y0, x1, y1 = d.hop
        cao = y1 - y0
        tren, duoi = max(0, y0 - cao // 4), min(cao_trang, y1 + cao // 4)
        for e in kq:
            if e is d or e.hop[2] <= x0 or e.hop[0] >= x1:
                continue
            if e.hop[3] <= y0:
                tren = max(tren, (e.hop[3] + y0) // 2)
            elif e.hop[1] >= y1:
                duoi = min(duoi, (y1 + e.hop[1]) // 2)
        d.dai = (tren, duoi)
    return kq


def ti_le_co(dich: DongAnh, nguon: DongAnh) -> float:
    """Tỉ lệ cỡ chữ dòng đích / dòng nguồn; chênh dưới 12% coi như cùng cỡ (cùng tài liệu thường cùng cỡ chữ)."""
    a, b = dich.co_x, nguon.co_x
    r = a / b if a and b else dich.co / max(nguon.co, 1)
    return 1.0 if abs(r - 1) <= 0.12 else r


def gop_dong_cung_hang(anh: np.ndarray, cac_dong: list[DongAnh]) -> list[DongAnh]:
    """Gộp các dòng Tesseract tách rời nằm trên cùng một hàng chữ (mục lục: số trang, dãy chấm hay thành dòng riêng).
    Chỉ gộp khi khoảng hở hẹp (< 30% bề rộng trang) hoặc được nối bằng dãy chấm dẫn: hai cột văn bản không bị gộp."""
    W = anh.shape[1]
    kq: list[DongAnh] = []
    for d in sorted(cac_dong, key=lambda d: (d.hop[1], d.hop[0])):
        for g in kq:
            cao = min(g.hop[3] - g.hop[1], d.hop[3] - d.hop[1])
            trung = min(g.hop[3], d.hop[3]) - max(g.hop[1], d.hop[1])
            if trung < 0.5 * cao or abs(g.chan - d.chan) > 0.35 * max(g.co, d.co):
                continue
            trai, phai = (g, d) if g.hop[0] <= d.hop[0] else (d, g)
            ho = phai.hop[0] - trai.hop[2]
            if ho < -2:
                continue
            moi = DongAnh((min(g.hop[0], d.hop[0]), min(g.hop[1], d.hop[1]), max(g.hop[2], d.hop[2]), max(g.hop[3], d.hop[3])),
                          float(np.median([g.chan, d.chan])), trai.tu + phai.tu, (min(g.dai[0], d.dai[0]), max(g.dai[1], d.dai[1])))
            if ho > 0.3 * W:
                cham = tim_cham_dan(anh, moi)
                phu = sum(b - a for a, b in cham) and (cham[-1][1] - cham[0][0]) if cham else 0
                if phu < 0.6 * ho:
                    continue
            kq[kq.index(g)] = moi
            break
        else:
            kq.append(d)
    return sorted(kq, key=lambda d: (d.hop[1], d.hop[0]))


def noi_dai_dong(anh: np.ndarray, cac_dong: list[DongAnh]) -> list[DongAnh]:
    """Nối dài dòng sang phải theo nét mực: Tesseract hay bỏ sót phần chữ đứng lẻ ở mép phải (số trang mục lục,
    dãy chấm dẫn). Nét mực nằm đúng hàng chữ sau phần đã đọc được thêm vào dòng thành ký tự chưa biết tên ("?"; "."
    nếu là chấm nhỏ trên đường chân chữ): xóa, dời được như chữ khác, chỉ không dùng làm mẫu chép.
    Dừng ở khoảng trống lớn (sang cột khác) và bỏ nét quá cao (con dấu, đường kẻ)."""
    H, W = anh.shape[:2]
    xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
    for d in cac_dong:
        y0, y1 = d.dai
        x0 = d.hop[2]
        if x0 >= W - 2 or y1 <= y0:
            continue
        vung = xam[y0:y1, x0:]
        t, _ = cv2.threshold(xam[y0:y1, d.hop[0]:d.hop[2]], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        toi = (vung < t).astype(np.uint8)
        n, _, tk, _ = cv2.connectedComponentsWithStats(toi, connectivity=8)
        co, loi0, loi1 = d.co, d.hop[1], d.hop[3]
        net = []
        for i in range(1, n):
            cx, cy, cw, ch, dt = (int(v) for v in tk[i])
            gy0, gy1 = y0 + cy, y0 + cy + ch
            if dt < 2 or ch > 1.6 * co or cw > 3 * co:
                continue
            if min(gy1, loi1) - max(gy0, loi0) < 0.5 * ch:  # không nằm trên hàng chữ của dòng
                continue
            net.append([x0 + cx, gy0, x0 + cx + cw, gy1])
        net.sort()
        # gộp nét chồng nhau theo chiều ngang (dấu thanh, nét đứt) thành một ký tự
        ky = []
        for a in net:
            if ky and a[0] <= ky[-1][2]:
                b = ky[-1]
                b[1], b[2], b[3] = min(b[1], a[1]), max(b[2], a[2]), max(b[3], a[3])
            else:
                ky.append(a)
        khoang = max(3.0, 0.3 * co)
        tu: list[list[KyTu]] = []
        cuoi = x0
        for a in ky:
            if a[0] - cuoi > 0.2 * W:  # khoảng trống lớn: sang cột khác
                break
            nho = a[3] - a[1] <= 0.45 * co and a[2] - a[0] <= 0.45 * co and abs(a[3] - d.chan) <= 0.3 * co
            c = KyTu("." if nho else "?", (a[0], a[1], a[2], a[3]), 0.0)
            if not tu or a[0] - cuoi > khoang:
                tu.append([c])
            else:
                tu[-1].append(c)
            cuoi = a[2]
        if tu:
            d.tu = d.tu + tu
            d.hop = (d.hop[0], d.hop[1], max(d.hop[2], cuoi), d.hop[3])
    return cac_dong


def thay_cham_dan(anh: np.ndarray, cac_dong: list[DongAnh]) -> list[DongAnh]:
    """Tesseract đọc dãy chấm dẫn thành hàng chục "chữ" (n, i, u…) với độ tin cậy cao: bỏ các chữ đó, thay bằng các
    dấu chấm tìm theo hình dạng, để cỡ chữ của dòng đo đúng và không lấy nhầm mẫu chép."""
    for d in cac_dong:
        cham = tim_cham_dan(anh, d)
        if not cham:
            continue
        buoc = (cham[-1][0] - cham[0][0]) / (len(cham) - 1)
        r0, r1 = cham[0][0] - buoc / 2, cham[-1][1] + buoc / 2
        y_tren = int(round(d.chan - 0.3 * d.co))
        tu = [[c for c in w if not (r0 <= (c.hop[0] + c.hop[2]) / 2 <= r1)] for w in d.tu]
        tu = [w for w in tu if w]
        truoc = [w for w in tu if w[-1].hop[2] <= r0 + buoc / 2]
        sau = [w for w in tu if w not in truoc]
        chan = int(round(d.chan))
        day = [KyTu(".", (a, max(y_tren, chan - (b - a) - 1), b, chan + 1), 100.0) for a, b in cham]
        d.tu = truoc + [day] + sau
    return cac_dong


def khe_trong_tu(cac_dong: list[DongAnh]) -> float:
    """Khe trung vị giữa hai ký tự liền nhau trong một từ (điểm ảnh)."""
    # bỏ khe cạnh dấu chấm, ký tự chưa đọc được: trang mục lục có hàng trăm khe giữa các chấm dẫn (rộng hơn khe chữ
    # nhiều), tính vào thì ký tự chèn bị giãn thưa
    khe = [b.hop[0] - a.hop[2] for d in cac_dong for w in d.tu for a, b in zip(w, w[1:])
           if a.chu not in ".?" and b.chu not in ".?"]
    return float(np.median(khe)) if khe else 1.0


# ---------------------------------------------------------------- nét mực thuộc dòng nào

def net_cua_dong(anh: np.ndarray, cac_dong: list[DongAnh], d: DongAnh, x0: int, x1: int) -> tuple[np.ndarray, np.ndarray]:
    """Phân nét mực trong vùng cột [x0, x1) × dải dòng `d`: (của dòng d, của chỗ khác). Dòng nghiêng, dòng sát nhau
    làm nét dòng trên, dòng dưới lọt vào dải: những nét đó phải đứng yên khi dời, xóa ký tự.
    Mỗi thành phần liên thông thuộc dòng có khung ký tự phủ nhiều điểm mực của nó nhất (khung ký tự của máy đọc
    gồm cả dấu thanh, dấu nặng nên dấu không bị gán nhầm sang dòng bên cạnh). Thành phần không chạm khung nào thì
    thuộc dòng có dải xiên chứa tâm nó, gần lõi chữ nhất; nét dính liền hai dòng thì tách từng điểm theo khung ký tự.
    Đường kẻ dài, nét quá cao (khung bảng, con dấu) không thuộc dòng nào: giữ nguyên."""
    y0, y1 = d.dai
    x0, x1 = max(0, x0), min(anh.shape[1], x1)
    h, w = y1 - y0, x1 - x0
    if h <= 0 or w <= 0:
        return np.zeros((max(h, 0), max(w, 0)), bool), np.zeros((max(h, 0), max(w, 0)), bool)
    xam = cv2.cvtColor(anh[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    # ngưỡng mực đo trên cả dòng (vùng hẹp chỉ toàn nền thì Otsu chia nhầm vân giấy)
    lx0, lx1 = max(0, min(x0, d.hop[0])), min(anh.shape[1], max(x1, d.hop[2]))
    t, _ = cv2.threshold(cv2.cvtColor(anh[y0:y1, lx0:lx1], cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    toi = (xam <= t).astype(np.uint8)
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(toi, connectivity=8)
    gan = [e for e in cac_dong if e.hop[2] > x0 and e.hop[0] < x1 and e.dai[1] > y0 and e.dai[0] < y1]
    if not any(e is d for e in gan):
        gan.append(d)
    # khung ký tự từng dòng: mỗi điểm ghi chỉ số dòng (−1: không khung nào, −2: khung hai dòng chồng nhau)
    khung = np.full((h, w), -1, np.int32)
    for k, e in enumerate(gan):
        for c in e.ky_tu:
            a0, b0 = max(0, c.hop[0] - x0 - 1), max(0, c.hop[1] - y0 - 1)
            a1, b1 = min(w, c.hop[2] - x0 + 1), min(h, c.hop[3] - y0 + 1)
            if a0 >= a1 or b0 >= b1:
                continue
            o = khung[b0:b1, a0:a1]
            o[(o >= 0) & (o != k)] = -2
            o[o == -1] = k
    so = len(gan)
    # đếm điểm mực từng thành phần nằm trong khung từng dòng
    m = (nhan > 0) & (khung >= 0)
    dem = np.zeros((n, so), np.int64)
    np.add.at(dem, (nhan[m], khung[m]), 1)
    chu = np.full(n, -1, np.int32)  # dòng sở hữu từng thành phần (−1: không dòng nào)
    tach = np.zeros(n, bool)        # thành phần dính hai dòng: tách từng điểm
    co = d.co
    yy = (np.arange(h) + y0)[:, None]
    for i in range(1, n):
        cx, cy, cw, ch, dt = (int(v) for v in tk[i])
        if (cw > 8 * co and ch < 0.35 * co) or ch > 2.6 * co:
            continue  # đường kẻ, khung, con dấu
        tong = dem[i].sum()
        if tong > 0:
            k = int(np.argmax(dem[i]))
            chu[i] = k
            if ch > 1.3 * co and (tong - dem[i, k]) >= 0.15 * tong:
                tach[i] = True
            continue
        # không chạm khung ký tự nào: theo dải xiên
        tx, ty = x0 + cx + cw / 2, y0 + cy + ch / 2
        tot, kc_tot = -1, None
        for k, e in enumerate(gan):
            u = e.chan_tai(tx) - ty
            if -(e.duoi or 0.3 * e.co) <= u <= (e.tren or 1.3 * e.co):
                kc = abs(u - 0.35 * e.co) / max(e.co, 1)
                if kc_tot is None or kc < kc_tot:
                    tot, kc_tot = k, kc
        chu[i] = tot
    ki = next(k for k, e in enumerate(gan) if e is d)
    cua = (chu[nhan] == ki) & (nhan > 0)
    if tach.any():
        # điểm của thành phần dính hai dòng: theo khung ký tự; ngoài khung thì theo đường chân gần nhất
        diem = tach[nhan]
        xx = (np.arange(w) + x0)[None, :]
        gan_nhat = np.full((h, w), np.inf)
        cua_ai = np.full((h, w), -1, np.int32)
        for k, e in enumerate(gan):
            kc = np.abs(e.chan + e.nghieng * (xx - e.x_chan) - 0.35 * e.co - yy) / max(e.co, 1)
            tot = kc < gan_nhat
            gan_nhat[tot], cua_ai[tot] = kc[tot], k
        ai = np.where(khung >= 0, khung, cua_ai)
        cua[diem] = ai[diem] == ki
    khac = (nhan > 0) & ~cua
    return cua, khac


# ---------------------------------------------------------------- mảnh của dòng

@dataclass
class Manh:
    """Một mảnh của dòng sau khi sửa. loai: goc (dải gốc của chính dòng), chep (ký tự chép từ chỗ khác, có thể ở
    trang khác; giữ sẵn điểm ảnh mẫu), ve (vẽ bằng phông khi cả tài liệu không có ký tự đó)."""
    loai: str
    chu: str
    x0: int = 0           # goc: dải cột trên ảnh
    x1: int = 0
    cao: int = 0          # goc: chiều cao khung ký tự (để vẽ ký tự thiếu cho cân cỡ)
    anh_mau: np.ndarray | None = field(default=None, repr=False)  # chep: điểm ảnh mẫu (cả dải dọc dòng nguồn)
    mat_mau: np.ndarray | None = field(default=None, repr=False)  # chep: chỉ các nét thuộc ký tự mẫu
    chua_chac: bool = False  # mẫu lấy từ trang khác hoặc vẽ bằng phông: nên xem lại, có thể chọn mẫu khác
    chan_mau: float = 0.0  # chep: đường chân chữ trong ảnh mẫu
    ti_le: float = 1.0    # chep: phóng, thu cho khớp cỡ dòng đích
    rong_ve: float = 0.0  # ve: bề rộng
    co_ve: float = 0.0    # ve: cỡ chữ (điểm ảnh)
    mau_muc: tuple[float, float, float] | None = None  # chep: tô bằng màu mực ở chỗ chèn (đậm nhạt đều với chữ quanh)
    diem: float = 0.0     # chep: điểm chọn mẫu (nhỏ là hợp); mẫu ghép dấu cộng thêm
    # đổi cỡ, đổi phông đoạn bôi chọn
    co_doi: float = 1.0   # tỉ lệ cỡ người dùng đặt so với cỡ gốc (phóng, thu chính nét chữ gốc)
    kieu_ve: snd.KieuChu | None = field(default=None, repr=False)  # ve: phông, kiểu, cỡ, màu người dùng chọn
    ban_goc: Manh | None = field(default=None, repr=False)  # mảnh trước khi đổi cỡ, đổi phông (để trả lại nét gốc)
    nen_muc: tuple[float, float] | None = None  # chep từ nét gốc của dòng: độ sáng nền, lõi mực đo trên cả dòng

    @property
    def rong(self) -> int:
        if self.loai == "ve":
            return int(round(self.rong_ve))
        if self.loai == "goc":
            return max(0, self.x1 - self.x0)
        return max(1, int(round(self.anh_mau.shape[1] * self.ti_le)))


def tim_cham_dan(anh: np.ndarray, d: DongAnh) -> list[tuple[int, int]]:
    """Dãy dấu chấm dẫn (mục lục) theo hình dạng: ≥ 5 chấm nhỏ cách đều, nằm trên đường chân chữ.
    Không dựa vào chữ máy đọc (ảnh mờ thường đọc dãy chấm thành chữ loạn). Trả [(x0, x1)] từng chấm."""
    y0, y1 = d.dai
    x0, x1 = d.hop[0], d.hop[2]
    xam = cv2.cvtColor(anh[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    if xam.size == 0:
        return []
    _, toi = cv2.threshold(xam, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, _, tk, _ = cv2.connectedComponentsWithStats(toi, connectivity=8)
    co = d.co
    # chấm nhỏ ở nửa dưới dòng; không so với một đường chân cố định vì bản scan nghiêng làm dãy chấm dốc dần
    cham = sorted((int(tk[i, 0]), int(tk[i, 0] + tk[i, 2]), int(y0 + tk[i, 1] + tk[i, 3])) for i in range(1, n)
                  if tk[i, 2] <= 0.45 * co and tk[i, 3] <= 0.45 * co and tk[i, 4] >= 2
                  and d.chan - 0.6 * co <= y0 + tk[i, 1] + tk[i, 3] <= d.chan + 0.4 * co)
    tot: list[tuple[int, int, int]] = []
    day = cham[:1]
    for c in cham[1:]:
        buoc = c[0] - day[-1][0]
        cung_hang = abs(c[2] - day[-1][2]) <= max(2, 0.15 * co)  # chấm liền nhau gần cùng độ cao
        if len(day) >= 2:
            # bản scan có chấm lệch nhịp, chấm mờ mất: chấp nhận bước 0,5–1,8 lần bước trung bình
            tb = (day[-1][0] - day[0][0]) / (len(day) - 1)
            hop_le = cung_hang and 0.5 * tb <= buoc <= 1.8 * tb
        else:
            hop_le = cung_hang and 0.15 * co <= buoc <= 1.2 * co
        if hop_le:
            day.append(c)
        else:
            if len(day) > len(tot):
                tot = day
            day = [c]
    if len(day) > len(tot):
        tot = day
    return [(x0 + a, x0 + b) for a, b, _ in tot] if len(tot) >= 5 else []


def manh_dong(d: DongAnh, anh: np.ndarray | None = None) -> list[Manh]:
    """Chia dòng thành các mảnh gốc liền nhau: ký tự (cắt ở giữa khe hai ký tự) và khoảng trắng giữa các từ.
    Có `anh` thì dãy chấm dẫn được thay bằng các mảnh chấm tìm theo hình dạng."""
    kq: list[Manh] = []
    for wi, w in enumerate(d.tu):
        for ci, c in enumerate(w):
            trai = c.hop[0] if ci == 0 else (w[ci - 1].hop[2] + c.hop[0]) // 2
            phai = c.hop[2] if ci == len(w) - 1 else (c.hop[2] + w[ci + 1].hop[0]) // 2
            kq.append(Manh("goc", c.chu, trai, max(trai + 1, phai), cao=c.hop[3] - c.hop[1]))
        if wi < len(d.tu) - 1:
            a, b = kq[-1].x1, d.tu[wi + 1][0].hop[0]
            kq.append(Manh("goc", " ", a, max(a + 1, b)))
    # khung ký tự đè nhau (chữ nghiêng, ghép nét, máy đọc loạn): cắt ở giữa chỗ chồng, giữ các mảnh liền nhau, không
    # chồng; mảnh rộng 0 (ký tự máy đọc thừa, khung lọt hẳn trong ký tự bên cạnh) bỏ đi. So với mảnh còn giữ gần nhất
    # chứ không chỉ mảnh liền trước: bỏ một mảnh có thể để lộ chỗ chồng với mảnh trước nữa (từ máy đọc chồng lên từ
    # sau), không xử lý thì vài cột điểm ảnh bị dán hai lần thành vệt lạ (bản Android phát hiện trên dòng PHỤ LỤC)
    gon: list[Manh] = []
    for b in kq:
        while gon and b.x0 < gon[-1].x1:
            a = gon[-1]
            b.x0 = a.x1 = max(a.x0, (a.x1 + b.x0) // 2)
            if a.x1 > a.x0:
                break
            gon.pop()
        if b.x1 > b.x0:
            gon.append(b)
    kq = gon
    cham = tim_cham_dan(anh, d) if anh is not None else []
    if cham:
        buoc = (cham[-1][0] - cham[0][0]) / (len(cham) - 1)
        cat = [int(round(cham[0][0] - buoc / 2))] + [(a[1] + b[0]) // 2 for a, b in zip(cham, cham[1:])] + [int(round(cham[-1][1] + buoc / 2))]
        r0, r1 = cat[0], cat[-1]
        truoc = [m for m in kq if m.x0 < r0]
        sau = [m for m in kq if m.x1 > r1]
        if truoc:
            truoc[-1].x1 = min(truoc[-1].x1, r0)
        if sau:
            sau[0].x0 = max(sau[0].x0, r1)
        # khoảng hở giữa mảnh cuối trước dãy chấm và dãy chấm (nếu có) gộp vào mảnh trước
        if truoc and truoc[-1].x1 < r0:
            truoc[-1].x1 = r0
        if sau and sau[0].x0 > r1:
            sau.insert(0, Manh("goc", " ", r1, sau[0].x0))
        kq = truoc + [Manh("goc", ".", a, b) for a, b in zip(cat, cat[1:])] + sau
    return kq


def manh_chep(anh: np.ndarray, d: DongAnh, c: KyTu, khe: float, ti_le: float = 1.0, chua_chac: bool = False,
              cac_dong: list[DongAnh] | None = None) -> Manh:
    """Mảnh chép từ ký tự `c` của dòng `d` trên ảnh `anh` (kèm nửa khe hai bên). Chỉ giữ các nét có phần lớn
    nằm trong khung ký tự: nét của ký tự đứng cạnh lọt vào dải cắt không bị chép theo; và chỉ nét của chính dòng
    (`cac_dong`: các dòng của trang đó): dòng nghiêng, dòng sát nhau có nét dòng trên, dòng dưới trong cùng cột."""
    x0, x1 = int(round(c.hop[0] - khe / 2)), int(round(c.hop[2] + khe / 2))
    x0, x1 = max(0, x0), min(anh.shape[1], max(x0 + 1, x1))
    y0, y1 = d.dai
    mau = anh[y0:y1, x0:x1].copy()
    _, toi = cv2.threshold(cv2.cvtColor(mau, cv2.COLOR_BGR2GRAY), 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(toi, connectivity=8)
    cx0, cx1 = c.hop[0] - x0, c.hop[2] - x0
    giu = np.zeros(n, bool)
    ky0, ky1 = c.hop[1] - y0 - 2, c.hop[3] - y0 + 2
    # chữ không dấu (trừ i, j có chấm; g, j, p, q, y có nét xuống): nét nhỏ nằm hẳn trên đỉnh thân chữ, hẳn dưới đường
    # chân là dấu của chữ bên cạnh lọt vào khung (ảnh mờ làm khung máy đọc rộng ra), không chép theo
    xh, chan = x_cao(d), d.chan_tai((c.hop[0] + c.hop[2]) / 2) - y0
    khong_dau = len(c.chu) == 1 and tach_dau(c.chu) is None and c.chu.isalnum()
    for i in range(1, n):
        trong = max(0, min(tk[i, 0] + tk[i, 2], cx1) - max(tk[i, 0], cx0))
        # khung ký tự của máy đọc gồm cả dấu của chính nó: nét nằm hẳn trên, dưới khung là dấu của chữ bên cạnh
        giu[i] = trong >= 0.5 * tk[i, 2] and tk[i, 1] < ky1 and tk[i, 1] + tk[i, 3] > ky0
        if giu[i] and khong_dau and tk[i, 3] < 0.5 * xh:
            if c.chu not in "ij" and tk[i, 1] + tk[i, 3] <= chan - (1.5 if c.chu.isupper() else 0.95) * xh:
                giu[i] = False
            elif c.chu not in "gjpqy" and tk[i, 1] >= chan + 0.15 * xh:
                giu[i] = False
    mat = giu[nhan]
    # ảnh nhòe làm chữ dính nhau thành một thành phần: trong khung ký tự thì giữ hết điểm mực của các thành phần
    # chạm khung (nét của dòng trên, dòng dưới lọt vào cùng cột thì không chạm khung, bỏ)
    cy0, cy1 = c.hop[1] - y0 - 2, c.hop[3] - y0 + 2
    cham = np.zeros(n, bool)
    for i in range(1, n):
        cham[i] = tk[i, 1] < cy1 and tk[i, 1] + tk[i, 3] > cy0 and tk[i, 0] < cx1 and tk[i, 0] + tk[i, 2] > cx0
    cot = np.zeros_like(mat)
    cot[:, max(0, cx0):max(0, cx1)] = True
    mat = mat | (cot & cham[nhan])
    cua, _ = net_cua_dong(anh, cac_dong or [d], d, x0, x1)
    mat = mat & cua
    mat = cv2.dilate(mat.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    return Manh("chep", c.chu, anh_mau=mau, mat_mau=mat, chan_mau=d.chan_tai((c.hop[0] + c.hop[2]) / 2) - y0,
                ti_le=ti_le if abs(ti_le - 1) > 0.06 else 1.0, chua_chac=chua_chac)


def do_dam(anh: np.ndarray, d: DongAnh) -> float:
    """Độ đậm nét của dòng: bề dày nét trung vị (biến đổi khoảng cách trên nét mực) chia cỡ chữ."""
    if d.dam:
        return d.dam
    y0, y1 = d.dai
    vung = cv2.cvtColor(anh[y0:y1, d.hop[0]:d.hop[2]], cv2.COLOR_BGR2GRAY)
    if vung.size == 0:
        return 0.0
    _, toi = cv2.threshold(vung, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kc = cv2.distanceTransform(toi, cv2.DIST_L2, 3)
    dinh = kc[(kc > 0) & (kc >= cv2.dilate(kc, np.ones((3, 3), np.uint8)))]  # đường giữa nét
    d.dam = float(2 * np.median(dinh) / max(d.co, 1)) if dinh.size else 0.0
    return d.dam


def x_cao(d: DongAnh) -> float:
    """Chiều cao chữ thường không dấu của dòng (đỉnh thân a, o, n… tới đường chân)."""
    return d.co_x or 0.62 * d.co


def be_day_net(toi: np.ndarray) -> float:
    """Bề dày nét trung bình của ảnh nhị phân (1 = mực): 2 × diện tích / chu vi (chu vi đếm cạnh điểm mực giáp nền
    theo 4 hướng). Mịn hơn đo bằng biến đổi khoảng cách (chỉ ra bội của 1 điểm ảnh), nên phân biệt được chữ đậm
    với chữ thường cả khi nét chỉ dày 3–4 điểm ảnh (ảnh chụp)."""
    t = np.pad(toi.astype(bool), 1)
    dien_tich = int(t.sum())
    if dien_tich == 0:
        return 0.0
    canh = int((t[1:, :] != t[:-1, :]).sum() + (t[:, 1:] != t[:, :-1]).sum())
    return 2 * dien_tich / max(canh, 1)


def dam_ky_tu(anh: np.ndarray, d: DongAnh, c: KyTu) -> float:
    """Độ đậm nét của riêng một ký tự: bề dày nét (điểm ảnh). Một dòng có thể lẫn chữ đậm, chữ thường (nhãn hàng,
    tiêu đề in đậm giữa dòng) nên không dùng độ đậm trung bình cả dòng để chọn mẫu. So hai chữ khác cỡ thì nhân tỉ lệ
    cỡ (không chia cho chiều cao chữ: trên ảnh chụp mờ, chiều cao đo theo máy đọc dao động hơn bề dày nét)."""
    if c.dam:
        return c.dam
    x0, y0, x1, y1 = c.hop
    vung = anh[max(0, y0 - 1):y1 + 1, max(0, x0 - 1):x1 + 1]
    if vung.size == 0:
        return 0.0
    _, toi = cv2.threshold(cv2.cvtColor(vung, cv2.COLOR_BGR2GRAY), 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    c.dam = be_day_net(toi)
    return c.dam


def dam_quanh(anh: np.ndarray, d: DongAnh, x: float, r: float | None = None) -> float:
    """Bề dày nét trung vị các chữ, số của dòng `d` quanh cột x (trong khoảng r, mặc định 2,5 cỡ chữ): đo một ký tự lẻ
    dao động theo dáng chữ (dấu thanh, chấm làm nét trông mảnh hơn), lấy vài chữ quanh nó thì ổn định mà vẫn phân
    biệt được từ in đậm giữa dòng chữ thường."""
    r = 2.5 * d.co if r is None else r
    v = [dam_ky_tu(anh, d, c) for c in d.ky_tu if c.chu.isalnum() and c.tin_cay >= 50 and abs((c.hop[0] + c.hop[2]) / 2 - x) <= r]
    v = [a for a in v if a > 0]
    return float(np.median(v)) if len(v) >= 2 else dam_dong(anh, d)


def dam_dong(anh: np.ndarray, d: DongAnh) -> float:
    """Bề dày nét trung vị các chữ, số của dòng (điểm ảnh)."""
    v = [dam_ky_tu(anh, d, c) for c in d.ky_tu if c.chu.isalnum() and c.tin_cay >= 50]
    v = [x for x in v if x > 0]
    return float(np.median(v)) if v else 0.0


def _hinh_ky_tu(anh: np.ndarray, c: KyTu) -> np.ndarray:
    if c.hinh is None:
        x0, y0, x1, y1 = c.hop
        vung = anh[max(0, y0):y1, max(0, x0):x1]
        if vung.size == 0:
            c.hinh = np.zeros((16, 16), np.float32)
        else:
            _, toi = cv2.threshold(cv2.cvtColor(vung, cv2.COLOR_BGR2GRAY), 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            c.hinh = cv2.resize(toi.astype(np.float32), (16, 16), interpolation=cv2.INTER_AREA)
    return c.hinh


def _la_hinh(ung_vien) -> set[int]:
    """Chỉ số các ứng viên có dáng khác hẳn các ứng viên cùng tên (≥ 3 ứng viên): thường là chỗ máy đọc nhầm (ảnh
    chụp mờ, chữ đậm đọc thành chữ khác) mà vẫn báo tin cậy cao. Chép nhầm hình là "lỗi phông" dễ thấy nhất."""
    la = set()
    nhom: dict[str, list[int]] = {}
    for i, (_, _, _, c) in enumerate(ung_vien):
        nhom.setdefault(c.chu, []).append(i)
    for ds in nhom.values():
        if len(ds) < 3:
            continue
        h = np.stack([_hinh_ky_tu(ung_vien[i][1], ung_vien[i][3]).ravel() for i in ds])
        kc = np.abs(h[:, None, :] - h[None, :, :]).mean(axis=2)
        tv = np.array([np.median(np.delete(kc[k], k)) for k in range(len(ds))])
        chuan = float(np.median(tv))
        for k, i in enumerate(ds):
            if tv[k] > max(0.22, 1.6 * chuan):
                la.add(i)
    return la


def _ung_vien(nguon, dich: DongAnh, chon, dam_dich: float | None, them=None, xet_dam: bool = True) -> list[tuple]:
    """Các ký tự mẫu hợp lệ trong `nguon` (ký tự `chon(c.chu)` đúng), xếp theo điểm tăng dần (nhỏ là hợp):
    [(điểm, trang, ảnh, dòng, ký tự, tỉ lệ cỡ)]. Loại mẫu có chiều cao, bề rộng (so với cỡ dòng của nó) khác hẳn các
    mẫu cùng tên, mẫu dáng lạ; rồi ưu tiên cỡ chữ, độ đậm nét gần chữ quanh chỗ chèn, cùng trang, cùng dòng, máy đọc
    chắc. Có mẫu đậm nhạt vừa (chênh dưới 18%) thì bỏ hẳn mẫu chênh nhiều: chữ chèn lệch đậm nhạt rất dễ thấy."""
    ung_vien = [(trang, anh, d, c) for trang, (anh, cac_dong) in enumerate(nguon) for d in cac_dong for w in d.tu for c in w
                if chon(c.chu) and c.tin_cay >= 70
                # chữ, số không thể là một nét nhỏ: loại chỗ máy đọc nhầm dấu chấm, vết bẩn thành chữ
                and (not c.chu.isalnum() or (c.hop[3] - c.hop[1] >= 0.55 * d.co and c.hop[2] - c.hop[0] >= 0.2 * d.co))]
    if not ung_vien:
        return []
    la = _la_hinh(ung_vien)
    anh_dich = nguon[0][0]
    if dam_dich is None:
        dam_dich = dam_dong(anh_dich, dich)
    kq = []
    nhom_cao: dict[str, tuple[float, float]] = {}
    for chu in {c.chu for _, _, _, c in ung_vien}:
        ds = [(c.hop[3] - c.hop[1]) / max(d.co, 1) for _, _, d, c in ung_vien if c.chu == chu]
        dr = [(c.hop[2] - c.hop[0]) / max(d.co, 1) for _, _, d, c in ung_vien if c.chu == chu]
        nhom_cao[chu] = (float(np.median(ds)), float(np.median(dr)), len(ds))
    for i, (trang, anh, d, c) in enumerate(ung_vien):
        if i in la:
            continue
        trung_cao, trung_rong, so = nhom_cao[c.chu]
        h, w = (c.hop[3] - c.hop[1]) / max(d.co, 1), (c.hop[2] - c.hop[0]) / max(d.co, 1)
        lech_hinh = abs(h - trung_cao) / max(trung_cao, 1e-6) + abs(w - trung_rong) / max(trung_rong, 1e-6)
        if so >= 3 and lech_hinh > 0.5:
            continue
        ti_le = ti_le_co(dich, d)
        lech_dam = (abs(math.log(max(dam_quanh(anh, d, (c.hop[0] + c.hop[2]) / 2) * ti_le, 1e-3) / max(dam_dich, 1e-3)))
                    if xet_dam else 0.0)
        diem = (abs(math.log(ti_le)) * 3 + lech_hinh + 4 * lech_dam + (0 if d is dich else 0.15) + (0.6 if trang else 0)
                + (100 - c.tin_cay) / 100 + (0.5 if c.chia else 0) + (them(c.chu) if them else 0))
        kq.append((diem, trang, anh, d, c, ti_le, lech_dam))
    vua = [k for k in kq if k[6] <= math.log(1.18)]
    if vua:
        kq = vua
    kq.sort(key=lambda k: k[0])
    return [k[:6] for k in kq]


def tim_ky_tu_mau(nguon: list[tuple[np.ndarray, list[DongAnh]]], dich: DongAnh, chu: str, khe: float,
                  dam_dich: float | None = None) -> Manh | None:
    """Tìm ký tự `chu` trong các trang `nguon` (trang đang sửa đứng đầu) để chép. `dam_dich`: độ đậm nét các chữ quanh
    chỗ chèn (mặc định: cả dòng đích). Mẫu lấy từ trang khác đánh dấu chưa chắc."""
    kq = _ung_vien(nguon, dich, lambda x: x == chu, dam_dich)
    if not kq:
        return None
    diem, trang, anh, d, c, ti_le = kq[0]
    dong_trang = {id(e): ds for _, ds in nguon for e in ds}
    m = manh_chep(anh, d, c, khe, ti_le, chua_chac=trang > 0, cac_dong=dong_trang.get(id(d)))
    m.diem = diem
    return m


# ---- dấu tiếng Việt: chữ có dấu không có sẵn thì ghép thân chữ với dấu chép từ chữ khác cùng trang

_DAU_TREN = "\u0300\u0301\u0303\u0309\u0302\u0306"  # huyền, sắc, ngã, hỏi, mũ, trăng
_DAU_DUOI = "\u0323"                                     # nặng
_MOC = "\u031b"                                          # móc của ơ, ư: thuộc thân chữ


def tach_dau(ch: str) -> tuple[str, str, str] | None:
    """Chữ có dấu tiếng Việt → (thân, các dấu trên, dấu dưới) dạng tổ hợp: "ố" → ("o", "\u0302\u0301", ""),
    "ợ" → ("ơ", "", "\u0323"). Thân giữ móc (ơ, ư). None nếu không phải chữ có dấu."""
    d = ud.normalize("NFD", ch)
    if len(d) < 2 or not d[0].isalpha():
        return None
    than = d[0] + "".join(x for x in d[1:] if x == _MOC)
    tren = "".join(x for x in d[1:] if x in _DAU_TREN)
    duoi = "".join(x for x in d[1:] if x in _DAU_DUOI)
    if len(than) + len(tren) + len(duoi) != len(d) or not (tren or duoi):
        return None
    return ud.normalize("NFC", than), tren, duoi


def _tach_phan(m: Manh, hoa: bool, xh: float):
    """Mặt nạ (thân, dấu trên, dấu dưới) của mẫu chép `m` (cỡ ảnh mẫu đã phóng theo tỉ lệ), chia theo thành phần
    liên thông: nằm hẳn trên đỉnh thân chữ là dấu trên, nằm hẳn dưới đường chân là dấu dưới."""
    mat = m.mat_mau.astype(np.uint8)
    # mặt nạ mẫu đã nới 1 điểm ảnh làm dấu sát thân dính vào thân: tách trên lõi (co lại), rồi nới nhãn ra như cũ
    loi = cv2.erode(mat, np.ones((3, 3), np.uint8))
    n, nhan, tk, _ = cv2.connectedComponentsWithStats(loi, connectivity=8)
    nhan = np.where(mat > 0, cv2.dilate(nhan.astype(np.float32), np.ones((3, 3), np.uint8)).astype(np.int32), 0)
    chan = m.chan_mau
    dinh = chan - (1.4 if hoa else 1.0) * xh
    loai = np.zeros(n, np.int8)  # 0 nền, 1 thân, 2 trên, 3 dưới
    for i in range(1, n):
        y0, y1 = tk[i, 1], tk[i, 1] + tk[i, 3]
        if y1 <= dinh + 0.2 * xh:
            loai[i] = 2
        elif y0 >= chan + 0.05 * xh and y1 - y0 < 0.6 * xh:
            loai[i] = 3
        else:
            loai[i] = 1
    l = loai[nhan]
    return l == 1, l == 2, l == 3


def _phong(m: Manh) -> tuple[np.ndarray, np.ndarray, float]:
    """Ảnh mẫu, mặt nạ, đường chân của mẫu chép sau khi phóng theo tỉ lệ cỡ."""
    if m.ti_le == 1.0:
        return m.anh_mau, m.mat_mau, m.chan_mau
    w, h = max(1, round(m.anh_mau.shape[1] * m.ti_le)), max(1, round(m.anh_mau.shape[0] * m.ti_le))
    return (cv2.resize(m.anh_mau, (w, h), interpolation=cv2.INTER_CUBIC),
            cv2.resize(m.mat_mau.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool), m.chan_mau * m.ti_le)


def _khung(mat: np.ndarray):
    ys, xs = np.nonzero(mat)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if ys.size else None


def ghep_dau(nguon, dich: DongAnh, ch: str, khe: float, dam_dich: float | None = None) -> Manh | None:
    """Chữ có dấu `ch` ghép từ mẫu trên trang: thân chữ (ưu tiên chữ không dấu; chữ cùng thân khác dấu thì bỏ dấu cũ)
    và cụm dấu trên, dấu dưới chép từ chữ khác có đúng các dấu ấy (ưu tiên cùng thân, cùng kiểu nét). Cụm dấu đặt
    so với thân như ở chữ nguồn (cách đỉnh thân, lệch ngang so với tâm thân). Dùng khi trang không có sẵn chữ đó hoặc
    chỉ có ở kiểu nét khác: chữ có dấu hiếm gặp (ố, ặ, ữ…) thường chỉ có một hai mẫu trên trang."""
    t = tach_dau(ch)
    if t is None:
        return None
    than, tren, duoi = t
    hoa = than[0].isupper()
    dong_trang = {id(e): ds for _, ds in nguon for e in ds}

    def mau(k):
        diem, trang, anh, d, c, ti_le = k
        m = manh_chep(anh, d, c, khe, ti_le, chua_chac=trang > 0, cac_dong=dong_trang.get(id(d)))
        anh_m, mat_m, chan_m = _phong(m)
        m2 = replace(m, anh_mau=anh_m, mat_mau=mat_m, chan_mau=chan_m, ti_le=1.0)
        return m2, _tach_phan(m2, c.chu[0].isupper(), x_cao(d) * m.ti_le), diem

    # thân
    tot_than = None
    for k in _ung_vien(nguon, dich, lambda x: x == than or (tach_dau(x) or ("",))[0] == than, dam_dich,
                       lambda x: 0 if x == than else 0.4)[:6]:
        m, (mt, mtr, md), diem = mau(k)
        td = tach_dau(k[4].chu)
        # chữ có dấu làm thân: phải tách được đúng phần dấu của nó, không thì thân còn dính dấu cũ
        if td and ((td[1] and not mtr.any()) or (td[2] and not md.any())):
            continue
        if _khung(mt) is None:
            continue
        tot_than = (m, mt, diem)
        break
    if tot_than is None:
        return None
    m_than, mat_than, diem = tot_than
    k_than = _khung(mat_than)
    anh_ra = m_than.anh_mau.copy()
    xam = cv2.cvtColor(anh_ra, cv2.COLOR_BGR2GRAY)
    nen = np.median(anh_ra[xam >= _nen(xam) - 3], axis=0)
    anh_ra[:] = nen.astype(np.uint8)
    anh_ra[mat_than] = m_than.anh_mau[mat_than]
    mat_ra = mat_than.copy()
    H, W = mat_ra.shape
    chua_chac = m_than.chua_chac
    for dau, phan in ((tren, 1), (duoi, 2)):
        if not dau:
            continue
        cung_than = lambda x, dau=dau: 0 if (tach_dau(x) or ("",))[0] == than else 0.2  # noqa: E731
        # dấu thanh nhỏ, dáng gần như nhau ở chữ đậm, chữ thường: không xét độ đậm nét khi chọn dấu
        ds = _ung_vien(nguon, dich, lambda x, dau=dau, phan=phan: (tach_dau(x) or ("", "", ""))[phan] == dau, dam_dich, cung_than,
                       xet_dam=False)
        dat = False
        for k in ds[:6]:
            m, parts, d2 = mau(k)
            mt, md = parts[0], parts[phan]
            kt, kd = _khung(mt), _khung(md)
            if kt is None or kd is None:
                continue
            # vị trí cụm dấu so với thân ở chữ nguồn → áp sang thân mới
            lech_x = (kd[0] + kd[2]) / 2 - (kt[0] + kt[2]) / 2
            if phan == 1:
                dy = (k_than[1] - (kt[1] - kd[3])) - kd[3]   # đáy dấu cách đỉnh thân như cũ
            else:
                dy = (m_than.chan_mau + (kd[1] - m.chan_mau)) - kd[1]  # đỉnh dấu cách đường chân như cũ
            dx = (k_than[0] + k_than[2]) / 2 + lech_x - (kd[0] + kd[2]) / 2
            dx, dy = int(round(dx)), int(round(dy))
            ys, xs = np.nonzero(md)
            ty, tx = ys + dy, xs + dx
            ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W)
            if ok.mean() < 0.8:
                continue
            anh_ra[ty[ok], tx[ok]] = m.anh_mau[ys[ok], xs[ok]]
            mat_ra[ty[ok], tx[ok]] = True
            chua_chac = chua_chac or m.chua_chac
            dat = True
            break
        if not dat:
            return None
    return Manh("chep", ch, anh_mau=anh_ra, mat_mau=mat_ra, chan_mau=m_than.chan_mau, chua_chac=chua_chac,
                diem=diem + 0.3)


def can_cham_dan(manh: list[Manh], rong_cu: int) -> list[Manh]:
    """Dòng có dãy dấu chấm dẫn (mục lục): bớt, thêm dấu chấm ở cuối dãy để dòng dài đúng như cũ, nên số trang cuối
    dòng đứng nguyên chỗ dù sửa chữ phía trước hay sửa chính số trang. Chấm thêm chép từ chấm cuối dãy (chấm đầu có
    thể dính đuôi chữ đứng trước). Phần lẻ dưới một chấm chia vào khe các chấm cuối dãy."""
    i = 0
    while i < len(manh):
        j = i
        while j < len(manh) and manh[j].chu == "." and manh[j].loai == "goc":
            j += 1
        if j - i >= 5:
            break
        i = j + 1
    else:
        return manh
    manh = [replace(m) for m in manh]
    lech = sum(m.rong for m in manh) - rong_cu
    while lech > 0 and j - i > 3:
        lech -= manh[j - 1].rong
        del manh[j - 1]
        j -= 1
    mau = manh[j - 1]
    while lech <= -mau.rong:
        manh.insert(j, replace(mau))
        lech += mau.rong
        j += 1
    # phần lẻ: nới, thu khe từng chấm 1 điểm ảnh, từ cuối dãy lên
    k = j - 1
    while lech != 0 and k >= i and k >= j - (j - i):
        d = 1 if lech < 0 else -1
        manh[k].x1 += d
        lech += d
        k -= 1
    return manh


# ---------------------------------------------------------------- thao tác sửa dòng

def _nen(anh_xam: np.ndarray) -> float:
    return float(np.percentile(anh_xam, 90))


@dataclass
class SuaDong:
    """Dựng lại một dòng từ các mảnh: mảnh gốc đứng yên thì không đụng tới; mảnh gốc phải dời thì chỉ nét mực của
    dòng được xóa chỗ cũ (vá nền) và dán sang chỗ mới, đi theo độ dốc của dòng; mảnh chép hòa theo độ phủ mực."""
    x0: int                 # mép trái dòng (mảnh đầu bắt đầu ở đây)
    x1_cu: int              # mép phải dòng cũ
    dai: tuple[int, int]    # dải dọc của dòng
    chan: float
    manh: list[Manh]
    chu_cu: str = ""
    kieu_chu: snd.KieuChu | None = field(default=None, repr=False)  # cho mảnh vẽ bằng phông
    nghieng: float = 0.0
    x_chan: float = 0.0
    net: np.ndarray | None = field(default=None, repr=False)   # nét của dòng, cột [x0, x1_cu) × dải (net_cua_dong)
    khac: np.ndarray | None = field(default=None, repr=False)  # nét chỗ khác trong cùng vùng

    def chan_tai(self, x: float) -> float:
        return self.chan + self.nghieng * (x - self.x_chan)

    @property
    def chu_moi(self) -> str:
        return "".join(m.chu for m in self.manh)

    def mo_ta(self) -> str:
        rut = lambda x: x if len(x) <= 40 else x[:38] + "…"  # noqa: E731
        return f"Sửa ký tự: “{rut(self.chu_cu)}” → “{rut(self.chu_moi)}”"

    def ap(self, anh: np.ndarray) -> np.ndarray:
        nguon = anh
        ra = anh.copy()
        H, W = anh.shape[:2]
        y0, y1 = self.dai
        net = self.net
        if net is None:  # thao tác tạo không qua phiên sửa: coi mọi nét trong dải là của dòng
            xam = cv2.cvtColor(anh[y0:y1, self.x0:self.x1_cu], cv2.COLOR_BGR2GRAY)
            _, net = cv2.threshold(xam, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            net = net.astype(bool)
        khac = self.khac if self.khac is not None else np.zeros_like(net)
        # viền nhòe quanh nét (1 điểm ảnh) đi cùng nét, nhưng không lấn nét chỗ khác
        net = cv2.dilate(net.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~khac
        dat, x = [], self.x0
        for m in self.manh:
            dat.append((m, x))
            x += m.rong
        x_het = min(W, max(self.x1_cu, x))
        # mảnh gốc đứng nguyên chỗ: không đụng tới (chữ không sửa giữ nguyên từng điểm ảnh)
        yen = np.zeros(max(0, x_het - self.x0), bool)
        for m, x in dat:
            if m.loai == "goc" and m.x0 == x:
                yen[max(0, x - self.x0):max(0, min(x_het, x + m.rong) - self.x0)] = True
        # xóa nét của dòng ở các cột còn lại, vá nền
        xoa = np.zeros((y1 - y0, len(yen)), np.uint8)
        c = min(net.shape[1], len(yen))
        xoa[:, :c] = net[:, :c]
        xoa[:, yen] = 0
        if xoa.any():
            vung = ra[y0:y1, self.x0:x_het]
            ra[y0:y1, self.x0:x_het] = cv2.inpaint(vung, xoa, 3, cv2.INPAINT_TELEA)
        for m, x in dat:
            w = m.rong
            if x >= W:
                break
            if m.loai == "goc":
                if m.x0 == x:
                    continue
                # dời nét của mảnh theo dòng: ngang dx, dọc theo độ dốc
                dx = x - m.x0
                dy = int(round(self.nghieng * dx))
                c0 = m.x0 - self.x0
                if c0 < 0 or c0 >= net.shape[1]:
                    continue
                ys, xs = np.nonzero(net[:, c0:min(net.shape[1], c0 + w)])
                sy, sx = ys + y0, xs + m.x0
                ty, tx = sy + dy, sx + dx
                ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W)
                # không đè lên nét dòng khác ở chỗ mới (đuôi chữ dòng trên, dấu dòng dưới)
                ry, rx = ty - y0, tx - self.x0
                trong = ok & (ry >= 0) & (ry < khac.shape[0]) & (rx >= 0) & (rx < khac.shape[1])
                ok[trong] = ~khac[ry[trong], rx[trong]]
                ra[ty[ok], tx[ok]] = nguon[sy[ok], sx[ok]]
            elif m.loai == "chep":
                self._dan_chep(nguon, ra, m, x)
            else:
                k = m.kieu_ve or self.kieu_chu
                if k is not None and m.chu.strip():
                    a, tt = snd.alpha_chu(H, W, m.chu, k.ten, k.kieu, m.co_ve or k.co_px, (x, self.chan_tai(x)), k.mo)
                    snd.ve_alpha(ra, self._tru_khac(a, tt), tt, k.mau)
        return ra

    def _tru_khac(self, a: np.ndarray, tt: tuple[int, int]) -> np.ndarray:
        """Độ phủ chữ vẽ bằng phông, bỏ chỗ trùng nét dòng khác trong dải dòng (không vẽ đè lên)."""
        if self.khac is None:
            return a
        a = a.copy()
        r0, r1 = max(tt[1], self.dai[0]), min(tt[1] + a.shape[0], self.dai[0] + self.khac.shape[0])
        c0, c1 = max(tt[0], self.x0), min(tt[0] + a.shape[1], self.x0 + self.khac.shape[1])
        if r0 < r1 and c0 < c1:
            k = self.khac[r0 - self.dai[0]:r1 - self.dai[0], c0 - self.x0:c1 - self.x0]
            a[r0 - tt[1]:r1 - tt[1], c0 - tt[0]:c1 - tt[0]][k] = 0
        return a

    def _dan_chep(self, nguon, ra, m: Manh, x: int):
        """Chép ký tự mẫu: căn theo đường chân chữ, hòa theo độ phủ mực (nền của mẫu không đè lên dòng đích)."""
        W = ra.shape[1]
        mau = m.anh_mau.astype(np.float32)
        chan_mau = m.chan_mau
        if m.ti_le != 1.0:
            mau = cv2.resize(mau, (max(1, round(mau.shape[1] * m.ti_le)), max(1, round(mau.shape[0] * m.ti_le))), interpolation=cv2.INTER_CUBIC)
            chan_mau *= m.ti_le
        xam = cv2.cvtColor(np.clip(mau, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
        nen, muc = m.nen_muc or (_nen(xam), float(np.percentile(xam, 3)))
        a = np.clip((nen - xam) / max(nen - muc, 1), 0, 1)
        if m.mat_mau is not None:
            mat = m.mat_mau.astype(np.float32)
            if m.ti_le != 1.0:
                mat = cv2.resize(mat, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_LINEAR)
            a = a * mat
        a = a[..., None]
        # đặt sao cho đường chân của mẫu trùng đường chân dòng đích tại chỗ chèn
        h, w = mau.shape[:2]
        dy = int(round(self.chan_tai(x + w / 2) - chan_mau))
        ty0, ty1 = max(0, dy), min(ra.shape[0], dy + h)
        tx0, tx1 = max(0, x), min(W, x + w)
        if ty0 >= ty1 or tx0 >= tx1:
            return
        cat_a = a[ty0 - dy:ty1 - dy, tx0 - x:tx1 - x]
        cat_m = mau[ty0 - dy:ty1 - dy, tx0 - x:tx1 - x]
        if m.mau_muc is not None:
            # tô bằng màu mực của chữ quanh chỗ chèn: mẫu chép từ chỗ ảnh sáng hơn, tối hơn vẫn đậm nhạt đều
            cat_m = np.broadcast_to(np.array(m.mau_muc, np.float32), cat_m.shape)
        if self.khac is not None:
            # không phủ lên nét dòng khác (đuôi chữ dòng trên, dấu dòng dưới lọt vào dải)
            k = np.zeros(cat_a.shape[:2], bool)
            r0, r1 = max(ty0, self.dai[0]), min(ty1, self.dai[0] + self.khac.shape[0])
            c0, c1 = max(tx0, self.x0), min(tx1, self.x0 + self.khac.shape[1])
            if r0 < r1 and c0 < c1:
                k[r0 - ty0:r1 - ty0, c0 - tx0:c1 - tx0] = self.khac[r0 - self.dai[0]:r1 - self.dai[0], c0 - self.x0:c1 - self.x0]
                cat_a = np.where(k[..., None], 0, cat_a)
        dich = ra[ty0:ty1, tx0:tx1].astype(np.float32)
        ra[ty0:ty1, tx0:tx1] = np.clip(dich * (1 - cat_a) + cat_m * cat_a, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- phiên sửa một dòng (con trỏ, gõ phím)

class PhienSuaDong:
    """Sửa một dòng bằng con trỏ: trái, phải, xóa lùi, xóa tới, gõ ký tự. Xem trước bằng `thao_tac().ap(anh)`."""

    def __init__(self, anh: np.ndarray, cac_dong: list[DongAnh], dong: DongAnh, x_bam: float | None = None,
                 trang_khac: list[tuple[np.ndarray, list[DongAnh]]] | None = None):
        """`trang_khac`: các trang khác của tài liệu (ảnh, dòng) để tìm ký tự mẫu khi trang này không có."""
        self.anh, self.cac_dong, self.dong = anh, cac_dong, dong
        self.nguon = [(anh, cac_dong)] + list(trang_khac or [])
        self.mau_tay: dict[str, Manh] = {}  # mẫu người dùng tự chọn cho từng ký tự
        self.goc = manh_dong(dong, anh)
        self.manh = list(self.goc)
        self.khe = khe_trong_tu(cac_dong)
        self.x0, self.x1_cu = self.goc[0].x0, self.goc[-1].x1
        self.net, self.khac = net_cua_dong(anh, cac_dong, dong, self.x0, self.x1_cu)
        self.con_tro = len(self.manh) if x_bam is None else self._vi_tri_gan(x_bam)
        self.moc: int | None = None  # đầu kia của đoạn bôi chọn (None: không chọn)
        self._kieu_go: tuple | None = None  # định dạng của đoạn chọn vừa xóa, cho chữ gõ thay vào
        self._kieu_chu: snd.KieuChu | None = None
        self.thieu: set[str] = set()  # ký tự không có trên trang, phải vẽ bằng phông
        y0, y1 = dong.dai
        xam = cv2.cvtColor(anh[y0:y1, self.x0:self.x1_cu], cv2.COLOR_BGR2GRAY)
        loi = xam[self.net] if self.net.any() else xam
        self.nen_muc = (_nen(xam), float(np.percentile(loi, 3)))  # cho nét gốc phóng, thu

    # vị trí con trỏ trên ảnh
    def x_con_tro(self) -> int:
        return self.x0 + sum(m.rong for m in self.manh[:self.con_tro])

    def _vi_tri_gan(self, x: float) -> int:
        bien = np.cumsum([0] + [m.rong for m in self.manh]) + self.x0
        return int(np.argmin(np.abs(bien - x)))

    def _di(self, vt: int, chon: bool = False):
        """Đặt con trỏ; `chon`: giữ đầu kia, mở rộng đoạn bôi chọn (như Shift + phím mũi tên)."""
        if chon and self.moc is None:
            self.moc = self.con_tro
        elif not chon:
            self.moc = None
        self.con_tro = max(0, min(len(self.manh), vt))
        self._kieu_go = None

    def dat_con_tro(self, x: float, chon: bool = False):
        self._di(self._vi_tri_gan(x), chon)

    def trai(self, chon: bool = False):
        a, b = self.doan_chon()
        self._di(a if b > a and not chon else self.con_tro - 1, chon)

    def phai(self, chon: bool = False):
        a, b = self.doan_chon()
        self._di(b if b > a and not chon else self.con_tro + 1, chon)

    def dau_dong(self, chon: bool = False):
        self._di(0, chon)

    def cuoi_dong(self, chon: bool = False):
        self._di(len(self.manh), chon)

    # đoạn bôi chọn
    def doan_chon(self) -> tuple[int, int]:
        """Đoạn chọn [a, b) theo chỉ số mảnh; không chọn thì a = b = con trỏ."""
        if self.moc is None:
            return self.con_tro, self.con_tro
        return min(self.moc, self.con_tro), max(self.moc, self.con_tro)

    @property
    def co_chon(self) -> bool:
        a, b = self.doan_chon()
        return b > a

    def chon_x(self, x0: float, x1: float):
        """Bôi chọn bằng chuột: từ chỗ bấm `x0` tới chỗ kéo `x1` (tọa độ ảnh)."""
        self.moc, self.con_tro = self._vi_tri_gan(x0), self._vi_tri_gan(x1)
        if self.moc == self.con_tro:
            self.moc = None

    def chon_ca_dong(self):
        self.moc, self.con_tro = 0, len(self.manh)

    def x_doan_chon(self) -> tuple[int, int]:
        a, b = self.doan_chon()
        return self.x0 + sum(m.rong for m in self.manh[:a]), self.x0 + sum(m.rong for m in self.manh[:b])

    def _xoa_chon(self) -> bool:
        a, b = self.doan_chon()
        self.moc = None
        if b <= a:
            return False
        self._kieu_go = self._kieu_cua(self.manh[a])
        del self.manh[a:b]
        self.con_tro = a
        return True

    def xoa_lui(self):
        if self._xoa_chon():
            return
        if self.con_tro > 0:
            del self.manh[self.con_tro - 1]
            self.con_tro -= 1

    def xoa_toi(self):
        if self._xoa_chon():
            return
        if self.con_tro < len(self.manh):
            del self.manh[self.con_tro]

    def go(self, chu: str):
        """Chèn `chu` ở con trỏ (đang bôi chọn thì thay đoạn chọn, chữ gõ vào giữ định dạng của đoạn đó). Chữ gõ kiểu
        tổ hợp (dấu rời, bộ gõ đặt Unicode tổ hợp) được ghép thành chữ dựng sẵn như máy đọc trả về; dấu rời gõ sau
        một chữ vừa chèn thì gộp vào chữ đó."""
        chu = ud.normalize("NFC", chu)
        if chu and not ud.combining(chu[0]):
            self._xoa_chon()
        for ch in chu:
            if ud.combining(ch):
                if self.con_tro > 0 and self.manh[self.con_tro - 1].loai != "goc":
                    gop = ud.normalize("NFC", self.manh[self.con_tro - 1].chu + ch)
                    if len(gop) == 1:
                        self.con_tro -= 1
                        self._kieu_go = self._kieu_cua(self.manh[self.con_tro])
                        self.manh[self.con_tro] = self._manh_moi(gop)
                        self.con_tro += 1
                continue
            self.manh.insert(self.con_tro, self._manh_moi(ch))
            self.con_tro += 1
            self._kieu_go = None
        self._kieu_go = None

    # ---------------------------------------------------------------- đổi cỡ, đổi phông đoạn chọn
    @staticmethod
    def _kieu_cua(m: Manh) -> tuple | None:
        """Định dạng người dùng đã đặt cho mảnh: ("ve", KieuChu) đổi phông, ("co", tỉ lệ) đổi cỡ, None giữ như gốc."""
        if m.kieu_ve is not None:
            return ("ve", m.kieu_ve)
        if abs(m.co_doi - 1) > 1e-3:
            return ("co", m.co_doi)
        return None

    def _kieu_tai_con_tro(self) -> tuple | None:
        """Chữ gõ thêm theo định dạng của chữ đứng trước con trỏ (đầu dòng thì chữ đứng sau), như trình soạn thảo."""
        if self._kieu_go is not None:
            return self._kieu_go
        if self.con_tro > 0:
            return self._kieu_cua(self.manh[self.con_tro - 1])
        return self._kieu_cua(self.manh[0]) if self.manh else None

    def _goc_sang_chep(self, m: Manh) -> Manh:
        """Mảnh gốc → mảnh chép chính nét của nó (để phóng, thu): chỉ nét mực của dòng, đo nền, mực trên cả dòng."""
        y0, y1 = self.dong.dai
        a0, a1 = m.x0 - self.x0, m.x1 - self.x0
        mat = cv2.dilate(self.net[:, a0:a1].astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~self.khac[:, a0:a1]
        return Manh("chep", m.chu, anh_mau=self.anh[y0:y1, m.x0:m.x1].copy(), mat_mau=mat,
                    chan_mau=self.dong.chan_tai((m.x0 + m.x1) / 2) - y0, nen_muc=self.nen_muc)

    def _phong_to(self, g: Manh, s: float) -> Manh:
        """Mảnh `g` (cỡ gốc) phóng, thu theo tỉ lệ `s` mà vẫn giữ nét: nét gốc, mẫu chép đổi cỡ điểm ảnh."""
        if abs(s - 1) <= 1e-3 and g.loai == "goc":
            return g
        goc = g if g.loai == "goc" else g.ban_goc
        if g.loai == "goc" and not g.chu.strip():
            return Manh("ve", g.chu, rong_ve=g.rong * s, co_doi=s, ban_goc=goc)
        if g.loai == "goc":
            return replace(self._goc_sang_chep(g), ti_le=s, co_doi=s, ban_goc=goc)
        if g.loai == "chep":
            return replace(g, ti_le=g.ti_le * s, co_doi=s, ban_goc=goc)
        co = g.co_ve or (self.kieu_chu().co_px if g.chu.strip() else 0.0)
        return replace(g, rong_ve=g.rong_ve * s, co_ve=co * s, co_doi=s, ban_goc=goc)

    def _co_goc(self, m: Manh) -> Manh:
        """Mảnh như lúc chưa đổi cỡ, đổi phông: mảnh gốc của dòng, mẫu chép ở cỡ gốc, hoặc mẫu tìm lại cho chữ gõ
        thêm bằng phông."""
        if m.ban_goc is not None:
            return m.ban_goc
        if m.loai == "goc":
            return m
        if m.kieu_ve is not None:  # chữ gõ thêm khi đang đổi phông: tìm mẫu như chữ gõ bình thường
            return self._manh_mau(m.chu)
        if m.loai == "chep":
            return replace(m, ti_le=m.ti_le / m.co_doi, co_doi=1.0)
        return replace(m, rong_ve=m.rong_ve / m.co_doi, co_ve=m.co_ve / m.co_doi, co_doi=1.0)

    def _manh_phong(self, ch: str, k: snd.KieuChu, ban_goc: Manh | None = None) -> Manh:
        return Manh("ve", ch, rong_ve=snd.do_rong(ch, k.ten, k.kieu, k.co_px), co_ve=k.co_px, kieu_ve=k, ban_goc=ban_goc)

    def dinh_dang_chon(self, ti_le: float = 1.0, kieu: snd.KieuChu | None = None):
        """Đổi định dạng đoạn bôi chọn. `kieu` None: giữ nét chữ gốc, chỉ phóng, thu theo `ti_le` (so với cỡ gốc; 1 là
        trả về như cũ, mảnh gốc đứng yên giữ nguyên từng điểm ảnh). Có `kieu`: vẽ lại đoạn chọn bằng phông, kiểu,
        cỡ, màu đó (chữ theo nội dung máy đọc, người dùng soát lại). Phần sau đoạn chọn tự dồn theo bề rộng mới."""
        a, b = self.doan_chon()
        for i in range(a, b):
            m = self.manh[i]
            g = self._co_goc(m)
            if kieu is not None:
                self.manh[i] = self._manh_phong(m.chu, kieu, g)
            else:
                self.manh[i] = self._phong_to(g, ti_le)

    def kieu_doan_chon(self, bo_phong: bool = False) -> tuple[snd.KieuChu, float, bool]:
        """Định dạng đang có của đoạn chọn: (phông, kiểu, cỡ, màu đoán trên nét gốc hoặc phông đã đặt; tỉ lệ cỡ so với
        gốc; đã đổi phông chưa). Đoán phông trên các ký tự gốc của đoạn; đoạn chỉ có chữ chèn thì đoán theo cả dòng.
        `bo_phong`: bỏ qua phông đã đặt, đoán trên nét gốc (để trả đoạn về nét gốc ở một cỡ mới)."""
        a, b = self.doan_chon()
        doan = self.manh[a:b] or self.manh[max(0, self.con_tro - 1):self.con_tro + 1]
        ve = [m.kieu_ve for m in doan if m.kieu_ve is not None]
        if ve and not bo_phong:
            return ve[0], 1.0, True
        tl = 1.0 if ve else (float(np.median([m.co_doi for m in doan])) if doan else 1.0)
        cot = [(g.x0, g.x1) for g in (self._co_goc(m) for m in doan if m.loai == "goc" or m.ban_goc is not None)
               if g.loai == "goc"]
        ky = [c for c in self.dong.ky_tu if c.chu.strip() and any(x0 <= (c.hop[0] + c.hop[2]) / 2 < x1 for x0, x1 in cot)]
        if not ky:
            return self.kieu_chu(), tl, False
        hop = (min(c.hop[0] for c in ky), min(c.hop[1] for c in ky), max(c.hop[2] for c in ky), max(c.hop[3] for c in ky))
        mat, hop_muc = snd.mat_na_muc(self.anh, hop)
        return snd.doan_kieu_chu(self.anh, "".join(c.chu for c in ky), mat, hop_muc), tl, False

    def _quanh_con_tro(self) -> list[KyTu]:
        """Các chữ gốc của dòng gần con trỏ (trong khoảng 3 cỡ chữ), để lấy độ đậm nét, màu mực tại chỗ chèn."""
        x = self.x0 + sum(m.rong for m in self.manh[:self.con_tro])
        r = 3 * self.dong.co
        gan = [c for c in self.dong.ky_tu if c.chu.isalnum() and c.tin_cay >= 50 and abs((c.hop[0] + c.hop[2]) / 2 - x) <= r]
        return gan if len(gan) >= 2 else [c for c in self.dong.ky_tu if c.chu.isalnum()]

    def dam_tai_con_tro(self) -> float:
        return dam_quanh(self.anh, self.dong, self.x0 + sum(m.rong for m in self.manh[:self.con_tro]))

    def mau_muc_tai_con_tro(self) -> tuple[float, float, float] | None:
        """Màu mực (BGR) của chữ quanh con trỏ: trung vị các điểm lõi nét (tối nhất 35%) của dòng."""
        y0, y1 = self.dong.dai
        diem = []
        for c in self._quanh_con_tro():
            a0, a1 = max(0, c.hop[0] - self.x0), min(self.net.shape[1], c.hop[2] - self.x0)
            if a1 <= a0:
                continue
            vung = self.anh[y0:y1, self.x0 + a0:self.x0 + a1]
            diem.append(vung[self.net[:, a0:a1]])
        if not diem:
            return None
        p = np.concatenate(diem)
        if len(p) < 20:
            return None
        xam = p @ np.array([0.114, 0.587, 0.299])
        loi = p[xam <= np.percentile(xam, 35)]
        return tuple(float(v) for v in np.median(loi, axis=0))

    def _manh_moi(self, ch: str) -> Manh:
        """Mảnh cho ký tự gõ vào: mẫu chép từ tài liệu, theo định dạng (đổi cỡ, đổi phông) của chữ ngay trước."""
        kieu = self._kieu_tai_con_tro()
        if kieu and kieu[0] == "ve":
            return self._manh_phong(ch, kieu[1])
        m = self._manh_mau(ch)
        return self._phong_to(m, kieu[1]) if kieu else m

    def _manh_mau(self, ch: str) -> Manh:
        if ch == " ":
            # khoảng trắng: chép khoảng trắng gốc của chính dòng (đúng bề rộng, đúng vân nền)
            trong = [m for m in self.goc if m.chu == " "]
            if trong:
                m = sorted(trong, key=lambda m: m.rong)[len(trong) // 2]
                return Manh("goc", " ", m.x0, m.x1)
            w = max(2, round(self.dong.co * 0.3))
            return Manh("ve", " ", rong_ve=w)
        if ch in self.mau_tay:
            return replace(self.mau_tay[ch], mau_muc=self.mau_muc_tai_con_tro())
        dam = self.dam_tai_con_tro()
        mau = tim_ky_tu_mau(self.nguon, self.dong, ch, self.khe, dam)
        # chữ có dấu: mẫu sẵn có mà khác kiểu nét, ở trang khác, hoặc không có thì thử ghép thân chữ với dấu cùng trang
        if tach_dau(ch) and (mau is None or mau.chua_chac or mau.diem > 0.9):
            ghep = ghep_dau(self.nguon, self.dong, ch, self.khe, dam)
            if ghep is not None and (mau is None or ghep.diem <= mau.diem + 0.3 or (mau.chua_chac and not ghep.chua_chac)):
                mau = ghep
        if mau is not None:
            mau.mau_muc = self.mau_muc_tai_con_tro()
            return mau
        self.thieu.add(ch)
        return self._manh_ve(ch)

    def _manh_ve(self, ch: str) -> Manh:
        """Vẽ ký tự thiếu bằng phông đoán được; cỡ chỉnh theo ký tự gốc đứng cạnh con trỏ (vd. "5" cao bằng "7")."""
        k = self.kieu_chu()
        co = k.co_px
        ben = [m for m in (self.manh[self.con_tro - 1:self.con_tro] + self.manh[self.con_tro:self.con_tro + 1])
               if m.loai == "goc" and m.cao and m.chu.isalnum()]
        if ben and ch.isalnum():
            _, t, _, b = snd.khung_chu(ben[0].chu, k.ten, k.kieu, k.co_px)
            if b - t > 0:
                co = float(np.clip(k.co_px * ben[0].cao / (b - t), 0.6 * k.co_px, 1.6 * k.co_px))
        return Manh("ve", ch, rong_ve=snd.do_rong(ch, k.ten, k.kieu, co) + self.khe, co_ve=co, chua_chac=True)

    def dat_mau(self, ch: str, anh: np.ndarray, d: DongAnh, c: KyTu):
        """Người dùng chọn ký tự `c` (trên ảnh `anh`, dòng `d`) làm mẫu cho `ch`: thay mọi chỗ đã chèn `ch` trong dòng."""
        cac_dong = next((ds for a, ds in self.nguon if any(e is d for e in ds)), None)
        self.mau_tay[ch] = manh_chep(anh, d, c, self.khe, ti_le_co(self.dong, d), cac_dong=cac_dong)
        self.manh = [replace(self.mau_tay[ch], mau_muc=m.mau_muc) if (m.loai != "goc" and m.chu == ch) else m
                     for m in self.manh]
        self.thieu.discard(ch)

    def kieu_chu(self) -> snd.KieuChu:
        """Phông đoán theo từ dài nhất của dòng (chỉ dùng cho ký tự trang không có)."""
        if self._kieu_chu is None:
            w = max(self.dong.tu, key=len)
            hop = (w[0].hop[0], min(c.hop[1] for c in w), w[-1].hop[2], max(c.hop[3] for c in w))
            mat, hop_muc = snd.mat_na_muc(self.anh, hop)
            self._kieu_chu = snd.doan_kieu_chu(self.anh, "".join(c.chu for c in w), mat, hop_muc)
        return self._kieu_chu

    @property
    def da_doi(self) -> bool:
        return len(self.manh) != len(self.goc) or any(a is not b for a, b in zip(self.manh, self.goc))

    def thao_tac(self) -> SuaDong:
        manh = can_cham_dan(self.manh, self.x1_cu - self.x0) if self.da_doi else list(self.manh)
        return SuaDong(self.x0, self.x1_cu, self.dong.dai, self.dong.chan, manh, self.dong.chu,
                       self._kieu_chu if any(m.loai == "ve" and m.chu.strip() and m.kieu_ve is None for m in manh) else None,
                       self.dong.nghieng, self.dong.x_chan, self.net, self.khac)

    def vuot_le(self, le_phai: int) -> bool:
        return self.x0 + sum(m.rong for m in self.thao_tac().manh) > le_phai + 2
