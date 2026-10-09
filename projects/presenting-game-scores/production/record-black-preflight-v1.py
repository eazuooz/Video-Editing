from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def identity(pid,contains):
 p=psutil.Process(pid);cmd=p.cmdline()
 assert contains in ' '.join(cmd),cmd
 return dict(pid=pid,createTime=p.create_time(),commandLine=cmd)
proof=read(BASE/'prepared-independent-mc-v1.json')
proof['files']=[dict(path=f['path'],sha256=sha(ROOT/f['path'])) for f in proof['files']]
proof['updatedAt']=datetime.now(timezone.utc).isoformat()
proof['membershipRerendered']=False
proof['scopedTypeScript']={'command':'node node_modules/typescript/bin/tsc --noEmit --project tsconfig.presenting-game-scores.json','exitCode':0,'scope':'Current project, imported shared components and style; global failures in other unfinished projects remain separate'}
write(BASE/'prepared-independent-mc-v1.json',proof)
record=dict(schemaVersion=1,slug='presenting-game-scores',recordedAt=proof['updatedAt'],stage='black-structural-preview-render-returned',
 previewServer={**identity(63080,'vite.presenting-game-scores.black-preflight-v1.config.ts'), 'sessionId':31622,'url':'http://127.0.0.1:9251/','cuaTabId':'135'},
 renderer=dict(pid=59652,creationDate='2026-10-09T13:17:34.323889+09:00',parentPid=63080,
 commandLine='ffmpeg.exe -f image2pipe -r 60 -i pipe:0 -y -r 60 -filter:v scale=w=1920:h=1080 -pix_fmt yuv420p -shortest -movflags +faststart -threads 2 -filter_threads 1 -preset veryfast -crf 18 -video_track_timescale 90000 .../presenting-game-scores-structural-preview.mp4',
 previouslyCimObserved=True,currentlyAlive=psutil.pid_exists(59652),cpuThreads=2,gpu=0,exitCode=None,exitCodeDirectlyObserved=False,uiRenderButtonReturned=True),
 voiceWaiting={**identity(38172,'render-voice-v1.py'),'sessionId':30677,'modelLoaded':False,'ownedResearchPauseOrProcessChanges':0},
 output='shared/output/presenting-game-scores/black-structural-preview-v1/presenting-game-scores-structural-preview.mp4',
 timingMeasured=False,renderComplete=False,actualAnimatedPixelsReviewed=False,finalMediaApproved=False,
 nextAction='Read actual renderer completion and inspect all structural paragraph states and animated spatial relationships; preserve voice waiting process and foreign lease.')
write(BASE/'black-structural-preview-execution-v1.json',record)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath)
item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
item['structuralPreview']=dict(evidence=str((BASE/'black-structural-preview-execution-v1.json').relative_to(ROOT)).replace('\\','/'),**record)
item['nextAction']=record['nextAction'];q['updatedAt']=record['recordedAt']
write(qpath,q)
print('Actual single CPU2 structural renderer and serialized pre-model voice request recorded; final gates remain false.')
