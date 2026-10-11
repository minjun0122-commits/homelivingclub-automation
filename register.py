"""
홈리빙클럽 스마트스토어 상품 등록 도구 (네이버 커머스 API)

사용법:
  python register.py check  products/고양이바디필로우.yaml   # 드라이런: 검사 + 등록될 내용 미리보기 (네이버에 아무것도 안 보냄)
  python register.py auth                                    # API 로그인만 테스트
  python register.py list                                    # 내 스토어 상품 목록 (채널상품번호 확인)
  python register.py fetch  <채널상품번호>                    # 이미 등록된 상품 정보를 받아서 참고용 JSON으로 저장
  python register.py categories 바디필로우                     # 카테고리 ID 검색
  python register.py upload products/xxx.yaml                # 실제 등록 (확인 질문 후 진행)
  python register.py display <채널상품번호> on|off            # 전시 켜기/끄기
  python register.py area-text <채널상품번호>                 # 제주/도서산간 안내 문구를 공통 설정값으로 수정"""
import base64
import json
import mimetypes
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
BASE = "https://api.commerce.naver.com/external"
OUT = ROOT / "output"

if sys.stdout:                                   # pythonw(창 없이 실행)일 때는 stdout 이 없음
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- 설정 / 입력

def load_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        sys.exit("⛔ .env 파일이 없어요. .env.example 을 복사해서 .env 로 만들고 ID/시크릿을 채워주세요.")
    env = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    if not env.get("NAVER_CLIENT_ID") or not env.get("NAVER_CLIENT_SECRET"):
        sys.exit("⛔ .env 에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 이 비어 있어요.")
    return env


def deep_merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_product(path):
    """store_defaults.yaml 위에 상품 YAML 을 덮어써서 반환."""
    import yaml
    p = Path(path)
    if not p.exists():
        sys.exit(f"⛔ 파일이 없어요: {p}")
    defaults_file = ROOT / "store_defaults.yaml"
    defaults = yaml.safe_load(defaults_file.read_text(encoding="utf-8")) if defaults_file.exists() else {}
    data = deep_merge(defaults or {}, yaml.safe_load(p.read_text(encoding="utf-8")))
    data["_dir"] = p.parent
    return data


# ---------------------------------------------------------------- 검사

