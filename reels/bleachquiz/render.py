"""
홈리빙클럽 릴스 — 락스 쓸 때 의외로 많이 헷갈리는 것, 몇 번? (생활 퀴즈, 어려움 표지 시험)
- 락스 + 식초(산성) 혼합은 유독 가스 위험. 찬물 희석, 환기, 고무장갑은 권장 사항
- 정답: 4 식초 섞기 / 제목은 격자 잘림 아래(y=300)로 내린 새 틀
- BGM: marimba2
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, INK, SUB, ACCENT, OK, F, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

TOTAL = 7.5
# Bbmaj7 → Am7 → Gm7 → C7
CHORDS = [[46, 50, 53, 57], [45, 48, 52, 55], [43, 46, 50, 53], [48, 52, 55, 58]]
CARDS = [
    ("1", "찬물에 희석", "OK", False),
    ("2", "창문 열고 환기", "OK", False),
    ("3", "고무장갑 끼기", "OK", False),
    ("4", "식초 섞기", "유독 가스 위험", True),
]
REVEAL = [4.0, 4.4, 4.8, 5.4]  # 정답(4번)을 마지막에 공개
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440


def bottle(d, cx, cy, body, cap, label=None):
    d.rounded_rectangle((cx - 45, cy - 60, cx + 45, cy + 100), 16, fill=body, outline=(150, 155, 164), width=4)
    d.rectangle((cx - 20, cy - 95, cx + 20, cy - 60), fill=cap)
    if label:
        d.text((cx, cy + 20), label, font=F(26, "Bold"), fill=(70, 74, 82), anchor="mm")


def draw_item(d, i, cx, cy):
    if i == 0:   # 찬물 + 양동이
        d.polygon([(cx - 90, cy - 40), (cx + 90, cy - 40), (cx + 65, cy + 110), (cx - 65, cy + 110)], fill=(235, 238, 242), outline=(150, 155, 164))
        d.polygon([(cx - 80, cy - 5), (cx + 80, cy - 5), (cx + 65, cy + 105), (cx - 65, cy + 105)], fill=(170, 210, 240))
        d.arc((cx - 90, cy - 110, cx + 90, cy + 30), 200, 340, fill=(120, 125, 135), width=6)
    elif i == 1:  # 열린 창문
        d.rectangle((cx - 110, cy - 110, cx + 110, cy + 110), fill=(205, 232, 248), outline=(150, 155, 164), width=8)
        d.polygon([(cx, cy - 106), (cx + 90, cy - 80), (cx + 90, cy + 80), (cx, cy + 106)], fill=(240, 244, 248), outline=(150, 155, 164))
        for k in range(3):
            d.arc((cx - 90, cy - 50 + k * 40, cx - 20, cy - 10 + k * 40), 180, 360, fill=(120, 165, 200), width=5)
    elif i == 2:  # 고무장갑
        d.rounded_rectangle((cx - 55, cy - 40, cx + 55, cy + 110), 24, fill=(250, 200, 80), outline=(205, 155, 50), width=4)
        for k in range(4):
            x = cx - 50 + k * 26
            d.rounded_rectangle((x, cy - 110, x + 20, cy - 25), 10, fill=(250, 200, 80), outline=(205, 155, 50), width=3)
    else:         # 락스 + 식초
        bottle(d, cx - 60, cy, (245, 245, 245), (70, 130, 200), "락스")
        bottle(d, cx + 60, cy, (240, 225, 190), (170, 110, 60), "식초")
        d.text((cx, cy - 25), "+", font=F(46, "ExtraBold"), fill=ACCENT, anchor="mm")

def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 300), "락스 쓸 때 의외로 많이 헷갈리는 것", 62)
    text(d, (W / 2, 410), "딱 하나. 몇 번?", 104, fill=ACCENT, weight="ExtraBold")
    for i, ((n, name, why, good), (x, y)) in enumerate(zip(CARDS, POS)):
        k = appear(T, REVEAL[i], 0.25)
        border = ACCENT if (good and k > 0) else ((200, 196, 188) if k > 0 else (220, 216, 208))
        d.rounded_rectangle((x, y, x + CW, y + CH), 36, fill=(255, 255, 255), outline=border, width=8 if k > 0 else 4)
        d.ellipse((x + 24, y + 24, x + 104, y + 104), fill=INK)
        d.text((x + 64, y + 64), n, font=F(50, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        draw_item(d, i, x + CW / 2, y + 190)
        if k <= 0:
            d.text((x + CW / 2, y + 390), name, font=F(38, "Bold"), fill=INK, anchor="mm")
        else:
            d.text((x + CW / 2, y + 390), why, font=F(34, "Bold"), fill=ACCENT if good else GRAY, anchor="mm")
            cx, cy, s = x + CW - 70, y + 70, 40 * k
            if good:
                d.ellipse((cx - s, cy - s, cx + s, cy + s), outline=ACCENT, width=12)
            else:
                d.line((cx - s, cy, cx - s * 0.3, cy + s * 0.7), fill=GRAY, width=12)
                d.line((cx - s * 0.3, cy + s * 0.7, cx + s, cy - s * 0.7), fill=GRAY, width=12)
    if T < 4.0:  # 카운트다운
        n = 3 - int((T - 1.0) // 1.0) if T >= 1.0 else 3
        n = max(1, min(3, n))
        d.ellipse((W / 2 - 70, 1495 - 70, W / 2 + 70, 1495 + 70), fill=INK)
        d.text((W / 2, 1495), str(n), font=F(80, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        text(d, (W / 2, 1620), "댓글로 번호 먼저 찍기", 44, fill=SUB, weight="SemiBold")
    elif T >= 6.0:
        a = appear(T, 6.0, 0.3)
        text(d, (W / 2, 1500), "정답 4번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "락스는 다른 세제와 섞지 않기", 44, fill=SUB, weight="SemiBold", alpha=a)
    return img


SCENES = [(TOTAL, s_all)]

if __name__ == "__main__":
    if "--preview" in sys.argv:
        from PIL import Image
        ts = [0, 2.0, 3.5, 4.3, 5.2, 6.0, 7.4]
        sheet = Image.new("RGB", (len(ts) * 270, 480), (0, 0, 0))
        for i, T in enumerate(ts):
            sheet.paste(s_all(T / TOTAL).resize((270, 480)), (i * 270, 0))
        sheet.save(HERE / "_preview.jpg", quality=85)
        sys.exit()
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_bleachquiz.mp4"
    render(SCENES, silent, HERE / "_frames")
    wav = HERE / "_bgm.wav"
    bgm.make(wav, TOTAL, CHORDS, "marimba2")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_bleachquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
