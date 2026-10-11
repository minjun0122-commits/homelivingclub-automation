"""
홈리빙클럽 릴스 — 시즌 생활 문제형 "10월에 안 해두면 겨울에 후회하는 것 3가지"
- 데이터: 누구나 겪는 생활 문제 포맷이 꾸준히 100+ (149·139·111), 단 평균 시청 2초 → '지금 해야 하는 이유'로 훅 강화
- 첫 프레임에 3가지 + "3번은 추워지면 늦어요" 티저
- 주장은 일반적인 생활 상식 수준만 (땀 자국 황변 / 에어컨 송풍 건조 / 보일러 미리 점검)
- 상품: 벨벳 옷걸이 사진 한 장 + 자사 상품 표기
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
from common import (W, BG, INK, SUB, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    photo_card, canvas, render, IMGS)
import bgm  # noqa: E402

PHOTO = Image.open(IMGS / "hanger/extra_1.jpg").convert("RGB")
TODO = ["여름옷 빨아서 넣기", "에어컨 송풍으로 말리기", "보일러 미리 틀어보기"]
SHIRT = (190, 214, 236)
STAIN = (226, 204, 120)
AIR = (150, 195, 235)
BOILER = (236, 236, 232)
# Cmaj7 → Em7 → Fmaj7 → G
CHORDS = [[48, 52, 55, 59], [52, 55, 59, 62], [53, 57, 60, 64], [43, 47, 50, 55]]


def rows(d, y0):
    for i, s in enumerate(TODO):
        y = y0 + i * 170
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=(255, 255, 255))
        d.text((150, y), f"{i + 1}", font=F(52, "ExtraBold"), fill=ACCENT, anchor="mm")
        d.text((210, y), s, font=F(56, "Bold"), fill=INK, anchor="lm")


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 300), "10월에 안 해두면", 92)
    text(d, (W / 2, 420), "겨울에 후회하는 것 3가지", 88, fill=ACCENT)
    rows(d, 680)
    text(d, (W / 2, 1230), "3번은 추워지면 늦어요", 58, fill=SUB, weight="SemiBold")
    return img


def shirt(d, cx, cy, s=1.0):
    pts = [(-150, -200), (-60, -230), (60, -230), (150, -200), (260, -90), (190, -20), (140, -70),
           (140, 230), (-140, 230), (-140, -70), (-190, -20), (-260, -90)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=SHIRT)
    d.chord((cx - 60 * s, cy - 270 * s, cx + 60 * s, cy - 190 * s), 0, 180, fill=BG)


def s_clothes(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 여름옷 빨아서 넣기")
    text(d, (W / 2, 400), "한 번 입은 옷 그대로 넣으면", 70)
    text(d, (W / 2, 510), "땀 자국이 누렇게 올라와요", 78, fill=ACCENT, alpha=appear(t, 0.12))
    cx, cy = W / 2, 930
    shirt(d, cx, cy, 1.25)
    k = appear(t, 0.3, 0.4)
    if k > 0:   # 겨드랑이·목 주변 누런 자국
        for x, y, r in [(-150, -60, 60), (150, -60, 60), (0, -230, 50)]:
            rr = r * k
            d.ellipse((cx + x - rr, cy + y - rr * 0.8, cx + x + rr, cy + y + rr * 0.8), fill=STAIN)
    text(d, (W / 2, 1330), "빨아서 바짝 말린 뒤 넣기", 56, fill=OK, weight="Bold", alpha=appear(t, 0.7))
    return img


def s_ac(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 에어컨 송풍으로 말리기")
    text(d, (W / 2, 400), "그냥 끄고 커버 씌우면", 76)
    text(d, (W / 2, 510), "안에 남은 물기가 그대로", 76, fill=ACCENT, alpha=appear(t, 0.12))
    x0, x1, y0 = 170, W - 170, 720
    d.rounded_rectangle((x0, y0, x1, y0 + 230), 40, fill=(245, 245, 245), outline=(210, 210, 210), width=4)
    d.rounded_rectangle((x0 + 40, y0 + 170, x1 - 40, y0 + 200), 14, fill=(200, 200, 205))
    k = appear(t, 0.3, 0.4)
    for i in range(5):     # 송풍 바람
        if k <= 0:
            break
        x = x0 + 110 + i * 150
        pts = [(x + (16 if s % 2 else -16), y0 + 250 + s * 45 * k) for s in range(6)]
        d.line(pts, fill=AIR, width=10, joint="curve")
    text(d, (W / 2, 1330), "끄기 전에 송풍으로 한동안 말려두기", 54, fill=OK, weight="Bold", alpha=appear(t, 0.65))
    return img


def s_boiler(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 보일러 미리 틀어보기")
    text(d, (W / 2, 400), "추운 날 처음 켰는데 안 되면", 70)
    text(d, (W / 2, 510), "수리 기다리는 동안 추워요", 78, fill=ACCENT, alpha=appear(t, 0.12))
    cx, cy = W / 2, 930
    d.rounded_rectangle((cx - 230, cy - 300, cx + 230, cy + 300), 36, fill=BOILER, outline=(205, 205, 200), width=4)
    d.rounded_rectangle((cx - 150, cy - 220, cx + 150, cy - 90), 20, fill=(60, 66, 74))
    k = appear(t, 0.3, 0.4)
    temp = int(18 + 4 * k)
    d.text((cx, cy - 155), f"{temp}°C", font=F(64, "Bold"), fill=(140, 230, 170), anchor="mm")
    for i in range(3):
        d.line((cx - 120 + i * 120, cy + 300, cx - 120 + i * 120, cy + 380), fill=(170, 170, 170), width=16)
    if k > 0.6:
        mark(d, cx + 320, cy - 155, True, (k - 0.6) / 0.4)
    text(d, (W / 2, 1400), "지금 한 번 틀어서 따뜻해지는지 확인", 52, fill=OK, weight="Bold", alpha=appear(t, 0.65))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 280), "여름옷 넣을 땐", 66)
    text(d, (W / 2, 380), "얇은 옷걸이로 자리 확보", 70, fill=OK)
    photo_card(img, PHOTO, (130, 470, 950, 1290))
    text(d, (W / 2, 1390), "영상 속 벨벳 옷걸이는 저희 스토어 상품이에요", 42, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 330), "님은 몇 개 했어요?", 92)
    text(d, (W / 2, 450), "댓글로 번호 남겨주세요", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    rows(d, 700)
    text(d, (W / 2, 1250), "저장해두고 이번 주말에 하기", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (3.4, s_hook),
    (3.0, s_clothes),
    (3.0, s_ac),
    (3.2, s_boiler),
    (2.4, s_photo),
    (3.0, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_october.mp4"
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
                    str(HERE / "homelivingclub_october_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
