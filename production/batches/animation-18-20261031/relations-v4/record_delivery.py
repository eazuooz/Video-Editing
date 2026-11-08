"""Record only the user-selected animation revision; preserve foreign Git state."""
from pathlib import Path
import json,datetime,importlib.util,sys,re,contextlib
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
records=read(H/'review-manifest.json')['records'];assert len(records)==18
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();prefix=H.relative_to(R).as_posix()
helper=R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py';s=importlib.util.spec_from_file_location('scoped',helper);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';C='shared/publishing/video-production-control.json';F='docs/VIDEO_WORKFLOW.md'
control=read(R/C)['animationRelationsRevision20261108'];control.update(status='18-local-final-reviews-ready',completedAt=now,reviewManifest=prefix+'/review-manifest.json',reviewUrl='http://127.0.0.1:9284/',humanReview='pending',platformChanged=False)
marker='ANIMATION-RELATIONSHIP-MAP-20261108';rule=re.search(r'<!-- '+marker+r' -->.*?<!-- '+marker+r'-END -->',(R/F).read_text('utf-8-sig'),re.S).group(0)
section='\n<!-- ANIMATION-RELATIONS-REVIEW-20261108 -->\n## 애니메이션18편 관계도 보강\n\n각 편의 개념 관계 설명을 시연 앞에 추가하고, 초기 반복 시연의 순서를 정리했다. A06 세 공격 시간표·A08 날개 부피·A14 블렌딩 타임라인도 보완. 기존 본문 음성·이전 완성본·YouTube 상태 보존. **18편 로컬 완성, 사용자 시청·청취 검수 대기.**\n\n[통합 검수 영상](http://127.0.0.1:9284/) · [대본·관계도 계획](../'+prefix+'/planning/narration.md) · [원본 대비 검수표](../production/batches/animation-18-20261031/review-20261108/REVIEW.md)\n<!-- ANIMATION-RELATIONS-REVIEW-20261108-END -->\n'
def overlay(name,raw,spec):
 if name==C:return m.patch(raw,['animationRelationsRevision20261108'],control)
 if name==W:
  for record in records:
   i=next(i for i,r in enumerate(m.load(raw)['rows']) if r['id']==record['id']);cap=next(f for f in record['files'] if f['kind']=='captioned.mp4')
   updates={'productionComplete':True,'productionStatus':'관계도 설명·정상속도 관찰·기존 분석 보강 완료','reviewStatus':'relations-v4 현재 파일 기술·표본 검사 완료 · 사용자 시청·청취 검수 대기','executionStatus':'관계도 보강본 로컬 검수 준비','localMasterAvailable':True,'captionedMasterSha256':cap['sha256'],'deliveryLedger':'projects/'+record['slug']+'/production/relations-v4/checkpoint.json','updatedAt':now,'relationsRevision':{'version':'relations-v4','masterSha256':cap['sha256'],'reviewUrl':'http://127.0.0.1:9284/'+record['id']+'/','humanViewed':False,'humanListened':False,'platformChanged':False}}
   for k,v in updates.items():raw=m.patch(raw,['rows',i,k],v)
  return raw
 if name==D:
  text=raw.decode('utf-8-sig');pattern=r'\n<!-- ANIMATION-RELATIONS-REVIEW-20261108 -->.*?<!-- ANIMATION-RELATIONS-REVIEW-20261108-END -->\n'
  text=re.sub(pattern,lambda _:section,text,flags=re.S) if '<!-- ANIMATION-RELATIONS-REVIEW-20261108 -->' in text else text.rstrip()+'\n'+section
  lines=text.splitlines(keepends=True)
  for i,line in enumerate(lines):
   if any(line.startswith('| '+r['id']+' | ') for r in records):
    end=line.rfind('|');before=line.rfind('|',0,end);lines[i]=line[:before+1]+' 관계도 보강본 · 로컬 완성 / 통합 검수 대기 |\n'
  return ''.join(lines).encode('utf-8')
 if name==F:
  text=raw.decode('utf-8-sig');pattern=r'<!-- '+marker+r' -->.*?<!-- '+marker+r'-END -->'
  text=re.sub(pattern,lambda _:rule,text,flags=re.S) if '<!-- '+marker+' -->' in text else text.replace('### 실제 게임으로 여는 Abstract','### 실제 게임으로 여는 Abstract\n\n'+rule,1)
  if '<!-- '+marker+' -->' not in text:
   # Older independently staged workflow versions lack the newer Abstract heading.
   # Append only our scoped block, preserving every unrelated staged byte.
   text=text.rstrip()+'\n\n'+rule+'\n'
  assert '<!-- '+marker+' -->' in text
  return text.encode('utf-8')
 raise ValueError(name)
m.SHARED={W,D,C,F};m.overlay=overlay
for name in m.SHARED:(R/name).write_bytes(overlay(name,(R/name).read_bytes(),{}))
decisions=read(H/'checkpoint.json').get('executionDecisions',[])
save(H/'checkpoint.json',{'stage':'18-local-final-reviews-ready','completedEpisodes':[r['id'] for r in records],'reviewUrl':'http://127.0.0.1:9284/','reviewManifest':prefix+'/review-manifest.json','humanReviewPending':[r['id'] for r in records],'platformChanged':False,'automaticNextVideo':False,'executionDecisions':decisions,'updatedAt':now})
owned=[]
for p in H.rglob('*'):
 if not p.is_file() or 'local' in p.relative_to(H).parts or '__pycache__' in p.parts:continue
 if p.suffix in {'.py','.cjs','.json','.md','.html'} or p.name=='.gitignore':owned.append(p.relative_to(R).as_posix())
for r in records:
 P=R/'projects'/r['slug'];owned += [p.relative_to(R).as_posix() for p in (P/'production/relations-v4').glob('*.json')]
 for name in ['project.json','rebuild.json','production/delivery-output.json','production/review-ledger.json']:
  p=P/name
  if p.exists():owned.append(p.relative_to(R).as_posix())
owned=sorted(set(owned))
def validate(spec):
 assert spec['ownedPaths']==owned and all((R/p).is_file() for p in owned)
 assert not any('/local/' in p or p.lower().endswith(('.mp4','.wav','.png','.jpg')) for p in owned)
 return owned+sorted(m.SHARED)
m.validate=validate;sp=L/'commit-spec.json';save(sp,{'ownedPaths':owned})
if '--commit' in sys.argv:
 sys.argv=[str(helper),'--spec',str(sp),'--execute','--push','--message','Add narrated relationship diagrams before animation demonstrations']
 with (L/'commit.json').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):m.main()
 print(read(L/'commit.json')['commit'])
else:print('Scoped18 animation delivery recorded; no platform changes')
