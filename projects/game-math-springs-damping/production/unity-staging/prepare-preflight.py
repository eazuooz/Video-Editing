"""Representative M28 runtime/image checks; preview time is not speech timing."""
from pathlib import Path
import json,copy,argparse
S=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='v1');a=ap.parse_args();assert a.revision.startswith('v') and a.revision[1:].isdigit()
W=S/('local-preflight-'+a.revision);assert not W.exists();W.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prep=read(S/'sandbox-preparation.json');plan=read(S/'spring-shots.json');jobs=[]
for row in plan['shots']:
 sid=row['sceneId']
 if int(sid) not in {1,2,5,6,8,9,11,14,15,18,19,20,21,22,23}:continue
 shot=copy.deepcopy(row['shot']);shot['durationSeconds']=8;cue=W/(sid+'.shot.json');save(cue,shot)
 job=dict(id='m28-preflight-'+a.revision+'-'+sid,projectSlug='game-math-springs-damping',command='preflight',output=str(W/sid),ffmpeg='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe',expectedFingerprint=prep['fingerprint'],shotFile=str(cue),factoryType='MechanicsSceneBuilder',frames=480,sampleFrames=[0,120,240,420],speechTimingVerified=False)
 jp=W/(sid+'.job.json');save(jp,job);jobs.append(str(jp))
save(W/'queue.json',dict(project='game-math-springs-damping',episode='M28',sandbox=prep['sandbox'],fingerprint=prep['fingerprint'],unity='C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe',jobs=jobs,actualSpeech=False,rigValidationRequired=False,scope='Fifteen spring/initial-condition/code/integration previews; no final speech or media approval'))
print('Prepared',len(jobs),'M28 preview jobs; renderer not started')
