"""
홈리빙클럽 릴스 — 솔직 단점형 "저희 화병 세트 단점 3가지, 솔직하게"
- 파는 쪽이 먼저 단점을 말하는 포맷 ('제가 하던 것 3가지' 틀 탈피)
- 단점은 상품 정보에 실제로 적힌 것만: 플라스틱이라 물 X(조화 전용) / 화병·튤립 택배 2개 / 튤립 34cm > 화병 14.5cm
- 화병·튤립 그림은 실제 상품 사진(white_pink.jpg)에서 잘라서 cm 비율 맞춤
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

SRC = Image.open(IMGS / "vase_tulip_set/white_pink.jpg").convert("RGB")
VASE = SRC.crop((180, 355, 420, 670))          # 화병 몸통 (높이 14.5cm)
TULIP = SRC.crop((650, 135, 765, 865))         # 튤립 1송이 (34cm)
BOX = (214, 186, 150)
CONS = ["물 못 담아요", "택배가 2개로 와요", "튤립이 화병보다 길어요"]
PROS = ["안 시들어요", "가볍고 안 깨져요", "화병까지 16,900원"]
# Am7 → Fmaj7 → C → G
CHORDS = [[45, 48, 52, 55], [53, 57, 60, 64], [48, 52, 55, 60], [43, 47, 50, 55]]


def rows(d, y0, items, label, col, good):
    for i, s in enumerate(items):
        y = y0 + i * 170
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=(255, 255, 255))
        d.text((150, y), f"{i + 1}", font=F(52, "ExtraBold"), fill=SUB, anchor="mm")
        d.text((210, y), s, font=F(54, "Bold"), fill=INK, anchor="lm")
        if label:
            d.text((W - 150, y), label, font=F(44, "SemiBold"), fill=col, anchor="mm")
        else:
            mark(d, W - 150, y, good, 1.0)


def _tulip_alpha(im):
    """가장자리에서 이어진 흰 배경만 투명 처리 (연한 꽃잎은 남김)"""
    from PIL import ImageDraw
    m = im.convert("L").point(lambda v: 255 if v > 246 else 0)   # 흰 후보
    for xy in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1),
               (im.width // 2, 0), (im.width // 2, im.height - 1)]:
        if m.getpixel(xy) == 255:
            ImageDraw.floodfill(m, xy, 128)
    a = m.point(lambda v: 0 if v == 128 else 255)
    out = im.convert("RGBA")
    out.putalpha(a)
    return out


TULIP = _tulip_alpha(TULIP)                     # 흰 배경 제거


def paste_h(img, im, x, bottom, h):
    sp = im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)
    if sp.mode == "RGBA":
        mask = sp
    else:                                        # 사진 블록은 모서리 둥글게
        mask = Image.new("L", sp.size, 0)
        from PIL import ImageDraw
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *sp.size), int(sp.width * 0.08), fill=255)
    img.paste(sp.convert("RGB"), (int(x - sp.width / 2), int(bottom - h)), mask if sp.mode != "RGBA" else sp)
    return sp.width


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 300), "저희 화병 세트", 88)
    text(d, (W / 2, 420), "단점 3가지, 솔직하게", 88, fill=ACCENT)
    rows(d, 680, CONS, "단점", ACCENT, False)
    text(d, (W / 2, 1230), "사기 전에 꼭 보세요", 58, fill=SUB, weight="SemiBold")
    return img


def s_water(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 물 못 담아요")
    text(d, (W / 2, 400), "플라스틱 화병이라", 84)
    text(d, (W / 2, 510), "조화·드라이플라워 전용", 80, fill=ACCENT, alpha=appear(t, 0.12))
    paste_h(img, VASE, W / 2, 1220, 520)
    k = appear(t, 0.35, 0.25)
    if k > 0:   # 물방울 + X
        cx, cy = W / 2 + 300, 820
        d.ellipse((cx - 50, cy - 20, cx + 50, cy + 80), fill=(150, 195, 235))
        d.polygon([(cx - 44, cy + 10), (cx, cy - 80), (cx + 44, cy + 10)], fill=(150, 195, 235))
        mark(d, cx, cy + 20, False, k)
    return img


def box(d, cx, cy, label, k):
    if k <= 0:
        return
    s = 200 * k
    d.rounded_rectangle((cx - s, cy - s * 0.7, cx + s, cy + s * 0.7), 18, fill=BOX)
    d.rectangle((cx - s * 0.12, cy - s * 0.7, cx + s * 0.12, cy + s * 0.7), fill=(236, 220, 190))
    if k > 0.8:
        d.text((cx, cy + s * 0.7 + 60), label, font=F(52, "Bold"), fill=INK, anchor="mm")


def s_ship(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 택배가 2개로 와요")
    text(d, (W / 2, 400), "화병이랑 튤립이", 84)
    text(d, (W / 2, 510), "따로 출발해요", 84, fill=ACCENT, alpha=appear(t, 0.12))
    box(d, 300, 880, "화병", appear(t, 0.2, 0.25))
    box(d, 780, 880, "튤립", appear(t, 0.35, 0.25))
    d.text((W / 2, 880), "+", font=F(90, "Bold"), fill=SUB, anchor="mm")
    text(d, (W / 2, 1300), "하루 이틀 차이로 도착할 수 있어요", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_length(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 튤립이 화병보다 길어요")
    text(d, (W / 2, 400), "그대로 꽂으면 길쭉해요", 80)
    text(d, (W / 2, 510), "줄기 구부려서 높이 맞추기", 80, fill=OK, alpha=appear(t, 0.12))
    floor, px = 1330, 19.0                              # cm → px (같은 비율)
    paste_h(img, VASE, 380, floor, 14.5 * px)
    paste_h(img, TULIP, 760, floor, 34 * px)
    d.line((90, floor, W - 90, floor), fill=(200, 196, 190), width=4)
    d.text((380, floor - 14.5 * px - 45), "화병 14.5cm", font=F(44, "Bold"), fill=SUB, anchor="mm")
    d.text((560, floor - 34 * px + 30), "튤립 34cm", font=F(44, "Bold"), fill=SUB, anchor="mm")
    text(d, (W / 2, 1420), "줄기 속 철사로 구부러져요", 52, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_pros(t):
    img, d = canvas()
    text(d, (W / 2, 330), "그래도 좋은 점", 92, fill=OK)
    for i, s in enumerate(PROS):
        k = appear(t, 0.1 + i * 0.15, 0.2)
        if k <= 0:
            continue
        y = 640 + i * 170
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=(255, 255, 255))
        d.text((150, y), f"{i + 1}", font=F(52, "ExtraBold"), fill=SUB, anchor="mm")
        d.text((210, y), s, font=F(54, "Bold"), fill=INK, anchor="lm")
        mark(d, W - 150, y, True, k)
    return img


def s_photo(t):
    img, d = canvas()
    text(d, (W / 2, 280), "화병 4색 × 튤립 조합 4가지", 64)
    photo_card(img, SRC, (90, 380, 990, 1280))
    text(d, (W / 2, 1380), "영상 속 화병·튤립 세트는 저희 스토어 상품이에요", 40, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.3))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 640), "더 궁금한 거 있으면", 76)
    text(d, (W / 2, 760), "댓글로 물어보세요", 92, fill=ACCENT, alpha=appear(t, 0.1))
    text(d, (W / 2, 900), "단점도 솔직하게 답할게요", 58, fill=SUB, weight="SemiBold", alpha=appear(t, 0.3))
    return img


SCENES = [
    (3.4, s_hook),
    (3.0, s_water),
    (3.0, s_ship),
    (3.2, s_length),
    (2.8, s_pros),
    (2.4, s_photo),
    (2.6, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_honest.mp4"
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
                    str(HERE / "homelivingclub_honest_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
