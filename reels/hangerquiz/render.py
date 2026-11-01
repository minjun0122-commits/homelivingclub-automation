"""
홈리빙클럽 릴스 — 벨벳 옷걸이 10개를 나란히 걸면 폭은 몇 cm? (상품 퀴즈 4탄)
- 상품 스펙: 두께 0.5cm → 10개면 5cm
- 정답: 1 5cm
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음
- BGM: piano2
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, INK, SUB, ACCENT, OK, F, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

TOTAL = 7.5
# Dm7 → Am7 → Bbmaj7 → C
CHORDS = [[38, 41, 45, 48], [45, 48, 52, 55], [46, 50, 53, 57], [36, 40, 43, 48]]
VEL = (140, 150, 160)
CARDS = [
    ("1", "5cm", "정답", True),
    ("2", "10cm", "아니에요", False),
    ("3", "15cm", "아니에요", False),
    ("4", "20cm", "아니에요", False),
]
REVEAL = [5.4, 4.0, 4.4, 4.8]  # 정답(1번)을 마지막에 공개
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440


def draw_item(d, i, cx, cy):
    w = [5, 10, 15, 20][i]
    width = w * 12
    d.line((cx - 150, cy - 80, cx + 150, cy - 80), fill=(120, 125, 135), width=8)
    n = 10
    for k in range(n):
        x = cx - width / 2 + (k + 0.5) * width / n
        d.line((x, cy - 80, x, cy - 40), fill=(110, 110, 116), width=3)
        d.polygon([(x - 2, cy - 40), (x + 2, cy - 40), (x + 3, cy + 90), (x - 3, cy + 90)], fill=VEL)
    d.line((cx - width / 2, cy + 120, cx + width / 2, cy + 120), fill=ACCENT, width=5)
    d.line((cx - width / 2, cy + 105, cx - width / 2, cy + 135), fill=ACCENT, width=5)
    d.line((cx + width / 2, cy + 105, cx + width / 2, cy + 135), fill=ACCENT, width=5)


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "두께 0.5cm 옷걸이 10개, 폭은?", 66)
    text(d, (W / 2, 350), "딱 하나. 몇 번?", 104, fill=ACCENT, weight="ExtraBold")
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
        text(d, (W / 2, 1500), "정답 1번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "0.5cm × 10개 = 5cm", 44, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (W / 2, 1690), "영상 속 옷걸이는 저희 스토어 상품", 38, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_hangerquiz.mp4"
    render(SCENES, silent, HERE / "_frames")
    wav = HERE / "_bgm.wav"
    bgm.make(wav, TOTAL, CHORDS, "piano2")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_hangerquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
