import json
import re
import time
from pathlib import Path
from typing import List, Optional, Set, Tuple

import httpx

from app.models.earthquakes_building import (
    EarthquakeBuildingFormatResponse,
    EarthquakeBuildingItemFormat,
    EarthquakeBuildingItemGeoList,
    EarthquakeBuildingResponse,
)
from data.util import get_geocode_from_arcgis

API_URL = "https://data.taipei/api/v1/dataset/a6e8f08e-ec2a-4be7-a762-54452b0c27df"
OUTPUT_PATH = Path(__file__).with_name("earthquake_building_format.json")


ROAD_RE = r"(.*?[路街](?:.*?段)?)"
ROAD_LANE_RE = r"(.*?[路街](?:.*?段)?\d+巷(?:\d+弄)?)"


def normalize_text(text: str) -> str:
    """統一範圍標記與全形符號，方便後續正則處理"""
    text = text.replace("~", "至").replace("～", "至").replace("到", "至")
    return text


def finalize_address(addr: str) -> str:
    """把 118-5號 改寫成 118之5號 等格式，提升 geocoding 命中率"""
    return re.sub(r"(\d+)-(\d+)", r"\1之\2", addr)


def extract_addresses(text: str) -> List[str]:
    """提取並展開台灣地址"""
    addresses: Set[str] = set()

    for chunk in re.findall(r"\(([^)]*)\)", text):
        if re.search(r"[路街]", chunk):
            extract_from_segment(normalize_text(chunk).strip(), "", addresses, None)

    parity_pat = re.compile(r"\(雙\)|\(偶\)|\(單\)|\(奇\)|[;；]")
    pieces: List[Tuple[str, Optional[str]]] = []
    pos = 0
    for m in parity_pat.finditer(text):
        marker = m.group()
        if marker in ("(雙)", "(偶)"):
            parity: Optional[str] = "even"
        elif marker in ("(單)", "(奇)"):
            parity = "odd"
        else:
            parity = None
        pieces.append((text[pos:m.start()], parity))
        pos = m.end()
    pieces.append((text[pos:], None))

    last_road = ""
    for raw_seg, parity in pieces:
        seg = re.sub(r"\([^)]*\)", " ", raw_seg)
        seg = re.sub(r"地下\s*\d+\s*樓|\d+至\d+樓|\d+\s*樓|地下室", "", seg)
        seg = normalize_text(seg).strip()
        if not seg:
            continue

        road_match = re.search(ROAD_RE, seg)
        if road_match:
            last_road = road_match.group(1)

        extract_from_segment(seg, last_road, addresses, parity)

    return sorted(finalize_address(a) for a in addresses)


PREFIX_NOISE_RE = re.compile(r"^(其中|同|另|及|並|且|含)\s*")


def extract_from_segment(
    segment: str,
    last_road: str,
    addresses: Set[str],
    parity: Optional[str] = None,
):
    """處理單個段落"""
    segment = PREFIX_NOISE_RE.sub("", segment)
    if "至" in segment:
        handle_range(segment, last_road, addresses, parity)
        return

    if "、" in segment:
        handle_enumeration(segment, last_road, addresses)
        return

    handle_single(segment, last_road, addresses)


def handle_enumeration(segment: str, last_road: str, addresses: Set[str]):
    """處理頓號分隔的號碼：2、4、6號"""
    base_match = re.match(ROAD_LANE_RE, segment)
    if not base_match:
        base_match = re.match(ROAD_RE, segment)

    base_addr = base_match.group(1) if base_match else ""

    if not base_addr and last_road:
        lane_match = re.match(r"(\d+巷)(?:\d+弄)?", segment)
        if lane_match:
            base_addr = last_road + lane_match.group(1)

    if not base_addr:
        return

    remaining = segment[len(base_addr):] if segment.startswith(base_addr) else segment
    numbers = re.findall(r"(\d+)(?=號|、)", remaining)
    for num in numbers:
        addresses.add(f"{base_addr}{num}號")


def handle_range(
    segment: str,
    last_road: str,
    addresses: Set[str],
    parity: Optional[str] = None,
):
    """處理範圍表示：16至22號 或 17至33之1號；parity 為 even/odd 時只展開對應奇偶號"""
    base_addr = ""

    full_match = re.match(ROAD_LANE_RE, segment)
    if full_match:
        base_addr = full_match.group(1)
    else:
        road_match = re.match(ROAD_RE, segment)
        if road_match:
            base_addr = road_match.group(1)
        else:
            lane_match = re.match(r"(\d+巷)(?:\d+弄)?", segment)
            if lane_match and last_road:
                base_addr = last_road + lane_match.group(1)

    if not base_addr:
        return

    range_match = re.search(r"(\d+)號?至(\d+)(之\d+)?號?", segment)
    if not range_match:
        return

    start = int(range_match.group(1))
    end = int(range_match.group(2))
    suffix = range_match.group(3) or ""

    for num in range(start, end + 1):
        if parity == "even" and num % 2 != 0:
            continue
        if parity == "odd" and num % 2 == 0:
            continue
        addresses.add(f"{base_addr}{num}{suffix}號")


def handle_single(segment: str, last_road: str, addresses: Set[str]):
    """處理單一地址"""
    match = re.search(
        r"(.*?[路街](?:.*?段)?(?:\d+巷)?(?:\d+弄)?\d+(?:[之\-]\d+)?號)", segment
    )
    if match:
        addresses.add(match.group(1))
        return

    if last_road:
        lane_only = re.search(r"(\d+巷(?:\d+弄)?\d+(?:[之\-]\d+)?號)", segment)
        if lane_only:
            addresses.add(last_road + lane_only.group(1))


def build_earthquake_building_dataset() -> None:
    params = {"limit": 2000, "offset": 0, "scope": "resourceAquire"}
    response = httpx.get(API_URL, params=params, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    upstream = EarthquakeBuildingResponse.model_validate(data)

    out_items: list[EarthquakeBuildingItemFormat] = []
    for item in upstream.result.results:
        codes = extract_addresses(item.building_location)
        geolist: list[EarthquakeBuildingItemGeoList] = []
        for code in codes:
            coords = get_geocode_from_arcgis(item.county + code)
            if coords is None:
                geolist.append(
                    EarthquakeBuildingItemGeoList(
                        longitude=None, latitude=None, geocoded=False
                    )
                )
            else:
                lon, lat = coords
                geolist.append(
                    EarthquakeBuildingItemGeoList(
                        longitude=lon, latitude=lat, geocoded=True
                    )
                )
            time.sleep(0.1)
            print(f"Processed: {code}")

        out_items.append(
            EarthquakeBuildingItemFormat(**item.model_dump(), geo=geolist)
        )

    format_response = EarthquakeBuildingFormatResponse(result=out_items)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            format_response.model_dump(),
            f,
            ensure_ascii=False,
            indent=4,
        )


if __name__ == "__main__":
    build_earthquake_building_dataset()
