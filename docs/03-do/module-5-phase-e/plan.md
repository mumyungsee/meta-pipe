# Module-5: Phase E (Execute) — Plan

> Phase E 레퍼런스 파일(`references/execute.md`) 구현 계획

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

pipeline.json의 step을 mode별(auto/assist/manual)로 순차 실행하고, 실행 결과를 execution-log.json + result.md로 기록

## Design 문서 기준

- **Section 3.4**: execution-log.json + result.md 스키마
- **Section 4.4**: Phase E — Execute 상세 설계
- **Section 8.3**: Module 5 핵심 구현 포인트
- **Section 7.2**: T-05 (파이프라인 실행 → execution-log.json + result.md 생성)

## 구현할 것

### 1. pipeline.json 로드 + 검증

- `test/{slug}/pipeline/pipeline.json` 읽기
- steps 배열 존재 여부 확인
- 각 step의 필수 필드(order, name, mode, instruction) 검증
- 검증 실패 시 → 사용자에게 오류 알림 + Phase C 재실행 제안

### 2. mode별 실행 전략

| Mode | 실행 방식 | 사용자 개입 |
|------|----------|------------|
| **auto** | AI가 직접 실행 (Bash, Write, Read 등) → 결과 기록 | 없음 (완료 알림만) |
| **assist** | AI가 초안/가이드 제시 → 사용자 확인 후 적용 | AskUserQuestion으로 확인 |
| **manual** | 실행 가이드 출력 → 사용자가 직접 실행 → 완료 확인 | AskUserQuestion으로 완료 여부 확인 |

### 3. step별 순차 실행 루프

```
for each step in pipeline.json.steps (order 순):
  1. "Step N: {name} [{mode}]" 상태 출력
  2. mode에 따라 실행:
     - auto: instruction 기반 AI 직접 실행
     - assist: 초안 제시 → 사용자 확인/수정 → 적용
     - manual: 가이드 출력 → 사용자 완료 확인
  3. 결과를 execution-log.json에 step 단위로 기록
  4. 실패 시 → 실패 처리 로직
```

### 4. 실패 처리

Design Section 4.4 실패 처리 전략 준수:

| 실패 유형 | 대응 |
|----------|------|
| 도구 오류 (명령 실패) | 오류 메시지 분석 → 수정 후 재시도 제안 |
| 권한 부족 (API 키 등) | manual step으로 전환 → 사용자 가이드 |
| 스택 비호환 | Phase C로 돌아가서 해당 step 수정 제안 |
| 연쇄 실패 (3회) | 파이프라인 중단 + 지금까지 결과 저장 |

사용자에게 3가지 선택지 제시:
- **skip**: 해당 step을 건너뜀 (status: "skipped")
- **retry**: 수정 후 재시도
- **modify**: step instruction 수정 후 재실행

### 5. execution-log.json 생성

Design Section 3.4 스키마 준수:

```json
{
  "steps_completed": [
    {
      "step": 1,
      "name": "Step 이름",
      "status": "success|skipped|failed",
      "output": "실행 결과 요약",
      "files_created": ["생성된 파일 경로"]
    }
  ],
  "final_result": "최종 결과 요약",
  "next_actions": ["후속 작업 제안"]
}
```

- 각 step 완료 시 즉시 기록 (중단 시에도 진행분 보존)
- 경로: `test/{slug}/pipeline/execution-log.json`

### 6. result.md 생성

전체 실행 완료 후 사람이 읽기 쉬운 결과 요약 문서:

```markdown
# {goal} — 실행 결과

## 요약
- 전체 steps: N개
- 성공: X개 / 건너뜀: Y개 / 실패: Z개

## Step별 결과
### Step 1: {name} [mode] — {status}
{output}

## 생성된 파일
- file1.md
- file2.yaml

## 후속 작업
- action1
- action2
```

- 경로: `test/{slug}/pipeline/result.md`

### 7. 에러 대응

- pipeline.json 파일 없음 → "Phase C를 먼저 실행해주세요" 안내
- step 실행 중 예상치 못한 오류 → 현재까지 결과 저장 + 사용자 알림
- 모든 step이 skip/failed → "파이프라인 실행에 실패했습니다" + 원인 분석 제안

## 완료 기준 (Design 7.2 T-05)

| ID | 기준 | 검증 방법 |
|----|------|----------|
| T-05 | 파이프라인 실행 → execution-log.json + result.md 생성 | 파일 존재 확인 |
| AC-01 | execution-log.json이 Design 3.4 스키마와 일치 | 필드 대조 |
| AC-02 | result.md가 사람이 읽을 수 있는 형식 | 마크다운 렌더링 확인 |
| AC-03 | auto step이 실제 실행됨 (파일 생성 등) | 실행 결과물 확인 |
| AC-04 | assist/manual step에서 사용자 확인 진행 | AskUserQuestion 동작 확인 |
| AC-05 | 실패 시 skip/retry/modify 선택지 제시 | 의도적 실패 시나리오로 검증 |

## 테스트 방법

- 기존 산출물 활용: `test/lecture-wiki-automation/pipeline/pipeline.json` (6 steps, sage-wiki 파이프라인)
- `/meta-pipe` 실행 → Phase A, B, C 건너뛰고 Phase E부터 테스트
  - 또는: pipeline.json을 직접 읽어서 Phase E만 독립 실행
- 검증 포인트:
  1. manual step(Step 1, 2): 가이드 출력 + 사용자 완료 확인이 동작하는지
  2. assist step(Step 3, 5, 6): AI 초안 제시 + 사용자 확인이 동작하는지
  3. auto step(Step 4): AI가 파일을 실제 생성하는지
  4. execution-log.json에 모든 step 결과가 기록되는지
  5. result.md가 사람이 읽을 수 있는 형식인지

## 산출물

- `skills/meta-pipe/references/execute.md` — Phase E 레퍼런스 (실행 정본)

## 의존성

- module-4 완료 ✅ (pipeline.json 출력이 Phase E 입력)
- Bash 도구 사용 가능해야 함 (auto mode step 실행)
- AskUserQuestion 사용 가능해야 함 (assist/manual mode 사용자 확인)

## 위험 요소

| 위험 | 대응 |
|------|------|
| auto step 실행 시 시스템 변경 (패키지 설치 등) | 실행 전 사용자에게 확인 요청, 위험한 명령은 assist로 전환 |
| manual step에서 사용자가 외부 작업 완료를 확인할 방법 | AskUserQuestion으로 "완료했나요?" 질문, 사용자 응답 신뢰 |
| pipeline.json step이 이전 step 결과에 의존 | step 실행 순서 보장 + 이전 step 실패 시 의존 step 자동 skip 검토 |
| 실행 시간이 길어질 수 있음 (Ollama 설치 등) | manual step은 사용자 페이스에 맞김, 타임아웃 없음 |
