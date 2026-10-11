"""
홈리빙클럽 릴스 — 정보형 "꽃 꽂았는데 어색한 이유 = 비율 (꽃 = 화병 × 1.5)"
디자인: 미색 배경 + Pretendard + 얇은 선 인포그래픽. 이모지·메모장 템플릿 없음.
실제 상품 사진은 실측 설명 장면(화병 14.5cm, 튤립 34cm)에만 사용.
"""
import math
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
FONTS = HERE.parent / "fonts"
IMGS = HERE.parents[1] / "products/images"
W, H, FPS = 1080, 1920, 30

BG = (247, 245, 240)
INK = (24, 24, 24)
SUB = (120, 116, 110)
LINE = (60, 60, 60)
ACCENT = (226, 86, 60)      # 강조(오답·숫자)
OK = (46, 140, 92)          # 정답
PETAL = (238, 140, 165)
LEAF = (104, 160, 96)


def F(size, weight="Bold"):
    return ImageFont.truetype(str(FONTS / f"Pretendard-{weight}.otf"), size)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def appear(t, start, dur=0.18):
    return ease((t - start) / dur)


def text(d, xy, s, size, fill=INK, weight="Bold", anchor="mm", alpha=1.0, spacing=14):
    if alpha <= 0:
        return
    col = tuple(int(BG[i] + (fill[i] - BG[i]) * alpha) for i in range(3))
    d.multiline_text(xy, s, font=F(size, weight), fill=col, anchor=anchor, align="center", spacing=spacing)


def chip(d, cx, y, label):
    f = F(40, "SemiBold")
    w = d.textlength(label, font=f)
    d.rounded_rectangle((cx - w / 2 - 28, y - 30, cx + w / 2 + 28, y + 30), 30, outline=INK, width=3)
    d.text((cx, y), label, font=f, fill=INK, anchor="mm")


# ---------------------------------------------------------------- 라인 드로잉

def vase(d, cx, bottom, h, width=5):
    """웨이브 미니 화병 실루엣 (높이:폭 = 14.5:12)"""
    w = h * 12 / 14.5
    neck_w, neck_h = w * 0.36, h * 0.16
    body_top = bottom - h + neck_h
    d.rounded_rectangle((cx - w / 2, body_top, cx + w / 2, bottom), radius=w * 0.32, outline=LINE, width=width)
    d.rectangle((cx - neck_w / 2, bottom - h, cx + neck_w / 2, body_top + w * 0.08), fill=BG)
    d.line((cx - neck_w / 2, bottom - h, cx - neck_w / 2, body_top + 6), fill=LINE, width=width)
    d.line((cx + neck_w / 2, bottom - h, cx + neck_w / 2, body_top + 6), fill=LINE, width=width)
    d.line((cx - neck_w / 2 - 6, bottom - h, cx + neck_w / 2 + 6, bottom - h), fill=LINE, width=width)
    for i in range(3):                               # 웨이브 무늬 힌트
        y = body_top + (bottom - body_top) * (0.35 + i * 0.2)
        pts = [(cx - w * 0.38 + k * w * 0.095, y + (8 if k % 2 else -8)) for k in range(9)]
        d.line(pts, fill=(170, 166, 160), width=2)
    return bottom - h


def tulip(d, base, top, bend=0.0, scale=1.0):
    """base(x,y)에서 top 높이까지 줄기 + 꽃. bend>0 이면 줄기가 옆으로 휘며 꽃 높이가 낮아짐."""
    bx, by = base
    tx, ty = top
    mx = (bx + tx) / 2 + bend * 160
    my = (by + ty) / 2
    pts = []
    for i in range(21):
        u = i / 20
        x = (1 - u) ** 2 * bx + 2 * (1 - u) * u * mx + u * u * tx
        y = (1 - u) ** 2 * by + 2 * (1 - u) * u * my + u * u * ty
        pts.append((x, y))
    d.line(pts, fill=LEAF, width=int(6 * scale), joint="curve")
    lx, ly = pts[12]
    d.polygon([(lx, ly), (lx - 50 * scale, ly - 80 * scale), (lx - 8 * scale, ly - 30 * scale)], fill=LEAF)
    r = 34 * scale
    d.chord((tx - r, ty - r * 1.2, tx + r, ty + r * 0.9), 0, 180, fill=PETAL)
    d.polygon([(tx - r, ty - r * 0.15), (tx - r * 0.55, ty - r * 1.35), (tx - r * 0.1, ty - r * 0.45),
               (tx, ty - r * 1.45), (tx + r * 0.1, ty - r * 0.45), (tx + r * 0.55, ty - r * 1.35),
               (tx + r, ty - r * 0.15)], fill=PETAL)


