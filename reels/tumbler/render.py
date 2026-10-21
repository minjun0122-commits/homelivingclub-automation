"""
홈리빙클럽 릴스 — "텀블러 뚜껑 고무패킹, 빼본 적 있어요?" (~7.5초)
- 전기포트(7.5초)가 평균 재생 8초(107%, 다시 보기)로 처음 3초 벽을 넘음 → 같은 공식 유지
  · 숨은 때가 '드러나는' 그림 훅 + 숫자가 들어간 구체적 3단계 + 댓글/저장 요청
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만
- 내용: 생활 상식 수준, 건강 효과 주장 없음
- BGM: piano2 (직전 전기포트 = marimba)
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
from common import (W, INK, SUB, ACCENT, OK, F, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

CAFE = (236, 230, 222)
LID = (70, 74, 82)
LID_L = (98, 102, 110)
RUBBER = (210, 214, 220)
SPOT = (40, 44, 30)
# Fmaj7 → G → Em7 → Am7
CHORDS = [[53, 57, 60, 64], [43, 47, 50, 55], [52, 55, 59, 62], [45, 48, 52, 55]]


def lid_top(d, cx, cy, r):
    """위에서 본 텀블러 뚜껑 안쪽 + 고무패킹 링"""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=LID, outline=LID_L, width=10)
    ring = r * 0.82
    d.ellipse((cx - ring, cy - ring, cx + ring, cy + ring), outline=RUBBER, width=44)
    d.ellipse((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), fill=LID_L)
    return ring


def s_hook(t):
    img, d = canvas(CAFE)
    text(d, (W / 2, 250), "텀블러 뚜껑 고무패킹,", 96)
    text(d, (W / 2, 390), "빼본 적 있어요?", 84, fill=ACCENT)
    cx, cy, r = W / 2, 1010, 330
    ring = lid_top(d, cx, cy, r)
    k = appear(t, 0.15, 0.7)                                          # 패킹에 거뭇한 점이 점점 보임
    rng = random.Random(5)
    for i in range(46):
        kk = max(0, min(1, k * 1.6 - i / 46))
        if kk <= 0:
            continue
        a = rng.uniform(0, 2 * math.pi)
        rad = ring + rng.uniform(-12, 12)
        x, y = cx + rad * math.cos(a), cy + rad * math.sin(a)
        s = rng.uniform(9, 20) * kk
        d.ellipse((x - s, y - s, x + s, y + s), fill=SPOT)
    return img


STEPS = [("1", "이쑤시개로 패킹 빼기"), ("2", "베이킹소다 물에 30분"), ("3", "바짝 말리고 끼우기")]


def s_steps(t):
    img, d = canvas()
    text(d, (W / 2, 330), "패킹 관리, 이렇게 끝", 80)
    for i, (k, v) in enumerate(STEPS):
        a = appear(t, 0.05 + i * 0.22, 0.15)
        if a <= 0:
            continue
        y = 640 + i * 300
        d.rounded_rectangle((110, y - 110, W - 110, y + 110), 40, fill=(255, 255, 255))
        d.ellipse((160, y - 60, 280, y + 60), fill=OK)
        d.text((220, y), k, font=F(64, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        d.text((330, y), v, font=F(60, "Bold"), fill=INK, anchor="lm")
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 720), "오늘 뚜껑 한 번 뒤집어보세요", 78)
    text(d, (W / 2, 860), "검은 점 있었다면 댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    text(d, (W / 2, 1100), "저장해두고 일주일에 한 번 보기", 54, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


SCENES = [
    (1.8, s_hook),
    (3.6, s_steps),
    (2.1, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_tumbler.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total, CHORDS, "piano2")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_tumbler_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
