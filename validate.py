#!/usr/bin/env python3
"""
스타워즈 캐넌 아카이브 — 데이터 거버넌스 검증기
schema-validator(구조) + canon-auditor(출처·확정도) 를 한 파일로.
헌법: 제2조(공유 스키마)·제4조(id 참조)·제5조(확정/추론 구분).
사용: python3 validate.py        (실패 시 종료코드 1)
"""
import json, sys, os
from collections import Counter, defaultdict

DIR=os.path.dirname(os.path.abspath(__file__))
def load(n): return json.load(open(os.path.join(DIR,n),encoding='utf-8'))

events=load('events.json'); chars=load('characters.json')
locs=load('locations.json'); facs=load('factions.json'); rels=load('relations.json')
creatures=load('creatures.json') if os.path.exists(os.path.join(DIR,'creatures.json')) else []
try:
    films=load('films.json')
except FileNotFoundError:
    films=[]
try:
    vehicles=load('vehicles.json')
except FileNotFoundError:
    vehicles=[]
try:
    starships=load('starships.json')
except FileNotFoundError:
    starships=[]

ERR=[]; WARN=[]; INFO=[]
def err(m): ERR.append(m)
def warn(m): WARN.append(m)
def info(m): INFO.append(m)

# ---- 허용 enum (헌법 표준) ----
ERA={"dawn_of_the_jedi","high_republic","fall_of_the_jedi","reign_of_the_empire","age_of_rebellion","new_republic","rise_of_the_first_order","new_jedi_order"}
CATEGORY={"battle","duel","politics","mission","founding","fall","discovery","treaty","other"}
TIER={1,2,3}
CERT={"exact","approximate","disputed"}
CANON={"explicit","referenced","inferred"}
STYPE={"film","series","novel","comic","game"}
ALIGN={"light","dark","neutral"}
ARCH={"jedi","sith","droid","trooper","pilot","bounty-hunter","bounty","royalty-politician","royal","creature","civilian"}
GENDER={"male","female","droid","none","other","n/a","hermaphrodite"}
RELTYPE={"family","master","ally","rival"}

# ---- id 집합 ----
ev_ids={e['id'] for e in events}
ch_ids={c['id'] for c in chars}
loc_ids={l['id'] for l in locs}
fac_ids={f['id'] for f in facs}

def dup_check(rows,label):
    ids=[r['id'] for r in rows]
    for k,n in Counter(ids).items():
        if n>1: err(f"[{label}] 중복 id: {k} ({n}회)")

# ================= schema-validator =================
dup_check(events,'events'); dup_check(chars,'characters'); dup_check(locs,'locations'); dup_check(facs,'factions')

# events
EV_REQ=["id","title","title_en","era","year_value","year_certainty","category","tier","characters","locations","factions","source","source_type","canon_status","one_liner","summary","preceded_by","followed_by"]
for e in events:
    for f in EV_REQ:
        if f not in e: err(f"[events:{e.get('id','?')}] 필수 필드 누락: {f}")
    if e.get('era') not in ERA: err(f"[events:{e['id']}] era enum 위반: {e.get('era')}")
    if e.get('category') not in CATEGORY: err(f"[events:{e['id']}] category enum 위반: {e.get('category')}")
    if e.get('tier') not in TIER: err(f"[events:{e['id']}] tier 위반: {e.get('tier')}")
    if e.get('year_certainty') not in CERT: err(f"[events:{e['id']}] year_certainty 위반: {e.get('year_certainty')}")
    if e.get('canon_status') not in CANON: err(f"[events:{e['id']}] canon_status 위반: {e.get('canon_status')}")
    if e.get('source_type') not in STYPE: err(f"[events:{e['id']}] source_type 위반: {e.get('source_type')}")
    for cid in e.get('characters',[]):
        if cid not in ch_ids: err(f"[events:{e['id']}] 깨진 인물 참조: {cid}")
    for lid in e.get('locations',[]):
        if lid not in loc_ids: err(f"[events:{e['id']}] 깨진 장소 참조: {lid}")
    for fid in e.get('factions',[]):
        if fid not in fac_ids: err(f"[events:{e['id']}] 깨진 세력 참조: {fid}")
    for k in ('preceded_by','followed_by'):
        for x in e.get(k,[]):
            if x not in ev_ids: err(f"[events:{e['id']}] {k} 깨진 참조: {x}")
    # 확장 필드 (구조화 + 서술) — 있으면 검증
    if 'belligerents' in e:
        b=e['belligerents']
        if not isinstance(b,dict) or 'side_a' not in b or 'side_b' not in b:
            err(f"[events:{e['id']}] belligerents 형식 오류(side_a/side_b 필요)")
        else:
            for side in ('side_a','side_b'):
                for fid in b.get(side,[]):
                    if fid not in fac_ids: err(f"[events:{e['id']}] belligerents {side} 깨진 세력: {fid}")
                    elif fid not in e.get('factions',[]): warn(f"[events:{e['id']}] belligerents {side} 세력 {fid} 이 factions 목록에 없음")
    for kf in e.get('key_figures',[]):
        if kf not in ch_ids: err(f"[events:{e['id']}] key_figures 깨진 인물: {kf}")
        elif kf not in e.get('characters',[]): warn(f"[events:{e['id']}] key_figures {kf} 이 characters 목록에 없음")
    for dd in e.get('deep_dive',[]):
        if 'phase' not in dd or 'note' not in dd: err(f"[events:{e['id']}] deep_dive 항목 형식 오류(phase/note 필요)")
    # tier1 인데 깊은 서술(deep_dive) 없으면 안내
    if e.get('tier')==1 and not e.get('deep_dive'): info(f"[커버리지] tier1 사건 deep_dive 미작성: {e['id']}")

