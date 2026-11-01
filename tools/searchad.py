"""네이버 검색광고 API — 키워드 검색량 조회 / 캠페인 성과 확인.

    python tools/searchad.py check                 # 연결 확인 (키 값은 출력하지 않음)
    python tools/searchad.py keywords 미니화병 바디필로우   # 연관 키워드 월간 검색수·경쟁도
    python tools/searchad.py stats                 # 캠페인별 최근 7일 노출·클릭·비용

키는 프로젝트의 비밀값 파일에 SEARCHAD_ACCESS_LICENSE / SEARCHAD_SECRET_KEY / SEARCHAD_CUSTOMER_ID 로 넣어둔다.
"""
import base64
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from register import load_env  # noqa: E402

BASE = "https://api.searchad.naver.com"


def _keys():
    env = load_env()
    need = ["SEARCHAD_ACCESS_LICENSE", "SEARCHAD_SECRET_KEY", "SEARCHAD_CUSTOMER_ID"]
    missing = [k for k in need if not env.get(k)]
    if missing:
        sys.exit("⛔ 비밀값 파일에 없는 항목: " + ", ".join(missing))
    return env[need[0]], env[need[1]], env[need[2]]


def call(method, uri, params=None, body=None):
    lic, secret, cid = _keys()
    ts = str(int(time.time() * 1000))
    sig = base64.b64encode(hmac.new(secret.encode(), f"{ts}.{method}.{uri}".encode(), hashlib.sha256).digest()).decode()
    headers = {"X-Timestamp": ts, "X-API-KEY": lic, "X-Customer": str(cid), "X-Signature": sig,
               "Content-Type": "application/json; charset=UTF-8"}
    r = requests.request(method, BASE + uri, headers=headers, params=params, json=body, timeout=30)
    if r.status_code >= 400:
        sys.exit(f"⛔ API 오류 {method} {uri} ({r.status_code}): {r.text[:300]}")
    return r.json()


def _num(v):
    return 5 if v == "< 10" else int(v)


def cmd_check():
    camps = call("GET", "/ncc/campaigns")
    print(f"✅ 검색광고 API 연결 성공 — 캠페인 {len(camps)}개")
    for c in camps:
        print(f"   {c.get('name')}  [{c.get('status')}]  하루예산 {c.get('dailyBudget', 0):,}원")


def cmd_keywords(words):
    res = call("GET", "/keywordstool", params={"hintKeywords": ",".join(w.replace(' ', '') for w in words[:5]), "showDetail": 1})
    rows = res.get("keywordList", [])
    rows.sort(key=lambda r: _num(r["monthlyPcQcCnt"]) + _num(r["monthlyMobileQcCnt"]), reverse=True)
    print(f"{'키워드':<20}{'월검색(PC+모바일)':>14}  경쟁")
    for r in rows[:40]:
        total = _num(r["monthlyPcQcCnt"]) + _num(r["monthlyMobileQcCnt"])
        print(f"{r['relKeyword']:<20}{total:>14,}  {r.get('compIdx', '')}")


def cmd_stats():
    camps = call("GET", "/ncc/campaigns")
    if not camps:
        print("캠페인이 없어요.")
        return
    ids = [c["nccCampaignId"] for c in camps]
    fields = json.dumps(["impCnt", "clkCnt", "salesAmt", "ccnt"])
    res = call("GET", "/stats", params={"ids": ",".join(ids), "fields": fields, "datePreset": "last7days"})
    names = {c["nccCampaignId"]: c["name"] for c in camps}
    for d in res.get("data", []):
        print(f"{names.get(d['id'], d['id'])}: 노출 {d.get('impCnt', 0):,} / 클릭 {d.get('clkCnt', 0):,} / "
              f"비용 {d.get('salesAmt', 0):,}원 / 전환 {d.get('ccnt', 0)}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["check"]:
        cmd_check()
    elif a[:1] == ["keywords"] and len(a) > 1:
        cmd_keywords(a[1:])
    elif a[:1] == ["stats"]:
        cmd_stats()
    else:
        print(__doc__)
