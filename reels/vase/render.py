"""
홈리빙클럽 릴스 — 웨이브 미니 화병 (v5 와 같은 구조: 훅 → 리스트 개그 2개 → 리빌 → 저장 CTA → 판매 안내)
사진은 products/images/minivase/_blocks (상세페이지에서 잘라낸 실제 상품 사진)만 사용.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "v5"))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter
from render import (W, H, FPS, CREAM, INK, RED, GREEN, font, ease, pop, ken_burns,
                    text_center, rounded_photo, memo_base, bookmark)

SAGE = (122, 150, 118)
BLOCKS = HERE.parents[1] / "products/images/minivase/_blocks"
interior = Image.open(BLOCKS / "b00.jpg").convert("RGB")
flowers = Image.open(BLOCKS / "b05.jpg").convert("RGB")
white_fl = Image.open(BLOCKS / "b06.jpg").convert("RGB")
group = Image.open(BLOCKS / "b08.jpg").convert("RGB")


def scene_hook(t):
    # 가로 사진이라 세로 화면을 꽉 채우면 흐려짐 → 흐린 배경 + 사진 카드
    bg = ken_burns(interior, 0, W, H).filter(ImageFilter.GaussianBlur(30))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    photo = ken_burns(interior, t, 960, 900, zoom=(1.0, 1.1), pan=(0.45, 0.55, 0.5, 0.5))
    rounded_photo(bg, photo, (W - 960) // 2, 820)
    d = ImageDraw.Draw(bg)
    a = pop(t * 2.6, 0.3)
    text_center(d, 330, "휑한 자취방", int(84 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    text_center(d, 470, "분위기 바꾸는\n제일 쉬운 방법", int(110 * (0.85 + 0.15 * a)), fill=(255, 226, 150),
                stroke=4, stroke_fill=(50, 40, 30), spacing=24)
    return bg


def scene_fail(t, num, title, result):
    img, d = memo_base()
    text_center(d, 250, "자취방 분위기 바꾸기", 56, fill=(150, 130, 115))
    f = font(110)
    label = f"{num}. {title}"
    bw = d.textlength(label, font=f)
    x = (W - bw) / 2
    d.text((x, 620), label, font=f, fill=INK)
    k = min(1.0, max(0.0, (t - 0.25) / 0.2))
    if k > 0:
        d.line((x - 10, 690, x - 10 + (bw + 20) * k, 690), fill=RED, width=14)
    if t > 0.45:
        a = pop(t - 0.45, 0.15)
        text_center(d, 880, result, int(66 * (0.8 + 0.2 * a)), fill=RED)
    return img


def scene_win(t):
    img, d = memo_base()
    f = font(88)
    label = "3. 화병에 조화 꽂기"
    bw = d.textlength(label, font=f)
    x = (W - bw - 120) / 2
    d.text((x, 250), label, font=f, fill=INK)
    k = min(1.0, t / 0.18)
    cx, cy = x + bw + 25, 300
    pts = [(cx, cy), (cx + 30, cy + 35), (cx + 90, cy - 45)]
    if k > 0:
        d.line(pts[:2] if k < 0.4 else pts, fill=GREEN, width=16, joint="curve")
    a = ease(min(1.0, t / 0.25))
    pw, ph = 940, 1000
    photo = ken_burns(flowers if t < 0.5 else white_fl, (t * 2) % 1, pw, ph, zoom=(1.0, 1.06))
    y = int(470 + (1 - a) * 200)
    rounded_photo(img, photo, (W - pw) // 2, y)
    return img


def scene_cta(t):
    img = Image.new("RGB", (W, H), SAGE)
    d = ImageDraw.Draw(img)
    a = pop(t * 2.4, 0.25)
    bob = int(12 * (1 - abs((t * 4) % 2 - 1)))
    bookmark(d, W / 2, 420 - bob, 200 * (0.7 + 0.3 * a), 260 * (0.7 + 0.3 * a), (255, 255, 255))
    text_center(d, 800, "저장해두고", int(120 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    text_center(d, 960, "방 꾸밀 때 보기", int(96 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    text_center(d, 1150, "(생화 3일 만에 보내본 사람만)", 50, fill=(232, 240, 228), bold=False)
    return img


def scene_end(t):
    img = Image.new("RGB", (W, H), CREAM)
    blur = ken_burns(group, 0, W, H).filter(ImageFilter.GaussianBlur(40))
    img = Image.blend(img, blur, 0.35)
    photo = ken_burns(group, t, 940, 900, zoom=(1.08, 1.0))
    rounded_photo(img, photo, (W - 940) // 2, 220)
    d = ImageDraw.Draw(img)
    text_center(d, 1170, "화이트 · 핑크 · 옐로우 · 그레이", 58, fill=INK)
    d.rounded_rectangle((110, 1270, W - 110, 1410), 70, fill=(255, 255, 255))
    text_center(d, 1298, "물 대신 조화·드라이플라워용", 52, fill=SAGE)
    text_center(d, 1450, "높이 14.5cm · 프로필 링크에서 확인", 48, fill=INK, bold=False)
    return img


SCENES = [
    (2.6, scene_hook),
    (2.2, lambda t: scene_fail(t, 1, "가구 바꾸기", "→ 월세 내면 남는 돈 없음")),
    (2.2, lambda t: scene_fail(t, 2, "생화 사기", "→ 3일 만에 시듦")),
    (3.0, scene_win),
    (2.4, scene_cta),
    (3.2, scene_end),
]


def main():
    out = HERE / "homelivingclub_minivase.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    (HERE / "_frames").mkdir(exist_ok=True)
    total, stills = 0, []
    for si, (dur, fn) in enumerate(SCENES):
        n = int(round(dur * FPS))
        for i in range(n):
            frame = fn(i / max(n - 1, 1)).convert("RGB")
            if i == int(n * 0.7):
                stills.append(frame.resize((W // 3, H // 3)))
            proc.stdin.write(frame.tobytes())
        total += n
    proc.stdin.close()
    proc.wait()
    w, h = stills[0].size
    sheet = Image.new("RGB", (w * len(stills) + 10 * (len(stills) - 1), h), "black")
    for i, s in enumerate(stills):
        sheet.paste(s, (i * (w + 10), 0))
    sheet.save(HERE / "_frames/all.jpg", quality=88)
    print(f"✅ {out.name}  {total / FPS:.1f}초, {total}프레임")


if __name__ == "__main__":
    main()
