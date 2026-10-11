"""
홈리빙클럽 릴스 — 정보형 "옷걸이만 바꿔도 옷장 봉이 14cm 남아요"
계산: (두꺼운 옷걸이 예시 1.2cm − 벨벳 슬림 0.5cm) × 20개 = 14cm  (옷걸이 두께만 비교)
실제 상품 사진은 마지막 직전 한 장면만.
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from common import (W, BG, INK, SUB, LINE, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    photo_card, canvas, floor, end_card, render, IMGS)

PX = 30          # 1cm = 30px
THICK, SLIM = 1.2, 0.5
PHOTO = Image.open(IMGS / "hanger/extra_1.jpg").convert("RGB")
HANGER_GRAY = (150, 146, 140)


def rod(d, x0, y, n, thick_cm, color, k=1.0, label=None, label_color=INK):
    """옆에서 본 옷걸이 n개를 봉에 붙여 건 모습. k: 왼쪽부터 채워지는 애니메이션"""
    d.line((x0 - 20, y, x0 + 30 * PX + 20, y), fill=LINE, width=8)           # 봉 30cm
    w = thick_cm * PX
    shown = int(round(n * k))
    for i in range(shown):
        x = x0 + i * w
        d.rectangle((x + 1, y + 6, x + w - 1, y + 150), fill=color)
    if label and k >= 1:
        used = n * w
        d.text((x0 + used / 2, y + 190), label, font=F(44, "SemiBold"), fill=label_color, anchor="mm")
    return x0 + shown * w


def gap(d, x0, x1, y, txt, a=1.0):
    if a <= 0:
        return
    d.rectangle((x0 + 4, y + 6, x1, y + 150), fill=(222, 240, 228))
    d.text(((x0 + x1) / 2, y + 78), txt, font=F(64, "ExtraBold"), fill=OK, anchor="mm")


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 280), "옷걸이만 바꿔도", 88)
    text(d, (W / 2, 400), "옷장 봉이 14cm 남아요", 88, fill=OK)
    text(d, (W / 2, 500), "옷걸이 20개 기준", 46, fill=SUB, weight="SemiBold")
    x0 = 90
    text(d, (W / 2, 640), "두꺼운 옷걸이 (예: 1.2cm)", 46, fill=SUB, weight="SemiBold")
    rod(d, x0, 700, 20, THICK, HANGER_GRAY, label="24cm")
    text(d, (W / 2, 1030), "벨벳 슬림 옷걸이 0.5cm", 46, fill=SUB, weight="SemiBold")
    end = rod(d, x0, 1090, 20, SLIM, (90, 90, 90), label="10cm")
    gap(d, end, end + (THICK - SLIM) * 20 * PX, 1090, "+14cm")
    return img


def s_thick(t):
    img, d = canvas()
    chip(d, W / 2, 250, "두께 비교")
    text(d, (W / 2, 400), "한 개당 0.7cm 차이", 92)
    base = 1300
    for cx, cm, col, lab in [(330, THICK, HANGER_GRAY, "1.2cm"), (750, SLIM, (90, 90, 90), "0.5cm")]:
        k = appear(t, 0.1, 0.3)
        w = cm * PX * 6 * (0.6 + 0.4 * k)       # 6배 확대해서 보여줌
        d.rounded_rectangle((cx - w / 2, 640, cx + w / 2, base), 12, fill=col)
        d.line((cx, 560, cx, 640), fill=LINE, width=8)
        d.arc((cx - 40, 500, cx + 40, 580), 180, 360, fill=LINE, width=8)
        d.text((cx, base + 80), lab, font=F(64, "ExtraBold"), fill=INK if cm == THICK else OK, anchor="mm")
    text(d, (W / 2, 1480), "※ 두께를 6배 확대한 그림", 40, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


def s_calc(t):
    img, d = canvas()
    text(d, (W / 2, 560), "0.7cm × 20개", 110, alpha=1)
    text(d, (W / 2, 720), "= 14cm", 150, fill=OK, weight="ExtraBold", alpha=appear(t, 0.15))
    text(d, (W / 2, 900), "옷 몇 벌이 더 들어가는 자리예요", 58, fill=SUB, weight="SemiBold", alpha=appear(t, 0.35))
    text(d, (W / 2, 1040), "옷걸이 두께만 통일해도 정리돼 보여요", 58, fill=SUB, weight="SemiBold", alpha=appear(t, 0.5))
    return img


def hanger_shape(d, cx, top, w=520, color=(90, 90, 90), width=14):
    hook_y = top
    d.arc((cx - 40, hook_y, cx + 40, hook_y + 80), 180, 360, fill=LINE, width=8)
    d.line((cx + 40, hook_y + 40, cx + 40, hook_y + 60), fill=LINE, width=8)
    neck = hook_y + 110
    d.line((cx, hook_y + 40, cx, neck), fill=LINE, width=8)
    shoulder_y = neck + 150
    d.line((cx, neck, cx - w / 2, shoulder_y), fill=color, width=width)
    d.line((cx, neck, cx + w / 2, shoulder_y), fill=color, width=width)
    d.line((cx - w / 2 + 10, shoulder_y, cx + w / 2 - 10, shoulder_y), fill=color, width=width)
    return shoulder_y


def s_knit(t):
    img, d = canvas()
    chip(d, W / 2, 250, "+ 니트 거는 법")
    text(d, (W / 2, 400), "니트는 어깨에 걸면 늘어나요", 70, fill=ACCENT)
    text(d, (W / 2, 500), "반 접어서 아래 바에 걸기", 70, fill=OK, alpha=appear(t, 0.2))
    cx = W / 2
    bar_y = hanger_shape(d, cx, 640)
    k = appear(t, 0.3, 0.4)
    knit = (236, 214, 178)
    drop = 380 * k
    d.rounded_rectangle((cx - 210, bar_y - 6, cx + 210, bar_y + 40 + drop), 18, fill=knit)
    d.rounded_rectangle((cx - 210, bar_y - 6, cx + 210, bar_y + 40 + drop * 0.85), 18, outline=(205, 180, 140), width=4)
    d.line((cx - 260, bar_y, cx + 260, bar_y), fill=(90, 90, 90), width=14)
    mark(d, cx, 1420, True, appear(t, 0.75))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 300), "벨벳이라 미끄러지지 않고", 64, fill=SUB, weight="SemiBold")
    text(d, (W / 2, 400), "두께는 0.5cm", 88, fill=OK)
    photo_card(img, PHOTO, (110, 520, 970, 1380))
    return img


SCENES = [
    (2.8, s_hook),
    (2.8, s_thick),
    (2.6, s_calc),
    (3.2, s_knit),
    (2.6, s_photo),
    (2.8, lambda t: end_card(t, "옷장 정리 전에", ["옷걸이 두께 통일", "니트는 접어서 걸기"], "저장해두고 옷장 정리할 때 보기")),
]

if __name__ == "__main__":
    render(SCENES, HERE / "homelivingclub_hanger.mp4", HERE / "_frames")
