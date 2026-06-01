# characters.json — 인물 마스터 스키마 정의서

> **인물 축의 공유 계약** (헌법 제2조). 인물 프로파일러가 소유하며, events.json에
> 매달리는 핵심 축. 사실 정보는 출처(SWAPI 등)에서, 서사·심리는 자기 언어로(제6조).
>
> 표기: **R** 필수 / **O** 선택 · `owner` = 채우는 주체(`AGENT_ROSTER.md`)
> 원칙: 사실(factual)과 추론·서사(curated)를 분리하고, 비운 칸을 확정으로 읽지 않는다(제5조).

---

## 1. 식별 (Identification)

| 필드 | 타입 | R/O | 규칙 | 예시 | owner |
| --- | --- | --- | --- | --- | --- |
| `id` | string | R | 소문자 영문 kebab-slug, 전역 유일 | `"luke-skywalker"` | orchestrator |
| `name` | string | R | 한국어 표시명 | `"루크 스카이워커"` | 인물 프로파일러 |
| `name_en` | string | R | 원어명 (SWAPI 등 외부 대조) | `"Luke Skywalker"` | 인물 프로파일러 |

---

## 2. 분류 (Classification) — 인물 프로파일러 / 큐레이션

| 필드 | 타입 | R/O | 규칙 | 예시 |
| --- | --- | --- | --- | --- |
| `alignment` | enum\|null | O | `light` / `dark` / `neutral`. 미상이면 null (제5조) | `"light"` |
| `tier` | integer | R | `1` 주요 / `2` 보조 / `3` 단역. 표시 등급 | `1` |
| `era_primary` | enum\|null | O | 표준 8개 시대 키 중 하나. 여러 시대 걸치면 null | `"age_of_rebellion"` |

---

## 3. 생물 정보 (Biographical) — 사실, 출처(SWAPI)에서

| 필드 | 타입 | R/O | 규칙 | 예시 |
| --- | --- | --- | --- | --- |
| `height_cm` | number\|null | O | 키(cm). 미상 null | `172` |
| `mass_kg` | number\|null | O | 몸무게(kg). 미상 null | `77` |
| `gender` | enum | O | `male`/`female`/`droid`/`none`/`other` | `"male"` |
| `species` | string\|null | O | 종족(추후 종족 축 id 참조 전환) | `"인간"` |
| `birth_year` | string\|null | O | 표기 그대로 | `"19BBY"` |
| `birth_year_value` | number\|null | O | BBY 음수·ABY 양수 (정렬·연대 연동) | `-19` |
| `birth_year_certainty` | enum | O | `exact`/`approximate`/`disputed` (제5조) | `"exact"` |

---

## 4. 출신·소속 (Origin & Affiliation) — **id 참조** (제2·4조)

| 필드 | 타입 | R/O | 규칙 | 예시 | 엔티티 owner |
| --- | --- | --- | --- | --- | --- |
| `homeworld` | string\|null | O | 장소 id 참조 (이름 직접입력 금지) | `"tatooine"` | location-curator |
| `affiliation_history` | object[] | O | `[{faction, from_event, to_event}]` 모두 id 참조 | `[{"faction":"rebel-alliance","from_event":null,"to_event":null}]` | faction-curator |

---

## 5. 서사·심리 (Narrative) — 인물 프로파일러 책임, 자기 언어 (제3·6조)

| 필드 | 타입 | R/O | 규칙 | 예시 |
| --- | --- | --- | --- | --- |
| `motivation` | string\|null | O | 핵심 동기·변화. 위키 복제 금지 | `"..."` |
| `arc` | object[] | O | 변화 곡선 `[{event, note}]` — **사건 id에 앵커링** | `[{"event":"battle-of-yavin","note":"..."}]` |
| `key_choices` | object[] | O | 결정적 선택 3개 `[{event, note}]` (제3조 대표질문 산출) | `[]` |

> 연대(`event`의 year)는 **직접 계산하지 않고** timeline-curator 값을 id로 참조(제4조).

---

## 6. 등장 (Appearances) — id 참조