def ruler(d, x, y_bottom, y_top, label, color=INK, side="right", k=1.0):
    """세로 치수선. k(0~1) 로 위로 자라나는 애니메이션"""
    if k <= 0:
        return
    yt = y_bottom - (y_bottom - y_top) * k
    d.line((x, y_bottom, x, yt), fill=color, width=4)
    for y in (y_bottom, yt):
        d.line((x - 16, y, x + 16, y), fill=color, width=4)
    if k >= 1:
        ax = x + 30 if side == "right" else x - 30
        d.text((ax, (y_bottom + y_top) / 2), label, font=F(48), fill=color,
               anchor="lm" if side == "right" else "rm")


def mark(d, cx, cy, good, k):
    if k <= 0:
        return
    s = 38 * ease(k)
    if good:
        d.line([(cx - s, cy), (cx - s * 0.2, cy + s * 0.8), (cx + s * 1.1, cy - s * 0.9)], fill=OK, width=12, joint="curve")
    else:
        d.line((cx - s, cy - s, cx + s, cy + s), fill=ACCENT, width=12)
        d.line((cx - s, cy + s, cx + s, cy - s), fill=ACCENT, width=12)


# ---------------------------------------------------------------- 장면

def s_hook(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (W / 2, 330), "꽃 꽂았는데", 92, alpha=appear(t, 0))
    text(d, (W / 2, 450), "어색하다면", 92, alpha=appear(t, 0.05))
    text(d, (W / 2, 580), "비율 때문이에요", 92, fill=ACCENT, alpha=appear(t, 0.12))
    bottom, h = 1330, 230
    for i, (cx, ratio, good) in enumerate([(230, 1.15, False), (540, 2.9, False), (850, 1.5, True)]):
        k = appear(t, 0.2 + i * 0.12, 0.25)
        if k <= 0:
            continue
        top = vase(d, cx, bottom, h)
        flower_y = bottom - h * ratio * (0.6 + 0.4 * k)
        tulip(d, (cx, top + 40), (cx, flower_y), scale=0.8)
        mark(d, cx, 1440, good, appear(t, 0.55 + i * 0.1))
    d.line((80, bottom + 2, W - 80, bottom + 2), fill=(210, 206, 200), width=3)
    return img


