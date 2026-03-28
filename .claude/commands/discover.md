# Domain Discovery 실행

meta-pipe의 핵심 기능인 도메인 발견 파이프라인을 실행합니다.

## 수행 작업

1. `skills/meta-pipe/SKILL.md` 읽기
2. 사용자 입력에서 도메인 키워드 추출
3. Phase A (Discover) → Phase B (Design Pipeline) → Phase C (Execute) 순서로 실행
4. 결과를 `meta-pipe-cache/` 에 저장

## 사용법

```
/discover [도메인 설명]
```

사용자가 "$ARGUMENTS"라고 입력했습니다. 이 도메인에 대해 meta-pipe 파이프라인을 실행하세요.
