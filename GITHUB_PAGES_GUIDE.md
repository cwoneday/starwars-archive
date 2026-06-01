# GitHub Pages 배포 가이드 — 스타워즈 캐넌 아카이브

> 로컬 서버 없이, 누구나 URL로 접속할 수 있게 무료 호스팅하기.
> fetch 방식(상세 페이지)이 **그대로 작동**합니다 — 실제 http로 서빙되니까요.

배포 방법은 두 가지입니다. **터미널이 익숙하지 않으면 방법 A(웹 업로드)** 를 권합니다.
명령어가 편하면 방법 B(git)로 가세요. 결과는 같습니다.

---

## 0. 준비물

1. **GitHub 계정** — github.com 에서 무료 가입 (이미 있으면 그대로 사용).
2. **업로드할 파일들** — 이 폴더(`/mnt/user-data/outputs`)에서 받은 파일.

### 올려야 할 파일 (사이트 필수)

HTML (8개)
```
index.html            ← 진입점(타임라인으로 자동 이동)
timeline.html         ← 마스터 타임라인 (사실상 홈)
event-detail.html     ← 사건 상세 (데이터 구동)
galaxy-network.html   ← 82인 관계망 (줌 실루엣)
relationships.html    ← 22인 핵심 관계도
location-detail.html  ← 장소 상세
faction-detail.html   ← 세력 상세
silhouettes.html      ← 실루엣 라이브러리
```

JSON 데이터 (4개)
```
events.json  characters.json  locations.json  factions.json
```

> **중요:** 위 파일은 **모두 같은 폴더(저장소 루트)** 에 평평하게 둬야 합니다.
> 페이지들이 `fetch("events.json")`, `event-detail.html?id=...` 처럼 **상대경로**로 서로를
> 부르기 때문에, 폴더를 나누면 링크가 깨집니다.

### 올려도 되고 안 올려도 되는 파일 (선택)

- `event-battle-of-yavin.html` — 초기 프로토타입(지금은 `event-detail.html?id=battle-of-yavin`로 대체). 안 올려도 됩니다.
- `*.md` 설계 문서들(`EVENTS_SCHEMA.md` 등) — 사이트 동작과 무관. 기록용으로 같이 올려도 무방.

---

## 방법 A — 웹 브라우저로 업로드 (터미널 불필요, 추천)

### A-1. 새 저장소 만들기
1. github.com 로그인 → 우측 상단 **`+`** → **New repository**
2. **Repository name**: `starwars-archive` (원하는 이름)
3. **Public** 선택 *(Pages 무료 사용 조건. 팬 아카이브라 공개해도 무방)*
4. "Add a README" 체크 **해제** (그냥 비워두기)
5. **Create repository** 클릭

### A-2. 파일 업로드
1. 방금 만든 저장소 화면에서 **`uploading an existing file`** 링크 클릭
   *(또는 **Add file → Upload files**)*
2. 위 "사이트 필수" 파일 **12개를 전부** 드래그&드롭
   *(html 8개 + json 4개 — 한 번에 끌어다 놓아도 됩니다)*
3. 아래 **Commit changes** 버튼 클릭

> 파일이 많아 한 번에 안 올라가면 나눠서 올려도 됩니다. 단, **반드시 루트(최상위)** 에.
> 폴더 안으로 들어가지 않도록 주의.

### A-3. Pages 켜기
1. 저장소 상단 **Settings** 탭
2. 왼쪽 메뉴 **Pages**
3. **Build and deployment → Source**: `Deploy from a branch` 선택
4. **Branch**: `main` / 폴더 `/ (root)` 선택 → **Save**
5. 페이지 상단에 잠시 후 주소가 뜹니다(1~10분 소요).

### A-4. 접속
```
https://(내아이디).github.io/starwars-archive/
```
→ 자동으로 타임라인이 뜨고, 사건·인물·장소·세력이 전부 링크로 연결됩니다.
상세 페이지의 "데이터 불러오기 실패" 안내도 **더는 안 뜹니다.**

---

## 방법 B — git 명령어 (개발자용)

로컬에 파일이 있고 git이 설치돼 있다면:

```bash
# 1) 파일이 있는 폴더로 이동
cd 스타워즈-파일-폴더

# 2) git 저장소 초기화
git init
git branch -M main

# 3) 전체 추가 & 커밋
git add .
git commit -m "스타워즈 캐넌 아카이브 초기 배포"

# 4) GitHub 원격 연결 (저장소는 github.com에서 미리 생성)
git remote add origin https://github.com/(내아이디)/starwars-archive.git

# 5) 푸시
git push -u origin main
```

그 뒤 **방법 A-3(Pages 켜기)** 와 동일하게 Settings → Pages에서 활성화.

---

## 수정·갱신하는 법

데이터(JSON)나 페이지(HTML)를 고치면, 다시 올리기만 하면 됩니다.

- **웹 방식:** 저장소에서 해당 파일 클릭 → 연필(Edit) 아이콘 → 수정 → Commit.
  또는 **Add file → Upload files** 로 새 버전 덮어쓰기.
- **git 방식:** `git add . && git commit -m "수정" && git push`

올리면 **1~2분 내 자동 재배포**됩니다. (JSON만 고쳐도 모든 페이지가 따라 바뀜 — 헌법 제2조의 효과.)

---

## 자주 막히는 곳 (체크리스트)

| 증상 | 원인 / 해결 |
| --- | --- |
| 주소 열었더니 404 | 배포에 몇 분 걸립니다. 5~10분 뒤 새로고침. Pages가 `main / root`로 켜졌는지 확인. |
| 타임라인은 뜨는데 상세에서 "데이터 불러오기 실패" | JSON 4개가 **루트에 같이** 올라갔는지 확인. 폴더 안에 있으면 fetch 경로가 안 맞음. |
| 링크 클릭 시 404 | 파일명 대소문자 확인. GitHub Pages는 **대소문자 구분**. 우리 파일명은 전부 소문자라 그대로면 OK. |
| 바뀐 내용이 안 보임 | 브라우저 캐시. **강력 새로고침**(Ctrl/Cmd+Shift+R). |
| 실루엣/관계망이 안 그려짐 | 인터넷 연결 확인 — D3, 폰트는 CDN에서 불러옵니다(차단 환경이면 안 보일 수 있음). |

---

## 알아두면 좋은 점

- **비용 0원.** 공개 저장소 + GitHub Pages는 무료.
- **공개 범위.** Public 저장소라 코드·데이터가 공개됩니다. 스타워즈 팬 아카이브엔 문제 없지만, 비공개로 두려면 Pages를 쓰려 GitHub Pro가 필요합니다.
- **저장소 이름을 `(내아이디).github.io`** 로 만들면 주소가 `https://(내아이디).github.io/` 로 더 짧아집니다(하위경로 없음). 다른 사이트도 올릴 계획이면 일반 이름(`starwars-archive`)이 깔끔합니다.
- **커스텀 도메인**(예: `myarchive.com`)도 Settings → Pages에서 연결 가능. 지금은 불필요.
- **D3·웹폰트는 CDN**(cdnjs, google fonts)에서 로드되므로, 완전 오프라인 보관이 필요하면 별도로 "방법 2: standalone 빌드"를 쓰세요.

---

## 한눈에 보는 최단 경로

```
github.com 가입/로그인
   └─ New repository (Public, 이름: starwars-archive)
        └─ Add file → Upload files → 12개 드래그 → Commit
             └─ Settings → Pages → main / root → Save
                  └─ 몇 분 뒤  https://(아이디).github.io/starwars-archive/  접속 ✔
```
