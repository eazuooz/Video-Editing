# 원버튼 디자인 샘플

현재 결과: **v2/one-button-concept-v2.mp4**
1920×1080 / 60 FPS / 정확히 1440프레임·24초. 연타·타이밍·반응·누르기/떼기 각6초.
무음 자체 2.5D 도식 샘플이며 실제 게임 화면·TTS·BGM·회원 엔딩은 포함하지 않습니다.
출판용 완성 영상이나 본문60:40 비율의 완성본이 아닙니다.

## 확인
- ffprobe 해상도·프레임 수·무음 스트림 구성 검사, FFmpeg 전체 디코드 통과.
- v1 4장 정지 프레임 검수 후 v2에서 버튼 밑부분 모서리와 반응시간 표시 겹침 수정.
- 250ms는 시뮬레이션 예시이며 실측 반응속도나 사용자 실험 결과가 아닙니다.
- v2 정지 프레임을 다시 확인한 뒤 production/status.md에 결과를 남깁니다.
- 승인 전 TTS·자막 타임코드를 임의 생성하지 않습니다.

## 다시 렌더
저장소 루트에서 npm start -- --host 127.0.0.1 --port 9210 --strictPort
별도 터미널에서 node motion-canvas/scripts/render-one-button-concept.cjs v3
기존 파일을 덮지 않도록 새 버전 이름을 사용합니다.

## 최종 납품
대본 → 음성 샘플 → 전체 음성 검수 → 게임 자료 권리/컷 검수 → 승인 BGM 믹스
→ 원본 프로필·표시 이름·뱃지를 사용하는 10초 회원 엔딩 → KO/EN SRT와 자막판 검수.
완성 후 node scripts/collect-video-output.cjs one-button-game-design 으로
output/one-button-game-design/에 최종4종만 모읍니다. 현재 샘플은 그 폴더에 넣지 않습니다.
