"""Render the human-readable worklist from the maintained state; never changes media or platforms."""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'shared/publishing/video-worklist.json').read_text(encoding='utf-8'))
rows=d['rows'];byid={x['id']:x for x in rows}
def cell(x):return str(x).replace('|',' / ').replace('\n',' ')
def link(r):return f"[{cell(r['title'])}]({r['url']})" if r.get('url') else cell(r['title'])
def review(r):
 s=cell(r['reviewStatus'])
 return ('☑ ' if s=='사용자 승인 완료' else '— ' if s in ['공개본 유지','중복 판단 유지'] else '☐ ')+s
out=['# 전체 영상 작업 순서와 검수 현황','','2026-10-16 기준. 게임디자인·렌더링 특별편·게임수학의 제작과 상태 갱신은 이 채팅과 `D:/Github/VideoEditing`에서만 진행한다. 다른 제작 채팅 세 개는 대기 상태로 확인했으며 새 작업을 전달하지 않았다.','','지금은 **렌더링 1편 승인본의 YouTube 비공개 업로드 → 게임디자인 「게임 보상 기획」 최신 규칙 점검·수정 → Drive 최종 검수** 순서다. 이후 목록은 작업 순서를 보여 주는 제안이며 자동 일괄 착수나 공개 예약 변경을 뜻하지 않는다.','','**표시:** ☑ 제작 완료 = 기존 완성 영상이 있음. ☐ = 미완성/미착수. 검수 필요는 별도 열로 표시하며, 제작 완료를 최신 규칙 합격이나 사용자 승인으로 해석하지 않는다. 공개 영상은 유지한다. 비공개 기존본은 선택할 때 최신 기준으로 검수해 필요한 부분만 수정한다.','','원본 주제 30개(중복 제외 1개 포함), 렌더링 납품 단위 6편, 게임수학 현 범위 20편·후속 후보 13편을 관리한다. 샘플·수정 버전·분할 전 통합본을 새 영상으로 중복 집계하지 않았다.','','## 앞으로의 통합 작업 순서','','공개일과 별개인 검수·제작 순서다. 시리즈 내부 설명 순서는 유지한다. 렌더링1과 다음 게임디자인1편만 현재 실행 범위이며, 그 이후는 한 편씩 선택한다.','','| 순서 | 분야 | 영상 | 현재 상태 | 검수/다음 작업 |','|---:|---|---|---|---|']
current=byid[d['currentVideo']]
series_names={'D':'게임디자인','R':'특별 렌더링','M':'게임수학','S':'별도 특별편'}
out[4]=f"현재 선택 영상은 **{series_names[current['series']]} 「{current['title']}」: {current['executionStatus']}**. {current['reviewStatus']}. 이전 완성본의 사용자 검수와 플랫폼 상태는 각 행에 보존한다. 이후 목록은 제안 순서이며 자동 일괄 착수나 공개 예약 변경을 뜻하지 않는다."
out[12]='공개일과 별개인 검수·제작 순서다. 현재 실행은 위 선택 영상 한 편이며, 다른 편은 별도 선택 전까지 기존 상태를 유지한다.'
for i,id in enumerate(d['workOrder'],1):
 r=byid[id];out.append(f"| {i} | {series_names[r['series']]} | {id} {link(r)} | {cell(r['executionStatus'])} | {review(r)} |")
for series,title in [('S','별도 특별편'),('D','게임디자인 전체 30개 주제'),('R','특별영상 렌더링 전체 6편'),('M','게임수학 Part2 전체 목록')]:
 out+=['',f'## {title}','','| 번호 | 영상 | 제작 | 검수 상태 | 현재 YouTube 상태 |','|---|---|---|---|---|']
 for r in rows:
  if r['series']!=series:continue
  out.append(f"| {r['id']} | {link(r)} | {'☑' if r['productionComplete'] else '☐'} {cell(r['productionStatus'])} | {review(r)} | {cell(r['platformStatus'])} |")
out+=['','## 복원과 확인이 필요한 항목','','| 영상 | 남은 내용 |','|---|---|']
for r in rows:
 if r['notes']:out.append(f"| {r['id']} {cell(r['title'])} | {cell(r['notes'])} |")
