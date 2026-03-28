"""섬네일 생성 CLI.

사용법:
    python -m src.generator.cli --template tech-gradient --title "AI 자동화" --output output/thumb.png
    python -m src.generator.cli --list
"""

import argparse
import sys
from pathlib import Path

from . import api_client, prompt_builder


def main():
    parser = argparse.ArgumentParser(description="유튜브 섬네일 생성기")
    parser.add_argument("--list", action="store_true", help="사용 가능한 템플릿 목록")
    parser.add_argument("--template", "-t", help="프롬프트 패턴 ID")
    parser.add_argument("--title", help="영상 제목 (한글, 5자 이내 권장)")
    parser.add_argument("--output", "-o", default="output/thumbnail.png", help="출력 경로")
    parser.add_argument("--model", default="gemini-2.5-pro-preview-06-05", help="모델 ID")

    args = parser.parse_args()

    if args.list:
        patterns = prompt_builder.list_patterns()
        print("사용 가능한 템플릿:")
        for p in patterns:
            print(f"  {p['id']:20s} {p['name']}  →  {', '.join(p['best_for'])}")
        return

    if not args.template or not args.title:
        parser.error("--template과 --title은 필수입니다. (--list로 템플릿 확인)")

    prompt = prompt_builder.build_prompt(args.template, args.title)
    print(f"패턴: {args.template}")
    print(f"제목: {args.title}")
    print(f"프롬프트: {prompt[:100]}...")
    print()

    client = api_client.create_client()
    result = api_client.generate_thumbnail(client, prompt, args.output, model=args.model)
    print(f"완료: {result}")


if __name__ == "__main__":
    main()
