# Module-4: Phase C (Adapt) — Plan

> Phase C 레퍼런스 파일(`references/adapt.md`) 구현 계획

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

선택한 사례(search-results.json의 selected)를 내 환경에 맞게 수정하고, 실행 가능한 파이프라인(pipeline.json + pipeline.md)으로 변환

## Design 문서 기준

- **Section 3.3**: pipeline.json + pipeline.md 스키마
- **Section 4.3**: Phase C — Adapt 상세 설계
- **Section 8.3**: Module 4 핵심 구현 포인트
- **Section 7.2**: T-04 (선택 사례 적용 → pipeline.json steps 1개 이상)

## 구현할 것

### 1. 선택 사례 원본 분석

- search-results.json의 `selected.url`을 WebFetch로 상세 읽기
- 원본 사례의 기술 스택, 설치 방법, 핵심 기능 파악
- `original` 필드에 source_url + summary 기록

### 2. 원본 vs 내 환경 차이점 도출

consult.json의 constraints와 원본 사례를 대조하여 차이점 도출:

| 비교 항목 | 방법 |
|----------|------|
| 스택 차이 | 원본 기술 vs `constraints.stack` → 대체 방법 |
| 도구 차이 | 원본 필요 도구 vs `constraints.tools` → 대체 도구 |
| 역량 차이 | 원본 난이도 vs `constraints.capabilities` → 단순화 or 자동화 |

- 각 차이점을 `adaptations[]`에 what/why로 기록

### 3. 수정 사항 사용자 확인

- AskUserQuestion으로 수정 사항 목록 제시
- 사용자 확인 후 다음 단계 진행
- 추가 수정 요청 시 adaptations에 반영

### 4. Step 분할 + mode 할당

사례를 실행 가능한 step으로 분할:

- 각 step에 `order`, `name`, `mode`, `instruction`, `expected_output`, `tools_needed` 할당
- mode 할당 기준:
  - **auto**: AI가 100% 실행 가능 (파일 생성, 코드 작성 등)
  - **assist**: AI 초안 + 사람 검수 필요 (설정 파일, 환경 변수)
  - **manual**: 사람만 실행 가능 (외부 서비스 가입, 결제 등)

### 5. pipeline.json + pipeline.md 동시 생성

- pipeline.json: Design Section 3.3 스키마 준수
- pipeline.md: 사람이 읽기 쉬운 마크다운 형식
- 경로: `test/{slug}/pipeline/pipeline.json`, `test/{slug}/pipeline/pipeline.md`

### 6. 에러 대응

- WebFetch 실패 → search-results.json의 summary만으로 분석 진행
- step 분할 불확실 → 사용자에게 확인 후 진행
- 원본 사례가 너무 복잡 → 핵심 기능만 추출하여 단순화

## 완료 기준 (Design 7.2 T-04)

| ID | 기준 | 검증 방법 |
|----|------|----------|
| T-04 | 선택 사례 적용 → pipeline.json에 steps 1개 이상 | pipeline.json 파일 확인 |
| AC-01 | pipeline.json이 Design 3.3 스키마와 일치 | 필드 대조 |
| AC-02 | pipeline.md가 사람이 읽을 수 있는 형식 | 마크다운 렌더링 확인 |
| AC-03 | adaptations에 원본 vs 내 환경 차이 1개 이상 | adaptations[] 확인 |
| AC-04 | 사용자 확인 후 저장 | AskUserQuestion 동작 확인 |

## 테스트 방법

- 기존 산출물 활용: `test/lecture-wiki-automation/pipeline/search-results.json` (sage-wiki 선택됨)
- `/meta-pipe` 실행 → Phase A, B 건너뛰고 Phase C부터 테스트
  - 또는: search-results.json을 직접 읽어서 Phase C만 독립 실행
- sage-wiki를 강의 위키에 맞게 적용한 pipeline이 실행 가능한지 사람이 판단

## 산출물

- `skills/meta-pipe/references/adapt.md` — Phase C 레퍼런스 (실행 정본)

## 의존성

- module-3 완료 ✅ (search-results.json 출력이 Phase C 입력)
- WebFetch 도구 사용 가능해야 함 (선택 사례 상세 분석)

## 위험 요소

| 위험 | 대응 |
|------|------|
| 선택 사례(sage-wiki)가 Go 기반 → 사용자 stack(Node.js, Python)과 불일치 | adapt 단계에서 "빌드된 바이너리 사용" or "대체 기술로 구현" 방향 제시 |
| step 분할이 너무 세밀하거나 너무 거칠 수 있음 | 사용자 확인 단계에서 조정 |
| pipeline.md와 pipeline.json 내용 불일치 가능 | 동시 생성으로 일관성 보장 |
