"""Prepare bounded source-layout diagnostics, never label them production footage."""
from pathlib import Path
from copy import deepcopy
import json,argparse
R=Path(__file__).resolve().parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--sandbox',default='LocalUnity-v1');ap.add_argument('--revision',default='local-preflight-v1');a=ap.parse_args()
 slugs=['game-math-parametric-hermite','game-math-bezier-subdivision','game-math-splines-continuity'];assert a.project in slugs;episode=31+slugs.index(a.project)
 P=R/'projects'/a.project;S=P/'production/unity-staging';sandbox=S/a.sandbox;marker=read(sandbox/'MATH_CAPTURE_SANDBOX.json');out=S/a.revision;assert not out.exists();out.mkdir()
 ffmpeg=read(R/'projects/game-math-momentum-collisions/production/unity-staging/local-preflight-v1/001.job.json')['ffmpeg'];jobs=[]
 for row in read(S/'curve-shots.json')['shots']:
  sid=row['sceneId'];shot=deepcopy(row['shot']);n=len(shot['steps']);shot['durationSeconds']=max(8,n*4);shot['stepSeconds']=[];shot['stepPositions']=[]
  sp=out/(sid+'.shot.json');save(sp,shot);frames=round(shot['durationSeconds']*60)
  samples=sorted(set([0]+[min(frames-1,round(frames*(i+f)/n)) for i in range(n) for f in [.25,.65,.95]]))
  job=dict(id=f'm{episode}-{a.revision.replace("local-","")}-{sid}',projectSlug=a.project,command='preflight',output=str(out/sid),ffmpeg=ffmpeg,expectedFingerprint=marker['fingerprint'],shotFile=str(sp),factoryType='CurveSceneBuilder',frames=frames,sampleFrames=samples,speechTimingVerified=False)
  jp=out/(sid+'.job.json');save(jp,job);jobs.append(str(jp))
 save(out/'queue.json',dict(project=a.project,episode=f'M{episode}',sandbox=str(sandbox),fingerprint=marker['fingerprint'],unity='C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe',jobs=jobs,actualSpeech=False,rigValidationRequired=False,scope='Source-ordered mathematical geometry only; actual speech timing and final media unverified'))
 print(a.project,len(jobs),'diagnostic jobs prepared; not started')
if __name__=='__main__':main()
