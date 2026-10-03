# 화면 움직임을 선택하게 만들기

사전 검토: 현재 전체 프로젝트 내용과 Studio 멀미0건/카메라3건/시야각1건을 직접 비교하고 distinct --check 뒤 생성했다. SetTarget, 다중 RenderTarget/알파, 스프라이트 좌표, FOV 기하/FPS 파이프라인과 겹치는 강의를 만들지 않는다.

질문: 목표를 조준할 때 화면 전체를 돌려야 하는가? 게임에 필요한 이동과 추가 연출을 어떻게 나누고 선택 가능하게 만드는가?

- 01 노즐만 돌리면 될까요? (actual-existing-game-action): Observe view, tool and target relationship before the linked explanation. 관찰: Read background lines, target surface and tool movement independently.. PF5L_2g9UVQ 48–69s; PF5L_2g9UVQ 99–118s; PF5L_2g9UVQ 187–199s
- 02 화면에서 보이는 이동과 몸의 감각 (explanation): Visible motion signals and individual response are separate from game-design choices. 관찰: Two signal paths, then view-turning versus added shake..
- 03 배경이 멈춰 있어도 조준은 움직인다 (actual-existing-game-action): Observe view, tool and target relationship before the linked explanation. 관찰: Read background lines, target surface and tool movement independently.. PF5L_2g9UVQ 132–156.5s; PF5L_2g9UVQ 156.5–169s; PF5L_2g9UVQ 199–227s
- 04 조작과 추가 연출을 따로 조절하기 (explanation): Necessary view-turning, tool aim and additive effects have different responsibilities. 관찰: Input route stays active as only the additive layer changes..
- 05 위치를 옮기는 일과 표면을 따라가는 일 (actual-existing-game-action): Observe view, tool and target relationship before the linked explanation. 관찰: Read background lines, target surface and tool movement independently.. PF5L_2g9UVQ 268–290s; PF5L_2g9UVQ 301–309.8s; PF5L_2g9UVQ 310–339s; PF5L_2g9UVQ 345–357.8s
- 06 한 번에 한 가지를 바꾸는 옵션 (explanation): Sensitivity, decoupled aim and extra shake are different player choices. 관찰: One option changes one labelled role; reset is visible..
- 07 게임 규칙이 시야의 방향을 바꿀 때 (actual-existing-game-action): Observe view, tool and target relationship before the linked explanation. 관찰: Read background lines, target surface and tool movement independently.. 6slinvkF0Rs 31.1–35.8s; 6slinvkF0Rs 36.1–39.7s; 6slinvkF0Rs 48–52.2s; 6slinvkF0Rs 40.2–42.2s; 6slinvkF0Rs 16.1–20.7s; 6slinvkF0Rs 23.1–30.1s; PF5L_2g9UVQ 247.5–267s; PF5L_2g9UVQ 359–383s
- 08 천천히 움직이면 언제나 편할까요? (explanation): Motion duration and arrival orientation are separate questions; do not promise a universal comfort transition. 관찰: Gradual path versus immediate change, common arrival landmarks..
- 09 작업할 목표가 계속 읽히는가 (actual-existing-game-action): Observe view, tool and target relationship before the linked explanation. 관찰: Read background lines, target surface and tool movement independently.. PF5L_2g9UVQ 408–433s; PF5L_2g9UVQ 437–460s; PF5L_2g9UVQ 465–483.8s
- 10 선택을 숨기지 않고 되돌릴 수 있게 (explanation): An understandable, accessible, saved and reversible choice matters beyond merely having an option. 관찰: Find → explain → save → restore; check each responsibility..
- 11 같은 작업을 다른 방향에서 읽기 (actual-existing-game-action): Observe view, tool and target relationship before the linked explanation. 관찰: Read background lines, target surface and tool movement independently.. PF5L_2g9UVQ 484–510s; PF5L_2g9UVQ 510–528s; PF5L_2g9UVQ 528–552.4s
- 12 효과보다 먼저 선택과 역할을 설계하기 (explanation): Separate camera responsibilities, retain task readability, offer choice and get individual feedback. 관찰: Movement / target / option / revert checks..

실제 행동 → 해당 흰2.5D 설명을6번 교차한다. 후보은행은 최종 사용량이나60:40통과 증거가 아니다. 실제 TTS 길이 이후 모든 컷/자막을 맞추고, 설명을 줄이지 않고 관련 미사용 구간을 더한다. 루프·저속·타이틀·메뉴·자가 게임0. 아래 가운데 자막(960,970)은 움직이지 않으며 원본 구간/크롭/큐를 조정한다.
