"""One local review collection, exact per-episode delivery links and script mapping."""
from common import *
import html,shutil
from urllib.parse import quote

STYLE='''body{margin:0;background:#080c0a;color:#f3f5ef;font:16px/1.6 system-ui,sans-serif}main{max-width:1260px;margin:auto;padding:24px}h1{color:#f2d787;font-size:29px;margin:0}h2{font-size:23px;margin:20px 0 10px}p{color:#abb9af}a{color:#81cfc5}button,select{font:inherit;color:inherit;background:#17231c;border:1px solid #425247;border-radius:4px;padding:9px 13px;cursor:pointer}button.active{border-color:#81cfc5;color:#81cfc5}nav{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}video{width:100%;aspect-ratio:16/9;background:#000}section{border-top:1px solid #425247;padding-top:14px;margin-top:18px}.links{display:flex;gap:18px;flex-wrap:wrap}.hint{color:#a4d987}small{color:#abb9af}.controls{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}.study{padding:8px 0;border-bottom:1px solid #23352a}.study b{color:#f2d787}table{border-collapse:collapse;width:100%}td,th{padding:10px;text-align:left;border-bottom:1px solid #425247}details{margin-top:16px}summary{cursor:pointer;color:#81cfc5}@media(max-width:500px){main{padding:12px}h1{font-size:23px}h2{font-size:19px}button{padding:7px 10px}.links{gap:12px}td,th{padding:8px 5px}}'''

