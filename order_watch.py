"""
새 주문 감시 → 텔레그램 알림 (+ 오너클랜 발주 안내)

사용법:
  python order_watch.py setup     # 텔레그램 연결 (봇에게 아무 메시지나 보낸 뒤 실행 → chat id 자동 저장)
  python order_watch.py test      # 텔레그램 테스트 메시지
  python order_watch.py           # 새 주문 확인 1회 (작업 스케줄러가 10분마다 실행)
  python order_watch.py --since 24  # 최근 24시간 주문을 다시 확인 (이미 알린 주문은 건너뜀)

발주 규칙은 products/*.yaml 의 order_rule 에서 읽음:
  channel_product_no: 13780208724
  order_rule:
    ownerclan_code: WFKL6CY
    qty_per_unit: 3                # 1개 팔리면 오너클랜에 3개 발주
    option_map: { 그레이: 블랙 }    # 스토어 옵션명 → 오너클랜 옵션명
"""
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

if sys.stdout is None:                           # 작업 스케줄러(pythonw)로 실행될 때 → 기록을 파일로
    (Path(__file__).parent / "output").mkdir(exist_ok=True)
    sys.stdout = sys.stderr = open(Path(__file__).parent / "output" / "order_watch.log", "a", encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
sys.argv, _args = sys.argv[:1], sys.argv[1:]      # register.py 의 명령 파싱과 겹치지 않게
import register as r

ROOT = Path(__file__).parent
STATE = r.OUT / "order_watch_state.json"
KST = timezone(timedelta(hours=9))


# ---------------------------------------------------------------- 텔레그램

def tg_env():
    env = r.load_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit("⛔ .env 에 TELEGRAM_BOT_TOKEN 이 없어요.")
    return token, env.get("TELEGRAM_CHAT_ID")


def tg_send(text):
    token, chat_id = tg_env()
    if not chat_id:
        sys.exit("⛔ TELEGRAM_CHAT_ID 가 없어요. 먼저 python order_watch.py setup")
    res = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                        json={"chat_id": chat_id, "text": text}, timeout=15)
    if not res.ok:
        print("텔레그램 전송 실패:", res.text)


def cmd_setup():
    token, _ = tg_env()
    upd = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15).json()
    if not upd.get("ok"):
        desc = upd.get("description", "")
        if "webhook" in desc.lower():
            sys.exit("⛔ 이 봇은 다른 곳(예: n8n)에 웹훅으로 연결돼 있어서 메시지를 읽을 수 없어요.\n"
                     "   그쪽을 계속 쓸 거면 새 봇을 만들고, 안 쓸 거면 알려주세요 (웹훅 해제는 그 연결을 끊음).")
        sys.exit(f"⛔ 텔레그램 오류: {desc} (토큰을 다시 확인해주세요)")
    chats = [u["message"]["chat"] for u in upd.get("result", []) if "message" in u]
    if not chats:
        sys.exit("⛔ 봇이 받은 메시지가 없어요. 텔레그램에서 봇에게 아무 말이나 보낸 뒤 다시 실행하세요.")
    chat = chats[-1]
    env_file = ROOT / ".env"
    lines = [l for l in env_file.read_text(encoding="utf-8").splitlines() if not l.startswith("TELEGRAM_CHAT_ID=")]
    lines.append(f"TELEGRAM_CHAT_ID={chat['id']}")
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ 연결됨: {chat.get('first_name', '')} (chat id 저장)")
    tg_send("✅ 홈리빙클럽 주문 알림이 연결됐어요.")


# ---------------------------------------------------------------- 발주 규칙

def load_rules():
    import yaml
    rules = {}
    for f in (ROOT / "products").glob("*.yaml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if d.get("channel_product_no"):
            rule = d.get("order_rule") or {}
            rule.setdefault("ownerclan_code", d.get("ownerclan_code"))
            rules[str(d["channel_product_no"])] = rule
    return rules


def order_guide(po, rules):
    """주문 1건 → 오너클랜 발주 안내 문장"""
    rule = rules.get(str(po.get("productId"))) or rules.get(str(po.get("channelProductNo"))) or {}
    qty = int(po.get("quantity", 1))
    option = po.get("productOption") or ""
    if rule.get("option_orders"):                  # 세트 상품: 옵션마다 여러 건 발주
        for key, parts in rule["option_orders"].items():
            if key in option:
                return "\n".join(f"→ 오너클랜 {p['code']} [{p['option']}] {p['qty'] * qty}개 발주" for p in parts)
        return f"→ ⚠️ 옵션 '{option}' 의 발주 규칙이 없어요 (YAML option_orders 확인)"
    if not rule.get("ownerclan_code"):
        return "→ 발주 규칙 없음 (상품 YAML 에 channel_product_no 를 적어주세요)"
    oc_option = option
    for store_name, oc_name in (rule.get("option_map") or {}).items():
        oc_option = oc_option.replace(store_name, oc_name)
    oc_qty = qty * int(rule.get("qty_per_unit", 1))
    guide = f"→ 오너클랜 {rule['ownerclan_code']}"
    if oc_option:
        guide += f" [{oc_option}]"
    guide += f" {oc_qty}개 발주"
    if oc_option != option:
        guide += f"  (⚠️ 스토어 '{option}' = 오너클랜 '{oc_option}')"
    return guide


# ---------------------------------------------------------------- 주문 조회

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"last_check": None, "notified": [], "last_error_alert": 0}


