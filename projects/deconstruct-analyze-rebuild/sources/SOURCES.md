# 자료 출처

## 개념 연구와 독립 대본

- 참고 주제: [Deconstruct, Analyze, and Rebuild — Masahiro Sakurai on Creating Games](https://www.youtube.com/watch?v=7VD0K1Sr5u0), 사용자 재생목록 7번. YouTube 제공 일본어 자동 자막을 내부 연구용으로 읽었다. 원본 영상·오디오를 사용하지 않으며 대본을 그대로 복사하거나 전체 번역하지 않는다. 우리 대본은 행동 관찰 → 조건 비교 → 다른 규칙으로 조립이라는 원리와 자체 점프·문·잠입 테스트를 새 문장으로 설명한다.
- Celeste 동작 확인: [개발사 공식 페이지](https://www.celestegame.com/), [개발사 제공 Steam 설명](https://store.steampowered.com/app/504230/Celeste?l=english). 점프·공중 대시·오르기와 빠른 재시도를 설명하는 내용만 사실 확인에 사용했다. 웹페이지 설명 확인이 영상 이용 허락을 뜻하지 않는다.
- Portal 공간 퍼즐 확인: [Valve 제공 Steam 설명](https://store.steampowered.com/app/400/Portal?l=english). 포털로 자신과 물체를 이동시키는 공간 퍼즐 원리만 확인했다. 실제 자료화면은 사용 근거를 별도로 확보한다.
- `projects/jump-physics/sources/gameplay.md`의 Mario·Celeste 클립은 CC BY 표시와 설명란 출처를 전제로 만든 이전 기록이다. 새 공개 설명에서 출처를 제외하라는 요청만으로 라이선스 의무가 사라지지 않는다. 원본 조건을 다시 확인하고 필요한 영상 내 표시 등을 갖추기 전에는 새 컷으로 사용하지 않는다.

## 채널 공통 자산

- 채널 고양이 원본: `shared/assets/branding/yamyamcoding-cats-original.png`, 기존 승인 인트로에 재사용한다.
- 회원 원본: `shared/assets/membership/member-list-20260929.png`, 프로필·표시 이름·배지 12개 행을 함께 유지한다. 잘린 핸들은 추정하지 않는다.
- 승인 BGM: Nimbus — Eveningland. 실제 입력은 `shared/assets/music/youtube-audio-library/Nimbus-Eveningland-restored.m4a`. `shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md`의 원래 Audio Library 파일 확인 경고를 보존한다.

## 이번 영상의 새 게임 검토 — 2026-10-01

Mario·Celeste는 이전 영상 사용 이력이 있어 이번 최종본에서 제외했다. 저장소 대본·출처·게시 기록을 검색한 결과 아래 세 게임은 기존 프로젝트에 사용 이력이 없었다. 후보와 제외 이유는 `game-candidates.json`, 실측 원본 컷과 타임라인은 `selected-footage.json`에 기록한다. 사용자 지시로 YouTube 업로드는 보류한다.

| 게임 / 로컬 파일 | 원본 · 제공자 | 확인한 사용 근거 | 실제 동작과 컷 선택 |
| --- | --- | --- | --- |
| Super Meat Boy / `raw/super-meat-boy-play.mp4` | [G-Gou_Plays](https://www.youtube.com/watch?v=Isk1PFfQOUE) | 업로더 설명에서 원본 통째 재업로드를 제외하고 편집·추가 콘텐츠·상업 이용을 허용. Team Meat 별도 게시 정책은 게시 전 확인 대기 | 3:00부터 받은 파일. 처음 확보했던 인트로·설정 화면은 제외하고 로컬22초부터 실제 점프·착지를 사용. 16초 컷은 전환 검은 화면이 있어 최종 검수에서 제외. 원본 검은 여백을 제거하고 게임 비율을 보존한 동일 소스 확장 배경을 사용 |
| Hollow Knight / `raw/hollow-knight-new.mp4` | [Royalty Free Game Clips](https://www.youtube.com/watch?v=Yj-MX_wBhmc) | 업로더가 상업·비상업 사용 허용 및 출처 선택을 명시. [Team Cherry FAQ](https://www.teamcherry.com.au/faq)의 게임 영상·수익화 허용 확인 | 원본 0:30부터 확보. 발판 읽기·점프·대시 구간, 로컬 18초 및 30초부터 서로 다른 컷. 영상 스트림 약92초와 오디오150초를 구별해 실제 프레임 범위만 사용 |
| Portal / `raw/portal.mp4` | [joel](https://www.youtube.com/watch?v=AmJ4orxVpss) | 업로더가 원본 통째 재업로드를 제외한 독립 콘텐츠 이용을 명시적으로 허용. [Valve Video Policy](https://store.steampowered.com/video_policy) 확인. 버전 불명 CC 표시에 의존하지 않음 | 원본 0:15부터 확보. 초반 큐브 운반보다 로컬45초·58초부터 입구·출구 배치와 공간 이동을 사용 |
| 직접 만든 비교 테스트 / `playtests-v2/` 및 `playtests-v3/variants-sound.mp4` | 채널의 독립 코드·도형·물리·절차적 효과음 | 원본 제작. 실제 키 입력·충돌·성공·실패 로그를 함께 저장 | 착지 폭, 재시도 대기, 행동 기록은 v2. 점프·문·빛 세 규칙과 서로 다른 복귀 위치는 v3. 반복 루프나 인위적 저속 없이 서로 다른 실제 시도를 촬영 |

외부 게임 소리는 별도 음악 권리를 분리하기 위해 제거했다. 승인된 연속 Nimbus와 직접 만든 입력·충돌 효과음을 사용한다. 업로더·원본 링크는 영상 안 짧은 출처 표시에 보존하며 공개 설명의 별도 출처 블록은 만들지 않는다. 원본 다운로드 메타데이터 `*.info.json`은 임시 URL을 포함하므로 Git에 넣지 않는다.

원본 컷은 로컬 파일 시작 시각과 전체 원본 시작 시각을 함께 기록한다. 실제 사용 구간은 최종 음성 길이에 따라 확정한 `production/final-v1/plan.json`을 기준으로 한다. 위의 이전 Mario·Celeste 연구는 제작 이력이며 이번 렌더의 사례가 아니다.

외부 영상, 이미지, 음악, 효과음을 추가할 때 아래 표에 기록합니다. 출처를 확인하지 못한 자료는 최종 영상에 사용하지 않습니다.

| 파일명 | 종류 | 원본 링크 | 권리자/채널 | 라이선스·허용 근거 | 사용 구간 | 원음 사용 | 출처 표기 | 확인일 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 현재 컷 목록 | 영상·자체 SFX | 위 표 및 selected-footage.json | 위 제공자 및 채널 독립 제작 | game-candidates.json | 실측 plan.json | 외부 원음 제거 / 자체 SFX 유지 | 내부 기록 및 영상 내 출처 | 2026-10-01 |

## 메모

- 원본 제목과 업로더 이름을 함께 남깁니다.
- 허용 조건을 확인한 페이지나 라이선스 링크를 기록합니다.
- 편집·비평 목적이라도 필요한 분량만 사용하고 출처를 표시합니다.
- 게임 영상은 화면뿐 아니라 원음 사용 여부와 권리 위험도 따로 기록합니다.
- BGM은 사용자 승인 전에는 최종 영상에 넣지 않습니다.
- CC BY 음악은 설명란에 붙일 정확한 출처 문구까지 기록합니다.
