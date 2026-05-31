# CleanTube Studio

Windows에서 로그인 없이 바로 실행하는 로컬 영상 제작 보조 프로그램입니다.

이 저장소는 원본 EXE의 코드, 리소스, 비공개 프롬프트를 복사하지 않고 현재 프로젝트 파일만으로 만든 클린룸 MVP입니다.

## 무엇을 할 수 있나요?

- 주제를 입력하면 대본 초안을 만듭니다.
- 장면별 비주얼 프롬프트를 만듭니다.
- 유튜브 제목, 설명, 태그 초안을 만듭니다.
- 프로젝트를 JSON으로 저장합니다.
- 제작 계획을 Markdown으로 내보냅니다.
- 자막 SRT 파일을 다운로드합니다.
- ElevenLabs API 키를 선택으로 저장합니다.
- ElevenLabs API 키가 없으면 TTS 기능만 비활성화하고 안내 메시지를 보여줍니다.

## 로그인과 API 키

로그인, 회원가입, 구독 확인은 없습니다.

프로그램은 API 키 없이 실행됩니다. 대본, 프롬프트, 메타데이터는 로컬 템플릿으로 생성됩니다.

설정 화면에는 ElevenLabs API 키 입력칸만 있습니다. 이 키는 선택 사항이며, 입력하지 않아도 프로그램 사용에는 문제가 없습니다.

## Windows에서 실행하기

1. GitHub에서 ZIP 파일을 다운로드합니다.
2. ZIP 압축을 풉니다.
3. 폴더 안의 `run_windows.bat`를 더블클릭합니다.
4. 처음 실행할 때 필요한 파일을 자동으로 설치합니다.
5. 브라우저가 열리면 `http://127.0.0.1:5055`에서 사용합니다.

Python이 없다는 메시지가 나오면 [python.org](https://www.python.org/downloads/)에서 Python 3.10 이상을 설치한 뒤 다시 실행하세요. 설치할 때 Add Python to PATH 옵션을 켜면 편합니다.

## EXE 만들기

Windows PC에서 `build_exe_windows.bat`를 더블클릭합니다.

성공하면 아래 파일이 생성됩니다.

```text
dist\CleanTubeStudio.exe
```

생성된 EXE를 더블클릭하면 로컬 서버가 실행되고 브라우저가 열립니다.

개인 빌드라서 Windows Defender SmartScreen 경고가 나올 수 있습니다. 서명되지 않은 EXE에서 흔히 보이는 경고입니다.

## GitHub Actions 자동 빌드

저장소의 Actions 탭에서 `Build Windows EXE` 워크플로를 실행하면 Windows EXE를 자동으로 빌드합니다.

빌드가 끝나면 workflow run의 Artifacts에서 `CleanTubeStudio-Windows`를 다운로드할 수 있습니다.

## 저장 위치

설정 파일은 사용자 폴더 아래 `.cleantube_studio`에 저장됩니다.

프로젝트 저장 파일은 실행 폴더의 `data/projects`에 저장됩니다.

Markdown과 SRT 내보내기 파일은 실행 폴더의 `exports`에 저장됩니다.

## 개발자용 실행

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

그 다음 브라우저에서 `http://127.0.0.1:5055`를 엽니다.
