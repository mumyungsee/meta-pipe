# meta-pipe

> 도메인 지식 없이도 AI가 도메인을 조사하고, 그 도메인에 최적화된 개발 파이프라인을 동적으로 설계/실행하는 Claude Code 스킬

## 프로젝트 상태

- **현재 단계**: Design + SKILL.md 구현 완료 → 테스트 대기
- **Plan 문서**: `docs/01-plan/features/domain-discovery-pipeline.plan.md` (v0.5)
- **Design 문서**: `docs/02-design/features/domain-discovery-pipeline.design.md` (v0.1)
- **SKILL.md**: `skills/meta-pipe/SKILL.md` + `references/` (v1.0)
- **PoC 결과**: `examples/card-news/` (카드뉴스 자동화 도메인)
- **다음 작업**: 5개 도메인 테스트 (Plan 10.4)

## 핵심 개념

```
입력: "X를 만들고 싶어" (도메인 지식 없음)
  ↓ Phase A: Discover → 도메인 조사 (WebSearch)
  ↓ Phase B: Design Pipeline → 도메인 맞춤 파이프라인 단계 설계
  ↓ Phase C: Execute → 각 단계를 전문가 수준으로 실행
출력: 도메인 맞춤 파이프라인 + 각 단계 산출물
```

## 핵심 설계 원칙

- **동적 파이프라인**: 단계 수/내용이 도메인에 따라 달라짐 (고정 N단계가 아님)
- **이중 사용자**: 사람 + 자율 AI 에이전트 모두 사용
- **이중 형식**: 마크다운 (사람용) + 구조화 메타데이터 (에이전트용)
- **approval_required 플래그**: 핵심 결정은 사람 승인, 나머지는 자율 실행

## 선행 사례 참조

- **AWS AI-DLC** (가장 유사): 2-tier 규칙, Adaptive Depth, Extensions opt-in 패턴 적용
- **DataFlow Agent**: 동적 파이프라인 조립 개념. 단, 데이터 처리 전용
- **bkit**: hooks + context injection 메커니즘 참조. 단, 고정 9단계

## 강제 메커니즘 전략

- **v1.0**: SKILL.md만 (프롬프트 기반, 빠른 검증)
- **v2.0**: SKILL.md + Hooks (에이전트 자율 실행 시 안전장치)
- 전환 시점: approval_required 무시 사례 발생 시

## 파일 구조

```
meta-pipe/
├── CLAUDE.md                 # 이 파일
├── docs/
│   ├── 01-plan/features/     # PDCA Plan 문서 (v0.5)
│   └── 02-design/features/   # PDCA Design 문서 (v0.1)
├── skills/meta-pipe/
│   ├── SKILL.md              # 메인 스킬 (Phase A/B/C)
│   └── references/           # 지연 로딩 참조 문서
│       ├── discovery.md      # Phase A 상세 가이드
│       ├── pipeline-design.md # Phase B 상세 가이드
│       └── execution.md      # Phase C 상세 가이드
└── examples/
    └── card-news/            # PoC: 카드뉴스 자동화 도메인
```

## 작업 규칙

- bkit PDCA 방법론 사용
- 새 세션 시작 시 이 파일 + Plan 문서 읽기
- WebSearch 결과는 반드시 출처 포함
- 규제 정보는 "[검토 필요]" 마킹
