# CleanTube Studio MVP

원본 EXE의 코드를 복사하지 않고, 기능 목적만 참고해 새로 작성한 클린룸 방식의 MVP입니다.

## 제공 기능
- 로컬 웹 UI
- API 설정 저장 및 마스킹 표시
- 주제 기반 대본 초안 생성
- 장면 분할 및 비주얼 프롬프트 생성
- 유튜브 제목/설명/태그 메타데이터 생성
- 프로젝트 JSON 저장
- 제작 계획 Markdown 내보내기
- 장면 자막 SRT 생성 유틸리티

## 실행 방법

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python app.py
```

브라우저에서 `http://127.0.0.1:5055` 접속.

## AI 연동
설정 화면에서 OpenAI-compatible API 정보를 넣으면 `/chat/completions` 형태의 호환 API로 대본/메타데이터 생성을 시도합니다.
키가 없으면 로컬 템플릿 기반 샘플 결과를 반환합니다.

## 주의
- 원본 프로그램의 소스, 프롬프트 원문, 폰트, 이미지, 비공개 리소스는 포함하지 않았습니다.
- 영상/TTS/이미지 생성은 서비스별 API 정책과 키가 필요하므로 확장 포인트만 포함했습니다.

## Windows에서 가장 쉬운 실행

1. ZIP 압축을 풉니다.
2. `run_windows.bat`을 더블클릭합니다.
3. 처음 실행 시 필요한 패키지를 설치합니다.
4. 브라우저가 열리면 `http://127.0.0.1:5055`에서 사용합니다.

## EXE로 만들기

현재 ZIP은 소스 프로젝트이며, 바로 실행되는 `.exe`는 아닙니다. Windows PC에서 아래 파일을 더블클릭하면 EXE를 빌드합니다.

```bat
build_exe_windows.bat
```

성공하면 다음 위치에 생성됩니다.

```text
dist\CleanTubeStudio.exe
```

생성된 EXE를 더블클릭하면 로컬 서버가 실행되고 브라우저가 열립니다. 첫 실행 때 Windows Defender SmartScreen 경고가 나올 수 있습니다. 서명되지 않은 개인 빌드라서 생기는 일반적인 경고입니다.
