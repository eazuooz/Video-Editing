"""Record measured cuts and compared sources while preserving rights limitations."""
from pathlib import Path
import copy,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
baseline=B/'baselines/game-math-polygons-triangulation/sources/gameplay-cuts.json';sources=copy.deepcopy(read(baseline)['sources'])
fresh=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates'
for folder,metadata in [(fresh/'tiny-glade',fresh/'tiny-glade/inputs.json'),(fresh,fresh/'inputs.json')]:
 for entry in read(metadata):
  source=folder/entry['file'];assert sha(source)==entry['sha256']
  s=copy.deepcopy(entry);s.update(sourceFile=rel(source),file=rel(source),sourceMetadata=rel(metadata),metadataSha256=sha(metadata),nativeCompared=True,selected=True,
    selectionEvidence=[rel(B/'polygons-candidate-comparison.json'),rel(B/'polygons-path-timing-refinement.json')],sourceAudioUsed=False,worldOrEngineMeasurementVerified=False,humanRightsComplete=False,
    rights='Official developer-supplied public footage; availability is not a broad license; game-IP/human review pending.')
  sources[s['id']]=s
current=[];episodes=[]
for slug in ['game-math-polygon-centers-v2','game-math-polygon-partition-v2']:
 P=ROOT/'projects'/slug;m=read(P/'project.json');lesson=read(P/'production/lesson.json');t=read(P/'production/timeline.json');ids=set();cuts=[]
 for slot in t['scenes']:
  if slot['classification']!='actual':continue
  original=next(s for s in lesson['scenes'] if s['id']==slot['id']);ids.add(original['sourceId'])
  if not slot['preservedOriginal']:
   for segment in original['sourceSegments']:
    sid=segment['sourceId'];ids.add(sid)
    if sid not in sources:
     matched=[v for v in sources.values() if v.get('file',v.get('sourceFile'))==segment['sourceFile']]
     assert matched,(sid,segment['sourceFile'])
     sources[sid]={**copy.deepcopy(matched[0]),'id':sid,'aliasOf':matched[0]['id'],'sourceFile':segment['sourceFile']}
    assert sha(ROOT/segment['sourceFile'])==segment['sourceSha256']
   record=copy.deepcopy(original);record.update(voiceSha256=slot['voiceSha256'],measuredCut=slot['cut'],measuredSeconds=slot['seconds'],currentMovingPixelApproval=False)
   record['selection'].update(finalNativeIntervals=[[s['in'],s['in']+s['frames']/60] for s in slot['cut']['segments']],selectedCapacityIntervals=original['intervals'],camera='Native1x; hide uncertain geometry and reset each separate source group.')
   current.append(record)
  cuts.append({k:slot[k] for k in ['id','frames','seconds','start','cut','baselineClip','preservedOriginal'] if k in slot})
 sourcepath=P/'production/footage-sources.json';cutpath=P/'production/footage-cuts.json'
 write(sourcepath,{'sources':{i:sources[i] for i in sorted(ids)},'currentSelectionRecord':rel(B/'polygons-current-game-insertions.json'),'baselineSourceRecord':rel(baseline),
   'editableAnnotationRegistry':rel(B/'polygons-annotation-tracks.json'),'bodyActualShare':.4,'bodyExplanationShare':.6,'sourceAudioUsed':False,'backgroundMusic':False,
   'originalFootagePreserved':True,'currentMovingPixelApproval':False,'humanRightsReviewComplete':False})
 write(cutpath,{'status':'Measured native1x cuts; final moving annotation/narration/caption review pending','scenes':cuts,'noArtificialLoopsFreezeOrSlowdown':True,'humanRightsReviewComplete':False})
 m['paths'].update(sources=rel(sourcepath),footageCuts=rel(cutpath),audioReport=rel(P/'audio/mix-measurements.json'));write(P/'project.json',m)
 episodes.append({'slug':slug,'seconds':t['seconds'],'bodyFrames':t['bodyFrames'],'actualFrames':t['actualFrames'],'explanationFrames':t['explanationFrames'],'ratioErrorFrames':t['ratioErrorFrames'],'koEnCaptionCount':len(t['koCaptions'])})
write(B/'polygons-current-game-insertions.json',{'recordedAt':datetime.datetime.now().astimezone().isoformat(),'history':rel(B/'polygons-game-insertions.json'),'candidateComparison':rel(B/'polygons-candidate-comparison.json'),
 'retakes':rel(B/'polygons-retakes-v3-pretts-audit.json'),'scenes':current,'episodes':episodes,'original22ScenesAndPCMPreserved':True,'ratio':[.4,.6],
 'annotationLimits':'Observed stable native projected geometry only; no game-world values, actual pivot/centroid or unverified engine partition algorithm asserted.',
 'movingPixelApproval':False,'humanListeningComplete':False,'humanRightsReviewComplete':False})
print('Current native cuts, all source hashes, comparison and licensing limitations recorded.')
