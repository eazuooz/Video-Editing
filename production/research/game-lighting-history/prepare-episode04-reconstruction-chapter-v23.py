"""Preserve all chapter20 PCM; classify hypothetical-test diagrams honestly."""
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
records=[]
for version,kind,sid,count,boards in [(19,'native',6427,34,9),(20,'fan',29330,7,2),(21,'reflection',39159,7,2),(22,'cyber',35107,17,5)]:
    ep=ROOT/f'production/research/game-lighting-history/local/episode04-reconstruction-{kind}-v{version}/execution.json'
    e=read(ep);assert e['status']=='samples-ready' and len(e['samples'])==count and len(e['boards'])==boards
    assert all(c['exitCode']==0 for c in e['commands'])
    try:alive=abs(psutil.Process(e['worker']['pid']).create_time()-e['worker']['createTime'])<.01
    except psutil.NoSuchProcess:alive=False
    assert not alive,'Extraction/acquisition worker still alive'
    sp=ep.with_name('session.json')
    if not sp.exists():write(sp,{'sessionId':sid,'worker':e['worker'],'execution':rel(ep),'closed':True,'exitCode':0,'unifiedExecExitObserved':True,'endedObservedAt':stamp(),'cpuThreads':2,'gpuJobs':0})
    else:
        s=read(sp);assert s['sessionId']==sid and s['closed'] and s['exitCode']==0 and s['unifiedExecExitObserved']
    bs=[];ss=[]
    for b in e['boards']:
        assert sha(ROOT/b['path'])==b['sha256'];bs.append({**b,'directlyRead':True,'reviewedAt':stamp()})
    for x in e['samples']:
        assert sha(ROOT/x['path'])==x['sha256'];ss.append({**x,'directlyReadOnBoard':True})
    records.append({'version':version,'execution':proof(ep),'session':proof(sp),'boards':bs,'samples':ss,'acquisition':e.get('acquisition'),'source':e.get('source')})
source={'path':'production/research/game-lighting-history/local/episode04-native-v1/cyberpunk-ray-reconstruction.mp4','sha256':'25a4f9f3d7c2cd335df4128687582e444b61c7d119b2af5493b80003b49ac2da','url':'https://www.youtube.com/watch?v=oMCC9TgsCDY'}
assert sha(ROOT/source['path'])==source['sha256']
rp=P/'reconstruction-native-direct-review-v23.json'
write(rp,{'reviewedAt':stamp(),'records':records,'samples':65,'boards':18,'allSampleBoardsDirectlyRead':True,'source':source,
    'chosenIntervals':[[33,37.5],[46,50.62]],'sourceOverviewIntervalNotRepeated':[39,42.2],
    'findings':[
        'Original Cyberpunk33-37s labelled DLSS Off/DLSS3.5 split comparison shows camera motion along an illuminated ceiling and wet floor. Compare reflected detail and boundaries; do not infer isolated RR speed or a ground-truth image from this joint-feature label.',
        'Original38-43s wet street comparison includes the39-42.2s opening example. It is excluded from this new guide to preserve distinct footage.30-32s Ray Reconstruction title and44-45s Frame Generation title are excluded from actual-footage time.',
        'Original46-49s market and50-53s dark interior/stair camera motion carry source DLSS Off Full RT On versus DLSS3.5 Full RT On FPS labels. These illustrate several labelled conditions changing together, beside the exact conditional narration. Their displayed FPS is not our benchmark, an RR-only improvement or input latency.',
        'Portal fan Gg_3-X3d3iY,2024-03-12: rotating fan/chain mesh and shadow comparison, not reflected neon-text detail. All7 source samples read. Do not silently substitute it under the unchanged reflected-detail narration or date its March2024 media as2023.',
        'Portal M9yHtS8EoFg,2023-08-18:7.9s cube/wall/floor reflection comparison with DLSS Off Ultra Graphics versus DLSS3.5 Ultra Graphics With Ray Reconstruction. All7 samples read. It is short and a different example requiring a narrated introduction; not selected or looped to fill the guide. Prior Portal use remains a recent-use caveat.',
        'New Cyberpunk HrkQldzUnAI,2023-10-12: all17 samples/5 boards read.0s black,6/12/15/27/33/42s promotional quotes/title,45/48s logo;21/24s reflection shots repeat visual material from the earlier source,30s shows a95FPS combined-feature presentation,36/39s combat. A new source ID is not new visual evidence. Not selected for this unchanged guide.',
        'The v22 acquisition script recorded primaryDate2023-10-12 while its linked August announcement is dated2023-08-22. Preserve the acquisition as history; this review corrects that field: media upload2023-10-12 and announcement2023-08-22 are distinct.',
        '65 sparse samples directly read across this continuing task. Normal-speed continuous source playback, all moving annotated frames, rights/recent-use and final use remain pending.'
    ],'sampledChosenContentSuitable':True,'allMovingFramesReviewed':False,'rightsApproved':False,'recentUseCheckPassed':False,'finalUseApproved':False,'newGitImages':0})
