"""섬네일 기술 규격 검증."""

from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image


@dataclass
class CheckResult:
    passed: bool
    checks: list[dict] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str):
        self.checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            self.passed = False

    def report(self) -> str:
        lines = []
        for c in self.checks:
            icon = "PASS" if c["passed"] else "FAIL"
            lines.append(f"  [{icon}] {c['name']}: {c['detail']}")
        status = "통과" if self.passed else "실패"
        lines.insert(0, f"품질 검증: {status} ({sum(c['passed'] for c in self.checks)}/{len(self.checks)})")
        return "\n".join(lines)


def check_thumbnail(image_path: str | Path) -> CheckResult:
    """섬네일 이미지의 기술 규격을 검증.

    검증 항목:
    - 파일 존재
    - 파일 크기 <= 2MB
    - 해상도 1280x720 권장 (최소 640x360)
    - 포맷 JPEG/PNG
    - 16:9 비율
    """
    result = CheckResult(passed=True)
    path = Path(image_path)

    # 파일 존재
    if not path.exists():
        result.add("파일 존재", False, f"파일 없음: {path}")
        return result
    result.add("파일 존재", True, str(path))

    # 파일 크기
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 2.0:
        result.add("파일 크기", False, f"{size_mb:.2f}MB > 2MB 제한")
    else:
        result.add("파일 크기", True, f"{size_mb:.2f}MB")

    # 이미지 열기
    try:
        img = Image.open(path)
    except Exception as e:
        result.add("이미지 포맷", False, f"이미지 열기 실패: {e}")
        return result

    # 포맷
    fmt = img.format
    if fmt in ("JPEG", "PNG"):
        result.add("포맷", True, fmt)
    else:
        result.add("포맷", False, f"{fmt} (JPEG 또는 PNG만 허용)")

    # 해상도
    w, h = img.size
    if w >= 1280 and h >= 720:
        result.add("해상도", True, f"{w}x{h}")
    elif w >= 640 and h >= 360:
        result.add("해상도", True, f"{w}x{h} (권장: 1280x720)")
    else:
        result.add("해상도", False, f"{w}x{h} (최소 640x360)")

    # 비율 (16:9 = 1.777...)
    ratio = w / h
    if 1.7 <= ratio <= 1.85:
        result.add("비율", True, f"{ratio:.3f} (16:9)")
    else:
        result.add("비율", False, f"{ratio:.3f} (16:9 = 1.778 필요)")

    img.close()
    return result
