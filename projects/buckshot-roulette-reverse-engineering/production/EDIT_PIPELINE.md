# 벅샷 룰렛 다큐멘터리 합성기

`assemble_documentary.py`는 실제로 선택한 클립·음성·자막을 받아 한 편을 조립한다. 실제 영상 인아웃이나 발화 시간을 자동으로 추정하지 않는다. **현재 편집 입력은 `timeline.json`**이며, 실제 원작 촬영·자체 구현·음성에 맞춘 분석 그림의 인아웃과 대사 대응을 기록했다. `timeline.template.json`은 별도의 미완성 예시이므로 제작 입력으로 쓰지 않는다.

2026-10-29 **v3 완성본의 기술 검사·표본 화면·전체 ASR 검수를 마치고 로컬 검수 폴더에 전달했다.** v2에서 혼합 PCM 연결을 수정했고, v3는 리미터 상한 -2.0dB를 적용했다. 실제 최종 AAC는 −17.0LUFS/−1.8dBTP이며 H.264 영상 패킷과 원래 음성 PCM은 보존했다. 영상·음성 길이 모두343.083333초(5분43.083333초), 20,585프레임이며 2초 브랜딩과10초 회원 안내를 포함한다. [현재 로컬 검수 페이지](D:/Github/VideoEditing/output/buckshot-roulette-reverse-engineering/index.html)와 [전체 자막 MP4](D:/Github/VideoEditing/output/buckshot-roulette-reverse-engineering/buckshot-roulette-reverse-engineering.captioned.mp4)를 사용한다. 최종 검수 범위는 `final-review.json`과 `checkpoint.json`에 기록했다. 네 발음 후보의 문맥 청취와 사용자 전체 시청은 대기 상태이며 기술 검사를 사용자 승인으로 간주하지 않는다.

- 모든 상대 경로의 기준은 이 프로젝트 폴더다. 현재 전달 폴더는 `../../output/buckshot-roulette-reverse-engineering-v3`다. 다음 수정은 검증된 기존 전달 파일을 덮어쓰지 않고 새 revision 폴더를 사용한다.
- `sources`: 실제 파일·SHA256·자료 유형·동작 검토 기록. 자료 유형은 `actual-gameplay`, `actual-development`, `prototype`, `analysis-visualization`, `explanation`이다. 연구 참고 영상과 정지 이미지 길이 채우기는 입력할 수 없다. 모든 입력 영상은 실제 디코딩 크기가 최소1920×1080이어야 한다.
- `beats`: 선택한 원본 시작 초·출력 정수 프레임 수·실제로 본 동작·대사 연결·원음 사용/게인. 각 컷은 원래 속도로 이어지며 원본 끝이 부족하면 오류로 멈춘다. 반복·감속·끝 프레임 복제를 하지 않는다. 기존 화면비는 검은 여백으로 보존한다.
- `narration`: 본문 전체 WAV, SHA256, 실제 발화에 맞춘 KO/EN SRT. 원래 WAV를 수정하지 않고 내레이션을 원음 덕킹의 기준으로 사용한다. 자막 시각은 본문 시작0초 기준이며 최종 출력에서는 브랜딩2초를 더한다. 자동 문단 무음은 넣지 않는다.
- `overlays`: 컷 안의 시작/끝, 역할 색, 검증된 좌표. `rect`, `ellipse`, `line`, `arrow`, `contour`, `text`, `code`를 지원한다. 선·경로는 `revealSeconds`, 움직이는 표식은 `keyframes`, 가려진 시각은 `hiddenIntervals`를 쓴다. 모든 표식은 컷 종료 때 사라진다. 고정 자막과 `protectedRects`를 침범하면 오류를 낸다.
- 코드 표시는 직접 작성한 설명용 의사 코드만 허용한다. 키워드·함수·변수·숫자·문자열·주석 역할을 구별하며 현재 실행 줄은 별도 노란 표시선으로 드러낸다. 실제 분석 결과·원작 동작·우리 구현의 화면 분류를 혼동하지 않는다.
- 자체 구현의 촬영 화면에 이미 자료 유형이 표시된 경우 해당 컷의 `pictureLabel`을 빈 문자열로 지정해 중복 라벨을 생략한다. `source.kind`는 그대로 유지한다. 원작 영상의 하단 선택 버튼을 보존하려면 부모 작업자가 실제 출력에서 확인한 `viewportHeight=860`과 변환된 표식 좌표를 사용한다. 기본 자체 구현은1080 전체 프레임이며 촬영 UI가892–1060 자막 영역을 비운다.
- 한국어 영구자막은 흰 박스·숲색 그림자·중심960,970·48px·최대2줄을 유지한다. 폭은 실제 폰트로 측정하며 넘치면 축소 대신 절 분할을 요구한다. `captionEmphasis`는 큐 번호별 최대 한 구간과 `term/result/problem` 역할을 받는다. SRT는 평문이다.
- 브랜딩2초/회원10초는 기존 승인된 `game-reward-planning` 파일을 해시로 고정했다. 원본 내레이션과 게임 소리는 별도 믹스한 뒤 AAC를 한 번만 인코딩하고 clean/captioned 양쪽에 복사한다. 최종 디코딩 오디오 해시도 비교한다.

실행 예시:

