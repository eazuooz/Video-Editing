# 현재 검수본의 오디오

최종 길이: 1471.933초. 인코딩 믹스: -16.31 LUFS / -1.77 dBTP.

원본 Qwen PCM을 보존하고 문단별 발화 게인과 짧은 피크 보호를 적용해 테이크 내부의 점진적 음량 감소를 보정했습니다. 음악만 음성에 따라 낮추고 목소리는 덕킹하지 않았습니다. Wholesome의 시작 레벨은−31 LUFS, 발화 중 추가감쇠는6dB입니다.

전체 발화의400ms창/100ms간격 비교: 믹스 감쇠검사 pass, 원본 국소레벨 의심 55곳. 실제 사람 청취는 pending입니다.

증거는 아래 기존 작업 폴더에 있습니다.

- `shared/output/ai-game-development-human-craft/revision-v2/audio/mix-report.json`
- `shared/output/ai-game-development-human-craft/revision-v2/audio/level-continuity.json`
- `shared/output/ai-game-development-human-craft/revision-v2/audio/final-asr/complete-readback.json`

원본 개발·게임 소스의 별도 음악/해설은 제외했습니다. 상점 보상음은 동작 시각에 맞춘 자체 제작 효과음이며 원본 게임 음향 보존으로 표시하지 않습니다.
