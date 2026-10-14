"""register.py 의 검사·데이터 조립 로직 테스트 (네이버 API 는 호출하지 않음)"""
import copy

import pytest

import register as r


@pytest.fixture
def prod(tmp_path):
    """등록 가능한 최소 상품 데이터. 이미지 파일은 tmp_path 에 만든다."""
    for name in ["main.jpg", "extra.jpg", "d1.jpg", "d2.jpg"]:
        (tmp_path / name).write_bytes(b"x")
    return {
        "_dir": tmp_path,
        "name": "미니 화병 튤립 세트",
        "category_id": 50001806,
        "cost": 10000,
        "price": 16900,
        "tags": ["화병", "튤립"],
        "options": {
            "group_name": "색상",
            "items": [{"name": "화이트", "stock": 10}, {"name": "핑크", "stock": 5, "extra_price": 1000}],
        },
        "images": {"main": "main.jpg", "extra": ["extra.jpg"], "detail": ["d1.jpg", "d2.jpg"]},
        "delivery": {
            "company": "CJGLS", "fee_type": "FREE", "base_fee": 0,
            "return_fee": 3500, "exchange_fee": 7000,
            "area_extra_fee": "제주 추가 5,000원", "bundle_group_id": 1,
        },
        "after_service": {"phone": "010XXXXXXXX", "guide": "톡톡으로 문의"},
    }


# ---------------------------------------------------------------- deep_merge / find_todos

def test_deep_merge_overrides_nested_keys_without_dropping_others():
    base = {"delivery": {"company": "CJGLS", "return_fee": 3500}, "tags": ["a"]}
    over = {"delivery": {"return_fee": 5000}, "tags": ["b"]}
    assert r.deep_merge(base, over) == {"delivery": {"company": "CJGLS", "return_fee": 5000}, "tags": ["b"]}
    assert base["delivery"]["return_fee"] == 3500  # 원본은 그대로


def test_find_todos_reports_paths_and_skips_private_keys():
    data = {"name": "TODO", "images": {"extra": ["ok.jpg", "TODO: 사진"]}, "_dir": "TODO"}
    assert r.find_todos(data) == ["name", "images.extra[1]"]


# ---------------------------------------------------------------- validate

def test_validate_passes_complete_product(prod):
    errors, warnings = r.validate(prod)
    assert errors == []
    assert warnings == []


@pytest.mark.parametrize("change, expected", [
    (lambda p: p.update(name="TODO"), "아직 안 채운 항목: name"),
    (lambda p: p.update(name=""), "상품명(name)이 비어 있어요."),
    (lambda p: p.update(name="가" * 101), "상품명이 100자를 넘어요 (101자)."),
    (lambda p: p.update(tags=[str(i) for i in range(11)]), "검색 태그는 10개까지예요 (현재 11개)."),
    (lambda p: p.update(price="미정"), "cost(총원가) / price(판매가)를 숫자로 적어주세요."),
    (lambda p: p.update(already_registered=True), "already_registered: true"),
    (lambda p: p.update(origin="중국 추정"), "'추정'"),
    (lambda p: p["images"].update(main=None), "대표 이미지(images.main)가 없어요."),
    (lambda p: p["images"]["detail"].append("missing.jpg"), "이미지 파일이 없어요: missing.jpg"),
    (lambda p: [i.update(stock=0) for i in p["options"]["items"]], "모든 옵션 재고가 0이에요."),
])
def test_validate_blocks_upload(prod, change, expected):
    change(prod)
    errors, _ = r.validate(prod)
    assert any(expected in e for e in errors), errors


def test_validate_warns_on_low_margin_long_name_and_doll(prod):
    prod.update(cost=15000, name="고양이 인형 " + "가" * 50)
    errors, warnings = r.validate(prod)
    assert errors == []
    assert any("마진율 11%" in w for w in warnings)
    assert any("50자 이내" in w for w in warnings)
    assert any("KC 인증" in w for w in warnings)


def test_validate_kc_warning_silenced_when_checked(prod):
    prod.update(tags=["인형"], kc_checked=True)
    _, warnings = r.validate(prod)
    assert not any("KC" in w for w in warnings)


def test_validate_accepts_remote_image_urls(prod):
    prod["images"]["extra"] = ["https://shop-phinf.pstatic.net/a.jpg"]
    assert r.validate(prod)[0] == []


# ---------------------------------------------------------------- build_payload

def fake_urls(prod):
    return {f: f"https://img/{f}" for f in r._all_images(prod)}


def test_build_payload_maps_product_to_naver_fields(prod):
    payload = r.build_payload(prod, fake_urls(prod))
    origin = payload["originProduct"]

    assert origin["leafCategoryId"] == "50001806"
    assert origin["salePrice"] == 16900
    assert origin["stockQuantity"] == 15                       # 옵션 재고 합
    assert origin["images"]["representativeImage"]["url"] == "https://img/main.jpg"
    assert origin["detailContent"].count("<img") == 2

    fee = origin["deliveryInfo"]["deliveryFee"]
    assert fee["differentialFeeByArea"] == "제주 추가 5,000원"
    assert origin["deliveryInfo"]["deliveryBundleGroupId"] == 1

    combos = origin["detailAttribute"]["optionInfo"]["optionCombinations"]
    assert [c["price"] for c in combos] == [0, 1000]
    assert origin["detailAttribute"]["seoInfo"]["sellerTags"] == [{"text": "화병"}, {"text": "튤립"}]

    # 실수로 바로 노출되지 않게 항상 '전시중지'로 등록
    assert payload["smartstoreChannelProduct"]["channelProductDisplayStatusType"] == "SUSPENSION"


def test_build_payload_without_options_uses_product_stock(prod):
    del prod["options"]
    prod["stock"] = 7
    origin = r.build_payload(prod, fake_urls(prod))["originProduct"]
    assert origin["stockQuantity"] == 7
    assert "optionInfo" not in origin["detailAttribute"]


def test_build_payload_naver_detail_is_passed_through(prod):
    prod["naver_detail"] = {"taxType": "TAX", "originAreaInfo": {"originAreaCode": "0200037"}}
    attr = r.build_payload(prod, fake_urls(prod))["originProduct"]["detailAttribute"]
    assert attr["taxType"] == "TAX"
    assert attr["originAreaInfo"] == {"originAreaCode": "0200037"}


def test_build_payload_does_not_mutate_input(prod):
    before = copy.deepcopy(prod)
    r.build_payload(prod, fake_urls(prod))
    assert prod == before


# ---------------------------------------------------------------- 저장소의 실제 상품 YAML

@pytest.mark.parametrize("path", sorted((r.ROOT / "products").glob("*.yaml")), ids=lambda p: p.stem)
def test_repo_products_build_valid_payload(path):
    """저장소에 있는 상품 YAML 이 기본값과 합쳐져 네이버 등록 데이터로 조립되는지 확인"""
    prod = r.load_product(path)
    assert r.find_todos(prod) == []
    payload = r.build_payload(prod, fake_urls(prod))
    assert payload["originProduct"]["name"] == prod["name"]
    assert len(prod.get("tags", [])) <= 10
