"""Register the user's whole-series footage revision without changing old masters."""
from pathlib import Path
import collections, datetime, hashlib, html, json
R=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
key='private-math-concept-fit-20261023'
old=read(R/'production/batches/private-game-math-polish-20261022/queue.json')['entries']
entries=[dict(id='M03-original',slug='game-math-orientation-matrices',title='3D 회전 ① 방향과 회전 행렬',baselineVideoId='6-kP65hrZcI'),dict(id='M04',slug='game-math-euler-axis-angle',title='3D 회전 ② 오일러 각과 축·각',baselineVideoId='iv9esV7vv_g')]+[{k:e[k] for k in ['id','slug','title']} for e in old]
authorization=dict(id=key,recordedAt=now,status='active',userEvidence='영상전부 내가 얘기한거 검수하고 반영해서 렌더링해줘',scope='Original private orientation/matrix 15:03 plus M04–M20: inspect every adopted game interval against narration, replace weak/repeated examples, render local review masters.',ids=[e['id'] for e in entries],slugs=[e['slug'] for e in entries],fullProductionAuthorized=True,renderAuthorized=True,limitedNarrationRepairAuthorized=True,newTtsScope='Only complete paragraphs whose game-specific wording must change after a verified replacement. Preserve unchanged math narration and teaching order; no full-lesson rewrite or speed fitting.',uploadAuthorized=False,deleteAuthorized=False,scheduleAuthorized=False,automaticAdvanceWithinThisList=True,advanceBeyondThisList=False,heartbeatEnabled=False,stopAt='18 locally delivered internally checked revisions, then user review')
save(B/'authorization.json',authorization)
scenes=[]; occurrences=collections.defaultdict(list)
for e in entries:
 p=R/'projects'/e['slug']; tpath=p/'production/timeline.json'; t=read(tpath)
 e.update(timeline=tpath.relative_to(R).as_posix(),timelineSha256=digest(tpath),frames=t['frames'],seconds=t['seconds'],status='scene-fit-audit-pending',humanReview='pending-for-new-revision')
 for s in t['scenes']:
  if s.get('classification')!='actual':continue
  cut=s.get('cut',{});parts=[]
  for seg in cut.get('segments',[cut]):
   source=seg.get('sourceFile',cut.get('sourceFile')); start=seg.get('in',0); frames=seg.get('frames',s['frames'])
   parts.append(dict(source=source,sourceId=seg.get('sourceId',cut.get('sourceId')),sourceIn=start,seconds=frames/60,exists=bool(source and (R/source).exists())))
   if source:occurrences[source].append(dict(episode=e['id'],scene=s['id'],start=start,end=start+frames/60))
  cues=s.get('cues') or s.get('sentenceCues') or s.get('captions',{}).get('ko',[])
  row=dict(episode=e['id'],slug=e['slug'],scene=s['id'],title=s.get('title',''),start=s.get('start'),frames=s['frames'],seconds=s.get('seconds',s['frames']/60),narration=[dict(start=c.get('start'),end=c.get('end'),text=c.get('text','')) for c in cues],parts=parts,claimedFocus=cut.get('focus'),claimedAction=cut.get('action'),claimedLesson=cut.get('claim'),decision='pending-direct-scene-fit-review',actualPixelReview='pending',replacement=None)
  scenes.append(row)
reuse=[]
for source,uses in occurrences.items():
 overlap=[]
 for i,a in enumerate(uses):
  for b in uses[i+1:]:
   seconds=min(a['end'],b['end'])-max(a['start'],b['start'])
   if seconds>1:overlap.append(dict(a=a['episode']+'/'+a['scene'],b=b['episode']+'/'+b['scene'],seconds=round(seconds,2)))
 reuse.append(dict(source=source,uses=len(uses),episodes=sorted(set(a['episode'] for a in uses)),overlaps=overlap))
