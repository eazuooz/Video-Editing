"""Extract new candidate boundaries once on CPU; retain approval gates."""
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib,subprocess,time
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
bank=read(PROOF/'additional-action-bank-candidates-v2.json')
resource=read(PROOF/'resource-observation-v13.json')
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
bank['clips']=[c for c in bank['clips'] if c['requiresNewBoundaryExtraction']]
assert len(bank['clips'])==13
out=ROOT/'shared/output/familiar-game-rules/research/additional-cut-edges-v2'
assert not out.exists(),'Preserve extracted files; no repeat'
out.mkdir();(out/'boards').mkdir()
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),startedAt=now(),status='starting',cpuThreads=2,gpuJobs=0,children=[],boards=[],resourceObservation=rel(PROOF/'resource-observation-v13.json'),candidateBank=rel(PROOF/'additional-action-bank-candidates-v2.json'),allDirectlyRead=False,exactCutApproval=False,crossSourceDuplicateSelectionApproved=False,finalPixelApproval=False,imagesGitPolicy='local-only')
def save(status):
    state.update(status=status,updatedAt=now());write(PROOF/'additional-cut-edges-execution-v2.json',state)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
    ex=dict(pid=state['pid'],commandLine=[os.sys.executable,*os.sys.argv],alive=status=='additional-cut-edges-running',state=rel(PROOF/'additional-cut-edges-execution-v2.json'),log=rel(BASE/'additional-cut-edges-v2.log'),status=status,activeTasks=[c for c in state['children'] if c['status']=='running'],cpuThreads=2,gpuJobs=0,foreignWorkPreserved=True)
    item.update(stage=status,updatedAt=state['updatedAt'],additionalCutEdgeExecution=ex,nextAction='Directly read13 refined boundary boards and compare retained actions with old source bank. Preserve current11PCM; exact cuts, final ratio, narration, render and upload remain unapproved.')
    q.update(updatedAt=state['updatedAt'],lastProgressAt=state['updatedAt']);write(qp,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','additionalCutEdgeExecution','nextAction']:d[k]=item[k]
        write(p,d)
def boundaries(c):return [c['inFrameInclusive']-1,c['inFrameInclusive'],c['inFrameInclusive']+1,c['outFrameExclusive']-2,c['outFrameExclusive']-1,c['outFrameExclusive']]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
try:
    save('additional-cut-edges-running');paths={}
    for sid in dict.fromkeys(c['sourceVideoId'] for c in bank['clips']):
        clips=[c for c in bank['clips'] if c['sourceVideoId']==sid];source=ROOT/clips[0]['sourcePath'];assert sha(source)==clips[0]['sourceSha256']
        frames=sorted(set(n for c in clips for n in boundaries(c)));directory=out/sid;directory.mkdir()
        expr='+'.join(f'eq(n,{n})' for n in frames)
        cmd=[ff,'-hide_banner','-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf',f"select='{expr}',scale=960:540",'-vsync','0','-q:v','3','-threads','2',str(directory/'%04d.jpg')]
        log=PROOF/'logs'/f'{sid}-additional-cut-edges-v2.log'
        with log.open('xb') as handle:
            p=subprocess.Popen(cmd,cwd=ROOT,stdout=handle,stderr=handle,creationflags=subprocess.CREATE_NO_WINDOW)
            child=dict(sourceVideoId=sid,pid=p.pid,commandLine=cmd,log=rel(log),startedAt=now(),status='running');state['children'].append(child);save('additional-cut-edges-running')
            code=p.wait();child.update(exitCode=code,endedAt=now(),status='finished' if code==0 else 'failed');assert code==0
        files=sorted(directory.glob('*.jpg'));assert len(files)==len(frames);paths[sid]=dict(zip(frames,files))
    for c in bank['clips']:
        board=Image.new('RGB',(1920,1710),'white');draw=ImageDraw.Draw(board);tiles=[];num,den=map(int,c['sourceFrameRate'].split('/'))
        for i,(tag,n) in enumerate(zip(['before-start','first','after-start','before-last','last','outside-end'],boundaries(c))):
            p=paths[c['sourceVideoId']][n];x=i%2*960;y=i//2*570
            with Image.open(p) as im:board.paste(im,(x,y+30))
            draw.text((x+8,y+3),f'{c["id"]} {tag} n={n} t={n*den/num:.6f}',font=font,fill='black')
            tiles.append(dict(tag=tag,sourceFrame=n,seconds=n*den/num,path=rel(p),sha256=sha(p)))
        target=out/'boards'/f'{c["id"]}.jpg';board.save(target,quality=95)
        state['boards'].append(dict(actionId=c['id'],board=rel(target),sha256=sha(target),tiles=tiles,directlyRead=False))
    state.update(boardCount=len(state['boards']),frameSlots=sum(len(b['tiles']) for b in state['boards']),finishedAt=now());save('additional-cut-edges-extracted-awaiting-direct-review')
    print(json.dumps(dict(pid=state['pid'],boards=state['boardCount'],frameSlots=state['frameSlots'],allApproval=False)))
except Exception as e:
    state['error']=repr(e);save('additional-cut-edges-failed');raise
