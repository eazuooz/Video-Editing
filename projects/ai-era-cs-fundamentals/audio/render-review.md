# 음성 확인용 MP4 렌더

아래 수치와 파일은 **v5 보존 기록**입니다. 현재 v6는 17:36.567, 63394프레임, 연속 우리 대사 + 작은 원음 + Blue Dream 검토 믹스입니다. [v6 재현 절차](v6-production.md), [프로젝트 최신 경로](../README.md)를 우선합니다. 현재 편집기 WAV 연결·한영 253개 자막은 반영됐으며 BGM 게시 조건과 전체 청취 승인은 별도입니다.

## 상태

35초 시험 렌더 완료. 1920×1080, 60fps, 2,100프레임.
영상과 음성을 전체 디코딩했으며 오류가 없었습니다. 원음/설명 화면을 각각 추출해 확인했습니다.
21~33초 내레이션 표본은 평균 -19.4dBFS, 최대 -2.5dBFS로 무음이 아닙니다.
**2026-09-12 전체 15:06.733 검토본 완료**. 54,404프레임, 1080p60.
12개 챕터의 예시/설명 24구간을 추출해 화면과 음량을 확인했습니다.
표준 MP4의 AAC 패킷 SHA-256이 원본 전체 믹스와 같고, 한영 SRT 복사본의 SHA-256도 원본과 같습니다.
VS Code용 H.264/MP3 호환본도 전체 디코딩 검사를 통과했습니다.

- [전체 표준 MP4](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260911T161653Z.mp4)
- [전체 VS Code 호환 MP4](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260911T161653Z-vscode.mp4)
- [전체 렌더·음성·자막 검사 보고서](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260911T161653Z-qa.json)

- [35초 표준 MP4](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-35s-20260911T161336Z.mp4): H.264 + AAC.
- [35초 VS Code 호환 MP4](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-35s-vscode.mp4): 동일 영상 + MP3 오디오.
- [시험 렌더 보고서](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-35s-20260911T161336Z.json).

이 파일들은 **TTS + 예시 영상 원음 검토본**입니다. Blue Dream은 파일·라이선스 확인 전이므로
들어 있지 않습니다. BGM이 완성된 게시본이나 사람의 전체 청취 승인을 의미하지 않습니다.

## 재현

Vite 서버가 9100에서 실행 중일 때, `motion-canvas` 폴더에서:

```powershell
node scripts/render-review.cjs ai-era-cs-fundamentals 35
node scripts/resume-ai-cs-render.cjs new
```

전체 출력의 재검수·SRT 복사·호환본 생성:

```powershell
node scripts/verify-ai-cs-render.cjs shared/output/motion-canvas/<새 전체 출력 파일>.mp4
```

검수 도구는 기존 결과를 덮지 않으므로 새 출력에 한 번 실행합니다.

`render-worker.html`에서 Motion Canvas의 Renderer API를 실행합니다. 기존 프로젝트의
씬 순서·1920×1080·60fps 설정을 유지합니다. 렌더 범위 끝은 포함되는 프레임이므로
`(총 프레임 수 - 1) / FPS`로 지정해 한 프레임이 추가되지 않게 합니다.

- 비디오 리소스를 `yield clip()`으로 준비한 후 재생합니다. 프레임/씬 시간을 늘리지 않습니다.
- Renderer의 종료 이벤트와 오류를 검사합니다. 파일 크기가 잠시 같다는 이유로 완료라 판단하지 않습니다.
- 출력 이름에 시각을 넣어 기존 파일을 덮어쓰거나 삭제하지 않습니다.
- 영상 렌더 뒤 원본 전체 믹스를 AAC 패킷 복사로 합칩니다. 브라우저 오디오 지원 여부에 의존하지 않습니다.
- 출력 프레임 수·해상도·음성 스트림·전체 길이·전체 디코딩을 검사합니다.
- 입력 믹스와 한국어/영어 SRT의 SHA-256이 작업 전후 같은지 검사합니다.
- `*-visual.mp4`는 무음 중간 파일이며 시청용이 아닙니다. **`-visual`이 없는 MP4**를 엽니다.

전체 렌더는 한 브라우저에서 54,404프레임을 계속 처리하는 대신, 새 작업용 브라우저로
각 60초를 처리하고 프레임 수를 검증한 뒤 연결합니다. 장시간 작업 중 브라우저 무응답이
발생했던 구간까지 정상 종료한 21,483프레임(358.05초)은 보존하고 다음 프레임부터 재개했습니다.
씬의 시간은 절대 타임라인을 사용하므로 구간마다 애니메이션을 처음부터 시작하지 않습니다.
체크포인트는 `shared/output/ai-cs-media-cache/<작업명>-resume/`에 보관합니다.
파일명에 `-part-` 또는 `-visual`이 들어간 파일은 시청용 전체본이 아닙니다.

## VS Code에서만 소리가 안 나는 경우

VS Code Webview는 AAC를 지원하지 않습니다. 영상이 보여도 AAC 소리는 들리지 않을 수 있습니다.
[공식 지원 형식 안내](https://code.visualstudio.com/api/extension-guides/webview#supported-media-formats).

표준 H.264/AAC MP4는 외부 Chrome 또는 Windows 미디어 플레이어에서 확인합니다.
위 35초 호환본은 영상 스트림을 복사하고 음성만 MP3로 바꾼 별도 검토 파일입니다.
렌더 성공이 기존 Motion Canvas 편집기의 M4A 재생 문제까지 해결한 것은 아닙니다.
편집기 연결/파형과 연속 BGM은 별도 남은 작업입니다.
