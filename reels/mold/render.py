"""
홈리빙클럽 릴스 — 생활 문제형 v2 "옷장 뒤 벽, 마지막으로 본 게 언제예요?"
- 데이터: 생활 문제 포맷 조회 111·123 (도달 OK) but 평균 시청 0:02, 반응 0
  → 첫 프레임을 '목록'에서 '질문 하나 + 그림'으로 바꾸고, 장면 2초 안팎·전체 ~13초로 짧게
- 내용: 옷장 곰팡이 원인 3가지 (벽에 붙임 / 옷 빽빽 / 덜 마른 옷) — 일반 생활 상식 수준, 수치 주장 없음
- 상품: 벨벳 옷걸이(얇아서 옷 사이 간격 확보) 사진 한 장 + 자사 상품 표기
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

PHOTO = Image.open(IMGS / "hanger/extra_1.jpg").convert("RGB")
WALL = (232, 228, 220)
WOOD = (196, 168, 132)
WOOD_D = (160, 132, 100)
MOLD = (70, 74, 64)
CLOTHES = [(190, 214, 236), (236, 200, 190), (200, 220, 190), (230, 220, 180), (210, 200, 230)]
# Am7 → Dm7 → G → Cmaj7
CHORDS = [[45, 48, 52, 55], [50, 53, 57, 60], [43, 47, 50, 55], [48, 52, 55, 59]]


def mold(d, cx, cy, k, seed=0, spots=None, s=1.0):
    spots = spots or [(-60, -40, 26), (10, 20, 34), (70, -70, 20), (-20, 90, 22), (90, 60, 16),
                      (-100, 40, 14), (40, -130, 18)]
    spots = [(x * s, y * s, r * s) for x, y, r in spots]
    for i, (x, y, r) in enumerate(spots):
        kk = max(0, min(1, k * 1.6 - i * 0.08))
        if kk > 0:
            rr = r * kk
            d.ellipse((cx + x - rr, cy + y - rr, cx + x + rr, cy + y + rr), fill=MOLD)


def wardrobe(d, x0, y0, x1, y1):
    d.rectangle((x0, y0, x1, y1), fill=WOOD)
    d.line(((x0 + x1) / 2, y0 + 20, (x0 + x1) / 2, y1 - 20), fill=WOOD_D, width=6)
    for hx in ((x0 + x1) / 2 - 40, (x0 + x1) / 2 + 40):
        d.rounded_rectangle((hx - 8, (y0 + y1) / 2 - 50, hx + 8, (y0 + y1) / 2 + 50), 8, fill=WOOD_D)


def s_hook(t):
    img, d = canvas(WALL)
    text(d, (W / 2, 250), "옷장 뒤 벽,", 100)
    text(d, (W / 2, 380), "마지막으로 본 게 언제예요?", 76, fill=ACCENT)
    # 벽 + 옆으로 밀린 옷장 → 뒤쪽 곰팡이
    mold(d, 330, 920, 1.0, s=1.7)
    mold(d, 300, 1230, 1.0, spots=[(-30, 0, 24), (40, 30, 18), (0, 70, 14), (70, -20, 12)], s=1.6)
    shift = 120 * appear(t, 0.0, 0.5)
    wardrobe(d, 520 + shift, 640, 960 + shift, 1400)
    d.line((90, 1400, W - 90, 1400), fill=(200, 196, 190), width=6)
    return img


def s_wall(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 벽에 딱 붙인 옷장")
    text(d, (W / 2, 400), "벽이랑 주먹 하나 정도", 84)
    text(d, (W / 2, 510), "띄워두기", 92, fill=OK, alpha=appear(t, 0.1))
    d.rectangle((140, 640, 200, 1360), fill=(210, 206, 200))                     # 벽 (옆에서 본 모습)
    gap = 90 * appear(t, 0.2, 0.4)
    wardrobe(d, 200 + gap, 680, 640 + gap, 1360)
    if gap > 40:
        d.line((210, 1020, 190 + gap, 1020), fill=OK, width=6)
        for i in range(3):     # 공기 흐름
            y = 760 + i * 200
            d.line([(215, y), (215 + gap * 0.5, y - 30), (205 + gap, y)], fill=(150, 195, 235), width=6)
    return img


def s_packed(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 빽빽하게 꽉 찬 옷")
    text(d, (W / 2, 400), "옷 사이에도", 84)
    text(d, (W / 2, 510), "공기 지나갈 틈 두기", 88, fill=OK, alpha=appear(t, 0.1))
    k = appear(t, 0.15, 0.45)
    d.line((140, 700, W - 140, 700), fill=(150, 150, 150), width=10)              # 행거 봉
    n = 9
    span = 560 + 240 * k                                                          # 빽빽 → 간격
    for i in range(n):
        x = (W - span) / 2 + i * span / (n - 1)
        d.line((x, 700, x, 740), fill=(120, 120, 120), width=6)
        d.rounded_rectangle((x - 34, 740, x + 34, 1220), 16, fill=CLOTHES[i % len(CLOTHES)])
    text(d, (W / 2, 1330), "얇은 옷걸이면 같은 칸에서 틈 만들기 쉬워요", 46, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.6))
    return img


def s_damp(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 덜 마른 옷")
    text(d, (W / 2, 400), "살짝 눅눅한 채로 넣지 말고", 76)
    text(d, (W / 2, 510), "바짝 말린 뒤 넣기", 92, fill=OK, alpha=appear(t, 0.1))
    cx, cy = W / 2, 950
    pts = [(-150, -200), (-60, -230), (60, -230), (150, -200), (260, -90), (190, -20), (140, -70),
           (140, 230), (-140, 230), (-140, -70), (-190, -20), (-260, -90)]
    d.polygon([(cx + x * 1.2, cy + y * 1.2) for x, y in pts], fill=(200, 214, 228))
    for i, (dx, dy) in enumerate([(-80, -40), (60, 40), (-20, 150), (110, -110)]):
        kk = 1 - appear(t, 0.3 + i * 0.08, 0.25)                                  # 물방울 사라짐
        if kk > 0:
            r = 26 * kk
            d.ellipse((cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r), fill=(150, 195, 235))
    if appear(t, 0.7) > 0:
        mark(d, cx + 330, cy - 220, True, appear(t, 0.7))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 290), "옷 사이 틈 만들 땐 얇은 옷걸이", 62)
    photo_card(img, PHOTO, (130, 400, 950, 1220))
    text(d, (W / 2, 1320), "영상 속 벨벳 옷걸이는 저희 스토어 상품이에요", 42, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 520), "오늘 옷장 한 번 밀어보세요", 76)
    text(d, (W / 2, 650), "뒤에 뭐 있었는지 댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    for i, s in enumerate(["벽에서 띄우기", "옷 사이 틈", "바짝 말려서"]):
        y = 860 + i * 150
        d.rounded_rectangle((200, y - 55, W - 200, y + 55), 28, fill=(255, 255, 255))
        d.text((260, y), f"{i + 1}", font=F(46, "ExtraBold"), fill=OK, anchor="mm")
        d.text((310, y), s, font=F(50, "Bold"), fill=INK, anchor="lm")
    text(d, (W / 2, 1360), "저장해두고 옷장 정리할 때 보기", 50, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (2.2, s_hook),
    (2.2, s_wall),
    (2.2, s_packed),
    (2.0, s_damp),
    (2.0, s_photo),
    (2.6, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_mold.mp4"
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
                    str(HERE / "homelivingclub_mold_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
