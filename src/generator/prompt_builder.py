"""프롬프트 템플릿 로딩 및 변수 치환."""

import json
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "config" / "prompts"
BRAND_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "brand.json"


def load_patterns(patterns_path: Path | None = None) -> dict:
    """prompt-patterns.json 로드."""
    path = patterns_path or PROMPTS_DIR / "prompt-patterns.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_brand(brand_path: Path | None = None) -> dict:
    """brand.json 로드."""
    path = brand_path or BRAND_PATH
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_patterns(patterns_path: Path | None = None) -> list[dict]:
    """사용 가능한 프롬프트 패턴 목록 반환."""
    data = load_patterns(patterns_path)
    return [
        {"id": p["id"], "name": p["name"], "best_for": p["best_for"]}
        for p in data["patterns"]
    ]


def build_prompt(pattern_id: str, title: str, patterns_path: Path | None = None) -> str:
    """패턴 ID + 영상 제목으로 완성 프롬프트 생성.

    Args:
        pattern_id: 프롬프트 패턴 ID (예: "tech-gradient")
        title: 영상 제목 (한글, 5자 이내 권장)
        patterns_path: prompt-patterns.json 경로 (기본: config/prompts/)

    Returns:
        변수가 치환된 완성 프롬프트 문자열
    """
    data = load_patterns(patterns_path)
    pattern = next((p for p in data["patterns"] if p["id"] == pattern_id), None)
    if pattern is None:
        available = [p["id"] for p in data["patterns"]]
        raise ValueError(f"패턴 '{pattern_id}' 없음. 사용 가능: {available}")

    prompt = pattern["prompt"].replace("{{title}}", title)
    return prompt
