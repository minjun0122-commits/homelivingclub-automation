"""
홈리빙클럽 릴스 — "전자레인지 천장, 올려다본 적 있어요?" (~7.5초)
- 같은 7.5초 구조(훅 1.8초 → 3단계 3.6초 → CTA 2.1초) 유지
- 변경점: 커버(첫 프레임)부터 얼룩이 이미 보이게 → 0초에 절반, 이후 더 진해짐 (텀블러·세탁기는 0초가 빈 그림이었음)
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만
- 내용: 생활 상식 수준(물+식초 수증기), 건강 효과 주장 없음
- BGM: piano (직전 세탁기 = marimba2)
"""
import random
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, INK, SUB, ACCENT, OK, F, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

KITCHEN = (236, 232, 226)
BODY = (60, 64, 70)
BODY_L = (92, 96, 104)
CAVITY = (214, 210, 200)
CEIL = (232, 228, 218)
WALL = (196, 192, 182)
PLATE = (246, 246, 244)
SPLAT = (150, 104, 60)
# Gmaj7 → Em7 → Cmaj7 → D
CHORDS = [[43, 47, 50, 54], [40, 43, 47, 50], [48, 52, 55, 59], [50, 54, 57, 62]]


def microwave(d, k):
    """문 열린 전자레인지 안쪽 (정면, 천장이 보이게 살짝 아래에서 본 모습)"""
    x0, y0, x1, y1 = 120, 640, W - 120, 1380
    d.rounded_rectangle((x0 - 30, y0 - 30, x1 + 30, y1 + 30), 50, fill=BODY, outline=BODY_L, width=8)
    ix0, iy0, ix1, iy1 = x0 + 30, y0 + 30, x1 - 190, y1 - 30          # 안쪽 공간 (오른쪽은 조작부)
    bx0, by0, bx1, by1 = ix0 + 120, iy0 + 170, ix1 - 120, iy1 - 120   # 뒷벽
    d.rectangle((ix0, iy0, ix1, iy1), fill=CAVITY)
    d.polygon([(ix0, iy0), (ix1, iy0), (bx1, by0), (bx0, by0)], fill=CEIL)   # 천장
    d.rectangle((bx0, by0, bx1, by1), fill=WALL)
    d.ellipse((bx0 - 40, by1 - 30, bx1 + 40, iy1 - 10), fill=PLATE, outline=WALL, width=4)  # 회전접시
    for j in range(4):                                                # 조작부 버튼
        cy = y0 + 120 + j * 130
        d.rounded_rectangle((x1 - 150, cy - 40, x1 - 30, cy + 40), 20, fill=BODY_L)
    rng = random.Random(11)
    for i in range(55):                                               # 천장·뒷벽 윗부분에 튄 얼룩
        kk = max(0, min(1, k * 1.5 - i / 55 * 0.5))
        if i < 30:
            u = rng.uniform(0.05, 0.95)
            v = rng.uniform(0.1, 0.9)
            xa = ix0 + (bx0 - ix0) * v
            xb = ix1 + (bx1 - ix1) * v
            x, y = xa + (xb - xa) * u, iy0 + (by0 - iy0) * v
        else:
            x, y = rng.uniform(bx0 + 20, bx1 - 20), rng.uniform(by0 + 10, by0 + 160)
        r = rng.uniform(8, 20) * kk
        if r > 1:
            d.ellipse((x - r * 1.4, y - r, x + r * 1.4, y + r), fill=SPLAT)


def s_hook(t):
    img, d = canvas(KITCHEN)
    text(d, (W / 2, 250), "전자레인지 천장,", 104)
    text(d, (W / 2, 390), "올려다본 적 있어요?", 84, fill=ACCENT)
    microwave(d, 0.45 + 0.55 * appear(t, 0.1, 0.6))                    # 첫 프레임부터 얼룩이 보임
    return img


STEPS = [("1", "물 1컵 + 식초 1스푼"), ("2", "3분 돌리고 5분 두기"), ("3", "불은 얼룩 행주로 닦기")]


def s_steps(t):
    img, d = canvas()
    text(d, (W / 2, 330), "천장 얼룩, 이렇게 끝", 80)
    for i, (k, v) in enumerate(STEPS):
        a = appear(t, 0.05 + i * 0.22, 0.15)
        if a <= 0:
            continue
        y = 640 + i * 300
        d.rounded_rectangle((110, y - 110, W - 110, y + 110), 40, fill=(255, 255, 255))
        d.ellipse((160, y - 60, 280, y + 60), fill=OK)
        d.text((220, y), k, font=F(64, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        d.text((330, y), v, font=F(60, "Bold"), fill=INK, anchor="lm")
    text(d, (W / 2, 1600), "그릇은 전자레인지용으로 (뜨거우니 조심)", 40, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.7))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 720), "오늘 데울 때 한 번 올려다보세요", 72)
    text(d, (W / 2, 860), "얼룩 있었다면 댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    text(d, (W / 2, 1100), "저장해두고 한 달에 한 번 보기", 54, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


SCENES = [
    (1.8, s_hook),
    (3.6, s_steps),
    (2.1, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_microwave.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total, CHORDS, "piano")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_microwave_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
