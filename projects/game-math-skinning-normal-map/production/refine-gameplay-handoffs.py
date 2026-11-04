"""Preserve actual actions and hand back to Unity at measured spoken transitions."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

P=Path(__file__).resolve().parents[1]
R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
assert c['productionAllowedNow'] and P.name in c['projectSlugs']
path=P/'planning/scene-bindings.json';b=read(path);plan=read(P/'planning/production-plan.json')
assert 'gameplaySpeechHandoffReview' not in plan,'Preserve recorded decisions; make another explicit revision'
evidence=[]
choices={
 '002':(738,746,744.8,'이 차이를 직접 만들어 보려고',
        'riders-fine/board-01.jpg',
        'Viewed 734–749 at 1fps: approach738–740, airborne articulation741–743, landing744 and riding away745. Existing unchanged002 PCM starts the next explanation at7.36s. The full24s window hid the coordinate-system explanation behind unrelated riding.'),
 '015':(115,121,119.5,'이런 표면 디테일을 표현하는 한 가지 방법을',
        'doom3-normal-surfaces/board-01.jpg',
        'Viewed110–127 source board: light sweeps metal115–118, then pipe119 and away120. Retains reviewed117–118.2 groove guide. Existing unchanged015 PCM starts the demonstration handoff5.60s after the paragraph starts, before the words about our own surface.')
}
for s in b['scenes']:
 if s['id'] not in choices:continue
 start,end,result,handoff,board,note=choices[s['id']]
 g=s['actualGamePart'];old=copy.deepcopy(g)
 delta=start-g['sourceIn']
 g.update(sourceIn=start,sourceOut=end,minimumObservedResultOut=result,
          fullOriginalAudioIn=g.get('fullOriginalAudioIn',old['sourceIn'])+delta)
 g['speechTarget']['endBeforeKo']=handoff
 g['speechTarget']['timing']='Start and handoff use actual original PCM words; native action/result remains complete. No narration, source speed or total length changes.'
 ev=dict(scene=s['id'],previousSourceWindow=[old['sourceIn'],old['sourceOut']],
         sourceWindow=[start,end],minimumObservedResultOut=result,
         speechHandoff=handoff,sourceBoard=str((P/'production/local/footage-review'/board).relative_to(R)),
         observation=note,finalEncodedReview=False)
 evidence.append(ev)
 for entry in plan.get('nativeGameCueBindings',[]):
  if entry.get('sceneId')==s['id']:
   entry.update(copy.deepcopy(g))
plan['gameplaySpeechHandoffReview']=dict(at=datetime.now(timezone.utc).isoformat(),
 changes=evidence,narrationUnchanged=True,actualPcmUnchanged=True,
 reason='Return to the visible Unity object when the narration introduces our demonstration; do not leave gameplay covering necessary explanatory steps.',
 validation='Final cut must retain the observed action/result; alignment checks required before costly capture.')
save(path,b);plan['sceneBindingsSha256']=sha(path);save(P/'planning/production-plan.json',plan)
print('Two inspected native-motion windows matched to unchanged spoken handoffs; final encoded review pending.')
