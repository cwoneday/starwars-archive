# 스타워즈 캐넌 아카이브 (Star Wars Canon Archive)

> 인물·사건·장소·세력·작품·함선·탈것·생물 — **8축 데이터가 서로를 참조하는 한국어 스타워즈 대서사 아카이브.**
> 단순 백과가 아니라, "누가 · 언제 · 어디서 · 왜"가 인과사슬로 연결된 **관계형 캐넌 데이터베이스**입니다.

🔗 **라이브 사이트**: https://cwoneday.github.io/starwars-archive/

---

## 한눈에 보기

| 축 | 규모 | 공식 이미지 연결 |
| --- | --- | --- |
| 인물 (characters) | 187명 | 148 (79%) |
| 사건 (events) | 74건 — 인과사슬 연결 | — |
| 장소 (locations) | 111곳 — 캐넌 격자좌표(A~S/1~26) | 68 (61%) |
| 세력 (factions) | 19개 | 15 (79%) |
| 작품 (films/series) | 34편 | — |
| 함선 (starships) | 46척 | 38 (83%) |
| 탈것 (vehicles) | 41종 | 28 (68%) |
| 생물 (creatures) | 18종 | 18 (100%) |
| **관계 (relations)** | **275개** — 혈연·사제·동맹·적대 타입 분류 | — |

공식 이미지·출처는 [Star Wars Databank](https://www.starwars.com/databank) 연동 — 합계 **315/422 (75%)**, 전 항목 출처 캡션 표기.

## 무엇이 다른가

1. **관계가 1급 데이터** — 인물은 고립된 카드가 아니라 사건의 참여자이고, 사건은 다른 사건의 원인이며, 장소는 사건과 출신 인물로 역참조됩니다. "아나킨" 페이지에서 출발해 클릭만으로 오더 66 → 만달로어 공성전 → 아소카로 이어지는 서사를 따라갈 수 있습니다.
2. **8개 시대 체계** — 제다이의 여명부터 뉴 제다이 오더까지, 모든 항목이 시대(era)에 귀속되어 시대 허브에서 교차 탐색됩니다.
3. **시간·관계·공간 3축 탐색** — 같은 데이터를 연대기(타임라인)·관계망·은하 지도(2D/3D) 세 방향에서 동시에 항해합니다.
4. **신작 캐넌 추적** — 안도르 S2, 애콜라이트, 만달로리안, 오비완 케노비, 반란군까지 디즈니+ 시리즈의 인물·사건이 영화 캐넌과 같은 격자 안에 통합되어 있습니다.
5. **정직한 공백 원칙** — 캐넌에서 확인되지 않는 정보는 추정으로 채우지 않고 비워둡니다(거버넌스 제5조). 출신 행성이 null인 요다는, 그것이 캐넌의 사실이기 때문입니다.

## 주요 페이지

| 페이지 | 설명 |
| --- | --- |
| `index.html` | 랜딩 — 전역 검색 + 추천 카드 |
| `search.html` | 8개 엔티티 통합 검색 (`?q=` 지원) |
| `timeline.html` | 연대기 — 사건 인과사슬 |
| `eras.html` | 8시대 허브 (작품·사건·인물·세력·함선 교차) |
| `galaxy-map.html` / `galaxy-map-3d.html` | 은하 지도 — 캐넌 격자좌표(A~S/1~26) 2D·3D, 세력 오로라, NASA 배경 |
| `relationships.html` / `relationships-3d.html` | 핵심 인물 관계도 (2D / Three.js 3D) |
| `galaxy-network.html` | 전체 인물 관계망 |
| `dashboard.html` | 통계 — 규모·분포·데이터뱅크 연결률 |
| `films.html` · `starships.html` · `vehicles.html` · `creatures.html` | 작품·함선·탈것·생물 도감 |

## 빠른 시작

정적 사이트라 서버가 필요 없습니다. 다만 JSON `fetch` 때문에 로컬에선 간이 서버를 띄워야 합니다:

```bash
git clone https://github.com/cwoneday/starwars-archive.git
cd starwars-archive
python3 -m http.server 8000
# → http://localhost:8000
```

오프라인 단일 파일이 필요하면 `python3 build_standalone.py`.
은하 지도 배경(선택)은 [`assets/README.md`](assets/README.md) 참조.

## 데이터 구조

모든 데이터는 사람이 읽을 수 있는 JSON입니다. id 기반 교차참조이므로 **모든 엔티티는 JSON 자체가 곧 공개 API**입니다 — 자유롭게 fetch해서 쓰셔도 됩니다. 상세 스키마는 스키마 문서를 참조하세요.

## 품질 게이트

- `validate.py` — id·enum·중복·고아 참조·인과사슬·이미지 정책 자동 검사 (현재 **PASS: 오류 0 / 경고 0**)
- `preflight.py` — 데이터 무결성 + 전 페이지 JS 문법 + 데이터뱅크 매핑 무결성 통합 게이트
- `.github/workflows/preflight.yml` — 푸시·PR마다 게이트 자동 실행 (CI)
- `.github/workflows/sync-databank.yml` — 주간 데이터뱅크 `external_refs` 갱신 PR 자동 생성
- `AGENT_CONSTITUTION.md` — 데이터 거버넌스 헌법 (출처 의무·공백의 정직성·점진적 변경 원칙)

## 개선 나침반 (로드맵)

매니아의 체류 동선을 강화하는 방향:

1. **인프라 정직성** — CI 워크플로 정상화, `.gitignore`로 cache/ 배포 제외, About/토픽 설정 *(진행 중)*
2. **인물별 개인 연대기 뷰** — 한 인물의 일생을 사건 순으로 (`appears_in` 활용)
3. **캐넌 근거 각주 강화** — 상세 페이지에 "근거: 작품·화수" 노출로 검증 아카이브 정체성 확립
4. **관계 경로 탐색기** — 두 인물 사이 최단 관계 경로 + 공유 URL
5. **유물(Artifacts) 9번째 축** — 다크세이버 계보·라이트세이버 이동 경로
6. **시청 가이드** — 공개순·연대기순·입문 코스

## 저작권 안내

- 본 프로젝트는 **비상업 팬 아카이브**입니다. Star Wars는 Lucasfilm Ltd. / The Walt Disney Company의 자산입니다.
- 공식 이미지는 Star Wars Databank를 출처 캡션과 함께 참조하며, 정책은 [`IMAGE_POLICY.md`](IMAGE_POLICY.md)를 따릅니다. 권리자 요청 시 즉시 제거합니다.
- 데이터(JSON)의 서술문은 자체 작성·재구성 텍스트입니다.

## 기여

오류 제보·캐넌 보강 제안은 [Issues](../../issues)로 환영합니다. 데이터 PR 시 `python3 preflight.py` 통과가 머지 조건입니다.

---

*"The Force will be with you. Always."*
