#!/usr/bin/env python3
"""매핑 확정 항목에 external_refs.databank 주입.

원칙(헌법 정합):
- 큐레이션 필드(사실·동기·arc·소속·works 등)는 절대 건드리지 않는다 (제2조).
- 영문 description 원문은 characters.json에 저장하지 않는다 (제6조).
  → cache/databank_descriptions/{char_id}.txt 에만 보관 (빌드·배포 제외).
- external_refs 네임스페이스로 외부 출처를 큐레이션과 분리한다.

대상: mapping의 match_status ∈ {exact, verified}
"""
import json, os, datetime

MAPPING = "mapping/characters_to_databank.json"
CACHE = "cache/databank_raw/characters.json"
DESC_DIR = "cache/databank_descriptions"

def main():
    chars = json.load(open("characters.json", encoding="utf-8"))
    mapping = json.load(open(MAPPING, encoding="utf-8"))
    bank = {}
    if os.path.exists(CACHE):
        bank = {b["_id"]: b for b in json.load(open(CACHE, encoding="utf-8"))}

    os.makedirs(DESC_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    injected = 0
    for c in chars:
        m = mapping.get(c["id"])
        if not m or m.get("match_status") not in ("exact", "verified"):
            continue
        if not m.get("databank_id"):
            continue
        c.setdefault("external_refs", {})["databank"] = {
            "id": m["databank_id"],
            "name": m.get("databank_name"),
            "image_url": m.get("image_url"),
            "credit": "Star Wars Databank \u00a9 Lucasfilm Ltd.",
            "fetched_at": today,
        }
        b = bank.get(m["databank_id"])
        if b and b.get("description"):
            with open(f"{DESC_DIR}/{c['id']}.txt", "w", encoding="utf-8") as f:
                f.write(b["description"])
        injected += 1

    with open("characters.json", "w", encoding="utf-8") as f:
        json.dump(chars, f, ensure_ascii=False, indent=2)
    print(f"external_refs 주입: {injected}명 / 원문 캐시: {DESC_DIR}/")
    print("주의: 영문 원문은 사이트에 노출되지 않습니다(제6조). 재구성 소스로만 사용.")

if __name__ == "__main__":
    main()
