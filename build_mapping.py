#!/usr/bin/env python3
"""characters.json ↔ Databank API 매핑 테이블 생성/갱신.

입력: characters.json, cache/databank_raw/characters.json
출력: mapping/characters_to_databank.json

매칭 규칙:
- name_en 정규화(소문자·따옴표/공백 정리) 후 완전 일치 → exact
- 부분 포함 일치 → fuzzy (candidates에 후보 나열, 수동 결정 대기)
- 불일치 → none
- 기존 match_status가 verified/rejected인 항목은 절대 덮어쓰지 않음 (수동 결정 보존)
"""
import json, os, re, datetime

MAPPING = "mapping/characters_to_databank.json"
CACHE = "cache/databank_raw/characters.json"

def norm(s):
    s = (s or "").lower().strip()
    s = re.sub(r'["\u201c\u201d\u2018\u2019\']', "", s)
    s = re.sub(r"\s+", " ", s)
    return s

def main():
    chars = json.load(open("characters.json", encoding="utf-8"))
    if not os.path.exists(CACHE):
        raise SystemExit(f"{CACHE} 없음 — 먼저 scripts/fetch_databank.py characters 실행")
    bank = json.load(open(CACHE, encoding="utf-8"))
    by_norm = {}
    for b in bank:
        by_norm.setdefault(norm(b["name"]), []).append(b)

    mapping = {}
    if os.path.exists(MAPPING):
        mapping = json.load(open(MAPPING, encoding="utf-8"))

    stats = {"exact": 0, "fuzzy": 0, "none": 0, "kept": 0}
    for c in chars:
        cid = c["id"]
        prev = mapping.get(cid, {})
        if prev.get("match_status") in ("verified", "rejected"):
            stats["kept"] += 1
            continue
        key = norm(c.get("name_en") or "")
        hit = by_norm.get(key)
        if hit and len(hit) == 1:
            b = hit[0]
            mapping[cid] = {
                "databank_name": b["name"], "databank_id": b["_id"],
                "image_url": b.get("image"), "match_status": "exact",
                "matched_at": datetime.date.today().isoformat(),
            }
            stats["exact"] += 1
        else:
            cands = [b for k, bs in by_norm.items() for b in bs if key and (key in k or k in key)][:5]
            if cands:
                mapping[cid] = {
                    "databank_name": None, "databank_id": None, "image_url": None,
                    "match_status": "fuzzy",
                    "candidates": [{"name": b["name"], "id": b["_id"]} for b in cands],
                }
                stats["fuzzy"] += 1
            else:
                mapping[cid] = {"databank_name": None, "databank_id": None,
                                "image_url": None, "match_status": "none"}
                stats["none"] += 1

    os.makedirs("mapping", exist_ok=True)
    with open(MAPPING, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=1)
    print(f"매핑 갱신 완료: exact {stats['exact']} / fuzzy(수동대기) {stats['fuzzy']} / "
          f"none {stats['none']} / 수동결정 보존 {stats['kept']}")
    print(f"→ {MAPPING}")

if __name__ == "__main__":
    main()
