# 다른 컴퓨터에서 작업 이어가기

2026-10-14 재부팅 후 인계. Git에는 제작 코드·대본·자막·편집 설정·출처·검수 기록·체크포인트를 전달합니다. 완성 영상, 게임 원본, TTS/음악, 모델, 압축 미디어는 포함하지 않습니다. 기존 파일을 삭제하거나 제작을 다시 시작하는 작업이 아닙니다.

먼저 [프로젝트별 인계 목록](../production/handoff/project-index.json), 현재 `AGENTS.md`, [제작 제어](../shared/publishing/video-production-control.json), [통합 제작 규칙](VIDEO_WORKFLOW.md)을 읽으세요. 목록의 상태는 저장된 제작 기록이며 현재 YouTube 공개 상태나 새 컴퓨터의 실행 성공을 보증하지 않습니다. 다른 컴퓨터에서 추가한 원격 작업도 보존합니다.

## 새 컴퓨터의 시작 순서

새 컴퓨터에는 새 폴더로 clone하는 것이 가장 간단합니다. 2026-09-29 이력 정리 전 clone은 개인 변경을 별도 보관하고 새로 clone하세요. 이미 현재 이력을 사용하는 깨끗한 clone이면 `git pull --ff-only`로 갱신할 수 있습니다. 실패하면 강제 reset하지 말고 로컬 변경·분기를 확인합니다.

```powershell
git clone https://github.com/eazuooz/Video-Editing.git Video-Editing-clean
cd Video-Editing-clean
npm ci --prefix motion-canvas
```

1. 사용자가 고른 **한 영상**의 `project.json`, 해당 revision의 체크포인트·인계 문서·검수 장부를 읽습니다. `project-index.json`의 `checkpointCandidates`는 탐색용입니다. 최신 수정본이 진행 중이면 root manifest의 납품 경로는 이전 완성본일 수 있습니다.
2. `projects/<slug>/rebuild.json`의 대본·편집기 소스·컷·원본 URL과 현재 revision의 타임라인을 함께 확인합니다. supporting/history 항목을 전부 현재 입력으로 취급하지 않습니다. 기존 소스가 가리키는 다른 프로젝트의 공통 장면·함수도 보존합니다.
3. 필요한 미디어만 개인 백업/별도 전달 경로에서 복원합니다. 파일 경로·크기·기록된 SHA256을 대조합니다. 새 다운로드가 동일 바이트라는 보장은 없으므로 다르면 사용 범위와 컷을 다시 확인합니다. 기존 TTS를 복원하는 것이 우선이며, 재합성은 같은 길이·발음·바이트를 보장하지 않습니다.
4. [실행 환경 관측값](../production/handoff/runtime-observation.json)과 해당 실행기의 import/설정을 확인해 필요한 환경만 설치합니다. `.venv`, `node_modules`, 모델 캐시는 복사된 Git 폴더에 자동으로 생기지 않습니다. Python 실행기·FFmpeg·폰트·브라우저 경로를 새 컴퓨터에 맞추고, 지원되는 환경변수/설정으로 지정합니다. 예전 PC의 절대경로를 모든 파일에서 일괄 치환하지 않습니다.
5. 체크포인트의 `running`, PID, session ID, localhost 포트는 **이전 PC의 관측 기록**입니다. 재부팅 후 작업 생존의 증거가 아닙니다. 완료 산출물과 입력 해시를 먼저 검사하고, 재개 기능이 있으면 남은 부분만 이어갑니다. 완료 TTS·ASR·렌더·검수를 처음부터 재실행하지 않습니다.
6. 수정한 범위와 연결부를 검수하고 새 인코딩의 전체 decode/PTS/오디오 무결성을 확인합니다. 납품 단계에 도달했을 때만 `node scripts/collect-video-output.cjs <slug>`로 clean/captioned/KO/EN을 모읍니다. 이번 Git 인계 요청은 제작·업로드·예약·삭제·다음 영상의 추가 승인이 아닙니다.

```powershell
# 필요한 자산을 옮긴 뒤 편집기 실행
npm start -- --host 127.0.0.1 --port 9100
# 선택한 프로젝트의 재현 목록만 검사
node scripts/build-rebuild-manifests.cjs <slug> --check
npm run media:check
```

Motion Canvas: http://127.0.0.1:9100/ . 전체 빌드는 등록된 모든 프로젝트의 미디어를 요구할 수 있습니다. 선택 프로젝트의 전용 설정/실행기를 먼저 사용합니다. 전체 rebuild manifest를 무조건 재작성하거나 다른 작업의 Git index를 초기화하지 않습니다.