def main():
 from studies import catalog
 provenance=catalog()
 plan=read(HERE/'plan.json');rows=[];ledger=[]
 for e in plan['episodes']:
  ep=e['id'];d=read(OUTPUT/ep/'delivery.json');assert not d.get('visualReviewPending',True),(ep,'encoded review incomplete');files={f['kind']:f for f in d['files']};folder=OUTPUT/ep
  assert not e.get('queuedVisualEnhancement') or e['queuedVisualEnhancement']['stage']=='internally-reviewed',(ep,'scoped correction is not accepted yet')
  assert all(Path(f['path']).exists() and sha(f['path'])==f['sha256'] for f in d['files'])
  kinds=['clean.mp4','captioned.mp4','ko.srt','en.srt'];assert set(kinds)<=set(files)
  if ep=='A06':
   baseline={f['kind']:f for f in read(e['baselineReceipt'])['files']}
   assert all(files[k]['sha256']==baseline[k]['sha256'] for k in kinds),'A06 must remain byte-identical'
  else:
   assert d['openingAndRecapSpeechPreserved'] and d['summaryFrames']==600 and d['cleanCaptionedIdenticalAac']
   ko,en=(srt(files[k]['path']) for k in ['ko.srt','en.srt'])
   assert len(ko)==len(en) and all(a['start']==b['start'] and a['end']==b['end'] for a,b in zip(ko,en))
   assert all(0<=c['start']<c['end']<=d['durationSeconds']+.01 for c in ko)
  links={k:ep+'/'+quote(Path(files[k]['path']).name) for k in kinds}
  studies=[dict(key=k,game=s['game'],purpose=s['focus'],grammar=s['grammar'],url=s.get('sourceUrl'),dataUrl=s.get('primaryDataUrl')) for k,s in e.get('studyDefinitions',{}).items()]
  if ep=='A08':
   source=provenance['maelle-no-commentary']
   studies.append(dict(key='clothing-context',game=source['game'],purpose='마엘의 복장·외투와 자세의 관계',grammar='pose',url=source['sourceUrl'],dataUrl=None))
  body_starts=[s['start'] for s in e.get('replacementSpans',[]) if s['start']>=e['opening']['endFrame']]
  first_study=min(body_starts) if body_starts else e['opening']['endFrame']
  rows.append(dict(id=ep,title=e['title'],duration=d['durationSeconds'],overview=d.get('overviewAt',2),recap=d['summaryAt'],
   preserved=ep=='A06',links=links,studies=studies,firstStudy=map_frame(first_study,d.get('audioChanges',[]))/60,
   changedSpeech=len(d.get('audioChanges',[]))))
  body=srt(files['ko.srt']['path']);narration='\n\n'.join(c['text'].replace('\n',' ') for c in body)
  (folder/'narration.txt').write_text(narration+'\n',encoding='utf-8')
  source_lines=['추가 분석 장면 출처','기존 완성본의 독립 게임 영상 출처는 그대로 유지합니다. 게시 시 기존 출처와 아래 추가 출처를 설명란 맨 아래에 병합합니다.','']
  seen=set()
  for s in studies:
   if s['url'] in seen:continue
   seen.add(s['url']);source_lines+=[s['game'],str(s['url']),s['purpose'],'']
   source=next((r for r in provenance.values() if r.get('sourceUrl')==s['url']),{})
   credit=source.get('rights')
   if isinstance(credit,dict):source_lines+=['촬영자: '+credit.get('publisher','미기록'),'이용 조건: '+credit.get('license','기존 출처 기록 유지'),'편집: 발췌·확대·속도 및 자세 시간 배분 비교·설명 표식 추가','']
   if s.get('dataUrl'):source_lines+=['기술 데이터',s['dataUrl'],'']
  (folder/'additional-sources.txt').write_text('\n'.join(source_lines),encoding='utf-8')
  one=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(e['title'])}</title><style>{STYLE}</style><main><a href="../">전체 검수 목록</a><h1>{html.escape(e['title'])}</h1><p>{'A06은 기존 파일과 SHA256이 같습니다.' if ep=='A06' else '실제 게임 장면과 원리 도식 수정본 · 개론과 마지막 정리 유지'}</p><video controls playsinline preload="metadata" src="{quote(Path(files['captioned.mp4']['path']).name)}"></video><nav><a href="{quote(Path(files['clean.mp4']['path']).name)}">클린 영상</a><a href="{quote(Path(files['ko.srt']['path']).name)}">한국어 자막</a><a href="{quote(Path(files['en.srt']['path']).name)}">English SRT</a><a href="narration.txt">전체 대본</a></nav></main></html>'''
  (folder/'index.html').write_text(one,encoding='utf-8')
  ledger.append(dict(id=ep,title=e['title'],preservedExactly=ep=='A06',files=d['files'],humanReviewed=False,platformChanged=False,
   audioEvidence=str(WORK/ep/'audio.json') if ep!='A06' else 'A06 exact-file preservation',sourceReferenceMap=e['sourceReferenceMap']))
 data=json.dumps(rows,ensure_ascii=False).replace('</','<\\/')
 page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>애니메이션 통합 검수 · 실제 게임 분석 수정본</title><style>'''+STYLE+'''</style><main><h1>애니메이션 통합 검수</h1><p>15편 수정 + A06 그대로 유지 · A01·A02 제외 · 1080p 60fps</p><nav id="episodes"></nav><h2 id="title"></h2><p id="note"></p><video id="movie" controls playsinline preload="metadata"></video><div class="controls"><button id="overview">개론</button><button id="study">첫 분석 장면</button><button id="recap">마지막 정리</button><button id="next">다음 편</button><label><input id="continuous" type="checkbox" checked> 연속 재생</label><label>속도 <select id="speed"><option value="0.5">0.5배</option><option value="1" selected>1.0배</option><option value="1.25">1.25배</option></select></label></div><section><div class="links" id="links"></div><small>수정할 부분은 편 번호와 재생 시각으로 알려 주세요. YouTube·Drive 상태는 변경하지 않았습니다.</small></section><section><h2>이번 편에서 바꾼 화면</h2><div id="studies"></div></section><details><summary>전체 제작·검수표</summary><table><thead><tr><th>편</th><th>주제</th><th>상태</th></tr></thead><tbody id="table"></tbody></table></details></main><script>const rows='''+data+''';let selected=0;const el=id=>document.getElementById(id);function choose(i){selected=i;const r=rows[i];el('title').textContent=r.id+' '+r.title;el('note').textContent=r.preserved?'A06: 기존 4파일 그대로 보존':'개론·마지막 정리 유지 · 화면 대응 대사 '+r.changedSpeech+'곳 수정';el('movie').src=r.links['captioned.mp4'];el('movie').playbackRate=Number(el('speed').value);el('links').replaceChildren();for(const [label,url] of [['자막 영상',r.links['captioned.mp4']],['클린 영상',r.links['clean.mp4']],['한국어 SRT',r.links['ko.srt']],['English SRT',r.links['en.srt']],['전체 대본',r.id+'/narration.txt']]){const a=document.createElement('a');a.textContent=label;a.href=url;el('links').append(a)}el('studies').replaceChildren();for(const s of r.studies){const p=document.createElement('div');p.className='study';const b=document.createElement('b');b.textContent=s.game+' · ';p.append(b,document.createTextNode(s.purpose));el('studies').append(p)}if(r.preserved)el('studies').textContent='요청대로 변경하지 않았습니다.';document.querySelectorAll('#episodes button').forEach((b,j)=>b.classList.toggle('active',i===j));location.hash=r.id}rows.forEach((r,i)=>{const b=document.createElement('button');b.textContent=r.id+(r.preserved?' 유지':'');b.onclick=()=>choose(i);el('episodes').append(b);const tr=document.createElement('tr');for(const t of [r.id,r.title.split('|')[0],r.preserved?'그대로 유지':'수정본 · 사용자 검수 대기']){const td=document.createElement('td');td.textContent=t;tr.append(td)}el('table').append(tr)});for(const [id,key] of [['overview','overview'],['study','firstStudy'],['recap','recap']])el(id).onclick=()=>{el('movie').currentTime=rows[selected][key];el('movie').play()};el('next').onclick=()=>choose(Math.min(rows.length-1,selected+1));el('speed').onchange=()=>el('movie').playbackRate=Number(el('speed').value);el('movie').onended=()=>{if(el('continuous').checked&&selected<rows.length-1){choose(selected+1);el('movie').play()}};choose(Math.max(0,rows.findIndex(r=>'#'+r.id===location.hash)));</script></html>'''
 # A fast episode/seek click must wait for that source's metadata, and a queued
 # ended event from the previous source must never advance the new selection.
 replacements={
  'let selected=0;':'let selected=0,loadVersion=0;',
  'function choose(i){selected=i;':"function choose(i){el('movie').pause();loadVersion++;selected=i;",
  "el(id).onclick=()=>{el('movie').currentTime=rows[selected][key];el('movie').play()}":"el(id).onclick=()=>{const version=loadVersion,time=rows[selected][key],movie=el('movie');const seek=()=>{if(version!==loadVersion)return;movie.currentTime=time;movie.play().catch(()=>{})};if(movie.readyState>=1)seek();else movie.addEventListener('loadedmetadata',seek,{once:true})}",
  "if(el('continuous').checked&&selected<rows.length-1)":"if(el('movie').ended&&el('continuous').checked&&selected<rows.length-1)"
 }
 for old,new in replacements.items():
  assert old in page,old
  page=page.replace(old,new)
 (OUTPUT/'index.html').write_text(page,encoding='utf-8')
 save(HERE/'delivery-review-manifest.json',dict(revision='gameplay-v8',reviewUrl='http://127.0.0.1:9302/',outputFolder=str(OUTPUT),episodes=ledger,
  boundary='Local user review pending. No platform mutations. A06 exact preservation; A01/A02 excluded.',updatedAt=stamp()))
 server=(BATCH/'overview-v7/serve.cjs').read_text(encoding='utf-8').replace('animation-overview-v7','animation-gameplay-v8').replace('const port = 9301','const port = 9302')
 server=server.replace('/\\.(html|mp4|srt)$/','/\\.(html|mp4|srt|txt)$/')
 server=server.replace("file.endsWith('.srt') ?", "file.endsWith('.txt') ? 'text/plain; charset=utf-8' : file.endsWith('.srt') ?")
 server=server.replace("fs.createReadStream(file, {start, end}).on('error', () => response.destroy()).pipe(response);","const stream = fs.createReadStream(file, {start, end}).on('error', () => response.destroy());\n  response.on('close', () => stream.destroy());\n  stream.pipe(response);")
 (HERE/'serve.cjs').write_text(server,encoding='utf-8')
 print('Integrated review collection ready:',OUTPUT)

if __name__=='__main__':main()
