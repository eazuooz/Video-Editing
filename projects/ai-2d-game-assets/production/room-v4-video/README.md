# AI 2D 게임 · 공개 v6 영상 반영

검수: http://127.0.0.1:9287/
공개 게임: https://yamyam-cartographers-room.eazuooz.chatgpt.site/
완성본: `C:\Users\1\Videos\YamyamCoding\ai-2d-room-v4-video\video\review\ai-2d-game-assets.captioned.mp4`
SHA256: `97003cf1db875a25aa862f1cf0acdf68fe21d8667b094b268af0be4b12ed848f`

1920×1080, 60fps, 75,289프레임, 20분54.817초. `delivery.json`에 자막 포함/없는 MP4와 KO/EN SRT 네 파일 경로·해시가 있습니다.

이번에는 기존 영상의 최신 게임 화면 불일치를 수정했습니다. 전경 중앙의 독립 나무 책상, 다리 앞 책상 부재와 상판 위 손·장부, 현재 촛불 위치, 화면 안 라디오, 500자 브라우저 메모를 반영했습니다. 19개 기존 시각 장면을 교체하고 메모 설명1장면을 추가했습니다. 기존51문단 최종 PCM 샘플은 삽입 앞뒤가 정확히 동일합니다. 총52장면입니다.

게임 시연은 공개 v6 소스 `0c294d8509dacfee2057f6b47b4dda414c2222b3`의 동결 사본을 실행했습니다. `source-snapshot.json`은 게임·에셋별 해시, `version-coherence.json`은 교체20장면 및 배경/책상 정합성을 기록합니다. 원화·PixelOE 초안 등 과거 입력은 실제 제작 과정으로 명시하고 보존했습니다. 완성 게임이라고 제시하는 화면은 새판입니다. 사이트 자체는 수정하지 않았습니다.

연속 게임 화면은 실제 game.js의 Canvas 실행을1920×1080/60fps로 인코딩했습니다. 라디오·메모는 root가 공개 웹사이트에서 조작해 확보한 실제 브라우저 스크린샷이며, 영상 녹화/FHD 원본이라고 주장하지 않습니다. 실제 파일 형식·치수·해시는 `browser-evidence.json`에 있습니다.

실제 실행 도구7개(2dimg2motion, sprite-gen, pixelfx, PixelOE, Agent Sprite Forge, Codixel, Pixelbolt), 이미지 생성과 ComfyUI 비교를 보존했습니다. Sprite-Sheet-Diffusion은 실제 설치검증 후 공식 필수 가중치 누락으로 추론 재현 미완료라는 기존 설명을 유지했습니다. 캐릭터LoRA 학습이나 소개만 한 대안의 실사용을 주장하지 않습니다. 최신도구/출처목록과 게임 링크는 설명 파일에 포함했고 출처가 맨 아래입니다.

검증: 최종 전체 디코드, 크기/fps/길이/프레임수, 동일AAC, 기존 PCM 보존, 추가문단 raw/최종AAC 독립ASR 대조, 변경20장면 인코딩40표본 및6개375px표본 확인. 전체 실시간 시청·음성청취나 새 버전의 사용자 승인은 미완료입니다.

기존 room-v3 검수본과 비공개 YouTube `t7Li-IzqJyk`는 보존했습니다. 새 영상 업로드·삭제·공개·예약은 하지 않았습니다. project/shared ledgers/Git 변경은 root가 `metadata-patch-spec.json`과 정확한 변경목록을 이용해 수행합니다.
