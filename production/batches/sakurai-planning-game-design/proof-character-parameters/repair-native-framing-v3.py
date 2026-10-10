"""Repair only prepared source framing; preserve native PNGs and both older trials."""
from pathlib import Path
from datetime import datetime, timezone
import json,os,hashlib,subprocess,traceback,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import psutil
ROOT=Path(__file__).resolve().parents[4]; PROOF=Path(__file__).resolve().parent
STATE=PROOF/'native-framing-execution-v3.json'; QA=ROOT/'shared/output/character-parameters/preflight/native-framing-v3'
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
assert not STATE.exists() and not QA.exists(),'Read existing work rather than rerunning.'
prior=json.loads((PROOF/'native-action-execution-v2.json').read_text(encoding='utf-8-sig'))
session=json.loads((PROOF/'native-action-execution-v2.json.session.json').read_text(encoding='utf-8-sig'))
assert prior['status']=='extracted-awaiting-direct-review' and session['outerExitCode']==0
resource=json.loads((ROOT/'shared/output/character-parameters/preflight/resource-before-framing-v3.json').read_text(encoding='utf-8-sig'))
assert (datetime.now().astimezone()-datetime.fromisoformat(resource['observedAt'])).total_seconds()<600
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
QA.mkdir(parents=True)
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18); cap=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
s={'schemaVersion':1,'slug':'character-parameters','status':'running','startedAt':stamp(),'pid':os.getpid(),'processCreateTime':psutil.Process().create_time(),'commandLine':sys.argv,'workingDirectory':str(ROOT),'cpuThreads':2,'gpuJobs':0,'resourceProof':'shared/output/character-parameters/preflight/resource-before-framing-v3.json','previousNativeExtractionRepeated':False,'newNativeExtractionCount':0,'sources':[],'directObservedFailure':{'matchNativeAndTrialBoards':[1,17],'dungeonsNativeAndTrialBoards':[11],'match':'Upward120px cuts off Ori aerial body at native f1515/1530.','dungeons':'Separate restoration crops truncate rightmost dice and STA baseline; inconsistent overlap with REACT label.','olderTrialsPreserved':True},'framing':'Original complete aspect and all HUD preserved at1600x900 centered x160,y0 over edge-to-edge same-frame blurred gameplay. No PPT matte, title card, foreign image, stretched game pixels or retimed action. This is a prepared framing trial requiring direct review; final fullscreen composition approval remains false. Official2:1 shorts retain existing1920x960 fullwidth trials.','nativeExactSelectionApproved':False,'sourceAdoptionApproved':False,'finalCueUiApproved':False,'finalFullscreenCompositionApproved':False,'externalResearchChanges':0}
def save():
 s['updatedAt']=stamp();write(STATE,s)
 qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';before=qpath.read_bytes();q=json.loads(before);item=next(i for i in q['items'] if i['slug']=='character-parameters');assert not item.get('videoId') and not any(item['checkpoints'].values())
 item.update(stage='native-framing-'+s['status'],updatedAt=stamp(),execution={k:s[k] for k in ['status','pid','processCreateTime','commandLine','workingDirectory','cpuThreads','gpuJobs']});item['execution'].update(state=str(STATE.relative_to(ROOT)).replace('\\','/'),phase='prepared-framing-repair-no-extraction');item['nextAction']='Directly review native actions and corrected framing, then normal-speed playback; no script/TTS/adoption before source gates.'
 q['updatedAt']=q['lastProgressAt']=stamp();assert qpath.read_bytes()==before;write(qpath,q)
def frame(im):
 im=im.convert('RGB');bg=im.resize((480,270),Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(12)).resize((1920,1080),Image.Resampling.BILINEAR)
 full=im.resize((1600,900),Image.Resampling.LANCZOS);bg.paste(full,(160,0))
 d=ImageDraw.Draw(bg);txt='캐릭터의 규칙을 함께 살펴봅시다.';b=d.textbbox((0,0),txt,font=cap);bw=b[2]-b[0]+44;bh=84;x=(1920-bw)//2;y=928
 d.rectangle((x+14,y+14,x+bw+14,y+bh+14),fill='#073c32');d.rectangle((x,y,x+bw,y+bh),fill='white',outline='#161b18',width=3);d.text((x+22,y+11-b[1]),txt,font=cap,fill='#080b09');return bg
def boards(files,samples,dest):
 out=[]
 for off in range(0,len(files),6):
  b=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(b)
  for n,(p,t) in enumerate(zip(files[off:off+6],samples[off:off+6])):
   x=n%3*640;y=n//3*408;im=Image.open(p).convert('RGB');im.thumbnail((640,360));b.paste(im,(x+(640-im.width)//2,y+36+(360-im.height)//2));d.text((x+6,y+3),str(t['nativeFrame'])+' '+','.join(t['windowKeys']),font=font,fill='white');d.text((x+6,y+384),f"PTS{t['pts']} t{t['timeSeconds']:.6f} trial-v3",font=font,fill=(180,230,230))
  p=dest/f'board-{off//6+1:03d}.jpg';b.save(p,quality=92);out.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'sampleRange':[off,min(off+6,len(files))]})
 return out
try:
 save()
 for src in prior['sources']:
  key=src['sourceKey']
  if key not in ['gBbKFYZYvbc','a8nwpiCqyTQ']:
   s['sources'].append({'sourceKey':key,'reusedUnchangedTrial':True,'samples':src['samples'],'trialBoards':src['trialBoards'],'trialFramingApproved':False});save();continue
  dest=QA/key;dest.mkdir();files=[];samples=[]
  for t in src['samples']:
   orig=ROOT/t['path'];assert sha(orig)==t['sha256'];p=dest/orig.name;frame(Image.open(orig)).save(p);files.append(p);samples.append({**t,'previousTrialPath':t['trialPath'],'trialPath':str(p.relative_to(ROOT)).replace('\\','/'),'trialSha256':sha(p)})
  s['sources'].append({'sourceKey':key,'sourceSha256':src['sourceSha256'],'reusedUnchangedTrial':False,'samples':samples,'trialBoards':boards(files,samples,dest),'trialFramingApproved':False});save()
 s.update(status='prepared-awaiting-direct-review',finishedAt=stamp(),totalTrialSamples=sum(len(i['samples']) for i in s['sources']),totalTrialBoards=sum(len(i['trialBoards']) for i in s['sources']));save();print(json.dumps({'status':s['status'],'samples':s['totalTrialSamples'],'boards':s['totalTrialBoards'],'adoption':False}),flush=True)
except BaseException:
 s.update(status='failed',error=traceback.format_exc());save();print(s['error'],flush=True);sys.exit(1)
