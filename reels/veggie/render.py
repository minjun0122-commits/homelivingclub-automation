"""
홈리빙클럽 릴스 — 생활 문제형 v4 "냉장고 야채칸, 마지막으로 다 꺼내본 게 언제예요?"
- 데이터: 질문 하나 + 큰 그림 훅 → 옷장 뒤 벽 154, 발매트 뒷면 115 (둘 다 비팔로워 97~98%) → 같은 훅 유지
- 내용: 야채칸 관리 3가지 (봉지째 / 밑에 깔린 것 / 바닥 물기) — 생활 상식 수준, 신선도·보관기간 수치 주장 없음
- 상품: 투명 냉장고 정리 용기 사진 한 장 + 자사 상품 표기 ("안이 보인다"만 말함)
- BGM: shampoo/bgm.py 직접 합성 피아노 → mux
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, BG, INK, SUB, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    photo_card, canvas, render, IMGS)
import bgm  # noqa: E402

PHOTO = Image.open(IMGS / "fridge/main.jpg").convert("RGB")
FRIDGE = (236, 240, 242)
DRAWER = (214, 226, 232)
EDGE = (180, 196, 204)
GREEN = (120, 170, 100)
CARROT = (236, 140, 70)
WILT = (120, 116, 80)
BAG = (250, 250, 250)
WATER = (150, 195, 235)
# Dm7 → G7 → Cmaj7 → Am7
CHORDS = [[38, 41, 45, 48], [43, 47, 50, 53], [48, 52, 55, 59], [45, 48, 52, 55]]


def drawer(d, x0, y0, x1, y1):
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=DRAWER, outline=EDGE, width=6)
    d.rounded_rectangle(((x0 + x1) / 2 - 90, y0 + 14, (x0 + x1) / 2 + 90, y0 + 40), 12, fill=EDGE)


def leaf(d, cx, cy, s=1.0, col=GREEN):
    d.ellipse((cx - 70 * s, cy - 40 * s, cx + 70 * s, cy + 40 * s), fill=col)
    d.line((cx - 60 * s, cy, cx + 60 * s, cy), fill=(255, 255, 255), width=max(2, int(4 * s)))


def carrot(d, cx, cy, s=1.0):
    d.polygon([(cx - 90 * s, cy - 22 * s), (cx + 90 * s, cy), (cx - 90 * s, cy + 22 * s)], fill=CARROT)
    d.ellipse((cx - 120 * s, cy - 20 * s, cx - 80 * s, cy + 20 * s), fill=GREEN)


def s_hook(t):
    img, d = canvas(FRIDGE)
    text(d, (W / 2, 250), "냉장고 야채칸,", 100)
    text(d, (W / 2, 380), "마지막으로 다 꺼내본 게 언제예요?", 68, fill=ACCENT)
    k = appear(t, 0.0, 0.5)
    y = 640 - 60 * k                                                  # 서랍이 살짝 열림
    drawer(d, 70, y, W - 70, y + 820)
    leaf(d, 330, y + 230, 1.9)
    carrot(d, 720, y + 220, 1.8)
    # 맨 밑에 깔린 시든 채소 (점점 드러남)
    kk = appear(t, 0.3, 0.5)
    if kk > 0:
        leaf(d, 440, y + 560, 2.6 * kk, WILT)
        for x, yy, r in ((360, y + 530, 26), (500, y + 590, 20), (440, y + 620, 14), (540, y + 520, 12)):
            d.ellipse((x - r * kk, yy - r * kk, x + r * kk, yy + r * kk), fill=(80, 76, 56))
        text(d, (800, y + 570), "?", 160, fill=ACCENT, alpha=kk)
    return img


def s_bag(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 마트 봉지째 넣기")
    text(d, (W / 2, 400), "봉지 안 물기 맺히기 전에", 76)
    text(d, (W / 2, 510), "꺼내서 정리해 넣기", 92, fill=OK, alpha=appear(t, 0.1))
    k = appear(t, 0.2, 0.5)
    cx, cy = W / 2, 980
    # 봉지 → 사라지고 채소만
    if k < 0.5:
        d.rounded_rectangle((cx - 260, cy - 240, cx + 260, cy + 260), 40, fill=BAG, outline=(210, 210, 210), width=6)
        for x, y in ((-120, -60), (90, 40), (-30, 140), (150, -130)):
            d.ellipse((cx + x - 16, cy + y - 22, cx + x + 16, cy + y + 22), fill=WATER)
    else:
        leaf(d, cx - 150, cy - 40, 1.3)
        carrot(d, cx + 150, cy + 60, 1.2)
        mark(d, cx + 320, cy - 260, True, appear(t, 0.7))
    return img


def s_bottom(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 맨 밑에 깔린 채소")
    text(d, (W / 2, 400), "먼저 산 건", 84)
    text(d, (W / 2, 510), "위로, 앞으로", 92, fill=OK, alpha=appear(t, 0.1))
    drawer(d, 130, 700, W - 130, 1340)
    k = appear(t, 0.2, 0.5)
    # 밑에 있던 것(오래된 것)이 위로 올라오고, 새것이 아래로
    old_y = 1180 - 300 * k
    new_y = 900 + 280 * k
    carrot(d, 640, new_y, 1.3)
    leaf(d, 420, old_y, 1.3, (170, 180, 110))
    text(d, (420, old_y + 95), "먼저 산 것", 40, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_wipe(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 칸 바닥에 고인 물")
    text(d, (W / 2, 400), "다 꺼낸 김에", 84)
    text(d, (W / 2, 510), "바닥 한 번 닦기", 92, fill=OK, alpha=appear(t, 0.1))
    drawer(d, 130, 700, W - 130, 1340)
    for i, (x, y, r) in enumerate([(360, 1220, 60), (620, 1250, 46), (800, 1200, 30), (480, 1160, 26)]):
        kk = 1 - appear(t, 0.35 + i * 0.07, 0.25)
        if kk > 0:
            d.ellipse((x - r * 1.6 * kk, y - r * kk, x + r * 1.6 * kk, y + r * kk), fill=WATER)
    # 행주
    k = appear(t, 0.3, 0.6)
    hx = 260 + 560 * k
    d.rounded_rectangle((hx - 90, 1150, hx + 90, 1250), 20, fill=(240, 200, 120))
    if appear(t, 0.9) > 0:
        mark(d, W - 160, 640, True, appear(t, 0.9))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 290), "안에 뭐 있는지 보이게, 투명 용기", 60)
    photo_card(img, PHOTO, (130, 400, 950, 1220))
    text(d, (W / 2, 1320), "영상 속 정리 용기는 저희 스토어 상품이에요", 42, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 520), "오늘 야채칸 한 번 다 꺼내보세요", 70)
    text(d, (W / 2, 650), "맨 밑에서 뭐 나왔는지 댓글로", 66, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    for i, s in enumerate(["봉지에서 꺼내기", "먼저 산 건 앞으로", "바닥 물기 닦기"]):
        y = 860 + i * 150
        d.rounded_rectangle((200, y - 55, W - 200, y + 55), 28, fill=(255, 255, 255))
        d.text((260, y), f"{i + 1}", font=F(46, "ExtraBold"), fill=OK, anchor="mm")
        d.text((310, y), s, font=F(50, "Bold"), fill=INK, anchor="lm")
    text(d, (W / 2, 1360), "저장해두고 장 보고 온 날 보기", 50, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (2.2, s_hook),
    (2.2, s_bag),
    (2.2, s_bottom),
    (2.0, s_wipe),
    (2.0, s_photo),
    (2.6, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_veggie.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total, CHORDS)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_veggie_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