out+=['','## 관리 기준과 근거','','- 기준 파일: [영상별 상태](../shared/publishing/video-worklist.json). 표를 갱신할 때 `python scripts/render-video-worklist.py`를 실행한다. 각 편의 상세 계획·검수 원장은 해당 프로젝트의 기존 파일을 사용한다.','- [실제 Studio 상태 확인](../shared/publishing/video-worklist-studio-observation.json): 최신 100개 행에서 현재 공개/비공개/예약을 확인했다. 오래된 예약표의 날짜를 현재 예약으로 승계하지 않았다. 목록에서 보이지 않은 과거 ID는 삭제로 단정하지 않는다.','- [게임디자인 순서](../production/batches/sakurai-planning-game-design/playlist-inventory.json), [기존 게임수학 순서](../shared/publishing/daily-alternating-schedule.json), [렌더링 시리즈 계획](../production/research/game-lighting-history/series-plan.json)을 연결했다. 과거 길이 제한·자동 작업 지시는 적용하지 않는다.','- 기존 비공개 영상에는 대사 연결, 쉬운 선행 설명, 정식 용어, 독립 게임 자료, 화면 표식, 자연스러운 TTS·국소 음량, 1080p60·모바일 가독성을 선택 시 검수한다. 최신 규칙 때문에 미선택 완성본을 자동 재제작하지 않는다.','- M21 이후는 기존 승인 상한 밖 후속 후보다. 이번 목록 작성으로 착수하지 않는다.','- 별도 완료 영상 「AI 시대 게임개발과 실력」은 현재 Studio에서 2026-10-16 예약 상태를 확인했다. 기존 설정을 유지한다.','']
out=[line.replace('별도 완료 영상 「AI 시대 게임개발과 실력」은 현재 Studio에서 2026-10-16 예약 상태를 확인했다. 기존 설정을 유지한다.','별도 완료 영상 「AI 시대 게임개발과 실력」은 2026-10-18 Studio에서 공개 상태와 게시일2026-10-16을 확인했다. 기존 설정을 유지한다.') for line in out]
polish=d.get('privateMathPolish')
if polish and not polish.get('conceptFitRevision'):
 section=['','## 기존 비공개 게임수학 시각 보강 진행표','',
  '기존 강의를 유지하며 표식·가독성·필요한 애니메이션만 다듬는다. 대본을 다시 쓰거나 새 음성을 만들지 않는다. '+('사용자 야간 요청으로 M05–M20의16편을 순차 보강해 각각 로컬 검수 대기로 모은다. M04는 검수 완료이며 업로드는 이번 범위에 포함되지 않는다.' if polish.get('batchAuthorization') else '현재는 M04 한 편만 착수하며 나머지는 작업 목록이다.'),
  '',f"Studio 확인: 비공개 {polish['privateUploadCount']}개 = 본편 {polish['mainLessonCount']}편 + 이전 버전 {len(polish['olderVersions'])}개. 공개본과 기존 업로드는 보존한다.",
  '']
 polish_rows=[r for r in rows if r.get('privatePolish')]
 approved=[r['id'] for r in polish_rows if r['privatePolish'].get('actualHumanReview',{}).get('status')=='accepted']
 pending=[r['id'] for r in polish_rows if r['id'] not in approved and r['privatePolish'].get('localReview',{}).get('status')=='ready-for-human-local-review']
 unfinished=[r['id'] for r in polish_rows if r['id'] not in approved+pending]
 updated_kst=datetime.datetime.fromisoformat(polish['updatedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M KST')
 section += [f"갱신: {updated_kst}. **사용자 승인 {len(approved)}편 · 완성본 검수 대기 {len(pending)}편 · 전체 완성본 작업 중 {len(unfinished)}편.**",'',
  f"- 사용자 승인: {', '.join(approved) or '없음'}.",
  f"- 내부 QA 완료·사용자 검수 대기: {', '.join(pending) or '없음'}. 각 행의 로컬 검수 링크에서1080p60 clean/captioned 영상과 한영 SRT를 확인한다.",
  f"- 전체 완성본 작업 중: {', '.join(unfinished) or '없음'}. 설명 화면 검수 완료는 전체 게임 화면·최종 영상 검수 완료와 구분한다."]
 decision=polish.get('sourceReplacementDecision')
 if decision:section += [f"- 원본 처리 결정: {decision['summaryKo']}"]
 section += ['', '**검수 구분:** 내부 화면·기술 QA 통과는 사용자 승인과 다르다. 기존 영상 열은 보존 중인 YouTube 원본이며, 수정본은 로컬 링크로 검수한다.','', '| 순서 | 기존 영상 | 길이 | 보강 작업 | 진행 | 사용자 검수·로컬 링크 |', '|---:|---|---:|---|---|---|']
 for r in rows:
  p=r.get('privatePolish')
  if not p:continue
  local=p.get('localReview',{});review_text=cell(p['humanReview'])
  if local.get('status')=='ready-for-human-local-review':review_text+=f" · [검수 파일](../{local['index']}) · [전체 자막 영상](../{local['captionedVideo']})"
  section.append(f"| {p['order']} | {r['id']} [{cell(p['baselineTitle'])}](https://youtu.be/{p['baselineVideoId']}) | {p['duration']} | {cell(p['task'])} | {cell(p['status'])} | {review_text} |")
 section+=['','이전 버전은 추가 제작 편수에서 제외하고 그대로 보존한다:']
 for r in polish['olderVersions']:
  section.append(f"- [{cell(r['title'])}](https://youtu.be/{r['videoId']}) · {r['duration']} · {r['status']}")
 section+=['',f"근거: [{polish['updatedAt'][:10]} Studio 실제 목록](../{polish['evidence']}). 원본 코드 재렌더 허가를 기록했으며 최신 로컬 V8을 비공개 업로드 원본으로 대체하지 않는다.",'']
 out+=section
 (R/'docs/GAME_MATH_PRIVATE_POLISH.md').write_text('# 기존 비공개 게임수학 시각 보강\n'+ '\n'.join(section[3:]),encoding='utf-8')
revision=(polish or {}).get('conceptFitRevision')
if revision:
 section=['','## 이번 게임수학 게임 장면 적합성 수정 (18편)','',
  f"갱신: {revision['updatedAt']}. **화면·기술검사 완료 / 사용자 시청·청취 대기 {revision['readyCount']}/18편.** 원래 수학 설명과 순서는 유지하고, 실제 장면과 맞지 않는 게임 설명 문단만 수정했다.",'',
  '이 표는 기존 보강본 이후의 concept-fit-v2 수정 상태다. 처음 목록에서 빠졌던15:03 방향과 회전 행렬 원본도 M03-original로 포함했다. 기존 파일·업로드는 보존하며 이번 완성본은 모두 로컬 검수용이다.','',
  '| 번호 | 강의 | 새 수정본 | 사용자 검수 |','|---|---|---|---|']
 for e in revision['entries']:
  local=e.get('outputFolder');status='화면·기술검사 완료 · 청취 대기' if e['status']=='local-review-ready-with-listening-notes' else cell(e['status'])
  links=f"[폴더](../{local}/index.html) · [전체 영상](../{local}/{e['slug']}.captioned.mp4)" if local else '제작 중'
  section.append(f"| {e['id']} | {cell(e['title'])} | {status} · {links} | 대기 |")
 section+=['','[장면 검수와 상세 진행표](GAME_MATH_PRIVATE_POLISH.md) · [전체 로컬 검수 페이지](../output/private-game-math-polish/index.html)','',
  '각 완성본은1920×1080/60fps clean·captioned 영상과 KO/EN SRT로 제공한다. 실제 전체 청취와 사용자 승인은 별도이며, 업로드·삭제·예약·다음 영상 착수는 하지 않는다.','']
 out+=section
gameplay=(polish or {}).get('gameplayTimingRevision')
if gameplay:
 latest=['','## 최신 게임수학 게임 장면·표식 수정','',
  f"**{gameplay['status']}** · 사용자 검수 대기. 기존 설명·음성·길이를 보존한 별도 수정본이다.",'',
  '| 번호 | 강의 | 현재 상태 | 로컬 검수 |','|---|---|---|---|']
 for e in gameplay['entries']:
  local=e.get('newOutput');target=f"[영상과 자막](../{local}/index.html)" if local else '제작 중'
  latest.append(f"| {e['id']} | {cell(e['title'])} | {cell(e['status'])} | {target} |")
 latest+=['','[최신 검수표](../output/private-math-gameplay-20261024/index.html) · 전체 최종 청취와 사용자 승인은 별도다. 아래 이전 버전의 완료 상태와 구분한다.','','---','']
 out=out[:1]+latest+out[1:]
(R/'docs/VIDEO_WORKLIST.md').write_text('\n'.join(out),encoding='utf-8')
print('Rendered VIDEO_WORKLIST.md:',len(rows),'rows')
