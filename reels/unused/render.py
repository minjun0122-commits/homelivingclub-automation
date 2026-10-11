"""
홈리빙클럽 릴스 — 순수 공감형 "자취하면 꼭 사는데 결국 안 쓰는 것 3가지"
- 상품 홍보 없음 (저장·공유·팔로우 실험용), 첫 프레임에 3가지가 다 보이게
- 마지막은 "4번째는 뭐예요?" 댓글 유도
- BGM: shampoo/bgm.py 직접 합성 피아노 (코드 진행만 다르게) → mux
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, BG, INK, SUB, ACCENT, OK, SOFT, F, appear, text, chip, mark,  # noqa: E402
                    canvas, render)
import bgm  # noqa: E402

ITEMS = ["홈트 기구", "대용량 식재료", "예쁜 그릇 세트"]
METAL = (120, 124, 130)
# Dm7 → G7 → Cmaj7 → Am7
CHORDS = [[50, 53, 57, 60], [55, 59, 62, 65], [48, 52, 55, 59], [45, 48, 52, 55]]


def checklist(d, y0):
    for i, s in enumerate(ITEMS):
        y = y0 + i * 170
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=(255, 255, 255))
        d.text((150, y), f"{i + 1}", font=F(52, "ExtraBold"), fill=SUB, anchor="mm")
        d.text((210, y), s, font=F(56, "Bold"), fill=INK, anchor="lm")
        d.text((W - 290, y), "샀음", font=F(46, "SemiBold"), fill=ACCENT, anchor="mm")
        mark(d, W - 150, y, False, 1.0)


def s_hook(t):
    img, d = canvas()
    text(d, (W / 2, 300), "자취하면 꼭 사는데", 88)
    text(d, (W / 2, 420), "결국 안 쓰는 것 3가지", 88, fill=ACCENT)
    checklist(d, 680)
    text(d, (W / 2, 1230), "셋 다 샀음 ㅋㅋ", 58, fill=SUB, weight="SemiBold")
    return img


def s_gym(t):
    img, d = canvas()
    chip(d, W / 2, 250, "1. 홈트 기구")
    text(d, (W / 2, 400), "3일 쓰고", 84)
    text(d, (W / 2, 510), "옷걸이 됨", 84, fill=ACCENT, alpha=appear(t, 0.12))
    # 실내자전거 + 걸린 옷
    cx, by = W / 2, 1180
    d.rounded_rectangle((cx - 260, by, cx + 260, by + 30), 15, fill=METAL)          # 바닥 받침
    d.line((cx - 60, by, cx + 40, by - 380), fill=METAL, width=34)                   # 몸통
    d.line((cx + 40, by - 380, cx + 170, by - 420), fill=METAL, width=24)            # 핸들 대
    d.rounded_rectangle((cx + 130, by - 450, cx + 230, by - 410), 18, fill=INK)      # 핸들
    d.rounded_rectangle((cx - 150, by - 300, cx - 10, by - 260), 18, fill=INK)       # 안장
    d.ellipse((cx - 110, by - 160, cx + 30, by - 20), outline=METAL, width=18)        # 휠
    k = appear(t, 0.3, 0.3)
    if k > 0:   # 핸들에 걸린 티셔츠
        x, y = cx + 180, by - 410
        h = 260 * k
        d.polygon([(x - 90, y), (x + 90, y), (x + 130, y + 60), (x + 90, y + 80), (x + 80, y + h),
                   (x - 80, y + h), (x - 90, y + 80), (x - 130, y + 60)], fill=(150, 180, 210))
    text(d, (W / 2, 1330), "장바구니에 2주 넣어두고 그래도 생각나면 사기", 46, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.6))
    return img


def s_bulk(t):
    img, d = canvas()
    chip(d, W / 2, 250, "2. 대용량 식재료")
    text(d, (W / 2, 400), "싸서 샀는데", 84)
    text(d, (W / 2, 510), "반은 버림", 84, fill=ACCENT, alpha=appear(t, 0.12))
    # 대용량 봉투 vs 실제로 먹은 양
    x0, y0, x1, y1 = 300, 660, 780, 1220
    d.rounded_rectangle((x0, y0, x1, y1), 50, fill=(236, 214, 170))
    d.rounded_rectangle((x0 + 60, y0 + 80, x1 - 60, y0 + 200), 20, fill=(255, 255, 255))
    d.text(((x0 + x1) / 2, y0 + 140), "대용량", font=F(64, "ExtraBold"), fill=INK, anchor="mm")
    k = appear(t, 0.25, 0.4)
    full = y0 + 240
    level = full + (y1 - 30 - full) * 0.5 * k       # 반쯤 먹고 나서 유통기한
    d.rectangle((x0 + 20, level, x1 - 20, y1 - 30), fill=(200, 190, 170))
    if k > 0:
        d.line((x0 - 30, level, x1 + 30, level), fill=ACCENT, width=8)
        d.text((x1 + 50, level), "유통기한", font=F(44, "Bold"), fill=ACCENT, anchor="lm")
    text(d, (W / 2, 1330), "다 먹을 수 있는 만큼만 사기", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_plates(t):
    img, d = canvas()
    chip(d, W / 2, 250, "3. 예쁜 그릇 세트")
    text(d, (W / 2, 400), "6개 샀는데", 84)
    text(d, (W / 2, 510), "쓰는 건 1개", 84, fill=ACCENT, alpha=appear(t, 0.12))
    k = appear(t, 0.25, 0.3)
    for i in range(6):     # 쌓인 접시 5개 + 꺼내 쓰는 1개
        r, c = divmod(i, 3)
        cx, cy = 270 + c * 270, 780 + r * 230
        used = i == 0
        fill = (255, 255, 255) if used else (226, 222, 214)
        d.ellipse((cx - 110, cy - 70, cx + 110, cy + 70), fill=fill, outline=(200, 195, 188), width=4)
        d.ellipse((cx - 60, cy - 36, cx + 60, cy + 36), outline=(210, 205, 198), width=4)
        if used and k > 0:
            d.ellipse((cx - 125, cy - 85, cx + 125, cy + 85), outline=OK, width=int(10 * k) or 1)
    if k > 0:
        d.text((270, 895), "이것만 씀", font=F(46, "Bold"), fill=OK, anchor="mm")
    text(d, (W / 2, 1330), "세트 말고 자주 쓸 것 하나만", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_end(t):
    img, d = canvas()
    text(d, (W / 2, 330), "님은 뭐 샀어요?", 92)
    text(d, (W / 2, 450), "4번째 댓글로 알려주세요", 70, fill=ACCENT, weight="SemiBold", alpha=appear(t, 0.1))
    checklist(d, 700)
    d.rounded_rectangle((90, 1140, W - 90, 1280), 34, outline=(200, 195, 188), width=4)
    d.text((150, 1210), "4", font=F(52, "ExtraBold"), fill=SUB, anchor="mm")
    d.text((210, 1210), "?", font=F(56, "Bold"), fill=SUB, anchor="lm")
    text(d, (W / 2, 1390), "사기 전에 저장해두고 보기", 54, fill=SUB, weight="SemiBold", alpha=appear(t, 0.4))
    return img


SCENES = [
    (3.4, s_hook),
    (3.0, s_gym),
    (3.0, s_bulk),
    (3.0, s_plates),
    (3.2, s_end),
]

if __name__ == "__main__":
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_unused.mp4"
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
                    str(HERE / "homelivingclub_unused_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
