"""
홈리빙클럽 릴스 — 계란후라이, 프라이팬 꺼내지 마세요 (상품 릴스, 순서 애니메이션 한 장면)
- 상품 상세 안내 기준: 계란 넣고 노른자에 구멍 → 물 1작은술 → 뚜껑 덮고 600W 50초 (700W 이하에서 사용)
- 시험: 상품명과 "저희 스토어 상품"을 0초부터 화면에 표시 (끝 화면 6초 표기와 프로필 활동 비교)
- 사진은 오너클랜 실물 사진, 그림은 직접 그림 / 제목은 격자 잘림 아래(y=300)
- BGM: piano2
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shampoo"))
from common import (W, INK, SUB, ACCENT, F, appear, text, canvas, render)  # noqa: E402
import bgm  # noqa: E402

TOTAL = 7.5
# Cmaj7 → Am7 → Fmaj7 → G7
CHORDS = [[36, 40, 43, 47], [45, 48, 52, 55], [41, 45, 48, 52], [43, 47, 50, 53]]
PHOTO = Image.open(HERE.parent.parent / "products/images/eggfry/main.jpg").convert("RGB").resize((104, 104))
GRAY = (170, 166, 158)
CX, CY, R = 540, 860, 225
STEPS = [
    ("1", "계란 넣고 노른자에 구멍 내기", 0.0, 1.2),
    ("2", "물 1작은술 넣기", 1.2, 2.0),
    ("3", "뚜껑 덮고 600W 50초", 2.0, 5.0),
]


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def draw_pan(d):
    d.line((CX - 150, CY + 150, CX - 240, CY + 240), fill=(30, 30, 32), width=46)
    d.ellipse((CX - 280, CY + 200, CX - 200, CY + 280), fill=(30, 30, 32))
    d.ellipse((CX - 260, CY + 220, CX - 220, CY + 260), fill=(247, 245, 240))
    d.ellipse((CX - R, CY - R, CX + R, CY + R), fill=(30, 30, 32))
    d.ellipse((CX - R + 22, CY - R + 22, CX + R - 22, CY + R - 22), fill=(56, 56, 60))


def draw_egg(d, cook, holes):
    white = mix((222, 220, 200), (255, 252, 240), cook)
    for x, y, r in [(0, 0, 150), (-52, 28, 118), (58, -34, 112), (34, 62, 104)]:
        d.ellipse((CX + x - r, CY + y - r, CX + x + r, CY + y + r), fill=white)
    r = 66
    d.ellipse((CX - r, CY - r, CX + r, CY + r), fill=mix((244, 132, 34), (250, 204, 62), cook))
    if holes > 0:
        for x, y in [(-24, -16), (20, -24), (2, 22)]:
            s = 8 * holes
            d.ellipse((CX + x - s, CY + y - s, CX + x + s, CY + y + s), fill=(170, 90, 20))


def draw_lid(d, x):
    d.ellipse((x - R - 12, CY - R - 12, x + R + 12, CY + R + 12), fill=(38, 38, 42))
    d.ellipse((x - 72, CY - 72, x + 72, CY + 72), fill=(24, 24, 26))
    d.ellipse((x - 40, CY - 40, x + 12, CY + 12), fill=(52, 52, 58))


def s_all(t):
    T = t * TOTAL
    img, d = canvas()
    text(d, (W / 2, 300), "계란후라이 이제", 62)
    text(d, (W / 2, 405), "프라이팬 꺼내지 마세요", 92, fill=ACCENT, weight="ExtraBold")
    # 상품 표기: 0초부터 끝까지
    d.rounded_rectangle((170, 480, 910, 604), 28, fill=(255, 255, 255), outline=(220, 216, 208), width=3)
    img.paste(PHOTO, (182, 490))
    d.text((310, 520), "저희 스토어 상품", font=F(38, "ExtraBold"), fill=ACCENT, anchor="lm")
    d.text((310, 568), "전자레인지 계란후라이 메이커", font=F(36, "SemiBold"), fill=INK, anchor="lm")

    draw_pan(d)
    draw_egg(d, appear(T, 2.6, 2.2), appear(T, 0.5, 0.3))
    # 물 1작은술: 한 방울 떨어짐
    if 1.2 <= T < 2.0:
        y = CY - 330 + 330 * appear(T, 1.25, 0.55)
        d.polygon([(CX + 110, y - 42), (CX + 88, y), (CX + 132, y)], fill=(110, 180, 235))
        d.ellipse((CX + 88, y - 22, CX + 132, y + 22), fill=(110, 180, 235))
    # 뚜껑: 오른쪽에서 들어왔다가 다 되면 빠짐
    on, off = appear(T, 2.0, 0.45), appear(T, 4.8, 0.45)
    if on > 0 and off < 1:
        lx = CX + (1 - on) * 800 + off * 800
        draw_lid(d, lx)
        k = appear(T, 2.45, 0.1) * (1 - appear(T, 4.8, 0.1))
        if k > 0:
            sec = max(0, round(50 * (1 - (T - 2.5) / 2.2))) if T >= 2.5 else 50
            d.rounded_rectangle((CX - 170, CY - 70, CX + 170, CY + 70), 22, fill=(20, 22, 26))
            d.text((CX, CY), f"0:{sec:02d}", font=F(96, "ExtraBold"), fill=(120, 230, 140), anchor="mm")
    if T >= 5.0:
        a = appear(T, 5.0, 0.3)
        d.text((CX + 275, CY - 150), "완성", font=F(58, "ExtraBold"), fill=mix((247, 245, 240), ACCENT, a), anchor="mm")

    for i, (n, s, start, end) in enumerate(STEPS):
        y = 1190 + i * 92
        active = start <= T < end
        d.ellipse((110, y - 36, 182, y + 36), fill=ACCENT if active else INK)
        d.text((146, y), n, font=F(44, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
        d.text((210, y), s, font=F(52 if active else 48, "ExtraBold" if active else "SemiBold"),
               fill=INK if active or T >= end else SUB, anchor="lm")
    text(d, (W / 2, 1465), "시간은 전자레인지 출력과 계란 크기에 따라 달라요", 34, fill=SUB, weight="SemiBold")
    if T < 5.4:
        text(d, (W / 2, 1570), "기름도 가스불도 없이", 56, fill=SUB, weight="SemiBold")
    else:
        a = appear(T, 5.4, 0.3)
        text(d, (W / 2, 1570), "1 프라이팬 / 2 전자레인지, 댓글로", 58, fill=ACCENT, weight="ExtraBold", alpha=a)
        text(d, (W / 2, 1670), "저장해두고 바쁜 아침에 보기", 44, fill=SUB, weight="SemiBold", alpha=a)
    return img


SCENES = [(TOTAL, s_all)]

if __name__ == "__main__":
    if "--preview" in sys.argv:
        ts = [0, 0.9, 1.6, 2.3, 3.6, 5.2, 7.4]
        sheet = Image.new("RGB", (len(ts) * 270, 480), (0, 0, 0))
        for i, T in enumerate(ts):
            sheet.paste(s_all(T / TOTAL).resize((270, 480)), (i * 270, 0))
        sheet.save(HERE / "_preview.jpg", quality=85)
        s_all(0).save(HERE / "_first.jpg", quality=88)
        sys.exit()
    silent = HERE / "_silent.mp4"
    out = HERE / "homelivingclub_nofrypan.mp4"
    render(SCENES, silent, HERE / "_frames")
    wav = HERE / "_bgm.wav"
    bgm.make(wav, TOTAL, CHORDS, "piano2")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-loglevel", "error",
                    "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-b:v", "4M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-movflags", "+faststart",
                    str(HERE / "homelivingclub_nofrypan_ig.mp4")], check=True)
    silent.unlink()
    print(f"✅ BGM 포함 → {out.name}")
