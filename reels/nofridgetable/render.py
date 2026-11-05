"""
홈리빙클럽 릴스 — 냉장고에 안 넣어도 되는 식재료 6가지 (저장용 정리표, 한 장면)
- 통째로 둔 것 기준. 자른 것은 냉장 안내
- 처음부터 표 전체가 보이고 이유만 차례로 나타남 (격자 표지에서 읽히도록, 제목은 y=300)
- BGM: marimba
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, INK, SUB, ACCENT, OK, F, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

TOTAL = 7.5
# Gmaj7 → Em7 → Am7 → D7
CHORDS = [[43, 47, 50, 54], [40, 43, 47, 50], [45, 48, 52, 55], [38, 42, 45, 48]]
ROWS = [
    ("감자", "서늘하고 어두운 곳", (205, 170, 120)),
    ("고구마", "찬 곳에 약해요", (170, 90, 110)),
    ("양파", "바람 통하는 곳", (225, 180, 110)),
    ("통마늘", "서늘하고 마른 곳", (240, 235, 220)),
    ("바나나", "껍질이 검게 변해요", (245, 215, 90)),
    ("꿀", "차면 잘 굳어요", (235, 170, 50)),
]
Y0, RH = 500, 165


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 300), "냉장고에 안 넣어도 되는 식재료", 62)
    text(d, (W / 2, 410), "6가지 정리표", 104, fill=ACCENT, weight="ExtraBold")
    for i, (name, why, col) in enumerate(ROWS):
        y = Y0 + i * RH
        k = appear(T, 0.8 + i * 0.75, 0.3)
        d.rounded_rectangle((90, y, W - 90, y + RH - 20), 28, fill=(255, 255, 255),
                            outline=ACCENT if k > 0 else (220, 216, 208), width=5 if k > 0 else 3)
        d.ellipse((120, y + 28, 210, y + 118), fill=col, outline=(170, 150, 120), width=3)
        d.text((240, y + 72), name, font=F(50, "ExtraBold"), fill=INK, anchor="lm")
        if k > 0:
            text(d, (710, y + 72), why, 40, fill=SUB, weight="SemiBold", alpha=k)
    a = appear(T, 5.6, 0.3)
    text(d, (W / 2, 1530), "통째로 둔 것 기준, 자른 건 냉장", 42, fill=SUB, weight="SemiBold")
    text(d, (W / 2, 1610), "저장해두고 장 본 날 보기", 46, fill=ACCENT, weight="ExtraBold", alpha=a)
    return img


SCENES = [(TOTAL, s_all)]

if __name__ == "__main__":
    if "--preview" in sys.argv:
        from PIL import Image
        ts = [0, 2.5, 5.0, 7.4]
        sheet = Image.new("RGB", (len(ts) * 270, 480), (0, 0, 0))
        for i, T in enumerate(ts):
            sheet.paste(s_all(T / TOTAL).resize((270, 480)), (i * 270, 0))
        sheet.save(HERE / "_preview.jpg", quality=85)
        sys.exit()
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_nofridgetable.mp4"
    render(SCENES, silent, HERE / "_frames")
    wav = HERE / "_bgm.wav"
    bgm.make(wav, TOTAL, CHORDS, "marimba")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_nofridgetable_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
