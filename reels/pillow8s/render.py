"""
홈리빙클럽 릴스 — 짧은 버전 실험 "베개, 마지막으로 빤 게 언제예요?" (~7.5초)
- 데이터(Business Suite): 13초 릴스들 평균 재생 3~5초, 형식과 상관없이 비슷 → 대부분 앞부분만 보고 넘김
  → 질문 훅은 유지하고 영상 길이를 7~8초로 줄여 끝까지 보는 비율 확인
- 구성: 질문 + 그림(1.8초) → 팁 3개 한 화면(3.6초) → 댓글/저장 요청(2.1초)
- 상품: 영상에 넣지 않음 (억지 연결 X), 캡션 끝에 스토어 안내만
- 내용: 생활 상식 수준, 건강·위생 효과 주장 없음
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, BG, INK, SUB, ACCENT, OK, F, appear, text, mark, canvas, render)  # noqa: E402
import bgm  # noqa: E402

BED = (232, 226, 236)
PILLOW = (250, 250, 252)
EDGE = (214, 214, 222)
STAIN = (234, 218, 170)
# Cmaj7 → Am7 → Fmaj7 → G
CHORDS = [[48, 52, 55, 59], [45, 48, 52, 55], [41, 45, 48, 52], [43, 47, 50, 55]]


def pillow(d, cx, cy, s=1.0):
    w, h = 380 * s, 230 * s
    d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), int(120 * s), fill=PILLOW, outline=EDGE, width=6)
    d.arc((cx - w * 0.7, cy - h * 0.5, cx + w * 0.7, cy + h * 0.5), 200, 340, fill=EDGE, width=5)


def s_hook(t):
    img, d = canvas(BED)
    text(d, (W / 2, 250), "베개,", 110)
    text(d, (W / 2, 390), "마지막으로 빤 게 언제예요?", 78, fill=ACCENT)
    pillow(d, W / 2, 960, 1.15)
    k = appear(t, 0.15, 0.6)                                          # 누런 얼룩이 번짐
    for i, (x, y, r) in enumerate([(-110, -20, 80), (40, 30, 58), (190, -50, 36), (-30, 100, 32), (120, 90, 22)]):
        kk = max(0, min(1, k * 1.5 - i * 0.12))
        if kk > 0:
            rr = r * kk
            d.ellipse((W / 2 + x - rr * 1.3, 960 + y - rr, W / 2 + x + rr * 1.3, 960 + y + rr), fill=STAIN)
    return img


TIPS = [("커버", "수건처럼 자주 빨기"), ("속통", "가끔 바람에 바짝 말리기"), ("아침", "이불 젖혀서 열기 빼기")]


def s_tips(t):
    img, d = canvas()
    text(d, (W / 2, 330), "베개 관리, 이 3개면 끝", 80)
    for i, (k, v) in enumerate(TIPS):
        a = appear(t, 0.05 + i * 0.22, 0.15)
        if a <= 0:
            continue
        y = 640 + i * 300
        d.rounded_rectangle((110, y - 110, W - 110, y + 110), 40, fill=(255, 255, 255))
        d.rounded_rectangle((150, y - 60, 330, y + 60), 30, fill=OK)
        d.text((240, y), k, font=F(56, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        d.text((370, y), v, font=F(60, "Bold"), fill=INK, anchor="lm")
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 720), "오늘 베개 커버 벗겨보세요", 80)
    text(d, (W / 2, 860), "마지막으로 빤 날, 댓글로", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    text(d, (W / 2, 1100), "저장해두고 빨래하는 날 보기", 54, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


SCENES = [
    (1.8, s_hook),
    (3.6, s_tips),
    (2.1, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_pillow8s.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total, CHORDS)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_pillow8s_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
