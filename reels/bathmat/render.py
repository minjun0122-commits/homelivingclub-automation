"""
홈리빙클럽 릴스 — 정보형 "발매트 3종류, 이렇게 달라요"
돌 규조토 / 면 매트 / 빨아쓰는 규조토 비교표가 첫 프레임에 다 보이게.
수치 주장 없이 소재 특성 비교만 (돌 규조토: 물세탁 불가·깨질 수 있음 / 면: 세탁 가능·늦게 마름)
실제 상품 사진은 한 장면만.
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from common import (W, BG, INK, SUB, LINE, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    photo_card, canvas, end_card, render, IMGS)

PHOTO = Image.open(IMGS / "bathmat/extra_khaki.jpg").convert("RGB")
COLS = ["돌 규조토", "면 매트", "빨아쓰는\n규조토"]
ROWS = [("빨리 마름", [True, False, True]),
        ("세탁 가능", [False, True, True]),
        ("깨질 걱정 없음", [False, True, True])]
STONE = (214, 206, 190)
COTTON = (236, 230, 220)
KHAKI = (150, 160, 140)


def table(d, y0, k_rows=(1, 1, 1), highlight=False):
    x_label, xs = 190, [470, 690, 900]
    if highlight:
        d.rounded_rectangle((xs[2] - 105, y0 - 90, xs[2] + 105, y0 + 120 + len(ROWS) * 150), 28, fill=(222, 240, 228))
    for x, c in zip(xs, COLS):
        d.multiline_text((x, y0), c, font=F(42, "Bold"), fill=INK, anchor="mm", align="center", spacing=6)
    for r, (lab, vals) in enumerate(ROWS):
        y = y0 + 170 + r * 150
        d.line((70, y - 75, W - 70, y - 75), fill=(220, 216, 208), width=2)
        d.text((x_label, y), lab, font=F(42, "SemiBold"), fill=SUB, anchor="mm")
        for x, v in zip(xs, vals):
            mark(d, x, y, v, k_rows[r])


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 280), "발매트 3종류", 96)
    text(d, (W / 2, 400), "이렇게 달라요", 96, fill=OK)
    table(d, 600)
    return img


def mat(d, cx, cy, w, h, color, thick=18, layers=None):
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 30, fill=color)
    d.rounded_rectangle((cx - w / 2, cy + h / 2 - 4, cx + w / 2, cy + h / 2 + thick), 10, fill=tuple(int(c * 0.8) for c in color))


def s_stone(t):
    img, d = canvas()
    chip(d, W / 2, 250, "돌 규조토")
    text(d, (W / 2, 400), "물은 빨리 마르지만", 80)
    text(d, (W / 2, 510), "물세탁 안 되고 떨어뜨리면 깨져요", 60, fill=ACCENT, alpha=appear(t, 0.15))
    k = appear(t, 0.3, 0.3)
    cx, cy = W / 2, 900
    mat(d, cx, cy, 640, 380, STONE, thick=34)
    if k > 0:   # 금 간 선
        pts = [(cx - 40, cy - 190), (cx + 10, cy - 80), (cx - 30, cy + 10), (cx + 40, cy + 120), (cx + 10, cy + 190)]
        n = max(2, int(len(pts) * k))
        d.line(pts[:n], fill=(120, 110, 100), width=7)
    return img


def s_cotton(t):
    img, d = canvas()
    chip(d, W / 2, 250, "면 매트")
    text(d, (W / 2, 400), "세탁은 편하지만", 80)
    text(d, (W / 2, 510), "젖은 채로 오래 있어요", 70, fill=ACCENT, alpha=appear(t, 0.15))
    cx, cy = W / 2, 900
    mat(d, cx, cy, 640, 380, COTTON, thick=26)
    k = appear(t, 0.25, 0.5)
    for i, (dx, dy, r) in enumerate([(-150, -40, 90), (60, 50, 110), (180, -80, 70)]):
        rr = r * k
        if rr > 0:
            d.ellipse((cx + dx - rr, cy + dy - rr * 0.7, cx + dx + rr, cy + dy + rr * 0.7), fill=(205, 200, 190))
    return img


def s_soft(t):
    img, d = canvas()
    chip(d, W / 2, 250, "빨아쓰는 규조토")
    text(d, (W / 2, 400), "둘 다 되는 3중 구조", 84, fill=OK)
    labels = [("섬유 겉감", KHAKI), ("규조토 발포층", (190, 196, 180)), ("논슬립 고무", (60, 60, 60))]
    for i, (lab, col) in enumerate(labels):
        k = appear(t, 0.1 + i * 0.15, 0.25)
        if k <= 0:
            continue
        y = 640 + i * 190
        d.rounded_rectangle((150, y, 650, y + 120), 22, fill=col)
        d.text((700, y + 60), lab, font=F(52, "Bold"), fill=INK, anchor="lm")
    text(d, (W / 2, 1300), "세탁기 OK · 깨질 걱정 없음", 60, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 300), "욕실 문 앞 60 × 40cm", 70)
    photo_card(img, PHOTO, (110, 420, 970, 1280))
    text(d, (W / 2, 1400), "세탁 후엔 그늘에서 말리기", 56, fill=SUB, weight="SemiBold", alpha=appear(t, 0.3))
    return img


def s_table_again(t):
    img, d = canvas()
    text(d, (W / 2, 330), "그래서 자취방엔", 80)
    text(d, (W / 2, 450), "빨아쓰는 규조토", 96, fill=OK)
    table(d, 650, highlight=True)
    return img


SCENES = [
    (2.8, s_hook),
    (2.6, s_stone),
    (2.6, s_cotton),
    (2.8, s_soft),
    (2.4, s_photo),
    (2.6, s_table_again),
]

if __name__ == "__main__":
    render(SCENES, HERE / "homelivingclub_bathmat.mp4", HERE / "_frames")
