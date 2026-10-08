"""Technical native reframing samples only; no final render/caption approval."""
import json,hashlib,os,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
R=Path('D:/Github/Video-Editing');P=R/'projects/player-customization/production'
src=R/'shared/output/player-customization/research/focused-ui-v1/native';out=R/'shared/output/player-customization/research/crop-samples-v1'
if out.exists():raise SystemExit('Preserve existing crop evidence; inspect before resuming.')
out.mkdir();(out/'frames').mkdir();(out/'boards').mkdir()
groups={'stats':([0,24,32,36,40,56,60],(240,46,992,558)),'modal':([16,20,186],(634,200,1152,648)),'ability':([116,124,128,132],(634,150,1152,648)),'look-upper':([144,174,192],(634,46,1152,648)),'look-lower':([170,174,182,184,192],(634,328,1152,648)),'starter':([558,560,562,566,570,574,576,580],(140,50,1632,918)),'nav-left':([636,642,644,648,650,658,666,670],(132,48,992,558)),'nav-right':([638,646,664,672],(634,200,1152,648))}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
state={'schemaVersion':1,'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'commandLine':[sys.executable,*sys.argv],'status':'running','cpuThreads':2,'gpu':0,'singleJob':True,'resourcesEvidence':'shared/output/player-customization/research/resources-before-crop-v1.json','sourceAudioUsed':False,'allRasterLocalOnly':True,'samples':[],'captionPixelsApproved':False,'continuousMotionApproved':False,'actualGameQuotaApproved':False}
for name,(times,box) in groups.items():
 x,y,w,h=box;assert w*9==h*16
 for t in times:
  inp=src/f'native-{t:04d}.png';p=out/'frames'/f'{name}-{t:04d}.png'
  im=Image.open(inp);im.crop((x,y,x+w,y+h)).resize((1920,1080),Image.Resampling.LANCZOS).save(p)
  state['samples'].append({'name':name,'requestedLocalSecond':t,'requestedSourceSecond':3900+t,'sourceSample':inp.relative_to(R).as_posix(),'sourceSampleSha256':sha(inp),'cropXYWH':box,'path':p.relative_to(R).as_posix(),'sha256':sha(p),'directlyRead':False})
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);state['boards']=[]
for offset in range(0,len(state['samples']),4):
 group=state['samples'][offset:offset+4];can=Image.new('RGB',(1920,1170),'white');d=ImageDraw.Draw(can)
 for k,row in enumerate(group):
  x=k%2*960;y=k//2*585;im=Image.open(R/row['path']);can.paste(im.resize((960,540)),(x,y+45));d.text((x+10,y+8),f"{row['name']} | local {row['requestedLocalSecond']}s",font=font,fill='black')
 p=out/'boards'/f'board-{offset//4+1:02d}.png';can.save(p);state['boards'].append({'path':p.relative_to(R).as_posix(),'sha256':sha(p),'samples':[f"{r['name']}:{r['requestedLocalSecond']}" for r in group],'directlyRead':False})
state.update({'status':'sample-extraction-complete-direct-review-pending','finishedAt':datetime.now(timezone.utc).isoformat(),'exitCode':0,'sampleCount':len(state['samples'])})
(P/'crop-samples-execution-v1.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pid':state['pid'],'status':state['status'],'sampleCount':state['sampleCount'],'boards':len(state['boards']),'cpu':2,'gpu':0}),flush=True)
