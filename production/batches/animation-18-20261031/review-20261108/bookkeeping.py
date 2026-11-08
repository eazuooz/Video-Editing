from pathlib import Path
import json,importlib.util,sys,datetime,re,contextlib
P=Path(__file__).resolve().parent;R=P.parents[3];L=P/'local';L.mkdir(exist_ok=True)
helper=R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
s=importlib.util.spec_from_file_location('scoped',helper);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';prefix=P.relative_to(R).as_posix()+'/'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();ids=['A'+str(n).zfill(2) for n in range(1,19)]
audit={'date':now,'version':'pacing-v3','scope':'Full source/current KO text;144 targeted encoded frames; not full human listening','status':'reviewed-with-improvements','report':prefix+'REVIEW.md','priorityEpisodes':['A06','A08','A14'],'remakesPerformed':False,'platformChanged':False}
section='\n<!-- ANIMATION-CONTENT-AUDIT-20261108 -->\n## 애니메이션18편 원본 대비 전달력 검수\n\n2026-11-08: 원본/현재 대본 전체 대조와 최종 인코딩144장 표본 확인. 핵심 내용은 대체로 유지. **A06·A08·A14 핵심 시연 우선 보완**, 나머지는 도입 연결·확대·중복 설명 정리. 전체 사람 청취 완료를 뜻하지 않으며 기존 파일·게시·예약은 유지.\n\n[18편 검수표](../'+prefix+'REVIEW.md) · [현재 검수 영상](http://127.0.0.1:9277/)\n<!-- ANIMATION-CONTENT-AUDIT-20261108-END -->\n'
def overlay(name,raw,spec):
 if name==W:
  rows=m.load(raw)['rows']
  for id in ids:
   indices=[n for n,r in enumerate(rows) if r['id']==id];assert len(indices)==1,id
   value=dict(audit,episodePriority='P1' if id in audit['priorityEpisodes'] else 'P2',videoHashVerified=True)
   # Add a dedicated audit object; preserve production, actual user review and platform fields.
   row=dict(rows[indices[0]]);row['contentAudit']=value;raw=m.patch(raw,['rows',indices[0]],row)
  return raw
 if name==D:
  text=raw.decode('utf-8-sig');pat=r'\n<!-- ANIMATION-CONTENT-AUDIT-20261108 -->.*?<!-- ANIMATION-CONTENT-AUDIT-20261108-END -->\n'
  text=re.sub(pat,lambda _:section,text,flags=re.S) if '<!-- ANIMATION-CONTENT-AUDIT-20261108 -->' in text else text.rstrip()+'\n'+section
  return text.encode('utf-8')
 raise ValueError(name)
m.SHARED={W,D};m.overlay=overlay
for name in m.SHARED:(R/name).write_bytes(overlay(name,(R/name).read_bytes(),{}))
owned=sorted(p.relative_to(R).as_posix() for p in P.iterdir() if p.is_file() and (p.suffix in {'.json','.py','.md'} or p.name=='.gitignore'))
def validate(spec):
 assert spec['ownedPaths']==owned
 assert all(x.startswith(prefix) and (R/x).is_file() for x in owned)
 return owned+sorted(m.SHARED)
m.validate=validate;sp=L/'commit-spec.json';sp.write_text(json.dumps({'ownedPaths':owned}),encoding='utf-8')
if '--commit' in sys.argv:
 sys.argv=[str(helper),'--spec',str(sp),'--execute','--push','--message','Audit animation A01-A18 source fidelity and explanation clarity']
 with (L/'commit.json').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):m.main()
 print(json.loads((L/'commit.json').read_text('utf-8'))['commit'])
else:print('Scoped animation audit recorded; no production or platform changes')
