"""Record only the seventh video's explicitly requested visual revision."""
import json,datetime,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(P/'production/delivery.json');project=read(P/'project.json');old=read(L/'camera-guides-v3/delivery.json')
assert d['technicalChecks']['status']=='pass' and d['technicalChecks']['identicalAac']
assert hashlib.sha256(Path(old['files']['captioned']['path']).read_bytes()).hexdigest()==old['files']['captioned']['sha256']
assert d['technicalChecks']['aacHash']==old['technicalChecks']['aacHash']
qa=P/project['currentFinalDirectory']/('qa-sequential-'+d['files']['captioned']['sha256'][:12])
review={'slug':P.name,'masterSha256':d['files']['captioned']['sha256'],'version':d['masterVersion'],'checkedAt':now,'request':'7편에서 카메라 2개도 위치를 보여서 더 이해하기 쉽게 영상 만들어줘~',
 'visual':{'rangeFrames':[415,1166],'rangeSeconds':[415/60,1166/60],'changes':['Observer-only meshes at player and portal optical centres','Actual viewing directions and truncated view-cone guides','Numbered cyan/yellow labels anchored by projected readback','Large overhead view with synchronized player inset','Heading raised to clear the camera at the beginning of the range','Static header held across the revised range to eliminate first-frame image decoding flash; future renders preload both headers'],
 'directInspection':'Native preview and final camera/screen cue frames, mobile contact sheets, and both changed joins inspected. Unchanged v2 visual evidence reused.',
 'browserPlayback':{'source':'output/shorts-portal-seamless-traversal/shorts-portal-seamless-traversal.v5.captioned.mp4','durationSeconds':61.1,'decodedWidth':1080,'decodedHeight':1920,'playingObserved':True,'sampledAtSeconds':[6.85,12],'displayWidthPixels':375,'scope':'Playback metadata and sampled moving screenshot; not continuous human viewing or listening.'},
 'qaIndex':str((qa/'index.json').relative_to(R)).replace('\\','/'),'cameraMathEvidence':'production/local/capture-full-cameras-v3/camera-verification.json','spliceEvidence':'production/local/motion-cameras-v4-stable-header-full-execution.json'},
 'audio':{'changed':False,'identicalEncodedAacToV2':True,'aacHash':d['technicalChecks']['aacHash'],'priorEvidence':'production/local/camera-guides-v3/review-ledger.json','humanWholeListening':False},
 'preservation':{'priorMaster':old['files']['captioned'],'oldFileHashVerified':True,'sixthAndFiveScheduledVideosChanged':False,'youtubeChanged':False,'driveChanged':False},
 'humanReview':'pending','remaining':['User final viewing of the new camera explanation; existing final whole-listening status remains pending.']}
save(P/'production/review-ledger.json',review)
plan=read(P/'planning/production-plan.json');plan['cameraGuidePlan']['result']='Completed in final-v5; heading clearance and first-frame static header corrected after native-frame inspection. Intermediate v3/v4 preserved but not delivery masters.';plan['cameraGuidePlan']['verification']=review['visual'];plan['cameraGuidePlan']['priorMaster']=old['files']['captioned']['sha256']
for s in plan['scenePlan']:
 if s['id'] in ['camera','screen']:s['capture']='capture-full-cameras-v3; actual camera position/direction, observer-only geometry; native 1080-square at60fps';s['annotationReadback']=['playerGuide','portalGuide','playerEye','portalEye','playerForward','portalForward']
save(P/'planning/production-plan.json',plan)
cp=read(P/'production/checkpoint.json');cp.update(reviewLedger='projects/'+P.name+'/production/review-ledger.json',next='Await final human review of exact delivered v5 master; no platform mutation authorized by this revision.',preservedPriorMaster=old['files']['captioned'],updatedAt=now);save(P/'production/checkpoint.json',cp)
cpath=R/'shared/publishing/video-production-control.json';c=read(cpath);a=c['portalTraversalShortsAuthorization'];a.update(status='completed-local-review-ready',fullProductionAuthorized=False,activeSlugs=[],completedAt=now);a['currentRevision'].update(status='completed-local-review-ready',captionedSha256=d['files']['captioned']['sha256'])
for item in a['deliveries']:
 if item['slug']==P.name:item.update(sha256=d['files']['captioned']['sha256'],captioned=d['files']['captioned']['path'],humanReview='pending',version=d['masterVersion'])
save(cpath,c)
wpath=R/'shared/publishing/shorts-worklist.json';w=read(wpath);row=next(x for x in w['rows'] if x['slug']==P.name);row.update(status='local-review-ready',production='complete',review='human-final-review-pending',captionedSha256=d['files']['captioned']['sha256'],revision=project['currentRevision'],updatedAt=now);w['updatedAt']=now;save(wpath,w)
print(json.dumps({'captioned':d['files']['captioned']['path'],'sha256':d['files']['captioned']['sha256'],'preservedAudio':True,'humanReview':'pending'},ensure_ascii=False))
