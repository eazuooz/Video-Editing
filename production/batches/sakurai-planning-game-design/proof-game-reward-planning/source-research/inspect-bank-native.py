"""Exact native source frames before narration. No synthesis, render or final approval."""
import argparse, hashlib, json, math, os, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
parser = argparse.ArgumentParser()
parser.add_argument('--version', default='v1', choices=['v1','v2','v3','v4','v5','v6','v7','v8','v9','v10','v11','v12','v13','v14'])
parser.add_argument('--internal-step', type=float, default=0)
parser.add_argument('--no-queue', action='store_true', help='Keep the active synthesis checkpoint; this CPU review has its own state.')
args = parser.parse_args()
bank_path = BASE / ('action-bank-' + args.version + '.json')
bank = json.loads(bank_path.read_text(encoding='utf-8'))
known_sources={s['videoId'] for s in bank['sources']}
missing_sources={c['sourceId'] for c in bank['cuts']}-known_sources
if missing_sources: raise RuntimeError('Candidate source metadata missing: '+','.join(sorted(missing_sources)))
target = BASE / ('frames/native-bank-' + args.version)
state_path = BASE / ('native-bank-inspection-' + args.version + '.json')
queue_path = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
launch_path = BASE / ('native-bank-launch-' + args.version + '.json')
stamp = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: str(p.relative_to(ROOT)).replace('\\','/')
def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(16*1024*1024),b''): h.update(chunk)
    return h.hexdigest()
if target.exists() or state_path.exists():
    raise RuntimeError('Preserve existing native bank extraction; inspect actual results rather than rerun.')
target.mkdir(parents=True)
state = {'pid':os.getpid(),'startedAt':stamp(),'status':'initializing','bankSha256':digest(bank_path),'children':[],'gpuJobs':0,'narrationWritten':(ROOT/'projects/game-reward-planning/script/narration.ko.json').exists(),'finalApproval':False}
def save(status):
    state.update(status=status,updatedAt=stamp())
    state_path.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    if args.no_queue: return
    q=json.loads(queue_path.read_text(encoding='utf-8'))
    item=next(x for x in q['items'] if x['slug']=='game-reward-planning')
    old=item.get('execution',{})
    launch=json.loads(launch_path.read_text(encoding='utf-8')) if launch_path.exists() else {}
    execution={**old,'phase':'source-native-bank-boundary-review','status':status,'pid':os.getpid(),'runner':rel(Path(__file__)),'state':rel(state_path),'children':state['children'],'activeTasks':[c for c in state['children'] if c['status']=='running'],'gpuJobs':0,'noTts':True,'noNewScript':True,'noNewProject':True,'overviewRequired':True,'updatedAt':state['updatedAt']}
    execution.pop('sessionId', None)
    if launch.get('sessionId') is not None: execution['sessionId']=launch['sessionId']
    item.update(stage=execution['phase'],execution=execution,updatedAt=state['updatedAt'],nextAction='Directly review native first/middle/last and outside boundary frames for all candidate actions, trim title/presenter/idle conflicts, check source-shot reuse and fixed bottom captions, then write independent bilingual planning including the new whole-video overview. Candidate duration is not final60:40 approval.')
    q['updatedAt']=state['updatedAt']
    queue_path.write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('native bank PID',os.getpid(),flush=True)
