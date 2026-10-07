from pathlib import Path
import json,datetime,sys
ROOT=Path(__file__).resolve().parents[3];BATCH=ROOT/'production/batches/visual-depth-revision'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
q=read(BATCH/'queue.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for i in q['items']:
 folder=ROOT/'projects'/i['slug']/'production/visual-depth-v1'
 request=folder/'caption-safe-repair-request.json'
 if not request.exists():continue
 r=read(request);i['revision']=r['revision']
 review=read(folder/'white-preflight-direct-review.json')
 current=review.get('revision')==r['revision'] and review.get('sourceSha256')==r['sourceSha256']
 i['currentPreflightApproved']=bool(current and review.get('preflightPixelsApproved'))
 if i['slug']!='motion-sickness-games':
  i.update(stage='caption-safe-preflight-reviewed-awaiting-render' if i['currentPreflightApproved'] else 'caption-safe-preflight-refinement-awaiting-direct-reading',pipelinePid=None,activePid=None)
  if i.get('pipelineExecution')=='production/batches/visual-depth-revision/local-review-pipeline-execution.json':
   i['historicalPipelineExecution']=i.pop('pipelineExecution')
 if i['slug']=='motion-sickness-games':
  i['pipelineSessionRecord']=dict(sessionId=79542,pid=15792,command=['C:/Users/eazuo/miniconda3/envs/renderformer/python.exe','production/batches/visual-depth-revision/run-caption-safe-local.py','motion-sickness-games'],checkedAt=now)
if 'localPipelineSessionId' in q:q['historicalLocalPipelineSessionId']=q.pop('localPipelineSessionId')
q['updatedAt']=now
(BATCH/'queue.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Current revision gates synchronized; no encoded or upload approval changed')
