# 반복 가능한 영상 제작 워크플로

이 저장소는 영상 한 편을 `기획 → 대본 승인 → TTS 샘플 승인 → 1.7B 장면 단위 TTS·SRT·받아쓰기 검수 → 독립 씬 제작 → 실제 예시·자체 설명 페어 → 음악 승인 → 게임 원음·BGM 믹스 → 최종 검수 → 게시` 순서로 제작합니다. 각 단계의 기준 파일과 승인 상태를 분리해, 수정할 때 무엇을 다시 생성해야 하는지 명확하게 유지합니다.

내레이션과 오디오의 상세 수치·완료 조건은
[내레이션·자막·오디오 제작 기준](NARRATION_AUDIO_STANDARD.md)을 단일 기준으로
사용합니다.

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
기본 대본의 도입·본론·결론에 대응하는 독립 씬 3개와, 첫 TTS 전에도 편집기를
열 수 있는 짧은 무음 내레이션 파일이 함께 생성됩니다.

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
- `scenes[].id` 하나는 Motion Canvas 씬 하나에 대응시킵니다.
- 숫자와 고유명사는 TTS가 자연스럽게 읽는 표기로 씁니다.
- 도입, 기본 원리, 사례, 결론의 순서를 유지합니다.
- 최종 생성 전에 대본을 직접 소리 내어 읽습니다.

대본은 TTS, SRT, 장면 타이밍의 기준 파일입니다. 대본이 바뀌면 음성부터 다시 생성합니다.

## 4. TTS 샘플 승인과 전체 TTS·SRT

기본 모델은 `Qwen3-TTS-12Hz-1.7B-Base`입니다. 기준 음성과 정확히 일치하는
발화문을 함께 사용하고, 같은 장면의 문장을 한 번에 읽게 합니다. 문장별 개별 합성은
종결 어미가 반복적으로 끊겨 들릴 수 있으므로 기본값으로 사용하지 않습니다.

전체 생성 전에 20~40초 정도의 비교 샘플로 목소리, 속도와 톤을 승인받습니다.
승인된 뒤 다음 통합 명령을 실행합니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/generate_sample.py `
  --project <slug> --scene 01
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/build-project-narration.ps1 -Project <slug>
```

이 명령은 장면별 TTS와 한국어 SRT, 번역 대본이 있을 때 영어 SRT, Motion Canvas
타이밍, 전체 Whisper 받아쓰기 검토 파일을 생성합니다. 중단 후 다시 실행하면 품질
검사를 통과한 장면 WAV는 재사용합니다.

생성 후 확인할 항목:

- 문장 끝이 잘리지 않았는가?
- 고유명사 발음이 자연스러운가?
- 문장 사이 휴지가 너무 짧거나 길지 않은가?
- 전체 속도가 영상 톤과 맞는가?
- 전체 받아쓰기에 누락·반복·잘못 읽힌 숫자나 고유명사가 없는가?
- SRT 번호와 타임코드가 음성과 일치하는가?

번역 자막은 한국어 SRT의 타임코드를 유지하고 텍스트만 번역합니다.

## 5. Motion Canvas와 Manim 분담

대본의 각 장면은 별도 Motion Canvas 씬으로 유지합니다. 모든 내용을 하나의
`main` 씬에 넣지 않습니다. `build_project_timing.py`가 실제 음성 길이를 씬별로
동기화하므로 장면 코드는 생성된 `timing.ts` 값을 사용합니다.

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

## 6. 실제 예시와 자체 설명 화면

기본 장면 구조는 `실제 게임·공식 기술 예시 영상 1개 → 같은 개념의 채널 제작
그래픽 1개`입니다. 실제 예시는 보통 5~10초만 사용합니다. 긴 설명은 하나의 긴
클립보다 리플레이, 확대, 슬로 모션과 프레임 스텝으로 나눕니다.

- 영상의 중요한 동작이 자막이나 그래픽에 가리지 않는지 확인합니다.
- 게임 예시에는 효과음·환경음 중심의 원음을 보존하고 내레이션보다 작게 둡니다.
- 원본 음악의 권리가 불명확하면 음악이 적은 구간을 고르거나 그 부분만 제거합니다.
- 실제 사용 파일, 원본 링크, 구간, 화면·원음 사용 여부를 출처 문서에 남깁니다.
- 라이선스나 사용 허용을 확인하지 못한 파일은 게시본에서 제외합니다.

## 7. BGM 후보 승인과 오디오 믹스

자체 설명 화면처럼 내레이션만 있는 구간에는 잔잔한 BGM을 사용합니다. 음악을
선택하기 전에 곡명, 원본 미리듣기 링크, 라이선스, 출처 표기와 영상 적합성을 먼저
제시합니다. 사용자가 곡을 선택하기 전에는 다운로드·믹스·최종 렌더를 진행하지
않습니다.

승인 뒤 `project.json`의 `audio.backgroundMusic`을 갱신하고 다음 기준으로 믹스합니다.

- 내레이션: 약 -16 LUFS, true peak -1.5 dBTP 이하
- 게임 원음: 내레이션보다 약 14~18dB 작게
- BGM: 내레이션보다 약 18~24dB 작게
- 내레이션 중 BGM을 약 4~8dB 더 낮추는 덕킹 적용
- 게임 원음 구간에서는 BGM을 더 낮추거나 잠시 끄기

## 8. 렌더와 검수

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
- 게임 예시 구간의 작은 원음과 자체 설명 구간의 BGM이 의도대로 들리는가?
- 내레이션, 원본 음악과 BGM이 서로 경쟁하지 않는가?

프로젝트 매니페스트에 최종 경로를 기록한 뒤 검사합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/check-video-project.ps1 -Project <slug> -Stage publish
```

음성 생성 직후에는 `-Stage narration`, 최종 MP4가 준비된 뒤에는 `-Stage publish`를
사용합니다. 음악 승인이 `pending`인 프로젝트는 게시 검사를 통과하면 안 됩니다.

## 9. YouTube 게시

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
| B-roll·원음 | 소스 기록 + Motion Canvas B-roll 설정 | 정규화 클립, 편집 큐, 원음 믹스 |
| 음악 | `project.json` 승인 정보 + 출처 문서 | 최종 오디오 믹스, 설명란 출처 |
| 영상 | Motion Canvas·Manim 소스 | MP4, 스틸 이미지 |
| 게시 | `projects/<slug>/publishing/` | YouTube 입력 내용 |

생성 파일을 직접 수정하기보다 기준 파일을 고친 뒤 다시 생성해야 다음 수정에서도 내용이 어긋나지 않습니다.
