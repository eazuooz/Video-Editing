"""Use inspected complete actions instead of long setup before the same result."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
at=datetime.now(timezone.utc).isoformat()
choices={
 'game-math-parametric-hermite':{
  '000':(702,718,715.9,None,'Moving train702–718 follows the visible curved rail. Journey has no discrete terminal event; second observed bend715.965 proves the narrated direction change.'),
  '012':(93,104,103.5,'일차 도함수는','Launch Star activation93–99, curved native flight99–102, landing103–104. Earlier crystal-breaking is unnecessary setup for the tangent claim.'),
  '027':(270,282,281.5,'에르미트 곡선은','Preview endpoint changes270–275, construction277–280, solid rail281–282. Removes the unrelated underwater camera move258–266.')},
 'game-math-bezier-subdivision':{
  '000':(238,247,246,None,'Actual corner edit238–243 changes the last angled corner to rounded; closed loop is visible243.933–247. Preserves the existing whole-thesis narration without a45second setup.'),
  '017':(93,104,103.5,'단항식 표현을 미분한 뒤','Retains complete Launch Star activation, curved flight and landing before the explicit derivative calculation.'),
  '022':(270,282,281.5,'이제 원하는 모양이 거의 완성됐는데','Retains endpoint adjustment, construction and completed connected track, then the independent subdivision demonstration.')},
 'game-math-splines-continuity':{
  '000':(270,282,281.5,None,'Endpoint adjustment to solid connected rail remains visible through281.9. Unrelated underwater setup omitted; abstract narration unchanged.'),
  '017':(93,104,103.5,'지나야 할 매듭점만 정하고','Preserves the complete real flight; return to our model before knot/tangent construction.'),
  '042':(702,720,715.9,None,'Conclusion reuses the recognizable moving train through the observed bend, without waiting for a route destination that is not the claim.')}
}
for slug,selected in choices.items():
 assert c['productionAllowedNow'] and slug in c['projectSlugs'];P=R/'projects'/slug
 bp=P/'planning/scene-bindings.json';b=read(bp);pp=P/'planning/production-plan.json';plan=read(pp)
 assert 'nativeGameHandoffRevision' not in plan,'Use an additive decision revision'
 changes=[]
 for s in b['scenes']:
  if s['id'] not in selected:continue
  start,end,result,handoff,note=selected[s['id']];g=s['actualGamePart'];old=[g['sourceIn'],g['sourceOut']]
  offset=g.get('fullOriginalAudioIn',g['sourceIn'])-g['sourceIn']
  g.update(sourceIn=start,sourceOut=end,minimumObservedResultOut=result,fullOriginalAudioIn=start+offset)
  if handoff:
   assert handoff in s['speech'];g['speechTarget']['endBeforeKo']=handoff
  g['handoffObservation']=dict(note=note,evidence='production/batches/game-math-remaining-20261104/local/handoff-observations-v1/manifest.json',
    mode='Actual decoded temporal source samples; final continuous composite/audio still pending',narrationUnchanged=True)
  for entry in plan['nativeGameCueBindings']:
   if entry['sceneId']==s['id']:entry.update(copy.deepcopy(g))
  changes.append(dict(scene=s['id'],previousWindow=old,selectedWindow=[start,end],minimumResultOut=result,reason=note))
 plan['nativeGameHandoffRevision']=dict(at=at,changes=changes,narrationUnchanged=True,newTts=False,finalEncodedQa=False)
 save(bp,b);plan['sceneBindingsSha256']=sha(bp);save(pp,plan)

# The shorter M32 opening has a different, directly reviewed corner guide.
P=R/'projects/game-math-bezier-subdivision';track=read(B/'local/handoff-observations-v1/loop-guide-v2/track.json')
track['visualQa']=dict(status='temporal-samples-reviewed-final-encoded-pending',at=at,
 evidence=['production/batches/game-math-remaining-20261104/local/handoff-observations-v1/loop-guide-v2/board.jpg'],
 note='18 actual overlay samples at8fps inspected. Shortened open contour avoids Toad, cursor and native context menus. Clear before rounding/zoom, let the actual rounded result remain unobstructed.',
 scope='Source overlay samples only; final narration/captions/mobile composite pending',humanFinalReview=False,continuousPlayback=False)
dest=P/'production/local/annotation-reviewed-v2/M32-loop-corner.json';assert not dest.exists();save(dest,track)
labels=read(P/'planning/game-annotation-tracks.json')
new={k:v for k,v in track.items() if k!='keyframes'};new['trackFile']=dest.relative_to(R).as_posix();new['sourceTrackSha256']=sha(dest);new['scenes']=['000']
labels['windows'].append(new);save(P/'planning/game-annotation-tracks.json',labels)
pp=P/'planning/production-plan.json';plan=read(pp)
next(x for x in plan['nativeGameCueBindings'] if x['sceneId']=='000')['annotationEvidence']=dict(file='planning/game-annotation-tracks.json',windows=[track['id']],sourceTemporalSamplesReviewed=True,finalSpeechAndMotionReview=False)
save(pp,plan)

mp=B/'local/handoff-observations-v1/manifest.json';m=read(mp)
for row in m['records']:row.update(viewed=True,reviewedAt=at,scope='16 native source samples per window directly inspected; no continuous playback claim')
m['status']='all-three-native-action-windows-inspected';save(mp,m)
print('Nine native game windows refined without narration changes; source result minimums recorded.')
