# 소스 사진 한눈에 보기 (번호 + 크기 표시)
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding="utf-8")
src = Path(__file__).parent / "src"
files = sorted(src.glob("s*.*"))
TW, TH = 180, 360
cols = 10
sheet = Image.new("RGB", (cols * TW, ((len(files) + cols - 1) // cols) * (TH + 20)), "white")
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f)
    size = im.size
    im = im.convert("RGB")
    im.thumbnail((TW - 6, TH - 6))
    x, y = (i % cols) * TW, (i // cols) * (TH + 20)
    sheet.paste(im, (x + 3, y + 3))
    d.text((x + 4, y + TH + 2), f"{f.stem} {size[0]}x{size[1]}", fill="red")
sheet.save(Path(__file__).parent / "_contact.jpg", quality=85)
