"""CPU-only native anchors; reuse exact previously extracted source frames."""
import json,hashlib,subprocess,os,psutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/extra-anchors-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
state_path=R/'extra-anchors-execution-v1.json'
assert not state_path.exists(), 'Never duplicate or overwrite an extraction.'
cpu=psutil.cpu_percent(interval=1);ram=psutil.virtual_memory().available//1024
assert cpu<85 and ram>8000000,(cpu,ram)
own_names=['render-motion-narration-timed-comparisons-v1.cjs','qa-motion-narration-timed-comparisons-v1.py',
           'extract-motion-extra-native-v1.py','extract-motion-extra-native-v2.py','extract-motion-extra-anchors-v1.py']
busy=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
    c=' '.join(p.info['cmdline'] or [])
    if p.pid!=os.getpid() and p.info['cmdline'] and any(n in c for n in own_names):
        if (p.info['cmdline'][0].lower().endswith('python.exe') or p.info['cmdline'][0].lower().endswith('node.exe')): busy.append(p.info)
assert not busy,busy
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
assert len(protected)==71
for x in protected: assert sha(ROOT/x['path'])==x['sha256'],x['path']
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip()
process_snapshot=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|node|ffmpeg' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"],capture_output=True,text=True,check=True).stdout
(R/'extra-anchors-current-process-cim-v1.json').write_text(process_snapshot,'utf-8')
plan=read(R/'narration-led-cut-allocation-proposal-v2.json')
sources=plan['cuts']
sources[0]['frames']=list(range(1289,1739,15))+[1738]
sources[1]['frames']=list(range(14040,14821,15))
previous={}
for f in ['extra-native-execution-v1.json','extra-native-execution-v2.json']:
    for s in read(R/f)['samples']: previous[(s['source'],s['frame'])]=s
state=dict(schemaVersion=1,startedAt=stamp(),pid=os.getpid(),createTime=psutil.Process().create_time(),
    resource=dict(cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,gpuRaw=gpu,ownedHeavyOtherJobs=0,
                  cimEvidence='extra-anchors-current-process-cim-v1.json'),
    sources=sources,cpuThreads=2,gpuJobs=0,protected71ShaMatched=True,status='running',
    actualOuterExitCode=None,results=[],samples=[],boards=[],freshSamples=0,reusedSamples=0)
def save(): state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
OUT.mkdir(parents=True,exist_ok=True);save()
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(ownedJob=dict(status='running',active=True,sessionId=None,pid=os.getpid(),createTime=state['createTime'],
          command='extract-motion-extra-anchors-v1.py',state=state_path.relative_to(ROOT).as_posix()),activeOwnedWorkers=1,
          next='Use actual anchor worker identity/session; do not duplicate. After completion read new84 native anchor samples/21boards, reuse exact old23 frames without re-extraction, then track actual screen roles and map narration-led cuts.')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
for row in sources:
    assert sha(ROOT/row['path'])==row['sha256']
    fresh=[n for n in row['frames'] if (row['path'],n) not in previous]
    folder=OUT/row['id'];folder.mkdir(exist_ok=True)
    if fresh:
        select='+'.join('eq(n\\,%d)'%n for n in fresh)
        run=subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','2','-filter_threads','2',
          '-i',str(ROOT/row['path']),'-vf',f'select={select},scale=1280:720','-fps_mode','passthrough','-an',str(folder/'fresh-%03d.png')],capture_output=True,text=True)
        state['results'].append(dict(id=row['id'],exitCode=run.returncode,stderr=run.stderr[-2000:]));save()
        assert run.returncode==0,run.stderr
    fi=0
    for n in row['frames']:
        old=previous.get((row['path'],n))
        if old:
            p=ROOT/old['path'];assert sha(p)==old['sha256'];state['reusedSamples']+=1
        else:
            fi+=1;p=folder/f'fresh-{fi:03d}.png';assert p.exists();state['freshSamples']+=1
        state['samples'].append(dict(id=row['id'],frame=n,pts=n*row['ptsStep'],timeBase=row['timeBase'],
           seconds=n*row['ptsStep']/(30000 if row['game']=='Portal2' else 15360),path=p.relative_to(ROOT).as_posix(),
           sha256=sha(p),source=row['path'],reused=bool(old)))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for start in range(0,len(state['samples']),4):
    chunk=state['samples'][start:start+4];board=Image.new('RGB',(1920,1160),'#e4e7ec');d=ImageDraw.Draw(board)
    for k,s in enumerate(chunk):
        x=k%2*960;y=k//2*580
        board.paste(Image.open(ROOT/s['path']).resize((960,540)),(x,y+40))
        d.text((x+8,y+5),f"{s['id']} native{s['frame']} {s['seconds']:.3f}s",font=font,fill='black')
    p=OUT/f'board-{len(state["boards"])+1:02d}.png';board.save(p)
    state['boards'].append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=chunk))
state.update(status='completed-awaiting-anchor-direct-review',finishedAt=stamp(),sampleCount=len(state['samples']),
    boardCount=len(state['boards']),directPixelReview=False,finalCutAllocationApproved=False)
save();print(json.dumps(dict(samples=state['sampleCount'],boards=state['boardCount'],fresh=state['freshSamples'],reused=state['reusedSamples'],allFfmpegExitCodes=[x['exitCode'] for x in state['results']])))