save('input-hash-check')
rows=[]
for source in bank['sources']:
    cuts=[c for c in bank['cuts'] if c['sourceId']==source['videoId']]
    if not cuts: continue
    file=ROOT/source['localMediaPath']
    if file.stat().st_size!=source['fileBytes'] or digest(file)!=source['fileSha256']:
        raise RuntimeError('Source bytes changed: '+source['videoId'])
    fps=source['fps']; source_rows=[]
    for cut in cuts:
        a=round(cut['sourceInSeconds']*fps);z=round(cut['sourceOutSeconds']*fps)-1
        for role,n in [('before',max(0,a-1)),('first',a),('middle',round((a+z)/2)),('last',z),('after',z+1)]:
            source_rows.append({'cutId':cut['id'],'sourceId':source['videoId'],'role':role,'nativeFrame':n,'sourceSeconds':n/fps,'visibleAction':cut['visibleAction']})
        if args.internal_step > 0:
            step=max(1,round(args.internal_step*fps))
            for n in range(a+step,z,step):
                source_rows.append({'cutId':cut['id'],'sourceId':source['videoId'],'role':'inside','nativeFrame':n,'sourceSeconds':n/fps,'visibleAction':cut['visibleAction']})
    points=sorted(set(r['nativeFrame'] for r in source_rows))
    out_dir=target/source['videoId'];out_dir.mkdir()
    expr='+'.join('eq(n\\,%d)'%n for n in points)
    command=[str(FF),'-hide_banner','-threads','2','-i',str(file),'-to',str((max(points)+1)/fps),'-map','0:v:0','-an','-vf',"select='"+expr+"',showinfo",'-fps_mode','vfr','-q:v','3',str(out_dir/'frame-%04d.jpg')]
    log=out_dir/'extraction.log'
    with log.open('w',encoding='utf-8') as f:
        child=subprocess.Popen(command,stdout=f,stderr=f)
        rec={'kind':'native-bank-frames','sourceId':source['videoId'],'pid':child.pid,'status':'running','startedAt':stamp(),'log':rel(log),'command':command}
        state['children'].append(rec);save('native-bank-extraction-running')
        code=child.wait()
    rec.update(status='finished' if code==0 else 'failed',exitCode=code,endedAt=stamp())
    save('source-native-bank-finished')
    if code: raise RuntimeError('Native extraction failed: '+source['videoId'])
    times=[float(x) for x in re.findall(r'pts_time:([\d.]+)',log.read_text(encoding='utf-8',errors='replace'))]
    files=sorted(out_dir.glob('frame-*.jpg'))
    if len(files)!=len(points) or len(times)!=len(points): raise RuntimeError('Native extraction count mismatch')
    lookup={n:(f,t) for n,f,t in zip(points,files,times)}
    for row in source_rows:
        f,t=lookup[row['nativeFrame']]
        if abs(t-row['sourceSeconds'])>0.001: raise RuntimeError('Native PTS mismatch')
        row.update(ptsSeconds=t,file=rel(f))
    rows.extend(source_rows)
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
sheets=[]
for offset in range(0,len(rows),20):
    chunk=rows[offset:offset+20]
    sheet=Image.new('RGB',(1920,math.ceil(len(chunk)/5)*244),(242,243,242));draw=ImageDraw.Draw(sheet)
    for local,row in enumerate(chunk):
        x=(local%5)*384;y=(local//5)*244
        img=Image.open(ROOT/row['file']).convert('RGB');img.thumbnail((384,216));sheet.paste(img,(x,y))
        draw.text((x+4,y+220),row['cutId']+' '+row['role']+' '+('%.3f'%row['ptsSeconds']),fill=(0,0,0),font=font)
    output=target/('sheet-%02d.jpg'%(len(sheets)+1));sheet.save(output,quality=95);sheets.append(rel(output))
record={'schemaVersion':1,'bankSha256':state['bankSha256'],'method':'Sequential linear native-frame selection; first/middle/last plus adjacent frames outside every candidate interval and optional internal samples; full1080 source frames; no source audio.','internalStepSeconds':args.internal_step,'frameCount':len(rows),'uniqueFrameCount':len({r['file'] for r in rows}),'cutCount':len(bank['cuts']),'rows':rows,'sheets':sheets,'directReview':'pending','fixedCaptionSafety':'pending','finalApproval':False}
index=target/'index.json';index.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
state.update(index=rel(index),frameCount=len(rows),uniqueFrameCount=record['uniqueFrameCount'],cutCount=record['cutCount'],endedAt=stamp())
save('finished-awaiting-direct-native-bank-review')
print(json.dumps({'status':state['status'],'frameCount':len(rows),'uniqueFrameCount':record['uniqueFrameCount'],'sheets':sheets}),flush=True)
