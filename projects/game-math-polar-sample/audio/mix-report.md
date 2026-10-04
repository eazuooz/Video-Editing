# 극좌표계 샘플 — 실제 오디오 믹스

2026-10-04 로컬 검토본. 기존 승인 Qwen3-TTS1.7B 기준 목소리와 Nimbus/Eveningland를 재사용했다. 사람의 전체 청취는 pending이다.

7개 장면 WAV를 측정한 편집 슬롯에 배치하고 총180초로 합쳤다. 음성 속도 변경 없이 발화 사이의 여백과 장면 길이를 함께 조정했으며 KO/EN43개 큐도 같은 발화에 정렬했다. 원본 게임 오디오/OST는 로컬에 남겨 두고 최종 믹스에서는 제외했다. 미확인 게임 음악이 승인곡과 겹치지 않도록 하는 샘플 예외다.

Nimbus는 처음부터 끝까지 연속 재생한다. 원본280.66초 중180초를 사용하므로 반복은 없다. 음악 목표 -28 LUFS, sidechain threshold0.08/ratio2.2/attack15ms/release280ms; 음성 정규화 후 음악을 낮추어 합치고 최종 마스터를 다시 측정했다. amix normalize=0, 합산 limiter0.82, 마스터 loudnorm -16 LUFS/-1.6 dBTP를 적용했다.

**AAC 전체 믹스 실제 결과: -16.04 LUFS, -1.55 dBTP, LRA9.80 LU.** 설정 목표와 실제 측정값을 구분하여 `mix-measurements.json`에 보존한다. 승인곡 복구본의 Audio Library 원본 취득 확인은 기존대로 pending이다.

재생성: `qwen3-tts/.venv/Scripts/python.exe projects/game-math-polar-sample/production/build.py assemble`. 현재 계획의 모든 컷이 이미 생성된 경우 `mix`로 음성 합성만 재개할 수 있다. `burn`은 영상만 다시 인코딩하고 AAC는 복사하므로 clean/captioned의 오디오는 동일해야 한다. 최종 전체 디코딩과 오디오 패킷MD5는 `production/qa.json`을 따른다.

전체 믹스 WAV/M4A는 `motion-canvas/src/projects/game-math-polar-sample/assets/`에 연결되며 각 Video는 mute로 중복 재생을 막는다. MP4는 `project.json.paths.videoClean` 및 `videoBurnedCaptions`; 최종 수집본은 `output/game-math-polar-sample/`. 편집기에서 사람이 실제 청취했다는 것으로 기록하지 않는다.
