"""
홈리빙클럽 릴스 — "냉장고에 넣으면 오히려 빨리 굳는 건 딱 하나, 몇 번?" (7.5초, 퀴즈형 한 장면, 생활 퀴즈 3탄)
- 정답: 2 식빵 (냉장 온도에서 전분이 빨리 굳음 → 실온 또는 냉동) / 우유·두부·김치는 냉장
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만 / 건강 효과 주장 없음
- BGM: marimba (직전 화병 퀴즈 = piano)
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
# Em7 → Am7 → D → G
CHORDS = [[40, 47, 50, 55], [45, 48, 52, 55], [38, 45, 50, 54], [43, 47, 50, 55]]
GRAY = (170, 166, 158)

CARDS = [  # (번호, 이름, 공개 문구, 정답 여부)
    ("1", "우유", "냉장 OK", False),
    ("2", "식빵", "더 빨리 딱딱해져요", True),
    ("3", "두부", "냉장 OK", False),
    ("4", "김치", "냉장 OK", False),
]
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
REVEAL = [4.0, 4.4, 4.8, 5.4]


def draw_item(d, i, cx, cy):
    if i == 0:   # 우유팩
        d.rectangle((cx - 60, cy - 60, cx + 60, cy + 110), fill=(250, 250, 250), outline=(180, 190, 205), width=5)
        d.polygon([(cx - 60, cy - 60), (cx, cy - 115), (cx + 60, cy - 60)], fill=(235, 240, 248), outline=(180, 190, 205))
        d.rectangle((cx - 60, cy + 10, cx + 60, cy + 60), fill=(110, 160, 220))
    elif i == 2:  # 두부
        d.rounded_rectangle((cx - 110, cy - 60, cx + 110, cy + 90), 18, fill=(230, 240, 248), outline=(170, 195, 215), width=5)
        d.rounded_rectangle((cx - 80, cy - 35, cx + 80, cy + 65), 10, fill=(252, 250, 240), outline=(220, 214, 196), width=3)
    elif i == 1:  # 식빵
        d.rounded_rectangle((cx - 95, cy - 70, cx + 95, cy + 105), 30, fill=(214, 160, 96))
        d.ellipse((cx - 110, cy - 115, cx - 10, cy - 15), fill=(214, 160, 96))
        d.ellipse((cx + 10, cy - 115, cx + 110, cy - 15), fill=(214, 160, 96))
        d.rounded_rectangle((cx - 75, cy - 50, cx + 75, cy + 88), 22, fill=(250, 232, 196))
        d.ellipse((cx - 90, cy - 98, cx - 20, cy - 28), fill=(250, 232, 196))
        d.ellipse((cx + 20, cy - 98, cx + 90, cy - 28), fill=(250, 232, 196))
    else:         # 김치통
        d.rounded_rectangle((cx - 115, cy - 75, cx + 115, cy - 45), 12, fill=(120, 170, 120))
        d.rounded_rectangle((cx - 105, cy - 50, cx + 105, cy + 100), 20, fill=(240, 244, 240), outline=(190, 200, 190), width=4)
        d.rounded_rectangle((cx - 85, cy - 10, cx + 85, cy + 85), 16, fill=(214, 72, 52))
        for k in range(3):
            d.arc((cx - 70 + k * 45, cy + 5, cx - 20 + k * 45, cy + 55), 200, 340, fill=(250, 230, 200), width=6)


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "냉장고에 넣으면 오히려 빨리 굳는 건", 64)
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
        text(d, (W / 2, 1500), "정답 2번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "바로 먹을 건 실온, 오래 둘 건 냉동", 44, fill=SUB, weight="SemiBold", alpha=a)
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
    out = HERE / "homelivingclub_breadquiz.mp4"
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
                    str(HERE / "homelivingclub_breadquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
