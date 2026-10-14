"""One CPU2/GPU0 job: missing exact-PTS candidate frames only, reusing coarse PNGs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, subprocess, sys, traceback
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[4]
PROOF=Path(__file__).resolve().parent
STATE=PROOF/'chicory-native-candidate-execution-v1.json'
QA=ROOT/'shared/output/limited-color-world/preflight/chicory-native-v1'
QUEUE=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p):return str(p.relative_to(ROOT)).replace('\\','/')
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
assert not STATE.exists(), 'Existing worker; inspect its actual state, never rerun.'
check=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert check.returncode==0,check.stdout+check.stderr
plan_path=PROOF/'chicory-native-action-plan-v1.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
coarse_path=PROOF/'chicory-coarse-direct-review-v1.json';coarse=json.loads(coarse_path.read_text(encoding='utf-8'))
state={'schemaVersion':1,'slug':'limited-color-world','status':'initializing','startedAt':stamp(),
    'pid':os.getpid(),'processCreateTime':psutil.Process().create_time(),'commandLine':sys.argv,'workingDirectory':str(ROOT),
    'sessionId':None,'cpuThreads':2,'gpuJobs':0,'children':[],'sources':[],'windows':[],
    'plan':rel(plan_path),'planSha256':sha(plan_path),'coarseReview':rel(coarse_path),'coarseReviewSha256':sha(coarse_path),
    'check':{'exitCode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},
    'allNativePixelsDirectlyRead':False,'nativeActionBoundaryApproved':False,'finalCaptionUiApproved':False,
    'sourceFootageAdopted':False,'projectScriptTtsMcCreated':False,'publicRightsApproved':False,
    'researchManipulated':False,'researchResumeClaim':False,'gitImagesOrMediaAdded':0}
QA.mkdir(parents=True,exist_ok=True)
def save(status):
    state.update(status=status,updatedAt=stamp())
    sp=STATE.with_name(STATE.name+'.session.json')
    if sp.exists():
        session=json.loads(sp.read_text(encoding='utf-8-sig'))
        if session.get('pid')==os.getpid():state['sessionId']=session['sessionId']
    write(STATE,state)
    before=QUEUE.read_bytes();q=json.loads(before);item=next(x for x in q['items'] if x['slug']=='limited-color-world')
    assert item['videoId'] is None and not any(item['checkpoints'].values())
    item.update(stage='chicory-native-'+status,updatedAt=state['updatedAt'])
    item['execution']={k:state[k] for k in ('status','pid','processCreateTime','commandLine','workingDirectory','sessionId','cpuThreads','gpuJobs')}
    item['execution'].update(phase='chicory-missing-exact-native-pts-inspection',state=rel(STATE),child=state['children'][-1] if state['children'] else None)
    item['nextAction']='Read all exact-PTS native candidate boards and critical full-size pixels; confirm normal-speed action and caption/UI composition before adoption or dependent narration.'
    q['updatedAt']=q['lastProgressAt']=state['updatedAt'];assert QUEUE.read_bytes()==before;write(QUEUE,q)
try:
    cim=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg|ffprobe' -or $_.ProcessId -in 27140,63080,56464 } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    write(PROOF/'chicory-resource-before-native-v1.json',{'recordedAt':stamp(),'processCim':cim.stdout.decode('utf-8-sig',errors='replace'),'gpu':gpu.stdout.decode().strip(),'ownJob':'single CPU2/GPU0 native candidate extraction','foreignJobsPreserved':True,'researchManipulated':False})
    save('running')
    allmaps={}
    for source in coarse['verifiedSources']:
        key=source['source'];windows=[w for w in plan['candidateWindows'] if w['source']==key]
        media=ROOT/source['path'];assert sha(media)==source['sha256']
        native=json.loads((ROOT/source['nativePtsPath']).read_text(encoding='utf-8'))['frames']
        wanted=set()
        for w in windows:
            a,b=w['startFrame'],w['endFrameExclusive']
            wanted.update(range(a,b,30));wanted.update([a-1,a,a+1,b-1,b,b+1])
        wanted=sorted(n for n in wanted if 0<=n<len(native));wanted_pts=[int(native[n]['best_effort_timestamp']) for n in wanted]
        assert wanted_pts==[n*256 for n in wanted]
        reused={s['pts']:s for s in source['samples'] if s['pts'] in wanted_pts}
        missing=[p for p in wanted_pts if p not in reused]
        sub=QA/key;sub.mkdir(exist_ok=True);logpath=sub/'missing-exact-pts.log'
        if missing:
            expression='+'.join(f'eq(pts,{p})' for p in missing)
            args=[FF,'-nostdin','-n','-v','info','-threads','2','-filter_threads','2','-ss',f'{max(0,missing[0]/15360-1):.9f}','-copyts','-i',str(media),'-vf',"select='"+expression+"',showinfo",'-frames:v',str(len(missing)),'-fps_mode','passthrough','-an','-threads','2',str(sub/'native-%04d.png')]
            with logpath.open('wb') as log:
                c=subprocess.Popen(args,cwd=ROOT,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
                rec={'label':key+'-missing-native-extract','pid':c.pid,'processCreateTime':psutil.Process(c.pid).create_time(),'commandLine':args,'startedAt':stamp(),'status':'running','log':rel(logpath)}
                state['children'].append(rec);save('extracting');c.wait();rec.update(status='exited',exitCode=c.returncode,endedAt=stamp());assert c.returncode==0
            actual=[int(p) for p in re.findall(r'\bn:\s*\d+\s+pts:\s*(-?\d+)',logpath.read_text(encoding='utf-8',errors='replace'))]
            assert actual==missing, f'{key}: actual selected PTS mismatch, preserve outputs for investigation'
            files=sorted(sub.glob('native-*.png'));assert len(files)==len(missing)
            new={p:{'path':rel(ip),'sha256':sha(ip),'reusedCoarse':False} for p,ip in zip(actual,files)}
        else:new={}
        mapping={}
        for n,p in zip(wanted,wanted_pts):
            if p in reused:
                info=reused[p];assert sha(ROOT/info['path'])==info['sha256'];image={k:info[k] for k in ('path','sha256')};image['reusedCoarse']=True
            else:image=new[p]
            mapping[n]={**image,'nativeFrame':n,'pts':p,'timeSeconds':p/15360}
        allmaps[key]=mapping
        state['sources'].append({'key':key,'sourcePath':source['path'],'sourceSha256':source['sha256'],'timeBase':'1/15360','nativeFramePtsStep':256,'sampleCount':len(wanted),'reusedCoarseSamples':len(reused),'newSamples':len(missing),'actualSelectedPtsVerified':True,'extractExitCode':0,'sampleMap':list(mapping.values())})
        save('source-extracted')
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
    for w in plan['candidateWindows']:
        mapping=allmaps[w['source']];a,b=w['startFrame'],w['endFrameExclusive']
        indices=sorted(set(range(a,b,30))|{a-1,a,a+1,b-1,b,b+1})
        samples=[mapping[n] for n in indices if n in mapping];sub=QA/w['key'];sub.mkdir(exist_ok=True);boards=[]
        for off in range(0,len(samples),6):
            board=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(board)
            for k,s in enumerate(samples[off:off+6]):
                x=k%3*640;y=k//3*408
                with Image.open(ROOT/s['path']) as im:board.paste(im.convert('RGB').resize((640,360)),(x,y+36))
                d.text((x+6,y+3),w['key']+' f'+str(s['nativeFrame']),font=font,fill='white')
                d.text((x+6,y+384),f"PTS {s['pts']} t {s['timeSeconds']:.6f}",font=font,fill=(180,230,230))
            bp=sub/f'board-{off//6+1:03d}.jpg';board.save(bp,quality=93)
            boards.append({'path':rel(bp),'sha256':sha(bp),'sampleRange':[off,min(off+6,len(samples))]})
        state['windows'].append({**w,'samples':samples,'boards':boards,'directPixelReviewApproved':False})
    state.update(totalUniqueSamples=sum(s['sampleCount'] for s in state['sources']),newSamples=sum(s['newSamples'] for s in state['sources']),reusedCoarseSamples=sum(s['reusedCoarseSamples'] for s in state['sources']),totalBoards=sum(len(w['boards']) for w in state['windows']))
    save('exited-awaiting-direct-review')
    print(json.dumps({k:state[k] for k in ('status','totalUniqueSamples','newSamples','reusedCoarseSamples','totalBoards')},ensure_ascii=False),flush=True)
except BaseException:
    state['error']=traceback.format_exc()
    try:save('failed')
    except Exception:write(STATE,state)
    print(state['error'],flush=True);sys.exit(1)
