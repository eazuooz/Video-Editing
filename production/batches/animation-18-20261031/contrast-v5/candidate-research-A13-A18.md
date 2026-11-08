# A13–A18 게임 후보 검수안

조사일: 2026-11-08. **게임 목록 검수 단계**이며 렌더·TTS는 시작하지 않았다. 현재 대본과 원본의 설명 순서를 유지하면서 사례의 적합성과 장르·캐릭터의 차이를 넓히는 안이다.

| 편 | 원본 주제 | 권장 실제 게임·캐릭터 | 관찰할 차이 | 한 화면에서 쌓아 보여줄 단계 | Nintendo |
|---|---|---|---|---|---|
| A13 | 좌우 반전 애니메이션 | **Super Street Fighter II / Dee Jay**, **Super Street Fighter IV / Dee Jay**, **Super Mario Bros. Wonder / Mario** | 2D 반전 → 3D의 앞손·얼굴, 카메라를 위한 몸 방향, 세로 문자 모양 | 몸 회전 / 포즈 반전 → 소품 부착 수정 → 두 카메라 → 대칭 문자 | 1/3 |
| A14 | 애니메이션 블렌딩 | **Horizon Zero Dawn / Aloy**, **EA SPORTS FC 25 / 동일 선수**, **Splatoon 3 / Inkling** | 공격 뒤 이동, 걷기·달리기 전환, 이동 중 상체 행동 | 공격·걷기 시간표 → 가중치 0·0.5·1 → 전환 시간 → 상·하체와 경사 | 1/3 |
| A15 | 손가락 표현 | **Half-Life: Alyx / VR 손**, **Nintendo Switch Sports / Sportsmate**, **Ghostwire: Tokyo / Akito** | 손잡이를 감싸는 각도, 실제 화면에서 손의 크기, 큰 전경 손의 표현 | 손 펴기 → 닿기 → 감싸기 → 쥠; 관절 제어 / 준비된 손 포즈 비교 | 1/3 |
| A16 | 공격 판정과 동작 설계 | **Monster Hunter: World / 태도·랜스**, **Elden Ring / 동일 직검**, **Metroid Dread / Samus** | 베기·찌르기의 경로, 낮은 몸 자세와 피격, 카운터 신호·결과 | 외형·판정 구별 → 같은 순간의 측면/위 시점 → 준비·활성·회수 → 명중 포즈 | 1/3 |
| A17 | 스켈레톤의 표현 한계 | **ARMS / Helix·Ribbon Girl**, **Cuphead / Cala Maria** | 몸·팔의 수축·신장과 곡선, 손그림 목표 실루엣과 3D 제어의 차이 | FK → IK → 목표 고정·굽힘 Hint 변경 → 추가 제어점과 표면 확인 | 1/2 |
| A18 | 두 축 회전 | **Luigi’s Mansion 3 / Luigi**, **Untitled Goose Game / 거위**, **The Last Guardian / Trico** | 고개를 내리고 돌리는 경로, 눈·고개·상체의 시간차, 동물의 관심 표현 | 같은 끝 자세의 세 경로 → 한 축 시작만 변경 → 어깨·쇄골 → 시선 추가 | 1/3 |

A17은 두 게임이 설명 역할을 충분히 나누므로 레이맨을 추가하지 않는다. 2게임의 1/3을 가장 가까운 정수로 반올림하면 Nintendo 1게임이다. 같은 ARMS의 두 캐릭터와 World의 두 무기는 각각 한 게임으로 계산한다.

## 핵심 근거와 선택 이유

