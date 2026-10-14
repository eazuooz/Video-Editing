"""Preserve completed PCM/spatial renders; compose observed exposure/focus cuts."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math, psutil

R=Path(__file__).resolve().parents[3]; P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
rf=lambda t:math.floor(t*60+.5)
proof=lambda p:{'path':rel(p),'sha256':sha(p)}
def write(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')

sessions=[]
for folder,ep,sid in [('episode04-dlss-chapter-v33',P/'dlss-chapter-review-execution-v33.json',82642),('episode04-dlss-encoded-v33',R/'production/research/game-lighting-history/local/episode04-dlss-encoded-v33/execution.json',38376)]:
 s=read(ep); w=s['worker']; assert s['active'] is None and all(c['exitCode']==0 for c in s['commands'])
 try:assert abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01,'Original worker remains alive'
 except psutil.NoSuchProcess:pass
 dst=R/'production/research/game-lighting-history/local'/folder/'session.json'
 write(dst,{'sessionId':sid,'worker':w,'terminalCompletionObserved':True,'exitCode':0,'completedAt':s['endedAt'],'verifiedAt':now(),'execution':proof(ep),'originalWorkerAlive':False})
 sessions.append(proof(dst))

xp=R/'production/research/game-lighting-history/local/episode04-dlss-encoded-v33/execution.json'; ex=read(xp)
assert(len(ex['items']),len(ex['boards']))==(43,12)
boards=[]
for b in ex['boards']:
 assert sha(R/b['path'])==b['sha256']
 boards.append({**b,'directlyViewed':True,'reviewedAt':now()})
dr=P/'dlss-encoded-direct-review-v33.json'
write(dr,{'reviewedAt':now(),'scope':'43 changed-cut/cue261/262 samples on12 boards directly read; other8 encoded clean cuts preserved byte-identically with earlier239-sample review. This is sampled clearance, not continuous/final approval.','build':proof(P/'dlss-chapter-review-build-v33.json'),'extraction':proof(xp),'sessions':sessions,'boards':boards,'sampleCount':43,'allPlannedSamplesDirectlyViewed':True,'sampledCaptionClearanceApproved':True,'findings':['Both DLSS4 and DLSS4.5 feature labels, comparison reticles and camera motion remain visible above the fixed caption box after native framing repair.','Cue261/262 first/middle/last plus before/after show readable maximum2-line text at960,970.','The source labels distinguish display-frame generation from simulation/ray work or measured input latency.','The prior artist-control model-template button limitation remains recorded; it is not used as evidence for the upper-control claim.'],'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'uploaded':False,'newTts':0,'newGitImages':0})

nx=R/'production/research/game-lighting-history/local/episode04-postprocess-native-v32/execution.json'; native=read(nx)
assert(len(native['samples']),len(native['boards']))==(45,13)
nb=[]
for b in native['boards']:
 assert sha(R/b['path'])==b['sha256']
 nb.append({**b,'directlyRead':True,'reviewedAt':now(),'reviewContinuity':'All13 native boards read in preceding context; exposure09/debug03/normal09 additionally read for framing coordinates in current context.'})
nr=P/'postprocess-native-direct-review-v34.json'
write(nr,{'reviewedAt':now(),'extraction':proof(nx),'sampleCount':45,'boards':nb,'allPlannedSamplesDirectlyRead':True,'observations':[{'source':'exposure','reviewedRange':[1570,1618],'chosenRange':[1586,1602.88],'visibleAction':'GlobalPostProcess3 AutoExposure MinBrightness/MaxBrightness/Bias controls change while camera also moves around the cube stack. Min/max reach1/1 and later return.','limits':'No light rearrangement observed; camera and parameters change, so this is not a strict fixed-camera photometric A/B or proof that every internal lighting computation was identical.'},{'source':'focus-debug','reviewedRange':[2330,2336],'chosenRange':[2330,2336.02],'visibleAction':'Blue far, green near and black focus legend is visible. FocalDistance remains250; NearTransitionRegion1467.89→733.94→0 changes the green region.','limits':'Do not claim FocalDistance changes to1259 in this interval.'},{'source':'focus-normal','reviewedRange':[2369,2381],'chosenRange':[2369,2380.1],'visibleAction':'FocalDistance1259.073364 and NearTransition366.972473 are visible; camera moves and the near right white cube appears blurred. MaxBokehSize changes8→8.889734→10.348624.','limits':'This is a separate moment/settings from debug, not an identical-setting on/off comparison. Scale0.2 through2380;0.310092 at2381 is outside chosen cut.'}],'presenterInChosenSamples':False,'nativeContinuousPlaybackReviewed':False,'allMovingPixelsReviewed':False,'finalApproved':False,'newGitImages':0})

ap=P/'additive-unmixed-review-assembly-v2.json'; sp=P/'clean-source-selection-v8.json'; cp=P/'local/caption-word-draft-v2.json'
a=read(ap); selected=read(sp); byId={m['id']:m for m in selected['selected']}
ids=['original-22p-1','20-pre-display-transform','original-22p-2','21-guide-post-exposure','original-22p-3','original-22p-4','22-guide-post-focus','original-22p-5','original-22p-6']
entries=[e for e in a['entries'] if e['id'] in ids]; assert[e['id'] for e in entries]==ids
priorPath=P/'dlss-chapter-review-build-v33.json'; prior=read(priorPath)
assert sha(R/prior['outputs'][0]['path'])==prior['outputs'][0]['sha256']
start=entries[0]['start']-.72; end=entries[-1]['end']; ff,lf=rf(start),rf(end); N=lf-ff; cuts=[]
def add(id,x,y,kind,**kw):
 f,t=rf(x)-ff,rf(y)-ff; assert t>f
 if cuts:assert cuts[-1]['toFrame']==f
 cuts.append({'id':id,'from':round(x-start,9),'to':round(y-start,9),'fromFrame':f,'toFrame':t,'frames':t-f,'kind':kind,**kw})
def model(e):
 m=byId[e['id']]; span=m['mediaSpanFrames']; assert abs(rf(e['end'])-rf(e['start'])-(span[1]-span[0]))<=1
 add(e['id'],e['start'],e['end'],'explanation',entryId=e['id'],path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,verification=m['verification'],shiftUpPixels=60)
po=prior['outputs'][0]
add('preserved-original-silent-boundary',start,entries[0]['start'],'explanation',path=po['path'],sha256=po['sha256'],sourceStart=(po['frames']-1)/60,freezeFrameOnly=True)
path='production/research/game-lighting-history/local/epic-post-processing.mp4'; digest='d4c422af11f1242fb9d1ac8fd233ddd5638dbfc4be6a93417e50d826f92ea723'; assert sha(R/path)==digest
base={'path':path,'sha256':digest,'normalSpeed':True,'loop':False,'slowdown':False,'sourceAudio':False,'nativeShiftUpPixels':120,'sourceSampleReview':proof(nr)}
for e in entries:
 if e['id']=='21-guide-post-exposure':
  add(e['id'],e['start'],e['end'],'actual',entryId=e['id'],sourceStart=1586,label='Unreal Engine · 노출 설정 시연 · 2017',secondaryLabel='설정과 카메라가 함께 변하는 관찰 · 고정 조건 A/B 아님',annotation={'type':'native-light-surface','screenIntervals':[{'from':3,'to':12,'boxes':[[1392,466,410,252,'0xE95757']]}]},**base)
 elif e['id']=='22-guide-post-focus':
  split=e['start']+6.02
  add(e['id']+'-debug',e['start'],split,'actual',entryId=e['id'],sourceStart=2330,label='Unreal Engine · 초점 영역 디버그 · 2017',secondaryLabel='파랑: 멀리 · 초록: 가까이 · 검정: 초점 영역',labelX=700,annotation={'type':'native-light-surface','screenIntervals':[{'from':0,'to':6.02,'boxes':[[30,127,575,49,'0xE95757']]}]},**base)
  add(e['id']+'-normal',split,e['end'],'actual',entryId=e['id'],sourceStart=2369,label='Unreal Engine · 일반 화면의 초점·번짐 · 2017',secondaryLabel='앞 디버그와 별도 설정·카메라 구간 · 동일 조건 A/B 아님',labelX=700,annotation={'type':'native-light-surface','screenIntervals':[{'from':0,'to':10.5,'boxes':[[1290,566,445,225,'0xE95757']]}]},**base)
 else:model(e)
assert cuts[-1]['toFrame']==N
cues=[]
for c in read(cp)['cues']:
 if c['entryId'] in ids:
  x,y=round(c['from']-start,9),round(c['to']-start,9)
  cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':x,'to':y,'firstFrame':math.ceil(x*60-1e-7),'exclusiveEndFrame':math.ceil(y*60-1e-7)})
audio={**a['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
plan={'preparedAt':now(),'scope':'Preserved9 postprocess paragraphs plus observed exposure/focus process, chapter review only; exact final60:40/split pending.','selection':proof(sp),'assembly':proof(ap),'captionDraft':proof(cp),'nativeReview':proof(nr),'priorBuild':proof(priorPath),'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,'totals':{'frames':N,'globalFromFrame':ff,'globalToFrame':lf,'videoSeconds':N/60,'pcmSeconds':audio['secondsInChapter'],'roundingErrorFrames':N-audio['secondsInChapter']*60,'actualFrames':sum(c['frames'] for c in cuts if c['kind']=='actual'),'explanationFrames':sum(c['frames'] for c in cuts if c['kind']=='explanation'),'body60to40Approved':False},'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,'causalPlan':['Computed light versus display transformation.','Linear2 × exposure0.5 =1 before a separate nonlinear tone curve.','Observe actual exposure controls; distinguish camera changes from a controlled A/B.','Bloom is image spread, not evidence of bounced light.','Depth-of-field debug legend then separate ordinary blur shot; explain different settings rather than claiming identical toggled comparison.','Input/output color transformations connect to RenderDoc resource inspection.'],'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'newTts':0,'newGitImages':0}
pp=P/'postprocess-chapter-review-plan-v34.json'; write(pp,plan)
src=R/'production/research/game-lighting-history/build-episode04-dlss-chapter-v31.py'
s=src.read_text('utf-8').replace('dlss','postprocess').replace('Dlss','Postprocess').replace('v31','v34').replace('V31','V34')
s=s.replace("N==6970 and len(plan['cuts'])==9 and len(plan['entries'])==7 and len(plan['cues'])==24",f"N=={N} and len(plan['cuts'])=={len(cuts)} and len(plan['entries'])==9 and len(plan['cues'])=={len(cues)}")
s=s.replace("'total':9",f"'total':{len(cuts)}").replace("'captionCues':24",f"'captionCues':{len(cues)}")
s=s.replace("  if c.get('freezeFrameOnly'):","  if c.get('nativeShiftUpPixels'):\n   shift=c['nativeShiftUpPixels'];vf+=[f'crop=1920:{1080-shift}:0:{shift}','pad=1920:1080:0:0:black']\n  if c.get('freezeFrameOnly'):")
s=s.replace("label(c['label'],32,24", "label(c['label'],c.get('labelX',32),24").replace("label(c['secondaryLabel'],32,66", "label(c['secondaryLabel'],c.get('labelX',32),66")
dest=src.with_name('build-episode04-postprocess-chapter-v34.py'); assert not dest.exists(); compile(s,str(dest),'exec');dest.write_text(s,'utf-8')
src=R/'production/research/game-lighting-history/extract-episode04-dlss-encoded-v31.py'
s=src.read_text('utf-8').replace('dlss','postprocess').replace('v31','v34').replace('V31','V34')
s=s.replace('N==6970',f'N=={N}').replace('len(metrics)==24',f'len(metrics)=={len(cues)}')
dest=src.with_name('extract-episode04-postprocess-encoded-v34.py');assert not dest.exists();compile(s,str(dest),'exec');dest.write_text(s,'utf-8')
cpPath=R/'production/research/game-lighting-history/checkpoint.json';j=read(cpPath)
j['episode04DlssEncodedDirectReviewV33']={**proof(dr),'sampleCount':43,'boards':12,'sampledCaptionClearanceApproved':True,'allFinalPixelsReviewed':False}
j['episode04PostprocessNativeDirectReviewV34']={**proof(nr),'sampleCount':45,'boards':13,'allMovingPixelsReviewed':False}
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':'Run one CPU2 postprocess review composition, then encoded cue/cut/annotation samples; no GPU/TTS.'}
j['updatedAt']=now();tmp=cpPath.with_suffix('.postprocess-v34.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cpPath)
print(json.dumps({'plan':rel(pp),'frames':N,'cuts':len(cuts),'cues':len(cues),'actualFrames':plan['totals']['actualFrames'],'pcmSamples':audio['samplesInChapter'],'newTts':0,'newGitImages':0}))
