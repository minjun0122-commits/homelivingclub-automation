"""
홈리빙클럽 릴스 — 이 튤립 조화로 할 수 있는 건 딱 하나, 몇 번? (상품 퀴즈 5탄)
- 상품 안내: PU 소재, 줄기 속 철사로 구부려 높이 조절 가능
- 정답: 4 줄기 구부려 높이 맞추기
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음
- BGM: marimba2
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
# Cmaj7 → Am7 → Dm7 → G7
CHORDS = [[36, 40, 43, 47], [45, 48, 52, 55], [38, 41, 45, 48], [43, 47, 50, 53]]
STEM = (90, 140, 90)
CARDS = [
    ("1", "물 주면 꽃 피우기", "조화라 안 돼요", False),
    ("2", "햇볕에 두면 자라기", "조화라 안 돼요", False),
    ("3", "향기 나기", "조화라 안 돼요", False),
    ("4", "줄기 구부려 높이 맞추기", "줄기 속 철사로 OK", True),
]
REVEAL = [4.0, 4.4, 4.8, 5.4]
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440


def tulip(d, x, y, col):
    d.chord((x - 28, y - 36, x + 28, y + 28), 0, 180, fill=col)
    d.polygon([(x - 28, y - 4), (x - 18, y - 36), (x - 4, y - 12), (x + 8, y - 38), (x + 18, y - 10), (x + 28, y - 4)], fill=col)


def draw_item(d, i, cx, cy):
    col = (240, 120, 130)
    if i == 3:  # 구부러진 줄기
        d.line([(cx - 60, cy + 110), (cx - 60, cy + 20), (cx - 20, cy - 30), (cx + 60, cy - 60)], fill=STEM, width=8, joint="curve")
        tulip(d, cx + 75, cy - 75, col)
    else:
        d.line((cx, cy + 110, cx, cy - 60), fill=STEM, width=8)
        tulip(d, cx, cy - 80, col)
        if i == 0:
            d.ellipse((cx - 70, cy - 10, cx - 40, cy + 30), fill=(120, 180, 230))
        elif i == 1:
            d.ellipse((cx + 50, cy - 130, cx + 110, cy - 70), fill=(250, 196, 70))
        else:
            for k in range(3):
                d.arc((cx + 30 + k * 18, cy - 150, cx + 60 + k * 18, cy - 90), 200, 320, fill=(200, 160, 200), width=4)
    d.ellipse((cx - 30, cy + 100, cx + 30, cy + 120), fill=(225, 220, 210))


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "이 튤립 조화로 할 수 있는 건", 68)
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
        text(d, (W / 2, 1500), "정답 4번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "줄기 속 철사로 구부려 높이 조절", 44, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (W / 2, 1690), "영상 속 튤립은 저희 스토어 상품", 38, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_tulipquiz.mp4"
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
                    str(HERE / "homelivingclub_tulipquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
