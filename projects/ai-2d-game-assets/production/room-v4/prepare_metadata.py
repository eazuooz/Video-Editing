"""Refresh website facts from the final receipt; prepare only, never commit."""
from pathlib import Path
import json,datetime,hashlib
import scoped_commit as scope
H=Path(__file__).resolve().parent;R=scope.ROOT
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
receipt=read(H/'site-deployment.json');qa=read(H/'website-qa.json');checkpoint=read(H/'checkpoint.json')
assert receipt['site']['status']=='succeeded' and qa['status']=='passed'
version=receipt['savedVersion']['version_number'];commit=receipt['source']['commit_sha'];url=receipt['site']['url']
control=read(R/scope.C);work=read(R/scope.W);row=next(x for x in work['rows'] if x['id']=='S-AI2D')
oldMaster=control['ai2dRoomRevision20261108']['localMasterSha256'];assert oldMaster==checkpoint['videoMasterPreserved']
now=datetime.datetime.now().astimezone().isoformat();prefix=H.relative_to(R).as_posix()
website={**control['ai2dRoomRevision20261108']['latestWebsiteRevision'],'siteVersion':version,'siteSourceCommit':commit,'url':url,'status':'published','review':prefix+'/website-qa.json','videoMasterPreserved':oldMaster,'videoReviewUrlPreserved':row['reviewUrl']}
update={'id':'S-AI2D','set':{'websiteRevision':website,'platformStatus':f'이번 수정본 YouTube/Drive 미업로드 · 웹 게임 v{version} 공개','updatedAt':now},'appendEvidence':[prefix+'/'+n for n in ['checkpoint.json','site-deployment.json','website-qa.json']]}
markdown='\n'.join(['<!-- AI2D-WEBSITE-20261108 -->',f'웹 게임 v{version}: 화면 앞쪽 중앙의 독립 책상·앉기 깊이 순서·게임 화면 안 라디오·브라우저 로컬 500자 메모를 반영했습니다. 동작·모바일 UI 검수 기록은 [웹 검수표](../'+prefix+'/website-qa.json)에 있습니다. 기존 room-v3 영상과 검수 링크는 그대로 유지합니다.','<!-- AI2D-WEBSITE-20261108-END -->'])
specPath=H/'commit-spec.json';existing=read(specPath) if specPath.exists() else {}
spec={'scope':'room-v4-website-and-selected-a03-contrast-v5','readyForCommit':False,'holdReason':'Root explicitly requested waiting until final website receipt and A03 completed handoff.','websiteReceiptSha256':hashlib.sha256((H/'site-deployment.json').read_bytes()).hexdigest(),'websiteSourceCommit':commit,'ownedPaths':[],'a03ApprovedPaths':existing.get('a03ApprovedPaths',[]),'controlPatches':[{'path':['ai2dRoomRevision20261108','latestWebsiteRevision'],'value':website}],'worklistUpdates':[update],'websiteMarkdown':markdown,'a03MarkdownRows':existing.get('a03MarkdownRows',[])}
# Keep an explicitly prepared A03 handoff, but never silently promote it to commit-ready.
spec['controlPatches'] += [x for x in existing.get('controlPatches',[]) if x['path']==['a03ContrastRevision20261108']]
spec['worklistUpdates'] += [x for x in existing.get('worklistUpdates',[]) if x['id']=='A03']
for key in ['a03Record','a03HtmlRow','a03CompletionEvidence']:
 if key in existing:spec[key]=existing[key]
write(specPath,spec)
spec['ownedPaths']=sorted([p.relative_to(R).as_posix() for p in H.iterdir() if p.is_file() and p.suffix in {'.py','.cjs','.json','.txt','.md','.html'}]+spec['a03ApprovedPaths'])
write(specPath,spec);scope.validate(spec)
for name in scope.mod.SHARED:
 p=R/name;before=p.read_bytes();after=scope.overlay(name,before,spec)
 if before!=after:p.write_bytes(after)
print(json.dumps({'stage':'prepared-only','commitExecuted':False,'siteVersion':version,'siteSourceCommit':commit,'videoHashPreserved':oldMaster,'reviewUrlPreserved':row['reviewUrl'],'pending':'Final root website receipt and A03 exact paths/metadata'},ensure_ascii=False,indent=2))
