# YouTube 업로드용 묶음 — 2026-09-15

대본v4 / 에디토리얼 화면v5, **8분1.8초 본편**에 맞춘 파일이다.
실제 YouTube 업로드·게시나 Git 커밋은 실행하지 않았다.

## 썸네일

[한국어 썸네일 PNG](thumbnails/let-them-play-ko-v1.png) — 사용자 첨부 썸네일의 노란 헤더·흰 배경·굵은 검정 글자·픽셀 닭 스타일.
문구: “게임의 첫 장면 / 어떻게 만들까?”. [디자인·생성 프롬프트 기록](thumbnail-design.md).

## 추천 제목

한국어: **게임은 어떻게 시작해야 할까? | 첫 장면과 튜토리얼 디자인**

영어: **How Should a Game Begin? | Opening and Tutorial Design**

사용자 정정 반영: **영상의 목적은 게임 디자인 교육이며, 야숨은 설명을 위한 사례다.**
제목은 첫 장면·튜토리얼의 설계 질문을 중심으로 쓰고, 게임 이름은 설명란의 사례 소개에 둔다.
특정 게임 리뷰나 야숨의 성공 비결을 분석하는 영상처럼 포장하지 않는다. 검색 순위나 조회수를 보장하지 않는다.
다른 후보는 [한국어 게시 문구](youtube.ko.md)와 [영어 게시 문구](youtube.en.md)에 각각2개를 더 적었다.
대본 내부 제목과 영상 내용은 바꾸지 않았다.

## 붙여 넣을 파일

| 언어 | 제목 | 설명란 전체 | 자막 |
|---|---|---|---|
| 한국어 | [title.ko.txt](title.ko.txt) | [description.ko.txt](description.ko.txt) | [let-them-play.ko.srt](subtitles/let-them-play.ko.srt) |
| 영어 | [title.en.txt](title.en.txt) | [description.en.txt](description.en.txt) | [let-them-play.en.srt](subtitles/let-them-play.en.srt) |

설명 TXT에는 소개·질문·8개 챕터·게임 영상 출처·Discovery 크레딧·논지 참고·해시태그가 포함된다.
출처를 영상에서 빼고 설명란에 두기로 했으므로, 짧은 소개 문단만이 아니라 **전체 설명 TXT**를 사용한다.
영문 설명은 영어 음성이 아닌 **한국어 내레이션 + 영어 자막**임을 정확히 표시한다.
원본 영상: `shared/output/motion-canvas/let-them-play.mp4`.

## SRT 검토

- 한국어120개, 영어120개. 번호와 시작·종료 타임코드가 모두 동일하다.
- 한국어는 승인 내레이션 대본과 일치하며 기존 SRT를 그대로 복사했다.
- 영어는 한국어의 각 구간에 대응하도록 다시 다듬었다. 기존 문단 단위 균등 분할의 문장 선행·지연과 짧은 구간의 과도한 길이를 줄였다.
- 영어 최대2줄·줄당46자, 가장 빠른 구간22.37자/초. 글자 수에 공백을 포함한다.
- 마지막 자막08:01.030, 영상 끝08:01.800. 중복·역전·영상 길이 초과 없음.
- MP4·믹스AAC/PCM·기존 한국어/영어SRT·타임라인의 해시는 변경되지 않았다.
- 자막 텍스트·파일 검증은 전체 음성의 사람 청취 승인을 대신하지 않는다.

최신 업로드 자막은 이 폴더의 `subtitles/`를 사용한다. TTS 출력 폴더의 기존 영어 SRT는 이전 자동 분할 번역 이력이다.

## 수정과 다시 만들기

제목·설명 기준: `youtube.ko.md`, `youtube.en.md`.
영어 자막 기준: `../script/captions.upload.en.json` (한국어 구간별 번역).
한국어 타임코드 기준: 프로젝트 매니페스트 `paths.captionsKo`.
TXT/SRT 출력만 직접 고치면 재생성할 때 사라지므로 위 기준 파일에서 수정한다.

저장소 루트에서:

```powershell
node scripts/prepare-let-them-play-publishing.cjs
```

한국어 원본 해시·전체 대사·자막 시간·영어 길이·최종 MP4 프레임·챕터 시작·음악 크레딧을 검사한다.
한국어 자막이 바뀌면 영어 구간을 다시 검토하기 전에는 생성을 중단한다.
검증 보고서: [upload-validation.json](upload-validation.json).