ap=P/'additive-unmixed-review-assembly-v2.json';assembly=read(ap)
sp=P/'clean-source-selection-v8.json';selection=read(sp)
cp=P/'local/caption-word-draft-v2.json';caption=read(cp)
entries=[e for e in assembly['entries'] if e['start']>=731 and e['end']<=853]
assert len(entries)==8 and entries[0]['id']=='original-20-1' and entries[-1]['id']=='original-20-6'
start=730.8800416666667;end=entries[-1]['end'];rf=lambda t:math.floor(t*60+.5)
ff,lf=rf(start),rf(end);N=lf-ff;assert(ff,lf,N)==(43853,51154,7301)
byId={s['id']:s for s in selection['selected']};cuts=[]
def add(id,a,b,kind,**kw):
    f,t=rf(a),rf(b)
    c={'id':id,'from':round(a-start,9),'to':round(b-start,9),'fromFrame':f-ff,'toFrame':t-ff,'globalFromFrame':f,'globalToFrame':t,'frames':t-f,'kind':kind,**kw}
    assert c['frames']>0
    if cuts:assert cuts[-1]['toFrame']==c['fromFrame']
    cuts.append(c)
def model(id,a,b,entryId=None,span=None,**kw):
    m=byId[id];assert m['sourceSamplePixelsApproved']
    span=span or m['mediaSpanFrames']
    assert abs((rf(b)-rf(a))-(span[1]-span[0]))<=1
    add((entryId or id),a,b,'explanation',entryId=entryId or id,path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,sourceSampleReview=m['sourceSampleReview'],verification=m['verification'],shiftUpPixels=60,padRoundingAtMostOneFrame=True,completeModelMeaningRetained=(entryId is None),**kw)
previous=read(P/'path-chapter-review-build-v18.json')['outputs'][0]
add('preserved-original-silent-boundary',start,entries[0]['start'],'explanation',path=previous['path'],sha256=previous['sha256'],sourceStart=(previous['frames']-1)/60,freezeFrameOnly=True,reason='Original0.72s PCM silence; last path explanation frame retained')
for e in entries:
    if e['id']!='14-guide-reconstruction-game':model(e['id'],e['start'],e['end']);continue
    a=e['start']
    for suffix,x,y,ss,se in [('reflection-detail',0,4.5,33,37.5),('joint-conditions',4.5,9.12,46,50.62)]:
        add(e['id']+'-'+suffix,a+x,a+y,'actual',entryId=e['id'],**source,sourceStart=ss,sourceEnd=se,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,cropTopPixels=200,
            label='Cyberpunk 2077 · 공식 비교 시연 · 2023',secondaryLabel='여러 DLSS 기능이 함께 표기됨 · RR 단독 측정 아님',sourceSampleReview=proof(rp),allMovingFramesReviewed=False,sourceTitleCardExcludedByCut=True,
            annotation=({'role':'Compare corresponding visible floor-reflection regions, not measured game-world ray geometry','colors':{'left':'red','right':'teal'},'frameStep':6,'frames':[0,164],'fromXY':[300,500],'toXY':[170,560],'size':[300,80],'rightOffsetX':970,'label':'반사 세부','allMovingAlignmentReviewed':False} if suffix=='reflection-detail' else None))
    # Actual sentence12.24s introduces a hypothetical controlled test. Do not pad
    # native footage, loop it, or call this diagram portion game action.
    model('original-20-5',a+9.12,a+12.24,entryId=e['id']+'-detail-diagram',span=[2626+304,2626+491],reuseReason='Diagram-led comparison targets while narration says what details to inspect; original20-5 model still preserved in full')
    model('original-20-6',a+12.24,e['end'],entryId=e['id']+'-controlled-test-diagram',span=[346,648],reuseReason='Narrated hypothetical matching camera/internal-resolution/exposure; not an actual measured test; original20-6 model still preserved in full')
