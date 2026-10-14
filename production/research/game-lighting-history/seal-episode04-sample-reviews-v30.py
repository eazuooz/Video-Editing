"""Seal direct sample review, preserving rejected media and incomplete moving QA."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
R=Path(__file__).resolve().parents[3]; P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def proof(p):return {'path':rel(p),'sha256':sha(p)}
def seal(directory,execution,sid,create):
 state=read(execution); w=state['worker']; assert abs(w['createTime']-create)<.01
 try:
  proc=psutil.Process(w['pid']); assert abs(proc.create_time()-create)>.01, 'Original worker still alive'
 except psutil.NoSuchProcess: pass
 assert state['status'] in ['technical-review-pair-ready','encoded-samples-ready'] and state['active'] is None
 assert all(c['exitCode']==0 for c in state['commands'])
 p=directory/'session.json'
 if not p.exists():write(p,{'sessionId':sid,'worker':w,'exitCode':0,'terminalCompletionObserved':True,'evidence':'Unified exec completion was directly observed in preceding context of this continuing task; current completed execution and identity rechecked.','completedAt':state['endedAt'],'verifiedAt':now(),'originalWorkerAlive':False,'execution':proof(execution)})
 return p
mega=P/'megalights-chapter-review-build-v28.json'; hair=P/'hair-chapter-review-build-v29.json'
seal(R/'production/research/game-lighting-history/local/episode04-hair-chapter-v29',P/'hair-chapter-review-execution-v29.json',79357,1791691083.1800508)
for name,ver,session,create,images,boards in [('megalights',28,48036,1791691009.755185,204,52),('hair',29,7890,1791691325.1979356,268,68)]:
 folder=R/f'production/research/game-lighting-history/local/episode04-{name}-encoded-v{ver}'
 ep=folder/'execution.json'; ex=read(ep); assert (len(ex['items']),len(ex['boards']))==(images,boards)
 sessionPath=seal(folder,ep,session,create)
 bp=mega if name=='megalights' else hair; b=read(bp); plan=read(R/b['plan']['path'])
 for ref in b['outputs']:assert sha(R/ref['path'])==ref['sha256']
 reviewed=[]
 for item in ex['boards']:
  assert sha(R/item['path'])==item['sha256']
  reviewed.append({**item,'directlyViewed':True,'reviewedAt':now(),'scope':'Every board was directly read across this continuing task; sampled frames only.'})
 findings=([
 'All204 samples on52boards directly read. Moving canopy light and metal surface markers remain on their roles in sampled frames; source dark transitions are retained without inventing an ON/OFF control.',
 'Visibility and candidate diagrams retain original6 plus guide15 KO/EN paragraphs and original PCM. Opaque header strips are clear; candidate annotation ends before the following state.',
 'Captions are readable at the fixed bottom center. Continuous playback, full60:40 allocation and final mixed audio remain pending.'
 ] if name=='megalights' else [
 'All268 samples on68boards directly read: clean001-014 and captioned001-054. All34cue before/first/middle/last/after samples and12cut/native samples read.',
 'REJECTED: yellow rectangle covers RednessMainColor/RednessSecondaryColor instead of narrated MelaninMainColor. Repair this native cut only; preserve11 other encoded cuts and all original PCM/AAC.',
 'Investigate possible one-frame cut discrepancy between clean and captioned near f43 and f1827; exact PTS continuity alone does not prove visual alignment.',
 'Cue229 breaks the spoken number 영 점 오 across lines; repair wrapping while keeping the exact spoken words and times.',
 'Alpha0.5 red-front/blue-front numerical contributions, crossing per-pixel order, depth peeling cost, weighted approximation limits, strand material versus geometry and demo versus invention dates read. Negative source input is shown only as the original editor action, not a valid physical melanin prescription.',
 'No sampled caption overlap with the demonstrated input or hair was found. This rejected sample review does not approve moving/final pixels or full60:40.'
 ])
 record={'reviewedAt':now(),'scope':'Direct encoded samples; not continuous playback or final upload approval','plan':b['plan'],'build':proof(bp),'execution':proof(ep),'session':proof(sessionPath),'boards':reviewed,'sampleCount':images,'allPlannedSamplesDirectlyViewed':True,'captionCuesReviewed':[c['id'] for c in plan['cues']],'sampledCaptionClearanceApproved':name=='megalights','sampledDiagramClearanceApproved':True,'sampledAnnotationApproved':name=='megalights','rejected':name=='hair','findings':findings,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending','normalSpeedContinuousPlayback':'pending','newTts':0,'newGitImages':0}
 dest=P/f'{name}-encoded-direct-review-v{ver}.json';write(dest,record)
 cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
 j[f'episode04{name.title()}EncodedDirectReviewV{ver}']={**proof(dest),'sampleCount':images,'boards':boards,'rejected':name=='hair','allFinalPixelsReviewed':False}
 j['updatedAt']=now();tmp=cp.with_suffix('.seal-v30.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
 print(json.dumps({'review':rel(dest),'samples':images,'boards':boards,'rejected':name=='hair'}))
