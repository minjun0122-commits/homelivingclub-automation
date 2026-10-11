"""
홈리빙클럽 릴스 — 생활 문제형 "집에서 냄새 날 때 제일 먼저 볼 곳 3군데"
- 데이터: '누구나 겪는 상황' 포맷(149·139) >> '사려는 사람만 궁금한 정보'(36·8) → 보편 문제 + 덜 알려진 실용 정보
- '제가 하던 것 ㅋㅋ' 가짜 1인칭 말투 없이, 첫 프레임에 3군데가 다 보이게
- 탈취·항균 같은 효능 주장 없음. 발매트는 '세탁기 되는 매트면 자주 빨기 편하다'까지만
- BGM: shampoo/bgm.py 직접 합성 피아노 (코드 진행만 다르게) → mux
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, BG, INK, SUB, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    photo_card, canvas, render, IMGS)
import bgm  # noqa: E402

PHOTO = Image.open(IMGS / "bathmat/extra_khaki.jpg").convert("RGB")
SPOTS = ["욕실·싱크대 배수구", "세탁기 고무패킹", "젖은 발매트·수건"]
PIPE = (176, 182, 190)
WATER = (150, 195, 235)
SMELL = (170, 150, 110)
KHAKI = (150, 160, 140)
# Em7 → Am7 → Dm7 → G
CHORDS = [[52, 55, 59, 62], [45, 48, 52, 55], [50, 53, 57, 60], [43, 47, 50, 55]]


def rows(d, y0):
    for i, s in enumerate(SPOTS):
        y = y0 + i * 170
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=(255, 255, 255))
        d.text((150, y), f"{i + 1}", font=F(52, "ExtraBold"), fill=ACCENT, anchor="mm")
        d.text((210, y), s, font=F(56, "Bold"), fill=INK, anchor="lm")


def smell(d, x, y, k, n=3):
    """물결 냄새 표시"""
    if k <= 0:
        return
    for j in range(n):
        xx = x + (j - 1) * 50
        pts = [(xx + (12 if s % 2 else -12), y - s * 30 * k) for s in range(5)]
        d.line(pts, fill=SMELL, width=8, joint="curve")


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 300), "집에서 냄새 날 때", 92)
    text(d, (W / 2, 420), "제일 먼저 볼 곳 3군데", 92, fill=ACCENT)
    rows(d, 680)
    text(d, (W / 2, 1230), "1번은 의외로 잘 모르는 원인", 56, fill=SUB, weight="SemiBold")
    return img


def s_drain(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 배수구")
    text(d, (W / 2, 400), "물을 오래 안 쓰면", 80)
    text(d, (W / 2, 510), "냄새 막는 물이 말라요", 80, fill=ACCENT, alpha=appear(t, 0.12))
    # U자 배관 (트랩) 단면
    cx, top, bot = W / 2, 700, 1120
    w = 70
    d.rectangle((cx - 220 - w, top, cx - 220 + w, bot - 60), fill=PIPE)              # 왼쪽 관
    d.rectangle((cx + 220 - w, 820, cx + 220 + w, bot - 60), fill=PIPE)              # 오른쪽 관(하수구 쪽)
    d.rectangle((cx + 220 - w, 820, cx + 460, 820 + 2 * w), fill=PIPE)               # 하수구로
    d.pieslice((cx - 220 - w, bot - 220 - w, cx + 220 + w, bot + 80), 0, 180, fill=PIPE)
    d.pieslice((cx - 220 + w, bot - 220 + w, cx + 220 - w, bot + 80 - 2 * w), 0, 180, fill=BG)
    lvl = appear(t, 0.2, 0.5)                                                        # 물 높이 내려감
    wy = 900 + 200 * lvl
    if wy < bot - 60:
        d.rectangle((cx - 220 - w + 10, wy, cx - 220 + w - 10, bot - 60), fill=WATER)
        d.rectangle((cx + 220 - w + 10, wy, cx + 220 + w - 10, bot - 60), fill=WATER)
    if lvl < 0.8:                                                                    # U자 아래 고인 물
        d.pieslice((cx - 220 - w + 10, bot - 220 - w + 10, cx + 220 + w - 10, bot + 70), 0, 180, fill=WATER)
        d.pieslice((cx - 220 + w, bot - 220 + w, cx + 220 - w, bot + 80 - 2 * w), 0, 180, fill=BG)
    d.text((cx + 330, 760), "하수구", font=F(42, "Bold"), fill=SUB, anchor="mm")
    smell(d, cx - 220, 680, appear(t, 0.55, 0.3))
    text(d, (W / 2, 1330), "안 쓰는 배수구엔 가끔 물 한 컵", 56, fill=OK, weight="Bold", alpha=appear(t, 0.7))
    return img


def s_washer(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 세탁기 고무패킹")
    text(d, (W / 2, 400), "빨래 끝나면", 84)
    text(d, (W / 2, 510), "문 열어두고 말리기", 84, fill=OK, alpha=appear(t, 0.12))
    cx, cy = W / 2, 930
    d.rounded_rectangle((cx - 300, cy - 330, cx + 300, cy + 330), 40, fill=(240, 240, 240), outline=(210, 210, 210), width=4)
    d.rectangle((cx - 300, cy - 330, cx + 300, cy - 230), fill=(225, 225, 228))
    d.ellipse((cx - 220, cy - 170, cx + 220, cy + 270), fill=(70, 70, 76))            # 고무패킹
    d.ellipse((cx - 170, cy - 120, cx + 170, cy + 220), fill=(200, 220, 235))         # 유리
    k = appear(t, 0.3, 0.3)
    if k > 0:   # 패킹 아래쪽 고인 물
        d.chord((cx - 220, cy - 170, cx + 220, cy + 270), 60, 120, fill=WATER)
    text(d, (W / 2, 1330), "고무 틈에 고인 물도 한 번 닦기", 56, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_mat(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 젖은 발매트·수건")
    text(d, (W / 2, 400), "축축한 채로 두지 말고", 80)
    text(d, (W / 2, 510), "말리거나 자주 빨기", 84, fill=OK, alpha=appear(t, 0.12))
    cx, cy = W / 2, 930
    d.rounded_rectangle((cx - 320, cy - 190, cx + 320, cy + 190), 30, fill=KHAKI)
    d.rounded_rectangle((cx - 320, cy + 186, cx + 320, cy + 206), 10, fill=(110, 118, 104))
    for i, (dx, dy) in enumerate([(-180, -60), (40, 30), (190, -90), (-60, 110)]):
        k = appear(t, 0.2 + i * 0.08, 0.2)
        if k > 0:
            r = 34 * k
            d.ellipse((cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r), fill=WATER)
    smell(d, cx, cy - 230, appear(t, 0.55, 0.3))
    text(d, (W / 2, 1330), "세탁기 되는 매트면 자주 빨기 편해요", 54, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.6))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 290), "세탁기에 넣어 빠는 규조토 발매트", 60)
    photo_card(img, PHOTO, (110, 400, 970, 1260))
    text(d, (W / 2, 1360), "영상 속 발매트는 저희 스토어 상품이에요", 42, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 330), "님 집은 어디였어요?", 92)
    text(d, (W / 2, 450), "댓글로 번호 남겨주세요", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    rows(d, 700)
    text(d, (W / 2, 1250), "저장해두고 냄새 날 때 보기", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (3.4, s_hook),
    (3.4, s_drain),
    (3.0, s_washer),
    (3.0, s_mat),
    (2.4, s_photo),
    (3.0, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_smell.mp4"
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
                    str(HERE / "homelivingclub_smell_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
