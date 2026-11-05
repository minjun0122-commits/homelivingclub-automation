"""
홈리빙클럽 릴스 — 옷걸이 20개 14,800원이면 개당 얼마? (상품 퀴즈, 계산형)
- 상품 옵션: 벨벳 옷걸이 20개 14,800원 (9,900 + 4,900), 14,800 / 20 = 740원
- 정답: 2 740원 / 상품명과 "저희 스토어 상품"을 0초부터 표기 / 작은 사진은 오너클랜 실물 사진
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
# Dmaj7 → Bm7 → Em7 → A7
CHORDS = [[38, 42, 45, 49], [35, 38, 42, 45], [40, 43, 47, 50], [33, 37, 40, 43]]
CARDS = [
    ("1", "540원", "540원", False),
    ("2", "740원", "740원", True),
    ("3", "940원", "940원", False),
    ("4", "1,140원", "1,140원", False),
]
REVEAL = [4.0, 5.4, 4.4, 4.8]  # 정답(2번)을 마지막에 공개
PHOTO = Image.open(HERE.parent.parent / "products/images/hanger/main.jpg").convert("RGB").resize((80, 80))
GRAY = (170, 166, 158)
POS = [(90, 590), (550, 590), (90, 1010), (550, 1010)]
CW, CH = 440, 400


def draw_item(d, i, cx, cy):
    col = (70, 72, 78)
    d.arc((cx - 24, cy - 110, cx + 24, cy - 62), 180, 60, fill=(150, 155, 164), width=7)
    d.line((cx, cy - 64, cx, cy - 38), fill=(150, 155, 164), width=7)
    d.line((cx, cy - 38, cx - 150, cy + 40), fill=col, width=16)
    d.line((cx, cy - 38, cx + 150, cy + 40), fill=col, width=16)
    d.line((cx - 150, cy + 40, cx + 150, cy + 40), fill=col, width=16)
    d.text((cx, cy + 92), "× 1개", font=F(36, "SemiBold"), fill=(150, 146, 138), anchor="mm")

def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 300), "옷걸이 20개 14,800원이면", 62)
    text(d, (W / 2, 400), "개당 얼마? 몇 번?", 92, fill=ACCENT, weight="ExtraBold")
    # 상품 표기: 0초부터 끝까지
    d.rounded_rectangle((170, 462, 910, 566), 26, fill=(255, 255, 255), outline=(220, 216, 208), width=3)
    img.paste(PHOTO, (182, 474))
    d.text((280, 494), "저희 스토어 상품", font=F(34, "ExtraBold"), fill=ACCENT, anchor="lm")
    d.text((280, 536), "벨벳 옷걸이 20개 옵션", font=F(32, "SemiBold"), fill=INK, anchor="lm")
    for i, ((n, name, why, good), (x, y)) in enumerate(zip(CARDS, POS)):
        k = appear(T, REVEAL[i], 0.25)
        border = ACCENT if (good and k > 0) else ((200, 196, 188) if k > 0 else (220, 216, 208))
        d.rounded_rectangle((x, y, x + CW, y + CH), 36, fill=(255, 255, 255), outline=border, width=8 if k > 0 else 4)
        d.ellipse((x + 24, y + 24, x + 104, y + 104), fill=INK)
        d.text((x + 64, y + 64), n, font=F(50, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        draw_item(d, i, x + CW / 2, y + 180)
        if k <= 0:
            d.text((x + CW / 2, y + 355), name, font=F(38, "Bold"), fill=INK, anchor="mm")
        else:
            d.text((x + CW / 2, y + 355), why, font=F(34, "Bold"), fill=ACCENT if good else GRAY, anchor="mm")
            cx, cy, s = x + CW - 70, y + 70, 40 * k
            if good:
                d.ellipse((cx - s, cy - s, cx + s, cy + s), outline=ACCENT, width=12)
            else:
                d.line((cx - s * 0.7, cy - s * 0.7, cx + s * 0.7, cy + s * 0.7), fill=GRAY, width=12)
                d.line((cx - s * 0.7, cy + s * 0.7, cx + s * 0.7, cy - s * 0.7), fill=GRAY, width=12)
    if T < 4.0:  # 카운트다운
        n = 3 - int((T - 1.0) // 1.0) if T >= 1.0 else 3
        n = max(1, min(3, n))
        d.ellipse((W / 2 - 70, 1495 - 70, W / 2 + 70, 1495 + 70), fill=INK)
        d.text((W / 2, 1495), str(n), font=F(80, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        text(d, (W / 2, 1620), "댓글로 번호 먼저 찍기", 44, fill=SUB, weight="SemiBold")
    elif T >= 6.0:
        a = appear(T, 6.0, 0.3)
        text(d, (W / 2, 1490), "정답 2번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1600), "14,800원 ÷ 20개 = 740원", 50, fill=INK, weight="Bold", alpha=a)
        text(d, (W / 2, 1690), "10개 옵션은 9,900원, 개당 990원", 40, fill=SUB, weight="SemiBold", alpha=a)
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
    out = HERE / "homelivingclub_hangerprice.mp4"
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
                    str(HERE / "homelivingclub_hangerprice_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
