# Module-3: Phase B (Search) — Plan

> Phase B 레퍼런스 파일(`references/search.md`) 구현 계획

---

## 목차

- [목표](#목표)
- [Design 문서 기준](#design-문서-기준)
- [구현할 것](#구현할-것)
- [완료 기준](#완료-기준)
- [테스트 방법](#테스트-방법)
- [산출물](#산출물)
- [의존성](#의존성)
- [위험 요소](#위험-요소)

---

## 목표

consult.json의 검색 키워드 + 제약 조건을 기반으로 검증된 사례를 검색하고, 사용자가 하나를 선택하도록 안내

## Design 문서 기준

- **Section 4.2**: Phase B — Search 상세 설계
- **Section 3.2**: search-results.json 스키마
- **Section 8.3**: Module 3 핵심 구현 포인트
- **Section 7.2**: T-02 (검색 실행), T-03 (B→C 게이트)

## 구현할 것

### 1. 검색 쿼리 생성 알고리즘

- consult.json의 `search_keywords` + `constraints`로 쿼리 구성
- 기본 패턴: `site:{site} {goal_refined} {stack keywords}`
- `excluded` 항목은 `-{keyword}`로 제외
- 한국어 목표 → 영어 + 한국어 쿼리 각 1회

### 2. 3사이트 순차 검색 (WebSearch)

- `site:github.com` → 실행 가능한 코드/레포
- `site:threads.net` → 실제 사용 후기/팁
- `site:gpters.org` → 검증된 사례 + 실행 결과
- 각 사이트 상위 3개씩 수집 (최대 9개)

### 3. 유망 결과 상세 수집 (WebFetch)

- 검색 결과 중 유망 2~3개를 WebFetch로 상세 수집
- 사례별 AI 요약 (2-3줄) 생성

### 4. 결과 테이블 제시 + 사용자 선택

- `| # | 소스 | 제목 | 요약 | 적합도 |` 형식
- AskUserQuestion으로 사례 선택 요청

### 5. B→C 게이트 판단 로직

- 기술 스택 호환성: 사용자 stack에 포함되거나 쉽게 대체 가능
- 역량 요구 수준: 사용자 capabilities 이하
- 도구 가용성: 사용자 tools에 포함되거나 무료
- 불가능 시 → 이유 설명 + 다른 사례 추천

### 6. search-results.json 저장

- Design Section 3.2 스키마 준수
- 경로: `test/{slug}/pipeline/search-results.json`

### 7. 에러 대응

- 검색 결과 0건 → 키워드 변경 제안 → 재검색
- WebSearch/WebFetch 실패 → 에러 알림 + 수동 검색 URL 제공
- WebFetch 차단 → 검색 요약만으로 진행 (상세 수집 skip)

## 완료 기준 (Design 7.2 T-02, T-03)

| ID | 기준 | 검증 방법 |
|----|------|----------|
| T-02 | 3개 사이트 검색 + 사례 요약 테이블 출력 | 실제 검색 결과 확인 |
| T-03 | 선택 사례 실행 가능성 판단 결과 출력 | feasibility 판단 결과 확인 |
| SC-01 | search-results.json이 Design 3.2 스키마와 일치 | 필드 대조 |
| SC-02 | 사용자 확인 후 Phase C 전환 질문 | AskUserQuestion 동작 확인 |

## 테스트 방법

- 기존 T-01 산출물 활용: `test/lecture-wiki-automation/pipeline/consult.json`
- `/meta-pipe` 실행 → Phase A 건너뛰고 Phase B부터 테스트
  - 또는: consult.json을 직접 읽어서 Phase B만 독립 실행
- 검색 결과가 consult.json의 제약 조건에 부합하는지 사람이 판단

## 산출물

- `skills/meta-pipe/references/search.md` — Phase B 레퍼런스 (실행 정본)

## 의존성

- module-2 완료 ✅ (consult.json 출력이 Phase B 입력)
- WebSearch, WebFetch 도구 사용 가능해야 함

## 위험 요소

| 위험 | 대응 |
|------|------|
| WebSearch가 site: 연산자를 잘 지원하지 않을 수 있음 | site: 없는 일반 검색도 fallback으로 준비 |
| gpters.org 검색 결과가 부실할 수 있음 | 결과 0건 시 해당 사이트 skip + 나머지로 진행 |
| WebFetch가 특정 사이트 차단당할 수 있음 | 검색 snippet만으로 요약 생성 (상세 수집 skip) |
