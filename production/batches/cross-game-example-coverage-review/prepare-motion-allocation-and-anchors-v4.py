"""Finalize the prepared timing repair and bounded observed screen roles."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
proof=read(R/'button-result-timing-corrected-evidence-v2.json')
for row in proof['correctedSamples']:assert sha(ROOT/row['path'])==row['sha256']
proof.update(all54CurrentNativeFramesDirectlyReviewed=True,directReviewCompletedAt=stamp,
 observations='Corrected first board12 Portal samples and retained remaining42 fresh/native Portal samples read directly. Native2947 cyan,2948 yellow; tail2968–2991 retains yellow/door action, no promotional sequence.',
 checkedFileHashes=[dict(path=x['path'],sha256=sha(ROOT/x['path'])) for x in proof['correctedSamples']]+[dict(path=proof['correctedFirstBoard']['path'],sha256=sha(ROOT/proof['correctedFirstBoard']['path']))])
(R/'button-result-timing-corrected-evidence-v2.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
p=read(R/'paragraph-native-allocation-v3.json');p.update(schemaVersion=4,preparedAt=stamp,previousPreparedAllocation='paragraph-native-allocation-v3.json',
 heldV3Reason='Yellow spoken before observed native2948 change. Additional48f result tail is offset by removing48f earliest Portal lead-in; useful explanation/voice unchanged.')
parts=p['newScenes'][0]['parts'];first=parts[0]
first.update(nativeInFrame=504,frames=1391)
first['voiceSegments'][1]['offsetFrame']=991
button=next(x for x in parts if x['id']=='07b-cube-button');button.update(nativeOutFrameExclusive=2992,frames=948,voiceOffsetFrame=620,voiceOut=34.56,
 purpose='Before/action/result observed at native2947 cyan→2948 yellow98.364933s. Start retained second sentence at output620/60; wordyellow maps98.3606s, within one source-frame of observed yellow. Retain yellow/door result through99.7997s. No promo.')
room=next(x for x in parts if x['id']=='07b-room-reacquire');room.update(voiceIn=34.56,voiceOut=38.56)
device=next(x for x in parts if x['id']=='07b-device-reacquire');device.update(voiceIn=38.56)
for scene in p['newScenes']:
 cursor=0
 for x in scene['parts']:x.update(localStartFrame=cursor,localEndFrame=cursor+x['frames']);cursor+=x['frames']
 assert cursor==scene['frames']
p['notes']+=['V3 source/timing is held. V4 source504..1199 gives1391f and button2518..2992 gives948f; total6596actual unchanged.',
 'Displayed prior conditional totalratio0.2f was erroneous. Baseline0.2f+addition0.2f=total0.4f, within1frame; final encoded approval remains false.']
out=R/'paragraph-native-allocation-v4.json';assert not out.exists();out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf-8')
native=read(R/'native-preflight-execution-v1.json');samples={(w['sourceKey'],r['nativeFrame']):r for w in native['windows'] for r in w['samples']}
fine=read(R/'alyx-annotation-observation-plan-v3.json')
tracks=[]
def track(id,key,color,label,rows,range_end=None):
 refs=[]
 for n,pt in rows:
  ref=samples.get((key,n))
  assert ref,(key,n)
  assert sha(ROOT/ref['path'])==ref['sha256']
  refs.append(dict(nativeFrame=n,screenPoint1280=pt,path=ref['path'],sha256=ref['sha256']))
 tracks.append(dict(id=id,sourceKey=key,color=color,label=label,rows=refs,rangeEndExclusive=range_end or rows[-1][0],
  rule='Observed1280x720 screen point; interpolate only within this bounded continuous view; hide outside/at uncertainty. Encoded tracking review required.'))
track('portal-held-cube','portal2','red','조작 대상: 큐브',[(1109,[625,350]),(1139,[635,385]),(1169,[635,375]),(1199,[635,377])],1199)
track('portal-device-cue','portal2','cyan','주변 단서: 벽의 장치',[(1919,[650,405]),(1949,[617,335]),(1979,[627,320])],1979)
track('portal-laser-cube','portal2','red','조작 대상: 큐브',[(2308,[610,285]),(2338,[610,285]),(2368,[620,315])],2368)
track('portal-target-status','portal2','cyan','목표 상태: 연결 표시',[(2308,[860,173]),(2338,[870,164]),(2368,[830,220]),(2398,[680,257]),(2428,[540,290])],2428)
track('alyx-board-object','alyx','red','조작 대상: 판자',[(3357,[940,240]),(3417,[920,280]),(3477,[920,260]),(3537,[900,250])],3537)
# Existing fine points are already directly reviewed against native samples.
for role,color,label in [('destinationFeet','red','선택한 목적지'),('arrivalWall','cyan','도착 후 단서: 문 옆 벽')]:
 rr=[s for s in fine['samples'] if s['role']==role]
 for s in rr:assert sha(ROOT/s['path'])==s['sha256']
 tracks.append(dict(id='alyx-'+role,sourceKey='alyx',color=color,label=label,rows=[dict(nativeFrame=s['nativeFrame'],screenPoint1280=s['observedSampleScreenPoint'],path=s['path'],sha256=s['sha256']) for s in rr],
  rangeEndExclusive=3063 if role=='destinationFeet' else 3082,rule='Hide all destination annotations3063..3069; no path interpolation across viewpoint jump.'))
anchors=dict(schemaVersion=1,preparedAt=stamp,allocation=out.name,coordinateTransform='1280x720 sample -> full-source1600x900 fit at160,0: x*1.25+160,y*1.25. Preserve entireHUD. Preview caption fixed960970.',
 tracks=tracks,additionalAnchorBoardsDirectlyRead=['portal-aim04/05','portal-traverse01/02/04/05','portal-cube02/03','alyx-platform02/03/04'],
 exactSourceFrameIdentity='sourceKey+nativeFrame; never nativeFrame alone',engineWorldAxisClaim=False,centroidClaim=False,comfortOutcomeClaim=False,
 allIntermediateTrackingApproved=False,narrationTimedPixelApproval=False,allFinalCueApproval=False,localOnlyRaster=True)
ap=R/'remaining-action-annotation-anchors-v1.json';assert not ap.exists();ap.write_text(json.dumps(anchors,ensure_ascii=False,indent=2)+'\n','utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path);cp.update(activeOwnedWorkers=0,ownedJob=dict(active=False,status='completed',exitCode=0,completion='080fb7'),
 paragraphNativeAllocation=out.name,remainingAnnotationAnchors=ap.name,nativeResultTiming= 'button-result-timing-corrected-evidence-v2.json',
 next='Render the remaining eight unique actual windows once with prepared bounded roles, current narration timing and caption preview; directly compare all encoded cues/anchors/normal1x. Preserve completed PortalV2/PWashV4/summary/comparisons/TTSASR. V3 allocation and wrong-source reuse remain held. Final17mix/QA/upload not yet approved.')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(allocation=out.name,tracks=len(tracks),nativeSamplesReviewed=54,ratioErrorFrames=p['ratioErrorFrames'],mediaRendered=False)))
