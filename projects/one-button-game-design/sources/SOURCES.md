# 원버튼 게임 디자인 — 사용 자료와 권리 기록

확인일: 2026-09-30. 제작용 자료 확보와 최종 게시 승인은 별도다.
현재 원본 구간은 production/final-v2/plan.json과 selected-footage.json의 cuts에 초 단위로 기록한다. final-v1은 이전 제작 기록으로 보존한다.

## 실제 게임 녹화

- Kirby Super Star (SNES): World of Longplays, Ironsharp & KTheorem.
  https://www.youtube.com/watch?v=GMjG70AHm00
  메가톤 펀치와 사무라이 커비의 실제 게임 실행 화면.
  raw/super-star-minigames.mp4는 원본 1980–2340초를 내려받은 파일이다.
- Kirby's Adventure (NES): World of Longplays, lemmy556.
  https://www.youtube.com/watch?v=rJXM4EPbPe0
  에그 캐처의 서로 다른 시도. raw/adventure-opening.mp4는 원본 0–900초,
  raw/adventure-egg-2.mp4는 2637–2670초, raw/adventure-egg-3.mp4는 4654–4690초다.
  동일 구간 반복, 느리게 재생, 마지막 프레임 늘리기를 사용하지 않는다.

파일 위치: shared/assets/one-button-game-design/.
녹화물 재사용 조건: [World of Longplays 공식 FAQ](https://longplays.org/infusions/faq/faq.php?cat_id=1).
자체 해설과 편집을 더하고 웹사이트·채널·플레이어를 영상 및 설명란에 표기한다.
게임마다 편집 없이 이어지는 구간을 1분 이내로 유지한다. AI 학습에는 사용하지 않는다.
이 사이트의 녹화는 재녹화·세이브 상태를 사용할 수 있으므로 실제 사람의 반응속도나 실력의 증거로 쓰지 않는다.
게시 후 완성 링크를 전달하는 FAQ 요청은 미완료다. 외부 연락은 승인 없이 보내지 않는다.

게임 저작권: Nintendo / HAL Laboratory.
[Nintendo 게임 콘텐츠 가이드라인](https://www.nintendo.co.jp/networkservice_guideline/en/index.html)
(2024-09-02 개정)을 확인했다. 출시된 게임에 채널 자체 해설과 설명을 더한다.
Nintendo 공식 제작물·후원물로 표시하지 않는다. 게시 시 적용 조건을 다시 확인한다.

## 직접 만든 실제 플레이테스트

production/prototype-v2/index.html의 연타 및 누르기·떼기 게임을 실제 키 입력으로 실행했다. 기존 prototype/index.html과 v1 녹화도 보존한다.
production/capture-playtests-v2.cjs로 서로 다른 입력 간격·누름 시간을 사용해 각각 40초를 녹화했다.
mash-v2-input-log.json과 charge-v2-input-log.json에 현재 키 입력 기록을 보관한다.
영상에 직접 만든 플레이테스트임을 표기한다. 외부 상용 게임이나 사람의 성능 측정으로 소개하지 않는다.
두 녹화는 소스 음향이 없어 승인된 Nimbus가 배경음을 맡는다.

## 자체 설명 도식

motion-canvas/src/projects/one-button-game-design/diagram.tsx.
화이트 연구 발표 스타일로 새로 그린 2.5D 버튼·진행 경로·목표·신호·입력 결과 비교다.
설명 도식의 시간은 실제 게임 화면 비중에 포함하지 않는다.

## 음악 — 최근 영상과 같은 곡으로 승인

Nimbus — Eveningland (YouTube Audio Library).
2026-09-30 사용자 승인: “아니 화면 프레임 에 사용된 음악있어 그걸로해줘”.
최근 small-window-game-design의 실제 최종 믹스 선택 기록을 기준으로 했다.
기존 라이선스 기록: shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md.

기존 MP3는 이 컴퓨터에 없어 기록에 연결된 곡 소개 업로드에서 제작용 사본을 복원했다.
https://www.youtube.com/watch?v=ZOc84gXN-lg (MusiCat).
Nimbus-Eveningland-restored.m4a가 기존 MP3와 바이트가 동일한 원본이라고 주장하지 않는다.
원래 Audio Library에서 받은 파일 확인은 게시 전 잔여 항목으로 보존한다.
설명란 표기: Music: Nimbus — Eveningland (YouTube Audio Library).
Discovery와 Wanderlust는 이전 후보이며 사용하지 않는다.

## 목소리와 회원 엔딩

사용자가 최신 영상의 목소리·회원 이미지 재사용을 승인했다.
기존 추출 스크립트에 기록된 Video Project 24.mp4의 15–35초를 복원해 기준 목소리로 사용했다.
개인 음성 원본과 모델은 Git에 포함하지 않는다.
회원 엔딩은 shared/assets/membership/member-list-20260929.png 원본을 표시한다.
프로필·표시 이름·회원 배지를 함께 보존하고 잘린 핸들을 추정하지 않는다.
새 영상의 제목은 정확히 “멤버쉽가입 감사드립니다.”이며 10초다.

## 개념 참고

- Masahiro Sakurai on Creating Games, The Potential of One Button:
  https://www.youtube.com/watch?v=tafG03n89MY
  사용자가 제공한 전사문을 개념 참고로 삼았다. 원본 영상·음성은 삽입하지 않았다.
- Nintendo, Megaton Punch: https://www.nintendo.co.jp/ds/ykwj/subgame/index5.html
  DS판 설명은 세 입력 단계 참고이며 SNES 영상의 버전 근거로 쓰지 않는다.

## 2026-09-30 추가 게임 — final-v2

|게임|녹화 원본|플레이어|로컬 확보 범위|삽입 목적|
|---|---|---|---|---|
|Canabalt HD|https://www.youtube.com/watch?v=p3rWb9eso0g |mihaibest / World of Longplays|원본 0–210초|장애물을 읽는 원버튼 입력, 누르는 길이에 따른 점프|
|Geometry Dash|https://www.youtube.com/watch?v=InDaD9xyfQ8 |RickyC / World of Longplays|원본 0–180초|장애물을 읽고 점프할 순간을 선택하는 타이밍|

각 실제 삽입 범위는 현재 selected-footage.json과 final-v2/plan.json에 기록됩니다.
같은 원본 시각을 반복하지 않고, 영상 속 웹사이트·채널·플레이어 표기와 게시 설명란 출처를 함께 제공합니다.
두 신규 게임의 소스 음향에는 별도 저작권 음악이 함께 섞여 있어 음소거하고 승인된 Nimbus를 계속 재생합니다. 기존 커비 구간은 원음을 유지합니다.

게임 규칙의 1차 근거:

- [Canabalt 제작사 Steam 설명](https://store.steampowered.com/app/358960/Canabalt/): 버튼 하나로 플레이하는 달리기 게임.
- [개발자 Adam Saltsman의 Tuning Canabalt](https://www.gamedeveloper.com/design/tuning-canabalt): 누르는 길이가 점프 높이를 바꾸는 원리를 개발자가 직접 설명합니다. Flash판 수치와 HD판 수치를 동일하다고 주장하지 않습니다.
- [Geometry Dash 제작사 Steam 설명](https://store.steampowered.com/app/322170/Geometry_Dash/): 리듬 기반 장애물 플랫폼 플레이. 선택 구간의 큐브 점프 동작을 실제 확인했습니다.

권리 기록:

- 녹화물 재사용은 [World of Longplays 공식 FAQ](https://longplays.org/infusions/faq/faq.php?cat_id=1)의 교육 해설·편집 및 웹사이트/채널/플레이어 출처 조건을 따릅니다.
- [RobTop Games 영상 정책](https://www.robtopgames.com/youtube.html)은 Geometry Dash 영상 제작·스트리밍·수익화를 허용합니다. 제3자 음악의 별도 권리를 포함하지 않으므로 신규 구간의 소스 음향을 사용하지 않습니다.
- Canabalt 게임 권리는 Finji / Kittehface Software, 음악 권리는 Danny Baranowsky 등에 있습니다. 녹화자 허용이 게임 권리까지 이전하지 않습니다. 짧은 교육용 해설 발췌로 제작하며 제작사 별도 게시 정책 확인은 최종 게시 전 권리 검수 항목으로 남깁니다. 원본 그래픽·코드 파일을 별도 재배포하는 허락으로 해석하지 않습니다.
