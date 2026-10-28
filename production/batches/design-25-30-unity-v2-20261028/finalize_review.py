"""Assemble the six verified visual revisions without altering a platform."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, html, json, os, subprocess, uuid

R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
MEDIA=Path('C:/Users/1/.codex/video-production')/B.name
OUT=R/'output/game-design-25-30-unity-v2-20261028'
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
IDS=['D'+str(i) for i in range(25,31)]
IMPROVEMENTS=[
 '색·밝기·무늬·모양을 바꾼 오브젝트와 배경 대비 비교',
 '캐릭터의 접근·공격·반응 지연·조건 우선순위 시연',
 '연출과 조작, 프레임률, QTE와 건너뛰기 상황 시연',
 '위기·첫 행동·보상을 실제 캐릭터와 소품으로 연결',
 '운전 보조, 행동 선택과 회복을 움직이는 장면으로 설명',
 '생활 속 선택·대기·메뉴·플레이 시간의 비용을 시각화'
]

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 t.write_text(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
def esc(x):return html.escape(str(x))
def cell(x):return str(x).replace('|',' / ').replace('\n',' ')

def main():
 auth=read(B/'authorization.json');assert auth['slugs']==SLUGS
 cp=R/'shared/publishing/video-production-control.json';control_hash=sha(cp);control=read(cp)
 assert control['finiteBatchAuthorizations'][B.name]['localProductionAuthorized']
 rows=[];now=datetime.now(timezone.utc).isoformat()
 for n,(episode,slug) in enumerate(zip(IDS,SLUGS)):
  project=R/'projects'/slug;review=project/'production/unity-visual-v2/review-status.json'
  q=read(review);m=read(project/'project.json');receipt=read(project/'production/delivery-output.json')
  assert q['status']=='local-review-ready' and q['fourOutputsVerified'] is True,(slug,'review not complete')
  directory=R/receipt['directory'];assert directory.resolve().is_relative_to(MEDIA/slug)
  assert directory==R/m['delivery']['localStorageRoot']/'output'/slug
  paths={};hashes={}
  for kind in ['captioned.mp4','clean.mp4','ko.srt','en.srt']:
   p=directory/(slug+'.'+kind);record=next(x for x in receipt['files'] if x['name']==p.name)
   digest=sha(p);assert digest==record['sha256'] and p.stat().st_size==record['bytes']
   paths[kind]=p.relative_to(R).as_posix();hashes[kind]=digest
  assert hashes['captioned.mp4']==q['captionedSha256']
  assert (directory/'index.html').is_file()
  old=next(x for x in auth['baseline'] if x['slug']==slug)
  for f in old['files'].values():assert sha(R/f['path'])==f['sha256'],'Baseline changed: '+f['path']
  assert hashes['ko.srt']==old['files']['captionsKo']['sha256'] and hashes['en.srt']==old['files']['captionsEn']['sha256']
  scenes=q['savedScenePaths'];assert len(scenes)==q['nativeReplacedCutCount']
  for s in scenes:
   p=R/s if s.startswith('unity/') else R/'unity/VideoEditing'/s
   assert p.is_file() and p.stat().st_size<5_000_000,'Missing scene or embedded media: '+s
  focus=q.get('reviewFocus','설명의 행동과 결과가 눈에 들어오는지')
  if isinstance(focus,list):focus=' / '.join(focus)
  rows.append(dict(id=episode,slug=slug,title=m.get('titles',{}).get('ko',slug),seconds=q['durationSeconds'],improvement=IMPROVEMENTS[n],paths=paths,hashes=hashes,index=(directory/'index.html').relative_to(R).as_posix(),reviewRecord=review.relative_to(R).as_posix(),nativeCuts=q['nativeReplacedCutCount'],reviewFocus=focus,q=q))
 assert sum(x['nativeCuts'] for x in rows)==91
 MEDIA.joinpath('review').mkdir(parents=True,exist_ok=True)
 if not OUT.exists():
  OUT.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run(['powershell','-NoProfile','-Command',"New-Item -ItemType Junction -Path '"+str(OUT)+"' -Target '"+str(MEDIA/'review')+"' | Out-Null"],check=True)
 assert OUT.resolve()==(MEDIA/'review').resolve()
 html_rows=[];md=[]
 for x in rows:
  total=int(x['seconds']+.5);duration=f'{total//60}:{total%60:02d}'
  index='../../'+x['index'];video='../../'+x['paths']['captioned.mp4']
  html_rows.append(f'<tr><td>{x["id"]}</td><td>{esc(x["title"])}<small>{esc(x["improvement"])}</small></td><td>{duration}</td><td>☑ 완성<small>1080p60 · Unity {x["nativeCuts"]}컷<br>기존 음성·음악·자막 보존<br>화면·자막·모바일·전체 파일 검사</small></td><td>☐ 사용자 검수<small>{esc(x["reviewFocus"])}</small></td><td><a href="{video}">전체 영상</a><br><a href="{index}">영상·한영 자막</a></td></tr>')
  md.append(f'| {x["id"]} | {cell(x["title"])} | {duration} | {cell(x["improvement"])} | ☑ 내부 검사 완료 | ☐ 사용자 검수 | [영상]({(R/x["paths"]["captioned.mp4"]).as_posix()}) |')
  # Each project page links back to this revised batch, leaving old deliveries intact.
  import re
  p=R/x['index'];content=p.read_text('utf-8-sig');link=os.path.relpath(OUT/'index.html',p.parent).replace('\\','/')
  updated,count=re.subn(r'<a href="[^"]*">전체 목록</a>',f'<a href="{link}">전체 검수표</a>',content)
  if count:save(p,updated)
 title='게임디자인 25–30 · Unity 설명 보완본'
 page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
 <style>body{{margin:32px auto;padding:0 20px;max-width:1550px;background:#111;color:#f5f5f5;font:16px/1.7 'Malgun Gothic',sans-serif}}h1,th{{color:#e8cf83}}a{{color:#8ce0ce}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse}}th,td{{padding:14px 12px;text-align:left;vertical-align:top;border-bottom:1px solid #444}}td:nth-child(2){{min-width:240px}}td:nth-child(4),td:nth-child(5){{min-width:160px}}td:last-child{{min-width:140px}}small{{display:block;color:#bbb;font-size:14px}}@media(max-width:600px){{body{{padding:0 12px}}table{{min-width:1000px}}}}</style>
 <h1>{title}</h1><p>6편 완성 · Unity 설명 91컷 · 1920×1080 / 60fps</p><p>이야기·순서·목소리·배경음악·게임 장면·한영 자막은 유지했습니다. 이전 검수본도 그대로 보관했습니다.</p><div class="scroll"><table><thead><tr><th>번호</th><th>주제와 보완 내용</th><th>길이</th><th>제작·내부 검사</th><th>사용자 검수</th><th>파일</th></tr></thead><tbody>{''.join(html_rows)}</tbody></table></div><p><small>내부 검사는 실제 사용자 전체 시청·청취와 구분합니다. 새 버전의 사용자 검수는 대기 중이며, 업로드·예약은 변경하지 않았습니다.<br>갱신 {now}</small></p></html>'''
 save(OUT/'index.html',page)
 save(B/'REVIEW.md',f'# {title}\n\n6편 완성. 기존 이야기·음성·음악·게임 구간·자막 유지. 새 버전 사용자 검수 대기.\n\n| 번호 | 제목 | 길이 | 설명 보완 | 내부 검사 | 사용자 검수 | 파일 |\n|---|---|---|---|---|---|---|\n'+'\n'.join(md)+'\n')
 workpath=R/'shared/publishing/video-worklist.json';work_hash=sha(workpath);work=read(workpath)
 doc=R/'docs/VIDEO_WORKLIST.md';doc_hash=sha(doc);lines=doc.read_text('utf-8-sig').splitlines(keepends=True)
 for x in rows:
  row=next(r for r in work['rows'] if r['id']==x['id'])
  oldreview=row.get('localReview')
  if oldreview and oldreview.get('captionedSha256')!=x['hashes']['captioned.mp4']:
   history=row.setdefault('localReviewHistory',[])
   if not any(h.get('captionedSha256')==oldreview.get('captionedSha256') for h in history):history.append(oldreview)
  row.update(productionComplete=True,productionStatus='Unity 설명 보완 · 1080p60 완성',reviewStatus='새 완성본 사용자 검수 대기',humanApproval='pending',executionStatus='D25–D30 Unity 설명 보완 완료 · 검수 대기',localMasterAvailable=True,activeRevision='unity-visual-v2',selectedBatch=B.name,internalQaStatus='complete; actual human viewing/listening pending')
  row['localReview']=dict(status='ready-for-human-local-review',index=x['index'],captionedVideo=x['paths']['captioned.mp4'],cleanVideo=x['paths']['clean.mp4'],captionsKo=x['paths']['ko.srt'],captionsEn=x['paths']['en.srt'],captionedSha256=x['hashes']['captioned.mp4'],durationSeconds=x['seconds'],actualUserViewed=False,humanWholeListening='pending',updatedAt=now)
  row.setdefault('evidence',[])
  if x['reviewRecord'] not in row['evidence']:row['evidence'].append(x['reviewRecord'])
  note='이전 이야기/순서 호평을 반영해 설명만 Unity로 보완. 기존 완성본 보존. 새 파일 사용자 전체 검수 대기; 플랫폼 변경 없음.'
  if note not in row.get('notes',''):row['notes']=(row.get('notes','').rstrip()+' '+note).strip()
 # Detect concurrent control changes before persisting this one owned batch state.
 assert sha(cp)==control_hash,'Control changed concurrently; rerun'
 assert sha(workpath)==work_hash,'Worklist changed concurrently; rerun'
 assert sha(doc)==doc_hash,'Rendered worklist changed concurrently; rerun'
 control['finiteBatchAuthorizations'][B.name].update(status='six-local-reviews-ready',completed=6,total=6,localReviewIndex=(OUT/'index.html').relative_to(R).as_posix(),updatedAt=now)
 save(cp,control);save(workpath,work)
 checkpoint=dict(status='six-local-reviews-ready',completed=6,total=6,updatedAt=now,explanationCuts=91,preservedUsefulExplanationCuts=4,baselineFilesPreserved=24,newTts=False,platformMutation=False,userReview='pending',localReviewIndex=(OUT/'index.html').relative_to(R).as_posix(),episodes=[{k:v for k,v in x.items() if k!='q'} for x in rows])
 previous_checkpoint=read(B/'checkpoint.json')
 for key in ['userGamingConstraint','resumeUserEvidence','resumedAt']:
  if key in previous_checkpoint:checkpoint[key]=previous_checkpoint[key]
 save(B/'checkpoint.json',checkpoint)
 owned={r['id']:r for r in work['rows'] if r['id'] in IDS}
 for i,line in enumerate(lines):
  for episode,r in owned.items():
   if line.startswith('| '+episode+' |'):lines[i]=f'| {episode} | {cell(r["title"])} | ☑ {cell(r["productionStatus"])} | ☐ {cell(r["reviewStatus"])} | {cell(r["platformStatus"])} |\n'
   elif '| 게임디자인 | '+episode+' ' in line:lines[i]=f'| {line.split("|")[1].strip()} | 게임디자인 | {episode} {cell(r["title"])} | {cell(r["executionStatus"])} | ☐ {cell(r["reviewStatus"])} |\n'
   elif line.startswith('| '+episode+' '):lines[i]=f'| {episode} {cell(r["title"])} | {cell(r["notes"])} |\n'
 assert sha(doc)==doc_hash,'Rendered worklist changed concurrently; rerun'
 save(doc,''.join(lines))
 print(json.dumps(dict(status=checkpoint['status'],review=str(OUT/'index.html'),baselineFilesPreserved=24),ensure_ascii=False))

if __name__=='__main__':main()
