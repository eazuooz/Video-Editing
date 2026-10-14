"""New dense annotation anchors only; reuse all matching sealed source images."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,psutil
from PIL import Image,ImageDraw,ImageFont
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
OUT=R/'annotation-anchor-native-v1'
STATE=R/'annotation-anchor-execution-v1.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
now=lambda:datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
assert not STATE.exists() and not OUT.exists(),'Inspect existing annotation anchors; do not repeat.'
assert not (R/'narration-tts-execution-v1.json').exists(),'Own model job started; finish voice before a new heavy CPU job.'
resource=dict(observedAt=now(),cpuLoadPercent=psutil.cpu_percent(interval=1),freePhysicalMemoryBytes=psutil.virtual_memory().available,
    cim=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg' -and $_.CommandLine -match 'orientation|gpu-handoff|train_|placement_focus' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"],text=True,encoding='utf8')),
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True).strip(),foreignManipulations=0)
assert resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryBytes']>8_000_000_000
save(R/'resource-before-annotation-anchors-v1.json',resource)
bank=read(R/'conservative-source-recut-proposal-v2.json')
defs=[('05',160),('08',269),('11',382),('14',891),('17',630),('20',688),('23',871)]
windows=[]
for sid,start in defs:
    a=start*60;b=a+360
    assert any(x['scene']==sid and x['firstNativeFrame']<=a and b<=x['endExclusiveNativeFrame'] for x in bank['windows'])
    frames=sorted(set(range(a,b,15))|{b-1})
    windows.append(dict(scene=sid,startNativeFrame=a,endNativeFrameExclusive=b,sourcePtsIn=a*256,sourcePtsOutExclusive=b*256,targetNativeFrames=frames))
prior={}
for name in ['selected-native-v1','repair-candidate-native-v1']:
    for x in read(R/name/'manifest.json')['samples']:prior[x['sourceFrame']]=x
source=ROOT/bank['source'];assert sha(source)==bank['sourceSha256']
OUT.mkdir();me=psutil.Process()
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),cpuThreads=2,gpuJobs=0,
    status='extracting-new-annotation-anchors',sessionId=None,workerExitCode=None,actualOuterExitCode=None,resource=resource)
save(STATE,state);samples=[];commands=[]
try:
    for w in windows:
        assert not (R/'narration-tts-execution-v1.json').exists(),'Preserve completed anchor windows; wait for own voice before continuing.'
        reused={f:prior[f] for f in w['targetNativeFrames'] if f in prior}
        assert all(sha(ROOT/x['path'])==x['sha256'] for x in reused.values())
        fresh=[f for f in w['targetNativeFrames'] if f not in reused]
        folder=OUT/('scene-'+w['scene']);folder.mkdir()
        select='+'.join(f'eq(pts,{f*256})' for f in fresh)
        cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-ss',str(w['startNativeFrame']/60-.5),'-copyts','-i',str(source),'-an','-vf',f"select='{select}',showinfo",'-fps_mode','passthrough','-frames:v',str(len(fresh)),'-threads','2','-compression_level','3',str(folder/'sample-%03d.png')]
        commands.append(dict(scene=w['scene'],command=cmd))
        log=folder/'extract.log'
        with log.open('wb') as f:
            process=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
            state.update(ffmpegPid=process.pid,ffmpegCreateTime=psutil.Process(process.pid).create_time(),currentScene=w['scene']);save(STATE,state)
            rc=process.wait()
        actual=[int(x) for x in re.findall(r'Parsed_showinfo_\d+.*?\bpts:\s*(-?\d+)',log.read_text('utf8'))]
        files=sorted(folder.glob('sample-*.png'))
        assert rc==0 and actual==[f*256 for f in fresh] and len(files)==len(fresh),(w['scene'],rc,len(actual),len(files))
        byframe={f:dict(path=rel(p),sha256=sha(p),sourceFrame=f,pts=f*256,seconds=f/60,reused=False) for f,p in zip(fresh,files)}
        byframe.update({f:{**x,'reused':True} for f,x in reused.items()})
        samples.extend([{**byframe[f],'scene':w['scene'],'localFrame':f-w['startNativeFrame']} for f in w['targetNativeFrames']])
    boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
    for w in windows:
        rows=[x for x in samples if x['scene']==w['scene']]
        for offset in range(0,len(rows),6):
            im=Image.new('RGB',(1280,1176),'#171717');draw=ImageDraw.Draw(im)
            for j,x in enumerate(rows[offset:offset+6]):
                px=j%2*640;py=j//2*392
                with Image.open(ROOT/x['path']) as frame:im.paste(frame.resize((640,360)),(px,py))
                draw.text((px+6,py+365),f"scene{x['scene']} local{x['localFrame']} native{x['sourceFrame']} PTS{x['pts']}",font=font,fill='white')
            p=OUT/f"scene-{w['scene']}-board-{offset//6+1:02d}.png";im.save(p)
            boards.append(dict(path=rel(p),sha256=sha(p),scene=w['scene'],samples=[x['path'] for x in rows[offset:offset+6]]))
    save(OUT/'commands.json',commands)
    manifest=dict(source=bank['source'],sourceSha256=bank['sourceSha256'],nativeTimebase='1/15360',nativePtsStep=256,
        exactRequestedPtsMatched=True,windows=windows,samples=samples,boards=boards,pointAnnotationsApproved=False,finalPixelsApproved=False)
    save(OUT/'manifest.json',manifest)
    state.update(status='completed-new-anchor-samples-awaiting-direct-read',workerExitCode=0,finishedAt=now(),manifest=rel(OUT/'manifest.json'),
        samples=len(samples),freshSamples=sum(not x['reused'] for x in samples),reusedSamples=sum(x['reused'] for x in samples),boards=len(boards))
    save(STATE,state);print(json.dumps({k:state[k] for k in ['workerExitCode','samples','freshSamples','reusedSamples','boards']}))
except BaseException as e:
    state.update(status='failed-preserve-available-anchor-windows',workerExitCode=1,error=repr(e),finishedAt=now());save(STATE,state);raise