- **A13:** [Nintendo의 Wonder 개발자 인터뷰](https://www.nintendo.com/us/whatsnew/ask-the-developer-vol-11-super-mario-bros-wonder-part-2/)가 이동 방향과 카메라에 보이는 얼굴·몸 방향을 조정하는 일을 직접 설명한다. [Dee Jay 제작자 글](https://news.capcomusa.com/kramez/blog/2009/10/02/the_origin_of_dee_jay_straight_from_creator_james_goddard)은 캐릭터와 3D 전환의 근거다. **이 글에 MAXIMUM의 대칭 문자 선택 이유가 나온다고 인용하지 않는다.** Wonder는 카메라용 포즈 조정 사례이며, 모든 동작의 미러링 구현을 입증하는 사례로 확대하지 않는다.
- **A14:** [Guerrilla의 이동 시스템 발표](https://www.guerrilla-games.com/read/player-traversal-mechanics-in-the-vast-world-of-horizon-zero-dawn)와 [EA의 FC25 게임플레이 설명](https://www.ea.com/en/games/ea-sports-fc/fc-25/news/pitch-notes-fc-25-gameplay-deep-dive)을 개발자 근거로 둔다. 숫자와 블렌드 비율은 우리 구현에서만 표시한다. [Splatoon 3 공식 제품 페이지](https://www.nintendo.com/us/store/products/splatoon-3-switch/?xs=1)는 Nintendo 발매 근거다.
- **A15:** [Valve의 Alyx 소개](https://www.half-life.com/en/alyx/)를 VR 상호작용 후보 근거로, [Tango 개발자의 손동작 제작 설명](https://blog.playstation.com/?p=363513)을 전경 손의 표현 근거로 사용한다. [Switch Sports](https://nintendoswitchsports.nintendo.com/)는 **손의 세부 가독성을 아직 보지 못한 조건부 후보**다. 손이 작으면 세부 그립 증거는 Alyx가 맡고 Sports는 화면 크기·중요도 비교에 한정한다.
- **A16:** [Capcom의 World 공식 매뉴얼 안내](https://www.capcom-support.com/hc/en-us/articles/5684038730780-Monster-Hunter-World-Online-Manual), [Elden Ring 공식 전투 가이드](https://www.bandainamcoent.com/pt_br/news/elden-ring-introduction-part-4-combat-guide), [Metroid Dread의 카운터 설명](https://metroid.nintendo.com/dread/news/metroid-dread-report-vol-9/)을 구분한다. World 매뉴얼의 세부 페이지는 403으로 읽지 못했다. 엘든 링의 공식 설명은 낮은 자세의 회피 관계를 뒷받침하지만 내부 도형이나 정확한 프레임 수를 제공하지 않는다. **World를 Wilds로 바꾸지 않는다.**
- **A17:** [Nintendo의 ARMS 캐릭터 설명](https://www.nintendo.com/en-gb/News/2017/May/Introducing-the-fighters-of-ARMS-1223651.html)은 Helix의 몸 전체 수축·신장을 명시한다. [Cuphead 개발진 인터뷰](https://unity.com/made-with-unity/cuphead)는 손그림과 SpriteRenderer 방식을 설명한다. Cuphead를 3D IK의 실증으로 쓰지 않고, 그림의 실루엣을 우리 리그가 어떻게 재현할지 비교한다.
- **A18:** [Luigi’s Mansion 3 공식 제품 페이지](https://www.nintendo.com/en-gb/Games/Nintendo-Switch-games/Luigi-s-Mansion-3-1437312.html?nsuid=70070000009530)로 Nintendo 발매를 확인했다. [genDESIGN의 애니메이터 Q&A](https://www.gendesign.co.jp/qa_01/interview04en.html)는 Trico의 여러 동물 기반 키프레임 제작과 돌아보기·통 받기의 절차적 고개 움직임을 직접 설명한다. **모캡을 쓰지 않았다는 말과 실시간 절차적 애니메이션을 썼다는 설명을 함께 보존한다.**

## 독립 플레이 녹화 탐색 결과

아래는 **검색 메타데이터 또는 기존 기록만 확인한 후보**다. 이번 조사에서 새로 다운로드하거나 실제 동작 프레임을 검수하지 않았다. 제목의 4K·1080p는 업로더의 표시일 뿐 디코딩 검증이 아니다. 공개된 영상 링크 자체는 사용 허가가 아니다.

| 편 | 발견한 후보 | 다음 확인 |
|---|---|---|
| A13 | [SSFII / LongplayArchive](https://www.youtube.com/watch?v=e2CVfXaW5G0), [Wonder](https://www.youtube.com/watch?v=3_tWdqzU4jM) | Dee Jay 양쪽 방향·같은 포즈, 레트로 녹화의 실제 FHD. SSFIV의 적합한 독립 녹화는 추가 탐색. |
| A14 | [Horizon PC 1440p60 표기](https://www.youtube.com/watch?v=8WMqD-IRbYA) | 공격→이동·경사 구간. FC25 연습장과 Splatoon 테스트 공간 녹화는 추가 탐색. |
| A15 | [Alyx VR](https://www.youtube.com/watch?v=20DJBNfhjbw), [Switch Sports / aWiibo](https://www.youtube.com/watch?v=WzddxMIaQN0), [Ghostwire / MKIceAndFire](https://www.youtube.com/watch?v=2IcOIvCLaVg) | VR/NoVR 구별, 손이 실제로 읽히는 구간, Sports의 출시 전 녹화 여부와 차이. |
| A16 | [Metroid Dread 카운터 모음](https://www.youtube.com/watch?v=6I6kptjna44) | 공식 Nintendo 채널이 아님. 타인 클립 재편집·자막·권리 확인. World 태도·랜스와 엘든 링은 적합한 독립 녹화 추가 탐색. |
| A17 | [Cuphead / Games Catalogue](https://www.youtube.com/watch?v=lCwvbXiyKt0) | 기존 기록에 CC BY·1080 표기가 있으나 현재 조건·사용 구간을 재확인. ARMS 독립 플레이 추가 탐색. |
| A18 | [Trico / SourceSpy91](https://www.youtube.com/watch?v=_0J0hHAiuXw), [Trico PS5 / Rubhen925](https://www.youtube.com/watch?v=ki4Lh6aBdQ8), [Luigi / ProsafiaGaming](https://www.youtube.com/watch?v=QegLZGBceCo) | 고개·시선이 큰 탐색 구간인지 확인. 4K 출력과 네이티브 렌더 해상도를 혼동하지 않음. 거위의 기존 공식 홍보 영상은 독립 플레이로 사용하지 않음. |

## 제작 전 보완과 유지 사항

1. 목록 검수 후 선택된 사례만 실제 파일·동작·권리·오디오·FHD를 확인한다. 현재는 후보 단계다.
2. 원본의 설명 순서와 예시 역할을 유지한다. A14는 공격→걷기로 시작하고 축구 걷기→달리기는 가중치 설명에 붙인다. A18의 시선 설명은 회전 축·경로·시간차를 설명한 뒤에 둔다.
3. 같은 화면에서 **같은 대상·크기·카메라·재생 시간**을 유지하고 변화 하나씩 비교한다. 단계를 전부 공격 동작으로 통일하지 않는다.
4. 실제 게임 위 표식은 눈에 보이는 대상과 궤적 안내다. 알 수 없는 내부 보간값·뼈 수·히트박스·처리 시간을 꾸며내지 않는다.
5. 180도는 두 팔 구간이 일직선이 되는 예시다. 모든 컴퓨터 관절의 회전 한계라는 오류를 반복하지 않는다.
6. 게임별 세부 근거, 기존 대본 경로, 보류 후보와 확인 범위는 같은 폴더의 `candidate-research-A13-A18.json`에 기록했다.

**현재 상태:** 후보 조사 완료 / 사용자 게임 목록 검수 대기 / 실제 소스 인수·새 제작 미시작.
