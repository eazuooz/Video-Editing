# AI 게임 제작 근황 — 여섯 게임 소개

2026-10-18 공개 자료 확인 기준. 현재는 **자료 조사·대본 초안·씬 설계** 단계이며 완성 영상은 아직 없다. 이번 편은 사용자가 선택한 게임 소개 형식으로 제작한다. 정해진60:40 비율이나 Unity 재현 씬을 강제하지 않는다. 최종 마스터는1080p60이며 완성본은Drive에서 먼저 검수한다.

## 조사 결과

| 게임 | 제작 기간의 의미 | 모델 | 제작 도구 |
|---|---|---|---|
| [I Just Wanted to Fish](https://store.steampowered.com/app/5350560/I_Just_Wanted_to_Fish/) | 약3주 · 제작자 진행 보고 | Claude Opus 5.5 | Claude Code, Blender MCP, Blender 5.2, Unity 6 HDRP, Unity MCP |
| [Emberfall — Luminati](https://broad-grass-ea4b.supportinfo-593.workers.dev/editor) | 전체 기간 미공개/미확인 | Claude Opus 5.5 (소개자 언급만 확인) | Luminati browser editor, Three.js, JSON level format luminati-level v1 |
| [Nightshoal](https://profactor.itch.io/nightshoal) | 11주 차 · 개발 진행 보고 | Claude Opus 5.5 / Codex Astra | Godot, Tripo AI, Blender MCP, ElevenLabs sound effects, Stable Audio music, OpenAI image API |
| [VECTOR: Anti-Gravity Racing](https://wavedash.com/games/vector-anti-gravity-racing) | 전체 기간 미공개/미확인 | Opus, exact version undisclosed (소개자 언급만 확인) | Three.js, WebGPU with WebGL 2 fallback, Blender for models as described by the creator |
| [AUGURY: Duel of the Gods](https://sybiote.itch.io/augury-duel) | 전체 기간 미공개/미확인 | 정확한 모델 미공개 | Phaser, TypeScript, DreamLayer, ImageGen, Local Python Pixelize, Creator's Move/Pose/Rig/Arena Studio tools |
| [Rally Road Rash — Off-Road Championship](https://sandscape.app/play?g=3UpDloEh) | 약3일 · 초기 버전 | Opus 5.5 / Astra 6 | Sandscape, Meshy, ElevenLabs music |

기간은 완료까지 걸린 동일한 척도가 아니다. 첫 버전의3일, 진행 중인11주 차, 약3주 작업을 구분한다. 출처별 주장과 반례는 [연구 기록](../sources/research.json), 확보 파일·해상도·권리는 [자료 목록](../sources/media.json)에 연결했다.

## 전체 대본과 화면 구성

### 01. 게임부터 보자

안녕하세요, 얌얌코딩입니다. 물고기를 낚고, 미래의 트랙을 달리고, 신들의 다음 공격을 예측하는 게임. 이 작품들의 제작 과정에는 어디까지 AI가 들어갔을까요?

오늘은 여섯 게임의 실제 모습부터 보고, 제작자가 밝힌 개발 기간과 사용 도구를 함께 살펴보겠습니다. 짧게 만든 초기 버전과 여러 주 동안 다듬고 있는 게임도 구분할게요.

먼저, 바닷속까지 들여다보이는 이 작은 섬으로 가보죠.

화면: Fish opening then brief VECTOR/Rally glimpses; game titles persist through source changes.

다음 연결: Island from overview becomes Fish opening.

### 02. I Just Wanted to Fish

아이 저스트 원티드 투 피시는 섬을 돌아다니며 낚시하는 게임입니다. 모래사장에 선 캐릭터가 낚싯대를 드리우고, 얕은 물 아래에는 물고기와 산호가 보이죠. 해변에는 작은 게도 돌아다닙니다.

제작자가 공개한 작업 기간은 거의 삼 주입니다. 개발 중인 버전을 소개한 시점의 기간이고, 출시까지 끝났다는 뜻은 아닙니다.

사용 모델은 클로드 오퍼스 오 점 오. 블렌더에서 입체 모델과 움직임을 만들고, 유니티 식스에서 게임으로 연결했습니다. 이 과정에 블렌더 엠씨피 같은 연결 도구를 썼어요. AI가 문장으로 답하는 데서 끝나지 않고, 제작 프로그램의 작업을 실행하도록 연결한 겁니다.

그렇다고 사람이 결과를 그대로 받은 건 아닙니다. 제작자는 지형과 배치를 직접 정하고, 참고 그림을 주고, 나온 모델과 동작을 보면서 여러 번 수정했습니다. 같은 낚시 장면도 캐릭터, 물, 환경을 맞추는 작업이 모여 만들어진 거죠.

입체 모델을 제작 프로그램에서 만들었다면, 다음 작품은 브라우저 속 작은 세계를 보여 줍니다.

화면: Beach fishing and crab from creator footage, followed by a compact Blender MCP → Unity6 flow beside a relevant frame.

다음 연결: 3D asset pipeline → browser miniature world.

### 03. Emberfall — Luminati

엠버폴, 루미나티입니다. 캐릭터는 도트 그림처럼 보이지만, 집과 길이 놓인 공간은 카메라를 돌려서 다른 각도로 볼 수 있습니다. 그림을 올려놓은 작은 모형 마을 같은 느낌이죠.

공개된 편집기에는 쓰리 제이에스가 표시되어 있고, 지형 높이와 물건, 조명을 편집하는 기능이 있습니다. 게임 화면에서는 캐릭터 이동과 카메라 회전도 직접 확인할 수 있었어요.

다만 정확한 AI 모델 버전과 전체 개발 기간은 제작자의 일차 자료에서 확인하지 못했습니다. 짧은 시간에 만든 첫 버전이라는 소개를, 지금 보이는 게임 전체의 제작 기간으로 바꾸어 말하지는 않겠습니다.

작은 세계의 인상이 눈에 들어왔다면, 이번에는 그 안에 이야기와 여러 시스템을 계속 쌓아 가는 사례를 보죠.

화면: Village and rotated-camera screenshots; two-state comparison labelled actual captured views. Editor controls named only when their screen is shown.

다음 연결: Small world → ongoing story and systems in Nightshoal.

### 04. Nightshoal

나이트숄도 낚시와 탐험을 다루지만, 분위기는 다릅니다. 절벽과 숲 사이로 물길이 이어지고, 배가 그 안을 지나갑니다. 제작자는 여기에 퀘스트와 이야기, 낚시와 인벤토리 시스템을 계속 더하고 있습니다.

공개된 개발 기록은 십일 주 차입니다. 엔진은 고도, 최근 작업에는 클로드 오퍼스 오 점 오를 사용했다고 밝혔습니다. 이전에는 코덱스 아스트라도 함께 썼고요.

입체 모델은 트리포 에이아이와 블렌더 엠씨피, 효과음은 일레븐랩스, 음악은 스테이블 오디오처럼 작업별 도구를 나누었습니다. 도구 이름이 공개됐어도, 그 안에서 사용한 세부 모델 버전까지 모두 알려진 것은 아닙니다.

이 사례에서는 여러 AI 작업이 같은 게임으로 이어지도록 관리하는 과정이 중요합니다. 무엇을 만들지 정하고, 결과를 확인하고, 서로 맞지 않는 부분을 고치는 일이 남아 있죠. 실제로 제작자도 지도와 기능을 계속 다시 다듬고 있다고 설명합니다.

이렇게 세계를 채우는 게임에서 시선을 돌리면, 조작에 바로 반응해야 하는 빠른 레이싱도 나옵니다.

화면: 25s environment trailer plus authored task/tool map beside one selected environment frame and creator update excerpt.

다음 연결: World building → responsive racing.

### 05. VECTOR: Anti-Gravity Racing

벡터, 안티 그래비티 레이싱입니다. 바퀴 대신 공중에 뜬 기체로 트랙을 달립니다. 코너를 통과하고, 가속 구간을 밟고, 다른 기체와 순위를 겨루죠.

제작자는 코딩을 AI와의 대화로 진행했다고 밝혔습니다. 기반은 쓰리 제이에스이고, 브라우저의 그래픽 기능인 웹 지피유를 사용합니다. 지원하지 않는 환경에는 웹 지엘 투 방식도 마련했다고 설명해요. 모델 제작에는 블렌더를 사용하도록 AI에 요청했다고 합니다.

정확한 개발 기간과 사용 모델 버전은 공개 자료로 확정할 수 없었습니다. 그래서 이 게임을 사흘 만에 완성했다거나, 특정 최신 모델 하나의 성과라고 단정할 수는 없어요.

빠른 화면만큼 흥미로운 것은 정반대로, 시간을 멈추고 한 수씩 생각하게 만드는 게임입니다.

화면: Creator racing segments showing corners and boost path. Compact Three.js/WebGPU label after game introduction.

다음 연결: Fast input → paused tactical decisions.

### 06. AUGURY: Duel of the Gods

오거리는 신들이 싸우는 게임인데, 버튼을 빠르게 누르는 방식과는 다릅니다. 행동을 고르는 동안 시간이 멈추고, 이동을 선택하면 초록색 모습으로 예상 위치를 보여 줍니다. 선택을 확정한 뒤에 결과가 진행돼요. 상대가 무엇을 할지 예상하는 판단이 중심입니다.

제작 보고서에 공개된 기반은 페이저와 타입스크립트입니다. 캐릭터와 소품, 효과 이미지에는 드림레이어와 이미지 생성 도구를 사용했습니다. 정확한 모델명과 전체 개발 기간은 공개하지 않았습니다.

여기서는 AI가 만든 그림을 곧바로 완성된 애니메이션으로 쓰지 않았다는 점이 눈에 띕니다. 배경을 지우고, 크기와 색을 정리하고, 몸과 소품의 겹치는 순서와 움직임을 맞추는 과정이 있었습니다. 생성한 그림을 게임에서 읽히는 캐릭터로 바꾼 거죠.

이런 손질이 필요하다는 점은, 다음의 짧은 제작 기간을 볼 때도 함께 기억할 만합니다.

화면: Actual1920×1080 before/preview/result tutorial screenshots, then minimal illustration of picture → prepared sprite → animation.

다음 연결: Preparation and refinement → short initial Rally milestone.

### 07. Rally Road Rash

랠리 로드 래시는 흙길에서 차량이 부딪치고, 점프대를 넘고, 로켓까지 사용하는 레이싱 게임입니다. 제작자는 약 사흘 만에 초기 버전을 만들었다고 밝혔습니다.

작업 공간은 샌드스케이프. 차량과 물리 코드는 오퍼스 오 점 오, 화면을 다듬는 데는 아스트라 식스를 사용했다고 합니다. 주요 차량과 소품은 메쉬, 단순한 배경 물체는 코드로 만든 도형을 함께 썼고요.

제작자는 레벨을 직접 편집했고, 이십오 년의 경험이 있다고 밝혔습니다. 오토바이의 물리 동작도 아직 다듬는 중이라고 했어요. 사흘이라는 숫자는 이런 초기 버전의 기록입니다. 누구나 같은 시간 안에 같은 결과를 낸다는 보장은 아니죠.

그래서 여섯 게임을 나란히 놓으면, 개발 기간의 숫자보다 더 분명하게 보이는 변화가 있습니다.

화면: Creator trailer action excerpts: dirt track, jump and vehicles. Keep creator title shot out of repeated closing.

다음 연결: Initial milestone → cross-game conclusion.

### 08. 어디까지 왔을까

AI가 쓰인 곳이 코드에만 머물지 않습니다. 모델과 그림, 애니메이션 작업, 소리와 음악까지 연결되고, 그 결과를 직접 조작해 볼 수 있는 게임도 공개되고 있습니다.

하지만 AI로 만들었다는 한마디 안에는 서로 다른 과정이 들어 있습니다. 어떤 모델을 썼는지, 무엇을 생성했는지, 사람이 무엇을 골라서 고쳤는지를 함께 보면 결과가 더 잘 보입니다.

오늘 내용은 이천이십육 년 시월 십팔 일에 확인한 공개 자료 기준입니다. 여섯 게임의 링크와 제작 기록은 설명란에 정리해 둘게요. 여러분은 어떤 게임을 직접 해 보고 싶으신가요?

화면: Three concise contrasts over relevant retained game frames: code / assets / human selection; final single question, then original10s member outro.

다음 연결: Carry music into original membership outro.

## 제작 상태

- 완료: 제작자 자료 조사, 미확인 정보 분리, 네 작품1080p이상 영상 확보, 두 브라우저 게임 실제 조작·1080p 캡처, 한영 대본 초안과8개씬 구성.
- 화면 시안: 실제 자료·자막을 넣은12초 무음1080p60 샘플 제작.1080p/375px 화면 확인과 출처 라벨의 게임UI 가림 수정 완료. 완성 영상이나 음성 검수본은 아님.
- 진행: 사용할 움직이는 구간의 세부 검수와 음성 확정 후 컷 배치.
- 대기: 사용자의 이전 지시에 따른 게임·Unity 사용 종료/GPU 인계 확인 후Qwen3 음성 생성.
- 미완료: 음성·전체 편집·최종QA·4파일·Drive 검수본.
- 별도 승인 경계: 이 버전의Drive 사용자 검수 후YouTube 업로드. 자동 다음 편 없음.
