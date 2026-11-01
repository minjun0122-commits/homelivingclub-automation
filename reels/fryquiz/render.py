"""
홈리빙클럽 릴스 — 600W 50초 계란후라이, 500W에선 몇 초? (상품 퀴즈 5탄, 계산형)
- 상품 상세 안내 조리 시간: 500W 1분 / 600W 50초 (공급사 표기 그대로)
- 정답: 1 1분
- 영상과 캡션에 "저희 스토어 상품" 표기 / 효과 주장 없음 / 끝 화면 사진은 오너클랜 실물 사진
- BGM: marimba
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
# Fmaj7 → Em7 → Dm7 → Cmaj7
CHORDS = [[41, 45, 48, 52], [40, 43, 47, 50], [38, 41, 45, 48], [36, 40, 43, 47]]
CARDS = [
    ("1", "1분", "정답", True),
    ("2", "40초", "아니에요", False),
    ("3", "30초", "아니에요", False),
    ("4", "2분", "아니에요", False),
]
REVEAL = [5.4, 4.0, 4.4, 4.8]  # 정답(1번)을 마지막에 공개
GRAY = (170, 166, 158)
POS = [(90, 520), (550, 520), (90, 990), (550, 990)]
CW, CH = 440, 440
PHOTO = Image.open(HERE.parent.parent / "products/images/eggfry/main.jpg").convert("RGB").resize((230, 230))


def draw_item(d, i, cx, cy):
    # 전자레인지 + 타이머 표시
    d.rounded_rectangle((cx - 150, cy - 100, cx + 150, cy + 100), 18, fill=(236, 236, 238), outline=(150, 152, 160), width=5)
    d.rounded_rectangle((cx - 130, cy - 80, cx + 50, cy + 80), 10, fill=(70, 74, 82))
    d.ellipse((cx - 70, cy + 5, cx - 10, cy + 45), fill=(255, 255, 255))
    d.ellipse((cx - 50, cy + 15, cx - 30, cy + 35), fill=(250, 190, 60))
    d.rounded_rectangle((cx + 65, cy - 75, cx + 140, cy - 35), 8, fill=(40, 44, 52))
    d.text((cx + 102, cy - 55), ["1:00", "0:40", "0:30", "2:00"][i], font=F(26, "Bold"), fill=(120, 230, 140), anchor="mm")
    for k in range(3):
        d.ellipse((cx + 88, cy - 15 + k * 32, cx + 116, cy + 13 + k * 32), fill=(200, 200, 206))

def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 230), "600W 50초 계란후라이, 500W에선?", 62)
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
        text(d, (W / 2, 1490), "정답 1번, 맞히셨나요?", 64, fill=ACCENT, weight="ExtraBold", alpha=a)
        if a > 0.5:
            img.paste(PHOTO, (110, 1570))
        text(d, (650, 1630), "출력이 낮으면 더 오래, 500W는 1분", 38, fill=SUB, weight="SemiBold", alpha=a)
        text(d, (650, 1710), "영상 속 계란후라이 메이커는", 36, fill=SUB, alpha=a)
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
    out = HERE / "homelivingclub_fryquiz.mp4"
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
                    str(HERE / "homelivingclub_fryquiz_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
