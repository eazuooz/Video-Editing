# 본편 검토 기록 — 대본 v4 / 화면 v5 — 2026-09-14

## 최신: 승인된 에디토리얼 2.5D 본편

8개 챕터의 설명·비교 화면을 교체하고 전체 본편을 렌더했다. [디자인·재현 기록](editorial-v5.md).
결과는 `shared/output/motion-canvas/let-them-play.mp4`.
1920×1080 / 60fps / 28908프레임, 영상·AAC·컨테이너 모두481.8초, 196326090바이트.

- 라이브24구간 및 그래픽48개 시간대 표본을 검사했다.
- 실제 MP4의24개 구간 표본·8개 비교 후반·마지막 프레임을 추출해 에이전트가 직접 확인했다.
- 07/08의 안내와 캐릭터 얼굴 겹침, 01/08의 높은 지형과 탑 바닥 배치를 보정했다.
- 02/05 A 화면의 잘림은 구도 비교를 위한 의도적 반례다. 다른 라벨·제목의 의도치 않은 겹침은 표본에서 발견되지 않았다.
- 이전 본편은 `shared/output/let-them-play/editorial-full-v5/before-editorial.mp4`에 보존했다.
- 새 디자인 렌더 전후 승인 믹스AAC/PCM·한국어/영어SRT·타임라인·대사·원본8개 게임클립 해시가 동일하다.
- 최종 AAC 패킷은 마스터와 일치한다. 기존 음성1.1배, 연속 Discovery, 작은 게임 원음과 -15.83LUFS / -2.06dBTP 유지.
- 한영120개 자막 타임코드 일치, 마지막 종료08:01.030. 전체 디코드·빌드·1:1:1 구성·게시 기술 검사 통과.
- 편집기 파형 피크0.7870, PCM481.8초, 음소거 해제 상태로 재생시간이2초 이상 증가했다.

최신 근거는 `final-visual-qa/render-report.json`, `final-assembled-qa/report.json`과
그 폴더의 `contact.png`, `late-contact.png`, `ending.jpg`다. 경로 기준은 `shared/output/let-them-play/`.
전체 청취 승인은 아직 대기다. 아래는 v4 제작과 음량 조정 이력이며, 최신 그림은 이 v5 검수를 따른다.

## 이력: v4 음량 수정

내레이션만 ×1.1 적용. 최신 AAC는 -15.83LUFS / -2.06dBTP.
영상 패킷·한영 SRT 해시 동일, 기존 배경 스템 동일, 전체 디코드·AAC 패킷 일치 통과.
최신 음량의 근거는 `shared/output/let-them-play/voice-gain-1p1/report.json`이다.
이전 마스터와 MP4는 같은 폴더 `before-voice-gain.*`에 보존했다.
아래 검토 수치 중 음량·파형은 변경 전 이력이다. 음량 수정 당시에는 그림 패킷을 유지했다.
당시 [독립 샘플](editorial-sample.md)로 제안한 새 디자인은 이후 승인을 받아 위 v5 본편에 적용했다.

## 이력: 기본 v4 본편 검토

결과: `shared/output/motion-canvas/let-them-play.mp4`.
1920×1080,60fps,28908프레임, 화면481.8초. 컨테이너481.82초는 AAC 패딩을 포함한다.
내레이션·작은 야숨 원음·연속 Discovery 포함. 한국어/영어 SRT는 각120개, 번호·타임코드 동일.

## 확인한 항목

- 원본 야숨 클립8개: 실제 동작 표본과 사용 조건 확인, 원음 보존, 프레임 수·전체 디코드 통과.
- Motion Canvas8씬·24구간: 실측 동일 비율, 게임/설명/비교 각각160.6초, 끝 크레딧0프레임.
- 라이브 캔버스24개 표본 확인: 글자 겹침이나 화면 밖 잘림 없음.
- 최종 MP4 자체24개 표본도 별도로 추출·확인: 실제 게임 → 디자인 해설 →2.5D 비교 순서, 출처/상태 꼬리말 없음.
- 481.7초 끝 화면 확인: 마지막 디자인 제목·요약으로 마무리하며 별도 크레딧 없음.
- 한영 YouTube 설명란에 Archive64, Nintendo 관련 고지, Discovery의 정확한 크레딧·링크·CC BY4.0·편집 내역과 챕터를 기록.
- 편집기 PCM 전체 믹스481.8초, 파형 피크0.7801, 음소거 해제, 재생 시간이2초 이상 증가함을 확인.
- 최종 AAC -16.36LUFS / -2.15dBTP. 각8씬의 게임·설명 구간에서 레이어 표본 확인.
- MP4 전체 디코드 통과, AAC 마스터와 최종 MP4 오디오 패킷 해시 일치.
- 마지막 SRT 종료08:01.030, 화면 종료08:01.800 이내. 한영120개 모두 동일 시간.
- `check-video-project.ps1 -Project let-them-play -Stage publish` 통과.

## 출력 방식

전체 화면을 브라우저에서 다시 그리는 방식은 게임 구간에서 느려 중단했다.
게임 클립은 원본 H.264 프레임을 보존하고, Motion Canvas에서 각 씬의 뒤 두 구간만 렌더해 연결했다.
이는 화면 비율·원래 게임 속도·음성·자막 시간 변경이 아니다. 총프레임을 재확인했다.
새 재렌더 기본 명령은 `render-let-them-play-hybrid.cjs`다. 전체 캔버스 방식은 대안으로 보존한다.
비디오 비동기 리소스를 먼저 yield하는 수정도 적용해 초기 메타데이터 로딩 오류를 해결했다.

## 근거 파일

- `shared/output/let-them-play/final-visual-qa/report.json`: 캔버스 타이밍·파형·편집기 재생
- 같은 폴더 `render-report.json`: 실제 연결 조각·프레임·디코드·AAC 일치
- `shared/output/let-them-play/final-assembled-qa/contact.png`: 최종 MP424개 표본
- 같은 폴더 `ending.jpg`, `report.json`: 끝 화면·스트림·동일 한영 자막 시간
- `shared/output/let-them-play/final-audio-v4/mix-report.json`: 레이어별/합산 음량

## 사람의 확인이 필요한 항목

자동 받아쓰기·파형·디코드 검사는 실제 사람의 전체 청취 승인을 대신하지 않는다.
특히07번 `컷신` 발음, 08번 종결음은 청취 확인이 필요하다.
08번은 끝 문장 전체가 인식됐으나 감쇠44ms가 자동 기준70ms에 못 미친다.
따라서 본편은 **review-ready**이며 `publishReady:false`, `complete`가 아니다.
게시·Git 커밋·푸시는 이번 작업에서 실행하지 않았다.
