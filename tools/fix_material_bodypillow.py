# 2026-09-29 바디필로우 상품정보제공고시 소재 정정 (공급사 제품정보 기준: 소재 스판덱스, 충전재 PP면)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.argv = ["x"]
import register as r

MATERIAL = "겉감: 스판덱스 / 충전재: PP면"


def fix(p):
    p["originProduct"]["detailAttribute"]["productInfoProvidedNotice"]["sleepingGear"]["material"] = MATERIAL


r.modify_product("13755644295", fix)
