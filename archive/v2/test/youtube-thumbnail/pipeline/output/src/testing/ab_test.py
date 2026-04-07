"""A/B 테스트: 동일 영상에 여러 템플릿으로 섬네일 변형 생성.

사용법:
    python -m src.testing.ab_test --title "AI 자동화" --templates tech-gradient,screen-glow,ai-neural
"""

import argparse
from pathlib import Path

from src.generator import api_client, prompt_builder
from src.validator import quality_checker


def generate_variants(
    title: str,
    templates: list[str],
    output_dir: str = "output/ab_test",
) -> list[dict]:
    """동일 제목에 대해 여러 템플릿으로 변형 생성.

    Returns:
        [{template, image_path, quality_passed}]
    """
    client = api_client.create_client()
    results = []

    for i, template in enumerate(templates, 1):
        print(f"\n[{i}/{len(templates)}] 템플릿: {template}")
        prompt = prompt_builder.build_prompt(template, title)
        output_path = Path(output_dir) / f"variant_{template}.png"

        try:
            saved = api_client.generate_thumbnail(client, prompt, output_path)
            quality = quality_checker.check_thumbnail(saved)
            results.append({
                "template": template,
                "image_path": str(saved),
                "quality_passed": quality.passed,
            })
            print(f"  생성 완료: {saved} (품질: {'통과' if quality.passed else '실패'})")
        except Exception as e:
            results.append({
                "template": template,
                "image_path": None,
                "quality_passed": False,
                "error": str(e),
            })
            print(f"  실패: {e}")

    print(f"\n변형 생성 완료: {len([r for r in results if r['quality_passed']])}/{len(results)} 통과")
    return results


def main():
    parser = argparse.ArgumentParser(description="A/B 섬네일 변형 생성")
    parser.add_argument("--title", required=True, help="영상 제목")
    parser.add_argument("--templates", required=True, help="쉼표 구분 템플릿 ID")
    parser.add_argument("--output-dir", default="output/ab_test", help="출력 디렉토리")

    args = parser.parse_args()
    templates = [t.strip() for t in args.templates.split(",")]
    generate_variants(args.title, templates, args.output_dir)


if __name__ == "__main__":
    main()
