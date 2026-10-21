"""
홈리빙클럽 릴스 — 생활 문제형 v3 "발매트 뒷면, 마지막으로 본 게 언제예요?"
- 데이터: v2 옷장 뒤 벽(질문 하나 + 큰 그림, 장면 ~2초, 13초) → 조회 154, 비팔로워 98% (지금까지 최고)
  → 같은 훅 구조를 다른 주제에 써서 포맷 효과인지 확인
- 내용: 발매트 관리 3가지 (바닥에 깔린 채 젖어 있음 / 뒷면·바닥 사이 물 / 오래 안 빨기) — 생활 상식 수준, 효능 주장 없음
- 상품: 빨아쓰는 규조토 발매트 사진 한 장 + 자사 상품 표기
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

PHOTO = Image.open(IMGS / "bathmat/extra_khaki.jpg").convert("RGB")
TILE = (226, 232, 234)
GROUT = (204, 212, 216)
MAT = (150, 160, 120)
MAT_BACK = (214, 206, 190)
MOLD = (70, 74, 64)
WATER = (150, 195, 235)
# Fmaj7 → Em7 → Dm7 → G
CHORDS = [[41, 45, 48, 52], [40, 43, 47, 50], [38, 41, 45, 48], [43, 47, 50, 55]]


def tiles(d, y0, y1, step=120):
    d.rectangle((0, y0, W, y1), fill=TILE)
    for x in range(0, W + 1, step):
        d.line((x, y0, x, y1), fill=GROUT, width=4)
    for y in range(y0, y1 + 1, step):
        d.line((0, y, W, y), fill=GROUT, width=4)


def spots(d, cx, cy, k, pts, s=1.0):
    for i, (x, y, r) in enumerate(pts):
        kk = max(0, min(1, k * 1.6 - i * 0.08))
        if kk > 0:
            rr = r * kk * s
            d.ellipse((cx + x * s - rr, cy + y * s - rr, cx + x * s + rr, cy + y * s + rr), fill=MOLD)


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 250), "발매트 뒷면,", 100)
    text(d, (W / 2, 380), "마지막으로 본 게 언제예요?", 76, fill=ACCENT)
    tiles(d, 640, 1440)
    # 뒤집힌 매트: 뒷면 + 거뭇한 점
    lift = appear(t, 0.0, 0.5)
    top = 760 - 60 * lift
    d.rounded_rectangle((170, top, W - 170, top + 520), 30, fill=MAT_BACK)
    for i in range(1, 8):                                             # 미끄럼방지 도트
        for j in range(1, 5):
            x, y = 170 + i * (W - 340) / 8, top + j * 104
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(196, 188, 172))
    spots(d, W / 2 - 120, top + 260, appear(t, 0.25, 0.5),
          [(-80, -60, 30), (20, 30, 40), (120, -80, 22), (-30, 120, 24), (170, 70, 18), (-160, 40, 16)], 1.3)
    spots(d, W / 2 + 230, top + 330, appear(t, 0.35, 0.5), [(0, 0, 22), (40, -40, 14), (-30, 50, 12)], 1.2)
    return img


def s_wet(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 샤워 후 젖은 채로 바닥에")
    text(d, (W / 2, 400), "다 쓰고 나면", 84)
    text(d, (W / 2, 510), "세워서 말리기", 92, fill=OK, alpha=appear(t, 0.1))
    tiles(d, 1300, 1440)
    k = appear(t, 0.2, 0.45)
    # 바닥에 누운 매트 → 벽/욕조에 걸쳐 세움
    if k < 0.5:
        d.rounded_rectangle((220, 1220, W - 220, 1290), 20, fill=MAT)
        for i, x in enumerate((360, 540, 720)):
            d.ellipse((x - 18, 1190 - i * 6, x + 18, 1226), fill=WATER)
    else:
        d.rectangle((640, 700, 700, 1300), fill=(220, 220, 220))      # 욕조 턱/수건걸이
        d.rounded_rectangle((420, 760, 680, 1260), 20, fill=MAT)
        for i in range(3):                                            # 바람
            y = 860 + i * 140
            d.line([(260, y), (330, y - 24), (400, y)], fill=WATER, width=6)
        mark(d, 860, 820, True, appear(t, 0.6))
    return img


def s_floor(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 매트 밑 바닥")
    text(d, (W / 2, 400), "매트만 말고", 84)
    text(d, (W / 2, 510), "바닥 물기도 닦기", 92, fill=OK, alpha=appear(t, 0.1))
    tiles(d, 700, 1400)
    lift = appear(t, 0.15, 0.4)
    # 매트를 들어 올리면 아래 고인 물
    for i, (x, y, r) in enumerate([(380, 1180, 60), (640, 1250, 46), (540, 1110, 34), (780, 1150, 28)]):
        kk = 1 - appear(t, 0.75 + i * 0.04, 0.2)                      # 닦이면서 사라짐
        if kk > 0:
            d.ellipse((x - r * 1.6 * kk, y - r * kk, x + r * 1.6 * kk, y + r * kk), fill=WATER)
    y0 = 1060 - 330 * lift
    d.rounded_rectangle((200, y0, W - 200, y0 + 260), 26, fill=MAT, outline=(120, 130, 95), width=4)
    if appear(t, 0.9) > 0:
        mark(d, W - 160, 1330, True, appear(t, 0.9))
    return img


def s_wash(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 마지막 세탁이 기억 안 나면")
    text(d, (W / 2, 400), "수건처럼", 84)
    text(d, (W / 2, 510), "주기적으로 빨기", 92, fill=OK, alpha=appear(t, 0.1))
    # 세탁기
    cx, cy = W / 2, 1000
    d.rounded_rectangle((cx - 280, cy - 330, cx + 280, cy + 330), 40, fill=(245, 245, 245),
                        outline=(200, 200, 200), width=6)
    d.ellipse((cx - 190, cy - 160, cx + 190, cy + 220), fill=(200, 210, 220))
    rot = 40 * appear(t, 0.2, 0.8)
    d.ellipse((cx - 140, cy - 110 + rot * 0.3, cx + 140, cy + 170 - rot * 0.3), fill=MAT)
    for i in range(3):
        d.ellipse((cx - 240 + i * 50, cy - 290, cx - 210 + i * 50, cy - 260), fill=(190, 190, 190))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 290), "세탁기에 넣을 수 있는 발매트", 62)
    photo_card(img, PHOTO, (130, 400, 950, 1220))
    text(d, (W / 2, 1320), "영상 속 발매트는 저희 스토어 상품이에요", 42, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 520), "지금 발매트 한 번 뒤집어보세요", 72)
    text(d, (W / 2, 650), "뒷면 어땠는지 댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    for i, s in enumerate(["세워서 말리기", "바닥 물기 닦기", "주기적으로 빨기"]):
        y = 860 + i * 150
        d.rounded_rectangle((200, y - 55, W - 200, y + 55), 28, fill=(255, 255, 255))
        d.text((260, y), f"{i + 1}", font=F(46, "ExtraBold"), fill=OK, anchor="mm")
        d.text((310, y), s, font=F(50, "Bold"), fill=INK, anchor="lm")
    text(d, (W / 2, 1360), "저장해두고 욕실 청소할 때 보기", 50, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (2.2, s_hook),
    (2.2, s_wet),
    (2.2, s_floor),
    (2.0, s_wash),
    (2.0, s_photo),
    (2.6, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_matback.mp4"
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
                    str(HERE / "homelivingclub_matback_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
