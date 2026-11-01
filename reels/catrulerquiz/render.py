"""
홈리빙클럽 릴스 — 90cm 고양이 바디필로우, 30cm 자 몇 개 길이? (상품 퀴즈 6탄, 계산형 + 고양이)
- 상품 스펙: 길이 90cm → 30cm 자 3개
- 정답: 2 3개
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음
- BGM: piano2
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
# Am7 → Dm7 → G7 → Cmaj7
CHORDS = [[45, 48, 52, 55], [38, 41, 45, 48], [43, 47, 50, 53], [36, 40, 43, 47]]
PINK, PINK_D = (244, 214, 204), (210, 170, 158)
CARDS = [
    ("1", "2개", "아니에요", False),
    ("2", "3개", "정답", True),
    ("3", "4개", "아니에요", False),
    ("4", "5개", "아니에요", False),
]
REVEAL = [4.0, 5.4, 4.4, 4.8]  # 정답(2번)을 마지막에 공개
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440


def cat(d, cx, cy, s=1.0):
    d.rounded_rectangle((cx - 150 * s, cy - 40 * s, cx + 150 * s, cy + 40 * s), int(40 * s), fill=PINK, outline=PINK_D, width=4)
    d.polygon([(cx + 100 * s, cy - 36 * s), (cx + 115 * s, cy - 70 * s), (cx + 130 * s, cy - 30 * s)], fill=PINK, outline=PINK_D)
    d.polygon([(cx + 60 * s, cy - 38 * s), (cx + 75 * s, cy - 72 * s), (cx + 92 * s, cy - 36 * s)], fill=PINK, outline=PINK_D)
    d.ellipse((cx + 72 * s, cy - 10 * s, cx + 82 * s, cy), fill=(80, 70, 70))
    d.ellipse((cx + 108 * s, cy - 10 * s, cx + 118 * s, cy), fill=(80, 70, 70))


def draw_item(d, i, cx, cy):
    cat(d, cx, cy - 40, 1.0)
    n = [2, 3, 4, 5][i]
    w = 300 / n
    for k in range(n):
        x0 = cx - 150 + k * w
        d.rectangle((x0 + 3, cy + 40, x0 + w - 3, cy + 80), fill=(250, 226, 140), outline=(200, 170, 80), width=3)
        for m in range(1, 6):
            xx = x0 + 3 + m * (w - 6) / 6
            d.line((xx, cy + 40, xx, cy + 52), fill=(160, 130, 60), width=2)

def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "90cm 고양이 바디필로우, 30cm 자로", 62)
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
        text(d, (W / 2, 1500), "정답 2번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "30cm × 3개 = 90cm", 44, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (W / 2, 1690), "영상 속 바디필로우는 저희 스토어 상품", 38, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_catrulerquiz.mp4"
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
                    str(HERE / "homelivingclub_catrulerquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