assert len(cuts)==12 and cuts[-1]['toFrame']==N
ids={e['id'] for e in entries};cues=[]
for c in caption['cues']:
    if c['entryId'] not in ids:continue
    f,t=round(c['from']-start,9),round(c['to']-start,9)
    cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':f,'to':t,'firstFrame':math.ceil(f*60-1e-7),'exclusiveEndFrame':math.ceil(t*60-1e-7),'sourceGlobalSeconds':[c['from'],c['to']],'encodedPixelsReviewed':False})
assert(cues[0]['id'],cues[-1]['id'],len(cues))==(169,194,26)
audio={**assembly['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
assert(audio['firstSample'],audio['exclusiveEndSample'],audio['samplesInChapter'])==(17541121,20461442,2920321)
actual=sum(c['frames'] for c in cuts if c['kind']=='actual')
plan={'preparedAt':stamp(),'scope':'Denoising/Ray Reconstruction chapter review pair. All8 KO/EN paragraphs and121.680041667s PCM preserved; guide split by visible role; not final episode allocation',
    'selection':proof(sp),'assembly':proof(ap),'captionDraft':proof(cp),'nativeReview':proof(rp),'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,
    'totals':{'frames':N,'globalFromFrame':ff,'globalToFrame':lf,'videoSeconds':N/60,'pcmSeconds':audio['secondsInChapter'],'roundingErrorFrames':N-audio['secondsInChapter']*60,'actualFrames':actual,'explanationFrames':N-actual,'body60to40Approved':False},
    'causalPlan':['Few ray samples create noise → distinguish same-wall variation from actual wall/window boundaries using depth/normal clues.',
    'Reject mismatched surface history after motion/disocclusion → explain2023 RR reconstruction role without proprietary model architecture.',
    'Separate SR resolution/FG displayed frames/RR noisy-effect restoration → compare reflected detail during camera motion, then read joint-feature labels without attributing all difference to RR.',
    'Define comparison targets → diagram of hypothetical matched camera/internal-resolution/exposure experiment → preserve original caution against universal quality claims.'],
    'guideVisibleRole':{'actualSeconds':9.12,'explanationSeconds':5.04+3.12,'reason':'The last guide sentences discuss a comparison method and hypothetical test; preserve them as explanation rather than fill the entire guide with unrelated short clips.'},
    'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,**gates,'humanWholeListening':'pending',
    'next':'SingleCPU2 pair build, both whole decodes/PTS/AAC check, then all26 cue/cut/annotation source samples. Full moving/whole-episode/mixed-audio gates remain pending.'}
pp=P/'reconstruction-chapter-review-plan-v23.json';write(pp,plan)
checkpoint=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(checkpoint)
j['episode04ReconstructionNativeDirectReviewV23']={'path':rel(rp),'sha256':sha(rp),'samples':65,'boards':18,'chosenIntervals':[[33,37.5],[46,50.62]],'allMovingFramesReviewed':False}
j['episode04ReconstructionChapterV23']={'plan':rel(pp),'status':'prepared-only','entries':8,'cuts':12,'cues':26,'frames':N,**gates}
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':plan['next']};j['updatedAt']=stamp()
tmp=checkpoint.with_suffix('.reconstruction-plan-v23.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(checkpoint)
print(json.dumps({'plan':rel(pp),'entries':len(entries),'cuts':len(cuts),'cues':len(cues),'frames':N,'actualFrames':actual,'newMediaCreated':0,'finalApproved':False}))
