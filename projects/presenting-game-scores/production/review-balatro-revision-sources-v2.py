"""One CPU source-preflight job. Preserve raw files; never approve footage here."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, sys
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent / 'revision-balatro60-v2'
RAW = ROOT / 'shared/assets/presenting-game-scores/revision-balatro60-v2'
OUT = ROOT / 'shared/output/presenting-game-scores/revision-balatro60-v2/source-review'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')
YTPY = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
NODE = Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
STATE = BASE / 'source-execution.json'
stamp = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for b in iter(lambda:stream.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def save(p,j):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)
def run(cmd,log):
    with log.open('w',encoding='utf-8') as stream:
        p=subprocess.run([str(x) for x in cmd],cwd=ROOT,stdout=stream,stderr=stream)
    if p.returncode: raise RuntimeError(f'Exit {p.returncode}: {log}')
    return p.returncode
if STATE.exists(): raise RuntimeError('Inspect actual source state first. No duplicate download/review job.')
if not (BASE/'request.json').exists(): raise RuntimeError('User revision request required.')
BASE.mkdir(exist_ok=True);RAW.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
os.environ['PATH']=str(NODE.parent)+os.pathsep+os.environ['PATH']
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
inventory=[]
for p in psutil.process_iter(['pid','name','create_time','cmdline']):
    try:
        d=p.info;cmd=' '.join(d['cmdline'] or [])
        if any(n in (d['name'] or '').lower() for n in ['python','ffmpeg','node']): inventory.append(d)
        own='presenting-game-scores' in cmd
        static='serve-native-review-v1.py' in cmd or 'vite.presenting-game-scores.black-preflight-v1.config.ts' in cmd
        if own and not static and d['pid']!=os.getpid() and 'review-balatro-revision-sources-v2.py' not in cmd:
            raise RuntimeError('Another own job requires inspection: '+cmd)
    except psutil.AccessDenied: pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
resource={'observedAt':stamp(),'processInventory':inventory,'gpuCsv':gpu.stdout.strip(),'cpuLoadPercent':psutil.cpu_percent(interval=1),'freePhysicalMemoryBytes':psutil.virtual_memory().available,'researchProcessChanges':0,'gpuJobs':0,'cpuThreads':2}
save(BASE/'resources-before-source-review.json',resource)
me=psutil.Process()
sources=[('launch','2n9pkiuSZLU'),('friends-pack3','1r1LVgAGXlE'),('friends-pack4','0G24sFdbXws')]
state={'schemaVersion':1,'slug':'presenting-game-scores','revision':'balatro60-tetris40-v2','startedAt':stamp(),'actualPid':me.pid,'createTime':me.create_time(),'command':me.cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpu':0,'stage':'source-acquisition','active':None,'results':[],'exitCode':None,'directReviewApproved':False,'footageAdopted':False,'rightsPublicApproved':False,'newGitImages':0,'resource':str(BASE/'resources-before-source-review.json')}
save(STATE,state)
try:
    for key,video_id in sources:
        state['active']=key;state['updatedAt']=stamp();save(STATE,state)
        url='https://www.youtube.com/watch?v='+video_id
        raw=RAW/(key+'.mp4'); out=OUT/key
        if raw.exists() or out.exists(): raise RuntimeError('Existing candidate preserved; inspect before resuming: '+key)
        out.mkdir()
        run([YTPY,'-X','utf8','-m','yt_dlp','--no-playlist','--no-progress','--no-overwrites','--js-runtimes','node','--write-info-json','-f','bv[height<=1080][ext=mp4]/b[height<=1080][ext=mp4]','-o',raw,url],out/'download.log')
        meta=json.loads(raw.with_suffix('.info.json').read_text('utf-8'))
        if meta.get('uploader')!='Playstack' and meta.get('channel')!='Playstack':raise RuntimeError('Publisher provenance mismatch')
        probe=subprocess.run([str(FP),'-v','error','-show_streams','-show_format','-of','json',str(raw)],capture_output=True,text=True,check=True)
        p=json.loads(probe.stdout);save(out/'probe.json',p)
        duration=float(p['format']['duration'])
        run([FF,'-nostdin','-v','error','-threads','2','-i',raw,'-map','0:v:0','-an','-f','null','-'],out/'whole-decode.log')
        frames=out/'frames';frames.mkdir()
        run([FF,'-nostdin','-v','error','-threads','2','-i',raw,'-an','-vf','fps=2,scale=948:533:force_original_aspect_ratio=decrease','-threads','2','-q:v','2',frames/'frame-%04d.jpg'],out/'sampling.log')
        images=sorted(frames.glob('*.jpg'));boards=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
        for first in range(0,len(images),6):
            board=Image.new('RGB',(1920,1683),'#171717');draw=ImageDraw.Draw(board);entries=[]
            for n,pth in enumerate(images[first:first+6]):
                im=Image.open(pth).convert('RGB');x=6+(n%2)*960;y=28+(n//2)*561;board.paste(im,(x,y))
                nominal=(first+n)*.5+.25;draw.text((x,y-27),f'{key} #{first+n+1:03d} nominal {nominal:.2f}s',font=font,fill='white')
                entries.append({'index':first+n+1,'nominalSeconds':nominal,'path':str(pth),'sha256':sha(pth)})
            bp=out/f'board-{first//6+1:03d}.jpg';board.save(bp,quality=94);boards.append({'path':str(bp),'sha256':sha(bp),'entries':entries})
        result={'key':key,'url':url,'recordingOwner':'Playstack','title':meta['title'],'channelId':meta.get('channel_id'),'sourcePath':str(raw),'sha256':sha(raw),'bytes':raw.stat().st_size,'durationSeconds':duration,'wholeDecodeExit':0,'sampleExtractionExit':0,'samples':len(images),'boards':boards,'samplesAreNominalNotNativePts':True,'allPixelsDirectlyReviewed':False,'adoptedSeconds':0,'sourceAudioSelected':False,'loop':False,'slowdown':False,'finalPublicRightsApproved':False}
        state['results'].append(result);save(STATE,state);print(json.dumps({k:result[k] for k in ['key','title','durationSeconds','samples','sha256']},ensure_ascii=False),flush=True)
    state.update(stage='source-technical-preflight-complete-direct-review-pending',active=None,finishedAt=stamp(),exitCode=0);save(STATE,state)
except BaseException as e:
    state.update(stage='source-preflight-failed-preserve-completed-results',error=repr(e),finishedAt=stamp(),exitCode=1);save(STATE,state);raise
