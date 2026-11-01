"""
홈리빙클럽 릴스 — "식초로 닦으면 안 되는 건 딱 하나, 몇 번?" (7.5초, 퀴즈형 한 장면, 생활 퀴즈 4탄)
- 정답: 4 대리석 상판 (산에 약해 표면이 상하고 얼룩질 수 있음 → 중성세제) / 유리컵·전기포트·샤워기 헤드는 식초 후 헹구면 OK
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만 / 건강 효과 주장 없음
- BGM: piano2 (직전 식빵 퀴즈 = marimba)
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
# Cmaj7 → Em7 → Fmaj7 → G
CHORDS = [[36, 40, 43, 47], [40, 43, 47, 50], [41, 45, 48, 52], [43, 47, 50, 55]]
GRAY = (170, 166, 158)
SILVER, SILVER_D = (205, 208, 214), (150, 155, 164)

CARDS = [  # (번호, 이름, 공개 문구, 정답 여부)
    ("1", "유리컵", "OK, 헹구기", False),
    ("2", "전기포트 안", "OK, 헹구기", False),
    ("3", "샤워기 헤드", "OK, 헹구기", False),
    ("4", "대리석 상판", "표면이 상할 수 있어요", True),
]
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
REVEAL = [4.0, 4.4, 4.8, 5.4]


def draw_item(d, i, cx, cy):
    if i == 0:   # 유리컵
        d.polygon([(cx - 75, cy - 110), (cx + 75, cy - 110), (cx + 58, cy + 100), (cx - 58, cy + 100)],
                  fill=(214, 236, 246), outline=(130, 180, 205))
        d.line((cx - 40, cy - 85, cx - 30, cy + 70), fill=(255, 255, 255), width=10)
    elif i == 1:  # 전기포트
        d.rounded_rectangle((cx - 85, cy - 80, cx + 75, cy + 100), 30, fill=SILVER, outline=SILVER_D, width=5)
        d.arc((cx + 40, cy - 60, cx + 130, cy + 60), 270, 90, fill=(70, 74, 82), width=16)
        d.polygon([(cx - 85, cy - 60), (cx - 135, cy - 85), (cx - 85, cy - 25)], fill=SILVER_D)
        d.rounded_rectangle((cx - 60, cy - 100, cx + 50, cy - 75), 10, fill=(70, 74, 82))
        d.rounded_rectangle((cx - 95, cy + 95, cx + 85, cy + 115), 8, fill=(70, 74, 82))
    elif i == 2:  # 샤워기 헤드
        d.line((cx + 40, cy + 40, cx + 120, cy + 120), fill=SILVER_D, width=26)
        d.ellipse((cx - 100, cy - 100, cx + 70, cy + 70), fill=SILVER, outline=SILVER_D, width=6)
        for r in range(3):
            for k in range(6 + r * 4):
                import math
                a = 2 * math.pi * k / (6 + r * 4)
                x, y = cx - 15 + (18 + r * 22) * math.cos(a), cy - 15 + (18 + r * 22) * math.sin(a)
                d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(120, 125, 135))
    else:         # 대리석 상판
        d.rounded_rectangle((cx - 150, cy - 70, cx + 150, cy + 80), 14, fill=(240, 240, 236), outline=(190, 190, 184), width=5)
        for pts in ([(cx - 130, cy - 40), (cx - 60, cy - 10), (cx + 10, cy - 30), (cx + 90, cy + 20)],
                    [(cx - 100, cy + 50), (cx - 30, cy + 25), (cx + 60, cy + 55), (cx + 130, cy + 30)]):
            d.line(pts, fill=(180, 180, 176), width=4)
        d.rounded_rectangle((cx - 150, cy + 80, cx + 150, cy + 105), 6, fill=(205, 205, 200))


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "식초로 닦으면 안 되는 건", 72)
    text(d, (W / 2, 350), "딱 하나. 몇 번?", 104, fill=ACCENT, weight="ExtraBold")
    for i, ((n, name, why, good), (x, y)) in enumerate(zip(CARDS, POS)):
        k = appear(T, REVEAL[i], 0.25)
        border = ACCENT if (good and k > 0) else ((200, 196, 188) if k > 0 else (220, 216, 208))
        d.rounded_rectangle((x, y, x + CW, y + CH), 36, fill=(255, 255, 255), outline=border, width=8 if k > 0 else 4)
        d.ellipse((x + 24, y + 24, x + 104, y + 104), fill=INK)
        d.text((x + 64, y + 64), n, font=F(50, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        draw_item(d, i, x + CW / 2, y + 190)
        if k <= 0:
            d.text((x + CW / 2, y + 380), name, font=F(42, "Bold"), fill=INK, anchor="mm")
        else:
            d.text((x + CW / 2, y + 380), why, font=F(36, "Bold"), fill=ACCENT if good else GRAY, anchor="mm")
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
        text(d, (W / 2, 1610), "대리석은 중성세제로 닦기", 44, fill=SUB, weight="SemiBold", alpha=a)
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
    out = HERE / "homelivingclub_vinegarquiz.mp4"
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
                    str(HERE / "homelivingclub_vinegarquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
