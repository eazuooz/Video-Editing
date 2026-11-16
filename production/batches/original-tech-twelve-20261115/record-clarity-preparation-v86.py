"""Record actual title completion and selected revision work without touching foreign rows."""
from pathlib import Path
import copy,hashlib,html,importlib.util,json,re
H=Path(__file__).resolve().parent;ROOT=H.parents[2];KEY='explicitOriginalTechTwelve20261115'
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def canonical(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def main():
 title=M/'shorts-mario64-lakitu-camera/title-revision-v83/local-review-v2/bundle-v2.json';bundle=read(title);assert bundle['localFinalBundleComplete']
 manifest=copy.deepcopy(read(H/'local-final-review-manifest-v2.json'));old=copy.deepcopy(manifest['projects'][1]);row=manifest['projects'][1];row.update(version='mario-title-v83',bundle=dict(**pin(title),bytes=title.stat().st_size),artifacts=bundle['artifacts'],titleKo=bundle['titleKo'],selectedRevisionComplete=True)
 row['checks']['technicalVisual']['approvedPilotReview']=pin(title.parent.parent/'film-v83/pilot-visual-review.json')
 selected=read(H/'selected-clarity-request-v83.json')['selectedOrders']
 for r in manifest['projects']:
  if r['order']in selected and r['order']!=2:r['requestedClarityRevisionPending']=True
 manifest.update(selectedRevision='selected-nine-clarity-revisions-v83',selectedLocalRevisionPreviewComplete=False,completedSelectedRevisions=1,pendingSelectedRevisions=8,previousDeliveredManifest=pin(H/'local-final-review-manifest-v2.json'),humanApproval=False,deliveryPostedInChat=False)
 mp=H/'local-revision-progress-manifest-v3.json';save(mp,manifest)
 page=(H/'local-final-review-v2.html').read_text('utf8')
 for key,r in old['artifacts'].items():page=page.replace(Path(r['path']).as_uri(),Path(row['artifacts'][key]['path']).as_uri())
 page=page.replace('2. 마리오64의 카메라맨은 누가 움직일까? #게임개발','2. '+html.escape(bundle['titleKo']))
 page=re.sub(r'(<h2>2\..*?</h2><p>).*?(</p>)',r'\1제목 수정본 완성 · 음성·자막 유지\2',page,count=1)
 for order in selected:
  if order!=2:page=re.sub(r'(<h2>'+str(order)+r'\..*?</h2><p>).*?(</p>)',r'\1설명·예시 수정 작업 중 · 아래는 보존한 기존 검수본\2',page,count=1)
 banner='<aside style="padding:18px;background:#17382d;color:white"><strong>선택한 9편 수정 진행표: 제목 수정 1편 완료 / 설명·예시 보강 8편 제작 중.</strong><p>기존 12편 검수본을 보존했습니다. 아래 8편은 새 수정본이 완성될 때 교체됩니다. 사람의 시청·청취 승인과 게시 승인은 별개입니다.</p></aside>'
 page=page.replace('<body>','<body>'+banner,1);pp=H/'local-revision-progress-v3.html';assert not pp.exists();pp.write_text(page,'utf8')
 sp=load('exact_scope_splice_v86',H/'finalize-cpu-preparation-v1.py');single=load('one_row_splice_v86',H/'finish-lockon-revision-ledger-v80.py');scopes=[]
 for name in ['video-production-control.json','video-worklist.json']:
  path=ROOT/'shared/publishing'/name;raw=path.read_bytes().decode('utf-8-sig');before=json.loads(raw);after=copy.deepcopy(before);own=after[KEY]
  own.update(activeRevisionProgress=dict(request=pin(H/'selected-clarity-request-v83.json'),selectedOrders=selected,completedTitleRevision=pin(title),selectedRevisionCompleted=1,selectedRevisionPending=8,progressPage=str(pp.relative_to(ROOT)).replace('\\','/'),narrationPreparation=pin(H/'selected-clarity-narration-preparation-v84.json'),humanApproval=False),selectedRevisionReviewReady=False)
  text=sp.replace_value(raw,KEY,own)
  if name=='video-worklist.json':
   wr=next(r for r in after['rows']if r.get('id')=='OT12-02');wr.update(title=bundle['titleKo'],latestTitleRevision=pin(title),reviewStatus='제목 수정본 기술 검수 완료 / 설명 수정 8편 진행 중 / 사람 검수 대기');text=single.replace_one_row(text,wr)
  check=json.loads(text)
  for d in [before,check]:
   d.pop(KEY,None)
   if 'rows'in d:d['rows']=[r for r in d['rows']if r.get('id')!='OT12-02']
  assert before==check;path.write_bytes(text.encode('utf8'));actual=read(path);scopes.append(dict(path=str(path),ownKeySha256=canonical(actual[KEY]),rowSha256=canonical([r for r in actual['rows']if r.get('id','').startswith('OT12-')])if'rows'in actual else None,foreignContentPreserved=True))
 docs=[]
 path=ROOT/'docs/VIDEO_WORKFLOW.md';text=path.read_bytes().decode('utf-8-sig');end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->';note='2026-11-16 최신 사용자 선택은 2번 제목 및 3·5·6·7·8·10·11·12번 설명·실제 예시 보강이다. 기존 원문 학습 순서와 승인 PCM을 보존하고 추가 문장만 제작한다. 2번은 잘못된 최초 도입 표현을 피한 제목 수정본을 완성했고, 나머지 8편은 새 음성·연결 검수 및 예시 합성 중이다. [수정 진행표](../production/batches/original-tech-twelve-20261115/local-revision-progress-v3.html)는 기존본과 새 수정본 상태를 구분한다. 다른 편·111·자동화·플랫폼은 변경하지 않는다.\r\n'
 assert note not in text;text=text.replace(end,note+end);path.write_bytes(text.encode('utf8'));a=text.index('<!-- ORIGINAL-TECH-TWELVE-20261115 -->');z=text.index(end)+len(end);docs.append(dict(path=str(path),ownMarkerSha256=hashlib.sha256(text[a:z].encode()).hexdigest()))
 names=['prepare-selected-clarity-v83.py','selected-clarity-request-v83.json','shorts-layout-clarity-v83.py','run-camera-title-revision-v83.py','verify-encoded-clarity-v83.py','finalize-camera-title-v83.py','clarity-content-v83.py','prepare-clarity-narration-v84.py','selected-clarity-narration-preparation-v84.json','run-selected-clarity-voice-v84.py','run-selected-clarity-asr-v84.py','run-selected-clarity-source-queue-v84.py','review-clarity-voice-v84.py','clarity-diagrams-v84.py','clarity-layout-v84.py','prepare-clarity-film-v84.py','prepare-journey-clarity-repair-v85.py','prepare-inside-clarity-repair-v85.py','run-selected-clarity-voice-v85.py','run-selected-clarity-asr-v85.py','prepare-clarity-master-v90.py','run-selected-clarity-master-asr-v90.py','review-clarity-master-v90.py','record-clarity-preparation-v86.py','local-revision-progress-v3.html','local-revision-progress-manifest-v3.json']
 files=[H/x for x in names]
 for r in read(H/'selected-clarity-narration-preparation-v84.json')['projects']:
  p=ROOT/'projects'/r['slug'];files += [p/x for x in ['planning/source-action-clarity-v84.json','planning/narration-repair-v84.json','planning/caption-clauses-repair-v84.json','script/narration.repair-v84.json','production/tts-manifest-repair-v84.json']]
  if r['order']in[3,5]:files += [p/x for x in ['planning/narration-repair-v85.json','planning/caption-clauses-repair-v85.json','script/narration.repair-v85.json','production/tts-manifest-repair-v85.json']]
 files.append(ROOT/'projects/shorts-mario64-lakitu-camera/publishing/metadata-title-v83.json')
 save(H/'production-resume-validation-v86.json',dict(sourceInputs=[pin(x)for x in files],scopedSharedInputs=scopes,scopedDocInputs=docs,progress=dict(finalVideos=12,selectedRevisionCompleted=1,selectedRevisionPending=8,humanApproval=False),platformActions=[],otherBatchesUnchanged=True))
 print(json.dumps(dict(progressPage=str(pp),sourcePaths=len(files),selectedCompleted=1,selectedPending=8)))
if __name__=='__main__':main()
