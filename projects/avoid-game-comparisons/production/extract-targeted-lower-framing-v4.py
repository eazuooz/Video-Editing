"""Inspect new framing only for sampled focus/UI issues; rasters stay local.

Reuse existing compiled native intervals and untouched PCM. This is a candidate
composition trial, not final video rendering or every-frame approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time, traceback
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
WORK=BASE/'measured-edit-v4'; DEST=WORK/'targeted-lower-framing-local'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing')
    for n in range(20):
        try:
            temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p);return
        except PermissionError:
            if n==19:raise
            time.sleep(.1)
assert not DEST.exists();DEST.mkdir()
plan=read(WORK/'plan.json');compiled=read(WORK/'native-review-v1/compiled.json');layout=read(WORK/'caption-layout-v1.json')
issues=read(BASE/'all-actual-cue-trial-direct-review-v3.json')['issues']
flagged={r['cut'] for i in issues if i['kind'] in ['focus-occlusion','source-text-overlap','source-UI-overlap','focus-and-UI-occlusion'] for r in i['samples']}
flagged={s.replace('action-83-960-1276','action-83-960-1270') for s in flagged}
cuts=[c for s in plan['scenes'] for c in s['segments'] if c['id'] in flagged]
assert len(cuts)==len(flagged)
state={'startedAt':now(),'pid':os.getpid(),'sessionId':None,'status':'CPU-targeted-lower-framing-trials',
       'threads':2,'activeTasks':[],'images':[],'sheets':[],'completedCuts':0,'totalCuts':len(cuts),
       'planSha256':sha(WORK/'plan.json'),'captionLayoutSha256':sha(WORK/'caption-layout-v1.json'),
       'allFinalPixelsApproved':False,'newGitImages':0}
def save():
    state['updatedAt']=now();write(DEST/'execution.json',state)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
    i.update(stage='current15-targeted-lower-framing-candidate-pixel-review',updatedAt=state['updatedAt'])
    i['execution'].update(observedAt=state['updatedAt'],phase=i['stage'],status=state['status'],pid=state['pid'],sessionId=state['sessionId'],alive='endedAt' not in state,
      activeTasks=state['activeTasks'],gpuSynthesisJobs=0,cpuProductionJobs=0 if 'endedAt' in state else 1,renderJobs=0,uploads=0,
      targetedFraming={'state':rel(DEST/'execution.json'),'completedCuts':state['completedCuts'],'totalCuts':len(cuts),'images':len(state['images'])})
    i['nextAction']='Directly inspect targeted lower-framing samples; fix12p1 rocket and10p2 spoken-name boundaries and cup UI before approving final cues/timing. Preserve all15 PCM and all original explanations.'
    q['updatedAt']=state['updatedAt'];write(qp,q)
    cp=read(BASE/'latest-checkpoint.json');cp.update(stage=i['stage'],updatedAt=state['updatedAt'],execution=i['execution'],nextAction=i['nextAction']);write(BASE/'latest-checkpoint.json',cp)
try:
    save()
    for c in cuts:
        media=next(x for x in compiled['cuts'] if x['id']==c['id']);assert sha(ROOT/media['video'])==media['sha256']
        frames={0:{'anchors':['start'],'cues':[]},c['frames']//2:{'anchors':['middle'],'cues':[]},c['frames']-1:{'anchors':['last'],'cues':[]}}
        for r in layout['rows']:
            if r['segment']==c['id']:frames.setdefault(r['localFrame'],{'anchors':[],'cues':[]})['cues'].append(r['cue'])
        # Shift the native viewport down; narration remains at960,970.
        # All game geometry, targets, top HUD and UI must still be read directly.
        crop='crop=1600:900:160:180,'
        context=c.get('requiredContextLabel');label=''
        if context:label=f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='{context}':fontsize=26:fontcolor=black:box=1:boxcolor=white@0.94:boxborderw=12:x=38:y=36,"
        select='+'.join(f'eq(n\\,{f})' for f in sorted(frames))
        vf=f"{crop}scale=1920:1080,setsar=1,{label}setpts=PTS+{c['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.ass,select='{select}'"
        folder=DEST/c['id'];folder.mkdir();log=folder/'extraction.log'
        command=[FF,'-v','error','-nostdin','-threads','2','-i',str(ROOT/media['video']),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(frames)),str(folder/'sample-%03d.png')]
        with log.open('wb') as fh:
            p=subprocess.Popen(command,cwd=WORK,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW)
            state['activeTasks']=[{'kind':'CPU-targeted-framing','pid':p.pid,'command':command,'log':rel(log)}];save();code=p.wait()
        state['activeTasks']=[];assert code==0 and not log.read_text(encoding='utf-8').strip()
        files=sorted(folder.glob('sample-*.png'));assert len(files)==len(frames)
        for f,n in zip(files,sorted(frames)):
            state['images'].append({'path':rel(f),'sha256':sha(f),'cut':c['id'],'localFrame':n,'globalFrame':c['startFrame']+n,
               'anchorRoles':frames[n]['anchors'],'cueIds':frames[n]['cues'],'trialCrop':crop,'directlyRead':False,'finalApproved':False})
        state['completedCuts']+=1;save()
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
    for offset in range(0,len(state['images']),6):
        subset=state['images'][offset:offset+6];sheet=Image.new('RGB',(1920,1740),'white');d=ImageDraw.Draw(sheet)
        for k,r in enumerate(subset):
            x,y=(k%2)*960,(k//2)*580
            with Image.open(ROOT/r['path']) as im:sheet.paste(im.resize((960,540)),(x,y+40))
            d.text((x+8,y+7),f'{offset+k+1:03d} {r["cut"]} n{r["localFrame"]} cue{r["cueIds"]}',font=font,fill='black')
        out=DEST/f'review-sheet-{offset//6+1:03d}.jpg';sheet.save(out,quality=94)
        state['sheets'].append({'path':rel(out),'sha256':sha(out),'imageIndices':list(range(offset+1,offset+len(subset)+1)),'directlyRead':False})
    state.update(status='closed-targeted-lower-framing-trials-awaiting-direct-read',endedAt=now(),exitCode=0);save()
    print(json.dumps({'pid':os.getpid(),'cuts':len(cuts),'images':len(state['images']),'sheets':len(state['sheets']),'newGitImages':0}))
except Exception:
    state.update(status='closed-targeted-framing-failed',endedAt=now(),exitCode=1,error=traceback.format_exc(),activeTasks=[]);save();raise
