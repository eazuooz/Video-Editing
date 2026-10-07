"""Promote only a directly reviewed exact pair to local delivery; old upload records remain history."""
from pathlib import Path
import sys,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];folder=ROOT/'projects'/slug/'production/visual-depth-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=read(folder/'pair-technical-qa.json');review=read(folder/'encoded-pixel-direct-review.json');baseline=read(folder/'baseline.json')
outputs={o['variant']:o for o in qa['outputs']}
if not review['allFinalPixelsReviewed'] or review['videoSha256']!=outputs['captioned']['sha256']:raise RuntimeError('Exact encoded captioned direct review required')
for o in outputs.values():
 if o['fullDecodeExitCode']!=0 or o['frames']!=qa['expectedFrames'] or sha(ROOT/o['path'])!=o['sha256']:raise RuntimeError('Current pair QA mismatch')
for f in baseline['files']:
 if f['role'] in ['script','scriptEn','audioMix','captionsKo','captionsEn'] and sha(ROOT/f['path'])!=f['sha256']:raise RuntimeError('Preserved input changed')
manifestPath=ROOT/'projects'/slug/'project.json';m=read(manifestPath)
if m.get('visualDepthRevision',{}).get('allFinalPixelsReviewed'):raise RuntimeError('Inspect existing adopted pair; preserve publishing history')
m['status']='reviewed-visual-depth-correction-awaiting-private-reupload'
m['publishReady']=False
m['paths']['videoClean']=outputs['clean']['path'];m['paths']['videoBurnedCaptions']=outputs['captioned']['path']
previous=m.get('publishing',{}).copy();m.setdefault('publishingHistory',[]).append(dict(reason='Preserved previous completed upload before requested visual correction',publishing=previous))
publishing=m.setdefault('publishing',{});publishing.update(uploaded=False,videoId=None,actualVideoId=None,privacyStatus='private',scheduled=False,receipt=f'projects/{slug}/publishing/youtube-upload-depth-v1.json',thumbnail=f'projects/{slug}/publishing/thumbnail-depth-v1.png',previousVideoId=next(i['oldVideoId'] for i in read(ROOT/'production/batches/visual-depth-revision/queue.json')['items'] if i['slug']==slug))
m['visualDepthRevision']=dict(status='reviewed-collected-candidate',approvedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline=baseline.get('path',f'projects/{slug}/production/visual-depth-v1/baseline.json'),technicalQa=f'projects/{slug}/production/visual-depth-v1/pair-technical-qa.json',pixelReview=f'projects/{slug}/production/visual-depth-v1/encoded-pixel-direct-review.json',allFinalPixelsReviewed=True,narrationAndSrtPreserved=True,gpuTts=0,privateUploadCompleted=False,gitDelivered=False)
fr=m.setdefault('finalRender',{});fr.update(status='visual-depth-correction-rendered-and-directly-reviewed',videoClean=outputs['clean']['path'],videoBurnedCaptions=outputs['captioned']['path'],pixelReview=m['visualDepthRevision']['pixelReview'],technicalQa=m['visualDepthRevision']['technicalQa'],allFinalPixelsReviewed=True)
write(manifestPath,m)
qpath=ROOT/'production/batches/visual-depth-revision/queue.json';q=read(qpath);item=next(i for i in q['items'] if i['slug']==slug)
item.update(stage='reviewed-pair-awaiting-output-collection-and-private-reupload',renderApproved=True,allPixelsReviewed=True,pixelReview=m['visualDepthRevision']['pixelReview'],pid=None,activePid=None)
write(qpath,q);print(slug+' exact reviewed pair adopted; upload/Git remain false')
