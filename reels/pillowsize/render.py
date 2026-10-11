"""
홈리빙클럽 릴스 — 사이즈 체감 "고양이 바디필로우 90cm, 실제로 이 정도예요"
- '제가 하던 것 3가지' 틀 탈피: 온라인 쇼핑에서 제일 감 안 오는 '크기'를 실제 비율로 비교
- 길이 기준: 상세페이지 표기 '귀 끝~발 끝 90cm' (봉제 특성상 1~2cm 오차)
- 비교 기준: 30cm 자 / 책상 약 73cm / 싱글 침대 200cm / 160cm 사람 — 전부 같은 장면 안에선 같은 cm 비율
- 재고는 핑크만 → 핑크 사진만 사용 (pink.png 는 v5/src/s13.jpg 에서 배경 제거)
- BGM: shampoo/bgm.py 직접 합성 피아노 (코드 진행만 다르게) → mux
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, BG, INK, SUB, ACCENT, OK, SOFT, F, appear, text, chip,  # noqa: E402
                    photo_card, canvas, render)
import bgm  # noqa: E402

PILLOW = Image.open(HERE / "pink.png").convert("RGBA")             # 세운 모습, 높이 = 90cm
PHOTO = Image.open(HERE.parent / "v5/src/s13.jpg").convert("RGB").crop((0, 250, 330, 1080))
PERSON = (196, 202, 212)
WOOD = (214, 190, 160)
BED = (226, 230, 236)
PINK = (236, 120, 150)
# Fmaj7 → Am7 → Dm7 → G (잔잔하게)
CHORDS = [[53, 57, 60, 64], [45, 48, 52, 55], [50, 53, 57, 60], [43, 47, 50, 55]]


def pillow(img, x, floor, px_cm, lying=False, k=1.0):
    """x: 왼쪽(세움) 또는 왼쪽 끝(누움). floor: 바닥 y. 90cm 를 px_cm 비율로."""
    if k <= 0:
        return
    h = int(90 * px_cm)
    sp = PILLOW.resize((int(PILLOW.width * h / PILLOW.height), h), Image.LANCZOS)
    if lying:
        sp = sp.rotate(90, expand=True)          # 머리가 왼쪽
        w = int(sp.width * k)
        sp = sp.crop((0, 0, max(w, 1), sp.height))
        img.paste(sp, (int(x), int(floor - sp.height)), sp)
    else:
        hh = int(h * k)
        sp = sp.crop((0, h - hh, sp.width, h))
        img.paste(sp, (int(x), int(floor - hh)), sp)


def person(d, cx, floor, px_cm, cm=160):
    h = cm * px_cm
    top = floor - h
    hr = h * 0.075
    d.ellipse((cx - hr, top, cx + hr, top + hr * 2), fill=PERSON)                      # 머리
    d.rounded_rectangle((cx - h * 0.13, top + hr * 2.2, cx + h * 0.13, top + h * 0.55), int(h * 0.05), fill=PERSON)
    d.rounded_rectangle((cx - h * 0.11, top + h * 0.5, cx - h * 0.015, floor), int(h * 0.03), fill=PERSON)
    d.rounded_rectangle((cx + h * 0.015, top + h * 0.5, cx + h * 0.11, floor), int(h * 0.03), fill=PERSON)


def height_tag(d, x, y, label, col=INK, anchor="lm"):
    d.line((x - 20 if anchor == "lm" else x + 20, y, x, y), fill=col, width=4)
    d.text((x + (14 if anchor == "lm" else -14), y), label, font=F(46, "Bold"), fill=col, anchor=anchor)


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 260), "고양이 바디필로우 90cm", 76)
    text(d, (W / 2, 370), "실제로 이 정도예요", 88, fill=PINK)
    floor, px = 1400, 5.0
    d.line((90, floor, W - 90, floor), fill=(200, 196, 190), width=4)
    person(d, 400, floor, px)
    pillow(img, 600, floor, px)
    d.text((400, floor - 160 * px - 45), "160cm", font=F(46, "Bold"), fill=SUB, anchor="mm")
    d.text((600 + 50, floor - 90 * px - 45), "90cm", font=F(50, "ExtraBold"), fill=PINK, anchor="mm")
    text(d, (W / 2, 1490), "세워두면 160cm 기준 골반~허리 사이", 50, fill=SUB, weight="SemiBold")
    return img


def s_ruler(t):
    img, d = canvas()
    chip(d, W / 2, 250, "30cm 자로 재면")
    text(d, (W / 2, 400), "딱 3개 길이", 92, fill=PINK)
    px, x0 = 10.0, 90
    pillow(img, x0, 900, px, lying=True, k=appear(t, 0.05, 0.3))
    for i in range(3):                                   # 30cm 자 3개
        k = appear(t, 0.3 + i * 0.15, 0.2)
        if k <= 0:
            continue
        x = x0 + i * 300
        y = 1000
        d.rectangle((x + 4, y, x + max(8, 296 * k), y + 70), fill=(250, 236, 170), outline=(200, 180, 110), width=3)
        for c in range(0, 31, 5):
            tx = x + c * 10
            if tx <= x + 296 * k:
                d.line((tx, y, tx, y + (30 if c % 10 == 0 else 18)), fill=(150, 130, 80), width=3)
        d.text((x + 150, y + 120), f"{(i + 1) * 30}cm", font=F(44, "Bold"), fill=SUB, anchor="mm")
    text(d, (W / 2, 1330), "귀 끝부터 발 끝까지", 56, fill=SUB, weight="SemiBold", alpha=appear(t, 0.7))
    return img


def s_desk(t):
    img, d = canvas()
    chip(d, W / 2, 250, "책상 옆에 세우면")
    text(d, (W / 2, 400), "책상보다 한 뼘 더 커요", 84, fill=PINK)
    floor, px = 1380, 8.0
    d.line((90, floor, W - 90, floor), fill=(200, 196, 190), width=4)
    dh = 73 * px                                          # 책상 약 73cm
    d.rectangle((130, floor - dh, 620, floor - dh + 34), fill=WOOD)
    d.rectangle((150, floor - dh + 34, 180, floor), fill=WOOD)
    d.rectangle((570, floor - dh + 34, 600, floor), fill=WOOD)
    d.text((375, floor - dh - 50), "책상 약 73cm", font=F(44, "Bold"), fill=SUB, anchor="mm")
    pillow(img, 680, floor, px, k=appear(t, 0.15, 0.4))
    if appear(t, 0.55) > 0:
        d.line((640, floor - 90 * px, 900, floor - 90 * px), fill=PINK, width=4)
        d.line((640, floor - dh, 900, floor - dh), fill=(200, 196, 190), width=4)
        d.text((915, floor - 81.5 * px), "+17cm", font=F(44, "Bold"), fill=PINK, anchor="lm")
    return img


def s_bed(t):
    img, d = canvas()
    chip(d, W / 2, 250, "싱글 침대에 눕히면")
    text(d, (W / 2, 400), "침대 길이의 절반이 안 돼요", 76, fill=PINK)
    px, x0 = 4.5, 90                                       # 침대 200cm = 900px
    y = 1060
    d.rounded_rectangle((x0, y, x0 + 200 * px, y + 120), 30, fill=BED)                 # 매트리스
    d.rounded_rectangle((x0 - 10, y - 160, x0 + 30, y + 200), 14, fill=WOOD)          # 헤드
    d.rounded_rectangle((x0 + 40, y - 60, x0 + 200, y + 10), 30, fill=(255, 255, 255))  # 베개
    pillow(img, x0 + 220, y + 10, px, lying=True, k=appear(t, 0.15, 0.35))
    d.line((x0, y + 190, x0 + 200 * px, y + 190), fill=SUB, width=3)
    d.text((x0 + 100 * px, y + 240), "싱글 침대 200cm", font=F(44, "Bold"), fill=SUB, anchor="mm")
    text(d, (W / 2, 1420), "다리 사이에 끼우고 안기 좋은 길이", 52, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 270), "실물은 이렇게 생겼어요", 70)
    photo_card(img, PHOTO, (240, 360, 840, 1260))
    text(d, (W / 2, 1340), "귀 끝~발 끝 90cm · 봉제 특성상 1~2cm 오차", 40, fill=SUB, weight="SemiBold")
    text(d, (W / 2, 1410), "영상 속 바디필로우는 저희 스토어 상품이에요", 40, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 560), "실제 크기 궁금한 상품 있으면", 66)
    text(d, (W / 2, 680), "댓글로 남겨주세요", 92, fill=PINK, alpha=appear(t, 0.1))
    text(d, (W / 2, 820), "다음 영상에서 비교해드릴게요", 56, fill=SUB, weight="SemiBold", alpha=appear(t, 0.3))
    pillow(img, W / 2 - 270, 1380, 6.0, lying=True)
    return img


SCENES = [
    (3.4, s_hook),
    (3.0, s_ruler),
    (2.8, s_desk),
    (3.0, s_bed),
    (2.8, s_photo),
    (3.0, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_pillowsize.mp4"
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
                    str(HERE / "homelivingclub_pillowsize_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
