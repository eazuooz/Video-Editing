"""Seal the actual v3 direct review and inspect six exact source HUD frames."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess,os,psutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
notes=read(BASE/'selected-input-direct-review-notes-v3.json');p=BASE/'selected-input-preflight-v3.json';d=read(p)
assert sorted(b for g in notes['groups'] for b in g['boards'])==list(range(1,142))
assert notes['allBoardsRead'] and notes['all845SamplesRead'] and not notes['inputPixelApproval']
for rows in (d['samples'],d['boards'],d['segments']):
 for row in rows:assert sha(ROOT/row['path'])==row['sha256'],row['path']
for key in ('plan','captionCandidate','bodyPath'):assert sha(ROOT/d[key])==d[key.replace('Path','')+'Sha256' if key=='bodyPath' else key+'Sha256']
assert len(d['samples'])==845 and len(d['boards'])==141 and all(s['pts']==s['frame']*1500 for s in d['samples'])
proof=BASE/'selected-input-direct-review-v3.json';assert not proof.exists()
save(proof,dict(schemaVersion=3,reviewedAt=now(),preflight=rel(p),preflightSha256=sha(p),all845SampleHashesVerified=True,all141BoardHashesVerified=True,all41SegmentHashesVerified=True,allBoardsDirectlyRead=True,allPlannedSamplesDirectlyRead=True,groups=notes['groups'],inputPixelApproval=False,finalTimingApproved=False,allContinuousFramesReviewed=False,humanListeningApproved=False,issues=['Scene02 moving cube hides 이동 label at body1552/1554/1586.','Enlarged damage HUD bottoms at6674/6676 and16847/16888 need source-vs-framing diagnostic.'],rasterGitAdditions=0,mediaGitAdditions=0))
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='selected-input-v3-direct-review-held-label-and-transient-HUD',selectedInputDirectReview=rel(proof),nextAction='Diagnose exact native HUD frames and repair only scene02 label and affected shared HUD framing. Preserve all completed v3 media/QA/voice/caption/timing.');cp['ownedJob'].update(sessionId=33900,exitCode=0,activeOperation=None,active=False);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items'] if i['slug']=='character-parameters');item.update(stage=cp['stage'],currentExecution=cp['ownedJob'],selectedInputDirectReview=rel(proof),nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
r=read(BASE/'resource-before-input-repair-v4.json');assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
out=ROOT/'shared/output/character-parameters/hud-diagnostic-v4';assert not out.exists();out.mkdir(parents=True)
src=ROOT/'shared/assets/character-parameters/raw/gBbKFYZYvbc.mp4';assert sha(src)=='96b6046ca1258292f7798bc3531a77ea35564fba7b28c22d9258045aab9d5771'
frames=[1776,1777,7523,7543,7839,7840];FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
cmd=[FF,'-nostdin','-hide_banner','-v','error','-threads','2','-i',str(src),'-filter_threads','1','-vf',"select='"+'+'.join('eq(pts,%d)'%(f*3000) for f in frames)+"'",'-fps_mode','vfr','-frames:v','6',str(out/'source-%02d.png')]
result=subprocess.run(cmd,capture_output=True,text=True);assert result.returncode==0,result.stderr
board=Image.new('RGB',(1280,6*190),'#222222');draw=ImageDraw.Draw(board)
rows=[]
for n,f in enumerate(frames,1):
 p=out/('source-%02d.png'%n);im=Image.open(p);assert im.size==(1280,720)
 # Show original bottom 170 px without rescaling or changing source pixels.
 board.paste(im.crop((0,550,1280,720)),(0,(n-1)*190+20));draw.text((8,(n-1)*190+3),f'native frame {f} / PTS {f*3000}',fill='white');rows.append(dict(nativeFrame=f,pts=f*3000,path=rel(p),sha256=sha(p)))
bp=out/'source-hud-six-native-frames.png';board.save(bp)
save(BASE/'hud-source-diagnostic-extraction-v4.json',dict(recordedAt=now(),source=rel(src),sourceSha256=sha(src),cpuThreads=2,gpuJobs=0,processIdentity=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=psutil.Process().cmdline(),cwd=str(ROOT)),extractionExitCode=result.returncode,samples=rows,board=dict(path=rel(bp),sha256=sha(bp)),directReviewPending=True,localOnly=True,rasterGitAdditions=0))
print(json.dumps(dict(review=rel(proof),diagnosticBoard=rel(bp),sourceFrames=frames,extractionExitCode=0)))