# characters
for c in chars:
    if c.get('alignment') not in ALIGN|{None}: err(f"[characters:{c['id']}] alignment 위반: {c.get('alignment')}")
    if c.get('tier') not in TIER: err(f"[characters:{c['id']}] tier 위반: {c.get('tier')}")
    if c.get('gender') not in GENDER: warn(f"[characters:{c['id']}] gender 비표준: {c.get('gender')}")
    if c.get('era_primary') not in ERA|{None}: err(f"[characters:{c['id']}] era_primary 위반: {c.get('era_primary')}")
    arch=c.get('portrait',{}).get('archetype')
    if arch not in ARCH|{None}: err(f"[characters:{c['id']}] archetype 위반: {arch}")
    er=(c.get('external_refs') or {}).get('databank')
    if er:
        if not er.get('id'): err(f"[characters:{c['id']}] external_refs.databank.id 누락")
        if not str(er.get('image_url') or '').startswith('http'): warn(f"[characters:{c['id']}] databank image_url 비정상")
        if not er.get('credit'): err(f"[characters:{c['id']}] databank credit(출처 표기) 누락 — IMAGE_POLICY 위반")
    if c.get('canon_status') not in CANON: err(f"[characters:{c['id']}] canon_status 위반: {c.get('canon_status')}")
    hw=c.get('homeworld')
    if hw and hw not in loc_ids: err(f"[characters:{c['id']}] homeworld 깨진 참조: {hw}")
    for a in c.get('affiliation_history',[]):
        if a['faction'] not in fac_ids: err(f"[characters:{c['id']}] affiliation 깨진 세력: {a['faction']}")
        for k in ('from_event','to_event'):
            if a.get(k) and a[k] not in ev_ids: err(f"[characters:{c['id']}] affiliation {k} 깨진 사건: {a[k]}")
    for fld in ('arc','key_choices'):
        for b in c.get(fld,[]):
            if b.get('event') and b['event'] not in ev_ids: err(f"[characters:{c['id']}] {fld} 깨진 사건: {b['event']}")

# locations / factions
def chk_extref(kind,o):
    er=(o.get('external_refs') or {}).get('databank')
    if er:
        if not er.get('id'): err(f"[{kind}:{o['id']}] external_refs.databank.id 누락")
        if not str(er.get('image_url') or '').startswith('http'): warn(f"[{kind}:{o['id']}] databank image_url 비정상")
        if not er.get('credit'): err(f"[{kind}:{o['id']}] databank credit(출처 표기) 누락 — IMAGE_POLICY 위반")

for l in locs:
    if l.get('canon_status') not in CANON: err(f"[locations:{l['id']}] canon_status 위반: {l.get('canon_status')}")
    if l.get('source_type') not in STYPE: warn(f"[locations:{l['id']}] source_type 비표준: {l.get('source_type')}")
    chk_extref('locations',l)
