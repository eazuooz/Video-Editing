"""Record the human's explicit approval of the V8 script and local production."""
from pathlib import Path
import datetime, hashlib, json
R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle'
H=Path(__file__).parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
script=P/'script/revision-v8-orientation-matrix/narration.ko.json'
digest=hashlib.sha256(script.read_bytes()).hexdigest()
assert digest=='2cfce716a62d3b951a81a5022dd216ac4cbaafb7b73ffa20e9d0765798e789c3'
evidence='대본 좋은거같아 제작해줘~'
auth=dict(revision='orientation-matrix-v8',project=P.name,deliverySlug='game-math-orientation-matrix',scriptApproved=True,humanScriptReview='approved',approvedScriptSha256=digest,approvedScript=str(script.relative_to(R)).replace('\\','/'),fullProductionAuthorized=True,ttsAuthorized=True,renderAuthorized=True,platformMutation=False,automaticNextVideo=False,userEvidence=evidence,recordedAt=stamp,scope='Approved article8.1–8.2.5 only: full local video, internal QA, four outputs and selective Git; final human video review before platform upload.',heavyJobConcurrency='One shared GPU_HANDOFF lease at a time; preserve foreign editors, processes and staging.')
save(H/'authorization.json',auth)
control=R/'shared/publishing/video-production-control.json'
d=read(control);claim=d['scopedProductionAuthorizations'][P.name]
claim.update(auth,status='authorized-production-v8',scriptAuthorized=True,scriptSha256=digest,selectedOn=stamp,localReview='output/game-math-orientation-matrix/index.html')
d['updatedAt']=stamp;save(control,d)
for name in ['project.json','production/checkpoint.json']:
 p=P/name;d=read(p);work=d['activeScriptWork'];work.update(status='approved-for-production',humanScriptReview='approved',userApprovalEvidence=evidence,approvedAt=stamp,authorizedScope=auth['scope'],newTts='authorized-preparing',newVideo='authorized-preparing')
 d['activeProductionV8']=dict(revision=auth['revision'],stage='preparing-voice-and-scenes',authorization=str((H/'authorization.json').relative_to(R)).replace('\\','/'),approvedScriptSha256=digest,deliveryProject=auth['deliverySlug'],humanFinalReview='pending',platformMutation=False)
 if name=='project.json': d.update(status='producing-v8-orientation-matrix',selectedDeliveryProject=auth['deliverySlug'])
 else: d.update(stage='v8-production-preparation',runningJob=None,nextAction='Generate paragraph Qwen voice and prepare coherent Unity scenes; complete local review version.')
 save(p,d)
p=P/'planning/revision-v8-orientation-matrix/production-plan.json';d=read(p);d.update(stage='full-production',productionAuthorization=str((H/'authorization.json').relative_to(R)).replace('\\','/'))
d['authorization'].update(tts=True,render=True,newGameCapture=True,scriptApproved=True,userEvidence=evidence,approvedScriptSha256=digest)
d['reviewLimits']='Script coverage and numerical checks reused unchanged; new audio/visual/final master checks required. Human final video review pending.';save(p,d)
p=P/'production/review-ledger.json';d=read(p);d['v8ScriptApproval']=auth;d['pendingScriptRevision']=None;save(p,d)
p=R/'shared/publishing/video-worklist.json';d=read(p)
row=next(x for x in d['rows'] if x['id']=='M04')
row.update(productionStatus='V8 제작 중 · 8.1–8.2.5 자세와 회전행렬',reviewStatus='V8 대본 사용자 승인 · 완성 영상 검수 대기',currentRevision='orientation-matrix-v8')
d['updatedAt']=stamp;save(p,d)
print('V8 script approved; scoped local production authorized; primary selection preserved.')