def find_todos(obj, path=""):
    """값에 TODO 가 남아 있는 항목 경로를 모두 찾는다."""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not str(k).startswith("_"):
                found += find_todos(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found += find_todos(v, f"{path}[{i}]")
    elif isinstance(obj, str) and "TODO" in obj:
        found.append(path)
    return found


def contains_text(obj, word):
    return word in json.dumps(obj, ensure_ascii=False, default=str)


def is_url(f):
    return str(f).startswith("http")


def validate(prod):
    """(errors, warnings) 반환. errors 가 하나라도 있으면 실제 등록 불가."""
    errors, warnings = [], []

    for p in find_todos(prod):
        errors.append(f"아직 안 채운 항목: {p}")

    if contains_text({k: v for k, v in prod.items() if not k.startswith("_")}, "추정"):
        errors.append("'추정' 이라는 표현이 있어요. 상품정보제공고시는 확인된 정보만 써야 해요.")

    if prod.get("already_registered"):
        errors.append("already_registered: true — 이미 스토어에 있는 상품이라 중복 등록을 막았어요.")

    name = prod.get("name", "")
    if not name:
        errors.append("상품명(name)이 비어 있어요.")
    elif len(name) > 100:
        errors.append(f"상품명이 100자를 넘어요 ({len(name)}자).")
    elif len(name) > 50:
        warnings.append(f"상품명이 {len(name)}자예요. 50자 이내가 검색 노출에 유리해요.")

    tags = prod.get("tags", [])
    if len(tags) > 10:
        errors.append(f"검색 태그는 10개까지예요 (현재 {len(tags)}개).")

    cost, price = prod.get("cost"), prod.get("price")
    if isinstance(cost, (int, float)) and isinstance(price, (int, float)) and price > 0:
        margin = price - cost
        rate = margin / price * 100
        if rate < 20:
            warnings.append(f"마진율 {rate:.0f}% — 목표 20% 미만이에요.")
    else:
        errors.append("cost(총원가) / price(판매가)를 숫자로 적어주세요.")

    items = (prod.get("options") or {}).get("items", [])
    if items and all(i.get("stock", 0) <= 0 for i in items):
        errors.append("모든 옵션 재고가 0이에요.")
    for i in items:
        if i.get("stock", 0) <= 0:
            warnings.append(f"옵션 '{i.get('name')}' 재고 0 — 품절로 등록돼요.")

    if (contains_text(name, "인형") or any("인형" in t for t in tags)) and not prod.get("kc_checked"):
        warnings.append(
            "상품명/태그에 '인형'이 있어요. 봉제인형은 어린이제품 KC 인증 대상일 수 있어요. "
            "오너클랜에서 인증번호를 확인했다면 kc_checked: true 로 표시하세요."
        )

    imgs = prod.get("images", {})
    all_imgs = [imgs.get("main")] + imgs.get("extra", []) + imgs.get("detail", [])
    if not imgs.get("main"):
        errors.append("대표 이미지(images.main)가 없어요.")
    for f in filter(None, all_imgs):
        if "TODO" not in f and not is_url(f) and not (prod["_dir"] / f).exists():
            errors.append(f"이미지 파일이 없어요: {f}")

    return errors, warnings


# ---------------------------------------------------------------- 등록 데이터 조립

def build_payload(prod, image_urls):
    """image_urls: 로컬 경로 -> 네이버 이미지 URL. 드라이런에선 가짜 URL."""
    imgs = prod["images"]
    d = prod["delivery"]
    opts = prod.get("options")

    detail_html = prod.get("detail_html_top", "") + "<br />\n".join(
        f'<img src="{image_urls[f]}" style="max-width:100%;width:100%;height:auto;display:block;" />'
        for f in imgs.get("detail", [])
    )

    detail_attribute = {
        "afterServiceInfo": {
            "afterServiceTelephoneNumber": prod["after_service"]["phone"],
            "afterServiceGuideContent": prod["after_service"]["guide"],
        },
        "minorPurchasable": True,
        "seoInfo": {"sellerTags": [{"text": t} for t in prod.get("tags", [])]},
    }
    if opts:
        detail_attribute["optionInfo"] = {
            "useStockManagement": True,
            "optionCombinationGroupNames": {"optionGroupName1": opts["group_name"]},
            "optionCombinations": [
                {"optionName1": i["name"], "stockQuantity": i["stock"], "price": i.get("extra_price", 0), "usable": True}
                for i in opts["items"]
            ],
        }
    # 원산지 / 상품정보제공고시 / KC 인증은 YAML 의 naver_detail 에 적힌 그대로 넣는다.
    # (필드 형식이 복잡해서, fetch 로 받은 기존 상품 JSON 을 보고 맞추는 게 가장 정확함)
    detail_attribute.update(prod.get("naver_detail", {}))

    stock_total = sum(i["stock"] for i in opts["items"]) if opts else prod.get("stock", 0)

    delivery_fee = {"deliveryFeeType": d["fee_type"], "baseFee": d.get("base_fee", 0)}
    if d.get("area_extra_fee"):
        delivery_fee["differentialFeeByArea"] = d["area_extra_fee"]
    claim = {"returnDeliveryFee": d["return_fee"], "exchangeDeliveryFee": d["exchange_fee"]}
    if d.get("shipping_address_id"):
        claim["shippingAddressId"] = d["shipping_address_id"]
    if d.get("return_address_id"):
        claim["returnAddressId"] = d["return_address_id"]
    delivery_info = {
        "deliveryType": "DELIVERY",
        "deliveryAttributeType": "NORMAL",
        "deliveryCompany": d["company"],
        "deliveryFee": delivery_fee,
        "claimDeliveryInfo": claim,
    }
    if d.get("bundle_group_id"):
        delivery_info.update(deliveryBundleGroupUsable=True, deliveryBundleGroupId=d["bundle_group_id"])

    return {
        "originProduct": {
            "statusType": "SALE",
            "saleType": "NEW",
            "leafCategoryId": str(prod["category_id"]),
            "name": prod["name"],
            "detailContent": detail_html,
            "images": {
                "representativeImage": {"url": image_urls[imgs["main"]]},
                "optionalImages": [{"url": image_urls[f]} for f in imgs.get("extra", [])],
            },
            "salePrice": prod["price"],
            "stockQuantity": stock_total,
            "deliveryInfo": delivery_info,
            "detailAttribute": detail_attribute,
        },
        "smartstoreChannelProduct": {
            "naverShoppingRegistration": True,
            # 전시중지 상태로 등록 → 판매자센터에서 직접 검수 후 '전시'로 바꾸기
            "channelProductDisplayStatusType": "SUSPENSION",
        },
    }


# ---------------------------------------------------------------- 네이버 API

def get_token(env):
    import bcrypt
    import requests
    cid, secret = env["NAVER_CLIENT_ID"], env["NAVER_CLIENT_SECRET"]
    ts = str(int(time.time() * 1000))
    hashed = bcrypt.hashpw(f"{cid}_{ts}".encode(), secret.encode())
    r = requests.post(
        f"{BASE}/v1/oauth2/token",
        data={
            "client_id": cid,
            "timestamp": ts,
            "client_secret_sign": base64.b64encode(hashed).decode(),
            "grant_type": "client_credentials",
            "type": "SELF",
        },
        timeout=15,
    )
    if r.status_code != 200:
        sys.exit(f"⛔ 로그인 실패 ({r.status_code}): {r.text}")
    return r.json()["access_token"]


def api(method, path, token, **kw):
    import requests
    r = requests.request(method, f"{BASE}{path}", headers={"Authorization": f"Bearer {token}"}, timeout=60, **kw)
    if r.status_code >= 400:
        sys.exit(f"⛔ API 오류 {method} {path} ({r.status_code}):\n{r.text}")
    return r.json() if r.text else {}


def upload_images(token, prod):
    """로컬 파일만 네이버에 업로드. 이미 URL 인 이미지는 그대로 사용."""
    files = [f for f in dict.fromkeys(_all_images(prod)) if not is_url(f)]
    urls = {f: f for f in _all_images(prod) if is_url(f)}
    for start in range(0, len(files), 10):  # 한 번에 최대 10장
        batch = files[start:start + 10]
        payload = [
            ("imageFiles", (Path(f).name, open(prod["_dir"] / f, "rb"), mimetypes.guess_type(f)[0] or "image/jpeg"))
            for f in batch
        ]
        res = api("POST", "/v1/product-images/upload", token, files=payload)
        for f, img in zip(batch, res["images"]):
            urls[f] = img["url"]
        print(f"  이미지 {start + len(batch)}/{len(files)} 업로드")
    return urls


# ---------------------------------------------------------------- 명령

def print_report(prod, errors, warnings):
    cost, price = prod.get("cost", 0), prod.get("price", 0)
    print(f"\n📦 {prod.get('name')}")
    if isinstance(cost, (int, float)) and isinstance(price, (int, float)) and price:
        print(f"   판매가 {price:,}원 / 원가 {cost:,}원 / 마진 {price - cost:,}원 ({(price - cost) / price * 100:.0f}%)")
    for i in (prod.get("options") or {}).get("items", []):
        print(f"   옵션 {i['name']}: 재고 {i['stock']}")
    print(f"   태그 {len(prod.get('tags', []))}개: {', '.join(prod.get('tags', []))}")
    print()
    for e in errors:
        print(f"  ❌ {e}")
    for w in warnings:
        print(f"  ⚠️  {w}")
    if not errors and not warnings:
        print("  ✅ 문제 없음")


def cmd_check(path):
    prod = load_product(path)
    errors, warnings = validate(prod)
    print_report(prod, errors, warnings)
    try:
        fake = {f: f if is_url(f) else f"https://(업로드후생성)/{Path(f).name}" for f in _all_images(prod)}
        payload = build_payload(prod, fake)
        OUT.mkdir(exist_ok=True)
        out = OUT / f"{Path(path).stem}_payload_preview.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n📝 네이버로 보낼 내용 미리보기: {out.relative_to(ROOT)}")
    except (KeyError, TypeError) as e:
        print(f"\n(미리보기 생성 불가 — 필수 항목 누락: {e})")
    print("\n※ 드라이런이라 네이버에는 아무것도 보내지 않았어요.")
    if errors:
        print(f"※ ❌ {len(errors)}개를 고쳐야 upload 할 수 있어요.")


