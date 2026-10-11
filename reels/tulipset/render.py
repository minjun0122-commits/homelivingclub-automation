"""
홈리빙클럽 릴스 — 화병+튤립 세트, 레퍼런스 스타일(검은 박스 + 형광 초록 계단식 자막, 사진 풀스크린)
훅: 생화 vs 조화 비교 / 마지막에 단점도 솔직하게 (레퍼런스의 신뢰 포인트)
주의: 판매자가 써본 척하는 후기 말투는 쓰지 않음 (정보 전달 말투)
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "v5"))
import imageio_ffmpeg
from PIL import Image, ImageDraw
from render import W, H, FPS, font, ease, ken_burns

ROOT = HERE.parents[1] / "products/images"
NEON = (57, 255, 120)
BOX = (10, 10, 10)
IMG = {
    "tulip_pink": Image.open(ROOT / "tulip/extra_pink.jpg").convert("RGB"),
    "tulip_red": Image.open(ROOT / "tulip/extra_red.jpg").convert("RGB"),
    "vase_group": Image.open(ROOT / "minivase/_blocks/b08.jpg").convert("RGB"),
    "vase_flower": Image.open(ROOT / "minivase/_blocks/b06.jpg").convert("RGB"),
    "set": Image.open(ROOT / "vase_tulip_set/white_pink.jpg").convert("RGB"),
    "vase_white": Image.open(ROOT / "minivase/_blocks/b10.jpg").convert("RGB"),
}


def stacked(img, lines, y, t, size=92, color=NEON, delay=0.12):
    """레퍼런스처럼 줄마다 검은 박스 + 형광 글씨, 좌우로 살짝 엇갈리게 쌓고 한 줄씩 튀어나옴"""
    d = ImageDraw.Draw(img)
    f = font(size)
    offsets = [-40, 30, -10, 40]
    for i, line in enumerate(lines):
        k = min(1.0, max(0.0, (t - i * delay) / 0.12))
        if k <= 0:
            continue
        box = d.textbbox((0, 0), line, font=f)
        tw, th = box[2] - box[0], box[3] - box[1]
        cx = W / 2 + offsets[i % len(offsets)]
        pad_x, pad_y = 26, 18
        x0, y0 = cx - tw / 2 - pad_x, y + i * (th + pad_y * 2 + 8)
        scale = 0.85 + 0.15 * ease(k)
        w2, h2 = (tw + pad_x * 2) * scale, (th + pad_y * 2) * scale
        bx, by = cx - w2 / 2, y0 + (th + pad_y * 2 - h2) / 2
        d.rectangle((bx, by, bx + w2, by + h2), fill=BOX)
        fs = font(int(size * scale))
        d.text((cx, by + h2 / 2), line, font=fs, fill=color, anchor="mm")


def photo_scene(key, lines, y=820, zoom=(1.0, 1.12), pan=(0.5, 0.5, 0.5, 0.5), color=NEON, size=92):
    def fn(t):
        img = ken_burns(IMG[key], t, W, H, zoom=zoom, pan=pan)
        stacked(img, lines, y, t * 2.5, size=size, color=color)
        return img
    return fn


def set_scene(t):
    """세트 구성 이미지는 잘리면 튤립 수가 틀려 보이므로 화면에 통째로(contain) 배치"""
    img = Image.new("RGB", (W, H), (255, 255, 255))
    z = 1.0 + 0.05 * ease(t)
    s = int(W * z)
    pic = IMG["set"].resize((s, s), Image.LANCZOS)
    img.paste(pic, ((W - s) // 2, (H - s) // 2 - 120))
    stacked(img, ["화병까지", "세트로 오는", "튤립 3송이"], 1300, t * 2.5)
    return img


SCENES = [
    (2.6, photo_scene("tulip_pink", ["생화 튤립", "일주일이면", "시드는데"], y=760)),
    (2.4, photo_scene("tulip_red", ["이건", "계속 그대로"], y=820, pan=(0.45, 0.5, 0.55, 0.45))),
    (2.6, photo_scene("vase_group", ["화병도", "4가지 색"], y=1250, zoom=(1.0, 1.1))),
    (2.8, set_scene),
    (3.0, photo_scene("vase_white", ["다만..", "화병엔 물 못 담음", "택배 2개로 따로 옴"], y=820,
                      color=(255, 235, 90), size=80)),
]


def main():
    out = HERE / "homelivingclub_tulipset.mp4"
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
            if i == int(n * 0.8):
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
