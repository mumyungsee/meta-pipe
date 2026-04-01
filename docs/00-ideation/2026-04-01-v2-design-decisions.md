# meta-pipe v2 Design 미결 사항 결정 기록

> 일시: 2026-04-01
> 목적: v2 Plan 9절의 미결 사항을 Design 문서 작성 전에 결정
> 선행 문서: `docs/01-plan/v2-plan.md`, `docs/00-ideation/2026-04-01-v2-redesign.md`

---

## 배경

v2 Plan 9절에서 "Design에서 결정할 사항" 7가지를 명시했다. Design 문서 작성 전에 이 미결 사항들을 먼저 결정하여 Design의 방향을 확정한다.

---

## 결정 1: 서브에이전트 실행 방식 — bkit 방식 단일 채택

### 논의 과정

bkit과 Harness 두 프로젝트를 비교 분석했다.

**분석 결과 — 두 프로젝트의 본질적 차이:**

| | bkit | Harness |
|---|---|---|
| 정체 | 플러그인 시스템 (37 스킬 + 32 에이전트가 이미 존재) | 메타 스킬 (에이전트 팀 + 스킬을 매번 새로 생성) |
| 핵심 가치 | 프로세스 프레임워크 (PDCA, 파이프라인, 품질 루프) | 에이전트 오케스트레이션 (도메인별 에이전트 구성 자동화) |
| 에이전트 실행 | Task(에이전트명) 또는 에이전트 팀 | TeamCreate + SendMessage 또는 Agent() |
| 데이터 전달 | 파일 체인 (docs/) + 상태 파일 + Context Anchor | 메시지 + 태스크 + 파일(_workspace/) 3종 조합 |
| 적용 대상 | 웹앱 개발 (고정 도메인, 사전 정의된 에이전트) | 아무 도메인 (매번 다른 에이전트를 동적 생성) |

**핵심 인사이트**: 둘 다 Claude Code의 동일한 에이전트 팀/서브에이전트 기능을 사용한다. 차이는 실행 메커니즘이 아니라 "에이전트가 사전 정의됨(bkit) vs 매번 생성(Harness)"이다.

**meta-pipe에 대입한 결과:**
- meta-pipe의 Phase A~F는 고정된 프로세스 → bkit의 Phase 1~9과 동일한 성격
- meta-pipe가 Phase C에서 도메인별 에이전트를 설계하는 것 자체가 Harness와 같은 역할
- Harness를 별도로 가져올 필요 없이, meta-pipe의 Phase C가 Harness의 역할을 흡수하면 됨
- bkit이 이미 설치되어 있으므로 PDCA, gap-detector 등을 재활용할 수 있음

### 결정

**bkit 방식 단일 채택. Harness의 설계 지식(6가지 아키텍처 패턴)은 references에 포함.**

구체적으로:
1. meta-pipe = bkit의 새 파이프라인 (development-pipeline 옆에 meta-pipeline 추가)
2. Phase A~F = bkit의 Phase 1~9과 동일 구조 (스킬 + references, 지연 로딩)
3. Phase F(Evaluate) = bkit의 PDCA Check-Act 재활용 (gap-detector, pdca-iterator)
4. Phase E의 에이전트 실행 = bkit이 쓰는 Task(에이전트명) 또는 Agent() 도구
5. Phase C에서 도메인별 에이전트 설계 시 Harness의 6가지 패턴(Pipeline, Fan-out, Expert Pool, Producer-Reviewer, Supervisor, Hierarchical)을 **설계 지식으로 참조** (references/pipeline-design.md에 포함)
6. Harness를 시스템/코드로 가져오지 않음

### 영향

- Phase C의 references/pipeline-design.md에 Harness 6가지 아키텍처 패턴 지식 포함
- Phase E의 references/execution.md에 bkit 패턴의 에이전트 실행 방식 적용
- Phase F는 bkit의 기존 에이전트(gap-detector, pdca-iterator, report-generator) 연동 설계 필요
- pipeline.json에 execution 섹션 추가 (agent, required_tools 매핑)

---

## 결정 2: 상태 관리

(Design 문서 작성 시 결정 예정)

---

## 결정 3: 캐시

(Design 문서 작성 시 결정 예정)

---

## 결정 4: 사용자 프로필

(Design 문서 작성 시 결정 예정)

---

## 결정 5: Phase 간 인터페이스 JSON Schema

(Design 문서 작성 시 결정 예정)

---

## 결정 6: 에러 처리

(Design 문서 작성 시 결정 예정)

---

## 결정 7: 컨텍스트 관리

(Design 문서 작성 시 결정 예정)

---

## 비교 분석 참조 자료

- bkit 레포: https://github.com/popup-studio-ai/bkit-claude-code
- Harness 레포: https://github.com/revfactory/harness
- v1 Harness 통합 Plan: `archive/v1/docs/05-act/next-cycle/harness-integration.plan.md`
