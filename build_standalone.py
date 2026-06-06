#!/usr/bin/env python3
"""
standalone 빌더 — fetch 구동 페이지를 데이터 인라인본으로 변환.
로직은 그대로 두고, 데이터(JSON)를 인라인으로 박은 뒤 fetch()를 가로채는
shim을 주입한다. 결과물은 서버 없이 file:// 더블클릭으로 작동한다.
사용: python3 build_standalone.py  →  standalone/ 폴더 생성
"""
import os,re,json,shutil

DIR=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(DIR,"standalone")
# 폴더 자체를 rmtree하면 일부 마운트에서 I/O 오류가 나므로, 폴더는 두고 내용만 비운다
os.makedirs(OUT, exist_ok=True)
for _n in os.listdir(OUT):
    _p=os.path.join(OUT,_n)
    try:
        shutil.rmtree(_p) if os.path.isdir(_p) else os.remove(_p)
    except OSError:
        pass

# 페이지별 필요한 JSON (fetch 분석 결과)
NEED={
 "character-detail.html":["characters","events","factions","locations","relations"],
 "event-detail.html":["characters","events","factions","locations"],
 "faction-detail.html":["characters","events","factions"],
 "film-detail.html":["characters","events","films","vehicles","starships","locations","factions"],
 "films.html":["characters","events","films"],
 "location-detail.html":["characters","events","locations"],
 "galaxy-network.html":["characters"],
 "vehicle-detail.html":["vehicles","characters","films"],
 "vehicles.html":["vehicles"],
 "starship-detail.html":["starships","characters","films"],
 "starships.html":["starships"],
 "validator.html":["characters","events","factions","locations","relations"],
 "search.html":["characters","films","events","locations","factions","vehicles","starships"],
 "eras.html":["films","events","characters","starships","factions"],
 "dashboard.html":["films","characters","events","relations","locations","factions","vehicles","starships"],
 "index.html":["films","characters","events","relations","locations","factions","vehicles","starships"],
}
# fetch 없이 더블클릭으로 이미 작동 (그대로 복사)
COPY=["timeline.html","relationships.html","silhouettes.html"]

# JSON 캐시
def jdata(name): return json.load(open(os.path.join(DIR,name+".json"),encoding='utf-8'))

def shim(files):
    data={f+".json":jdata(f) for f in files}
    blob=json.dumps(data,ensure_ascii=False,separators=(",",":"))
    return ('<script id="__standalone__">\n'
        'window.__SW_DATA__='+blob+';\n'
        '(function(){var orig=window.fetch?window.fetch.bind(window):null;'
        'window.fetch=function(u,o){var k=String(u).split("/").pop().split("?")[0];'
        'if(window.__SW_DATA__[k]!==undefined){var d=window.__SW_DATA__[k];'
        'return Promise.resolve({ok:true,status:200,'
        'json:function(){return Promise.resolve(d);},'
        'text:function(){return Promise.resolve(JSON.stringify(d));}});}'
        'return orig?orig(u,o):Promise.reject(new Error("offline:"+k));};})();\n'
        '</script>\n')

def inject(html,files):
    s=shim(files)
    # <body ...> 직후에 주입 (페이지 스크립트보다 먼저 정의)
    m=re.search(r'<body[^>]*>',html)
    if m: return html[:m.end()]+"\n"+s+html[m.end():]
    return s+html  # 안전장치

built=[]
for page,files in NEED.items():
    html=open(os.path.join(DIR,page),encoding='utf-8').read()
    out=inject(html,files)
    open(os.path.join(OUT,page),'w',encoding='utf-8').write(out)
    built.append((page,len(out),files))

for page in COPY:
    p=os.path.join(DIR,page)
    if os.path.exists(p):
        shutil.copy(p,os.path.join(OUT,page)); built.append((page,os.path.getsize(p),["(복사)"]))

# README
open(os.path.join(OUT,"_README.txt"),'w',encoding='utf-8').write(
 "스타워즈 캐넌 아카이브 — STANDALONE 빌드\n\n"
 "이 폴더의 HTML은 데이터를 내부에 품고 있어 서버 없이 더블클릭으로 열립니다.\n"
 "index.html 또는 timeline.html 부터 여세요.\n\n"
 "주의:\n"
 "- 웹폰트·D3·NASA 헤더 이미지는 인터넷 연결 시 로드됩니다(오프라인이면 기본 폰트/대체 배경으로 표시).\n"
 "- 데이터를 바꾸면 build_standalone.py 를 다시 실행해 이 폴더를 갱신하세요.\n")

print("standalone 빌드 완료 →", OUT)
for p,sz,fl in built:
    print(f"  {p:24} {sz/1024:6.1f} KB  {'+'.join(fl)}")
