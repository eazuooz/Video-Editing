# 본편 오디오 믹스 — 2026-09-20

## 현재 v3 — 역할군 소개·전면 신규 자료화면

`production/build_episode_audio.py align`과 `mix --revision v3`로 새 대본의 장면 단위
TTS, Whisper 정렬, KO/EN SRT, 연속 믹스를 함께 생성했다. 409.95초 / 24,597프레임 / 한영
94큐이며, 편집기 `final-mix-v3.wav`, MP4용 `final-mix-v3.m4a`를 사용한다.

- 내레이션 장면별 ASR 일치율 98.7–100%. 차이는 2·3·4 숫자 표기, C++, 도형화·모델러의 근접 인식이며 문장 누락이나 반복은 없다.
- 내레이션 -16 LUFS / Discovery -28 LUFS / 자료화면 원음 01 -27 LUFS, 02–09 -31 LUFS 목표.
- Discovery는 처음부터 끝까지 연속 재생하고 자료화면 구간에서만 추가 -3dB, 내레이션에는 사이드체인 덕킹을 적용했다.
- 실제 AAC 입력 측정: **-17.99 LUFS / -3.94 dBTP / LRA 3.90 LU**.
- 9개 씬의 예시·설명 구간에 배경 레이어가 있고, 409.95초 영상 길이와 오디오 길이, KO/EN 94큐 타이밍이 일치한다.
- 기계 기록: `production/mix-report-v3.json`, `production/audio-layer-check-v3.json`.
- 사람의 전체 청취 승인은 대기 상태다.

---

## v2 보존 기록 — 실제 외부 영상 9개 슬롯

`production/build_episode_audio.py mix --revision v2`로 별도 생성했다.
TTS 원본·SRT·434.25초 타이밍은 변경하지 않았다. 편집기 `final-mix-v2.wav`,
MP4용 `final-mix-v2.m4a`를 사용하며 v1 마스터는 보존한다.

- 원본: `production/media-sources-v2.json`. 01 실제 게임 원음 -23 LUFS,
  02–09 외국어 해설이 포함된 자료는 -31 LUFS 목표. 더 작게 두어 한국어 대사와 경쟁하지 않도록 했다.
- 내레이션 -16 LUFS / Discovery 연속 -28 LUFS / 겹침 감쇠 -3dB / 덕킹·1초 곡 루프 크로스페이드 유지.
- 실제 인코딩 AAC 측정: **-17.85 LUFS / -3.70 dBTP / LRA 3.70 LU** (`input_*` 측정값).
- 9개 씬 예시·설명 구간 배경 레이어 존재와 동일한 KO/EN 102큐 검사 통과.
- `production/mix-report-v2.json`, `production/audio-layer-check-v2.json`에 기계 검수 기록.
- 사람의 전체 청취 승인은 별도 대기.

## v1 보존 기록

길이 434.250초. 원본 승인 목소리 Qwen3-TTS 1.7B Base, 장면 단위 합성.
9개 장면 모두 말미 감쇠 검사 통과. ASR 일치율 98.6–100%이며, 숫자·C++·UV의 표기 차이와
일부 어미 인식 차이는 `production/asr-review.json`에 보존한다. 사람의 최종 청취 승인은 아직 하지 않았다.

| 레이어 | 설정 |
| --- | --- |
| 내레이션 | -16 LUFS 정규화 목표 |
| 자체 프로토타입 효과음 | -23 LUFS 정규화 목표 |
| 외부 Krita·Blender 해설 | -31 LUFS 정규화 목표, 한국어 대사와 경쟁하지 않게 감쇠 |
| Discovery | -28 LUFS 목표, 전체 연속 재생 |
| 원음 겹침 | BGM 추가 -3dB, 0.45초 완만한 전환 |
| 덕킹 | threshold .08 / ratio 2.2 / attack 15ms / release 280ms |
| 곡 반복 | 1초 크로스페이드 |
| 바깥 페이드 | 시작·끝 각각 0.45초 |
| 합산 | amix normalize=0, limiter 0.80 |
| 출력 | AAC 192kbps, 48kHz stereo; 편집기는 같은 믹스 PCM WAV |

최종 AAC **측정값**: -17.87 LUFS integrated, **-3.03 dBTP**, LRA 3.60 LU.
이는 `loudnorm` 검사 결과의 `input_*` 값이며, 검사기의 가상 재정규화 `output_*`가 아니다.

원음 구간에서도 Discovery는 끊기지 않는다. 06은 대사 대상에 맞춰 13.2초에 자료화면과 원음이 끝나며,
나머지는 19.5초. 9개 씬의 예시/설명 배경 레이어 존재와 KO/EN 동일 타임코드를
`production/audio-layer-check.json`에서 확인했다. 원음 없는 상용 소스를 임의로 소리가 있는 것처럼 꾸미지 않았다.
프로토타입 효과음은 자체 게임의 입력 시점에 맞춰 직접 합성한 소리다.

재현: `production/build_episode_audio.py mix`. 원본 TTS를 입력으로 사용하며 이미 믹스된 MP4를 다시 섞지 않는다.
원본 클립 음성은 보존하고 Motion Canvas `MutedVideo`에서만 음소거해 중복 재생을 막는다.
최종 MP4의 AAC packet hash를 마스터 M4A와 비교한다.

음악: 'Discovery' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au
https://www.scottbuckley.com.au/library/discovery/
