"""Finite M26 sample instructions with explicit preview-only timing."""
from pathlib import Path
import argparse,copy,json
P=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='v1');args=ap.parse_args();assert args.revision.isalnum()
prep=read(P/'sandbox-preparation.json');plan=read(P/'circular-shots.json');W=P/('local-preflight-'+args.revision);assert not W.exists();W.mkdir()
jobs=[]
for row in plan['shots']:
    if int(row['sceneId']) not in {3,5,9,11,15,16,18,21,23,28,29,31,36,38}:continue
    sid=row['sceneId'];shot=copy.deepcopy(row['shot']);shot.update(durationSeconds=8,stepSeconds=[],stepPositions=[])
    cue=W/(sid+'.shot.json');save(cue,shot)
    job={'id':'m26-preflight-'+args.revision+'-'+sid,'projectSlug':'game-math-circular-motion','command':'preflight','output':str(W/sid),'ffmpeg':'C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe','expectedFingerprint':prep['fingerprint'],'shotFile':str(cue),'factoryType':'MotionSceneBuilder','frames':480,'sampleFrames':[0,120,240,420],'speechTimingVerified':False}
    p=W/(sid+'.job.json');save(p,job);jobs.append(str(p))
save(W/'queue.json',{'project':'game-math-circular-motion','episode':'M26','sandbox':prep['sandbox'],'fingerprint':prep['fingerprint'],'unity':'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','jobs':jobs,'actualSpeech':False,'rigValidationRequired':False,'scope':'Fourteen mathematical diagram/plot runtime samples; not final voice timings or complete visual QA'})
print('Prepared',len(jobs),'M26 preview instructions; no editor launched.')
