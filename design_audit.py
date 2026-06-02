#!/usr/bin/env python3
"""
스타워즈 캐넌 아카이브 — 시각 일관성 감사 (design-auditor)
데이터 검증기(validate.py)의 시각 버전. 전 페이지가 공유 디자인 토큰·폰트·
네비게이션·기본 메타를 일관되게 지키는지 정적 분석한다.
사용: python3 design_audit.py   (FAIL 시 종료코드 1)
"""
import os, re, sys
DIR=os.path.dirname(os.path.abspath(__file__))

# 감사 대상: 사이트 페이지 (index 리디렉션·sample 데모 제외)
PAGES=["timeline.html","event-detail.html","character-detail.html","location-detail.html",
       "faction-detail.html","galaxy-network.html","relationships.html","silhouettes.html","validator.html"]

# 헌법적 디자인 토큰 (홀로그램 아카이브)
HOLO="#45d4e3"      # 홀로 시안 액센트
VOID="#04060b"      # 딥 보이드 배경
FONTS=["Chakra Petch","Spline Sans","JetBrains Mono"]
NAVLINKS=["timeline.html","galaxy-network.html","relationships.html","silhouettes.html"]

ERR=[];WARN=[];INFO=[]
def err(m):ERR.append(m)
def warn(m):WARN.append(m)
def info(m):INFO.append(m)

present={}  # 토큰별 보유 페이지 수
for f in PAGES:
    p=os.path.join(DIR,f)
    if not os.path.exists(p): err(f"[{f}] 파일 없음"); continue
    s=open(p,encoding='utf-8').read()
    # 1) 핵심 색 토큰
    if VOID not in s: warn(f"[{f}] 딥 보이드 배경({VOID}) 미사용 — 배경 톤 불일치 가능")
    else: present['void']=present.get('void',0)+1
    if HOLO not in s: warn(f"[{f}] 홀로 시안 액센트({HOLO}) 없음")
    else: present['holo']=present.get('holo',0)+1
    # 2) 폰트 3종
    for fam in FONTS:
        if fam.replace(" ","+") not in s and fam not in s:
            warn(f"[{f}] 폰트 '{fam}' 미로드")
    # 3) 네비게이션 바
    n=s.count('class="site-nav"')
    if n==0: err(f"[{f}] 네비게이션 바 없음")
    elif n>1: warn(f"[{f}] 네비게이션 바 중복({n}개)")
    else: present['nav']=present.get('nav',0)+1
    # 4) 네비 링크 4종
    if n>=1:
        navseg=s[s.find('class="site-nav"'):s.find('class="site-nav"')+800]
        for link in NAVLINKS:
            if link not in navseg: warn(f"[{f}] 네비에 '{link}' 링크 누락")
    # 5) 기본 메타
    if 'charset' not in s: warn(f"[{f}] meta charset 누락")
    if 'viewport' not in s: warn(f"[{f}] meta viewport 누락")
    if '<title' not in s: warn(f"[{f}] <title> 누락")

info(f"[커버리지] 감사 페이지: {len(PAGES)}")
info(f"[커버리지] 딥 보이드 배경: {present.get('void',0)}/{len(PAGES)}")
info(f"[커버리지] 홀로 액센트: {present.get('holo',0)}/{len(PAGES)}")
info(f"[커버리지] 네비게이션 바: {present.get('nav',0)}/{len(PAGES)}")

print("="*54)
print(" 스타워즈 캐넌 아카이브 · 시각 일관성 감사")
print("="*54)
def block(t,items,sym):
    print(f"\n{sym} {t} ({len(items)})")
    for m in items: print(f"   {m}")
block("ERROR (반드시 수정)",ERR,"❌")
block("WARNING (검토 권장)",WARN,"⚠️ ")
block("INFO (리포트)",INFO,"ℹ️ ")
print("\n"+"-"*54)
print(f" 판정: {'PASS ✅ — 시각 일관성 이상 없음' if not ERR else f'FAIL ❌ — 오류 {len(ERR)}건'}  |  경고 {len(WARN)}  정보 {len(INFO)}")
print("-"*54)
sys.exit(1 if ERR else 0)
