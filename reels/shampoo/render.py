"""
홈리빙클럽 릴스 — 공감형 "머리 감을 때 내가 하던 것 3가지"
- 계정 피드백 반영: 1인칭 공감 + 리스트 (정신건강 게시물 스타일), 첫 프레임에 3가지가 다 보이게
- ⚠️ 효능 표현 금지 (탈모·두피건강·혈액순환 X) → 감는 습관 팁만, 상품은 '손톱 대신 쓰는 도구'로만
- 마지막은 댓글 유도 CTA
- BGM: bgm.py 로 직접 합성한 잔잔한 피아노 (저작권 없음) → mux
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from common import (W, BG, INK, SUB, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    photo_card, canvas, render, IMGS)
import bgm  # noqa: E402

PHOTO = Image.open(IMGS / "shampoobrush/main.jpg").convert("RGB")
HAIR = (70, 58, 50)
ITEMS = ["손톱으로 벅벅", "거품 대충 헹구기", "린스를 두피까지"]


def checklist(d, y0, k=1.0):
    for i, s in enumerate(ITEMS):
        y = y0 + i * 170
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=(255, 255, 255))
        d.text((150, y), f"{i + 1}", font=F(52, "ExtraBold"), fill=SUB, anchor="mm")
        d.text((210, y), s, font=F(56, "Bold"), fill=INK, anchor="lm")
        d.text((W - 290, y), "했음", font=F(46, "SemiBold"), fill=ACCENT, anchor="mm")
        mark(d, W - 150, y, False, k)


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 300), "머리 감을 때", 92)
    text(d, (W / 2, 420), "제가 하던 것 3가지", 92, fill=ACCENT)
    checklist(d, 680)
    text(d, (W / 2, 1230), "셋 다 하고 있었음 ㅋㅋ", 58, fill=SUB, weight="SemiBold")
    return img


def s_nail(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 손톱으로 벅벅")
    text(d, (W / 2, 400), "손톱 말고", 84)
    text(d, (W / 2, 510), "손가락 지문 쪽으로", 84, fill=OK, alpha=appear(t, 0.12))
    # 손가락 옆모습: 손톱(위) / 지문(아래)
    for i, (good, lab) in enumerate([(False, "손톱 끝"), (True, "지문 쪽")]):
        k = appear(t, 0.2 + i * 0.2, 0.25)
        if k <= 0:
            continue
        cx, cy = W / 2, 800 + i * 330
        d.rounded_rectangle((cx - 330, cy - 70, cx + 150, cy + 70), 70, fill=(240, 205, 180))
        d.rounded_rectangle((cx + 20, cy - 70, cx + 150, cy - 10), 26, fill=(250, 232, 222) if not good else (240, 205, 180))
        hi = (cx + 150, cy - 60) if not good else (cx + 110, cy + 70)
        d.ellipse((hi[0] - 34, hi[1] - 34, hi[0] + 34, hi[1] + 34), outline=ACCENT if not good else OK, width=8)
        d.text((cx + 260, cy), lab, font=F(52, "Bold"), fill=INK, anchor="lm")
        mark(d, cx - 420, cy, good, k)
    return img


def s_rinse(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 거품 대충 헹구기")
    text(d, (W / 2, 400), "헹구는 시간은", 84)
    text(d, (W / 2, 510), "샴푸한 시간보다 길게", 84, fill=OK, alpha=appear(t, 0.12))
    k1, k2 = appear(t, 0.2, 0.3), appear(t, 0.4, 0.4)
    for i, (lab, w, col, k) in enumerate([("샴푸", 330, SOFT, k1), ("헹굼", 680, (200, 228, 210), k2)]):
        y = 790 + i * 220
        d.text((150, y), lab, font=F(56, "Bold"), fill=INK, anchor="lm")
        if k > 0:
            d.rounded_rectangle((300, y - 60, 300 + w * k, y + 60), 30, fill=col)
    text(d, (W / 2, 1300), "미끈거림 없어질 때까지", 58, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_conditioner(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 린스를 두피까지")
    text(d, (W / 2, 400), "린스·트리트먼트는", 84)
    text(d, (W / 2, 510), "두피 말고 머리 끝에", 84, fill=OK, alpha=appear(t, 0.12))
    cx, top, bottom = W / 2, 680, 1300
    d.ellipse((cx - 210, top, cx + 210, top + 300), fill=HAIR)             # 머리 윗부분
    for j in range(9):                                                    # 머리카락
        x = cx - 200 + j * 50
        d.rounded_rectangle((x, top + 150, x + 34, bottom), 17, fill=HAIR)
    k = appear(t, 0.3, 0.4)
    if k > 0:
        y0 = bottom - (bottom - 1000) * k
        d.rounded_rectangle((cx - 240, y0, cx + 240, bottom + 30), 30, outline=OK, width=10)
        d.text((cx + 270, (y0 + bottom) / 2), "여기만", font=F(54, "ExtraBold"), fill=OK, anchor="lm")
    d.text((cx + 270, top + 150), "두피", font=F(50, "Bold"), fill=SUB, anchor="lm")
    mark(d, cx + 440, top + 150, False, appear(t, 0.5))
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 280), "손가락 끝이 귀찮을 땐", 70)
    text(d, (W / 2, 380), "실리콘 샴푸 브러시", 70, fill=OK)
    photo_card(img, PHOTO, (130, 470, 950, 1290))
    text(d, (W / 2, 1390), "영상 속 브러시는 저희 스토어 상품이에요", 44, fill=SUB, weight="SemiBold", alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 330), "님은 몇 개 했어요?", 92)
    text(d, (W / 2, 450), "댓글로 알려주세요", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    checklist(d, 700, k=1.0)
    text(d, (W / 2, 1250), "저장해두고 머리 감을 때 보기", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (3.4, s_hook),
    (3.0, s_nail),
    (3.0, s_rinse),
    (3.0, s_conditioner),
    (2.8, s_photo),
    (3.0, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_shampoo.mp4"
    render(SCENES, silent, HERE / "_frames")
    total = sum(s for s, _ in SCENES)
    wav = HERE / "_bgm.wav"
    bgm.make(wav, total)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