for f in facs:
    if f.get('alignment') not in ALIGN: err(f"[factions:{f['id']}] alignment 위반: {f.get('alignment')}")
    if f.get('canon_status') not in CANON: err(f"[factions:{f['id']}] canon_status 위반: {f.get('canon_status')}")
    chk_extref('factions',f)
# creatures (생물 축)
for cr in creatures:
    if 'id' not in cr or 'name' not in cr: err(f"[creatures:{cr.get('id','?')}] 필수 필드 누락")
    if cr.get('homeworld') and cr['homeworld'] not in loc_ids: err(f"[creatures:{cr['id']}] homeworld 깨진 장소 참조: {cr['homeworld']}")
    if cr.get('canon_status') not in CANON: err(f"[creatures:{cr['id']}] canon_status 위반: {cr.get('canon_status')}")
    chk_extref('creatures',cr)

# relations
for i,r in enumerate(rels):
    if r.get('type') not in RELTYPE: err(f"[relations#{i}] type 위반: {r.get('type')}")
    for k in ('s','t'):
        if r.get(k) not in ch_ids: err(f"[relations#{i}] 깨진 인물 참조({k}): {r.get(k)}")
    if r.get('s')==r.get('t'): warn(f"[relations#{i}] 자기 자신 관계: {r.get('s')}")

# ================= films (작품 축) =================
WORKTYPE={"film","series","novel","comic","game"}
TRILOGY={"prequel","original","sequel","none"}
film_ids={f['id'] for f in films}
dup_check(films,'films')
FILM_REQ=["id","title","title_en","work_type","summary","source_type","canon_status"]
for f in films:
    for k in FILM_REQ:
        if k not in f: err(f"[films:{f.get('id','?')}] 필수 필드 누락: {k}")
    if f.get('work_type') not in WORKTYPE: err(f"[films:{f['id']}] work_type 위반: {f.get('work_type')}")
    if f.get('trilogy') and f.get('trilogy') not in TRILOGY: warn(f"[films:{f['id']}] trilogy 비표준: {f.get('trilogy')}")
    if f.get('canon_status') not in CANON: err(f"[films:{f['id']}] canon_status 위반: {f.get('canon_status')}")
    if f.get('source_type') not in STYPE: err(f"[films:{f['id']}] source_type 위반: {f.get('source_type')}")
    if f.get('era_primary') and f.get('era_primary') not in ERA: err(f"[films:{f['id']}] era_primary 위반: {f.get('era_primary')}")
# 생물 works 링크 정합성
for cr in creatures:
    for w in cr.get('works',[]):
        if w not in film_ids: err(f"[creatures:{cr['id']}] works 깨진 작품 참조: {w}")
# 사건 work 링크 정합성
for e in events:
    if e.get('work') and e['work'] not in film_ids:
        err(f"[events:{e['id']}] work 깨진 작품 참조: {e['work']}")
# 인물 works 링크 정합성
for c in chars:
    for w in c.get('works',[]):
        if film_ids and w not in film_ids:
            warn(f"[characters:{c['id']}] works 미등록 작품 slug: {w}")

# ================= vehicles (탈것 축) =================
dup_check(vehicles,'vehicles')
char_ids_v={c['id'] for c in chars}
for v in vehicles:
    if 'id' not in v or 'name' not in v: err(f"[vehicles:{v.get('id','?')}] 필수 필드 누락")
    for fi in v.get('films',[]):
        if fi not in film_ids: err(f"[vehicles:{v['id']}] films 깨진 작품 참조: {fi}")
    for p in v.get('pilots',[]):
        if p not in char_ids_v: err(f"[vehicles:{v['id']}] pilots 깨진 인물 참조: {p}")
    if v.get('affiliation') and v["affiliation"] not in fac_ids:
        err(f"[vehicles:{v['id']}] affiliation 깨진 세력 참조: {v['affiliation']}")
    if v.get('canon_status') and v['canon_status'] not in CANON:
        err(f"[vehicles:{v['id']}] canon_status 위반: {v['canon_status']}")
    chk_extref('vehicles',v)

