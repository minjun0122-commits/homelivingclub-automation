# 등록용 정사각 이미지 만들기: python tools/make_square.py <src> <dst> [fit|crop]
#   fit  = 흰 배경 위에 통째로 (기본, 글자·제품이 잘리지 않게)
#   crop = 가운데 기준 정사각으로 잘라냄 (사진이 꽉 차야 할 때)
import sys
from PIL import Image

S = 1000


def square(src, dst, mode="fit"):
    im = Image.open(src).convert("RGB")
    if mode == "crop":
        s = min(im.size)
        x, y = (im.width - s) // 2, (im.height - s) // 2
        out = im.crop((x, y, x + s, y + s)).resize((S, S), Image.LANCZOS)
    else:
        im.thumbnail((S, S), Image.LANCZOS)
        out = Image.new("RGB", (S, S), "white")
        out.paste(im, ((S - im.width) // 2, (S - im.height) // 2))
    out.save(dst, quality=92)


if __name__ == "__main__":
    square(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "fit")
