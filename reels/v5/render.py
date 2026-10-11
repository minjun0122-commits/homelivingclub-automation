"""
홈리빙클럽 릴스 v5 — 실제 상품 사진 + 줌/팬(켄 번즈) 모션, 무음, 1080x1920, 30fps
PIL 로 매 프레임을 그려 ffmpeg 로 바로 인코딩.

사용 사진 (섞인 타 디자인 사진 제외, 우리 옵션과 일치하는 것만):
  src/s00.jpg  그레이+브라운 안고 있는 사진
  src/s13.jpg  핑크/브라운/그레이 3색 라인업
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
W, H, FPS = 1080, 1920, 30
BOLD = "C:/Windows/Fonts/malgunbd.ttf"
REG = "C:/Windows/Fonts/malgun.ttf"

CREAM = (255, 247, 238)
INK = (45, 35, 30)
PINK = (240, 120, 150)
RED = (225, 60, 60)
GREEN = (40, 170, 90)


def font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, size)


def ease(t):
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- 사진 준비

s00 = Image.open(HERE / "src/s00.jpg").convert("RGB")
s13 = Image.open(HERE / "src/s13.jpg").convert("RGB")
lineup = s13.crop((80, 330, 780, 1075))          # 3색 몸통 (상단 문구 제외)
pink = s13.crop((95, 340, 320, 1070))            # 핑크만


def ken_burns(img, t, box_w, box_h, zoom=(1.0, 1.12), pan=(0.5, 0.5, 0.5, 0.5)):
    """img 를 box 비율로 꽉 채우며 t(0~1)에 따라 줌/이동."""
    z = zoom[0] + (zoom[1] - zoom[0]) * ease(t)
    iw, ih = img.size
    target = box_w / box_h
    if iw / ih > target:
        cw, ch = ih * target, ih
    else:
        cw, ch = iw, iw / target
    cw, ch = cw / z, ch / z
    cx = (pan[0] + (pan[2] - pan[0]) * ease(t)) * iw
    cy = (pan[1] + (pan[3] - pan[1]) * ease(t)) * ih
    x0 = min(max(cx - cw / 2, 0), iw - cw)
    y0 = min(max(cy - ch / 2, 0), ih - ch)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((box_w, box_h), Image.BILINEAR)


def text_center(d, y, text, size, fill=INK, bold=True, spacing=18, stroke=0, stroke_fill=None):
    f = font(size, bold)
    box = d.multiline_textbbox((0, 0), text, font=f, spacing=spacing, align="center", stroke_width=stroke)
    x = (W - (box[2] - box[0])) / 2
    d.multiline_text((x, y), text, font=f, fill=fill, spacing=spacing, align="center",
                     stroke_width=stroke, stroke_fill=stroke_fill)
    return box[3] - box[1]


def rounded_photo(canvas, photo, x, y, r=40):
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *photo.size), r, fill=255)
    canvas.paste(photo, (x, y), mask)


def pop(t, dur=0.25):
    """0→1 로 빠르게 커지는 등장 효과 계수"""
    return min(1.0, t / dur)


# ---------------------------------------------------------------- 장면

def scene_hook(t):
    """0.0–2.6s  훅: 안고 있는 사진 + 큰 제목"""
    bg = ken_burns(s00, t, W, H, zoom=(1.0, 1.15), pan=(0.5, 0.45, 0.5, 0.4))
    shade = Image.new("RGB", (W, H), (0, 0, 0))
    grad = Image.linear_gradient("L").resize((W, H)).transpose(Image.FLIP_TOP_BOTTOM).point(lambda v: int(v * 0.75))
    bg = Image.composite(shade, bg, grad)
    d = ImageDraw.Draw(bg)
    a = pop(t * 2.6, 0.3)
    text_center(d, 330, "자취 3년차가\n요즘 매일 지키는", int(78 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    text_center(d, 560, "루틴 3가지", int(130 * (0.85 + 0.15 * a)), fill=(255, 214, 102),
                stroke=4, stroke_fill=(60, 40, 20))
    return bg


def memo_base():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for y in range(420, 1500, 110):                 # 메모장 줄
        d.line((90, y, W - 90, y), fill=(236, 222, 205), width=3)
    d.line((150, 300, 150, 1550), fill=(245, 170, 170), width=4)
    return img, d


def scene_fail(t, num, title, result):
    """리스트 개그: 제목 → 취소선 → 현실"""
    img, d = memo_base()
    text_center(d, 250, "자취 3년차 루틴", 56, fill=(150, 130, 115))
    f = font(110)
    label = f"{num}. {title}"
    bw = d.textlength(label, font=f)
    x = (W - bw) / 2
    d.text((x, 620), label, font=f, fill=INK)
    k = min(1.0, max(0.0, (t - 0.25) / 0.2))       # 취소선 긋기
    if k > 0:
        d.line((x - 10, 690, x - 10 + (bw + 20) * k, 690), fill=RED, width=14)
    if t > 0.45:
        a = pop(t - 0.45, 0.15)
        text_center(d, 880, result, int(66 * (0.8 + 0.2 * a)), fill=RED)
    return img


def scene_win(t):
    """3번째 루틴 = 바디필로우 + 3색 라인업 리빌"""
    img, d = memo_base()
    f = font(92)
    label = "3. 얘 안고 자기"
    bw = d.textlength(label, font=f)
    x = (W - bw - 120) / 2                           # 체크 표시 자리까지 포함해 가운데 정렬
    d.text((x, 250), label, font=f, fill=INK)
    k = min(1.0, t / 0.18)                           # 체크 표시
    cx, cy = x + bw + 25, 300
    pts = [(cx, cy), (cx + 30, cy + 35), (cx + 90, cy - 45)]
    if k > 0:
        d.line(pts[:2] if k < 0.4 else pts, fill=GREEN, width=16, joint="curve")
    a = ease(min(1.0, t / 0.25))
    pw, ph = 940, 1000                               # 라인업 원본 비율에 맞춰 3색이 다 보이게
    photo = ken_burns(lineup, t, pw, ph, zoom=(1.0, 1.04), pan=(0.5, 0.5, 0.5, 0.5))
    y = int(470 + (1 - a) * 200)
    rounded_photo(img, photo, (W - pw) // 2, y)
    return img


def bookmark(d, cx, top, w, h, color):
    d.polygon([(cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, top + h),
               (cx, top + h - w * 0.45), (cx - w / 2, top + h)], fill=color)


def scene_cta(t):
    """저장 유도 CTA — 크게, 일찍"""
    img = Image.new("RGB", (W, H), PINK)
    d = ImageDraw.Draw(img)
    a = pop(t * 2.4, 0.25)
    bob = int(12 * (1 - abs((t * 4) % 2 - 1)))      # 살짝 통통 튀는 아이콘
    bookmark(d, W / 2, 420 - bob, 200 * (0.7 + 0.3 * a), 260 * (0.7 + 0.3 * a), (255, 255, 255))
    text_center(d, 800, "저장해두고", int(120 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    text_center(d, 960, "나중에 다시 보기", int(96 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    text_center(d, 1150, "(자취템 고를 때 꼭 필요함)", 50, fill=(255, 228, 236), bold=False)
    return img


def scene_end(t):
    """핑크 클로즈업 + 판매중 자막"""
    img = Image.new("RGB", (W, H), CREAM)
    blur = ken_burns(pink, 0, W, H).filter(ImageFilter.GaussianBlur(40))
    img = Image.blend(img, blur, 0.35)
    # 얼굴(상단)이 계속 보이도록 위쪽에 고정한 채 살짝 줌아웃
    photo = ken_burns(pink, t, 620, 1180, zoom=(1.08, 1.0), pan=(0.5, 0.26, 0.5, 0.30))
    rounded_photo(img, photo, (W - 620) // 2, 190)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((170, 1330, W - 170, 1480), 75, fill=(255, 255, 255))
    text_center(d, 1355, "지금은 핑크만 판매중", 70, fill=PINK)
    text_center(d, 1520, "90cm · 프로필 링크에서 확인", 50, fill=INK, bold=False)
    return img


SCENES = [
    (2.6, scene_hook),
    (2.0, lambda t: scene_fail(t, 1, "방 정리하기", "→ 내일의 나한테 넘김")),
    (2.0, lambda t: scene_fail(t, 2, "일찍 자기", "→ 정신 차리면 새벽 3시")),
    (2.8, scene_win),
    (2.4, scene_cta),
    (3.2, scene_end),
]


def main():
    out = HERE / "homelivingclub_v5.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    (HERE / "_frames").mkdir(exist_ok=True)
    total = 0
    for si, (dur, fn) in enumerate(SCENES):
        n = int(round(dur * FPS))
        for i in range(n):
            frame = fn(i / max(n - 1, 1)).convert("RGB")
            if i == n // 2:                          # 장면별 검수용 스틸
                frame.resize((W // 3, H // 3)).save(HERE / "_frames" / f"scene{si + 1}.jpg")
            proc.stdin.write(frame.tobytes())
        total += n
    proc.stdin.close()
    proc.wait()
    print(f"✅ {out.name}  {total / FPS:.1f}초, {total}프레임")


if __name__ == "__main__":
    main()
