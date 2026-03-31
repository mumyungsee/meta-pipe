# Step 6: 통합 테스트 & A/B 최적화

> **작성일**: 2026-03-27
> **의존**: Step 3, 4, 5

---

## 1. 파일 구조

```
src/testing/
├── e2e_test.py              # E2E 파이프라인 테스트
└── ab_test.py               # A/B 변형 생성
src/analytics/
└── performance_tracker.py   # YouTube Analytics CTR 수집
```

---

## 2. E2E 테스트

전체 흐름: 제목 → 프롬프트 빌드 → 이미지 생성 → 검증 → (업로드)

```bash
# 생성 + 검증만
python -m src.testing.e2e_test --title "AI 자동화" --template tech-gradient

# 생성 + 검증 + 업로드
python -m src.testing.e2e_test --title "AI 자동화" --template tech-gradient \
  --upload --video-id VIDEO_ID
```

---

## 3. A/B 테스트

동일 제목에 여러 템플릿으로 변형 생성:

```bash
python -m src.testing.ab_test \
  --title "AI 자동화" \
  --templates tech-gradient,screen-glow,ai-neural
```

- output/ab_test/에 variant_*.png 생성
- YouTube Studio > Test & Compare로 업로드하여 비교
- 최소 7일, 변형당 1,000 노출 이상 후 판단

---

## 4. 성과 추적

YouTube Analytics API로 CTR, 노출수, 조회수 수집:

```python
from src.youtube.auth import get_credentials
from src.analytics.performance_tracker import (
    build_analytics_client, get_thumbnail_performance, save_report
)

creds = get_credentials()
analytics = build_analytics_client(creds)
data = get_thumbnail_performance(analytics, "CHANNEL_ID", "VIDEO_ID")
save_report(data)
```

수집 지표:
- **impressions**: 섬네일 노출 수
- **ctr**: 클릭률 (%)
- **views**: 조회수
- **avg_duration_sec**: 평균 시청 시간

---

## 5. 프롬프트 피드백 루프

```
A/B 변형 생성 → YouTube 업로드 → 7일 대기
→ CTR 수집 → 고성과 프롬프트 패턴 식별
→ config/prompts/ 업데이트
```

주의:
- 빈번한 섬네일 변경은 알고리즘에 부정적
- Watch Time도 CTR과 함께 추적

---

## 6. 완료 기준

- [ ] E2E: 제목 → 섬네일 생성 & 검증 통과
- [ ] A/B: 동일 영상에 2개 이상 변형 생성
- [ ] 성과: CTR 데이터 수집 & JSON 리포트 저장
