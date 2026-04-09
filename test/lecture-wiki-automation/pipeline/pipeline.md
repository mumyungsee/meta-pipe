# Andrej Karpathy 스타일 강의록 위키 자동 생성 파이프라인

원본 사례: https://github.com/xoai/sage-wiki

## 수정 사항

| # | 변경 | 이유 |
|---|------|------|
| 1 | Go 직접 빌드 → GitHub Releases 빌드된 바이너리 다운로드 | 사용자 stack에 Go 없음. beginner 역량이므로 빌드 과정 생략 |
| 2 | 유료 LLM API → Ollama (로컬 LLM) 사용 | 사용자 budget 제약: 유료 API 제외. sage-wiki가 Ollama를 공식 지원 |
| 3 | config.yaml 수동 작성 → AI가 Ollama용 설정 초안 생성 | beginner 역량. LLM provider 설정이 복잡하므로 AI가 대신 작성 |
| 4 | 마크다운 소스 수동 작성 → Claude Code로 강의록 자동 생성 | 사용자 도구에 Claude Code 포함. 강의록→마크다운 변환 자동화가 핵심 목표 |

## Steps

### Step 1: Ollama 설치 + 모델 다운로드 [manual]
1. https://ollama.ai 에서 OS에 맞는 Ollama 설치
2. 터미널에서 `ollama pull llama3.2` 실행 (또는 원하는 모델)
3. `ollama list`로 모델 설치 확인
> 기대 결과: ollama list에서 모델이 표시됨
> 도구: 브라우저, 터미널

### Step 2: sage-wiki 바이너리 다운로드 [manual]
1. https://github.com/xoai/sage-wiki/releases 에서 최신 릴리스 확인
2. OS에 맞는 바이너리 다운로드 (Windows: sage-wiki.exe, Mac: sage-wiki-darwin)
3. PATH에 추가하거나 프로젝트 폴더에 배치
4. `sage-wiki --version`으로 설치 확인
> 기대 결과: sage-wiki --version이 버전 번호를 출력
> 도구: 브라우저, 터미널

### Step 3: 프로젝트 초기화 + config.yaml 생성 [assist]
1. `sage-wiki init`으로 프로젝트 초기화
2. AI가 Ollama를 provider로 설정한 config.yaml 초안을 생성
3. 사용자가 config.yaml 내용을 확인하고 필요 시 수정
4. 소스 폴더 경로를 강의록 디렉토리로 지정
> 기대 결과: config.yaml이 Ollama provider로 설정되고 소스 폴더가 지정됨
> 도구: 터미널, Claude Code

### Step 4: 강의록 마크다운 소스 생성 [auto]
Claude Code로 주제별 강의록을 마크다운 파일로 생성. 각 파일은 하나의 강의 주제를 담고, 제목/개요/핵심내용/참고자료 구조를 따름. 소스 폴더에 저장.
> 기대 결과: 소스 폴더에 주제별 .md 파일 생성 (최소 3개)
> 도구: Claude Code

### Step 5: sage-wiki compile 실행 [assist]
1. `sage-wiki compile` 실행
2. 컴파일 결과 확인 (생성된 위키 문서 수, 인터링크 수)
3. 오류 발생 시 AI가 에러 메시지 분석 후 수정 제안
4. 필요 시 config.yaml 수정 후 재실행
> 기대 결과: 컴파일 완료. 위키 문서가 output 폴더에 생성됨
> 도구: 터미널, Claude Code

### Step 6: 위키 UI 확인 [assist]
1. `sage-wiki serve`로 웹 UI 실행 (기본 포트: localhost:8080)
2. 브라우저에서 위키 페이지 탐색
3. 위키링크 클릭 동작 확인
4. 지식 그래프 시각화 확인
5. 검색 기능 테스트
> 기대 결과: 웹 UI에서 위키 문서가 표시되고 위키링크/검색이 동작
> 도구: 터미널, 브라우저
