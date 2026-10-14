"""Compare decoded frames; equality never substitutes for direct pixel approval."""
from pathlib import Path
import json, hashlib, subprocess, os
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
L=ROOT/'production/research/game-lighting-history/local/part1-decoded-comparison-v314'
L.mkdir(exist_ok=True)
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
statePath=P/'part1-decoded-comparison-execution-v314.json'
assert not statePath.exists(), 'Do not rerun completed work'
old=read(P/'part1-reviewed-pair-build-v293.json')
new=read(P/'part1-reviewed-pair-build-v313.json')
assert old['captioned']['frames']==new['captioned']['frames']==89148
state=dict(startedAt=stamp(),status='running',workerPid=os.getpid(),cpuThreads=2,gpuJobs=0,commands=[],pixelApproval=False)
def save():
 t=statePath.with_suffix('.writing.json');t.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf8');t.replace(statePath)
save()
parsed=[]
for tag,build in [('old293',old),('current313',new)]:
 src=ROOT/build['captioned']['path'];assert sha(src)==build['captioned']['sha256']
 dest=L/(tag+'.framemd5');assert not dest.exists()
 cmd=[str(FF),'-n','-v','error','-nostdin','-threads','2','-i',str(src),'-map','0:v:0','-an','-fps_mode','passthrough','-c:v','rawvideo','-threads','2','-f','framemd5',str(dest)]
 with (L/(tag+'.log')).open('wb') as log:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  row=dict(tag=tag,pid=child.pid,commandLine=cmd,startedAt=stamp(),sourceSha256=build['captioned']['sha256']);state['commands'].append(row);save()
  row.update(exitCode=child.wait(),completedAt=stamp());save();assert row['exitCode']==0
 frames=[line.split(',')[-1].strip() for line in dest.read_text().splitlines() if line and not line.startswith('#')]
 assert len(frames)==89148
 parsed.append(frames)
changed=[i for i,(a,b) in enumerate(zip(*parsed)) if a!=b]
ranges=[]
for n in changed:
 if ranges and n==ranges[-1][1]:ranges[-1][1]=n+1
 else:ranges.append([n,n+1])
record=dict(createdAt=stamp(),oldCaptionedSha256=old['captioned']['sha256'],currentCaptionedSha256=new['captioned']['sha256'],frameCount=89148,exactDecodedFrames=89148-len(changed),differentDecodedFrames=len(changed),differentFrameRangesExclusive=ranges,hashFiles=[dict(path=str((L/(tag+'.framemd5')).relative_to(ROOT)).replace('\\','/'),sha256=sha(L/(tag+'.framemd5'))) for tag in ['old293','current313']],directPixelApproval=False,historicalIssuesPreserved=True,newGitImages=0)
(P/'part1-decoded-pixel-comparison-v314.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
state.update(status='complete',exitCode=0,completedAt=stamp(),comparisonPath='projects/game-lighting-history-04/production/part1-decoded-pixel-comparison-v314.json');save()
print(json.dumps({k:record[k] for k in ['frameCount','exactDecodedFrames','differentDecodedFrames','differentFrameRangesExclusive']}))
