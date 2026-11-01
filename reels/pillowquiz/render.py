"""
홈리빙클럽 릴스 — 고양이 바디필로우, 빨 때 하면 안 되는 건 딱 하나, 몇 번? (상품 퀴즈 3탄)
- 상품 세탁 안내(찬물·중성세제, 세탁망 단독, 그늘 건조, 건조기 사용 금지)
- 정답: 2 건조기 돌리기
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음
- BGM: marimba
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
# Gmaj7 → Bm7 → Em7 → A7
CHORDS = [[43, 47, 50, 54], [47, 50, 54, 57], [40, 43, 47, 50], [45, 49, 52, 55]]
PINK, PINK_D = (244, 214, 204), (210, 170, 158)
CARDS = [
    ("1", "찬물 + 중성세제", "OK", False),
    ("2", "건조기 돌리기", "건조기는 피해 주세요", True),
    ("3", "세탁망에 넣기", "OK", False),
    ("4", "그늘에서 말리기", "OK", False),
]
REVEAL = [4.0, 5.4, 4.4, 4.8]  # 정답(2번)을 마지막에 공개
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440


def cat(d, cx, cy, s=1.0):
    d.rounded_rectangle((cx - 120 * s, cy - 40 * s, cx + 120 * s, cy + 40 * s), int(40 * s), fill=PINK, outline=PINK_D, width=4)
    d.polygon([(cx + 70 * s, cy - 36 * s), (cx + 85 * s, cy - 70 * s), (cx + 100 * s, cy - 30 * s)], fill=PINK, outline=PINK_D)
    d.polygon([(cx + 30 * s, cy - 38 * s), (cx + 45 * s, cy - 72 * s), (cx + 62 * s, cy - 36 * s)], fill=PINK, outline=PINK_D)
    d.ellipse((cx + 42 * s, cy - 10 * s, cx + 52 * s, cy), fill=(80, 70, 70))
    d.ellipse((cx + 78 * s, cy - 10 * s, cx + 88 * s, cy), fill=(80, 70, 70))


def draw_item(d, i, cx, cy):
    if i == 0:   # 대야 + 물방울
        d.chord((cx - 140, cy - 40, cx + 140, cy + 120), 0, 180, fill=(170, 205, 230), outline=(120, 165, 200), width=5)
        cat(d, cx, cy + 20, 0.8)
        d.ellipse((cx - 20, cy - 120, cx + 20, cy - 70), fill=(120, 180, 230))
    elif i == 1:  # 건조기
        d.rounded_rectangle((cx - 100, cy - 120, cx + 100, cy + 110), 20, fill=(240, 240, 240), outline=(180, 180, 184), width=5)
        d.ellipse((cx - 70, cy - 60, cx + 70, cy + 80), fill=(250, 220, 190), outline=(150, 155, 164), width=8)
        for k in range(3):
            d.arc((cx - 40 + k * 25, cy - 105, cx - 20 + k * 25, cy - 75), 90, 270, fill=(230, 120, 80), width=4)
    elif i == 2:  # 세탁망
        d.rounded_rectangle((cx - 140, cy - 80, cx + 140, cy + 80), 30, fill=(245, 245, 245), outline=(170, 170, 176), width=5)
        for k in range(-120, 140, 30):
            d.line((cx + k, cy - 75, cx + k, cy + 75), fill=(215, 215, 220), width=2)
        cat(d, cx, cy + 5, 0.85)
    else:         # 그늘 건조
        d.polygon([(cx - 150, cy - 70), (cx, cy - 140), (cx + 150, cy - 70)], fill=(150, 170, 190))
        d.line((cx - 130, cy - 40, cx + 130, cy - 40), fill=(120, 125, 135), width=4)
        cat(d, cx, cy + 30, 0.9)


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "고양이 바디필로우, 빨 때 안 되는 건", 62)
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
        text(d, (W / 2, 1610), "찬물 세탁 후 그늘에서 말리기", 44, fill=SUB, weight="SemiBold", alpha=a)
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
    out = HERE / "homelivingclub_pillowquiz.mp4"
    render(SCENES, silent, HERE / "_frames")
    wav = HERE / "_bgm.wav"
    bgm.make(wav, TOTAL, CHORDS, "marimba")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_pillowquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
