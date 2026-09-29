# 제작 상태 — 2026-09-29

## 완료
- 새 프로젝트 생성, 7장 한국어 대본 및 문장 수가 맞는 영어 번역 초안.
- 본문 240초 임시 편집 JSON: 자료화면144초/자체설명96초 (목표60:40, 실측 아님).
- 대본당 독립 Motion Canvas 씬 7개. 실제 자료 미확보 슬롯은 초안 안내 화면으로 표시.
- 자체 2.5D 설명 7종 및 핵심4종 무음24초 샘플 v2.
- v2 1920×1080, 60FPS, 1440프레임 확인 및 전체 디코드 통과.
- 네 장면 정지 프레임 시각 검수. 반응시간 표시 겹침과 눌린 버튼 모서리 수정.
- 영상/음성 Git 제외 정책 검사 및 rebuild manifest 검사 통과.

## 보류 / 사용자 입력 필요
- 대본 검토 승인 → 짧은 TTS 샘플 → 음색/속도 승인 → 전체 TTS.
- Discovery / Wanderlust / BGM 없음 선택 질문 전달, 아직 답변 없음.
- 게임 영상 후보는 권리·업로더·내용·버전·실제 컷 검수 미완료, 다운로드/삽입 미실행.
- 회원 프로필·표시 이름·뱃지가 함께 있는 원본 이미지 요청 중.
  원본이 없으므로 공유 텍스트 전용 엔딩을 대신 렌더하지 않는다.
- KO/EN SRT는 발화 실측 후 생성. 현재 제공물은 자막이 아니라 대본이다.
- 최종 무자막/한국어 자막 MP4는 아직 없으며 publishReady=false.

## 검증 범위
- 새 프로젝트의 타입 오류는 해결했다.
- 저장소 전체 TypeScript 검사는 기존 다른 프로젝트의 오류로 실패:
  motion-canvas/src/projects/yamyam-dx12-rendering/scenes/paper-scene.tsx:9
  new Node()의 필수 인자 누락. 요청 범위 밖이라 변경하지 않았다.
- 기존 프로젝트와 다른 작업의 수정 파일은 건드리지 않았다. 커밋/푸시하지 않았다.
- 디자인 샘플은 최종 결과물4종이 아니므로 output의 완성본 모음에 섞지 않았다.
  최종 완료 시 node scripts/collect-video-output.cjs one-button-game-design 실행.

## 미리보기
projects/one-button-game-design/preview/v2/one-button-concept-v2.mp4
Motion Canvas 로컬 서버: http://127.0.0.1:9210/ (프로젝트 목록에서 one-button-game-design/preview 선택)
이 서버는 개발 미리보기용이며 공개 업로드가 아니다.