def _all_images(prod):
    imgs = prod.get("images", {})
    return list(filter(None, [imgs.get("main")] + imgs.get("extra", []) + imgs.get("detail", [])))


def cmd_upload(path):
    prod = load_product(path)
    errors, warnings = validate(prod)
    print_report(prod, errors, warnings)
    if errors:
        sys.exit("\n⛔ 위 ❌ 항목을 고친 뒤 다시 실행하세요. 등록하지 않았어요.")
    if input("\n실제로 네이버에 등록할까요? (yes 입력): ").strip().lstrip("﻿").lower() != "yes":
        sys.exit("취소했어요.")
    env = load_env()
    token = get_token(env)
    urls = upload_images(token, prod)
    payload = build_payload(prod, urls)
    res = api("POST", "/v2/products", token, json=payload)
    OUT.mkdir(exist_ok=True)
    log = OUT / "registered_log.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"time": time.strftime("%Y-%m-%d %H:%M"), "file": str(path), "result": res}, ensure_ascii=False) + "\n")
    print(f"\n✅ 등록 완료: {res}")
    print("   '전시중지' 상태로 올라가 있어요. 판매자센터에서 확인한 뒤 전시로 바꾸세요.")
    print(f"   YAML 에 already_registered: true 를 추가해두면 중복 등록을 막을 수 있어요.")


