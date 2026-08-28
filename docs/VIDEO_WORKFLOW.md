# 반복 가능한 영상 제작 워크플로

이 저장소는 영상 한 편을 `기획 → 대본 → TTS/SRT → Motion Canvas·Manim → B-roll → 검수 → 게시` 순서로 제작합니다. 각 단계의 기준 파일을 분리해 두어, 수정할 때 무엇을 다시 생성해야 하는지 명확하게 유지하는 것이 핵심입니다.

## 1. 새 프로젝트 생성

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/new-video-project.ps1 `
  -Slug "camera-shake" `
  -TitleKo "카메라 흔들림은 어떻게 손맛을 만들까?" `
  -TitleEn "How Does Camera Shake Create Impact?"
```

생성되는 위치:

```text
projects/camera-shake/                    # 기획·대본·출처·게시 정보
motion-canvas/src/projects/camera-shake/  # Motion Canvas 시작 프로젝트
manim/projects/camera-shake/              # Manim 시작 프로젝트
```

Motion Canvas 프로젝트는 `motion-canvas/projects.json`에 자동 등록됩니다.

## 2. 기획

먼저 `projects/<slug>/planning/outline.md`를 작성합니다.

- 이 영상이 답할 질문은 무엇인가?
- 시청자가 끝까지 보고 기억할 한 문장은 무엇인가?
- 설명만 할 부분과 실제 화면으로 보여 줄 부분은 어디인가?
- 도입 30~45초 안에 영상의 약속이 드러나는가?
- 결론에서 시청자가 직접 적용할 방법을 제시하는가?

게임 영상이나 외부 이미지를 사용할 예정이라면 이 단계부터 `sources/SOURCES.md`에 후보 링크와 허용 근거를 기록합니다.

## 3. 대본

`projects/<slug>/script/narration.ko.json`을 장면 단위로 작성합니다.

권장 규칙:

- 한 줄에는 한 가지 정보만 둡니다.
- 화면 전환이 필요한 지점에서 장면을 나눕니다.
- 숫자와 고유명사는 TTS가 자연스럽게 읽는 표기로 씁니다.
- 도입, 기본 원리, 사례, 결론의 순서를 유지합니다.
- 최종 생성 전에 대본을 직접 소리 내어 읽습니다.

대본은 TTS, SRT, 장면 타이밍의 기준 파일입니다. 대본이 바뀌면 음성부터 다시 생성합니다.

## 4. TTS와 SRT

Qwen3-TTS 파이프라인은 프로젝트 매니페스트의 대본, 음성 참조, 모델, 출력 경로를 읽습니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/render_narration.py --project <slug>
```

중단 후 다시 실행하면 품질 검사를 통과한 문장별 WAV는 재사용하고, 필요한 문장만 다시 생성합니다. 생성 결과는 매니페스트의 `tts.outputDir`에 저장됩니다.

생성 후 확인할 항목:

- 문장 끝이 잘리지 않았는가?
- 고유명사 발음이 자연스러운가?
- 문장 사이 휴지가 너무 짧거나 길지 않은가?
- 전체 속도가 영상 톤과 맞는가?
- SRT 번호와 타임코드가 음성과 일치하는가?

번역 자막은 한국어 SRT의 타임코드를 유지하고 텍스트만 번역합니다.

## 5. Motion Canvas와 Manim 분담

### Motion Canvas가 적합한 부분

- 텍스트, 제목, 강조 표시
- UI, 다이어그램, 장면 전환
- 내레이션에 맞춘 전체 타임라인
- 게임 영상 B-roll 합성

### Manim이 적합한 부분

- 좌표축, 수식, 그래프
- 물리 궤적 비교
- 값을 바꿨을 때의 수학적 변화
- 독립적인 설명용 클립

Manim 클립을 먼저 렌더한 뒤 Motion Canvas의 영상 에셋으로 넣거나, 최종 단계에서 `scripts/combine.ps1`로 이어 붙일 수 있습니다.

```powershell
# Motion Canvas
npm start

# 특정 Manim 프로젝트
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/render-manim.ps1 -Project camera-shake -Quality qh
```

## 6. B-roll과 출처

한 게임 화면은 일반적으로 8~15초 정도가 내용을 파악하기 좋습니다. 긴 설명은 하나의 30초 클립을 그대로 두기보다 리플레이, 확대, 슬로 모션, 프레임 스텝으로 나눕니다.

- 영상의 중요한 동작이 자막이나 그래픽에 가리지 않는지 확인합니다.
- 내레이션 아래 게임 원음은 보통 약 -16~-20dB에서 시작해 조절합니다.
- 실제 사용한 파일, 원본 링크, 사용 구간을 출처 문서에 남깁니다.
- 라이선스나 사용 허용을 확인하지 못한 파일은 게시본에서 제외합니다.

## 7. 렌더와 검수

최종 렌더 권장값:

- 1920×1080
- 60fps
- H.264 영상 + AAC 오디오
- 무자막 본편을 기준 파일로 보관
- 디자인 고정이 필요한 경우에만 별도 고정 자막 버전 생성

게시 전에는 처음부터 끝까지 한 번 재생하며 다음을 확인합니다.

- 음성과 장면 전환이 맞는가?
- 검은 화면, 프레임 멈춤, 영상 반복 오류가 없는가?
- B-roll 출처와 파일명이 일치하는가?
- 자막 오탈자와 줄바꿈이 자연스러운가?
- 음량이 장면마다 갑자기 달라지지 않는가?

프로젝트 매니페스트에 최종 경로를 기록한 뒤 검사합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project <slug> -Stage publish
```

## 8. YouTube 게시

`projects/<slug>/publishing/`에서 언어별 제목, 설명, 챕터를 관리합니다.

권장 구성:

- 유튜브 본편: 무자막 영상 + 언어별 SRT
- 영상 내부: 핵심 단어와 꼭 필요한 모션 자막만 사용
- 쇼츠·SNS: 고정 자막 버전 사용
- 설명란: 핵심 검색어를 첫 두 줄에 자연스럽게 포함
- 챕터: 반드시 `00:00`부터 시작

업로드 후에는 실제 모바일 화면에서 제목 잘림, 썸네일 가독성, 자막 위치를 확인합니다.

## 기준 파일과 생성 파일

| 종류 | 기준 파일 | 다시 생성되는 파일 |
| --- | --- | --- |
| 내용 | `projects/<slug>/script/narration.ko.json` | WAV, 한국어 SRT, timing JSON |
| 장면 길이 | timing JSON + 장면 구간 설정 | Motion Canvas 타이밍 코드 |
| B-roll | Motion Canvas B-roll 설정 | 편집 큐 MD/CSV |
| 영상 | Motion Canvas·Manim 소스 | MP4, 스틸 이미지 |
| 게시 | `projects/<slug>/publishing/` | YouTube 입력 내용 |

생성 파일을 직접 수정하기보다 기준 파일을 고친 뒤 다시 생성해야 다음 수정에서도 내용이 어긋나지 않습니다.
