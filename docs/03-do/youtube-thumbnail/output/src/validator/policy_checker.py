"""YouTube 정책 준수 검증."""

from dataclasses import dataclass, field


# YouTube 커뮤니티 가이드라인 위반 키워드 (한국어/영어)
BLOCKED_KEYWORDS = [
    # 성적 암시
    "야한", "섹시", "노출", "19금", "성인",
    "sexy", "nude", "nsfw", "xxx",
    # 폭력
    "살인", "학대", "고문", "자해",
    "kill", "murder", "gore", "violence",
    # 혐오
    "혐오", "차별",
    "hate", "racist",
]

# 클릭베이트 패턴 (과장된 표현)
CLICKBAIT_PATTERNS = [
    "충격", "경악", "실화", "ㄷㄷ", "헐",
    "절대 하지마", "무조건", "100%", "역대급",
    "shocking", "you won't believe", "insane",
]


@dataclass
class PolicyResult:
    passed: bool = True
    warnings: list[dict] = field(default_factory=list)
    blocks: list[dict] = field(default_factory=list)

    def add_warning(self, category: str, detail: str):
        self.warnings.append({"category": category, "detail": detail})

    def add_block(self, category: str, detail: str):
        self.blocks.append({"category": category, "detail": detail})
        self.passed = False

    def report(self) -> str:
        lines = []
        status = "통과" if self.passed else "차단"
        lines.append(f"정책 검증: {status}")

        if self.blocks:
            lines.append("  [차단]")
            for b in self.blocks:
                lines.append(f"    - {b['category']}: {b['detail']}")

        if self.warnings:
            lines.append("  [경고]")
            for w in self.warnings:
                lines.append(f"    - {w['category']}: {w['detail']}")

        if not self.blocks and not self.warnings:
            lines.append("  문제 없음")

        return "\n".join(lines)


def check_text_policy(title: str, thumbnail_text: str) -> PolicyResult:
    """섬네일 텍스트와 영상 제목의 정책 준수 검증.

    검증 항목:
    1. 금지 키워드 (성적/폭력/혐오) → 차단
    2. 클릭베이트 패턴 → 경고
    3. 섬네일-제목 관련성 → 경고

    Args:
        title: 영상 제목
        thumbnail_text: 섬네일에 들어간 텍스트
    """
    result = PolicyResult()
    combined = f"{title} {thumbnail_text}".lower()

    # 금지 키워드 검사
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in combined:
            result.add_block("금지 콘텐츠", f"'{keyword}' 감지 → 3 Strike 위험")

    # 클릭베이트 패턴 검사
    for pattern in CLICKBAIT_PATTERNS:
        if pattern.lower() in combined:
            result.add_warning("클릭베이트", f"'{pattern}' 감지 → 정책 위반 가능성")

    # 섬네일-제목 관련성 (기본: 공통 단어 존재 여부)
    title_words = set(title.replace(" ", ""))
    thumb_words = set(thumbnail_text.replace(" ", ""))
    if title_words and thumb_words:
        overlap = title_words & thumb_words
        if len(overlap) == 0:
            result.add_warning(
                "관련성",
                "섬네일 텍스트와 영상 제목 간 공통 문자 없음 → 클릭베이트 의심"
            )

    return result


def check_all(title: str, thumbnail_text: str, image_path: str | None = None) -> PolicyResult:
    """전체 정책 검증 실행.

    Args:
        title: 영상 제목
        thumbnail_text: 섬네일 텍스트
        image_path: 이미지 경로 (향후 이미지 안전 검증용)
    """
    result = check_text_policy(title, thumbnail_text)

    # 향후: 이미지 안전 검증 (Google Vision SafeSearch 등)
    # if image_path:
    #     image_result = check_image_safety(image_path)
    #     result.merge(image_result)

    return result
