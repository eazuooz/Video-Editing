"""Single CPU2/GPU0 offline source inspection; never adopts footage or writes narration."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, subprocess, sys, traceback
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
MEDIA = ROOT / 'shared/assets/limited-color-world/raw'
QA = ROOT / 'shared/output/limited-color-world/preflight/chicory-official-v1'
STATE = PROOF / 'chicory-official-source-execution-v1.json'
QUEUE = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()
def rel(p): return str(p.relative_to(ROOT)).replace('\\', '/')
def write(p, d):
    t = p.with_name(p.name + f'.{os.getpid()}.tmp')
    t.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    os.replace(t, p)

if STATE.exists(): raise SystemExit('Existing execution: inspect its actual state, do not repeat.')
subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'limited-color-world', '--check'], cwd=ROOT, check=True)
MEDIA.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
state = {'schemaVersion':1, 'slug':'limited-color-world', 'status':'initializing', 'startedAt':stamp(),
 'pid':os.getpid(), 'processCreateTime':psutil.Process().create_time(), 'commandLine':sys.argv,
 'workingDirectory':str(ROOT), 'sessionId':None, 'cpuThreads':2, 'gpuJobs':0, 'children':[], 'sources':[],
 'wholeDecodeApproved':False, 'directPixelReviewApproved':False, 'sourceAdoptionApproved':False,
 'newScriptOrTts':False, 'externalResearchChanges':0, 'publicRightsApproved':False}
def save(status):
    state.update(status=status, updatedAt=stamp())
    sp = STATE.with_name(STATE.name+'.session.json')
    if sp.exists():
        session = json.loads(sp.read_text(encoding='utf-8-sig'))
        if session.get('pid') == os.getpid(): state['sessionId'] = session.get('sessionId')
    write(STATE, state)
    before = QUEUE.read_bytes(); q = json.loads(before)
    item = next(x for x in q['items'] if x['slug']=='limited-color-world')
    if item.get('videoId') or any(item['checkpoints'].values()): raise RuntimeError('Limited item advanced; preserve it.')
    item.update(status='in-progress', stage='official-source-'+status, updatedAt=state['updatedAt'])
    item['execution'] = {k:state[k] for k in ('status','pid','processCreateTime','commandLine','workingDirectory','sessionId','cpuThreads','gpuJobs')}
    item['execution'].update(phase='chicory-official-native-pts-coarse-inspection', state=rel(STATE), child=state['children'][-1] if state['children'] else None)
    item['nextAction']='Read every generated coarse board; select and inspect exact native action intervals and caption/UI space before adoption or dependent narration.'
    q['updatedAt']=q['lastProgressAt']=state['updatedAt']
    if QUEUE.read_bytes()!=before: raise RuntimeError('Concurrent queue changed; do not overwrite.')
    write(QUEUE,q)
def run(args,label,output=None):
    logpath=QA/(label+'.log')
    with logpath.open('wb') as log:
        c=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE if output else log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        rec={'label':label,'pid':c.pid,'processCreateTime':psutil.Process(c.pid).create_time(),'commandLine':args,'startedAt':stamp(),'status':'running','log':rel(logpath)}
        state['children'].append(rec); save('single-cpu-job-running')
        data=c.communicate()[0]
        rec.update(status='exited',exitCode=c.returncode,endedAt=stamp())
        if c.returncode: raise RuntimeError(f'{label}: exit {c.returncode}')
        if output: output.write_bytes(data); return json.loads(data)

try:
    # Save fresh resource evidence without manipulating any process or queue outside this item.
    cmd="Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"
    resource=subprocess.run(['powershell','-NoProfile','-Command',cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    write(PROOF/'chicory-resource-before-review-v1.json',{'recordedAt':stamp(),'processCim':resource.stdout.decode('utf-8-sig',errors='replace'),'gpu':gpu.stdout.decode().strip(),'researchManipulated':False,'ownGpuJobs':0})
    acquisitions=[]
    for number, token in [(1,'AOCgsW798urHRb55KPc8Rig'),(2,'AL7Urbfno1oJc4vykZUHXfw')]:
        download=Path(f'C:/Users/eazuo/Downloads/B-Roll {number}.mp4')
        if not download.is_file(): raise RuntimeError('Completed browser download missing')
        target=MEDIA/f'chicory-b-roll-{number}.mp4'; h=sha(download)
        if target.exists():
            if sha(target)!=h: raise RuntimeError('Divergent preserved source; no overwrite')
        else: shutil.copy2(download,target)
        if sha(target)!=h: raise RuntimeError('Copy hash mismatch')
        acquisitions.append({'key':f'chicory-b-roll-{number}','title':f'B-Roll {number}.mp4','kind':'official-developer-press-b-roll','developer':'Wishes Ultd / Greg Lobanov','publisher':'Finji',
         'discoveryUrl':'https://impress.games/press-kit/wishes/chicory-a-colorful-tale',
         'officialFolderUrl':'https://www.dropbox.com/sh/kzu705qlt8g4rjz/AABZD35PdofcrbLTZbiE-83wa?dl=0',
         'fileUrl':f'https://www.dropbox.com/scl/fo/96x40dg743j9lc43vmzar/{token}/Video/B-Roll%20{number}.mp4?rlkey=bweconxebq1n9oz24ljhpgc7l&dl=0',
         'browserDownloadPath':str(download),'downloadFileModifiedAt':datetime.fromtimestamp(download.stat().st_mtime,timezone.utc).isoformat(),'localPath':rel(target),'bytes':target.stat().st_size,'sha256':h,
         'rights':'Official developer press B-roll linked from official press kit; explicit broad monetized reuse license not observed. Final public-rights review remains pending.',
         'sourceAudioForFinal':'exclude-all','sourceAdopted':False,'publicRightsApproved':False})
    write(PROOF/'chicory-official-acquisition-v1.json',{'schemaVersion':1,'recordedAt':stamp(),'downloadMethod':'CUA visible download controls and download completion event; no account created','downloadedOnceEach':True,'sources':acquisitions,'allSourceMediaLocalOnly':True,'adopted':False})
    save('cpu-review-initializing')
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
    for source in acquisitions:
        p=ROOT/source['localPath']; key=source['key']; sub=QA/key; sub.mkdir(exist_ok=True)
        meta=run([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)],key+'-probe',sub/'probe.json')
        video=next(v for v in meta['streams'] if v['codec_type']=='video')
        frame_data=run([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp,best_effort_timestamp_time,pkt_duration','-of','json',str(p)],key+'-frame-pts',sub/'native-pts.json')
        frames=frame_data['frames']; pts=[int(f['best_effort_timestamp']) for f in frames]
        if len(set(pts))!=len(pts) or any(b<=a for a,b in zip(pts,pts[1:])): raise RuntimeError('Nonmonotonic native PTS requires investigation')
        run([FF,'-nostdin','-v','error','-threads','2','-filter_threads','2','-i',str(p),'-map','0:v:0','-map','0:a?','-f','null','-'],key+'-whole-decode')
        chosen=[]; next_time=0.0
        for idx,f in enumerate(frames):
            t=float(f['best_effort_timestamp_time'])
            if t+1e-8>=next_time:
                chosen.append({'nativeFrame':idx,'pts':pts[idx],'timeSeconds':t}); next_time+=1.0
        if chosen[-1]['nativeFrame']!=len(frames)-1: chosen.append({'nativeFrame':len(frames)-1,'pts':pts[-1],'timeSeconds':float(frames[-1]['best_effort_timestamp_time'])})
        expr='+'.join(f"eq(pts,{f['pts']})" for f in chosen)
        run([FF,'-nostdin','-v','error','-threads','2','-filter_threads','2','-i',str(p),'-vf',"select='"+expr+"'",'-fps_mode','passthrough','-an','-threads','2',str(sub/'sample-%04d.png')],key+'-coarse-extract')
        files=sorted(sub.glob('sample-*.png'))
        if len(files)!=len(chosen): raise RuntimeError('Exact selected PTS extraction count mismatch; no guessing')
        for sample,ip in zip(chosen,files): sample.update(path=rel(ip),sha256=sha(ip))
        boards=[]
        for off in range(0,len(files),6):
            board=Image.new('RGB',(1920,816),(24,24,24)); d=ImageDraw.Draw(board)
            for n,(ip,sample) in enumerate(zip(files[off:off+6],chosen[off:off+6])):
                x=n%3*640;y=n//3*408
                with Image.open(ip) as image:
                    im=image.convert('RGB');im.thumbnail((640,360));board.paste(im,(x+(640-im.width)//2,y+36+(360-im.height)//2))
                d.text((x+6,y+3),key+' f'+str(sample['nativeFrame']),font=font,fill='white')
                d.text((x+6,y+384),f"PTS {sample['pts']} t {sample['timeSeconds']:.6f}",font=font,fill=(180,230,230))
            bp=sub/f'board-{off//6+1:03d}.jpg';board.save(bp,quality=92)
            boards.append({'path':rel(bp),'sha256':sha(bp),'sampleRange':[off,min(off+6,len(files))]})
        state['sources'].append({**source,'probe':rel(sub/'probe.json'),'nativePts':rel(sub/'native-pts.json'),
         'video':{k:video.get(k) for k in ('width','height','r_frame_rate','avg_frame_rate','time_base','duration','nb_frames')},'decodedFrames':len(frames),'wholeDecodeExitCode':0,'nativePtsMonotonic':True,'samples':chosen,'boards':boards,'directPixelReviewApproved':False})
        save('source-coarse-extracted')
    state.update(wholeDecodeApproved=True,totalSamples=sum(len(s['samples']) for s in state['sources']),totalBoards=sum(len(s['boards']) for s in state['sources']))
    save('coarse-extracted-awaiting-direct-review')
    print(json.dumps({'status':state['status'],'sources':len(state['sources']),'samples':state['totalSamples'],'boards':state['totalBoards']},ensure_ascii=False),flush=True)
except BaseException:
    state['error']=traceback.format_exc()
    try: save('failed')
    except Exception: write(STATE,state)
    print(state['error'],flush=True);sys.exit(1)
