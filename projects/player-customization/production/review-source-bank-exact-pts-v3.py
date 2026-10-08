"""Single CPU2 extraction of prospective source intervals at actual native PTS.

This is research review, not source allocation or quota approval. The older
fps=1/5 boards have nominal navigation labels. These images instead identify
the selected original decoded frame and its actual presentation timestamp.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, bisect, ctypes, hashlib, json, os, subprocess, sys, time, traceback

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
OUT = ROOT/'shared/output/player-customization/research/source-bank-exact-pts-v3'
STATE = BASE/'source-bank-exact-pts-review-execution-v3.json'
SESSION = STATE.with_name(STATE.stem+'.session.json')
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
PROBE = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def save(p, value):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n','utf-8')
    for retry in range(40):
        try: os.replace(tmp,p); return
        except OSError:
            if retry==39: raise
            time.sleep(.15)

ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
resource=read(ROOT/args.resource)
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85
assert resource['freePhysicalMemoryKiB']>8_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert not STATE.exists() and not OUT.exists(), 'Read/resume actual existing extraction.'
bank_path=ROOT/'projects/player-customization/sources/native-source-bank-v2.json'
bank=read(bank_path)
rows=list(bank['rows'])
rows.append(dict(id='dante-round-actual352-v3',source='dante',localInSeconds=351.6,
    localOutSeconds=354.2,classification='actual-action-research-reserve',
    visibleAction='Distinct nearby round cyan effect and forward targets; CUA352.5 observed. Exact edge/middle still pending.'))
if os.name=='nt': ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True)
state=dict(schemaVersion=3,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],
    sessionId=None,startedAt=now(),status='reading-native-frame-PTS',resourceEvidence=args.resource,
    cpuThreads=2,gpu=0,singleJob=True,bankPath=rel(bank_path),bankSha256=sha(bank_path),operations=[],
    sourceActionApproved=False,sourceAllocationApproved=False,bodyRatioApproved=False,
    allPixelsDirectlyReviewed=False,finalCaptionPixelsApproved=False,newGitImages=0,exitCode=None)

def checkpoint():
    if SESSION.exists():
        launch=read(SESSION)
        if launch['pid']==os.getpid():state.update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity'])
    state['updatedAt']=now();save(STATE,state)
    job=dict(status=state['status'],pid=os.getpid(),commandLine=state['commandLine'],sessionId=state['sessionId'],
        processIdentity=state.get('processIdentity'),state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,
        exitCode=state['exitCode'],workerExpectedRunning=state['exitCode'] is None)
    cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob=job,
        nextAction='Read every prospective exact-PTS source board; reject occluded/static/notification portions and connect each actual action to narration before final allocation. No final ratio/mix/pair/collection/private approval.')
    save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
    item=next(i for i in q['items'] if i['slug']=='player-customization')
    item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)

def run(name,cmd):
    op=dict(name=name,commandLine=cmd,startedAt=now());state['operations'].append(op);state['status']=name;checkpoint()
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);op['pid']=p.pid;checkpoint()
    out,err=p.communicate();op.update(exitCode=p.returncode,finishedAt=now());(OUT/(name+'.stderr.log')).write_bytes(err);checkpoint()
    assert p.returncode==0,err.decode('utf-8','replace');return out

try:
    checkpoint();samples=[];source_records=[]
    for key,source in bank['sources'].items():
        path=ROOT/source['path'];assert sha(path)==source['sha256']
        raw=run('probe-native-pts-'+key,[PROBE,'-v','error','-threads','2','-select_streams','v:0',
            '-show_frames','-show_entries','frame=best_effort_timestamp,best_effort_timestamp_time',
            '-of','json',str(path)])
        (OUT/(key+'-native-frame-pts.json')).write_bytes(raw)
        fs=json.loads(raw)['frames'];pts=[float(f['best_effort_timestamp_time']) for f in fs]
        assert all(b>a for a,b in zip(pts,pts[1:])),key
        requested=[]
        for row in rows:
            if row['source']!=key:continue
            a,b=row['localInSeconds'],row['localOutSeconds'];ts=[a+.025,b-.025]
            t=a+.5
            while t<b-.025:ts.append(t);t+=.75
            for t in sorted(set(ts)):
                ix=bisect.bisect_left(pts,t);assert ix<len(pts) and pts[ix]<b
                requested.append(dict(rowId=row['id'],source=key,requestedSeconds=t,frameIndex=ix,
                    nativePts=int(fs[ix]['best_effort_timestamp']),nativeSeconds=pts[ix],
                    visibleAction=row['visibleAction'],classification=row['classification']))
        indices=sorted({s['frameIndex'] for s in requested});folder=OUT/key;folder.mkdir()
        crop=[636,108,1152,648] if key in ['dante','jade'] else [0,0,1920,1080]
        # UI shots are explanation; one generic composition here is only a
        # research overview. Final shot-specific stats/look/modal crops remain required.
        if key=='ui':crop=[634,200,1152,648]
        expression='+'.join(f'eq(n,{n})' for n in indices)
        run('extract-native-pts-'+key,[FF,'-nostdin','-v','error','-threads','2','-i',str(path),
            '-vf',f"select='{expression}',crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}",
            '-fps_mode','vfr','-an','-threads','2',str(folder/'frame-%04d.png')])
        images={n:folder/f'frame-{i:04d}.png' for i,n in enumerate(indices,1)}
        for s in requested:s.update(path=rel(images[s['frameIndex']]),sha256=sha(images[s['frameIndex']]),crop=crop)
        samples+=requested
        source_records.append(dict(key=key,path=source['path'],sha256=source['sha256'],frames=len(fs),
            firstNativeSeconds=pts[0],lastNativeSeconds=pts[-1],cropCandidate=crop,sampleCount=len(requested),uniqueExtractedFrames=len(indices)))
    from PIL import Image,ImageDraw,ImageFont
    folder=OUT/'boards';folder.mkdir();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);boards=[]
    # One board per prospective interval. This keeps chronological action
    # inspection and exclusions explicit, including the known questionable intervals.
    for row in rows:
        entries=[s for s in samples if s['rowId']==row['id']]
        for part,start in enumerate(range(0,len(entries),6),1):
            group=entries[start:start+6];board=Image.new('RGB',(1920,1194),'white');draw=ImageDraw.Draw(board)
            for i,s in enumerate(group):
                x,y=(i%2)*960,(i//2)*398
                draw.text((x+7,y+5),f"{row['id']} actual{s['nativeSeconds']:.4f}s n{s['frameIndex']}",font=font,fill='black')
                im=Image.open(ROOT/s['path']).convert('RGB');im.thumbnail((960,360));board.paste(im,(x+(960-im.width)//2,y+32))
            target=folder/f"{row['id']}-{part:02d}.png";board.save(target)
            boards.append(dict(rowId=row['id'],part=part,path=rel(target),sha256=sha(target),entries=group))
    state.update(status='native-PTS-source-candidates-extracted-awaiting-direct-review',exitCode=0,finishedAt=now(),
        rows=rows,sources=source_records,samples=samples,boards=boards,sampleCount=len(samples),boardCount=len(boards),
        oldCoarseLabelsWereOnlyNavigation=True,sourceAudioUsed=False)
    checkpoint();print(json.dumps({'samples':len(samples),'boards':len(boards),'approved':False}),flush=True)
except BaseException:
    state.update(status='failed-native-PTS-source-review',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
