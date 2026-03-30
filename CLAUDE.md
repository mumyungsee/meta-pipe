# meta-pipe

> 도메인 지식 없이도 AI가 도메인을 조사하고, 그 도메인에 최적화된 개발 파이프라인을 동적으로 설계/실행하는 Claude Code 스킬

## 프로젝트 상태

- **현재 단계**: Design + SKILL.md 구현 완료, 2개 도메인 테스트 완료
- **Plan 문서**: `docs/01-plan/features/domain-discovery-pipeline.plan.md` (v0.5)
- **Design 문서**: `docs/02-design/features/domain-discovery-pipeline.design.md` (v0.1)
- **SKILL.md**: `skills/meta-pipe/SKILL.md` + `references/` (v1.0)
- **Do 결과**: `docs/03-do/card-news/`, `docs/03-do/youtube-thumbnail/`
- **다음 작업**: Harness 패턴 통합 (Phase B/C 확장), 추가 도메인 테스트

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
- **Harness** (revfactory/harness): 에이전트 팀 설계 + 스킬 생성 메타스킬. Phase C 분산 실행에 참조

## 강제 메커니즘 전략

- **v1.0**: SKILL.md만 (프롬프트 기반, 빠른 검증)
- **v2.0**: SKILL.md + Hooks (에이전트 자율 실행 시 안전장치)
- 전환 시점: approval_required 무시 사례 발생 시

## 파일 구조

```
meta-pipe/
├── CLAUDE.md                          # 이 파일
├── .meta-pipe-status.json             # 실행 상태 추적
│
├── skills/meta-pipe/                  # [스킬 본체]
│   ├── SKILL.md                       # 메인 스킬 (Phase A/B/C)
│   └── references/                    # 지연 로딩 참조 문서
│       ├── discovery.md               # Phase A 상세 가이드
│       ├── pipeline-design.md         # Phase B 상세 가이드
│       └── execution.md              # Phase C 상세 가이드
│
├── docs/                              # [PDCA 문서]
│   ├── 01-plan/features/              # Plan 기획
│   ├── 02-design/features/            # Design 설계
│   ├── 03-do/                         # Do 실행 (도메인별 파이프라인 결과)
│   │   ├── card-news/                 # 카드뉴스 도메인 테스트
│   │   │   ├── domain-discovery.md    #   Phase A 결과
│   │   │   ├── pipeline.md/json       #   Phase B 결과
│   │   │   ├── steps/                 #   Phase C 각 단계 산출물
│   │   │   └── output/               #   실제 생성물 (이미지 등)
│   │   └── youtube-thumbnail/         # 유튜브 썸네일 도메인 테스트
│   │       ├── domain-discovery.md
│   │       ├── pipeline.md/json
│   │       ├── steps/
│   │       └── output/               #   실제 생성물 (src/, config/)
│   ├── 04-analysis/features/          # Check 분석
│   └── 05-report/features/            # Act 보고서
│
├── meta-pipe-cache/                   # 도메인 조사 캐시 (30일)
└── meta-pipe-logs/                    # 실행 로그
```

## 작업 규칙

- bkit PDCA 방법론 사용
- 새 세션 시작 시 이 파일 + Plan 문서 읽기
- WebSearch 결과는 반드시 출처 포함
- 규제 정보는 "[검토 필요]" 마킹

## 커맨드

- `/discover [도메인]` - 도메인 발견 파이프라인 실행
- `/status` - 프로젝트 현황 빠른 확인
- `/test-domain [도메인]` - 파이프라인 테스트 + 품질 평가

## 트렌드 체크

- 마지막 설정 업그레이드: 2026-03-28
- 다음 체크 권장: 2026-04-28
- 실행: /upgrade-claude-code
