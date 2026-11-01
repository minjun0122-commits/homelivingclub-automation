"""
홈리빙클럽 릴스 — "건조기에 넣으면 안 되는 건 딱 하나, 몇 번?" (7.5초, 퀴즈형 한 장면, 생활 퀴즈 5탄)
- 정답: 3 울 니트 (열·회전에 줄어들 수 있음 → 세탁 라벨 확인, 뉘어서 말리기) / 면 티셔츠·수건·청바지는 대체로 OK
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만 / 효과 주장 없음
- BGM: piano (직전 발매트 퀴즈 = marimba2)
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
# Am7 → Fmaj7 → C → G
CHORDS = [[45, 48, 52, 55], [41, 45, 48, 52], [36, 40, 43, 48], [43, 47, 50, 55]]
GRAY = (170, 166, 158)

CARDS = [  # (번호, 이름, 공개 문구, 정답 여부)
    ("1", "면 티셔츠", "OK", False),
    ("2", "수건", "OK", False),
    ("3", "울 니트", "줄어들 수 있어요", True),
    ("4", "청바지", "OK", False),
]
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
REVEAL = [4.0, 4.4, 5.4, 4.8]  # 정답(3번)을 마지막에 공개


def shirt(d, cx, cy, col, out, long=False):
    sl = 140 if long else 70
    d.polygon([(cx - 70, cy - 100), (cx - 25, cy - 110), (cx, cy - 90), (cx + 25, cy - 110), (cx + 70, cy - 100),
               (cx + 70 + sl * 0.6, cy - 100 + sl), (cx + 70 + sl * 0.6 - 35, cy - 100 + sl + 15), (cx + 70, cy - 50),
               (cx + 70, cy + 110), (cx - 70, cy + 110), (cx - 70, cy - 50),
               (cx - 70 - sl * 0.6 + 35, cy - 100 + sl + 15), (cx - 70 - sl * 0.6, cy - 100 + sl)], fill=col, outline=out)


def draw_item(d, i, cx, cy):
    if i == 0:   # 티셔츠
        shirt(d, cx, cy, (250, 250, 250), (180, 184, 190))
    elif i == 1:  # 수건
        for k, y in enumerate((cy + 40, cy - 10, cy - 60)):
            d.rounded_rectangle((cx - 120, y - 25, cx + 120, y + 25), 14, fill=(170, 210, 225) if k % 2 else (230, 240, 245), outline=(140, 180, 200), width=3)
    elif i == 2:  # 울 니트
        shirt(d, cx, cy, (214, 170, 150), (170, 125, 105), long=True)
        for x in (cx - 30, cx + 30):
            for y in range(int(cy - 70), int(cy + 100), 26):
                d.arc((x - 12, y, x + 12, y + 24), 200, 340, fill=(170, 125, 105), width=4)
    else:         # 청바지
        d.polygon([(cx - 80, cy - 110), (cx + 80, cy - 110), (cx + 95, cy + 115), (cx + 20, cy + 115), (cx, cy - 20),
                   (cx - 20, cy + 115), (cx - 95, cy + 115)], fill=(90, 120, 170), outline=(60, 85, 130))
        d.line((cx - 80, cy - 85, cx + 80, cy - 85), fill=(60, 85, 130), width=4)


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "건조기에 넣으면 안 되는 건", 72)
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
        text(d, (W / 2, 1610), "넣기 전에 세탁 라벨 확인하기", 44, fill=SUB, weight="SemiBold", alpha=a)
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
    out = HERE / "homelivingclub_dryerquiz.mp4"
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
                    str(HERE / "homelivingclub_dryerquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
