"""
홈리빙클럽 릴스 — "이 미니 화병에 넣으면 안 되는 건 딱 하나, 몇 번?" (7.5초, 퀴즈형 한 장면, 상품 퀴즈 1탄)
- 판매 연결 실험: 스토어 상품(웨이브 미니 화병)의 실제 특징(플라스틱 → 물 못 담음)을 퀴즈 정답으로
- 정답: 3 물 / 튤립 조화·드라이플라워·조화 잎 가지는 OK
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음
- BGM: piano (직전 담가두기 퀴즈 = marimba2)
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
# Am7 → Dm7 → G → Cmaj7
CHORDS = [[45, 48, 52, 55], [38, 45, 48, 53], [43, 47, 50, 55], [36, 40, 43, 47]]
VASE, VASE_D = (236, 232, 224), (190, 184, 172)
GRAY = (170, 166, 158)
STEM, LEAF = (90, 140, 90), (120, 170, 110)

CARDS = [  # (번호, 이름, 공개 문구, 정답 여부)
    ("1", "튤립 조화", "OK", False),
    ("2", "드라이플라워", "OK", False),
    ("3", "물", "플라스틱이라 물은 X", True),
    ("4", "조화 잎 가지", "OK", False),
]
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
REVEAL = [4.0, 4.4, 4.8, 5.4]


def draw_vase(d, cx, cy):
    # 웨이브 미니 화병 (낮고 넓은 물결 모양)
    pts = []
    for k in range(13):
        x = cx - 85 + k * 170 / 12
        pts.append((x, cy - 10 + (8 if k % 2 else -8)))
    pts += [(cx + 95, cy + 40), (cx + 80, cy + 110), (cx - 80, cy + 110), (cx - 95, cy + 40)]
    d.polygon(pts, fill=VASE, outline=VASE_D)
    for k in range(4):
        x = cx - 60 + k * 40
        d.arc((x - 12, cy + 10, x + 12, cy + 100), 270, 90, fill=VASE_D, width=3)


def draw_item(d, i, cx, cy):
    vy = cy + 20
    if i == 0:   # 튤립
        for dx, col in ((-30, (240, 120, 130)), (30, (250, 200, 90))):
            d.line((cx + dx, vy, cx + dx * 1.3, cy - 90), fill=STEM, width=7)
            x, y = cx + dx * 1.3, cy - 110
            d.chord((x - 26, y - 34, x + 26, y + 26), 0, 180, fill=col)
            d.polygon([(x - 26, y - 4), (x - 16, y - 34), (x - 4, y - 10), (x + 8, y - 36), (x + 16, y - 8), (x + 26, y - 4)], fill=col)
    elif i == 1:  # 드라이플라워
        import math
        for a in (-40, -15, 10, 35):
            r = math.radians(a)
            x2, y2 = cx + 120 * math.sin(r), vy - 130 * math.cos(r)
            d.line((cx, vy, x2, y2), fill=(170, 140, 100), width=4)
            for t in (0.6, 0.8, 1.0):
                px, py = cx + (x2 - cx) * t, vy + (y2 - vy) * t
                d.ellipse((px - 8, py - 8, px + 8, py + 8), fill=(205, 160, 170))
    elif i == 2:  # 물
        x, y = cx + 10, cy - 100
        d.polygon([(x, y - 45), (x - 30, y + 5), (x + 30, y + 5)], fill=(120, 180, 230))
        d.ellipse((x - 30, y - 22, x + 30, y + 38), fill=(120, 180, 230))
        d.line((cx + 10, cy - 45, cx + 10, vy - 15), fill=(120, 180, 230), width=10)
    else:         # 잎 가지
        for dx in (-25, 25):
            d.line((cx, vy, cx + dx * 2.4, cy - 120), fill=STEM, width=6)
            for t in (0.35, 0.6, 0.85):
                px, py = cx + dx * 2.4 * t, vy + (cy - 120 - vy) * t
                d.ellipse((px - 20, py - 12, px + 20, py + 12), fill=LEAF)
    draw_vase(d, cx, vy)


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "이 미니 화병에 넣으면 안 되는 건", 68)
    text(d, (W / 2, 350), "딱 하나. 몇 번?", 104, fill=ACCENT, weight="ExtraBold")
    for i, ((n, name, why, good), (x, y)) in enumerate(zip(CARDS, POS)):
        k = appear(T, REVEAL[i], 0.25)
        border = ACCENT if (good and k > 0) else ((200, 196, 188) if k > 0 else (220, 216, 208))
        d.rounded_rectangle((x, y, x + CW, y + CH), 36, fill=(255, 255, 255), outline=border, width=8 if k > 0 else 4)
        d.ellipse((x + 24, y + 24, x + 104, y + 104), fill=INK)
        d.text((x + 64, y + 64), n, font=F(50, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        draw_item(d, i, x + CW / 2, y + 190)
        if k <= 0:
            d.text((x + CW / 2, y + 390), name, font=F(42, "Bold"), fill=INK, anchor="mm")
        else:
            d.text((x + CW / 2, y + 390), why, font=F(36, "Bold"), fill=ACCENT if good else GRAY, anchor="mm")
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
        text(d, (W / 2, 1500), "정답 3번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "조화·드라이플라워 전용 화병이에요", 44, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (W / 2, 1690), "영상 속 화병은 저희 스토어 상품", 38, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_vasequiz.mp4"
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
                    str(HERE / "homelivingclub_vasequiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
