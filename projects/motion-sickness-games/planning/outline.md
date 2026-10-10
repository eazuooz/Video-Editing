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

## 공개 전 이해도 수정본 — teaching-clarity-v1

기존 12씬의 모든 설명·순서·승인 PCM은 보존했다. 아래 개론과 연결 문단은 음성 제작 전에 `production/revision-teaching-clarity-v1/paired-script-direct-review-v1.json`에서 독립 KO/EN으로 검토했으며, 이 기획 문서는 검수된 수정본을 채택하는 시점에 해당 기록을 합쳐 보존한다.

고양이 2초 다음 개론: 게임의 목표를 따라가면서도 화면은 덜 돌릴 수 있을까요? 청소 게임의 조준과 시점, 퍼즐에서 방향이 바뀐 뒤 목표를 찾는 단서를 차례로 보겠습니다. 이 관찰을 멀미를 고려한 카메라 설정과 되돌리기 기능의 설계로 연결해 보죠. 먼저 물줄기로 바닥의 때를 지우는 장면에서, 빨간선으로 표시한 물줄기 방향과 파란 기둥 표시를 따로 보세요.

개론 음성은 실측 22.4초, 도입 씬은 고유 정상속도 행동과 입체 설명을 합해 25.116667초다. 빨간 표시를 보기 전에 물줄기로 때를 지우는 목표를 말한다. 파란 기둥과 노란 바닥 표시는 물줄기와 배경의 움직임을 따로 읽는 데 쓰며, 실측 게임 세계 좌표·각도나 개인의 멀미 개선 효과를 주장하지 않는다.

청소 목표와 조준/시점 관찰 → 보이는 움직임과 개인 반응 구분 → 필요한 조작과 부가 연출 분리 → 위치·표면을 바꿀 때 필요한 방향 전환 → 이해 가능하고 되돌릴 수 있는 옵션 → 방향을 바꾼 뒤 목표를 다시 찾는 단서 → 퍼즐의 서로 다른 발췌와 도착 방향 비교 → 목표 가독성과 옵션의 저장/복구 → 다른 방향에서 같은 작업을 다시 읽고 역할·선택·피드백으로 결론을 맺는다. 06과 07 사이 새 06b는 조준을 나눠도 목표를 다시 알아봐야 한다는 질문으로 게임 변경의 이유를 설명한다.

참고 OS4CZkBBbW4의 개인차 → 관찰 가능한 화면 움직임/고정 기준 → 개발자 선택 → 옵션/피드백 흐름과 대조했다. 우리의 도입은 과제부터 보여 주며 약물·임상 조언은 포함하지 않는다. 처음 보는 사람에게 청소의 전후 변화가 더 명료하여 PowerWash를 먼저 사용했고, Talos의 짧은 서로 다른 장면은 연속 퍼즐 성공이나 통제된 비교로 제시하지 않는다. 선택/제외·정확 native PTS·권리 범위는 현재 source-action-bank와 직접검수 기록을 따른다.

원래 실제 게임60:설명40 분류를 유지하며 본편 39473프레임 중 실제 23684 / 설명 15789프레임, 반올림 오차 0.2000000000007276프레임이다. 고양이120/회원600프레임은 제외한다. 최종179 KO/EN큐, 표시·컷·입체 설명 픽셀과 정상1배속 선택 흐름은 현재 final-pixel/direct-flow 기록으로 확인했다. 사람 전체청취·발음·공개권리는 별도 pending이며 채택은 플랫폼 게시/예약 완료가 아니다.
