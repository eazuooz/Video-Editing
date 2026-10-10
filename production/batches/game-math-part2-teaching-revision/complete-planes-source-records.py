"""Reconcile current V3 speech/native cuts while keeping earlier evidence frozen."""
from pathlib import Path
import copy, datetime, hashlib, json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
history=B/'planes-game-insertions.json';old=read(history)
baseline=B/'baselines/game-math-planes-barycentric/sources/gameplay-cuts.json'
sources=copy.deepcopy(read(baseline)['sources'])
for item in old['sourceRecords']:
    s=copy.deepcopy(item);assert sha(ROOT/s['sourceFile'])==s['sha256']
    s.update(nativeCompared=True,selected=True,metadataSha256=sha(ROOT/s['sourceMetadata']),
        selectionEvidence=[rel(B/'planes-candidate-comparison.json'),rel(B/'planes-capacity-source-review.json')],
        sourceAudioUsed=False,worldOrEngineMeasurementVerified=False,humanRightsComplete=False)
    sources[s['id']]=s
current=[];episodes=[]
for slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']:
    P=ROOT/'projects'/slug;m=read(P/'project.json');lesson=read(P/'production/lesson.json');t=read(P/'production/timeline.json')
    ids=set();cuts=[]
    for slot in t['scenes']:
        if slot['classification']!='actual':continue
        original=next(s for s in lesson['scenes'] if s['id']==slot['id'])
        ids.add(original['sourceId'])
        if not slot['preservedOriginal']:
            ids.update(original.get('segmentSourceIds',[]))
            ids.update(s.get('sourceId',original['sourceId']) for s in original.get('sourceSegments',[]))
            record=copy.deepcopy(original);record.update(voiceSha256=slot['voiceSha256'],sourceGroupStartsAtLines=original['sourceGroupStartsAtLines'],
                measuredCut=copy.deepcopy(slot['cut']),measuredSeconds=slot['seconds'],currentMovingPixelApproval=False)
            record['selection']['finalNativeIntervals']=[[s['in'],s['in']+s['frames']/60] for s in slot['cut']['segments']]
            record['selection']['selectedCapacityIntervals']=original['intervals']
            record['selection']['camera']='Native1x; each non-contiguous cut announced; hide uncertain geometry rather than extending it.'
            current.append(record)
        cuts.append({k:slot[k] for k in ['id','frames','seconds','start','cut','baselineClip','preservedOriginal'] if k in slot})
    sourcepath=P/'production/footage-sources.json';cutpath=P/'production/footage-cuts.json'
    prior=read(sourcepath) if sourcepath.exists() else {}
    write(sourcepath,{'sources':{i:sources[i] for i in ids},'historicalSelectionRecord':rel(history),'historicalSelectionSha256':sha(history),
        'currentSelectionRecord':rel(B/'planes-current-game-insertions.json'),'baselineSourceRecord':rel(baseline),
        'editableAnnotationRegistry':rel(B/'planes-annotation-tracks.json'),'bodyActualShare':.4,'bodyExplanationShare':.6,
        'sourceAudioUsed':False,'backgroundMusic':False,'originalFootagePreserved':True,
        'currentMovingPixelApproval':prior.get('currentMovingPixelApproval',False),'humanRightsReviewComplete':False})
    write(cutpath,{'status':'Current measured native1x cuts; current-hash narration and tracked pixels separately reviewed',
        'baselineSourceRecord':rel(baseline),'currentSelectionRecord':rel(B/'planes-current-game-insertions.json'),
        'scenes':cuts,'noArtificialLoopsFreezeOrSlowdown':True,'humanRightsReviewComplete':False})
    m['paths'].update(sources=rel(sourcepath),footageCuts=rel(cutpath),audioReport=rel(P/'audio/mix-measurements.json'))
    write(P/'project.json',m)
    episodes.append({'slug':slug,'seconds':t['seconds'],'bodyFrames':t['bodyFrames'],'actualFrames':t['actualFrames'],
        'explanationFrames':t['explanationFrames'],'ratioErrorFrames':t['ratioErrorFrames'],'koEnCaptionCount':len(t['koCaptions']),
        'originalIds':[s['id'] for s in t['scenes'] if s['preservedOriginal']]})
write(B/'planes-current-game-insertions.json',{'recordedAt':datetime.datetime.now().astimezone().isoformat(),
    'historicalV2SelectionRecord':rel(history),'historicalV2SelectionSha256':sha(history),'currentV3NarrationRetakes':rel(B/'planes-retakes-v3-pretts-audit.json'),
    'capacityRevisions':rel(B/'planes-capacity-source-review.json'),'scenes':current,'episodes':episodes,
    'mathTeachingClaimsPreserved':True,'original22ScenesAndPCMPreserved':True,'ratio':[.4,.6],
    'annotationLimits':'Only directly observed stable native geometry; brief lost/occluded tracks hidden. No actual world coordinate or unverified mesh/physics claim.',
    'movingPixelApproval':False,'humanListeningComplete':False,'humanRightsReviewComplete':False})
capacity=read(B/'planes-capacity-source-review.json')
extra='shared/output/game-math-part2-teaching-revision/planes-capacity-review/vents-72.3.png'
capacity.setdefault('additionalDirectlyViewedPixels',[])
if extra not in capacity['additionalDirectlyViewedPixels']:capacity['additionalDirectlyViewedPixels'].append(extra)
capacity['historyNote']='The frozen V2 selection file records the historical intervals. Re-running the capacity helper can have identical before/after fields; final lesson/timeline and current selection record are authoritative.'
write(B/'planes-capacity-source-review.json',capacity)
print('Current V3 source groups, native measured cuts and both40:60 timelines reconciled; historical evidence preserved.')
