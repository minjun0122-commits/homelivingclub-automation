"""
홈리빙클럽 릴스 — "전기포트 안, 마지막으로 들여다본 게 언제예요?" (~7.5초, 짧은 버전 2회차)
- 베개(7.5초) 실험과 같은 구조: 질문 + 그림(1.8초) → 방법 3단계 한 화면(3.6초) → 댓글/저장 요청(2.1초)
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만
- 내용: 생활 상식 수준(구연산 물때 제거), 건강 효과 주장 없음
- BGM: marimba (직전 베개 = piano)
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, BG, INK, SUB, ACCENT, OK, F, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

KITCHEN = (226, 234, 236)
STEEL = (196, 202, 208)
STEEL_D = (150, 158, 166)
INSIDE = (120, 128, 136)
SCALE = (238, 236, 226)
# Dm7 → G → Cmaj7 → Am7
CHORDS = [[50, 53, 57, 60], [43, 47, 50, 55], [48, 52, 55, 59], [45, 48, 52, 55]]


def kettle_top(d, cx, cy, r):
    """위에서 내려다본 전기포트 안쪽"""
    d.ellipse((cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40), fill=STEEL, outline=STEEL_D, width=8)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INSIDE)
    d.ellipse((cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35), outline=STEEL_D, width=6)   # 바닥 열판
    d.rounded_rectangle((cx + r + 30, cy - 70, cx + r + 120, cy + 70), 30, fill=STEEL, outline=STEEL_D, width=8)


def s_hook(t):
    img, d = canvas(KITCHEN)
    text(d, (W / 2, 250), "전기포트 안,", 104)
    text(d, (W / 2, 390), "마지막으로 들여다본 게 언제예요?", 70, fill=ACCENT)
    cx, cy, r = W / 2 - 40, 1000, 300
    kettle_top(d, cx, cy, r)
    k = appear(t, 0.15, 0.7)                                          # 하얀 물때가 점점 보임
    rng = __import__("random").Random(3)
    for i in range(60):
        kk = max(0, min(1, k * 1.6 - i / 60))
        if kk <= 0:
            continue
        a = rng.uniform(0, 6.283)
        rad = rng.uniform(0.45, 0.95) * r
        x, y = cx + rad * __import__("math").cos(a), cy + rad * __import__("math").sin(a)
        s = rng.uniform(6, 16) * kk
        d.ellipse((x - s, y - s, x + s, y + s), fill=SCALE)
    return img


STEPS = [("1", "물 + 구연산 1스푼"), ("2", "한 번 끓이고 30분"), ("3", "버리고 맹물 한 번 더")]


def s_steps(t):
    img, d = canvas()
    text(d, (W / 2, 330), "하얀 물때, 이렇게 끝", 80)
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
    text(d, (W / 2, 720), "오늘 뚜껑 한 번 열어보세요", 80)
    text(d, (W / 2, 860), "하얀 점 보였다면 댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
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
    out = HERE / "homelivingclub_kettle.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total, CHORDS, "marimba")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_kettle_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
