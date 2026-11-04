"""Prepare source-ordered M23 diagnostic pictures; no renderer or TTS launch."""
from pathlib import Path
import argparse,copy,json,math
P=Path(__file__).resolve().parents[1];S=P/'production/unity-staging'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--revision',required=True);ap.add_argument('--sandbox',required=True);a=ap.parse_args()
sandbox=(S/a.sandbox).resolve();marker=read(sandbox/'MATH_CAPTURE_SANDBOX.json');folder=(S/a.revision).resolve()
assert folder.parent==S.resolve() and not folder.exists()
folder.mkdir();scenes={r['id']:r for r in read(P/'planning/scene-bindings.json')['scenes']}
old=read(S/'local-preflight-v2/queue.json');selected=sorted({Path(j).name.split('.')[0] for j in old['jobs']}|{'024','025','060','066'})
jobs=[]
for sid in selected:
 row=scenes[sid];shot=copy.deepcopy(row['shot']);anchors=row['speechPhaseAnchors'];steps=max(2,len(anchors));duration=max(8,4*steps)
 shot['durationSeconds']=duration;shot['phaseSeconds']=[];shot['phasePositions']=[]
 # Inspect both sides of each discrete transition; synthetic time is never
 # reused as final speech timing. Actual phrase timestamps replace it later.
 positions={0.0,.25,.5,.875}
 for anchor in anchors:
  pos=anchor['position'];positions.update([max(0,pos-.012),min(.999,pos+.012)])
 if shot.get('stepOrder'):
  positions.update((i+.5)/len(shot['stepOrder']) for i in range(len(shot['stepOrder'])))
 frames=math.ceil(duration*60);samples=sorted({min(frames-1,round(u*frames)) for u in positions})
 sp=folder/f'{sid}.shot.json';jp=folder/f'{sid}.job.json';save(sp,shot)
 save(jp,dict(id=f'm23-{a.revision}-{sid}',projectSlug=P.name,command='preflight',output=str(folder/sid),ffmpeg=read(Path(old['jobs'][0]))['ffmpeg'],expectedFingerprint=marker['fingerprint'],shotFile=str(sp),factoryType='PipelineSceneBuilder',frames=frames,sampleFrames=samples,speechTimingVerified=False))
 jobs.append(str(jp))
 save(folder/'queue.json',dict(project=P.name,episode='M23',sandbox=str(sandbox),fingerprint=marker['fingerprint'],unity=old['unity'],jobs=jobs,actualSpeech=False,scope='Updated source-order, material exercise and winding diagnostic pictures; final speech/moving QA pending',rigValidationRequired=False))
print(f'{len(jobs)} targeted scenes prepared; no renderer started.')
