"""
홈리빙클럽 릴스 — "규조토 발매트, 하면 안 되는 건 딱 하나, 몇 번?" (7.5초, 퀴즈형 한 장면, 상품 퀴즈 2탄)
- 스토어 상품(빨아쓰는 소프트 규조토 발매트)의 실제 안내(손빨래/세탁기 가능, 직사광선 피해 그늘 건조)를 퀴즈로
- 정답: 1 햇볕에 바짝 말리기 / 손빨래·세탁기·그늘 건조는 OK
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음
- BGM: marimba2 (직전 식초 퀴즈 = piano2)
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
# Fmaj7 → Em7 → Dm7 → Cmaj7
CHORDS = [[41, 45, 48, 52], [40, 43, 47, 50], [38, 41, 45, 48], [36, 40, 43, 47]]
GRAY = (170, 166, 158)
MAT, MAT_D = (226, 214, 196), (190, 176, 156)

CARDS = [  # (번호, 이름, 공개 문구, 정답 여부)
    ("1", "햇볕에 바짝 말리기", "그늘에서 말려요", True),
    ("2", "손빨래", "OK", False),
    ("3", "세탁기 돌리기", "OK", False),
    ("4", "그늘에서 말리기", "OK", False),
]
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
REVEAL = [5.4, 4.0, 4.4, 4.8]  # 정답(1번)을 마지막에 공개


def draw_mat(d, cx, cy, w=150, h=90):
    d.rounded_rectangle((cx - w, cy - h / 2, cx + w, cy + h / 2), 22, fill=MAT, outline=MAT_D, width=4)
    for k in range(5):
        x = cx - w + 40 + k * (2 * w - 80) / 4
        d.line((x, cy - h / 2 + 14, x, cy + h / 2 - 14), fill=MAT_D, width=3)


def draw_item(d, i, cx, cy):
    if i == 0:   # 해
        d.ellipse((cx - 45, cy - 140, cx + 45, cy - 50), fill=(250, 196, 70))
        import math
        for k in range(8):
            a = 2 * math.pi * k / 8
            d.line((cx + 60 * math.cos(a), cy - 95 + 60 * math.sin(a), cx + 80 * math.cos(a), cy - 95 + 80 * math.sin(a)),
                   fill=(250, 196, 70), width=7)
        draw_mat(d, cx, cy + 50)
    elif i == 1:  # 손빨래 (대야 + 거품)
        d.chord((cx - 140, cy - 60, cx + 140, cy + 120), 0, 180, fill=(170, 205, 230), outline=(120, 165, 200), width=5)
        draw_mat(d, cx, cy + 10, 110, 60)
        for x, y, r in ((cx - 70, cy - 40, 22), (cx - 20, cy - 70, 28), (cx + 45, cy - 45, 20), (cx + 85, cy - 85, 16)):
            d.ellipse((x - r, y - r, x + r, y + r), outline=(130, 175, 210), width=4, fill=(240, 248, 252))
    elif i == 2:  # 세탁기
        d.rounded_rectangle((cx - 100, cy - 120, cx + 100, cy + 110), 20, fill=(240, 240, 240), outline=(180, 180, 184), width=5)
        d.line((cx - 100, cy - 75, cx + 100, cy - 75), fill=(180, 180, 184), width=4)
        d.ellipse((cx - 65, cy - 50, cx + 65, cy + 80), fill=(200, 225, 240), outline=(150, 155, 164), width=8)
        d.ellipse((cx + 50, cy - 105, cx + 70, cy - 88), fill=(120, 125, 135))
    else:         # 그늘 (지붕 아래 빨랫줄)
        d.polygon([(cx - 150, cy - 70), (cx, cy - 140), (cx + 150, cy - 70)], fill=(150, 170, 190))
        d.line((cx - 130, cy - 40, cx + 130, cy - 40), fill=(120, 125, 135), width=4)
        draw_mat(d, cx, cy + 20, 120, 100)


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "규조토 발매트, 하면 안 되는 건", 70)
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
        text(d, (W / 2, 1610), "빨고 나면 직사광선 피해 그늘에서", 44, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (W / 2, 1690), "영상 속 발매트는 저희 스토어 상품", 38, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_matquiz.mp4"
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
                    str(HERE / "homelivingclub_matquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
