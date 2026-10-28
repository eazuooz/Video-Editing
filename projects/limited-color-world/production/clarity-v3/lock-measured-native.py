"""Promote measured cue drafts after coordinating the shared native bridge."""
from pathlib import Path
import json,copy
import audio_pipeline as a
H=Path(__file__).resolve().parent
def main():
 a.require_authorized('lock-measured-native-cues')
 draft=a.read(H/'unity-cues.draft.json');plan=a.read(H/'edit-plan.draft.json')
 assert draft['timingLocked'] and len(draft['cuts'])==23
 photos={'proof-options','puyo-official-filters','mirror-still'};byid={x['cutId']:x for x in draft['cuts']};jobs=[]
 for c in plan['cuts']:
  if c['kind']!='explanation' or c['variant'] in photos:continue
  frames={0,c['frames']//4,c['frames']//2,c['frames']*3//4,c['frames']-1}
  for cue in byid[c['id']]['cues']:
   for t in [cue['start'],(cue['start']+cue['end'])/2,cue['end']]:
    frames.update(round(t*60)+d for d in [-1,0,1] if 0<=round(t*60)+d<c['frames'])
  jobs.append({'slug':'limited-color-world','cutId':c['id'],'frames':c['frames'],'stageClass':'D25ColorClarityStage','sampleFrames':sorted(frames)})
 assert len(jobs)==18
 for name in ['unity-cues.json','capture-jobs.json']:
  prior=H/'evidence'/(name.replace('.json','-before-measured.json'))
  if not prior.exists():prior.write_bytes((H/name).read_bytes())
 a.save(H/'unity-cues.json',draft)
 a.save(H/'capture-jobs.json',{'revision':'clarity-v3','timingLocked':True,'worldOnly':True,'photoOnlyCuts':['c009','c010','c012','c029','c031'],'jobs':jobs})
 p=a.read(H/'production-plan.json');p['rendererRevision']={'choice':'Unity world-only grayscale and object animation; measured 2D transparent brand labels and official photographs composited afterward','reason':'Two native overlay-camera attempts omitted UI, and one bounded second-pass diagnosis erased the world color buffer. Preserve correct native world output and existing2D composition responsibility. No further URP stack patches.','sourceStage':a.artifact(H/'unity-src/D25ColorClarityStage.cs'),'uiSource':a.artifact(H/'ui_compositor.py'),'sameCueFile':a.artifact(H/'unity-cues.json'),'nativeCutCount':18,'photoOnlyCutCount':5,'photoOnlyExplanationClassification':True,'actualRenderedPixels':'two bounded 1080/375 native-world/UI/caption still proofs inspected; complete capture/encoding remains pending','oldFailedEvidencePreserved':True}
 a.save(H/'production-plan.json',p)
 checkpoint=a.read(H/'checkpoint.json');checkpoint.update(status='measured-cues-locked-world-only-and-2d-ui-ready',sourceStageSha256=a.sha(H/'unity-src/D25ColorClarityStage.cs'));checkpoint['measuredTiming'].update(status='locked',activeCueJsonChanged=True,nativeExplanationCuts=18,photoOnlyExplanationCuts=5);checkpoint['nativeQa'].update(activeCueTimingLocked=True,stagedSourceSha256=a.sha(H/'unity-src/D25ColorClarityStage.cs'),repairPixelVerification='bounded postcomposited grayscale/world/photo/UI/caption stills pass; full native moving preflight pending',worldOnly=True);a.save(H/'checkpoint.json',checkpoint)
 print(json.dumps({'nativeJobs':len(jobs),'photoOnly':5,'sourceSha256':a.sha(H/'unity-src/D25ColorClarityStage.cs'),'cueSha256':a.sha(H/'unity-cues.json'),'jobsSha256':a.sha(H/'capture-jobs.json')}))
if __name__=='__main__':main()
