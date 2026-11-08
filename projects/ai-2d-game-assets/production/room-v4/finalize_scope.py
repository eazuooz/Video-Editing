"""Consume the completed A03 handoff and frozen web receipt; no Git mutation."""
from pathlib import Path
import json,datetime,re,hashlib
import prepare_metadata  # Refresh only the explicitly owned website metadata.
import scoped_commit as scope
H=Path(__file__).resolve().parent;R=scope.ROOT;A=R/'projects/animation-breaking-down-attack-animations/production/contrast-v5'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
handoff=read(A/'changed-files.json');delivery=read(A/'delivery.json');checkpoint=read(A/'checkpoint.json')
assert handoff['writeComplete'] is True
assert handoff['masterSha256']==delivery['captionedMasterSha256']==checkpoint['captionedMasterSha256']=='478a289bfe41b3b0013c1eb9e45fcaece6f06a2d170d98de5b3efdd142f90120'
assert checkpoint['stage']=='local-four-files-ready-user-review-pending'
assert checkpoint['other17ManifestRecordBytesUnchanged'] and checkpoint['audioPacketsAndBothSrtBytesUnchanged']
assert set(handoff['sharedOverlay'])=={scope.M,scope.B}
s=read(H/'commit-spec.json');control=read(R/scope.C);work=read(R/scope.W);row=next(x for x in work['rows'] if x['id']=='A03')
now=datetime.datetime.now().astimezone().isoformat();prefix=A.relative_to(R).as_posix()
a03Control={**control['a03ContrastRevision20261108'],'status':'review-pending','updatedAt':now,'revision':'contrast-v5','checkpoint':prefix+'/checkpoint.json','reviewUrl':delivery['reviewUrl'],'captionedMasterSha256':delivery['captionedMasterSha256'],'humanReview':'pending','sampledRealPlayback':'passed; root observed 114.433–123.466 s in current 1080p browser video, no full human watch/listening claim'}
update={'id':'A03','set':{'productionComplete':True,'productionStatus':'같은 실제 공격의 네 단계 자세·관절 궤적·기준 자세 비교 보완 완료','reviewStatus':'contrast-v5 기술·인코딩·모바일 표본 및 실제 재생 확인 · 최종 사용자 검수 대기','humanApproval':'A03 제작 명시 승인 · contrast-v5 사람 검수 대기','platformStatus':'로컬 검수 · YouTube/Drive 변경 없음','executionStatus':'contrast-v5-local-final-review','localMasterAvailable':True,'updatedAt':now,'reviewUrl':delivery['reviewUrl'],'captionedMasterSha256':delivery['captionedMasterSha256'],'deliveryLedger':prefix+'/checkpoint.json','contrastRevision':{'version':'contrast-v5','masterSha256':delivery['captionedMasterSha256'],'durationSeconds':delivery['durationSeconds'],'frames':delivery['frames'],'reviewUrl':delivery['reviewUrl'],'sampledRealPlayback':'pass','humanViewed':False,'humanListened':False,'platformChanged':False,'other17Unchanged':True,'previousRelationsVersionPreserved':True}},'appendEvidence':[prefix+'/'+n for n in ['checkpoint.json','visual-review.json','technical-qa.json','integration-proof.json','http-proof.json']]}
s['a03ApprovedPaths']=handoff['ownedSourceAndMetadata'];s['ownedPaths']=sorted(set(s['ownedPaths']+s['a03ApprovedPaths']))
s['controlPatches']=[x for x in s['controlPatches'] if x['path']!=['a03ContrastRevision20261108']]+[{'path':['a03ContrastRevision20261108'],'value':a03Control}]
s['worklistUpdates']=[x for x in s['worklistUpdates'] if x['id']!='A03']+[update]
s['a03Record']=next(x for x in read(R/scope.M)['records'] if x['id']=='A03');assert s['a03Record']['revision']=='contrast-v5'
s['a03HtmlRow']=re.search(r'<tr><td>A03</td>.*?</tr>',(R/scope.B).read_text('utf8'),re.S).group()
line=next(x for x in (R/scope.D).read_text('utf-8-sig').splitlines() if x.startswith('| A03 |'))
s['a03MarkdownRows']=[re.sub(r'\| [^|]* \|$',lambda _:'| contrast-v5 · 네 단계 자세·궤적 비교 보강 / 사용자 검수 대기 |',line)]
s['a03CompletionEvidence']={'handoff':prefix+'/changed-files.json','handoffSha256':sha(A/'changed-files.json'),'deliverySha256':sha(A/'delivery.json'),'writeComplete':True,'rootApprovedCommitAfterCompletedHandoff':True}
s['readyForCommit']=True;s['holdReason']=None
write(H/'commit-spec.json',s);scope.validate(s)
for name in scope.mod.SHARED:
 p=R/name;before=p.read_bytes();after=scope.overlay(name,before,s)
 if before!=after:p.write_bytes(after)
print(json.dumps({'readyForCommit':True,'ownedPaths':len(s['ownedPaths']),'sharedPaths':sorted(scope.mod.SHARED),'siteSource':s['websiteSourceCommit'],'a03Master':delivery['captionedMasterSha256'],'gitExecuted':False},ensure_ascii=False,indent=2))
