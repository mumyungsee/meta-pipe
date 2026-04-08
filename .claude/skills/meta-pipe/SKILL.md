---
name: meta-pipe
description: "검증된 사례를 검색하여 사용자 상황에 맞게 적용하는 사례 기반 메타 파이프라인"
allowed-tools: AskUserQuestion, WebSearch, WebFetch, Read, Write, Bash, Glob
---

검증된 사례를 검색하여 사용자 상황에 맞게 적용하는 4단계 메타 파이프라인을 실행합니다.

**흐름**: Consult(상담) → Search(검색) → Adapt(적용) → Execute(실행)

**핵심 원칙**:
- 매 Phase 전환 시 사용자 확인 필수 (자동 진행 없음)
- AI의 검색/판단 과정을 항상 사용자에게 보여줌
- 모든 결과를 `test/{slug}/pipeline/`에 파일로 저장

**상세 오케스트레이션 로직**: `skills/meta-pipe/SKILL.md` 파일을 Read로 읽어서 따르세요.
**Phase A 상세**: `skills/meta-pipe/references/consult.md`
**Phase B 상세**: `skills/meta-pipe/references/search.md`
**Phase C 상세**: `skills/meta-pipe/references/adapt.md`
**Phase E 상세**: `skills/meta-pipe/references/execute.md`

## 실행 순서

1. `skills/meta-pipe/SKILL.md`를 Read로 읽고 전체 오케스트레이션 흐름을 파악
2. Step 0: 초기화 — 사용자에게 "무엇을 만들고 싶으세요?" 질문 (AskUserQuestion)
3. Step 1: Phase A — `skills/meta-pipe/references/consult.md`를 Read로 읽고 따름
4. Step 2: Phase B — `skills/meta-pipe/references/search.md`를 Read로 읽고 따름
5. Step 3: Phase C — `skills/meta-pipe/references/adapt.md`를 Read로 읽고 따름
6. Step 4: Phase E — `skills/meta-pipe/references/execute.md`를 Read로 읽고 따름
