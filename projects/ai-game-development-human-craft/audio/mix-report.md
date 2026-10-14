# 현재 검수본의 오디오

최종 길이: 1478.867초. 인코딩 믹스: -16.25 LUFS / -1.78 dBTP.

원본 Qwen PCM을 보존하고 문단별 발화 게인과 짧은 피크 보호를 적용해 테이크 내부의 점진적 음량 감소를 보정했습니다. 음악만 음성에 따라 낮추고 목소리는 덕킹하지 않았습니다. Wholesome의 시작 레벨은−31 LUFS, 발화 중 추가감쇠는6dB입니다.

전체 발화의400ms창/100ms간격 비교: 믹스 감쇠검사 pass, 원본 국소레벨 의심 53곳. 실제 사람 청취는 pending입니다.

증거는 아래 기존 작업 폴더에 있습니다.

- `shared/output/ai-game-development-human-craft/audio/mix-report.json`
- `shared/output/ai-game-development-human-craft/audio/level-continuity.json`
- `shared/output/ai-game-development-human-craft/audio/final-asr/complete-readback.json`

원본 개발·게임 소스의 별도 음악/해설은 제외했습니다. 상점 보상음은 동작 시각에 맞춘 자체 제작 효과음이며 원본 게임 음향 보존으로 표시하지 않습니다.


## 2026-10-15 수정2차 진행

사용자 요청으로 출처 영상에 관한 메타 설명을 제거하고 한영41문단을 다시 연결했다. 기존 배포 음성과 v1 Drive는 보존한다. 인사는 쉼표로 연결하고 검증되지 않은 브랜드 음절 분리를 제거했다. 먼저01·03 전체 문맥을 동일 승인 Qwen1.7B/레퍼런스로 비교하며, 실제 시작/끝과 접합 파형·인식 결과를 확인한 뒤 나머지 변경 씬에 적용한다. 변경 없는04·09·17·19·28의 PCM은 그대로 재사용한다. 연구 근거는 `shared/output/ai-game-development-human-craft/revision-v2/tts-research.json`; 새 음성/믹스 청취와 완성본 검수는 아직 pending이다. 기존 v1 검수를 새 출력의 통과로 사용하지 않는다.
