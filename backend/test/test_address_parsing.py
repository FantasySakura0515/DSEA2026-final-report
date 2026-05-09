"""
固定 extract_addresses 的清洗行為，避免日後改動規則時靜默退化。

每個案例都對應一筆原始資料的常見寫法：
- 頓號枚舉 + 範圍混合
- 之-連字符
- 括號內藏完整地址
- 樓層描述需被剝除
- 多段巷弄需要承襲上一段路名
"""

from data.earthquake_building_cleaning import extract_addresses


def test_enumeration_with_range():
    addrs = extract_addresses("天母北路87巷22弄2、4、6號； 87巷16至22號1至5樓")
    assert "天母北路87巷22弄2號" in addrs
    assert "天母北路87巷22弄4號" in addrs
    assert "天母北路87巷22弄6號" in addrs
    for n in range(16, 23):
        assert f"天母北路87巷{n}號" in addrs


def test_range_with_suffix_zhi():
    addrs = extract_addresses("延平北路五段213巷17至33之1號")
    assert "延平北路五段213巷17之1號" in addrs
    assert "延平北路五段213巷33之1號" in addrs


def test_parenthetical_full_address_extracted():
    text = "知行路62至74號(其中知行路64、66號地下一樓及地上一.二.三.四.五樓建築物撤銷列管)、(同知行路60巷1號)"
    addrs = extract_addresses(text)
    for n in range(62, 75):
        assert f"知行路{n}號" in addrs
    assert "知行路60巷1號" in addrs


def test_floor_text_is_stripped():
    addrs = extract_addresses("清江路156號1樓")
    assert "清江路156號" in addrs
    assert all("樓" not in a for a in addrs)


def test_inherits_last_road_for_lane_only_segment():
    addrs = extract_addresses("中央北路四段442巷4弄2至10號")
    for n in range(2, 11):
        assert f"中央北路四段442巷4弄{n}號" in addrs


def test_dash_is_normalized_to_zhi():
    addrs = extract_addresses("某路118-5號")
    assert "某路118之5號" in addrs


def test_parity_odd_marker_filters_to_odd():
    addrs = extract_addresses("某路1至10號(單)")
    nums = [int(a.replace("某路", "").replace("號", "")) for a in addrs]
    assert nums and all(n % 2 == 1 for n in nums)