```powershell
C:/Python/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/assemble_documentary.py projects/buckshot-roulette-reverse-engineering/production/timeline.json --preflight
C:/Python/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/assemble_documentary.py projects/buckshot-roulette-reverse-engineering/production/timeline.json --render --verify
```

같은 입력·설정·결과 해시가 있는 중간 컷은 재사용한다. 납품 MP4가 이미 있으면 덮어쓰지 않고 새 revision 출력 폴더를 요구한다. 최종1920×1080/60fps·정확한 프레임 수·전체 디코딩·양쪽 오디오 동일성·최종 음량 로그까지 생성한다. `--verify`는 기술 확인이며 실제 화면/375px/청취/ASR/권리/사용자 검수를 통과로 표시하지 않는다. 이 검사는 기존 최종 검수 기록에 별도로 남긴다.

현재 확인한 근거:

| 단계 | 실제 결과 | 기록 |
|---|---|---|
| 모델 | Blender로 독립 제작한 GLB 10개, 별도 편집 가능한 `.blend` 보존 | `../prototype/assets/provenance.json`, `local/asset-evidence/` |
| 구현 검사 | 규칙 374개·메인 씬 통합 32개·다섯 촬영 실험의 실행 검증 26개 통과 | `local/test-evidence/`, `local/documentary-capture/all-v1-events.json` |
| 짧은 GPU 시연 | 실제 FHD60 AVI, 1,990프레임·33.166667초 | `../captures/prototype-demo-fhd.avi`, `local/test-evidence/prototype-demo-fhd-capture.json` |
| 확장 GPU 시연 | 실제 FHD60 AVI, 7,271프레임·121.183333초 | `local/documentary-capture/all-v1.avi`, `all-v1-qa.json` |
| 원작 선택 컷 | 실제 1080p60 녹화의 동작·인아웃·대사 연결 확인 | `../planning/original-footage-audit.json`, `timeline.json` |
| 선택한 자체 구현 컷 | 9개 후보의 시작·중간·끝 프레임을 이벤트와 비교; 돋보기와 회복 팩 경계를 수정 | `local/documentary-capture/selected-cut-qa/selected-cut-review.json` |
| 최종 레이아웃 대표 검사 | 실제 원작 선택 화면·상대 공포탄·탄환 큐를 현재 자막과 합성하여 FHD/375px 확인 | `local/documentary-capture/representative-caption-preflight/receipt.json` |
| 원음 측정 | 원작 11개 선택 구간·짧은 시연·확장 시연 5개 실험의 EBU128 음량/피크 측정 | `local/audio-source-audit.json`, `local/documentary-capture/all-v1-audio-audit.json` |

`local/edit-pipeline-check/bookend-font-current-audit.json`에는 기존 승인 브랜딩120프레임·회원600프레임 및 폰트의 실제 해시가 있다. 캡처는 정상 영화 시간 60fps이며 반복·정지·감속으로 길이를 채우지 않았다. 모델 파일·로직 검사·실제 렌더 영상은 서로 다른 검증 근거이고, 프레임 표본 검수는 전체 영상의 연속 시청이나 최종 청취를 대신하지 않는다. 사용자 최종 시청 승인은 아직 없다.

촬영용 `../prototype/tests/capture_documentary.gd`는 기존 main/rules/stage를 수정하지 않고 호출한다. `--scenario=items|turns|damage|dealer|assets|all`을 받아 서로 다른 규칙 실험과 직접 제작한 모델 투어를 실행한다. `--demo`는 기존 짧은 시연을 중복 시작하므로 함께 사용하지 않는다. 선택적으로 `--plan`의 JSON `scenarios` 배열과 `eventLog` 경로를 읽는다. 이벤트 로그는 이 프로젝트의 `production/local` 내부 새 파일만 허용하며 출력 프레임 시각·실제 상태·함수 반환값·코드 SHA256을 저장한다. 미확인 딜러 결과는 실제 반환값으로 정하고 원작 확률 측정이라고 표시하지 않는다.

실제 GPU 촬영 `all-v1.avi`가 완료되었고, ffprobe의 디코딩 결과는 **7,271프레임·121.183333초·1920×1080/60fps·48kHz 스테레오 PCM**이다. 다섯 실험의 유효 범위는 0–121.15초이며 마지막 종료 프레임은 편집에 채우지 않는다. 26개 실행 검증, 실제 이벤트 시각, 파일 해시, 표본 프레임·모바일 확인 기록이 `local/documentary-capture/`에 있다. 실제 선택 컷과 원음 게인은 `timeline.json`에 연결했다. 필요해 다시 촬영할 때는 음성 생성과 GPU 사용을 직렬화하고, 기존 AVI·이벤트 로그를 보존하도록 **새 출력 이름**을 사용한다. 아래는 이미 실행한 명령의 기록이며 기존 결과를 덮어쓰기 위한 재실행 명령이 아니다.

```powershell
& 'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe' --path 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/prototype' --script res://tests/capture_documentary.gd --resolution 1920x1080 --fixed-fps 60 --write-movie 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/local/documentary-capture/all-v1.avi' --log-file 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/local/documentary-capture/all-v1.log' -- --scenario=all --event-log=D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/local/documentary-capture/all-v1-events.json
```
