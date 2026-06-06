#!/usr/bin/env python3
"""Star Wars Databank API 수집기 — 회원님 로컬 PC에서 실행하는 스크립트.

사용법:
  python3 scripts/fetch_databank.py              # 7종 전체 수집
  python3 scripts/fetch_databank.py characters   # 특정 타입만

출력: cache/databank_raw/{type}.json  (해당 타입 전체 항목 배열)

주의:
- Render 무료 서버라 첫 요청에 콜드 스타트 지연(5~30초)이 있을 수 있음.
- 수집물(영문 description)은 캐시 전용. 사이트에 원문 노출 금지(헌법 제6조).
"""
import json, os, sys, time
import urllib.request

BASE = "https://starwars-databank-server.onrender.com/api/v1"
TYPES = ["characters", "creatures", "droids", "locations", "organizations", "species", "vehicles"]
OUT = "cache/databank_raw"

def get(url, retries=5):
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            wait = 2 ** i
            print(f"  재시도 {i+1}/{retries} ({e}) — {wait}s 대기")
            time.sleep(wait)
    raise SystemExit(f"수집 실패: {url}")

def fetch_type(t):
    print(f"[{t}] 수집 시작")
    items, page = [], 1
    while True:
        d = get(f"{BASE}/{t}?page={page}&limit=100")
        items += d["data"]
        total = d["info"]["total"]
        print(f"  p{page}: 누적 {len(items)}/{total}")
        if not d["info"].get("next"):
            break
        page += 1
        time.sleep(0.4)  # 서버 예의
    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/{t}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"✓ {path} ({len(items)}건)\n")

if __name__ == "__main__":
    for t in (sys.argv[1:] or TYPES):
        fetch_type(t)
    print("완료. cache/databank_raw/ 폴더를 아카이브 작업 환경에 업로드하세요.")