save(B/'scene-audit.json',dict(updatedAt=now,authorization=key,entries=entries,scenes=scenes,sourceReuse=sorted(reuse,key=lambda a:-a['uses']),decisions=[],note='An inventory or old technical QA is not new footage suitability approval.'))
save(B/'checkpoint.json',dict(updatedAt=now,status='whole-series-source-and-narration-audit',entries=entries,active=[],ready=[],blocked=[],nextAction='Inspect actual source intervals and record retain/replace reasons; recover original orientation lecture audio; select verified stationary manipulation examples before changed narration/TTS/render.'))
cpath=R/'shared/publishing/video-production-control.json'; c=read(cpath);c.setdefault('scopedBatchAuthorizations',{})[key]=authorization;c['updatedAt']=now;save(cpath,c)
wpath=R/'shared/publishing/video-worklist.json';w=read(wpath);w['updatedAt']=now
w['privateMathPolish']['conceptFitRevision']=dict(authorization=key,checkpoint=(B/'checkpoint.json').relative_to(R).as_posix(),status='all-18-under-revision',entries=entries,previousOutputsPreserved=True,previousHumanApprovalDoesNotApproveThisRevision=True)
w['privateMathPolish']['automaticNextVideo']=False
for r in w['rows']:
 if r['id'] in authorization['ids'] and 'privatePolish' in r:r['privatePolish']['conceptFitRevision']=dict(status='게임 장면 적합성 재검수·교체 예정',humanReview='새 수정본 검수 대기 전',checkpoint=(B/'checkpoint.json').relative_to(R).as_posix())
save(wpath,w)
out=R/'output/private-game-math-polish';out.mkdir(exist_ok=True)
table=[]
for e in entries:
 count=sum(s['episode']==e['id'] for s in scenes);oldlink='../'+e['slug']+'-private-polish/index.html'
 link=f'<a href="{oldlink}">이전 보강본</a>' if (R/'output'/(e['slug']+'-private-polish')/'index.html').exists() else '15:03 기존 비공개본 복원·포함'
 table.append(f'<tr><td>{e["id"]}</td><td>{html.escape(e["title"])}</td><td>{count}</td><td>장면 적합성 재검수 중</td><td>{link}</td></tr>')
(out/'index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>게임수학 전체 장면 재검수</title><style>body{font:17px/1.65 system-ui;background:#101512;color:#f2f5f2;max-width:1250px;margin:32px auto;padding:0 20px}h1{color:#ffdf73}a{color:#8cdbbc}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px;border-bottom:1px solid #405147}.scroll{overflow:auto}p{max-width:950px}</style><h1>게임수학 · 설명에 맞는 게임 장면으로 재검수</h1><p>2026-10-23 사용자 피드백 반영: 누락됐던 15분 3초 방향·회전 행렬 강의를 포함한 18편. 아래 링크는 이전 보강본이며, 이번 수정본 완료를 뜻하지 않습니다.</p><p>회전은 물체를 제자리에서 돌리고 배치하는 조작을 우선합니다. 모든 장면에서 대사·대상·조작·결과의 일치와 반복 사용을 확인한 뒤 교체합니다. 수학 설명 순서는 유지하며 필요한 게임 지칭 문장만 수정합니다.</p><div class="scroll"><table><thead><tr><th>번호</th><th>강의</th><th>게임 구간 수</th><th>이번 상태</th><th>이전 버전</th></tr></thead><tbody>'''+''.join(table)+'</tbody></table></div></html>',encoding='utf8')
md=['# 기존 비공개 게임수학 · 게임 장면 적합성 재검수','',f'갱신: {now[:16]} KST. 이번 수정 대상 **18편**, 새 수정본 완료 **0편**. 기존 보강본·업로드는 보존한다.','',"누락됐던 15:03 ‘방향과 회전 행렬’ 원본(`6-kP65hrZcI`)을 독립 항목 M03-original로 포함한다. 공개된 후속본이나 별도25분 V8과 합치지 않는다.",'','| 번호 | 강의 | 실제 게임 구간 | 이번 상태 |','|---|---|---:|---|']
md += [f'| {e["id"]} | {e["title"]} | {sum(s["episode"]==e["id"] for s in scenes)} | 장면 적합성 재검수 중 |' for e in entries]
md += ['','[검수 페이지](../output/private-game-math-polish/index.html)','',f'근거: `{(B/"scene-audit.json").relative_to(R).as_posix()}`. 기존 내부 QA 완료는 이번 적합성 승인으로 사용하지 않는다.']
(R/'docs/GAME_MATH_PRIVATE_POLISH.md').write_text('\n'.join(md)+'\n',encoding='utf8')
print(json.dumps(dict(episodes=len(entries),actualScenes=len(scenes),sourceFiles=len(reuse),topReuse=[{k:v for k,v in x.items() if k!='overlaps'}|{'overlaps':len(x['overlaps'])} for x in sorted(reuse,key=lambda a:-a['uses'])[:12]]),ensure_ascii=False,indent=2))
