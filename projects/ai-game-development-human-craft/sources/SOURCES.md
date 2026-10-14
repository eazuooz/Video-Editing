# AI 게임 개발 영상 — 제작 자료

기준일2026-10-14. 전체 대본/순서는 기존 계획을 유지한다. 확보·부분 관찰과 최종 사용 승인을 구분하며, 아직 최종 cut list는 없다.

## 발언·공지·반응 자료

| 자료 | 역할과 확인 범위 |
|---|---|
| [Wild Ox Studios 참고 영상](https://www.youtube.com/watch?v=Zxbn55DVi-Q) | 사용자 제공 대본의 구성/주장 참고. `research-reference-only`; 완성 영상/음성/게임 컷을 편집에 넣지 않음 |
| [Epic: The Road to UE6](https://www.unrealengine.com/news/the-road-to-ue-6) | 공식 발표. Verse/Scene Graph/MCP 계획과 Blueprint 전환 단계 구별. 발표 계획을 현재 완성 기능으로 말하지 않음 |
| [Unity: Why we built Unity Spark](https://unity.com/blog/why-we-built-unity-spark), [Spark](https://unity.com/spark) | 공식 설명과 접근 상태. 기준일 대기 등록 상태; 한 번의 프롬프트로 완제품이 된다는 증거 아님 |
| [Bloomberg 보도](https://www.bloomberg.com/news/articles/2026-10-12/epic-games-delays-disney-project-asks-developers-to-use-more-ai) | 보도로 귀속할 항목. 유료 본문 전체 확인 완료로 표시하지 않음 |
| [Reddit 토론](https://www.reddit.com/r/gamedev/comments/1x4fg83/epic_games_delays_disney_game_and_tells/) | 개인 반응 사례. 산업 전체 의견/공식 사실로 일반화하지 않으며 짧은 필요한 문장만 출처와 함께 사용 |

## Unity 제작 자산과 실제 저장 씬

- KayKit Adventurers Knight: 기존 승인 CC0 모델/애니메이션 재사용. 출처·해시는 `unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers/provenance.json`.
- [Kenney Tiny Dungeon1.0](https://kenney.nl/assets/tiny-dungeon): CC0 도트 시트, 재배포 가능. 원본 ZIP/선택 파일 해시는 `unity/VideoEditing/Assets/ThirdParty/KenneyTinyDungeon/provenance.json`. 원본 라이선스를 함께 보존.
- `Assets/VideoScenes/ai-game-development-human-craft/`에09/17/18/23/25/28 상점 씬과20 입력 응답 씬 저장. 실행 조건·미구현 범위와 캡처 설정은 `planning/scene-design.json`의 각 씬을 참조.
- 자체 제작 씬은 `self-authored-engine-explanation`. 네트워크/영속 저장을 구현·검증했다고 주장하지 않으며, 점프는 응답 지연을 비교하는 교육용 애니메이션이다.

## 잉크 게임 개발 화면 후보

[Mix and Jam / Splatoon-Ink](https://github.com/mixandjam/Splatoon-Ink), 리비전 `10a730cc26d48d9a3f8a34983827291f4ecef5b2`의 `Recordings/movie001–004.mp4`를 로컬 확보했다. URL·SHA256·크기는 `source-manifest.json`. Unity 회색 테스트 공간에서 로봇이 이동하며 바닥/벽에 초록 잉크를 칠하는 개발 녹화다. Nintendo Splatoon 실제 게임 플레이, AI 생성 증거, 개발 소요시간/성능 증거로 표시하지 않는다.

001/002/003 각12개 프레임을 관찰했다.001/002는 이동·바닥/벽 칠하기 후보이고003은 동작 중복이 많아 우선 제외한다.004는 아직 시각 검수하지 않았다. 정확한 in/out, 전체 동작 재생과 오디오 권리는 pending이다. 샘플 프레임 확인을 전체 재생 통과로 기록하지 않는다.

[저장소 LICENSE](https://github.com/mixandjam/Splatoon-Ink/blob/10a730cc26d48d9a3f8a34983827291f4ecef5b2/LICENSE)는 이용/복제/수정/게시와 고지 보존 조건을 포함한다. README의 MIT 명칭만으로 모든 녹화 속 제3자 캐릭터·플러그인·오디오까지 표준 MIT 권리가 확정되었다고 보지 않는다. 정확한 적용 범위·Jammo 자산/오디오 조건을 마친 뒤 채택한다. 현재 분류는 `independent-development-demo`, 사용 상태는 `candidate-rights-pending`이다.

## 실제 게임 영상 미확보 부분

- Thomas Brush: [공식 사이트](https://www.thomasbrush.com/), [Atmos Games presskit](https://atmosgames.com/presskit) 조사. Twisted Tower 실제 사용 가능 녹화는 미확보.
- WoW: [최신 Midnight 공식 정보](https://worldofwarcraft.blizzard.com/en-us/midnight)를 검토했지만 최신작 실제 플레이 원본은 미확보. [Blizzard Video Policy](https://www.blizzard.com/en-gb/legal/2068564f-f427-4c1c-8664-c107c90b34d5/blizzard-video-policy)는 게임에 들어 있지 않은 홍보/광고 영상을 제외한다. 따라서 공식 트레일러를 커뮤니티 게임 영상 권한으로 채택하지 않는다.
- 대안 후보 [Nyhver의 Classic Paladin 영상과 사용 허용 문구](https://www.warcraftmovies.com/movieview.php?id=252801), [원본 YouTube](https://www.youtube.com/watch?v=A2VQbPrw9-g): 미다운로드/미재생. 캐릭터 외형 수정과 제3자 음악이 있어 현재 게임 기본 화면·오디오 권리를 가정하지 않는다. 최신 버전 대안 조사와 원래 사례 역할 일치 확인 뒤 결정한다.

원본 녹화·웹페이지·ZIP·QA 이미지는 `shared/sources/ai-game-development-human-craft/`, `shared/output/ai-game-development-human-craft/`에 로컬 보관하며 Git에는 넣지 않는다. 파일 확보는 최종 비율/권리/움직임 검수나 영상 완성을 의미하지 않는다.
