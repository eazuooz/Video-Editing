"""Publish only internally verified D25/D26 files to the existing local collector."""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[4]
M=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def logical(p):return str(Path(p).relative_to(R)).replace('\\','/')
ap=argparse.ArgumentParser();ap.add_argument('--slug',required=True,choices=['limited-color-world','computer-controlled-players']);ap.add_argument('--version',default='v5');a=ap.parse_args()
project=R/'projects'/a.slug;rev=project/'production/unity-visual-v2';local=project/'production/local/unity-visual-v2';media=M/a.slug;out=media/('composite-'+a.version)
assert a.version.isalnum()
control=read(R/'shared/publishing/video-production-control.json')['finiteBatchAuthorizations']['design-25-30-unity-v2-20261028']
assert control['localProductionAuthorized'] and a.slug in control['slugs']
v=read(rev/'visual-plan.json');structure=read(out/'structural-verification.json');pixels=read(rev/'visual-review.json');build=read(out/'pair-build.json')
assert structure['status']=='pass' and structure['originalAacIdentical'] and structure['originalCaptionsIdentical']
assert pixels['status']=='pass' and pixels['masterSha256']==build['outputs']['captioned']['sha256']
assert set(pixels['reviewedChangedCutIds'])=={c['id'] for c in v['cuts'] if c['operation']=='replace-explanation-visual'}
for k,p in build['outputs'].items():assert sha(p['path'])==p['sha256']==structure['outputs'][k]['sha256']
assert local.is_dir() and local.resolve()==media.resolve(),'Create only the approved project junction before finalizing.'
manifest=read(project/'project.json');now=datetime.now(timezone.utc).isoformat()
backup=rev/'baseline-manifest.json'
if not backup.exists():write(backup,manifest)
else:assert read(backup)['revision']=='batch-v1'
oldcollection=project/'production/delivery-output.json'
if oldcollection.exists() and not (rev/'baseline-delivery-output.json').exists():write(rev/'baseline-delivery-output.json',read(oldcollection))
prefix=logical(local/('composite-'+a.version));delivery=logical(local/'delivery');index=delivery+'/output/'+a.slug+'/index.html'
files={'videoBurnedCaptions':prefix+'/'+a.slug+'.captioned.mp4','videoClean':prefix+'/'+a.slug+'.clean.mp4','captionsKo':prefix+'/'+a.slug+'.ko.srt','captionsEn':prefix+'/'+a.slug+'.en.srt'}
manifest['revision']='unity-visual-v2';manifest['status']='local-review-ready';manifest['updatedAt']=now
manifest['currentRevision']={'id':'unity-visual-v2','status':'local-review-ready','productionComplete':True,'humanFinalReview':'pending','automaticNextVideo':False,'baseRevision':'batch-v1','visualOnly':True}
manifest['paths'].update(files)
manifest['paths'].update({'checkpoint':logical(rev/'checkpoint.json'),'reviewStatus':logical(rev/'review-status.json'),'visualRevisionPlan':logical(rev/'visual-plan.json'),'deliveryIndex':index,'outputDirectory':delivery+'/output/'+a.slug})
manifest['delivery'].update({'localStorageRoot':delivery,'userReviewClaimed':False})
manifest['finalRender']={'status':'complete-local-review-ready','captionedSha256':build['outputs']['captioned']['sha256'],'durationSeconds':structure['durationSeconds'],'openItems':['새 Unity 설명 화면을 포함한 전체 영상의 최종 검수를 기다립니다.'],'originalAacPreserved':True,'originalCaptionsPreserved':True,'visualRevisionPlan':logical(rev/'visual-plan.json')}
manifest['localFinalReview']={'index':index,'files':{key:delivery+'/output/'+a.slug+'/'+a.slug+'.'+key for key in ['captioned.mp4','clean.mp4','ko.srt','en.srt']},'sha256':{'captioned.mp4':build['outputs']['captioned']['sha256'],'clean.mp4':build['outputs']['clean']['sha256'],'ko.srt':sha(out/(a.slug+'.ko.srt')),'en.srt':sha(out/(a.slug+'.en.srt'))},'durationSeconds':structure['durationSeconds'],'actualUserViewed':False,'humanWholeListening':'pending','internalQa':'complete','reviewRecord':logical(rev/'review-status.json')}
manifest['approvals'].update({'render':True,'qa':True,'collected':False,'uploaded':False})
manifest['publishReady']=False
manifest['audio']['visualRevisionPreservation']='Original complete AAC stream copied byte-for-byte; narration, game sounds, Nimbus and ducking unchanged.'
write(project/'project.json',manifest)
subprocess.run(['node','scripts/collect-video-output.cjs',a.slug],cwd=R,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
collection=read(oldcollection);assert collection['directory']==delivery+'/output/'+a.slug
for f in collection['files']:assert sha(R/collection['directory']/f['name'])==f['sha256']
manifest=read(project/'project.json');manifest['approvals']['collected']=True;write(project/'project.json',manifest)
review={'schemaVersion':1,'slug':a.slug,'revision':'unity-visual-v2','status':'local-review-ready','stage':'local-final-review','fourOutputsVerified':True,'captionedSha256':build['outputs']['captioned']['sha256'],'durationSeconds':structure['durationSeconds'],'localFiles':files,'localOutputDirectory':collection['directory'],'localIndex':index,'technicalSummary':'Complete FHD60 pair decoded; all video frames/PTS verified; original AAC packets and KO/EN SRT bytes identical. Replaced explanation clips only; original cut clocks and actual60/explanation40 retained.','visualSummary':pixels,'audioSummary':{'changed':False,'evidence':prefix+'/structural-verification.json','priorReview':'projects/'+a.slug+'/production/batch-v1/review-status.json','humanWholeListening':'pending'},'humanReview':'pending','humanListening':'pending','uploadAuthorized':False,'schedulingAuthorized':False,'evidence':{'structural':prefix+'/structural-verification.json','visual':logical(rev/'visual-review.json'),'collection':logical(oldcollection)},'updatedAt':now}
review.update({'reviewFocus':['Unity 설명 화면의 이해도와 기존 게임 영상으로 이어지는 연결','원래 내레이션·배경음악·자막이 그대로 유지되는지'],'humanWholeReview':'pending','nativeReplacedCutCount':len(pixels['reviewedChangedCutIds']),'savedScenePaths':[c['scenePath'] for c in v['cuts'] if c['operation']=='replace-explanation-visual']})
write(rev/'review-status.json',review)
checkpoint={'schemaVersion':1,'slug':a.slug,'revision':'unity-visual-v2','stage':'local-final-review','status':'local-review-ready','updatedAt':now,'jobs':[],'nextAction':'Local human final review only; no upload or automatic next video authorized.','captionedSha256':review['captionedSha256'],'reviewStatus':logical(rev/'review-status.json'),'localOutputDirectory':collection['directory'],'actualHumanListening':False,'actualHumanViewingNewVersion':False,'uploadAuthorized':False,'automaticNextVideo':False,'preservedBaseRevision':'batch-v1','visualRevisionPlan':logical(rev/'visual-plan.json'),'originalAacIdentical':True,'originalKoEnCaptionsIdentical':True,'totalFrames':structure['totalFrames'],'actualFrames':structure['actualFrames'],'explanationFrames':structure['explanationFrames']}
write(rev/'checkpoint.json',checkpoint)
prepared=read(out/'preparation.json')
for entry in prepared['entries']:
 if 'nativeCapture' not in entry:continue
 c=next(c for c in v['cuts'] if c['id']==entry['id']);c['nativeCapture']=entry['nativeCapture']
 c['nativeCapture']['videoPath']=entry['path'];c['nativeCapture']['videoSha256']=entry['sha256']
 c['sceneSaveStatus']='saved-full-native-capture-verified';c.pop('sceneSha256AtPreflight',None)
 c['sceneSha256Observed']=sha(R/c['scenePath']);c['finalCaptionedVisualReview']='pass'
v['status']='local-review-ready';v['openChecks']=['Human final review of the new visual version.'];v['finalFiles']=files;v['finalVerification']=review['evidence'];write(rev/'visual-plan.json',v)
print(json.dumps({'slug':a.slug,'index':index,'captionedSha256':review['captionedSha256'],'status':'local-review-ready'},ensure_ascii=False))
