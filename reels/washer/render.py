"""
홈리빙클럽 릴스 — "세탁기 세제통, 통째로 빼본 적 있어요?" (~7.5초)
- 전기포트 공식(평균 재생 107%) 반복: 숨은 때가 드러나는 그림 훅 + 숫자 있는 3단계 + 댓글/저장 요청
- 상품: 영상에 넣지 않음, 캡션 끝에 스토어 안내만
- 내용: 생활 상식 수준, 건강 효과 주장 없음 / 빼는 방법은 모델마다 달라서 '설명서 확인' 문구
- BGM: marimba2 (직전 텀블러 = piano2)
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

LAUNDRY = (226, 232, 240)
BODY = (248, 248, 250)
EDGE = (196, 200, 208)
SLOT = (222, 226, 232)
GUNK = (120, 112, 84)
# Am7 → Dm7 → G → Cmaj7
CHORDS = [[45, 48, 52, 55], [50, 53, 57, 60], [43, 47, 50, 55], [48, 52, 55, 59]]


def drawer(d, x0, y0, x1, y1, k):
    """반쯤 빼낸 세제 서랍을 위에서 본 모습 (칸 3개)"""
    d.rounded_rectangle((x0 - 30, y0 - 60, x1 + 30, y1 + 30), 40, fill=BODY, outline=EDGE, width=6)
    w = (x1 - x0) / 3
    rng = random.Random(7)
    for i, (lbl, frac) in enumerate([("세제", 1.0), ("유연제", 0.6), ("표백", 0.8)]):
        sx0, sx1 = x0 + i * w + 14, x0 + (i + 1) * w - 14
        d.rounded_rectangle((sx0, y0, sx1, y1), 26, fill=SLOT, outline=EDGE, width=4)
        d.text(((sx0 + sx1) / 2, y0 - 30), lbl, font=F(36, "Bold"), fill=SUB, anchor="mm")
        for j in range(18):                                          # 칸 바닥·모서리에 끼는 찌꺼기
            kk = max(0, min(1, k * 1.6 - j / 18)) * frac
            if kk <= 0:
                continue
            x = rng.uniform(sx0 + 16, sx1 - 16)
            y = rng.choice([rng.uniform(y1 - 70, y1 - 18), rng.uniform(y0 + 18, y1 - 18)])
            r = rng.uniform(10, 22) * kk
            d.ellipse((x - r * 1.3, y - r, x + r * 1.3, y + r), fill=GUNK)


def s_hook(t):
    img, d = canvas(LAUNDRY)
    text(d, (W / 2, 250), "세탁기 세제통,", 104)
    text(d, (W / 2, 390), "통째로 빼본 적 있어요?", 80, fill=ACCENT)
    drawer(d, 170, 780, W - 170, 1260, appear(t, 0.15, 0.7))
    return img


STEPS = [("1", "서랍 통째로 빼기"), ("2", "미지근한 물에 10분"), ("3", "칫솔로 틈 닦고 말리기")]


def s_steps(t):
    img, d = canvas()
    text(d, (W / 2, 330), "세제통 관리, 이렇게 끝", 80)
    for i, (k, v) in enumerate(STEPS):
        a = appear(t, 0.05 + i * 0.22, 0.15)
        if a <= 0:
            continue
        y = 640 + i * 300
        d.rounded_rectangle((110, y - 110, W - 110, y + 110), 40, fill=(255, 255, 255))
        d.ellipse((160, y - 60, 280, y + 60), fill=OK)
        d.text((220, y), k, font=F(64, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        d.text((330, y), v, font=F(60, "Bold"), fill=INK, anchor="lm")
    text(d, (W / 2, 1600), "빼는 방법은 모델마다 달라요 (설명서 확인)", 40, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.7))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 720), "오늘 빨래할 때 한 번 빼보세요", 76)
    text(d, (W / 2, 860), "찌꺼기 있었다면 댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
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
    out = HERE / "homelivingclub_washer.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total, CHORDS, "marimba2")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_washer_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
