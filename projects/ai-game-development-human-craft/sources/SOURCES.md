# AI 게임 개발 영상 — 제작 자료

기준일2026-10-14. 사용자 제공 원문의 주장·예시 역할과 승인 대본의28개 장면 순서를 유지한다. 선택 파일·해시·구간·권리 근거는 `source-manifest.json`, 검수 상태는 기존 `production/review-ledger.json`에 기록한다.

## 공지·보도·개인 의견

- [Wild Ox Studios 참고 영상](https://www.youtube.com/watch?v=Zxbn55DVi-Q): 사용자 제공 자막의 구성과 주장 참고용. `research-reference-only`. 원영상의 음성·게임 컷을 편집에 넣지 않는다. 공장11년 경력·음악/프로그래밍 경험·미래 전망은 그 제작자에게 귀속한다.
- [Epic: The Road to UE6](https://www.unrealengine.com/news/the-road-to-ue-6):2026-06-22 공식 발표. Verse/Scene Graph/MCP와 단계적 전환 계획. 초기 Blueprint/Actor 유지를 즉시 폐지와 혼동하지 않는다. 실제 브라우저의 제목·날짜 영역을 짧게 보여 준 뒤 자체 도식으로 설명한다.
- [Unity: Why we built Unity Spark](https://unity.com/blog/why-we-built-unity-spark), [Spark](https://unity.com/spark):2026-10-14 영어 페이지의 COMING SOON / Join the waitlist를 확인하고 소개 화면을 확보했다. 브라우저 제작의 방향과 완제품 보장을 구분한다.
- [Bloomberg 보도](https://www.bloomberg.com/news/articles/2026-10-12/epic-games-delays-disney-project-asks-developers-to-use-more-ai): Disney 협업 일정과 AI 활용 확대를 보도로 귀속한다. 유료 본문 전체 확인으로 표시하지 않는다.
- [Reddit 토론](https://www.reddit.com/r/gamedev/comments/1x4fg83/epic_games_delays_disney_game_and_tells/): 이번 브라우저 접근은 네트워크 보안으로 차단됐다. 우회하지 않았으며 댓글 화면/인용은 편집에서 제외한다.
- Thomas Brush: [공식 사이트](https://www.thomasbrush.com/), [Atmos Games](https://atmosgames.com/presskit). 게임명과 제공 자막에 나온 감정의 취지를 구분한다. 확인하지 않은 직접 인용/게임 플레이를 만들지 않는다. Halo/Elder Scrolls도 원영상의 사례명과 창작자의 선택을 도식으로 설명하며 게임 음악은 사용하지 않는다.

## Unity 자산과 저장 씬

- KayKit Adventurers Knight: 승인된 CC0 모델/애니메이션 재사용. `unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers/provenance.json`.
- [Kenney Tiny Dungeon1.0](https://kenney.nl/assets/tiny-dungeon): CC0 도트 시트. 원본 라이선스·해시·Point 필터/원본 픽셀 크기를 보존. `unity/VideoEditing/Assets/ThirdParty/KenneyTinyDungeon/provenance.json`.
- `Assets/VideoScenes/ai-game-development-human-craft/`에12개 독립 씬 저장:02/06/08/09/14/17/18/20/23/25/26/28. Unity6000.6.0f1,URP17.6.0,1920×1080,60fps. 설정·동작은 기존 `planning/scene-design.json`와 `production/ai-game-development-human-craft/capture-plan.json`에 연결한다.
- 자체 씬은 `self-authored-engine-explanation`. 구매는 실제 메모리 내 C# 조건을 실행하고, UV는 실제 메시 좌표를 사용한다. 문/공구/점프 교육용 재현을 상용 게임 측정치·네트워크/영속 저장 검증으로 표시하지 않는다.

## 잉크 개발 화면

[Mix and Jam / Splatoon-Ink](https://github.com/mixandjam/Splatoon-Ink), 리비전`10a730cc26d48d9a3f8a34983827291f4ecef5b2`의001(11.667초),002(9.3초)를 선택했다.003/004는 사용하지 않는다. 깨끗한 바닥/벽→캐릭터 이동과 발사→초록 잉크가 남는 결과를 관찰했다. 전체 시간 범위의2fps 필름스트립을 확인했으며 최종 편집의 움직임 검수는 별도 기록한다.

저장소의 이용/복제/수정/게시 허용 및 고지 보존 문구는 `licenses/Splatoon-Ink.txt`에 원문 보존했다. SPDX 이름 대신 실제 문구를 따른다. 캐릭터는 [Jammo Character](https://github.com/mixandjam/Jammo-Character)의 별도 MIT 라이선스를 `licenses/Jammo-Character.txt`에 보존했다. [Adobe Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html)의 렌더된 상업적 사용 허용도 확인했다. 원본 오디오는 사용하지 않는다.

분류는 `independent-development-demo`. Nintendo Splatoon 본편, AI가 만든 게임, 개발 시간이나 완제품 성능의 증거로 표시하지 않는다.

## 월드 오브 워크래프트 화면

[Nyhver의 Classic Paladin 소개](https://www.warcraftmovies.com/movieview.php?id=252801), [독립 녹화 원본](https://www.youtube.com/watch?v=A2VQbPrw9-g). 제작자는 자신의 녹화 사용을 허용한다고 명시했다.2020-03-13 자료이며 일부 외형 변경을 사용했다고 밝힌다. 최신 기본 캐릭터 외형·셰이더 측정 결과로 설명하지 않는다. [Blizzard Video Policy](https://www.blizzard.com/en-gb/legal/2068564f-f427-4c1c-8664-c107c90b34d5/blizzard-video-policy)의 게임 녹화 범위와 홍보 영상 제외를 구분한다.

원본120–240초 구간을 확보한 로컬 파일에서36–91초(55초)를 정규화했다. 키프레임 다운로드의 프리롤 때문에 로컬 시각을 원본 YouTube의 정확한 시각으로 단정하지 않는다. 최종 파일 해시/in/out은 manifest에 기록한다. 제3자 음악 때문에 원음을 전부 제외했다. 최신 Midnight 자료도 검토했지만 권리가 확인된 독립 녹화를 확보하지 못했고 공식 트레일러를 대체 사용하지 않는다. 사례의 목적은 오랫동안 유지된 미술 방향이므로 Classic을 버전 표시와 함께 사용한다.

## 음악과 보존

기존 사용자 승인 차분한 곡 **Wholesome / Kevin MacLeod**를 재사용한다. CC BY4.0 근거·해시는 `shared/assets/music/incompetech/Wholesome.LICENSE.md`. 현재 믹스에서는−31LUFS를 시작값으로 내레이션 중심 덕킹과 비교 검수를 한다. 스타일 승인과 현재 믹스 검수는 별개다. 필수 고지는 `CREDITS.md`와 게시 설명에 보존한다.

원본 녹화·음성·웹 캡처·QA 이미지는 `shared/sources/ai-game-development-human-craft/`, `shared/output/ai-game-development-human-craft/`에 로컬 보관하며 Git에는 넣지 않는다. 확보·부분 검수·완성본 검수를 구분한다.

<!-- selected-actual-footage-v2 -->

최신 실제 화면60:설명40 구성은 [컷 계획](../planning/actual-footage-plan.json)과 [자료 매니페스트](source-manifest.json)의 `actualFootageSources`를 따른다. 각 원본의 제작자·연도·실제 동작·권리·해시·네이티브 인아웃을 기록했다. 자체 Unity 시연은 설명이며 공지 캡처도 실제 녹화 비중에 포함하지 않는다. David Revoy의 작업을 Thomas Brush의 작품으로,2023년 별도 Unity 플러그인을 Spark로 소개하지 않는다.