def save_state(s):
    r.OUT.mkdir(exist_ok=True)
    s["notified"] = s["notified"][-500:]
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def fetch_new_orders(token, since):
    """결제완료(PAYED)로 바뀐 상품주문 id → 상세 조회"""
    res = requests.get(f"{r.BASE}/v1/pay-order/seller/product-orders/last-changed-statuses",
                       headers={"Authorization": f"Bearer {token}"},
                       params={"lastChangedFrom": since.isoformat(timespec="milliseconds"), "lastChangedType": "PAYED"},
                       timeout=30)
    if res.status_code >= 400:
        raise RuntimeError(f"주문 조회 실패 ({res.status_code}): {res.text[:300]}")
    items = (res.json().get("data") or {}).get("lastChangeStatuses") or []
    ids = [i["productOrderId"] for i in items]
    if not ids:
        return []
    detail = requests.post(f"{r.BASE}/v1/pay-order/seller/product-orders/query",
                           headers={"Authorization": f"Bearer {token}"},
                           json={"productOrderIds": ids}, timeout=30)
    if detail.status_code >= 400:
        raise RuntimeError(f"주문 상세 조회 실패 ({detail.status_code}): {detail.text[:300]}")
    return detail.json().get("data") or []


def format_order(o, rules):
    po = o.get("productOrder", {})
    order = o.get("order", {})
    ship = po.get("shippingAddress", {})
    addr = " ".join(x for x in [ship.get("zipCode"), ship.get("baseAddress"), ship.get("detailedAddress")] if x)
    lines = [
        "🔔 새 주문이 들어왔어요!",
        f"상품: {po.get('productName')}",
        f"옵션: {po.get('productOption') or '-'} / 수량 {po.get('quantity')}",
        f"결제금액: {int(po.get('totalPaymentAmount') or 0):,}원",
        "",
        order_guide(po, rules),
        "",
        f"받는 분: {ship.get('name')} / {ship.get('tel1')}",
        f"주소: {addr}",
    ]
    if po.get("shippingMemo"):
        lines.append(f"배송메모: {po['shippingMemo']}")
    lines.append(f"주문번호: {order.get('orderId')} (상품주문 {po.get('productOrderId')})")
    return "\n".join(lines)


def run(since_hours=None):
    state = load_state()
    now = datetime.now(KST)
    if since_hours:
        since = now - timedelta(hours=since_hours)
    elif state["last_check"]:
        since = datetime.fromisoformat(state["last_check"]) - timedelta(minutes=5)   # 겹쳐서 확인 (누락 방지)
    else:
        since = now - timedelta(hours=24)
    since = max(since, now - timedelta(hours=23, minutes=50))                      # API 조회 한도 24시간

    try:
        token = _token()
        orders = fetch_new_orders(token, since)
    except Exception as e:
        print("⚠️", e)
        if time.time() - state.get("last_error_alert", 0) > 3 * 3600:              # 오류 알림은 3시간에 1번
            hint = "\n집 IP가 바뀌었을 수 있어요 → 커머스API센터에서 API 호출 IP 교체" if "IP_NOT_ALLOWED" in str(e) else ""
            tg_send(f"⚠️ 주문 확인이 안 되고 있어요.\n{str(e)[:200]}{hint}")
            state["last_error_alert"] = time.time()
        save_state(state)
        return

    rules = load_rules()
    new = [o for o in orders if o.get("productOrder", {}).get("productOrderId") not in state["notified"]]
    for o in new:
        tg_send(format_order(o, rules))
        state["notified"].append(o["productOrder"]["productOrderId"])
    state["last_check"] = now.isoformat()
    save_state(state)
    print(f"{now:%m-%d %H:%M} 확인 완료 — 새 주문 {len(new)}건")


def _token():
    """register.get_token 은 실패 시 sys.exit 하므로, 예외로 바꿔서 알림을 보낼 수 있게 함"""
    try:
        return r.get_token(r.load_env())
    except SystemExit as e:
        raise RuntimeError(str(e))


if __name__ == "__main__":
    if _args[:1] == ["setup"]:
        cmd_setup()
    elif _args[:1] == ["test"]:
        tg_send("🧪 테스트 알림이에요. 주문이 들어오면 이렇게 알려드릴게요.")
        print("보냄")
    elif _args[:1] == ["--since"] and len(_args) == 2:
        run(float(_args[1]))
    else:
        run()
