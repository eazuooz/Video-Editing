"""Prepare M27 representative source-step render checks, explicitly preview timing."""
from pathlib import Path
import json,copy,argparse
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='v1');args=ap.parse_args();assert args.revision.isalnum()
S=Path(__file__).resolve().parent;W=S/('local-preflight-'+args.revision);assert not W.exists();W.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prep=read(S/'sandbox-preparation.json');plan=read(S/'force-shots.json');jobs=[]
for row in plan['shots']:
 sid=row['sceneId']
 if int(sid) not in {2,3,4,8,10,11,12,13,17,22,25,27,28,29,30}:continue
 shot=copy.deepcopy(row['shot']);shot['durationSeconds']=8;cue=W/(sid+'.shot.json');save(cue,shot)
 job=dict(id='m27-preflight-'+args.revision+'-'+sid,projectSlug='game-math-forces-friction',command='preflight',output=str(W/sid),ffmpeg='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe',expectedFingerprint=prep['fingerprint'],shotFile=str(cue),factoryType='MechanicsSceneBuilder',frames=480,sampleFrames=[0,120,240,420],speechTimingVerified=False)
 jp=W/(sid+'.job.json');save(jp,job);jobs.append(str(jp))
save(W/'queue.json',dict(project='game-math-forces-friction',episode='M27',sandbox=prep['sandbox'],fingerprint=prep['fingerprint'],unity='C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe',jobs=jobs,actualSpeech=False,rigValidationRequired=False,scope='Fifteen prop/model/layout previews; no final speech or media approval'))
print('Prepared',len(jobs),'M27 preview jobs; no renderer launched')