## 지금 확인할 작업

- **렌더링 역사 1편의 초심자 보강본**: `projects/game-lighting-history-01/production/beginner-revision-v1/HANDOFF.md`와 `production/checkpoint.json`. 별도 제작 채팅이 작성한 구체적인 재개 절차·미디어 전송 목록이 우선입니다. 재부팅 전 현재 믹스 ASR 01~03이 저장됐고 최종 합성/새 업로드는 미완료였습니다. 이후 기록이 있으면 그 기록부터 이어갑니다.
- **계층형 디자인**: `projects/hierarchical-game-outlines/production/pokemon-opening-v2/latest-checkpoint.json`. 최종 비공개 `x04OdXSt98U` 전달 완료, 요청받은 이전 중복 `Bjh2e5f5ync` 삭제 검증 완료입니다. 완료 업로드/삭제를 반복하지 않습니다.
- **다른 컴퓨터의 AI 게임 제작 영상**: `projects/ai-game-development-human-craft/project.json` 및 그 프로젝트의 현재 진행 기록. 원격 소스와 Unity 장면은 이 인계의 부모 이력에 보존합니다. 이 컴퓨터에 없던 파일을 삭제로 해석하지 않습니다.
- **다른 게임 디자인·게임수학·렌더링 역사 편**: 프로젝트별 목록에서 현재 manifest와 revision을 찾습니다. 오래된 batch `ACTIVE`, 4게임 규칙, 과거 예약 날짜는 현재 제작 제어를 대체하지 않습니다. 새 채팅에서 사용자가 고른 편만 진행합니다.

## Git 밖에서 필요한 것

| 종류 | 새 컴퓨터에서 복원할 자료 |
| --- | --- |
| 독립 게임/엔진 촬영 원본 | 현재 source/cut 목록의 파일, URL, 선택 구간과 권리 근거 |
| 승인 음성 | 현재 타이밍에 사용된 문장/장면 PCM, 타이밍 JSON에 대응하는 원본 |
| 개인 목소리 레퍼런스 | `shared/voice-reference/`의 실제 녹음·대응 원문을 비공개 전달 |
| BGM·게임 효과음 | 승인 트랙/유용한 원음과 라이선스·출처, 현재 믹스에 쓰인 버전 |
| 로고·회원·썸네일·폰트 | Git에 이미 있는 필수 자산 외 누락된 원본을 실제 경로에 복원 |
| 모델과 도구 | Qwen3-TTS 1.7B, 해당 ASR 모델, Python/CUDA/FFmpeg/렌더러 환경 |

완성 MP4와 모든 과거 QA 이미지를 옮길 필요는 없습니다. 다만 완료된 장면/PCM을 그대로 이어 쓰려면 해당 중간 미디어는 별도로 있어야 합니다. Git은 그 바이트를 대신 보관하지 않으며, 외부 백업/전송은 실제 확인 전까지 pending입니다.

## 새 채팅에 붙여 넣을 문장

> 이 저장소의 최신 main을 확인하고 `docs/CONTINUE_ON_ANOTHER_COMPUTER.md`와 `production/handoff/project-index.json`을 읽어 줘. 내가 선택한 `<영상 slug>`의 현재 revision 체크포인트에서 이어가자. 필요한 로컬 미디어와 실행 환경부터 확인하고, 완료된 제작/검수/업로드는 반복하지 마. 다른 영상·자동 채팅·배치는 시작하지 말고, 선택한 한 영상의 현재 승인 범위를 지켜 줘.

기존 `shared/media-archives/**/manifest.json`은 남아 있지만 압축 조각은 Git에서 제거되었습니다. 조각을 개인 백업에서 옮긴 경우에만 `node scripts/restore-media.cjs --project <slug>`로 해시 검증 복원할 수 있습니다. 이전의 “clone만 하면 완성 영상을 복원” 안내는 폐기합니다.

Unity는 `unity/` 폴더, Unreal은 `unreal/VideoEditing.uproject`를 엽니다. 엔진 버전은 각 설정 파일을 확인하며 캐시는 새 컴퓨터에서 생성합니다.

추가 조건과 이력 정리 한계는 [미디어 보관/재제작](MEDIA_STORAGE.md), 제작 검수는 [워크플로](VIDEO_WORKFLOW.md)를 따릅니다. Git에 없는 원본은 JSON만으로 되살릴 수 없으므로 개인 백업이 중요합니다.