def cmd_auth():
    get_token(load_env())
    print("✅ 네이버 커머스 API 로그인 성공")


def cmd_fetch(channel_no):
    token = get_token(load_env())
    res = api("GET", f"/v2/products/channel-products/{channel_no}", token)
    OUT.mkdir(exist_ok=True)
    out = OUT / f"fetched_{channel_no}.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 저장: {out.relative_to(ROOT)}")
    print("   detailAttribute 안의 originAreaInfo / productInfoProvidedNotice / 인증 정보를 YAML naver_detail 에 참고하세요.")


def _leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from _leaves(v, f"{p}.{k}" if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _leaves(v, f"{p}[{i}]")
    else:
        yield p, o


def modify_product(channel_no, mutate):
    """기존 상품 수정: 현재 정보 백업 → mutate(product) 로 일부만 변경 → 저장 → 실제로 바뀐 항목 출력.
    네이버 수정 API 는 상품 전체를 다시 보내야 해서, 받아온 그대로에서 필요한 칸만 바꾼다."""
    token = get_token(load_env())
    path = f"/v2/products/channel-products/{channel_no}"
    before = api("GET", path, token)
    OUT.mkdir(exist_ok=True)
    backup = OUT / f"backup_{channel_no}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    backup.write_text(json.dumps(before, ensure_ascii=False, indent=2), encoding="utf-8")
    product = json.loads(json.dumps(before))
    mutate(product)
    api("PUT", path, token, json=product)
    after = api("GET", path, token)
    a, b = dict(_leaves(before)), dict(_leaves(after))
    changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    print(f"✅ {after['originProduct']['name']}")
    for k in changed:
        print(f"   {k}: {a.get(k)} → {b.get(k)}")
    if not changed:
        print("   (바뀐 항목 없음)")
    print(f"   백업: {backup.relative_to(ROOT)}")


def cmd_display(channel_no, state):
    state = {"on": "ON", "off": "SUSPENSION"}.get(state.lower())
    if not state:
        sys.exit("⛔ on 또는 off 로 적어주세요.")
    modify_product(channel_no, lambda p: p["smartstoreChannelProduct"].update(channelProductDisplayStatusType=state))


def cmd_area_text(channel_no):
    """제주/도서산간 안내 문구를 store_defaults.yaml 의 area_extra_fee 로 맞춘다."""
    import yaml
    text = yaml.safe_load((ROOT / "store_defaults.yaml").read_text(encoding="utf-8"))["delivery"]["area_extra_fee"]
    modify_product(channel_no, lambda p: p["originProduct"]["deliveryInfo"]["deliveryFee"].update(differentialFeeByArea=text))


def cmd_list():
    token = get_token(load_env())
    res = api("POST", "/v1/products/search", token, json={"page": 1, "size": 50})
    for p in res.get("contents", []):
        for ch in p.get("channelProducts", []):
            print(f"  채널상품번호 {ch.get('channelProductNo')}  [{ch.get('statusType')}]  "
                  f"{ch.get('salePrice', 0):,}원  {ch.get('name')}")
    print(f"\n총 {res.get('totalElements', 0)}개")


def cmd_categories(keyword):
    token = get_token(load_env())
    cats = api("GET", "/v1/categories", token, params={"last": "true"})
    hits = [c for c in cats if keyword in c.get("wholeCategoryName", "")]
    for c in hits[:30]:
        print(f"  {c['id']}  {c['wholeCategoryName']}")
    print(f"\n{len(hits)}개 찾음" + (" (30개만 표시)" if len(hits) > 30 else ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    cmds = {"check": cmd_check, "upload": cmd_upload, "fetch": cmd_fetch, "categories": cmd_categories}
    if args[:1] == ["auth"]:
        cmd_auth()
    elif args[:1] == ["list"]:
        cmd_list()
    elif len(args) == 2 and args[0] == "area-text":
        cmd_area_text(args[1])
    elif len(args) == 3 and args[0] == "display":
        cmd_display(args[1], args[2])
    elif len(args) == 2 and args[0] in cmds:
        cmds[args[0]](args[1])
    else:
        print(__doc__)
