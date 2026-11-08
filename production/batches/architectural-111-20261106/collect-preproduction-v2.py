"""Collect the exact111 written preparations, preserving all existing production inputs."""
from __future__ import annotations
import argparse,hashlib,html,json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
BASELINE=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/preproduction-first-20261108/baseline.json')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def validate(packet,row,contract):
 issues=[]
 def need(ok,why):
  if not ok:issues.append(why)
 for k in contract['requiredFields']:need(k in packet,'missing:'+k)
 need(packet.get('schemaVersion')=='architectural111-preproduction-v2','schema')
 need(packet.get('topicId')==row['topicId'],'topicId')
 need(packet.get('batchOrder')==row['order'],'batchOrder')
 ko,en=packet.get('narrationKo',[]),packet.get('paragraphsEn',[])
 need(isinstance(ko,list) and len(ko)>0 and all(isinstance(s,str) and s.strip() for s in ko),'nonemptyKO')
 need(isinstance(en,list) and len(en)==len(ko) and all(isinstance(s,str) and s.strip() for s in en),'alignedEN')
 maps=packet.get('sourceMapping',[]);beats=packet.get('sceneBeats',[])
 for k in ['glossary','gameCandidates','claimLimits']:need(isinstance(packet.get(k),list),'listField:'+k)
 for g in packet.get('glossary',[]):
  need(isinstance(g,dict) and all(g.get(k) not in (None,'') for k in ['english','korean','plainMeaningKo']),'glossaryDefinition')
 need(isinstance(maps,list) and {x.get('paragraph') for x in maps if isinstance(x,dict)}==set(range(1,len(ko)+1)),'sourceParagraphCoverage')
 need(isinstance(beats,list) and {x.get('paragraph') for x in beats if isinstance(x,dict)}==set(range(1,len(ko)+1)),'sceneParagraphCoverage')
 ids=[]
 for x in beats if isinstance(beats,list) else []:
  if not isinstance(x,dict):issues.append('sceneNotObject');continue
  ids.append(x.get('sceneId'))
  for k in ['sceneId','paragraph','kind','renderer','spokenCueKo','visualTargetKo','before','action','result','oneChangedVariable','heldConditionsKo','annotationPlanKo','captionClearanceKo','transitionToNextKo','evidenceStatus']:
   need(k in x and (k=='oneChangedVariable' or x[k] not in (None,'')),'scene:'+str(x.get('sceneId'))+':'+k)
 need(len(ids)==len(set(ids)) and None not in ids,'uniqueSceneIds')
 preservation=packet.get('preservation',{});need(preservation.get('originalInputsChanged') is False,'originalInputsChanged')
 if row['topicId'] in {'03.02','07.04','06.02','11.05'}:
  need(preservation.get('mode')=='preserved-current-production','selectedPreservationMode')
  for k in ['selectedNarration','selectedScenePlan']:
   ref=preservation.get(k);need(isinstance(ref,str) and (R/ref).is_file(),'preservedRef:'+k)
  ref=preservation.get('selectedNarration')
  if isinstance(ref,str) and (R/ref).is_file():
   selected=read(R/ref)
   if isinstance(selected,dict) and 'narrationKo'in selected:need(packet.get('narrationKo')==selected['narrationKo'],'preservedCanonicalKO')
   if isinstance(selected,dict) and 'paragraphsEn'in selected:need(packet.get('paragraphsEn')==selected['paragraphsEn'],'preservedCanonicalEN')
 source=packet.get('sourceReview',{});need(source.get('wholeAssignedPassageRead') is True,'sourceReadingPending')
 text=source.get('sourceTextPath');need(isinstance(text,str) and Path(text).is_file(),'sourceTextPath')
 if isinstance(text,str) and Path(text).is_file():need(sha(text)==source.get('sourceTextSHA256'),'sourceTextHash')
 readiness=packet.get('readiness',{});need(readiness.get('scriptAndStructureComplete') is True,'writtenPreparationIncomplete')
 for k in ['gpuProductionStarted','actualNewAudio','actualNewRender','humanApproval']:need(readiness.get(k) is False,'unprovenReadiness:'+k)
 need(packet.get('readthrough',{}).get('performed') is True,'textReadthroughPending')
 pub=packet.get('publishingPlan',{});need(isinstance(pub.get('titleOptionsKo'),list) and len(pub['titleOptionsKo'])>=(1 if preservation.get('mode')=='preserved-current-production' else 2),'titleOptions')
 for k in ['centralQuestionKo','thesisKo']:need(isinstance(packet.get(k),str) and bool(packet[k].strip()),k)
 return issues
