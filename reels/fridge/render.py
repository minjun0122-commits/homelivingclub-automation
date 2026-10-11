"""
홈리빙클럽 릴스 — 정보형 "냉장실은 60%만, 냉동실은 꽉"
근거: 한국에너지공단 냉장고 절약 요령(냉장실 60% 정도 · 냉동실은 채울수록 냉기 유지)
실제 상품 사진은 투명 용기 장면 한 곳만.
"""
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from common import (W, BG, INK, SUB, LINE, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    photo_card, canvas, end_card, render, IMGS)

PHOTO = Image.open(IMGS / "fridge/extra_3.jpg").convert("RGB")
FOODS = [(244, 196, 120), (150, 196, 130), (236, 140, 120), (200, 180, 220), (250, 220, 150), (140, 180, 210)]
COLD = (110, 170, 220)


def fridge(d, x0, y0, w, h, fill_ratio, seed=0, shelves=3):
    """냉장고 단면: 칸마다 fill_ratio 만큼 음식 상자"""
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 26, outline=LINE, width=7)
    sh = h / shelves
    for s in range(shelves):
        top = y0 + s * sh
        if s:
            d.line((x0 + 14, top, x0 + w - 14, top), fill=LINE, width=5)
        inner = w - 40
        used = inner * fill_ratio
        x = x0 + 20
        i = 0
        while x < x0 + 20 + used - 10:
            bw = min(inner * 0.2 + ((i + seed + s) % 3) * 12, x0 + 20 + used - x)
            bh = sh * (0.55 + 0.12 * ((i + s + seed) % 3)) if fill_ratio < 0.9 else sh - 22
            d.rounded_rectangle((x, top + sh - 8 - bh, x + bw - 6, top + sh - 8), 8,
                                fill=FOODS[(i + s * 2 + seed) % len(FOODS)])
            x += bw
            i += 1


def airflow(d, x0, y0, w, h, k):
    if k <= 0:
        return
    cx = x0 + w * 0.82
    for j in range(3):
        y = y0 + h * (0.18 + j * 0.32)
        pts = [(cx + 28 * math.sin((u / 20) * math.pi * 2 + j), y - 60 + u * 6 * k) for u in range(21)]
        d.line(pts, fill=COLD, width=6)
        ex, ey = pts[-1]
        d.polygon([(ex - 14, ey - 10), (ex + 14, ey - 10), (ex, ey + 12)], fill=COLD)


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 280), "냉장실은", 92)
    text(d, (W / 2, 400), "60%만 채우세요", 100, fill=OK)
    text(d, (W / 2, 500), "냉동실은 반대로 꽉", 52, fill=SUB, weight="SemiBold")
    fridge(d, 110, 620, 380, 640, 1.0, seed=1)
    fridge(d, 590, 620, 380, 640, 0.6, seed=2)
    airflow(d, 590, 620, 380, 640, 1)
    text(d, (300, 1320), "꽉 채움", 46, fill=SUB, weight="SemiBold")
    text(d, (780, 1320), "60%", 46, fill=SUB, weight="SemiBold")
    mark(d, 300, 1420, False, 1)
    mark(d, 780, 1420, True, 1)
    return img


def s_why(t):
    img, d = canvas()
    chip(d, W / 2, 250, "왜 60%일까")
    text(d, (W / 2, 400), "냉기가 돌 틈이 있어야", 80)
    text(d, (W / 2, 510), "골고루 시원해져요", 80, fill=OK, alpha=appear(t, 0.1))
    fridge(d, 290, 640, 500, 760, 0.6, seed=3)
    airflow(d, 290, 640, 500, 760, appear(t, 0.2, 0.6))
    return img


def s_freezer(t):
    img, d = canvas()
    chip(d, W / 2, 250, "냉동실은 반대")
    text(d, (W / 2, 400), "꽉 채울수록 좋아요", 88, fill=OK)
    text(d, (W / 2, 510), "얼린 음식끼리 냉기를 붙잡아요", 56, fill=SUB, weight="SemiBold", alpha=appear(t, 0.15))
    k = appear(t, 0.1, 0.5)
    fridge(d, 290, 640, 500, 640, 0.3 + 0.65 * k, seed=4, shelves=2)
    text(d, (W / 2, 1420), "냉동실은 빈틈 적게", 64, fill=COLD, alpha=appear(t, 0.6))
    return img


def s_clear(t):
    img, d = canvas()
    chip(d, W / 2, 250, "+ 정리 팁")
    text(d, (W / 2, 400), "안 보이면 또 사게 돼요", 80, fill=ACCENT)
    text(d, (W / 2, 510), "투명 용기로 칸 나누기", 80, fill=OK, alpha=appear(t, 0.15))
    photo_card(img, PHOTO, (130, 620, 950, 1440))
    return img


def s_door(t):
    img, d = canvas()
    text(d, (W / 2, 640), "한눈에 보이면", 88)
    text(d, (W / 2, 770), "문 여는 시간도 줄어요", 96, fill=OK, alpha=appear(t, 0.15))
    text(d, (W / 2, 920), "→ 냉기 덜 빠져요", 64, fill=SUB, weight="SemiBold", alpha=appear(t, 0.35))
    return img


SCENES = [
    (2.8, s_hook),
    (2.8, s_why),
    (2.8, s_freezer),
    (3.0, s_clear),
    (2.2, s_door),
    (2.8, lambda t: end_card(t, "냉장고 정리 기준", ["냉장실 60%", "냉동실은 꽉", "투명 용기로 칸 나누기"], "저장해두고 장 보고 와서 보기")),
]

if __name__ == "__main__":
    render(SCENES, HERE / "homelivingclub_fridge.mp4", HERE / "_frames")
