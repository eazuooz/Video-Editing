# Large media archives

큰 WAV와 MP4는 **원본 바이트를 그대로 복원하는 gzip 분할 압축**으로 보관합니다. 파일 확장자만 바꾸거나 화질·음질을 낮추지 않습니다. 조각 하나는 최대 80 MiB입니다.

원본 WAV/MP4는 로컬에 그대로 있고 Git에서는 제외합니다. 압축본에 원본 경로·크기·SHA-256과 각 조각의 SHA-256을 기록합니다. 모델, 기준 목소리, 비밀 키는 이 폴더에 넣지 않습니다.

## 복원 (저장소 루트, Node.js 18 이상)

전체 한 번에 복원: `node scripts/restore-media.cjs`.
프로젝트별 복원: `node scripts/restore-media.cjs --project visible-rewards`.
검사만 실행: `node scripts/restore-media.cjs --verify-only`.
새 컴퓨터 설치 순서는 [인계 문서](../../docs/CONTINUE_ON_ANOTHER_COMPUTER.md)를 참고합니다.

```powershell
node scripts/media-archive.cjs restore shared/media-archives/ai-era-cs-fundamentals/editor-mix/manifest.json
node scripts/media-archive.cjs restore shared/media-archives/ai-era-cs-fundamentals/mix-v6-artist-music-review/manifest.json
```

두 번째 명령은 해당 검토본 압축 묶음까지 전달받은 경우에만 사용합니다. 음악 포함 검토본의 보관함 사용 조건 확인은 별도이며, 압축은 이용 허가를 뜻하지 않습니다.

원래 파일이 이미 있고 SHA-256이 같으면 건너뜁니다. 내용이 다르면 덮어쓰지 않고 중단합니다. 복원할 파일을 별도로 보존한 뒤 다시 시도하세요. 개별 `part-001.gz` 등은 완전한 gzip 파일이 아니며 모든 조각을 순서대로 이어야 하므로 위 명령 사용을 권장합니다.

검사만 할 때:

```powershell
node scripts/media-archive.cjs verify shared/media-archives/ai-era-cs-fundamentals/editor-mix/manifest.json
```

## 새 파일 보관

```powershell
node scripts/media-archive.cjs pack path/to/large.wav shared/media-archives/project/version-name
```

원본과 다른 기존 묶음은 덮어쓰지 않습니다. 수정 버전은 새 폴더명을 사용합니다. 압축 후 반드시 원본 SHA-256 검증을 통과해야 합니다. 검토 전용 파일이면 마지막에 `--review-only`를 붙여 상태를 기록합니다.

현재 묶음:

| 원본 | 원본 크기 | 압축 총크기 | 조각 |
| --- | ---: | ---: | ---: |
| editor-mix.wav (이전 편집기 음성) | 174,076,570 bytes | 116,255,173 bytes | 2 |
| mix-v6-artist-music-review.wav (음악 포함 검토용) | 202,860,878 bytes | 183,142,257 bytes | 3 |
| let-them-play.mp4 (2026-09-17 보관 v1) | 196,326,090 bytes | 195,062,853 bytes | 3 |
| visible-rewards.mp4 (2026-09-17 보관 v1) | 138,772,995 bytes | 137,332,102 bytes | 2 |
| visible-rewards-final.mp4 (2026-09-17 최종 v3) | 141,252,470 bytes | 140,605,897 bytes | 2 |

조각 누락·변조·잘못된 경로·기존 파일 덮어쓰기는 검사에서 거절합니다. 회귀 검사: `node scripts/test-media-archive.cjs`.
