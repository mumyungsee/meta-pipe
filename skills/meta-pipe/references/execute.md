# Phase E: Execute (실행)

> 파이프라인 step을 mode별(auto/assist/manual)로 순차 실행하고, 결과를 execution-log.json + result.md로 기록

---

## 목차

- [1. 목적](#1-목적)
- [2. 입력](#2-입력)
- [3. pipeline.json 로드 + 검증](#3-pipelinejson-로드--검증)
- [4. mode별 실행 전략](#4-mode별-실행-전략)
- [5. step별 순차 실행](#5-step별-순차-실행)
- [6. 실패 처리](#6-실패-처리)
- [7. execution-log.json 생성](#7-execution-logjson-생성)
- [8. result.md 생성](#8-resultmd-생성)
- [9. 에러 대응](#9-에러-대응)

---

## 1. 목적

Phase E는 Phase C에서 생성한 pipeline.json의 step을 순차 실행합니다:
- **auto** step은 AI가 직접 실행 (파일 생성, 코드 작성, 명령 실행)
- **assist** step은 AI가 초안을 제시하고 사용자 확인 후 적용
- **manual** step은 실행 가이드를 제공하고 사용자가 직접 실행
- 모든 step 결과를 **execution-log.json**에 기록
- 전체 완료 후 **result.md**로 요약

---

## 2. 입력

Phase E는 아래 파일을 읽어서 시작합니다:

### 2.1 pipeline.json

`test/{slug}/pipeline/pipeline.json`에서 사용하는 필드:
- `steps[]` — 실행할 step 배열 (order 순 정렬)
- `steps[].order` — 실행 순서
- `steps[].name` — step 이름
- `steps[].mode` — 실행 모드 (auto/assist/manual)
- `steps[].instruction` — 실행 지시사항
- `steps[].expected_output` — 기대 결과
- `steps[].tools_needed` — 필요한 도구 목록
- `original.source_url` — 원본 사례 URL (result.md 참조용)
- `adaptations[]` — 적용된 수정 사항 (result.md 참조용)

### 2.2 consult.json (참조용)

`test/{slug}/pipeline/consult.json`에서 참조하는 필드:
- `goal_refined` — result.md 제목에 사용
- `constraints.capabilities` — auto step 실행 시 난이도 조절 참고

---

## 3. pipeline.json 로드 + 검증

### 3.1 파일 읽기

`test/{slug}/pipeline/pipeline.json`을 Read로 읽습니다.

### 3.2 검증 항목

| 검증 항목 | 실패 시 대응 |
|----------|------------|
| 파일 존재 여부 | "Phase C를 먼저 실행해주세요" 안내 + Phase E 중단 |
| steps 배열 존재 | "pipeline.json에 steps가 없습니다" 안내 + Phase C 재실행 제안 |
| steps 길이 >= 1 | "실행할 step이 없습니다" 안내 + Phase C 재실행 제안 |
| 각 step 필수 필드 (order, name, mode, instruction) | 누락 필드 목록 출력 + Phase C 재실행 제안 |
| mode 값이 auto/assist/manual 중 하나 | 잘못된 mode 값 출력 + 수정 제안 |

### 3.3 실행 전 사용자 확인

검증 통과 후, 실행 전에 파이프라인 요약을 보여줍니다:

```
파이프라인을 실행합니다:

| Step | 이름 | Mode | 설명 |
|------|------|------|------|
| 1 | {name} | {mode} | {instruction 첫 줄 요약} |
| 2 | {name} | {mode} | {instruction 첫 줄 요약} |
| ... | ... | ... | ... |

총 {N}개 step (auto: {X}개, assist: {Y}개, manual: {Z}개)

실행을 시작할까요?
```

AskUserQuestion으로 확인 후 실행 시작.

---

## 4. mode별 실행 전략

### 4.1 auto mode

AI가 직접 실행합니다:
1. instruction을 파싱하여 실행할 작업 결정
2. 적절한 도구로 실행:
   - 파일 생성/수정 → Write, Edit
   - 코드 실행 → Bash
   - 파일 읽기 → Read
   - 파일 검색 → Glob, Grep
3. 실행 결과를 사용자에게 출력:
   ```
   Step {N}: {name} [auto]
   실행 중...
   ✅ 완료: {결과 요약}
   생성된 파일: {파일 목록}
   ```
4. expected_output과 실제 결과 비교 → 불일치 시 사용자 알림

**주의사항**:
- 시스템에 영향을 주는 명령(패키지 설치, 환경 변수 변경 등)은 실행 전 사용자에게 확인
- 실행 결과가 expected_output과 다르면 "기대와 다른 결과입니다. 계속할까요?" 확인

### 4.2 assist mode

AI가 초안을 제시하고 사용자 확인 후 적용합니다:
1. instruction을 기반으로 초안 생성 (설정 파일, 코드, 콘텐츠 등)
2. 초안을 사용자에게 제시:
   ```
   Step {N}: {name} [assist]
   
   아래 초안을 생성했습니다:
   
   {초안 내용}
   
   이대로 적용할까요? (수정 요청도 가능합니다)
   ```
3. AskUserQuestion으로 사용자 응답 대기
4. 사용자 응답 처리:
   - **확인** → 초안 적용 (Write/Edit 등)
   - **수정 요청** → 수정 후 다시 제시
   - **건너뛰기** → status: "skipped"로 기록
5. 적용 후 결과 출력:
   ```
   ✅ 완료: {적용 결과 요약}
   ```

### 4.3 manual mode

사용자가 직접 실행하고, AI는 가이드만 제공합니다:
1. instruction을 보기 쉽게 포맷팅하여 출력:
   ```
   Step {N}: {name} [manual]
   
   아래 작업을 직접 수행해주세요:
   
   {instruction (번호 매긴 단계별 가이드)}
   
   기대 결과: {expected_output}
   필요 도구: {tools_needed}
   
   완료되면 알려주세요. (건너뛰기도 가능합니다)
   ```
2. AskUserQuestion으로 사용자 응답 대기
3. 사용자 응답 처리:
   - **완료** ("완료", "했어", "done") → status: "success"
   - **건너뛰기** ("건너뛰기", "skip") → status: "skipped"
   - **실패/문제 발생** → 실패 처리 로직으로 이동
   - **질문** → 추가 설명 제공 후 다시 완료 확인

---

## 5. step별 순차 실행

### 5.1 실행 루프

```
consecutive_failures = 0

for each step in pipeline.json.steps (order 순):
  1. 상태 헤더 출력:
     "━━━ Step {order}/{total}: {name} [{mode}] ━━━"
  
  2. mode에 따라 실행 (Section 4 참조)
  
  3. 결과 기록:
     - status: success/skipped/failed
     - output: 실행 결과 요약
     - files_created: 생성된 파일 경로 목록
  
  4. 실패 판정:
     - success → consecutive_failures = 0, 다음 step
     - skipped → consecutive_failures = 0, 다음 step
     - failed → consecutive_failures += 1
       - consecutive_failures >= 3 → 파이프라인 중단 (Section 6.2)
       - 그 외 → 실패 처리 (Section 6.1)
```

### 5.2 진행 상황 표시

각 step 완료 시 전체 진행률을 보여줍니다:

```
[{완료}/{전체}] Step {N} {status}. 다음: Step {N+1} ({name})
```

### 5.3 마지막 step 완료 후

모든 step 실행 완료 시:
1. execution-log.json 저장 (Section 7)
2. result.md 생성 (Section 8)
3. 완료 요약 출력:
   ```
   파이프라인 실행 완료!
   - 성공: {X}개 / 건너뜀: {Y}개 / 실패: {Z}개
   - 결과: test/{slug}/pipeline/result.md
   ```

---

## 6. 실패 처리

### 6.1 단일 step 실패

step 실행이 실패하면 사용자에게 3가지 선택지를 제시합니다:

```
Step {N}: {name} 실행에 실패했습니다.
오류: {에러 메시지 또는 실패 원인}

어떻게 진행할까요?
1. skip — 이 step을 건너뛰고 다음으로 진행
2. retry — 수정 후 다시 시도
3. modify — step instruction을 수정한 뒤 다시 실행
```

AskUserQuestion으로 선택 받은 후:

| 선택 | 처리 |
|------|------|
| **skip** | status: "skipped", output: "사용자 요청으로 건너뜀" 기록. 다음 step 진행 |
| **retry** | AI가 오류 원인 분석 → 수정 사항 적용 → 같은 step 재실행 |
| **modify** | 사용자가 instruction 수정 → 수정된 instruction으로 재실행 |

### 6.2 연쇄 실패 (3회)

연속으로 3개 step이 failed 상태일 때:

```
연속 3개 step이 실패했습니다. 파이프라인을 중단합니다.

실패한 steps:
- Step {N-2}: {name} — {실패 원인}
- Step {N-1}: {name} — {실패 원인}
- Step {N}: {name} — {실패 원인}

지금까지 결과는 execution-log.json에 저장되었습니다.

제안:
- Phase C로 돌아가서 파이프라인 수정
- 실패 원인을 해결한 후 재실행
```

- 중단 시에도 execution-log.json + result.md는 저장 (진행분 보존)
- result.md에 "중단됨" 상태와 실패 원인 기록

### 6.3 실패 유형별 대응

| 실패 유형 | 감지 방법 | 자동 대응 |
|----------|----------|----------|
| 도구 오류 (Bash 명령 실패) | exit code != 0 또는 에러 출력 | 에러 메시지 분석 → 수정 제안 후 retry 권유 |
| 권한 부족 (API 키, 접근 권한) | "permission denied", "unauthorized" 등 | manual step으로 전환 제안 → 사용자가 직접 설정 |
| 스택 비호환 (도구 미설치 등) | "command not found", "not installed" 등 | Phase C로 돌아가서 해당 step 수정 제안 |
| 파일 충돌 (이미 존재) | "already exists", 덮어쓰기 경고 | 사용자에게 덮어쓰기 여부 확인 |

---

## 7. execution-log.json 생성

### 7.1 스키마 (Design Section 3.4)

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

### 7.2 기록 시점

- 각 step 완료 시 **즉시** steps_completed에 추가하여 저장
  - 중단 시에도 진행분이 보존됨
- 모든 step 완료 후 final_result와 next_actions 추가

### 7.3 필드 작성 규칙

| 필드 | 규칙 |
|------|------|
| step | pipeline.json의 order 값과 동일 |
| name | pipeline.json의 name 값과 동일 |
| status | "success": 정상 완료, "skipped": 건너뜀, "failed": 실패 |
| output | 실행 결과 1-2줄 요약. 성공 시 주요 결과, 실패 시 에러 원인 |
| files_created | 이 step에서 생성/수정된 파일 경로 배열. 없으면 빈 배열 [] |
| final_result | 전체 파이프라인 결과 1-2줄 요약 |
| next_actions | 파이프라인 완료 후 추천하는 후속 작업 목록 |

### 7.4 저장 경로

`test/{slug}/pipeline/execution-log.json`

---

## 8. result.md 생성

### 8.1 형식

전체 실행 완료 후 사람이 읽기 쉬운 결과 요약 문서를 생성합니다:

```markdown
# {goal_refined} — 실행 결과

> 원본 사례: {original.source_url}
> 실행 일시: {YYYY-MM-DD}

---

## 요약

| 항목 | 값 |
|------|-----|
| 전체 steps | {N}개 |
| 성공 | {X}개 |
| 건너뜀 | {Y}개 |
| 실패 | {Z}개 |
| 상태 | 완료 / 중단 |

## 적용된 수정 사항

| # | 변경 | 이유 |
|---|------|------|
| 1 | {adaptations[0].what} | {adaptations[0].why} |
| ... | ... | ... |

## Step별 결과

### Step 1: {name} [{mode}] — {status}
{output}
- 생성된 파일: {files_created}

### Step 2: {name} [{mode}] — {status}
{output}

...

## 생성된 파일 목록

- file1.md
- file2.yaml
- ...

## 후속 작업

- {next_actions[0]}
- {next_actions[1]}
- ...
```

### 8.2 중단 시 result.md

파이프라인이 중단된 경우에도 result.md를 생성합니다:
- 요약 테이블의 상태: "중단"
- 실패한 step에 실패 원인 기록
- 후속 작업에 "Phase C로 돌아가서 실패 step 수정" 포함

### 8.3 저장 경로

`test/{slug}/pipeline/result.md`

---

## 9. 에러 대응

| 상황 | 대응 |
|------|------|
| pipeline.json 파일 없음 | "Phase C를 먼저 실행해주세요" 안내 + Phase E 중단 |
| pipeline.json 스키마 불일치 | 누락 필드 목록 출력 + Phase C 재실행 제안 |
| step 실행 중 예상치 못한 오류 | 현재까지 결과 즉시 저장 + 사용자 알림 + skip/retry/modify 제시 |
| 모든 step이 skipped 또는 failed | "파이프라인 실행에 실패했습니다. Phase C에서 파이프라인을 수정하거나 다른 사례를 선택해보세요" |
| 사용자가 중도 중단 요청 ("그만", "중단") | 현재까지 결과 저장 + result.md에 "사용자 요청으로 중단" 기록 |
| auto step이 위험한 명령 포함 | 실행 전 사용자에게 "이 명령을 실행해도 될까요?" 확인 |
