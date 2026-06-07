#!/usr/bin/env python3
"""Databank ↔ 아카이브 범용 매핑·주입 (장소/조직/탈것·함선).

사용법:
  python3 scripts/entity_pipeline.py map locations      # 매핑 생성/갱신
  python3 scripts/entity_pipeline.py enrich locations   # external_refs 주입
  (엔티티: locations | organizations | vehicles | creatures)

규칙 (캐릭터 파이프라인과 동일):
- name_en 정규화 완전 일치 → exact / 부분 일치 → fuzzy(수동대기) / 불일치 → none
- 기존 verified/rejected 수동 결정은 절대 덮어쓰지 않음
- 주입은 external_refs.databank 네임스페이스만. 큐레이션 필드 불가침(제2조)
- 영문 원문은 cache/databank_descriptions_{entity}/ 에 격리 (제6조)
"""
import json, os, re, sys, datetime

CONFIG = {
    "locations":     {"ours": ["locations.json"],
                      "cache": "cache/databank_raw/locations.json",
                      "mapping": "mapping/locations_to_databank.json"},
    "organizations": {"ours": ["factions.json"],
                      "cache": "cache/databank_raw/organizations.json",
                      "mapping": "mapping/factions_to_databank.json"},
    "creatures":     {"ours": ["creatures.json"],
                      "cache": "cache/databank_raw/creatures.json",
                      "mapping": "mapping/creatures_to_databank.json"},
    "vehicles":      {"ours": ["vehicles.json", "starships.json"],
                      "cache": "cache/databank_raw/vehicles.json",
                      "mapping": "mapping/craft_to_databank.json"},
}

def norm(s):
    s = (s or "").lower().strip()
    s = re.sub(r'["\u201c\u201d\u2018\u2019\u00e9\']', lambda m: 'e' if m.group(0)=='\u00e9' else '', s)
    return re.sub(r"\s+", " ", s)

def load_ours(cfg):
    items = []
    for fn in cfg["ours"]:
        for o in json.load(open(fn, encoding="utf-8")):
            items.append((fn, o))
    return items

def cmd_map(entity):
    cfg = CONFIG[entity]
    if not os.path.exists(cfg["cache"]):
        raise SystemExit(f"{cfg['cache']} 없음 — 덤프를 먼저 업로드/변환하세요")
    bank = json.load(open(cfg["cache"], encoding="utf-8"))
    by_norm = {}
    for b in bank:
        by_norm.setdefault(norm(b["name"]), []).append(b)
    mapping = json.load(open(cfg["mapping"], encoding="utf-8")) if os.path.exists(cfg["mapping"]) else {}
    today = datetime.date.today().isoformat()
    stats = {"exact": 0, "fuzzy": 0, "none": 0, "kept": 0}
    for fn, o in load_ours(cfg):
        oid = o["id"]
        if mapping.get(oid, {}).get("match_status") in ("verified", "rejected"):
            stats["kept"] += 1; continue
        key = norm(o.get("name_en") or "")
        hit = by_norm.get(key)
        if hit and len(hit) == 1:
            b = hit[0]
            mapping[oid] = {"file": fn, "databank_name": b["name"], "databank_id": b["_id"],
                            "image_url": b.get("image"), "match_status": "exact", "matched_at": today}
            stats["exact"] += 1
        else:
            cands = [b for k, bs in by_norm.items() for b in bs if key and len(key) >= 3 and (key in k or k in key)][:5]
            if cands:
                mapping[oid] = {"file": fn, "databank_name": None, "databank_id": None, "image_url": None,
                                "match_status": "fuzzy",
                                "candidates": [{"name": b["name"], "id": b["_id"]} for b in cands]}
                stats["fuzzy"] += 1
            else:
                mapping[oid] = {"file": fn, "databank_name": None, "databank_id": None,
                                "image_url": None, "match_status": "none"}
                stats["none"] += 1
    os.makedirs("mapping", exist_ok=True)
    json.dump(mapping, open(cfg["mapping"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[{entity}] 매핑: exact {stats['exact']} / fuzzy {stats['fuzzy']} / "
          f"none {stats['none']} / 보존 {stats['kept']} → {cfg['mapping']}")

def cmd_enrich(entity):
    cfg = CONFIG[entity]
    mapping = json.load(open(cfg["mapping"], encoding="utf-8"))
    bank = {b["_id"]: b for b in json.load(open(cfg["cache"], encoding="utf-8"))} if os.path.exists(cfg["cache"]) else {}
    desc_dir = f"cache/databank_descriptions_{entity}"
    os.makedirs(desc_dir, exist_ok=True)
    today = datetime.date.today().isoformat()
    injected = 0
    for fn in cfg["ours"]:
        items = json.load(open(fn, encoding="utf-8"))
        for o in items:
            m = mapping.get(o["id"])
            if not m or m.get("match_status") not in ("exact", "verified") or not m.get("databank_id"):
                continue
            if not o.get("external_refs"): o["external_refs"] = {}
            o["external_refs"]["databank"] = {
                "id": m["databank_id"], "name": m.get("databank_name"),
                "image_url": m.get("image_url"),
                "credit": "Star Wars Databank \u00a9 Lucasfilm Ltd.", "fetched_at": today}
            b = bank.get(m["databank_id"])
            if b and b.get("description"):
                open(f"{desc_dir}/{o['id']}.txt", "w", encoding="utf-8").write(b["description"])
            injected += 1
        json.dump(items, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[{entity}] external_refs 주입: {injected}건 / 원문 캐시: {desc_dir}/ (사이트 미노출, 제6조)")

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("map", "enrich") or sys.argv[2] not in CONFIG:
        raise SystemExit(__doc__)
    (cmd_map if sys.argv[1] == "map" else cmd_enrich)(sys.argv[2])