def s_rule(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chip(d, W / 2, 260, "꽃꽂이 기본 비율")
    text(d, (W / 2, 420), "꽃 높이 = 화병 × 1.5", 96, alpha=appear(t, 0.05))
    bottom, h = 1480, 380
    cx = W / 2 - 60
    top = vase(d, cx, bottom, h, width=6)
    k = appear(t, 0.2, 0.35)
    tulip(d, (cx, top + 60), (cx, bottom - h * (1 + 0.5 * k)), scale=1.1)
    ruler(d, cx + h * 0.5 + 60, bottom, bottom - h, "1", color=SUB, k=appear(t, 0.15, 0.2))
    ruler(d, cx + h * 0.5 + 170, bottom, bottom - h * 1.5, "1.5", color=OK, k=appear(t, 0.45, 0.3))
    d.line((120, bottom + 2, W - 120, bottom + 2), fill=(210, 206, 200), width=3)
    return img


def photo_card(img, photo, box, r=36):
    x0, y0, x1, y1 = box
    ph = photo.copy()
    ph.thumbnail((x1 - x0, y1 - y0), Image.LANCZOS)
    card = Image.new("RGB", (x1 - x0, y1 - y0), (255, 255, 255))
    card.paste(ph, ((card.width - ph.width) // 2, (card.height - ph.height) // 2))
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *card.size), r, fill=255)
    img.paste(card, (x0, y0), mask)


VASE_PHOTO = Image.open(IMGS / "minivase/_blocks/b10.jpg").convert("RGB").crop((150, 60, 710, 760))
STEM_PHOTO = Image.open(IMGS / "tulip/src_d_02_1.jpg").convert("RGB").crop((40, 170, 300, 650))


def s_vase(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (W / 2, 330), "예를 들어 14.5cm 화병이면", 64, fill=SUB, weight="SemiBold", alpha=appear(t, 0))
    photo_card(img, VASE_PHOTO, (130, 450, 780, 1150))
    ruler(d, 830, 1100, 520, "14.5cm", color=INK, k=appear(t, 0.15, 0.25))
    text(d, (W / 2, 1320), "14.5 × 1.5 = 약 22cm", 88, fill=OK, alpha=appear(t, 0.45))
    text(d, (W / 2, 1430), "꽃은 22cm 정도가 딱 좋아요", 54, fill=INK, weight="SemiBold", alpha=appear(t, 0.6))
    return img


def s_stem(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (W / 2, 330), "그런데 튤립 조화는 보통", 64, fill=SUB, weight="SemiBold", alpha=appear(t, 0))
    photo_card(img, STEM_PHOTO, (290, 430, 790, 1250))
    ruler(d, 840, 1220, 460, "약 34cm", color=ACCENT, k=appear(t, 0.15, 0.25))
    text(d, (W / 2, 1400), "그대로 꽂으면 너무 길어요", 76, fill=ACCENT, alpha=appear(t, 0.45))
    return img


def s_bend(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (W / 2, 330), "줄기 속에 철사가 있어서", 64, fill=SUB, weight="SemiBold", alpha=appear(t, 0))
    text(d, (W / 2, 440), "구부려서 22cm로 맞추면 끝", 76, fill=INK, alpha=appear(t, 0.05))
    bottom, h = 1480, 380
    cx = W / 2 - 80
    top = vase(d, cx, bottom, h, width=6)
    k = appear(t, 0.2, 0.5)
    long_top = bottom - h * 34 / 14.5
    good_top = bottom - h * 1.5
    fy = long_top + (good_top - long_top) * k
    fx = cx + 150 * k
    tulip(d, (cx, top + 60), (fx, fy), bend=0.9 * k, scale=1.1)
    ruler(d, cx + h * 0.5 + 240, bottom, fy, "", color=OK if k >= 1 else SUB, k=1)
    if k >= 1:
        d.text((cx + h * 0.5 + 270, (bottom + fy) / 2), "22cm", font=F(48), fill=OK, anchor="lm")
    d.line((120, bottom + 2, W - 120, bottom + 2), fill=(210, 206, 200), width=3)
    return img


def s_end(t):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    a = appear(t, 0, 0.25)
    col = tuple(int(24 + (255 - 24) * a) for _ in range(3))
    d.text((W / 2, 760), "화병 높이 × 1.5", font=F(120, "ExtraBold"), fill=col, anchor="mm")
    d.text((W / 2, 900), "이것만 기억하면 꽃꽂이 반은 끝", font=F(56, "SemiBold"), fill=tuple(int(24 + 200 * a) for _ in range(3)), anchor="mm")
    b = appear(t, 0.35, 0.25)
    d.text((W / 2, 1120), "저장해두고 꽃 꽂을 때 보기", font=F(50, "SemiBold"),
           fill=(int(24 + (226 - 24) * b), int(24 + (86 - 24) * b), int(24 + (60 - 24) * b)), anchor="mm")
    return img


SCENES = [(2.6, s_hook), (3.0, s_rule), (3.0, s_vase), (2.8, s_stem), (3.2, s_bend), (2.4, s_end)]


def main():
    out = HERE / "homelivingclub_ratio.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    (HERE / "_frames").mkdir(exist_ok=True)
    total, stills = 0, []
    for dur, fn in SCENES:
        n = int(round(dur * FPS))
        for i in range(n):
            frame = fn(i / max(n - 1, 1)).convert("RGB")
            if i == n - 1:
                stills.append(frame.resize((W // 4, H // 4)))
            proc.stdin.write(frame.tobytes())
        total += n
    proc.stdin.close()
    proc.wait()
    w, h = stills[0].size
    sheet = Image.new("RGB", (w * len(stills) + 8 * (len(stills) - 1), h), "black")
    for i, s in enumerate(stills):
        sheet.paste(s, (i * (w + 8), 0))
    sheet.save(HERE / "_frames/all.jpg", quality=88)
    print(f"✅ {out.name}  {total / FPS:.1f}초")


if __name__ == "__main__":
    main()
