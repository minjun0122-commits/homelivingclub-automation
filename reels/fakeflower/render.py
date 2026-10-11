"""
홈리빙클럽 릴스 — 정보형 "조화 싸 보이지 않게 두는 법 3가지"
꽃꽂이 비율 릴스 인사이트(평균 시청 0:01, 저장 0) 반영:
  - 첫 프레임부터 결론(3송이 ✓ / 잔뜩 ✕)이 다 보이게 — 페이드인 없음
  - 장면마다 숫자·결론을 큰 글씨로 먼저
그래픽·글꼴은 ratio/render.py 재사용. 실제 상품 사진은 ① 장면 한 곳만.
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "ratio"))
from render import (W, H, FPS, BG, INK, SUB, ACCENT, OK, F, appear, text, chip,
                    vase, tulip, ruler, mark, photo_card, IMGS)

FLOOR = (210, 206, 200)
SET_PHOTO = Image.open(IMGS / "vase_tulip_set/white_pink.jpg").convert("RGB").crop((20, 110, 1000, 890))


def floor(d, y, x0=80, x1=W - 80):
    d.line((x0, y + 2, x1, y + 2), fill=FLOOR, width=3)


def bouquet(d, cx, bottom, h, tops, scale=0.7, spread=1.0):
    """화병 하나에 튤립 여러 송이. tops = 화병 바닥 기준 꽃 높이 비율 리스트"""
    top = vase(d, cx, bottom, h)
    n = len(tops)
    for i, r in enumerate(tops):
        off = (i - (n - 1) / 2) * (h * 0.9 / max(n - 1, 1)) * spread
        tulip(d, (cx + off * 0.15, top + 40), (cx + off, bottom - h * r), scale=scale)


# ---------------------------------------------------------------- 장면

def s_hook(t):
    """첫 프레임에 결론이 이미 다 보임 (멈추게 하는 장면)"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (W / 2, 300), "조화는", 92)
    text(d, (W / 2, 420), "3송이가 10송이보다", 92)
    text(d, (W / 2, 540), "진짜 같아요", 92, fill=ACCENT)
    bottom, h = 1300, 260
    many = [1.9, 2.3, 2.0, 2.4, 2.1, 1.8, 2.25, 1.95, 2.35, 2.05]
    bouquet(d, 290, bottom, h, many, scale=0.62, spread=1.35)
    bouquet(d, 790, bottom, h, [1.35, 1.6, 1.45], scale=0.8)
    floor(d, bottom)
    text(d, (290, 1390), "10송이", 50, fill=SUB, weight="SemiBold")
    text(d, (790, 1390), "3송이", 50, fill=SUB, weight="SemiBold")
    mark(d, 290, 1480, False, 1)
    mark(d, 790, 1480, True, 1)
    return img


def s_tip1(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chip(d, W / 2, 250, "① 한 종류 · 홀수로")
    text(d, (W / 2, 400), "3송이 · 5송이", 104, fill=OK)
    text(d, (W / 2, 520), "색도 한 가지만", 64, fill=INK, weight="SemiBold", alpha=appear(t, 0.1))
    photo_card(img, SET_PHOTO, (110, 640, 970, 1324))
    text(d, (W / 2, 1420), "여러 종류 섞으면 '조화 티'가 나요", 54, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.35))
    return img


def s_tip2(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chip(d, W / 2, 250, "② 높이는")
    text(d, (W / 2, 400), "화병 × 1.5", 120, fill=OK)
    bottom, h = 1480, 380
    cx = W / 2 - 60
    top = vase(d, cx, bottom, h, width=6)
    k = appear(t, 0.1, 0.35)
    tulip(d, (cx, top + 60), (cx, bottom - h * (1 + 0.5 * k)), scale=1.1)
    ruler(d, cx + h * 0.5 + 60, bottom, bottom - h, "1", color=SUB, k=appear(t, 0.05, 0.2))
    ruler(d, cx + h * 0.5 + 170, bottom, bottom - h * 1.5, "1.5", color=OK, k=appear(t, 0.35, 0.3))
    floor(d, bottom, 120, W - 120)
    return img


def s_tip3(t):
    """높이가 똑같으면 ✕ → 조금씩 다르게 ✓ (철사 줄기 구부리기)"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chip(d, W / 2, 250, "③ 높이를 조금씩 다르게")
    text(d, (W / 2, 400), "똑같으면 가짜 같아요", 84, fill=ACCENT)
    bottom, h = 1340, 300
    k = appear(t, 0.25, 0.4)
    same = [1.5, 1.5, 1.5]
    good = [1.3, 1.6, 1.42]
    tops = [s + (g - s) * k for s, g in zip(same, good)]
    bouquet(d, W / 2, bottom, h, tops, scale=0.95, spread=1.15)
    floor(d, bottom, 160, W - 160)
    mark(d, W / 2, 1450, k >= 1, 1)
    text(d, (W / 2, 1560), "철사 줄기라 살짝 구부려서 맞추면 돼요", 50, fill=SUB, weight="SemiBold",
         alpha=appear(t, 0.6))
    return img


def s_dust(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chip(d, W / 2, 250, "+ 하나 더")
    text(d, (W / 2, 420), "먼지 쌓이면\n바로 싸 보여요", 92, spacing=24)
    text(d, (W / 2, 640), "드라이기 찬바람으로", 76, fill=OK, alpha=appear(t, 0.15))
    text(d, (W / 2, 740), "한 달에 한 번", 76, fill=OK, alpha=appear(t, 0.15))
    bottom, h = 1500, 300
    bouquet(d, W / 2 - 40, bottom, h, [1.3, 1.6, 1.42], scale=0.95, spread=1.15)
    # 바람 선
    k = appear(t, 0.3, 0.5)
    for i, y in enumerate((1000, 1070, 1140)):
        x1 = W - 90
        x0 = x1 - 220 * k
        if k > 0:
            d.line((x0, y + i * 6, x1, y), fill=SUB, width=5)
    floor(d, bottom, 160, W - 160)
    return img


def s_end(t):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    a = appear(t, 0, 0.2)

    def c(v):
        return tuple(int(24 + (v - 24) * a) for _ in range(3))
    d.text((W / 2, 560), "조화 덜 싸 보이게", font=F(64, "SemiBold"), fill=c(200), anchor="mm")
    for i, s in enumerate(["3송이 · 한 가지 색", "화병 × 1.5", "높이는 조금씩 다르게"]):
        b = appear(t, 0.1 + i * 0.12, 0.2)
        col = tuple(int(24 + (255 - 24) * b) for _ in range(3))
        d.text((W / 2, 760 + i * 150), s, font=F(92, "ExtraBold"), fill=col, anchor="mm")
    e = appear(t, 0.5, 0.2)
    d.text((W / 2, 1300), "저장해두고 꽃 꽂을 때 보기", font=F(50, "SemiBold"),
           fill=(int(24 + (226 - 24) * e), int(24 + (86 - 24) * e), int(24 + (60 - 24) * e)), anchor="mm")
    return img


SCENES = [(2.4, s_hook), (3.0, s_tip1), (2.6, s_tip2), (3.2, s_tip3), (3.0, s_dust), (2.8, s_end)]


def main():
    out = HERE / "homelivingclub_fake.mp4"
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
            if total == 0 and i == 0:
                frame.save(HERE / "_frames/first_frame.jpg", quality=90)
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
