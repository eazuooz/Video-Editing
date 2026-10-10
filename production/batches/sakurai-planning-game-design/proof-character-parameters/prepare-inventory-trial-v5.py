"""Correct only Dungeons trial inventory/header overlap from v4, preserving v4."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[4]; PROOF=Path(__file__).resolve().parent
QA=ROOT/'shared/output/character-parameters/preflight/fullscreen-ui-v5'
STATE=PROOF/'fullscreen-ui-trial-v5.json'
assert not QA.exists() and not STATE.exists()
v4=json.loads((PROOF/'fullscreen-ui-trial-v4.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
small=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
QA.mkdir(parents=True);samples=[]
for t in v4['samples']:
 if t['sourceKey']!='a8nwpiCqyTQ':continue
 p=ROOT/t['path'];assert sha(p)==t['sha256']
 im=Image.open(p).convert('RGB');out=im.copy()
 inventory=im.crop((406,921,1520,1065)).resize((424,55),Image.Resampling.NEAREST)
 bg=im.crop((406,870,1520,920)).filter(ImageFilter.GaussianBlur(12)).resize((1114,144),Image.Resampling.BILINEAR)
 out.paste(bg,(406,921));out.paste(inventory,(1490,135))
 d=ImageDraw.Draw(out);txt='캐릭터마다 규칙이 다릅니다.';b=d.textbbox((0,0),txt,font=font)
 bw=b[2]-b[0]+44;x=(1920-bw)//2;y=928
 d.rectangle((x+14,y+14,x+bw+14,y+98),fill='#073c32')
 d.rectangle((x,y,x+bw,y+84),fill='white',outline='#161b18',width=3)
 d.text((x+22,y+11-b[1]),txt,font=font,fill='#080b09')
 q=QA/f"dungeons-f{t['nativeFrame']}.png";out.save(q)
 samples.append({**t,'previousTrialPath':t['trialPath'],'trialPath':str(q.relative_to(ROOT)).replace('\\','/'),'trialSha256':sha(q)})
boards=[]
for off in range(0,len(samples),6):
 b=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(b)
 for n,t in enumerate(samples[off:off+6]):
  x=n%3*640;y=n//3*408
  b.paste(Image.open(ROOT/t['trialPath']).resize((640,360),Image.Resampling.LANCZOS),(x,y+36))
  d.text((x+6,y+3),f"Dungeons f{t['nativeFrame']}",font=small,fill='white')
  d.text((x+6,y+384),f"PTS{t['pts']} t{t['timeSeconds']:.6f} trial-v5",font=small,fill=(180,230,230))
 p=QA/f'board-{off//6+1:03d}.jpg';b.save(p,quality=93)
 boards.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'sampleRange':[off,min(off+6,len(samples))]})
state={'schemaVersion':1,'slug':'character-parameters','createdAt':datetime.now(timezone.utc).isoformat(),
 'status':'prepared-awaiting-direct-review','priorDirectObservedFailures':[
 'v4 inventory covers enemy REACT header at2034 and STRONG at2265.',
 'v4 inventory overlaps the Foreman Kohler upper body at4533/4605.'],
 'framing':'All original1920x1080 game action/stats/skills/hearts preserved; same-frame inventory+coins moved to1490,135 at0.38scale outside stats and below enemy-name header. Old inventory alone replaced by same-frame blurred floor. Fixed caption requires single line and restrained width.',
 'rivalsTrialReusedUnchanged':'production/batches/sakurai-planning-game-design/proof-character-parameters/fullscreen-ui-trial-v4.json',
 'samples':samples,'boards':boards,'newNativeExtractionCount':0,'cpuThreads':1,'gpuJobs':0,
 'fullscreenCompositionApproved':False,'sourceAdoptionApproved':False,'allFinalCueUiApproved':False,
 'externalResearchChanges':0,'rasterGitAdditions':0}
STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':state['status'],'newTrialSamples':len(samples),'boards':len(boards)}))
