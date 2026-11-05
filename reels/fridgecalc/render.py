"""
홈리빙클럽 릴스 — 폭 9.9cm 케이스 3개, 나란히 놓으면? (상품 퀴즈, 계산형)
- 상품 스펙: 슬림형 폭 9.9cm x 3 = 29.7cm, 약 30cm
- 정답: 3 약 30cm / 영상과 캡션에 "저희 스토어 상품" 표기 / 끝 화면 사진은 오너클랜 실물 사진
- BGM: piano
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
# Ebmaj7 → Dm7 → Cm7 → F7
CHORDS = [[39, 43, 46, 50], [38, 41, 45, 48], [36, 39, 43, 46], [41, 45, 48, 51]]
CARDS = [
    ("1", "약 20cm", "아니에요", False),
    ("2", "약 25cm", "아니에요", False),
    ("3", "약 30cm", "정답", True),
    ("4", "약 40cm", "아니에요", False),
]
REVEAL = [4.0, 4.4, 5.4, 4.8]  # 정답(3번)을 마지막에 공개
PHOTO = Image.open(HERE.parent.parent / "products/images/fridge/main.jpg").convert("RGB").resize((230, 230))
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440


def draw_item(d, i, cx, cy):
    w = [20, 25, 30, 40][i] * 8
    d.line((cx - 170, cy + 60, cx + 170, cy + 60), fill=(150, 155, 164), width=6)
    n = 3
    for k in range(n):
        x0 = cx - w / 2 + k * w / n
        d.rounded_rectangle((x0 + 3, cy - 40, x0 + w / n - 3, cy + 56), 8, fill=(226, 240, 248), outline=(130, 170, 195), width=4)
    d.line((cx - w / 2, cy + 100, cx + w / 2, cy + 100), fill=ACCENT, width=5)
    d.line((cx - w / 2, cy + 85, cx - w / 2, cy + 115), fill=ACCENT, width=5)
    d.line((cx + w / 2, cy + 85, cx + w / 2, cy + 115), fill=ACCENT, width=5)

def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 300), "폭 9.9cm 케이스 3개, 나란히 놓으면?", 62)
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
        text(d, (W / 2, 1490), "정답 3번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        if a > 0.5:
            img.paste(PHOTO, (110, 1570))
        text(d, (650, 1630), "9.9cm × 3개 = 29.7cm", 40, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (650, 1710), "영상 속 냉장고 정리케이스는", 36, fill=SUB, alpha=a)
        text(d, (650, 1765), "저희 스토어 상품", 36, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_fridgecalc.mp4"
    render(SCENES, silent, HERE / "_frames")
    wav = HERE / "_bgm.wav"
    bgm.make(wav, TOTAL, CHORDS, "piano")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_fridgecalc_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