| 필드 | 타입 | R/O | 규칙 | 예시 | owner |
| --- | --- | --- | --- | --- | --- |
| `appears_in` | string[] | O | 등장 사건 id (events.json) | `["battle-of-yavin"]` | orchestrator 교차참조 |
| `works` | string[] | O | 출연작 id (작품 축) | `["ep-4-a-new-hope"]` | 에피소드 요약자 |

> **관계(가족/사제/동맹/적대)는 이 스키마에 넣지 않는다.** 관계 추출자의 관계 스키마가
> 소유(제4조). 인물은 관계의 끝점 id로만 참조된다.

---

## 7. 시각 (Visual) — asset-designer, 실루엣 (제6조)

줌인 부각 연출의 소스. **오리지널 실루엣만** — 디즈니 IP·실제 배우/스틸 복제 금지.

| 필드 | 타입 | R/O | 규칙 | 예시 |
| --- | --- | --- | --- | --- |
| `portrait` | object | O | `{type, archetype, ref, license}` | (아래) |
| ┗ `type` | enum | — | `silhouette` / `procedural` / `image` | `"silhouette"` |
| ┗ `archetype` | enum\|null | — | 실루엣 형태 분류 (아래) | `"jedi"` |
| ┗ `ref` | string\|null | — | 자산 id·경로 (오리지널 SVG) | `null` |
| ┗ `license` | enum | — | `original` / `licensed`. 기본 `original` (제6조) | `"original"` |

`archetype` enum (실루엣 형태): `jedi` / `sith` / `droid` / `trooper` / `pilot` /
`bounty-hunter` / `royalty-politician` / `creature` / `civilian`

---

## 8. 출처 (Source) — 제5·6조

| 필드 | 타입 | R/O | 규칙 | 예시 |
| --- | --- | --- | --- | --- |
| `source` | string | R | 1차 출처 | `"스타워즈 오리지널 3부작"` |
| `source_type` | enum | R | `film`/`series`/`novel`/`comic`/`game` | `"film"` |
| `canon_status` | enum | R | `explicit`/`referenced`/`inferred` | `"explicit"` |

---

## 9. 검증 예시 — 루크 스카이워커

```json
{
  "id": "luke-skywalker",
  "name": "루크 스카이워커",
  "name_en": "Luke Skywalker",

  "alignment": "light",
  "tier": 1,
  "era_primary": "age_of_rebellion",

  "height_cm": 172,
  "mass_kg": 77,
  "gender": "male",
  "species": "인간",
  "birth_year": "19BBY",
  "birth_year_value": -19,
  "birth_year_certainty": "exact",

  "homeworld": "tatooine",
  "affiliation_history": [{ "faction": "rebel-alliance", "from_event": null, "to_event": null }],

  "motivation": "(인물 프로파일러가 자기 언어로 작성)",
  "arc": [{ "event": "battle-of-yavin", "note": "(변화 메모)" }],
  "key_choices": [],

  "appears_in": ["battle-of-yavin", "battle-of-hoth", "battle-of-endor"],
  "works": ["ep-4-a-new-hope", "ep-5-empire", "ep-6-return-of-jedi", "ep-3-revenge-of-sith"],

  "portrait": { "type": "silhouette", "archetype": "jedi", "ref": null, "license": "original" },

  "source": "스타워즈 오리지널 3부작",
  "source_type": "film",
  "canon_status": "explicit"
}
```

---

## 10. 확정 필요한 결정 (제5조)

1. **`species` id화** — 지금은 문자열. 종족 축(별도 큐레이터)을 만들면 id 참조로 전환할지.
2. **`era_primary` 자동 도출 규칙** — 여러 시대 걸친 인물(bridge)은 null로 둘지, 첫 등장 시대로 고정할지.
3. **`tier` 산정 기준** — 자동 채움에서는 공동출연 관계 수(deg)로 임시 산정(아래 JSON). 정식 기준 확정 필요.
4. **`portrait.archetype` 배정 주체** — asset-designer가 일괄 배정. 자동 채움에서는 드로이드만 선배정, 나머지 null.
