# 등록된 바디필로우 상품 사진 받기 (대표이미지 + 상세이미지)
import json, re, sys, requests
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[2]
d = json.load(open(root / "output/fetched_13755644295.json", encoding="utf-8"))["originProduct"]
urls = [d["images"]["representativeImage"]["url"]] + re.findall(r'src="([^"]+)"', d["detailContent"])
out = Path(__file__).parent / "src"
out.mkdir(exist_ok=True)
for i, u in enumerate(urls):
    r = requests.get(u, timeout=30)
    ext = ".gif" if u.lower().endswith(".gif") else ".jpg"
    (out / f"s{i:02d}{ext}").write_bytes(r.content)
    print(i, r.status_code, len(r.content) // 1024, "KB")
