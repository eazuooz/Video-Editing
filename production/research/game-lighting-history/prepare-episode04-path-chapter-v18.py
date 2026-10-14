"""Preserve native title-card rejection and prepare the path chapter CPU pair."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math, psutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
proof=lambda p:{'path':rel(p),'sha256':sha(p)}
def write(p,j):
 assert not p.exists(),f'Preserve earlier record: {p}'
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
gates={k:False for k in ['allFinalPixelsReviewed','allMovingPixelsReviewed','causalFlowApproved','finalMixedAsrApproved','wholeEpisode60to40Approved','qaApproved','collected','uploaded']}
boards=[];samples=[];executions=[]
for version,expected,sid in [(17,13,80423),(18,9,54114)]:
 ep=ROOT/f'production/research/game-lighting-history/local/episode04-path-native-v{version}/execution.json'
 e=read(ep);assert e['status']=='samples-ready' and len(e['samples'])==expected
 assert len(e['commands'])==expected and all(c['exitCode']==0 for c in e['commands'])
 try:alive=abs(psutil.Process(e['worker']['pid']).create_time()-e['worker']['createTime'])<.01
 except psutil.NoSuchProcess:alive=False
 assert not alive,'Owned extraction worker still alive'
 sessionPath=ep.with_name('session.json')
 if not sessionPath.exists():
  write(sessionPath,{'sessionId':sid,'worker':e['worker'],'execution':rel(ep),'closed':True,'exitCode':0,'unifiedExecExitObserved':True,'endedObservedAt':stamp(),'cpuThreads':2,'gpuJobs':0})
 else:
  s=read(sessionPath);assert s['sessionId']==sid and s['closed'] and s['exitCode']==0 and s['unifiedExecExitObserved']
 executions.append(proof(ep))
 for b in e['boards']:
  assert sha(ROOT/b['path'])==b['sha256'];boards.append({**b,'directlyRead':True,'reviewedAt':stamp()})
 for s in e['samples']:
  assert sha(ROOT/s['path'])==s['sha256'];samples.append({**s,'directlyReadOnBoard':True})
assert len(samples)==22 and len(boards)==7
nativeReview=P/'path-native-direct-review-v18.json'
source={'path':'production/research/game-lighting-history/local/episode04-native-v1/cyberpunk-ray-reconstruction.mp4','sha256':'25a4f9f3d7c2cd335df4128687582e444b61c7d119b2af5493b80003b49ac2da','url':'https://www.youtube.com/watch?v=oMCC9TgsCDY'}
assert sha(ROOT/source['path'])==source['sha256']
write(nativeReview,{'reviewedAt':stamp(),'executions':executions,'boards':boards,'samples':samples,'source':source,
 'all22SamplesDirectlyRead':True,'all7BoardsDirectlyRead':True,
 'rejectedCandidate':{'localInterval':[10,26.96],'approved':False,'reason':'Direct13/14/15s samples contain the Phantom Liberty Full Ray Tracing title card; do not count this as game action or silently reuse the earlier broad-sample assumption.'},
 'chosenLocalIntervals':[[8,12],[16,28.96]],
 'findings':['8-9.5s interior with figures and ceiling light,10-11s illuminated pyramid,11.966s neon wall retain RTX ON. This is a short source montage, not an uninterrupted single-camera comparison.',
 '16s wet floor and people show RTX ON;18s RTX OFF;20s split wipe;22s RTX ON. Same scene objects and floor reflections are the observation target; do not infer raw sample count or isolated performance.',
 '24-28.933s red neon building/stone figure alternates comparison wipe,RTX OFF26s and RTX ON27-28.933s. No FPS counter, frame-generation card, logo, presenter or desktop in the selected sample points.',
 '13-15s title card is excluded by a source cut between12s and16s. No loop, slowdown or source sound; preserve original narration and show original feature tags.',
 'These are sparse direct source samples. Normal-speed continuous review, source-frame-wide title-card exclusion and final caption clearance remain separate gates.'],
 'sampledNativeContentSuitable':True,'allMovingFramesReviewed':False,'allFinalPixelsReviewed':False,'newGitImages':0})
selectionPath=P/'clean-source-selection-v8.json';selection=read(selectionPath)
assemblyPath=P/'additive-unmixed-review-assembly-v2.json';assembly=read(assemblyPath)
captionPath=P/'local/caption-word-draft-v2.json';caption=read(captionPath)
entries=[e for e in assembly['entries'] if e['start']>=548.39 and e['end']<=730.89]
assert len(entries)==12 and entries[0]['id']=='original-19-1' and entries[-1]['id']=='original-19-9'
start=547.68;end=entries[-1]['end'];rf=lambda t:math.floor(t*60+.5)
ff,lf=rf(start),rf(end);N=lf-ff;assert(ff,lf,N)==(32861,43853,10992)
byId={s['id']:s for s in selection['selected']};cuts=[]
def add(id,a,b,kind,**kw):
 f,t=rf(a),rf(b)
 c={'id':id,'from':round(a-start,9),'to':round(b-start,9),'fromFrame':f-ff,'toFrame':t-ff,'globalFromFrame':f,'globalToFrame':t,'frames':t-f,'kind':kind,**kw}
 assert c['frames']>0
 if cuts:assert cuts[-1]['toFrame']==c['fromFrame']
 cuts.append(c)
previous=read(P/'mobile-chapter-review-build-v16.json')['outputs'][0]
add('preserved-original-silent-boundary',start,entries[0]['start'],'explanation',path=previous['path'],sha256=previous['sha256'],sourceStart=(previous['frames']-1)/60,freezeFrameOnly=True,reason='Original0.72s PCM silence; held last mobile explanation frame')
for e in entries:
 if e['id']=='10-guide-path-game':
  for suffix,a,b,ss,se in [('feature-label',e['start'],e['start']+4,8,12),('wet-surface-comparison',e['start']+4,e['end'],16,28.96)]:
   add(e['id']+'-'+suffix,a,b,'actual',entryId=e['id'],**source,sourceStart=ss,sourceEnd=se,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,
    label='Cyberpunk 2077 · 공식 비교 시연 · 2023',secondaryLabel='RTX 기능 표기 확인 · 표본 수·단독 성능 실측 아님',sourceSampleReview=proof(nativeReview),allMovingFramesReviewed=False,sourceTitleCardExcludedByCut=True)
 else:
  m=byId[e['id']];span=m['mediaSpanFrames'];assert m['sourceSamplePixelsApproved']
  assert abs((rf(e['end'])-rf(e['start']))-m['frames'])<=1
  add(e['id'],e['start'],e['end'],'explanation',entryId=e['id'],path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,sourceSampleReview=m['sourceSampleReview'],verification=m['verification'],shiftUpPixels=60,padRoundingAtMostOneFrame=True,completeModelMeaningRetained=True)
assert len(cuts)==14 and cuts[-1]['toFrame']==N
ids={e['id'] for e in entries};cues=[]
for c in caption['cues']:
 if c['entryId'] not in ids:continue
 f,t=round(c['from']-start,9),round(c['to']-start,9)
 cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':f,'to':t,'firstFrame':math.ceil(f*60-1e-7),'exclusiveEndFrame':math.ceil(t*60-1e-7),'sourceGlobalSeconds':[c['from'],c['to']],'encodedPixelsReviewed':False})
assert cues[0]['id']==124 and all(b['id']==a['id']+1 for a,b in zip(cues,cues[1:]))
audio={**assembly['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
assert(audio['firstSample'],audio['exclusiveEndSample'],audio['samplesInChapter'])==(13144320,17541121,4396801)
actual=sum(c['frames'] for c in cuts if c['kind']=='actual')
plan={'preparedAt':stamp(),'scope':'Path tracing chapter review pair; preserved12 KO/EN paragraphs and PCM, source title-card exclusion; final episode allocation pending',
 'selection':proof(selectionPath),'assembly':proof(assemblyPath),'captionDraft':proof(captionPath),'nativeReview':proof(nativeReview),'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,
 'totals':{'frames':N,'globalFromFrame':ff,'globalToFrame':lf,'videoSeconds':N/60,'pcmSeconds':audio['secondsInChapter'],'roundingErrorFrames':N-audio['secondsInChapter']*60,'actualFrames':actual,'explanationFrames':N-actual,'body60to40Approved':False},
 'causalPlan':['2023 Overdrive preview conditions → read source RTX tags and wet-floor/object comparison → camera/surface/material sampled path; no all-paths claim.',
 'Directional contribution and probability density → independent two-direction2/8 mean5 example →0.8/0.2 corrected contributions both5 in this special example.',
 'Light and BSDF strategies and qualified MIS weights → stochastic survival0.8 compensation1.25 → expectation1, not exactly every fifth path, variance caveat.',
 'Probabilistic weighting versus fixed-bounce truncation bias → independent-sample1/sqrt(N) relation and temporal-correlation limits → allocation/reuse/reconstruction transition.'],
 'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,**gates,'humanWholeListening':'pending',
 'next':'SingleCPU2 chapter build; preserve complete original AAC in both outputs, whole decode/PTS verification, then all encoded cue/cut/source samples. Whole episode allocation/mix/moving review remains pending.'}
pp=P/'path-chapter-review-plan-v18.json';write(pp,plan)
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j['episode04PathNativeDirectReviewV18']={'path':rel(nativeReview),'sha256':sha(nativeReview),'samples':22,'boards':7,'rejectedCandidateTitleCard':[13,15],'chosenLocalIntervals':[[8,12],[16,28.96]],'allMovingFramesReviewed':False}
j['episode04PathChapterV18']={'plan':rel(pp),'status':'prepared-only','entries':12,'cuts':14,'cues':len(cues),'frames':N,**gates}
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':plan['next']};j['updatedAt']=stamp()
tmp=cp.with_suffix('.path-plan-v18.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({'plan':rel(pp),'entries':len(entries),'cuts':len(cuts),'cueCount':len(cues),'cueRange':[cues[0]['id'],cues[-1]['id']],'frames':N,'actualFrames':actual,'newMediaCreated':0,'finalApproved':False}))
