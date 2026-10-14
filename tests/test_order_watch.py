"""order_watch.py 의 발주 안내·알림 문구 테스트 (텔레그램·네이버 API 는 호출하지 않음)"""
import pytest

import order_watch as ow

RULES = {
    "111": {"ownerclan_code": "WFKL6CY", "qty_per_unit": 3, "option_map": {"그레이": "블랙"}},
    "222": {"option_orders": {
        "화이트 화병 + 연핑크": [{"code": "WFPOSIT", "option": "화이트", "qty": 1},
                                 {"code": "WFKL6CY", "option": "연핑크", "qty": 3}],
    }},
    "333": {},
}


def test_order_guide_multiplies_quantity_by_unit():
    po = {"productId": 111, "quantity": 2, "productOption": "화이트"}
    assert ow.order_guide(po, RULES) == "→ 오너클랜 WFKL6CY [화이트] 6개 발주"


def test_order_guide_maps_store_option_to_supplier_option_and_warns():
    po = {"productId": 111, "quantity": 1, "productOption": "그레이"}
    assert ow.order_guide(po, RULES) == "→ 오너클랜 WFKL6CY [블랙] 3개 발주  (⚠️ 스토어 '그레이' = 오너클랜 '블랙')"


def test_order_guide_falls_back_to_channel_product_no():
    po = {"productId": 999, "channelProductNo": 111, "quantity": 1, "productOption": ""}
    assert ow.order_guide(po, RULES) == "→ 오너클랜 WFKL6CY 3개 발주"


def test_order_guide_set_product_lists_each_supplier_order():
    po = {"productId": 222, "quantity": 2, "productOption": "조합: 화이트 화병 + 연핑크 튤립"}
    assert ow.order_guide(po, RULES).splitlines() == [
        "→ 오너클랜 WFPOSIT [화이트] 2개 발주",
        "→ 오너클랜 WFKL6CY [연핑크] 6개 발주",
    ]


@pytest.mark.parametrize("po, expected", [
    ({"productId": 222, "quantity": 1, "productOption": "없는 조합"}, "발주 규칙이 없어요"),
    ({"productId": 333, "quantity": 1}, "발주 규칙 없음"),
    ({"productId": 404, "quantity": 1}, "발주 규칙 없음"),
])
def test_order_guide_flags_missing_rules(po, expected):
    assert expected in ow.order_guide(po, RULES)


def test_format_order_contains_everything_needed_to_ship():
    order = {
        "order": {"orderId": "2026101500001"},
        "productOrder": {
            "productOrderId": "PO-1", "productId": 111, "productName": "바디필로우",
            "productOption": "그레이", "quantity": 1, "totalPaymentAmount": "29900",
            "shippingMemo": "문 앞",
            "shippingAddress": {"name": "홍길동", "tel1": "010-0000-0000",
                                "zipCode": "12345", "baseAddress": "서울시", "detailedAddress": None},
        },
    }
    text = ow.format_order(order, RULES)
    assert "결제금액: 29,900원" in text
    assert "→ 오너클랜 WFKL6CY [블랙] 3개 발주" in text
    assert "주소: 12345 서울시" in text                # 빈 칸은 건너뜀
    assert "배송메모: 문 앞" in text
    assert text.endswith("주문번호: 2026101500001 (상품주문 PO-1)")


def test_load_rules_reads_repo_product_yaml():
    rules = ow.load_rules()
    assert rules, "products/*.yaml 에 channel_product_no 가 있는 상품이 없어요"
    for rule in rules.values():
        assert rule.get("ownerclan_code") or rule.get("option_orders")
        for parts in (rule.get("option_orders") or {}).values():
            assert all({"code", "option", "qty"} <= set(p) for p in parts)
