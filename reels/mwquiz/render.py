"""
홈리빙클럽 릴스 — "전자레인지에 넣어도 되는 건 딱 하나, 몇 번?" (7.5초, 퀴즈형 한 장면)
- 새 시리즈 1탄(퀴즈형). 정답이 궁금해서 끝까지 보게 + 댓글로 번호 달기
- 정답: 4 내열 유리그릇 / 1 호일·2 스텐 텀블러 = 불꽃 위험, 3 껍질째 삶은 달걀 = 터질 수 있음
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만 / 건강 효과 주장 없음
- BGM: piano2 (직전 샤워기 = marimba)
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
# Fmaj7 → G7 → Em7 → Am7
CHORDS = [[41, 45, 48, 52], [43, 47, 50, 53], [40, 43, 47, 50], [45, 48, 52, 55]]
SILVER, SILVER_D = (205, 208, 214), (150, 155, 164)

CARDS = [  # (번호, 이름, 오답 이유, 정답 여부)
    ("1", "알루미늄 호일", "불꽃이 튈 수 있어요", False),
    ("2", "스텐 텀블러", "금속이라 불꽃 위험", False),
    ("3", "껍질째 삶은 달걀", "터질 수 있어요", False),
    ("4", "유리그릇", "'내열' 표시면 OK", True),
]
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
REVEAL = [4.0, 4.5, 5.0, 5.6]


def draw_item(d, i, cx, cy):
    if i == 0:   # 호일 롤
        d.rounded_rectangle((cx - 130, cy - 50, cx + 130, cy + 10), 30, fill=SILVER, outline=SILVER_D, width=5)
        d.polygon([(cx - 120, cy + 10), (cx + 120, cy + 10), (cx + 100, cy + 90), (cx - 140, cy + 80)], fill=(225, 228, 233), outline=SILVER_D)
    elif i == 1:  # 텀블러
        d.rounded_rectangle((cx - 55, cy - 110, cx + 55, cy + 100), 26, fill=SILVER, outline=SILVER_D, width=5)
        d.rounded_rectangle((cx - 62, cy - 130, cx + 62, cy - 95), 14, fill=(70, 74, 82))
        d.line((cx - 25, cy - 80, cx - 25, cy + 80), fill=(235, 237, 240), width=10)
    elif i == 2:  # 달걀
        d.ellipse((cx - 75, cy - 100, cx + 75, cy + 95), fill=(244, 230, 205), outline=(205, 185, 150), width=5)
    else:         # 유리그릇 + 내열 표시
        d.chord((cx - 140, cy - 120, cx + 140, cy + 110), 0, 180, fill=(214, 236, 246), outline=(130, 180, 205), width=6)
        d.rounded_rectangle((cx - 50, cy + 20, cx + 50, cy + 66), 12, fill=(255, 255, 255), outline=(130, 180, 205), width=3)
        d.text((cx, cy + 43), "내열", font=F(30, "Bold"), fill=(80, 130, 160), anchor="mm")


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "전자레인지에 넣어도 되는 건", 72)
    text(d, (W / 2, 350), "딱 하나. 몇 번?", 104, fill=ACCENT, weight="ExtraBold")
    for i, ((n, name, why, good), (x, y)) in enumerate(zip(CARDS, POS)):
        k = appear(T, REVEAL[i], 0.25)
        border = OK if (good and k > 0) else (ACCENT if k > 0 else (220, 216, 208))
        d.rounded_rectangle((x, y, x + CW, y + CH), 36, fill=(255, 255, 255), outline=border, width=8 if k > 0 else 4)
        d.ellipse((x + 24, y + 24, x + 104, y + 104), fill=INK)
        d.text((x + 64, y + 64), n, font=F(50, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        draw_item(d, i, x + CW / 2, y + 190)
        if k <= 0:
            d.text((x + CW / 2, y + 380), name, font=F(42, "Bold"), fill=INK, anchor="mm")
        else:
            d.text((x + CW / 2, y + 380), why, font=F(38, "Bold"), fill=OK if good else ACCENT, anchor="mm")
            cx, cy, s = x + CW - 70, y + 70, 40 * k
            if good:
                d.ellipse((cx - s, cy - s, cx + s, cy + s), outline=OK, width=12)
            else:
                d.line((cx - s, cy - s, cx + s, cy + s), fill=ACCENT, width=12)
                d.line((cx - s, cy + s, cx + s, cy - s), fill=ACCENT, width=12)
    if T < 4.0:  # 카운트다운
        n = 3 - int((T - 1.0) // 1.0) if T >= 1.0 else 3
        n = max(1, min(3, n))
        d.ellipse((W / 2 - 70, 1495 - 70, W / 2 + 70, 1495 + 70), fill=INK)
        d.text((W / 2, 1495), str(n), font=F(80, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        text(d, (W / 2, 1620), "댓글로 번호 먼저 찍기", 44, fill=SUB, weight="SemiBold")
    elif T >= 6.2:
        a = appear(T, 6.2, 0.3)
        text(d, (W / 2, 1500), "정답 4번, 맞히셨나요?", 64, fill=OK, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1610), "저장해두고 헷갈릴 때 보기", 44, fill=SUB, weight="SemiBold", alpha=a)
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
    out = HERE / "homelivingclub_mwquiz.mp4"
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
                    str(HERE / "homelivingclub_mwquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
