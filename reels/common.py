"""
정보형 릴스 공통 도구 (ratio/render.py 디자인 재사용)
- 첫 프레임부터 결론이 보이게 (꽃꽂이 비율 릴스 평균 시청 0:01 반영)
- 중요한 요소는 y < 1500 (인스타 하단 캡션 영역 피하기)
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent / "ratio"))
from render import (W, H, FPS, BG, INK, SUB, LINE, ACCENT, OK, F, ease, appear, text, chip,  # noqa: E402,F401
                    mark, photo_card, ruler, IMGS)

FLOOR = (210, 206, 200)
SOFT = (232, 228, 220)


def canvas(bg=BG):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def floor(d, y, x0=80, x1=W - 80):
    d.line((x0, y + 2, x1, y + 2), fill=FLOOR, width=3)


def end_card(t, title, lines, cta="저장해두고 필요할 때 보기"):
    img, d = canvas(INK)
    a = appear(t, 0, 0.2)
    d.text((W / 2, 520), title, font=F(60, "SemiBold"), fill=tuple(int(24 + (200 - 24) * a) for _ in range(3)), anchor="mm")
    for i, s in enumerate(lines):
        b = appear(t, 0.1 + i * 0.12, 0.2)
        d.text((W / 2, 720 + i * 150), s, font=F(88, "ExtraBold"), fill=tuple(int(24 + (255 - 24) * b) for _ in range(3)), anchor="mm")
    e = appear(t, 0.5, 0.2)
    d.text((W / 2, 720 + len(lines) * 150 + 120), cta, font=F(50, "SemiBold"),
           fill=(int(24 + (226 - 24) * e), int(24 + (86 - 24) * e), int(24 + (60 - 24) * e)), anchor="mm")
    return img


def render(scenes, out, frames_dir):
    """scenes: [(초, fn(t)->Image)] → mp4 + _frames/all.jpg(장면별 마지막 프레임) + first_frame.jpg"""
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames_dir.mkdir(exist_ok=True)
    total, stills = 0, []
    for dur, fn in scenes:
        n = int(round(dur * FPS))
        for i in range(n):
            frame = fn(i / max(n - 1, 1)).convert("RGB")
            if total == 0 and i == 0:
                frame.save(frames_dir / "first_frame.jpg", quality=90)
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
    sheet.save(frames_dir / "all.jpg", quality=88)
    print(f"✅ {Path(out).name}  {total / FPS:.1f}초")
