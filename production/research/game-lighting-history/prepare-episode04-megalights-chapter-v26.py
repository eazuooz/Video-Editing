"""Reuse approved PCM/models; separate native observation from visibility teaching."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math, psutil

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
records=[]
for version,sid,count,boards in [(24,83007,39,10),(25,74622,8,2)]:
    ep=ROOT/f'production/research/game-lighting-history/local/episode04-megalights-native-v{version}/execution.json'
    e=read(ep);assert e['status']=='samples-ready' and len(e['samples'])==count and len(e['boards'])==boards
    assert all(c['exitCode']==0 for c in e['commands'])
    try:alive=abs(psutil.Process(e['worker']['pid']).create_time()-e['worker']['createTime'])<.01
    except psutil.NoSuchProcess:alive=False
    assert not alive
    sp=ep.with_name('session.json')
    write(sp,{'sessionId':sid,'worker':e['worker'],'execution':rel(ep),'closed':True,'exitCode':0,'unifiedExecExitObserved':True,'endedObservedAt':stamp(),'cpuThreads':2,'gpuJobs':0})
    bs=[];ss=[]
    for b in e['boards']:
        assert sha(ROOT/b['path'])==b['sha256'];bs.append({**b,'directlyRead':True,'reviewedAt':stamp()})
    for x in e['samples']:
        assert sha(ROOT/x['path'])==x['sha256'];ss.append({**x,'directlyReadOnBoard':True})
    records.append({'version':version,'execution':proof(ep),'session':proof(sp),'boards':bs,'samples':ss})
source={'path':'production/research/game-lighting-history/local/episode04-native-v1/megalights-engine-2024.mp4','sha256':'bd4d52ecb2cdad739c41bbea2494a2a96f9a6ef7a8090dd92d57f06fd08be3a3','url':'https://www.youtube.com/watch?v=hzcsKvrF-Ho'}
assert sha(ROOT/source['path'])==source['sha256']
rp=P/'megalights-native-direct-review-v26.json'
write(rp,{'reviewedAt':stamp(),'records':records,'samples':47,'boards':12,'allSampleBoardsDirectlyRead':True,'source':source,'chosenIntervals':[[49.8,55.8]],
    'officialBrowserObservation':{'tabId':'37','url':source['url'],'title':'MegaLights Demo | Unreal Fest Seattle 2024','verifiedChannel':'Unreal Engine','seek180SecondsContentMatchesLocal34Seconds':True,'exactFrameOffsetVerified':False,'playStartObservedSeconds':195.58118,'rate':1,'laterObservedSeconds':346.721,'laterPaused':True,'allInterveningFramesDirectlyViewed':False},
    'findings':[
        'All39 v24 exact-time samples/10 boards and all8 v25 samples/2 boards were directly read in this continuing task. Original coarse fps1/8 label48 is not exact input timestamp48: use exact -ss samples for decisions.',
        'Local34-49s holds the character and camera nearly stationary. Cloth movement alone does not justify the full18.64s observation guide as meaningful game action. This planned interval is rejected.',
        'Local49.8s is the wide market;50-50.5s camera pans/cuts toward a round kiosk. Lights turn on at51-53s: white canopy bulbs, blue pipe, pink/cyan screen and lit metal/tableware. Local54.5s cuts to adjoining arcade machines;55-55.79s cyan/pink screens and pipe highlights activate. Two adjacent demo shots, not a controlled single-camera occlusion experiment.',
        'Use49.8-55.8s at normal speed for the narrated first sentence. Continue with a clearly labelled explanation diagram when the narration distinguishes light visibility, candidate selection and visibility tests. Do not count that diagram as actual footage.',
        'No ray count, selected-sample count, ground-truth radiance, internal architecture or isolated performance is inferred from brightness. Native light/surface highlights identify visible regions only.',
        'CUA HTTPS official playback corroborates180s market content with local34s and195.58s wide market with local49.8s vicinity. Full offset/frame equality and continuous annotated-render playback remain unapproved.'
    ],'sampledChosenContentSuitable':True,'allMovingFramesReviewed':False,'rightsApproved':False,'finalUseApproved':False,'newGitImages':0})
primary=P/'megalights-primary-version-review-v26.json'
write(primary,{'reviewedAt':stamp(),'scope':'Release-era scope; later docs distinguished from release announcement','sources':[
    {'url':'https://www.unrealengine.com/en-US/blog/unreal-engine-5-5-is-now-available','date':'2024-11-12','directlyRead':True,'finding':'Release announcement names MegaLights experimental. Use that status for2024 narration, despite a later version-labelled documentation header saying Beta.'},
    {'url':'https://dev.epicgames.com/documentation/en-us/unreal-engine/megalights-in-unreal-engine?application_version=5.5','directlyRead':True,'finding':'Stochastic direct-light samples and visibility tests; fixed ray budget is not fixed quality. Complexity and denoising can cause blur/ghosting. Hardware ray-tracing scene responsibilities overlap with Lumen, but direct light is not indirect illumination. Forward rendering is incompatible in the version-labelled page. Later/unversioned5.8 features are not copied into the2024 claim.'}],
    'technicalScopeApprovedForCurrentNarration':True,'allPixelAndMixedAudioApproval':False})
ap=P/'additive-unmixed-review-assembly-v2.json';assembly=read(ap)
sp=P/'clean-source-selection-v8.json';selection=read(sp)
cp=P/'local/caption-word-draft-v2.json';caption=read(cp)
entries=[e for e in assembly['entries'] if e['start']>=853 and e['end']<=961]
assert len(entries)==7 and entries[0]['id']=='original-21m-1' and entries[-1]['id']=='original-21m-6'
start=852.5600833333334;end=entries[-1]['end'];rf=lambda t:math.floor(t*60+.5)
ff,lf=rf(start),rf(end);N=lf-ff;assert(ff,lf,N)==(51154,57610,6456)
byId={s['id']:s for s in selection['selected']};cuts=[]
def add(id,a,b,kind,**kw):
    f,t=rf(a),rf(b);c={'id':id,'from':round(a-start,9),'to':round(b-start,9),'fromFrame':f-ff,'toFrame':t-ff,'globalFromFrame':f,'globalToFrame':t,'frames':t-f,'kind':kind,**kw}
    assert c['frames']>0
    if cuts:assert cuts[-1]['toFrame']==c['fromFrame']
    cuts.append(c)
def model(id,a,b,entryId=None,span=None,**kw):
    m=byId[id];assert m['sourceSamplePixelsApproved'];span=span or m['mediaSpanFrames']
    assert abs((rf(b)-rf(a))-(span[1]-span[0]))<=1
    add(entryId or id,a,b,'explanation',entryId=entryId or id,path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,sourceSampleReview=m['sourceSampleReview'],verification=m['verification'],shiftUpPixels=60,padRoundingAtMostOneFrame=True,completeModelMeaningRetained=(entryId is None),**kw)
previous=read(P/'reconstruction-chapter-review-build-v23.json')['outputs'][0]
add('preserved-original-silent-boundary',start,entries[0]['start'],'explanation',path=previous['path'],sha256=previous['sha256'],sourceStart=(previous['frames']-1)/60,freezeFrameOnly=True,reason='Original0.72s PCM silence; last reconstruction explanation frame retained')
for e in entries:
    if e['id']!='15-guide-megalights-view':model(e['id'],e['start'],e['end']);continue
    a=e['start']
    add(e['id']+'-market-activation',a,a+6,'actual',entryId=e['id'],**source,sourceStart=49.8,sourceEnd=55.8,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,cropTopPixels=0,
        label='MegaLights · Unreal Engine 공식 시연 · 2024',secondaryLabel='광원·표면 관찰 · 엔진 내부 표본 실측 아님',sourceSampleReview=proof(rp),allMovingFramesReviewed=False,
        annotation={'type':'native-light-surface','note':'Screen-space observed regions; stop at the54.5s arcade cut; no causal ray drawn through unmeasured world geometry','screenIntervals':[{'from':1.2,'to':4.7,'boxes':[[880,280,390,225,'0xF6D872'],[500,620,500,180,'0x43D7CC']]}],'allMovingAlignmentReviewed':False})
    # Existing independent diagram preserves original model in full earlier.
    model('original-21m-2',a+6,a+10.24,entryId=e['id']+'-visibility',span=[1949+330,1949+584],reuseReason='Visible light versus contribution: red line ends at the occluder, green line reaches a surface',label='설명용 도식 · 엔진 내부 표본 실측 아님')
    model('original-21m-2',a+10.24,e['end'],entryId=e['id']+'-candidate-versus-visibility',span=[1949+303,1949+807],reuseReason='Candidate annotation is yellow and unchecked; visibility rays are green/red after selection. Original full model is retained earlier.',label='설명용 도식 · 엔진 내부 표본 실측 아님',
        annotation={'type':'candidate-versus-visibility','fromXY':[907,608],'toXY':[780,340],'fromFrame':0,'exclusiveEndFrame':269,'colors':{'candidate':'yellow','visible':'green','blocked':'red'},'candidateNeverCountedAsVisible':True,'allMovingAlignmentReviewed':False})
assert len(cuts)==10 and cuts[-1]['toFrame']==N
ids={e['id'] for e in entries};cues=[]
for c in caption['cues']:
    if c['entryId'] not in ids:continue
    f,t=round(c['from']-start,9),round(c['to']-start,9)
    cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':f,'to':t,'firstFrame':math.ceil(f*60-1e-7),'exclusiveEndFrame':math.ceil(t*60-1e-7),'sourceGlobalSeconds':[c['from'],c['to']],'encodedPixelsReviewed':False})
assert(cues[0]['id'],cues[-1]['id'],len(cues))==(195,216,22)
audio={**assembly['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
assert(audio['firstSample'],audio['exclusiveEndSample'],audio['samplesInChapter'])==(20461442,23043842,2582400)
actual=sum(c['frames'] for c in cuts if c['kind']=='actual')
plan={'preparedAt':stamp(),'scope':'MegaLights chapter review pair. All7 KO/EN paragraphs and107.6s PCM preserved; native activation separated from visibility diagram; not final episode allocation',
    'selection':proof(sp),'assembly':proof(ap),'captionDraft':proof(cp),'nativeReview':proof(rp),'primaryVersionReview':proof(primary),'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,
    'totals':{'frames':N,'globalFromFrame':ff,'globalToFrame':lf,'videoSeconds':N/60,'pcmSeconds':audio['secondsInChapter'],'roundingErrorFrames':N-audio['secondsInChapter']*60,'actualFrames':actual,'explanationFrames':N-actual,'body60to40Approved':False},
    'causalPlan':['Many direct-light contributors → choose candidates rather than evaluate every light uniformly.', 'Candidate contribution estimate → separate visibility check → distinguish Forward+ light lists from stochastic sampling/reuse.', 'Complex occlusion and changing light → conditional quality, not a universal constant-cost claim.', 'Observe official market activation → explain visible light versus reaching the surface → yellow unchecked candidate versus green reaching/red blocked visibility rays.', 'Keep sample-count caveat → separate MegaLights direct light/Lumen GI → geometry extension is not a GI algorithm.'],
    'guideVisibleRole':{'actualSeconds':6,'explanationSeconds':12.64,'reason':'Only moving camera/light activation is actual action; candidate/visibility diagrams are explanation. No idle footage quota, loop or slowdown.'},
    'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,**gates,'humanWholeListening':'pending','next':'Build one CPU2 review pair, both decode/PTS/sameAAC, then inspect all22 cue/cut/annotation samples; whole episode and moving/mixed audio gates remain pending.'}
pp=P/'megalights-chapter-review-plan-v26.json';write(pp,plan)
checkpoint=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(checkpoint)
j['episode04MegaLightsNativeDirectReviewV26']={'path':rel(rp),'sha256':sha(rp),'samples':47,'boards':12,'chosenIntervals':[[49.8,55.8]],'allMovingFramesReviewed':False}
j['episode04MegaLightsChapterV26']={'plan':rel(pp),'status':'prepared-only','entries':7,'cuts':10,'cues':22,'frames':N,**gates}
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':plan['next']};j['updatedAt']=stamp()
tmp=checkpoint.with_suffix('.megalights-plan-v26.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(checkpoint)
print(json.dumps({'plan':rel(pp),'entries':len(entries),'cuts':len(cuts),'cues':len(cues),'frames':N,'actualFrames':actual,'newMediaCreated':0,'finalApproved':False}))
