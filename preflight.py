#!/usr/bin/env python3
"""통합 사전검사 — 머지/배포 전 한 번에 돌리는 게이트.

  python3 preflight.py

검사 3단:
  1) 데이터 무결성     — validate.py 위임 (id·enum·참조·인과·external_refs)
  2) 페이지 JS 문법    — 전 *.html 최대 <script>를 node --check
  3) 매핑 무결성        — 유령 id·필드 누락·중복 databank_id(오매핑)·역참조 일관성

종료 코드: 통과 0 / 실패 1  (GitHub Actions 게이트가 이 값으로 머지를 막음)
"""
import json, os, re, subprocess, sys, glob, tempfile

DIR = os.path.dirname(os.path.abspath(__file__))
FAIL, WARN = [], []
def fail(m): FAIL.append(m)
def warn(m): WARN.append(m)
def load(n): return json.load(open(os.path.join(DIR, n), encoding="utf-8"))

# ── 1) 데이터 무결성 (validate.py 위임) ───────────────────────────
def stage_validate():
    r = subprocess.run([sys.executable, "validate.py"], cwd=DIR, capture_output=True, text=True)
    line = next((l for l in r.stdout.splitlines() if "판정" in l), r.stdout.strip()[-200:])
    print(f"  {line.strip()}")
    if r.returncode != 0:
        fail("데이터 무결성 검증 실패 (validate.py)")

# ── 2) 페이지 JS 문법 ─────────────────────────────────────────────
def stage_js():
    if not _have_node():
        warn("node 미설치 — JS 문법 검사 건너뜀")
        return
    pages = sorted(glob.glob(os.path.join(DIR, "*.html")))
    ok = 0
    for p in pages:
        html = open(p, encoding="utf-8").read()
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
        scripts = [s for s in scripts if "src=" not in s[:0] and s.strip()]
        if not scripts:
            continue
        body = max(scripts, key=len)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(body); tmp = f.name
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.unlink(tmp)
        if r.returncode == 0:
            ok += 1
        else:
            err = r.stderr.strip().splitlines()
            fail(f"JS 문법 오류: {os.path.basename(p)} — {err[-1] if err else '?'}")
    print(f"  JS 문법 통과 {ok}개 페이지")

def _have_node():
    try:
        subprocess.run(["node", "--version"], capture_output=True); return True
    except FileNotFoundError:
        return False

# ── 3) 매핑 무결성 ────────────────────────────────────────────────
MAP = {
    "characters": (["characters.json"], "mapping/characters_to_databank.json"),
    "locations":  (["locations.json"],  "mapping/locations_to_databank.json"),
    "factions":   (["factions.json"],   "mapping/factions_to_databank.json"),
    "craft":      (["vehicles.json", "starships.json"], "mapping/craft_to_databank.json"),
    "creatures":  (["creatures.json"],  "mapping/creatures_to_databank.json"),
}
def stage_mapping():
    total_linked = 0
    for ent, (files, mpath) in MAP.items():
        if not os.path.exists(os.path.join(DIR, mpath)):
            continue
        mapping = load(mpath)
        ours = {}
        for fn in files:
            for o in load(fn): ours[o["id"]] = o
        # 유령 id: 매핑 키가 실제 데이터에 없음 (병합/삭제 잔재)
        for k in mapping:
            if k not in ours:
                fail(f"[{ent}] 유령 매핑 id: '{k}' (데이터에 없음)")
        # 확정 항목 필드 + 중복 databank_id(오매핑 신호)
        seen = {}
        for k, v in mapping.items():
            if v.get("match_status") in ("exact", "verified"):
                if not v.get("databank_id"): fail(f"[{ent}:{k}] 확정인데 databank_id 없음")
                if not v.get("image_url"):   warn(f"[{ent}:{k}] 확정인데 image_url 없음")
                did = v.get("databank_id")
                if did:
                    if did in seen:
                        fail(f"[{ent}] 중복 databank_id(오매핑 의심): '{k}' ↔ '{seen[did]}'")
                    seen[did] = k
        # 순참조: 매핑 확정인데 데이터에 external_refs 미주입 (enrich 누락 검출)
        for k, v in mapping.items():
            if v.get("match_status") in ("exact", "verified") and v.get("databank_id"):
                o = ours.get(k)
                if o is not None and not (o.get("external_refs") or {}).get("databank"):
                    fail(f"[{ent}:{k}] 매핑 확정인데 external_refs 미주입 — enrich 실행 누락")
        # 역참조 일관성: 데이터의 external_refs.databank ⊂ 확정 매핑
        for oid, o in ours.items():
            er = (o.get("external_refs") or {}).get("databank")
            if not er: continue
            mv = mapping.get(oid, {})
            if mv.get("match_status") not in ("exact", "verified"):
                fail(f"[{ent}:{oid}] external_refs 있는데 매핑 미확정({mv.get('match_status')})")
            elif mv.get("databank_id") != er.get("id"):
                fail(f"[{ent}:{oid}] external_refs.id ≠ 매핑 databank_id")
            if er.get("credit") != "Star Wars Databank \u00a9 Lucasfilm Ltd.":
                fail(f"[{ent}:{oid}] credit 누락/불일치 — IMAGE_POLICY 위반")
            total_linked += 1
    print(f"  매핑 무결성 확인 — 공식 이미지 연결 {total_linked}건")

# ── 4) 관계 일관성: 핵심관계도(relationships.html) ⊂ relations.json ──
def stage_relations():
    path=os.path.join(DIR,"relationships.html")
    if not os.path.exists(path): return
    s=open(path,encoding="utf-8").read()
    links=re.findall(r'\{s:"(\w+)",t:"(\w+)",type:"(\w+)"\}',s)
    msm=re.search(r"const SHORTMAP=\{(.*?)\};",s,re.S)
    if not links or not msm:
        warn("핵심관계도 LINKS/SHORTMAP 파싱 실패 — 관계 일관성 검사 건너뜀"); return
    sm=dict(re.findall(r'(\w+):"([\w-]+)"',msm.group(1)))
    rel=load("relations.json")
    have={(r["s"],r["t"],r["type"]) for r in rel}|{(r["t"],r["s"],r["type"]) for r in rel}
    miss=[(sm.get(a),sm.get(b),t) for a,b,t in links if sm.get(a) and sm.get(b) and (sm[a],sm[b],t) not in have]
    if miss:
        for m in miss: fail(f"핵심관계도에만 있는 관계(원천 누락): {m}")
    print(f"  핵심관계도 {len(links)}개 관계 ⊆ relations.json 확인")

# ── 실행 ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("PREFLIGHT — 통합 사전검사")
    print("1) 데이터 무결성"); stage_validate()
    print("2) 페이지 JS 문법"); stage_js()
    print("3) 매핑 무결성");   stage_mapping()
    print("4) 관계 일관성");   stage_relations()
    print("─" * 48)
    for w in WARN: print(f"  ⚠️  {w}")
    if FAIL:
        for m in FAIL: print(f"  ❌ {m}")
        print(f"\n게이트: FAIL ❌ — 오류 {len(FAIL)} / 경고 {len(WARN)}")
        sys.exit(1)
    print(f"\n게이트: PASS ✅ — 오류 0 / 경고 {len(WARN)}")
    sys.exit(0)
