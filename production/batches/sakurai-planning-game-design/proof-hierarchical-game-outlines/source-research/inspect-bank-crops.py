"""Exact native-frame first/middle/last research for each candidate crop.
No final timing, subtitle approval, render, synthesis or GPU use.
"""
import hashlib, json, math, os, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]
bank_path = BASE / 'action-bank.json'
bank = json.loads(bank_path.read_text(encoding='utf-8'))
source = ROOT / bank['source']['localMediaPath']
target = BASE / 'frames/native-bank-v1'
state_path = BASE / 'native-bank-inspection.json'
stamp = lambda: datetime.now(timezone.utc).isoformat()
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(16*1024*1024), b''): h.update(chunk)
    return h.hexdigest()

state = {'pid':os.getpid(),'startedAt':stamp(),'status':'input-hash-check','bankSha256':digest(bank_path),'gpuJobs':0,'finalApproval':False}
def save():
    state['updatedAt'] = stamp()
    state_path.write_text(json.dumps(state, indent=2)+'\n',encoding='utf-8')

print('native crop inspection PID', os.getpid(), flush=True)
save()
if source.stat().st_size != bank['source']['fileBytes'] or digest(source) != bank['source']['fileSha256']:
    raise RuntimeError('Source has changed; repeat source review')
target.mkdir(parents=True,exist_ok=True)
if (target/'index.json').exists() or list(target.glob('frame-*.jpg')):
    raise RuntimeError('Preserve existing extraction and inspect its actual checkpoint')
points=[]
rows=[]
for cut in bank['cuts']:
    begin=round(cut['sourceInSeconds']*60)
    finish=round(cut['sourceOutSeconds']*60)-1
    for role,n in [('first',begin),('middle',round((begin+finish)/2)),('last',finish)]:
        points.append(n)
        rows.append({'cutId':cut['id'],'role':role,'nativeFrame':n,'sourceSeconds':n/60,'crop':cut['crop'],'visibleAction':cut['visibleAction']})
order=sorted(range(len(points)),key=points.__getitem__)
expr='+'.join('eq(n\\,%d)'%points[i] for i in order)
command=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-threads','2','-i',str(source),'-to',str(max(points)/60+1/60),'-map','0:v:0','-an','-vf',"select='"+expr+"',showinfo",'-fps_mode','vfr','-q:v','3',str(target/'frame-%04d.jpg')]
with (target/'extraction.log').open('w',encoding='utf-8') as log:
    child=subprocess.Popen(command,stdout=log,stderr=log)
    state.update(status='linear-native-extraction-running',childPid=child.pid,command=command,expectedFrames=len(points))
    save()
    code=child.wait()
state.update(childExitCode=code,childEndedAt=stamp())
save()
if code: raise RuntimeError('Native extraction failed; preserve log and frames')
lines=(target/'extraction.log').read_text(encoding='utf-8',errors='replace')
times=[float(x) for x in re.findall(r'pts_time:([\d.]+)',lines)]
files=sorted(target.glob('frame-*.jpg'))
if len(files)!=len(order) or len(times)!=len(order): raise RuntimeError('Native frame count mismatch')
for index,position in enumerate(order):
    row=rows[position]
    if abs(times[index]-row['sourceSeconds'])>0.001: raise RuntimeError('Unexpected native timestamp')
    row['ptsSeconds']=times[index]
    row['file']=str(files[index].relative_to(ROOT)).replace('\\','/')
    x,y,w,h=row['crop']
    original=Image.open(files[index]).convert('RGB')
    if original.size != (1920,1080) or x+w>1920 or y+h>1080: raise RuntimeError('Crop outside original frame')
    cropped=original.crop((x,y,x+w,y+h)).resize((1920,1080),Image.Resampling.LANCZOS)
    output=target/(row['cutId']+'-'+row['role']+'.jpg')
    cropped.save(output,quality=94)
    row['croppedFile']=str(output.relative_to(ROOT)).replace('\\','/')
try: font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
except OSError: font=ImageFont.load_default()
sheets=[]
for start in range(0,len(rows),18):
    batch=rows[start:start+18]
    sheet=Image.new('RGB',(1920,math.ceil(len(batch)/6)*207),(243,244,242))
    draw=ImageDraw.Draw(sheet)
    for local,row in enumerate(batch):
        x=(local%6)*320;y=(local//6)*207
        image=Image.open(ROOT/row['croppedFile']);image.thumbnail((320,180))
        sheet.paste(image,(x,y))
        draw.text((x+3,y+181),row['cutId']+' '+row['role']+' '+('%.3f'%row['ptsSeconds']),fill=(0,0,0),font=font)
    output=target/('sheet-%02d.jpg'%(len(sheets)+1));sheet.save(output,quality=95)
    sheets.append(str(output.relative_to(ROOT)).replace('\\','/'))
record={'bankSha256':state['bankSha256'],'sourceSha256':bank['source']['fileSha256'],'method':'linear native-frame selection; first/middle/last of each candidate, face-free crop proposed; source audio excluded','frameCount':len(rows),'cutCount':len(bank['cuts']),'command':command,'exitCode':code,'rows':rows,'sheets':sheets,'directReview':'pending','captionCueApproval':False,'finalApproval':False}
(target/'index.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
state.update(status='finished-awaiting-direct-crop-review',frameCount=len(rows),endedAt=stamp(),index=str((target/'index.json').relative_to(ROOT)).replace('\\','/'))
save()
print(json.dumps({'status':state['status'],'frameCount':len(rows),'sheets':sheets}),flush=True)
