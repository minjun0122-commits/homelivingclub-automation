"""
홈리빙클럽 릴스 — "물에 오래 담가두면 안 되는 건 딱 하나, 몇 번?" (7.5초, 퀴즈형 한 장면)
- 퀴즈 시리즈 2탄. 정답 위치를 4번→3번으로 바꿈
- 정답: 3 나무 도마 (물을 먹어 갈라지거나 휠 수 있음) / 유리컵·스텐 냄비·실리콘 주걱은 담가도 괜찮음
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만 / 건강 효과 주장 없음
- BGM: marimba2 (직전 전자레인지 퀴즈 = piano2)
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
# Dm7 → G7 → Cmaj7 → Am7
CHORDS = [[38, 45, 48, 53], [43, 47, 50, 53], [40, 43, 47, 48], [45, 48, 52, 55]]
SILVER, SILVER_D = (205, 208, 214), (150, 155, 164)
WOOD, WOOD_D = (214, 170, 118), (160, 115, 70)
GRAY = (170, 166, 158)

CARDS = [  # (번호, 이름, 공개 문구, 정답 여부)
    ("1", "유리컵", "담가도 괜찮아요", False),
    ("2", "스텐 냄비", "담가도 괜찮아요", False),
    ("3", "나무 도마", "갈라지고 휠 수 있어요", True),
    ("4", "실리콘 주걱", "담가도 괜찮아요", False),
]
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
REVEAL = [4.0, 4.4, 4.8, 5.4]


def draw_item(d, i, cx, cy):
    if i == 0:   # 유리컵
        d.polygon([(cx - 75, cy - 110), (cx + 75, cy - 110), (cx + 58, cy + 100), (cx - 58, cy + 100)],
                  fill=(214, 236, 246), outline=(130, 180, 205))
        d.line((cx - 40, cy - 85, cx - 30, cy + 70), fill=(255, 255, 255), width=10)
    elif i == 1:  # 스텐 냄비
        d.rounded_rectangle((cx - 120, cy - 60, cx + 120, cy + 90), 24, fill=SILVER, outline=SILVER_D, width=5)
        d.rounded_rectangle((cx - 175, cy - 45, cx - 118, cy - 20), 10, fill=(70, 74, 82))
        d.rounded_rectangle((cx + 118, cy - 45, cx + 175, cy - 20), 10, fill=(70, 74, 82))
        d.rounded_rectangle((cx - 130, cy - 85, cx + 130, cy - 60), 10, fill=SILVER_D)
    elif i == 2:  # 나무 도마
        d.rounded_rectangle((cx - 150, cy - 100, cx + 150, cy + 100), 30, fill=WOOD, outline=WOOD_D, width=5)
        d.ellipse((cx + 95, cy - 18, cx + 125, cy + 12), fill=(255, 255, 255), outline=WOOD_D, width=3)
        for k in range(4):
            y = cy - 60 + k * 38
            d.arc((cx - 130, y - 14, cx + 70, y + 14), 0, 180, fill=WOOD_D, width=4)
    else:         # 실리콘 주걱
        d.rounded_rectangle((cx - 12, cy - 120, cx + 12, cy + 30), 10, fill=(80, 84, 92))
        d.rounded_rectangle((cx - 55, cy + 10, cx + 55, cy + 115), 30, fill=(240, 150, 140), outline=(200, 110, 100), width=4)


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "물에 오래 담가두면 안 되는 건", 70)
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
        text(d, (W / 2, 1500), "정답 3번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "쓰고 바로 씻어서 세워 말리기", 44, fill=SUB, weight="SemiBold", alpha=a)
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
    out = HERE / "homelivingclub_soakquiz.mp4"
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
                    str(HERE / "homelivingclub_soakquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