PAGE=r'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>레벨디자인111편 · 대본과 장면 구성</title><style>
:root{color-scheme:dark;font-family:"Malgun Gothic","Noto Sans KR",sans-serif;background:#080b0a;color:#f4f5ef}*{box-sizing:border-box}body{margin:0 auto;max-width:1200px;padding:28px 20px}h1,h2{color:#f3d66b}h1{font-size:30px;margin-bottom:8px}p{line-height:1.75}a{color:#99dfc2}input,select{padding:11px;border:1px solid #6a756d;background:#111813;color:#fff;font:inherit}input{flex:1;min-width:220px}nav{display:flex;gap:10px;flex-wrap:wrap;position:sticky;top:0;background:#080b0a;padding:14px 0;border-bottom:1px solid #485048;z-index:2}details{border-bottom:1px solid #485048;padding:16px 0}summary{cursor:pointer;line-height:1.65;font-weight:bold}.muted{color:#bac4bb}.tag{font-size:13px;border:1px solid #718675;border-radius:3px;padding:3px 7px;margin-left:10px;white-space:nowrap}.title{color:#f3d66b;font-size:21px}.paragraph{border-left:3px solid #78c7a3;padding-left:16px;margin:22px 0}.en{color:#c9d3d0}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}td,th{border:1px solid #485048;text-align:left;padding:10px;vertical-align:top;line-height:1.6}th{background:#172219}.scene{padding:12px 0;border-top:1px dashed #485048}code{overflow-wrap:anywhere}.warning{color:#f3d66b}footer{padding-top:30px;color:#b8c8b9}@media(max-width:600px){body{padding:18px 14px}h1{font-size:24px}table{display:block;overflow-x:auto}.title{font-size:18px}nav{position:static}}
</style><h1>레벨디자인111편 · 대본과 장면 구성</h1><p id="counts"></p>
<p class="muted">완결된 글과 장면 설계를 먼저 검토하는 묶음입니다. 독립 게임영상 확보·권리·실제 음성·시연·최종 재생 검수는 각 편의 후속 항목에서 구분합니다. 기존 영상·원음·촬영 자료는 보존합니다.</p>
<nav><input id="query" aria-label="주제 검색" placeholder="주제 번호·제목·핵심 질문 검색"><select id="chapter" aria-label="장"><option value="">모든 장</option></select><select id="language" aria-label="언어"><option value="both">한국어 + English</option><option value="ko">한국어</option><option value="en">English</option></select><button id="expand" type="button">표시된 편 펼치기</button></nav><main id="list"></main><footer><a href="preproduction-validation-v2.json">구조·원본 보존 검수표</a> · <a href="preproduction-v2.json">전체 목록과 파일 해시</a></footer>
<script id="data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('data').textContent),rows=data.episodes;
const el=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
el('counts').textContent='대본·구성 패킷 '+data.completePackets+'/111편 · 기존 영상 로컬검수본 '+data.existingLocalReviewVideos+'편 · 생성 '+data.createdAtKst;
for(const n of [...new Set(rows.map(x=>x.chapter))].sort((a,b)=>a-b)){const op=document.createElement('option');op.value=n;op.textContent=n+'장';el('chapter').append(op)}
function render(){
 const q=el('query').value.trim().toLowerCase(),ch=el('chapter').value,lang=el('language').value;
 const shown=rows.filter(x=>(ch===''||String(x.chapter)===ch)&&[x.topicId,x.titleKo,x.packet?.centralQuestionKo,x.packet?.thesisKo].join(' ').toLowerCase().includes(q));
 el('list').innerHTML=shown.map(x=>{
  const p=x.packet,head='<summary>'+x.order+'. '+esc(x.topicId)+' <span class="title">'+esc(x.titleKo)+'</span><span class="tag">'+(x.valid?'글·구성 준비':'작성·검수 중')+'</span></summary>';
  if(!p)return '<details>'+head+'<p>기존 초안을 원문과 대조하며 작성 중입니다.</p></details>';
  let body='<p><b>중심 질문</b> '+esc(p.centralQuestionKo)+'<br><b>핵심 설명</b> '+esc(p.thesisKo)+'</p><p class="muted">'+esc(p.preservation?.notesKo)+'</p><p><a href="../../../projects/'+esc(x.slug)+'/preproduction-v2.json">편별 원문 JSON</a></p><h2>전체 내레이션</h2>';
  body+=p.narrationKo.map((k,i)=>'<section class="paragraph"><b>문단 '+(i+1)+'</b>'+(lang!=='en'?'<p>'+esc(k)+'</p>':'')+(lang!=='ko'?'<p class="en">'+esc(p.paragraphsEn[i])+'</p>':'')+'</section>').join('');
  body+='<h2>장면 구성</h2>'+p.sceneBeats.map(s=>'<section class="scene"><b>'+esc(s.sceneId)+' · 문단 '+esc(s.paragraph)+' · '+esc(s.renderer)+'</b><p>'+esc(s.visualTargetKo)+'<br><b>전 상태</b> '+esc(s.before)+'<br><b>변화</b> '+esc(s.action)+'<br><b>결과</b> '+esc(s.result)+'<br><b>바꿀 변수 / 유지 조건</b> '+esc(s.oneChangedVariable??'변경 변수 없음')+' / '+esc(s.heldConditionsKo)+'<br><b>발화 큐</b> '+esc(s.spokenCueKo)+'<br><b>표식</b> '+esc(s.annotationPlanKo)+'<br><b>자막 여백</b> '+esc(s.captionClearanceKo)+'<br><b>다음 장면 연결</b> '+esc(s.transitionToNextKo)+'<br><span class="muted">'+esc(s.evidenceStatus)+'</span></p></section>').join('');
  body+='<h2>원문 대응과 용어</h2><p>'+esc(p.sourceReview?.printPages)+' · '+esc(p.sourceReview?.coverageNotesKo)+'</p><table><tr><th>문단</th><th>원문 구간</th><th>유지한 학습 관계</th></tr>'+p.sourceMapping.map(s=>'<tr><td>'+esc(s.paragraph)+'</td><td>'+esc(s.sourcePrintedPages)+' '+esc(s.sourceSectionOrFigure)+'</td><td>'+esc(s.retainedLogicKo)+'</td></tr>').join('')+'</table>';
  body+='<ul>'+p.glossary.map(g=>'<li>'+esc(g.english)+' ('+esc(g.korean)+'): '+esc(g.plainMeaningKo)+'</li>').join('')+'</ul><h2>영상 자료와 후속 작업</h2><pre style="white-space:pre-wrap">'+esc(JSON.stringify({gameCandidates:p.gameCandidates,claimLimits:p.claimLimits,readthrough:p.readthrough,readiness:p.readiness},null,2))+'</pre><h2>제목·썸네일·설명 초안</h2><pre style="white-space:pre-wrap">'+esc(JSON.stringify(p.publishingPlan,null,2))+'</pre>';
  return '<details>'+head+body+'</details>';
 }).join('');
}
el('query').addEventListener('input',render);el('chapter').addEventListener('change',render);el('language').addEventListener('change',render);el('expand').onclick=()=>document.querySelectorAll('main details').forEach(d=>d.open=true);render();
</script></html>'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--require-complete',action='store_true');args=ap.parse_args()
 batch=read(B/'batch.json');contract=read(B/'preproduction-contract-v2.json');baseline=read(BASELINE);issues=[];items=[];seen=set();script_hashes={}
 for row in batch['projects']:
  topic=row['topicId'];assert topic not in seen;seen.add(topic);p=R/Path(row['project']).parent/'preproduction-v2.json';packet=None;errors=['not-written']
  if p.is_file():
   try:packet=read(p);errors=validate(packet,row,contract)
   except (ValueError,KeyError,TypeError,OSError) as e:errors=['unreadable-or-invalid:'+str(e)]
  valid=not errors
  if packet:
   h=hashlib.sha256(json.dumps(packet.get('narrationKo'),ensure_ascii=False).encode()).hexdigest()
   if h in script_hashes:errors.append('duplicateFullNarration:'+script_hashes[h]);valid=False
   script_hashes[h]=topic
  items.append({'order':row['order'],'topicId':topic,'chapter':row['chapter'],'slug':row['slug'],'titleKo':packet.get('titleKo',row['title']) if packet else row['title'],'path':p.relative_to(R).as_posix(),'sha256':sha(p) if p.is_file() else None,'valid':valid,'issues':errors,'koParagraphs':len(packet.get('narrationKo',[])) if packet else 0,'sceneCount':len(packet.get('sceneBeats',[])) if packet else 0,'packet':packet})
  if errors:issues.append({'topicId':topic,'issues':errors})
 protected=[x for x in baseline['inputFiles'] if sha(R/x['path'])!=x['sha256']]
 complete=sum(x['valid'] for x in items);stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
 report={'schemaVersion':'architectural111-preproduction-validation-v2','checkedAtKst':stamp,'expectedTopics':111,'packetFiles':sum(bool(x['sha256']) for x in items),'completePackets':complete,'issues':issues,'protectedInputCount':len(baseline['inputFiles']),'changedProtectedInputs':protected,'all111WrittenPreparationComplete':complete==111 and not protected,'scope':'Text packet structure/source and scene paragraph coverage/duplicate scripts/preserved input byte hashes; not observed gameplay/rights/actual audio/implementation/render/user approval','gpuProductionStarted':False,'actualHumanReview':False,'videoLocalReviews':batch['completedLocalReviewCount']}
 save(B/'preproduction-validation-v2.json',report)
 manifest={'schemaVersion':'architectural111-preproduction-collection-v2','createdAtKst':stamp,'completePackets':complete,'total':111,'existingLocalReviewVideos':batch['completedLocalReviewCount'],'all111WrittenPreparationComplete':report['all111WrittenPreparationComplete'],'totalKoParagraphs':sum(x['koParagraphs'] for x in items),'totalEnParagraphs':sum(len(x['packet']['paragraphsEn']) for x in items if x['packet']),'totalSceneBeats':sum(x['sceneCount'] for x in items),'episodes':[{k:v for k,v in x.items() if k!='packet'} for x in items],'sourceValidation':'production/batches/architectural-111-20261106/preproduction-validation-v2.json','contract':'production/batches/architectural-111-20261106/preproduction-contract-v2.json','gpuProductionStarted':False,'humanApproval':False}
 save(B/'preproduction-v2.json',manifest)
 payload={'createdAtKst':stamp,'completePackets':complete,'existingLocalReviewVideos':batch['completedLocalReviewCount'],'episodes':items}
 (B/'preproduction-v2.html').write_text(PAGE.replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
 print(json.dumps({'completePackets':complete,'expected':111,'files':report['packetFiles'],'issues':len(issues),'protectedInputsChanged':len(protected),'all111WrittenPreparationComplete':report['all111WrittenPreparationComplete']},ensure_ascii=False))
 if protected or (args.require_complete and not report['all111WrittenPreparationComplete']):raise SystemExit(2)
if __name__=='__main__':main()
