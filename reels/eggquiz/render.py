"""
홈리빙클럽 릴스 — 전자레인지에 그냥 돌리면 터질 수 있는 건 딱 하나, 몇 번? (상품 퀴즈 4탄)
- 껍질째 날계란은 전자레인지에 그냥 돌리면 터질 수 있음 → 전용 찜기(꼬꼬 찜기, 물 붓고 사용)
- 정답: 3 껍질째 날계란
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음 / 끝 화면 상품 사진은 오너클랜 실물 사진
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
# Cmaj7 → Am7 → Dm7 → G7
CHORDS = [[48, 52, 55, 59], [45, 48, 52, 55], [50, 53, 57, 60], [43, 47, 50, 53]]
CARDS = [
    ("1", "식은 밥", "OK", False),
    ("2", "냉동 만두", "OK", False),
    ("3", "껍질째 날계란", "터질 수 있어요", True),
    ("4", "식빵 한 장", "OK", False),
]
REVEAL = [4.0, 4.4, 5.4, 4.8]  # 정답(3번)을 마지막에 공개
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
PHOTO = Image.open(HERE.parent.parent / "products/images/eggsteamer/main.jpg").convert("RGB").resize((230, 230))


def draw_item(d, i, cx, cy):
    if i == 0:   # 밥공기
        d.chord((cx - 120, cy - 60, cx + 120, cy + 120), 0, 180, fill=(235, 240, 245), outline=(150, 160, 175), width=5)
        d.chord((cx - 110, cy - 50, cx + 110, cy + 110), 180, 360, fill=(255, 255, 255), outline=(200, 200, 205), width=4)
        d.line((cx - 120, cy + 30, cx + 120, cy + 30), fill=(150, 160, 175), width=5)
    elif i == 1:  # 만두
        for dx in (-70, 70):
            d.chord((cx + dx - 75, cy - 70, cx + dx + 75, cy + 70), 180, 360, fill=(250, 244, 230), outline=(200, 185, 160), width=5)
            d.line((cx + dx - 75, cy, cx + dx + 75, cy), fill=(200, 185, 160), width=5)
            for k in range(-40, 50, 25):
                d.arc((cx + dx + k - 10, cy - 70, cx + dx + k + 10, cy - 40), 0, 180, fill=(200, 185, 160), width=3)
    elif i == 2:  # 껍질째 계란
        for dx, s in ((-55, 1.0), (60, 0.9)):
            d.ellipse((cx + dx - 55 * s, cy - 80 * s, cx + dx + 55 * s, cy + 70 * s), fill=(246, 226, 200), outline=(200, 170, 135), width=5)
    else:         # 식빵
        d.rounded_rectangle((cx - 100, cy - 60, cx + 100, cy + 110), 14, fill=(245, 215, 160), outline=(190, 140, 80), width=8)
        d.ellipse((cx - 115, cy - 130, cx + 115, cy - 10), fill=(245, 215, 160), outline=(190, 140, 80), width=8)
        d.rectangle((cx - 92, cy - 70, cx + 92, cy - 20), fill=(245, 215, 160))


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "전자레인지에 그냥 돌리면 터지는 건", 62)
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
        text(d, (W / 2, 1490), "정답 3번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        if a > 0.5:
            img.paste(PHOTO, (110, 1570))
        text(d, (650, 1630), "껍질째 찔 땐 물 붓는 전용 찜기로", 38, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (650, 1710), "영상 속 꼬꼬 찜기는", 36, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_eggquiz.mp4"
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
                    str(HERE / "homelivingclub_eggquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
