"""Record only this Short's verified local delivery; never imply human review."""
from pathlib import Path
import json,hashlib,datetime
from audio_revision import P,R,L as A,read,guard,REVISION
guard();L=P/'production/local/final-reviewed'
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();pair=read(L/'pair-build.json');checks=read(L/'integrity.json');timing=read(P/'production/visual-timing.json');assert checks['status']=='pass'
master={'path':rel(L/'captioned.mp4'),'sha256':sha(L/'captioned.mp4'),'revision':REVISION}
assert master['sha256']==pair['captioned']
assert read(L/'visual-review.json')['masterSha256']==master['sha256']
assert read(A/'mix-asr-review.json')['inputSha256']==sha(A/'final-mix.m4a')
project=read(P/'project.json');project.update(status='ready-for-local-final-review',updatedAt=now,publishReady=False)
project['video'].update(frames=timing['frames'],durationSeconds=timing['durationSeconds'])
project['finalRender']={'revision':REVISION,'sha256':master['sha256'],'technicalChecks':'passed','openItems':['Actual human final viewing and full listening pending.']}
project['delivery'].update(captioned=f'output/{P.name}/{P.name}.captioned.mp4',index=f'output/{P.name}/index.html')
save(P/'project.json',project)
plan=read(P/'planning/production-plan.json');plan.update(status='local-final-review-ready',finalMaster=master,realizedTeachingBeats=timing)
plan['measuredShares']={'gameSeconds':timing['sections'][0]['end'],'totalSeconds':timing['durationSeconds'],'gameFraction':timing['sections'][0]['end']/timing['durationSeconds'],'contract':'Technical Shorts: one complete demonstrated mechanism; no padded60:40 quota.'}
plan['capture']={'editor':'6000.6.0f1','driver':'Microsoft Basic Render Driver / CPU WARP','pipeline':'Built-in explicit custom shader in isolated project','project':'unity/VideoEditing','mainProjectPipeline':'URP17.6.0 unchanged; live URP runtime not certified','nativeDimensions':[1080,1080],'masterDimensions':[1080,1920],'fps':60,'frames':timing['frames'],'evidence':rel(P/'production/local/capture-full/success.json')}
plan['sceneSaveStatus']='eight-independent-editable-scenes-exist';plan['humanFinalReview']='pending';save(P/'planning/production-plan.json',plan)
plan['unity']['scenes']=[rel(p) for p in sorted((R/'unity/VideoEditing/Assets/VideoScenes'/P.name/'Scenes').glob('*.unity'))]
assert len(plan['unity']['scenes'])==8
for i,scene in enumerate(plan['scenes']):scene['narrationParagraphIndices']=[i] if i<7 else [7,8]
plan['audioRepair']={'revision':'audio-r2','reason':'Initial last paragraph had sustained low source speech level. Split only that paragraph into two meaningful takes in the same approved voice; retain first seven raw takes and natural speed.','voiceSha256':sha(A/'voice/interior.wav'),'mixSha256':sha(A/'final-mix.m4a'),'humanListening':'pending'}
plan['resourceDecision']={'choice':'CPU-only Qwen and CPU WARP Unity capture; CPU Motion Canvas composition','reason':'Other authorized work was using the GPU. No game, editor or foreign render was closed or interrupted.','gpuUsedByThisRevision':False}
save(P/'planning/production-plan.json',plan)
sources=read(P/'sources/sources.json');sources['sources'][2]['sourceRange']=[70,70+timing['sections'][0]['end']]
sources['music']['sha256']=sha(R/sources['music']['path']);sources['assets'][0]['files']=[{'path':rel(R/'shared/assets/branding/cat-reactions-v1'/(n+'.png')),'sha256':sha(R/'shared/assets/branding/cat-reactions-v1'/(n+'.png'))} for n in ['puzzled','realize','relief']];save(P/'sources/sources.json',sources)
ledger=read(P/'production/review-ledger.json');ledger.update(updatedAt=now,finalMaster=master)
ledger['checks']=[x for x in ledger['checks'] if x['id']=='source-format-rights']+[
 {'id':'native-unity-shader','status':'pass','evidence':rel(P/'production/local/capture-full/success.json')},
 {'id':'audio-video-integrity','status':'pass','evidence':rel(L/'integrity.json')},
 {'id':'current-master-technical-review','status':'recorded','evidence':rel(P/'production/technical-review.json'),'humanApprovalClaimed':False},
 {'id':'visual-cue-mobile-review','status':'recorded-separately','evidence':rel(L/'visual-review.json')},
 {'id':'voice-and-mix-asr','status':'technical-checked','evidence':rel(A/'asr-reconciliation.json'),'humanListeningClaimed':False},
 {'id':'final-mix-full-input-asr','status':'technical-checked','evidence':rel(A/'mix-asr-review.json'),'humanListeningClaimed':False},
 {'id':'audio-continuity','status':'technical-checked','evidence':rel(A/'audio-continuity.json')},
 {'id':'human-full-listening','status':'pending'}, {'id':'human-final-video-review','status':'pending','sha256':master['sha256']}]
ledger['platform']={'youtube':'not-uploaded','drive':'not-requested','nextVideoStarted':False};save(P/'production/review-ledger.json',ledger)
cp=read(P/'production/checkpoint.json');cp.update(stage='local-final-review-ready',nextAction='Human final viewing/listening of this exact local master. No platform mutation in the daily heartbeat.',updatedAt=now,finalMaster=master,delivery=project['delivery'],humanFinalReview='pending');save(P/'production/checkpoint.json',cp)
daily=R/'shared/publishing/shorts-research/daily-2026-10-24.json';slate=read(daily);slate['status']='awaiting-local-final-review';first=slate['firstProduction'];first.update(status='local-final-review-ready',scriptStatus='finalized-after-independent-footage-review',finalMaster=master,durationSeconds=timing['durationSeconds'],delivery=project['delivery'],requiredNextActions=['Human final viewing/listening of this exact master. Publication requires a separate request after review.'])
first['teachingSequence']=['Independent SimCity recording establishes the many-window city context; not hidden-geometry evidence.','Own Unity implementation shows a flat window rendering room depth.','Observer camera reveals the flat geometry and camera-to-pixel ray.','Nearest virtual-wall intersection selects the texture colour.','Same-camera photo/mapping comparison exposes view dependence.','Per-pixel repetition, flat-furniture limit and modelling-cost conclusion.']
first.pop('noProductionClaims',None);first['boundaries']={'humanFinalReview':'pending','youtube':'not-uploaded','drive':'not-requested','otherVideoStarted':False};save(daily,slate)
wp=R/'shared/publishing/shorts-worklist.json';w=read(wp);rows=[x for x in w['rows'] if x.get('slug')==P.name];assert len(rows)==1
rows[0].update(status='awaiting-local-final-review',production=f"Completed {timing['durationSeconds']:.2f}s1080x1920/60 Unity+MotionCanvas; BGM included",review='user-final-viewing-and-listening-pending',finalMaster=master,delivery=project['delivery']);w['updatedAt']=now;save(wp,w)
print(json.dumps({'master':master,'seconds':timing['durationSeconds'],'humanReview':'pending'}))
