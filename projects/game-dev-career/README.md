# 게임 개발로 먹고살기

프로젝트: `game-dev-career` · 2026-09-20 승인 대본으로 본편 제작.
게임 기획자·프로그래머·2D·3D 아티스트가 맡는 역할과 협업을 넓게 소개한다.

## 최신 본편

- [자막판 미리보기](http://localhost:9191/career-final.html)
- [무자막 미리보기](http://localhost:9191/career-final.html?clean)
- [Motion Canvas 편집기](http://localhost:9191/src/projects/game-dev-career/project)
- [상자 직접 테스트](http://localhost:9191/career-prototype.html)
- 자막 MP4: `shared/output/motion-canvas/game-dev-career-v3-subtitled.mp4`
- 무자막 MP4: `shared/output/motion-canvas/game-dev-career-v3.mp4`
- KO/EN SRT: `shared/output/narration/game-dev-career/qwen3-1.7b-role-overview-v2/`

**실측 6분 49.95초 / 1920×1080 / 60fps / 9개 독립 씬 / 94개 한영 대응 자막.**
렌더·검수 상태와 사람이 아직 승인하지 않은 항목은 [제작 체크리스트](checklist.md)에서 확인한다.

자막 중심은 사용자 요청에 따라 기존보다 **30px 위인 y=400**으로 이동했다.
두 줄 기준 테두리·그림자 아래 최소 51.5px 여백. 흰 박스·검정 글자·초록 그림자 유지.
자막은 편집 가능한 텍스트이며 무자막 마스터와 별도 SRT도 보관한다.

## 실행

```powershell
cd D:/Github/VideoEditing/motion-canvas
npm start -- --host 127.0.0.1 --port 9191
```

정적 빌드: `npm run build`. MP4 렌더는 정적 빌드와 별개이며
[제작·재현 명령](production/README.md)을 따른다.

## 내용과 소스

- [승인 대본](script/review.ko.md) · [직무/기본기 조사](planning/fundamentals-proposal.ko.md)
- [실제 사용 미디어·인/아웃점](production/media-sources-v3.json) · [출처](sources/SOURCES.md)
- [오디오 설정·측정](audio/mix-report.md) · [검수 기록](production/review-notes.md)
- [한국어 게시문](publishing/description.ko.txt) · [영어 게시문](publishing/description.en.txt)

v3는 저장소에서 이미 사용한 YouTube URL을 제외하고 9개 씬의 자료화면을 모두 새로 선정했다.
완성 게임 플레이, 한 프로젝트의 손그림·3D·코드·결과, 게임 기획 문서, C++ 프레임워크,
Krita, Blender, 픽셀 애니메이션, 3D 캐릭터, 엔진 반복 작업을 역할 설명에 맞춰 사용한다.
세부 코딩 강의가 아니라 각 역할의 책임·전문 분야·협업·작은 입문 과제를 설명한다.
모든 예시는 19.5초이며 그 위에서도 한국어 대사가 이어지고 Discovery와 작은 원음이 함께 재생된다.
자료화면 속 타인의 프로젝트를 채널의 자체 제작물로 주장하지 않는다. 기존 v1·v2 본편과 오디오는 보존한다.

## 이전 프리뷰 보관

- [90초 자막 프리뷰](preview/v2/captioned/game-dev-career-preview-v2-captioned.mp4)
- [90초 무자막 프리뷰](preview/v2/game-dev-career-preview-v2.mp4)
- [15초 승인 자막 샘플](preview/v2/captions/game-dev-career-caption-sample-v2.mp4)
- [54초 무음 시각 콘티](http://localhost:9191/career-storyboard.html?reel)

예전 495초 편집 예산과 프리뷰 자막을 본편 타이밍으로 사용하지 않는다.
이전 프리뷰는 삭제하거나 재렌더하지 않았다. 최종 청취 승인 전 `publishReady=false` 유지.
