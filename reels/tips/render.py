"""
홈리빙클럽 릴스 — 모음형 정보 콘텐츠 "원룸 분위기 가성비로 바꾸는 법 5가지"
촬영/AI 없이 제작. 일반 팁 3개는 이모지, 우리 상품 2개(화병·바디필로우)만 실제 사진.
영상 안에는 판매 문구를 넣지 않는다 (판매 안내는 캡션/고정 댓글로).
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "v5"))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from render import W, H, FPS, CREAM, INK, font, ease, pop, ken_burns, text_center, rounded_photo, memo_base, bookmark

EMOJI_FONT = "C:/Windows/Fonts/seguiemj.ttf"
ACCENT = (232, 120, 70)
ROOT = HERE.parents[1]
vase = Image.open(ROOT / "products/images/minivase/_blocks/b06.jpg").convert("RGB")
pillow = Image.open(HERE.parent / "v5/src/s13.jpg").convert("RGB").crop((95, 340, 320, 1070))

ITEMS = [
    ("💡", None, "형광등 끄고\n전구색 조명", "스탠드 하나만 켜도 카페 됨"),
    ("🖼", None, "빈 벽에\n패브릭 포스터", "못 없이 마스킹테이프로 OK"),
    ("🌷", vase, "화병에 조화 꽂기", "안 시들고 물 갈 필요 없음"),
    ("🛏", None, "침구 색\n2가지로 통일", "베개·이불 톤만 맞춰도 정돈돼 보임"),
    ("🐱", pillow, "침대 위 대형 쿠션", "기대면 침대가 소파처럼 변신"),
]


def emoji(img, ch, cx, cy, size):
    """컬러 이모지를 (cx, cy) 중심에 그림. Segoe UI Emoji 는 109px 에서 가장 선명 → 그린 뒤 확대."""
    f = ImageFont.truetype(EMOJI_FONT, 109)
    tile = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
    tile = tile.resize((size, size), Image.LANCZOS)
    img.paste(tile, (int(cx - size / 2), int(cy - size / 2)), tile)


def scene_hook(t):
    img, d = memo_base()
    a = pop(t * 2.6, 0.3)
    text_center(d, 330, "원룸 분위기", int(96 * (0.85 + 0.15 * a)), fill=INK)
    text_center(d, 470, "가성비로 바꾸는 법", int(96 * (0.85 + 0.15 * a)), fill=INK)
    text_center(d, 610, "5가지", int(170 * (0.85 + 0.15 * a)), fill=ACCENT)
    text_center(d, 860, "(3번이 제일 효과 큼)", 54, fill=(150, 130, 115), bold=False)
    for i, (e, *_rest) in enumerate(ITEMS):          # 이모지가 하나씩 튀어나옴
        k = min(1.0, max(0.0, (t * 2.6 - 0.3 - i * 0.18) / 0.25))
        if k > 0:
            emoji(img, e, 180 + i * 180, 1120 - int(40 * (1 - k)), int(130 * (0.5 + 0.5 * ease(k))))
    return img


def scene_item(t, idx):
    e, photo, title, tip = ITEMS[idx]
    img, d = memo_base()
    slide = int((1 - ease(min(1.0, t / 0.15))) * W)  # 오른쪽에서 밀려 들어옴
    card = Image.new("RGB", (W, H), CREAM)
    cd = ImageDraw.Draw(card)
    cd.ellipse((W / 2 - 70, 230, W / 2 + 70, 370), fill=ACCENT)
    text_center(cd, 252, str(idx + 1), 88, fill=(255, 255, 255))
    if photo is not None:
        pw = 640 if photo is vase else 440              # 바디필로우는 세로로 길어서 좁은 카드로 얼굴까지 보이게
        ph = ken_burns(photo, t, pw, 760, zoom=(1.0, 1.06),
                       pan=(0.5, 0.35, 0.5, 0.4) if photo is vase else (0.5, 0.27, 0.5, 0.3))
        rounded_photo(card, ph, (W - pw) // 2, 420)
        ty = 1220
    else:
        emoji(card, e, W / 2, 700, 420 + int(20 * ease(min(1.0, t / 0.3))))
        ty = 1000
    text_center(cd, ty, title, 92, fill=INK, spacing=14)
    th = cd.multiline_textbbox((0, 0), title, font=font(92), spacing=14)[3]
    text_center(cd, ty + th + 40, tip, 54, fill=ACCENT)
    img.paste(card, (slide, 0))
    return img


def scene_cta(t):
    img = Image.new("RGB", (W, H), ACCENT)
    d = ImageDraw.Draw(img)
    a = pop(t * 2.4, 0.25)
    bob = int(12 * (1 - abs((t * 4) % 2 - 1)))
    bookmark(d, W / 2, 330 - bob, 180 * (0.7 + 0.3 * a), 230 * (0.7 + 0.3 * a), (255, 255, 255))
    text_center(d, 650, "저장하고", int(120 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    text_center(d, 800, "방 꾸밀 때 보기", int(96 * (0.85 + 0.15 * a)), fill=(255, 255, 255))
    for i, (e, _p, title, _t) in enumerate(ITEMS):   # 5가지 한눈에 요약
        y = 1020 + i * 90
        emoji(img, e, 250, y + 34, 64)
        d.text((310, y), f"{i + 1}. {title.replace(chr(10), ' ')}", font=font(50), fill=(255, 255, 255))
    return img


SCENES = [(2.6, scene_hook)] + [(2.3, (lambda k: lambda t: scene_item(t, k))(i)) for i in range(5)] + [(2.6, scene_cta)]


def main():
    out = HERE / "homelivingclub_tips5.mp4"
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
            if i == int(n * 0.75):
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
    print(f"✅ {out.name}  {total / FPS:.1f}초, {total}프레임")


if __name__ == "__main__":
    main()
