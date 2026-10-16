"""Render the human-readable worklist from the maintained state; never changes media or platforms."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'shared/publishing/video-worklist.json').read_text(encoding='utf-8'))
rows=d['rows'];byid={x['id']:x for x in rows}
def cell(x):return str(x).replace('|',' / ').replace('\n',' ')
def link(r):return f"[{cell(r['title'])}]({r['url']})" if r.get('url') else cell(r['title'])
def review(r):
 s=cell(r['reviewStatus'])
 return ('☑ ' if s=='사용자 승인 완료' else '— ' if s in ['공개본 유지','중복 판단 유지'] else '☐ ')+s
out=['# 전체 영상 작업 순서와 검수 현황','','2026-10-16 기준. 게임디자인·렌더링 특별편·게임수학의 제작과 상태 갱신은 이 채팅과 `D:/Github/VideoEditing`에서만 진행한다. 다른 제작 채팅 세 개는 대기 상태로 확인했으며 새 작업을 전달하지 않았다.','','지금은 **렌더링 1편 승인본의 YouTube 비공개 업로드 → 게임디자인 「게임 보상 기획」 최신 규칙 점검·수정 → Drive 최종 검수** 순서다. 이후 목록은 작업 순서를 보여 주는 제안이며 자동 일괄 착수나 공개 예약 변경을 뜻하지 않는다.','','**표시:** ☑ 제작 완료 = 기존 완성 영상이 있음. ☐ = 미완성/미착수. 검수 필요는 별도 열로 표시하며, 제작 완료를 최신 규칙 합격이나 사용자 승인으로 해석하지 않는다. 공개 영상은 유지한다. 비공개 기존본은 선택할 때 최신 기준으로 검수해 필요한 부분만 수정한다.','','원본 주제 30개(중복 제외 1개 포함), 렌더링 납품 단위 6편, 게임수학 현 범위 20편·후속 후보 13편을 관리한다. 샘플·수정 버전·분할 전 통합본을 새 영상으로 중복 집계하지 않았다.','','## 앞으로의 통합 작업 순서','','공개일과 별개인 검수·제작 순서다. 시리즈 내부 설명 순서는 유지한다. 렌더링1과 다음 게임디자인1편만 현재 실행 범위이며, 그 이후는 한 편씩 선택한다.','','| 순서 | 분야 | 영상 | 현재 상태 | 검수/다음 작업 |','|---:|---|---|---|---|']
out[4]='현재 **렌더링 1편은 승인본 YouTube 비공개 업로드 완료**, 현재 게임디자인 **「게임 보상 기획」의 새 구성·독립 소스·설명 애니메이션을 제작 중**이다. 이 편을 수정하면 전체 Drive 최종본으로 검수받는다. 이후 목록은 제안 순서이며 자동 일괄 착수나 공개 예약 변경을 뜻하지 않는다.'
for i,id in enumerate(d['workOrder'],1):
 r=byid[id];out.append(f"| {i} | { {'D':'게임디자인','R':'특별 렌더링','M':'게임수학'}[r['series']]} | {id} {link(r)} | {cell(r['executionStatus'])} | {review(r)} |")
for series,title in [('D','게임디자인 전체 30개 주제'),('R','특별영상 렌더링 전체 6편'),('M','게임수학 Part2 전체 목록')]:
 out+=['',f'## {title}','','| 번호 | 영상 | 제작 | 검수 상태 | 현재 YouTube 상태 |','|---|---|---|---|---|']
 for r in rows:
  if r['series']!=series:continue
  out.append(f"| {r['id']} | {link(r)} | {'☑' if r['productionComplete'] else '☐'} {cell(r['productionStatus'])} | {review(r)} | {cell(r['platformStatus'])} |")
out+=['','## 복원과 확인이 필요한 항목','','| 영상 | 남은 내용 |','|---|---|']
for r in rows:
 if r['notes']:out.append(f"| {r['id']} {cell(r['title'])} | {cell(r['notes'])} |")
out+=['','## 관리 기준과 근거','','- 기준 파일: [영상별 상태](../shared/publishing/video-worklist.json). 표를 갱신할 때 `python scripts/render-video-worklist.py`를 실행한다. 각 편의 상세 계획·검수 원장은 해당 프로젝트의 기존 파일을 사용한다.','- [실제 Studio 상태 확인](../shared/publishing/video-worklist-studio-observation.json): 최신 100개 행에서 현재 공개/비공개/예약을 확인했다. 오래된 예약표의 날짜를 현재 예약으로 승계하지 않았다. 목록에서 보이지 않은 과거 ID는 삭제로 단정하지 않는다.','- [게임디자인 순서](../production/batches/sakurai-planning-game-design/playlist-inventory.json), [기존 게임수학 순서](../shared/publishing/daily-alternating-schedule.json), [렌더링 시리즈 계획](../production/research/game-lighting-history/series-plan.json)을 연결했다. 과거 길이 제한·자동 작업 지시는 적용하지 않는다.','- 기존 비공개 영상에는 대사 연결, 쉬운 선행 설명, 정식 용어, 독립 게임 자료, 화면 표식, 자연스러운 TTS·국소 음량, 1080p60·모바일 가독성을 선택 시 검수한다. 최신 규칙 때문에 미선택 완성본을 자동 재제작하지 않는다.','- M21 이후는 기존 승인 상한 밖 후속 후보다. 이번 목록 작성으로 착수하지 않는다.','- 별도 완료 영상 「AI 시대 게임개발과 실력」은 현재 Studio에서 2026-10-16 예약 상태를 확인했다. 기존 설정을 유지한다.','']
(R/'docs/VIDEO_WORKLIST.md').write_text('\n'.join(out),encoding='utf-8')
print('Rendered VIDEO_WORKLIST.md:',len(rows),'rows')