# ================= starships (함선 축) =================
dup_check(starships,'starships')
for v in starships:
    if 'id' not in v or 'name' not in v: err(f"[starships:{v.get('id','?')}] 필수 필드 누락")
    for fi in v.get('films',[]):
        if fi not in film_ids: err(f"[starships:{v['id']}] films 깨진 작품 참조: {fi}")
    for p in v.get('pilots',[]):
        if p not in char_ids_v: err(f"[starships:{v['id']}] pilots 깨진 인물 참조: {p}")
    if v.get('affiliation') and v['affiliation'] not in fac_ids:
        err(f"[starships:{v['id']}] affiliation 깨진 세력 참조: {v['affiliation']}")
    if v.get('canon_status') and v['canon_status'] not in CANON:
        err(f"[starships:{v['id']}] canon_status 위반: {v['canon_status']}")
    chk_extref('starships',v)

# 고아 데이터 (어디서도 참조 안 됨)
ref_loc=set(); ref_fac=set(); ref_ch=set()
for e in events:
    ref_loc|=set(e.get('locations',[])); ref_fac|=set(e.get('factions',[])); ref_ch|=set(e.get('characters',[]))
for c in chars:
    if c.get('homeworld'): ref_loc.add(c['homeworld'])
    for a in c.get('affiliation_history',[]): ref_fac.add(a['faction'])
for r in rels: ref_ch.add(r['s']); ref_ch.add(r['t'])
for l in loc_ids-ref_loc: info(f"[고아] 장소 미참조: {l}")
for f in fac_ids-ref_fac: info(f"[고아] 세력 미참조: {f}")
for c in ch_ids-ref_ch: info(f"[고아] 인물 미참조(관계·사건 어디에도 없음): {c}")

# ================= canon-auditor =================
# 연대 체인 정합성 (preceded/followed 상호 일치)
byid={e['id']:e for e in events}
for e in events:
    for nxt in e.get('followed_by',[]):
        if nxt in byid and e['id'] not in byid[nxt].get('preceded_by',[]):
            warn(f"[연대체인] {e['id']} → {nxt} 이지만 역방향 preceded_by 불일치")
# 추론을 확정처럼 쓰지 않는지: inferred인데 year_certainty exact 면 주의
for e in events:
    if e.get('canon_status')=='inferred' and e.get('year_certainty')=='exact':
        warn(f"[제5조] {e['id']}: canon=inferred 인데 연대=exact (추론을 확정처럼 표기)")

# ================= 커버리지 리포트 =================
nar=sum(1 for c in chars if c.get('motivation'))
aff=sum(1 for c in chars if c.get('affiliation_history'))
arc=sum(1 for c in chars if c.get('arc'))
info(f"[커버리지] 인물 심층서사(동기): {nar}/{len(chars)}")
info(f"[커버리지] 인물 소속 기록: {aff}/{len(chars)}")
info(f"[커버리지] 인물 변화(arc): {arc}/{len(chars)}")
info(f"[커버리지] 사건 canon: " + ", ".join(f"{k}={v}" for k,v in Counter(e['canon_status'] for e in events).items()))
linked=sum(1 for e in events if e.get("work"))
info(f"[커버리지] 작품 연결 사건: {linked}/{len(events)}")
info(f"[커버리지] 작품(films): {len(films)}편")
info(f"[커버리지] 탈것(vehicles): {len(vehicles)}종 (조종사연결 "+str(sum(1 for v in vehicles if v.get('pilots')))+", 소속 "+str(sum(1 for v in vehicles if v.get('affiliation')))+")")
info(f"[커버리지] 함선(starships): {len(starships)}종 (조종사연결 "+str(sum(1 for v in starships if v.get('pilots')))+", 소속 "+str(sum(1 for v in starships if v.get('affiliation')))+")")
info(f"[규모] events={len(events)} characters={len(chars)} locations={len(locs)} factions={len(facs)} relations={len(rels)}")

# ================= 출력 =================
print("="*54)
print(" 스타워즈 캐넌 아카이브 · 데이터 거버넌스 감사")
print("="*54)
def block(title,items,sym):
    print(f"\n{sym} {title} ({len(items)})")
    for m in items: print(f"   {m}")
block("ERROR (반드시 수정)",ERR,"❌")
block("WARNING (검토 권장)",WARN,"⚠️ ")
block("INFO (리포트)",INFO,"ℹ️ ")
print("\n"+"-"*54)
verdict = "PASS ✅ — 구조 오류 없음" if not ERR else f"FAIL ❌ — 오류 {len(ERR)}건"
print(f" 판정: {verdict}  |  경고 {len(WARN)}  정보 {len(INFO)}")
print("-"*54)
sys.exit(1 if ERR else 0)
