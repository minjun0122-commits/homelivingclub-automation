"""
홈리빙클럽 릴스 — 공감형 "냉장고 열면 매번 나오는 것 3가지"
- 샴푸 릴스(공감형, 조회 149) 포맷 그대로: 1인칭 공감 + 체크리스트, 첫 프레임에 3가지가 다 보이게
- 수치·효능 주장 없음 (정리 습관 팁만), 상품은 사진 한 장 + 자사 상품 표기
- 마지막은 댓글 유도 CTA
- BGM: shampoo/bgm.py 로 직접 합성한 잔잔한 피아노 (코드 진행만 다르게) → mux
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

PHOTO = Image.open(IMGS / "fridge/main.jpg").convert("RGB")
ITEMS = ["유통기한 지난 소스", "또 사온 두부", "구석에 숨은 반찬통"]
SHELF = (236, 240, 242)
GLASS = (214, 226, 232)
# C → Am → F → G (샴푸 릴스와 다른 진행, 같은 잔잔한 피아노)
CHORDS = [[48, 52, 55, 59], [45, 48, 52, 55], [53, 57, 60, 64], [55, 59, 62, 65]]


def checklist(d, y0):
    for i, s in enumerate(ITEMS):
        y = y0 + i * 170
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=(255, 255, 255))
        d.text((150, y), f"{i + 1}", font=F(52, "ExtraBold"), fill=SUB, anchor="mm")
        d.text((210, y), s, font=F(56, "Bold"), fill=INK, anchor="lm")
        d.text((W - 290, y), "있음", font=F(46, "SemiBold"), fill=ACCENT, anchor="mm")
        mark(d, W - 150, y, False, 1.0)


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 300), "냉장고 열면", 92)
    text(d, (W / 2, 420), "매번 나오는 것 3가지", 92, fill=ACCENT)
    checklist(d, 680)
    text(d, (W / 2, 1230), "다 우리 집 얘기 ㅋㅋ", 58, fill=SUB, weight="SemiBold")
    return img


def s_sauce(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 유통기한 지난 소스")
    text(d, (W / 2, 400), "소스는 문 칸에", 84)
    text(d, (W / 2, 510), "라벨 보이게 한 줄로", 84, fill=OK, alpha=appear(t, 0.12))
    # 냉장고 문 칸 + 소스병 (라벨이 앞으로)
    x0, x1, y = 170, W - 170, 1080
    d.rounded_rectangle((x0, y, x1, y + 70), 20, fill=GLASS)
    cols = [(226, 86, 60), (240, 190, 70), (120, 160, 90), (150, 100, 70), (90, 130, 190)]
    for i, c in enumerate(cols):
        k = appear(t, 0.15 + i * 0.08, 0.2)
        if k <= 0:
            continue
        cx = x0 + 90 + i * 150
        top = y - 300 * k
        d.rounded_rectangle((cx - 50, top, cx + 50, y + 20), 24, fill=c)
        d.rounded_rectangle((cx - 22, top - 50, cx + 22, top + 10), 10, fill=c)
        d.rounded_rectangle((cx - 42, y - 170, cx + 42, y - 80), 10, fill=(255, 255, 255))
    text(d, (W / 2, 1300), "날짜가 보이면 먼저 쓰게 돼요", 58, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_rebuy(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 또 사온 두부")
    text(d, (W / 2, 400), "장 보기 전에", 84)
    text(d, (W / 2, 510), "냉장고 사진 한 장", 84, fill=OK, alpha=appear(t, 0.12))
    # 휴대폰 + 화면 속 냉장고 칸
    cx, top = W / 2, 640
    d.rounded_rectangle((cx - 210, top, cx + 210, top + 640), 50, fill=INK)
    d.rounded_rectangle((cx - 185, top + 40, cx + 185, top + 600), 30, fill=SHELF)
    k = appear(t, 0.25, 0.3)
    if k > 0:
        for r in range(3):
            yy = top + 80 + r * 170
            d.line((cx - 165, yy + 140, cx + 165, yy + 140), fill=GLASS, width=6)
            for j in range(3):
                if (r * 3 + j) / 9 > k:
                    continue
                x = cx - 150 + j * 105
                d.rounded_rectangle((x, yy + 40, x + 85, yy + 135), 14,
                                    fill=[(250, 250, 245), (240, 200, 120), (190, 220, 180)][(r + j) % 3])
    text(d, (W / 2, 1390), "마트에서 열어보면 끝", 58, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_back(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 구석에 숨은 반찬통")
    text(d, (W / 2, 400), "먼저 산 건 앞으로", 84, fill=OK)
    text(d, (W / 2, 510), "새로 산 건 뒤로", 84, alpha=appear(t, 0.12))
    k = appear(t, 0.25, 0.4)
    # 뒤 줄(새로 산 것) / 앞 줄(먼저 산 것)
    for row, (y, lab, col, w) in enumerate([(760, "새로 산 것", (200, 205, 210), 150), (1000, "먼저 산 것", (200, 228, 210), 190)]):
        if row == 1 and k <= 0:
            continue
        a = 1 if row == 0 else k
        for j in range(3):
            x = 170 + j * (w + 40) + (0 if row == 0 else -40 * (1 - a))
            d.rounded_rectangle((x, y, x + w, y + (130 if row == 0 else 170)), 22, fill=col)
        d.text((170, y - 45), lab, font=F(48, "Bold"), fill=INK if row else SUB, anchor="lm")
    d.line((120, 1200, W - 120, 1200), fill=GLASS, width=10)
    text(d, (W / 2, 1330), "앞에 있는 것부터 꺼내 먹기", 58, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 280), "안 보이면 또 사게 되니까", 70)
    text(d, (W / 2, 380), "속이 보이는 투명 케이스", 70, fill=OK)
    photo_card(img, PHOTO, (130, 470, 950, 1290))
    text(d, (W / 2, 1390), "영상 속 케이스는 저희 스토어 상품이에요", 44, fill=SUB, weight="SemiBold", alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 330), "님 냉장고엔 몇 개 있어요?", 84)
    text(d, (W / 2, 450), "댓글로 알려주세요", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    checklist(d, 700)
    text(d, (W / 2, 1250), "저장해두고 장 보기 전에 보기", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (3.4, s_hook),
    (3.0, s_sauce),
    (3.0, s_rebuy),
    (3.0, s_back),
    (2.8, s_photo),
    (3.0, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_fridge2.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total, CHORDS)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    # 인스타 웹 업로드용 (어제 통과한 설정)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_fridge2_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
