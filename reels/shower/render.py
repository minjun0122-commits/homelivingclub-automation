"""
홈리빙클럽 릴스 — "샤워기 헤드, 구멍 막힌 거 보여요?" (7.5초, 한 장면 연속 애니메이션)
- 그림 릴스 9개가 전부 평균 2~3초 이탈 → 형식 변경 실험
  · 장면 전환 없음: 그림이 끝까지 화면에 있고 단계 글자만 바뀜 (1.8초 컷에서 이탈하던 문제)
  · 0초부터 막힌 구멍이 보이고 천천히 확대
  · 칫솔이 지나가면 구멍이 하나씩 뚫리고 '막힌 구멍 N개' 숫자가 줄어듦 → 끝에 물줄기(보상)
  · 댓글 문턱 낮추기: "1 깨끗 / 2 막힘"
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만 / 건강 효과 주장 없음
- BGM: marimba (직전 전자레인지 = piano)
"""
import math
import random
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, INK, SUB, ACCENT, OK, F, ease, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

TOTAL = 7.5
CHROME = (206, 210, 216)
CHROME_D = (160, 166, 174)
FACE = (232, 234, 238)
HOLE = (70, 76, 86)
SCALE = (250, 248, 238)
SCALE_E = (214, 206, 180)
WATER = (120, 180, 230)
# Cmaj7 → Fmaj7 → Am7 → G
CHORDS = [[48, 52, 55, 59], [53, 57, 60, 64], [45, 48, 52, 55], [43, 47, 50, 55]]

CX, CY, R = W / 2, 830, 320
rng = random.Random(21)
HOLES = []                                     # (dx, dy, 막힘 여부)
for ring, n in [(0.0, 1), (0.22, 8), (0.42, 14), (0.62, 20), (0.80, 26)]:
    off = rng.uniform(0, 1)
    for i in range(n):
        a = 2 * math.pi * (i + off) / n
        HOLES.append((ring * math.cos(a), ring * math.sin(a), rng.random() < 0.72))
CLOGGED = sum(1 for h in HOLES if h[2])

SOAK = (1.4, 2.6)      # 1단계: 구연산 물 (하얀 때가 살짝 옅어짐)
BRUSH = (2.6, 5.2)     # 2단계: 칫솔이 왼쪽 → 오른쪽
RINSE = 5.2            # 3단계: 물줄기


def brush_x(T):
    return CX - R - 40 + (2 * R + 80) * ease((T - BRUSH[0]) / (BRUSH[1] - BRUSH[0]))


def head(d, T):
    z = 1 + 0.06 * ease(T / 1.4)                                   # 처음 1.4초 천천히 확대
    r = R * z
    d.rounded_rectangle((CX - 70, CY + r * 0.7, CX + 70, CY + r + 90), 50, fill=CHROME, outline=CHROME_D, width=6)
    d.ellipse((CX - r - 30, CY - r - 30, CX + r + 30, CY + r + 30), fill=CHROME, outline=CHROME_D, width=8)
    d.ellipse((CX - r, CY - r, CX + r, CY + r), fill=FACE)
    soak = 0.35 * ease((T - SOAK[0]) / (SOAK[1] - SOAK[0]))
    bx = brush_x(T) if T >= BRUSH[0] else -1e9
    left = 0
    for dx, dy, clog in HOLES:
        x, y = CX + dx * r, CY + dy * r
        cleaned = clog and x < bx
        if clog and not cleaned:
            left += 1
            s = 26 * z * (1 - soak)
            d.ellipse((x - s, y - s, x + s, y + s), fill=SCALE, outline=SCALE_E, width=3)
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=SCALE_E)
        else:
            s = 11 * z
            d.ellipse((x - s, y - s, x + s, y + s), fill=HOLE)
    if BRUSH[0] <= T < BRUSH[1] + 0.2:                             # 칫솔 (위아래로 문지름)
        y = CY + math.sin(T * 22) * r * 0.55
        x = bx
        d.rounded_rectangle((x - 22, y - 70, x + 22, y + 70), 14, fill=(255, 255, 255), outline=CHROME_D, width=4)
        for k in range(5):
            d.line((x - 22, y - 56 + k * 28, x - 44, y - 56 + k * 28), fill=(120, 190, 210), width=8)
        d.rounded_rectangle((x + 18, y - 20, x + 300, y + 20), 18, fill=(120, 190, 210))
    if T >= RINSE:                                                 # 물줄기 = 보상
        k = ease((T - RINSE) / 0.6)
        for dx, dy, _ in HOLES[::2]:
            x, y = CX + dx * r, CY + dy * r
            d.line((x, y, x + dx * 40, y + 120 * k + 40 * k), fill=WATER, width=6)
    return left


STEPS = [(SOAK[0], "1", "물 1L + 구연산 2스푼, 1시간"),
         (BRUSH[0], "2", "칫솔로 구멍 문지르기"),
         (RINSE, "3", "물 틀어서 헹구면 끝")]


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    if T < 6.2:
        text(d, (W / 2, 230), "샤워기 헤드,", 104)
        text(d, (W / 2, 370), "구멍 막힌 거 보여요?", 84, fill=ACCENT)
    else:
        a = appear(T, 6.2, 0.25)
        text(d, (W / 2, 230), "우리 집 샤워기는?", 100, alpha=a)
        text(d, (W / 2, 370), "1 깨끗  /  2 막힘  댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=a)
    left = head(d, T)
    col = OK if left == 0 else ACCENT
    text(d, (W / 2, 1335), f"막힌 구멍 {left}개" if left else "막힌 구멍 0개", 64, fill=col, weight="ExtraBold")
    cur = [s for s in STEPS if T >= s[0]]
    if cur:
        _, k, v = cur[-1]
        a = appear(T, cur[-1][0], 0.2)
        y = 1455
        d.rounded_rectangle((90, y - 80, W - 90, y + 80), 40, fill=(255, 255, 255))
        d.ellipse((130, y - 50, 230, y + 50), fill=OK)
        d.text((180, y), k, font=F(54, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        text(d, (270, y), v, 52, anchor="lm", alpha=a)
    if T >= 6.6:
        text(d, (W / 2, 1590), "저장해두고 한 달에 한 번 보기", 44, fill=SUB, weight="SemiBold", alpha=appear(T, 6.6, 0.3))
    return img


SCENES = [(TOTAL, s_all)]

if __name__ == "__main__":
    if "--preview" in sys.argv:                                   # 확인용 컨택트 시트
        from PIL import Image
        ts = [0, 1.2, 2.0, 3.5, 4.8, 5.8, 7.4]
        sheet = Image.new("RGB", (len(ts) * 270, 480), (0, 0, 0))
        for i, T in enumerate(ts):
            sheet.paste(s_all(T / TOTAL).resize((270, 480)), (i * 270, 0))
        sheet.save(HERE / "_preview.jpg", quality=85)
        sys.exit()
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_shower.mp4"
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
                    str(HERE / "homelivingclub_shower_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
