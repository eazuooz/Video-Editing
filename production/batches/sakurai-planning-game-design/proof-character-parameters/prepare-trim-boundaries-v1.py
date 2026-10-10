"""Extract only missing pixels around revised boundaries; reuse all sealed samples."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import json, hashlib, os, subprocess, sys, traceback, psutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[4]; P=Path(__file__).resolve().parent
QA=ROOT/'shared/output/character-parameters/preflight/trim-boundaries-v1'
STATE=P/'trim-boundary-execution-v1.json'; PLAN=P/'native-trim-plan-v3.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 t=p.with_name(p.name+f'.{os.getpid()}.tmp'); t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); os.replace(t,p)
assert not STATE.exists() and not PLAN.exists() and not QA.exists(), 'Inspect existing work; never repeat.'
resource=json.loads((ROOT/'shared/output/character-parameters/preflight/resource-before-boundary-v1.json').read_text(encoding='utf-8-sig'))
assert (datetime.now().astimezone()-datetime.fromisoformat(resource['observedAt'])).total_seconds()<600
assert json.loads((P/'fullscreen-ui-direct-review-v5.json').read_text(encoding='utf-8-sig'))['sampleFullscreenLayoutApproved']
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
sources=json.loads((P/'native-action-execution-v2.json').read_text(encoding='utf-8-sig'))['sources']
original=json.loads((P/'native-action-plan-v2.json').read_text(encoding='utf-8-sig'))
windows=[]
changes={'zetterburn-gameplay1':(0,280),'zetterburn-gameplay2':(0,129),'forsburn-gameplay2':(0,153),
 'slade-steal':(1710,1783),'hamir-react':(1902,2077),'artemis-stun':(2139,2344),'fleet-snipe':(2424,2577),'fleet-strike':(4533,4612)}
for w in original['windows']:
 x=dict(w); x['priorStartFrame']=w['startFrame']; x['priorEndFrameExclusive']=w['endFrameExclusive']
 if w['key'] in changes:x['startFrame'],x['endFrameExclusive']=changes[w['key']]
 src=next(s for s in sources if s['sourceKey']==x['sourceKey'])
 frames=json.loads((ROOT/src['nativePtsPath']).read_text(encoding='utf-8-sig'))['frames']
 step=int(frames[1]['best_effort_timestamp'])-int(frames[0]['best_effort_timestamp'])
 a,b=x['startFrame'],x['endFrameExclusive'];assert 0<=a<b<=len(frames)
 x['startPts']=int(frames[a]['best_effort_timestamp']); x['endPtsExclusive']=int(frames[b]['best_effort_timestamp']) if b<len(frames) else int(frames[-1]['best_effort_timestamp'])+step
 x['timeBase']=src['nativeVideo']['time_base'];x['durationSeconds']=float(Fraction(x['endPtsExclusive']-x['startPts'])*Fraction(x['timeBase']))
 x['sourceSha256']=src['sourceSha256'];x['boundaryDirectReviewApproved']=False
 windows.append(x)
plan={'schemaVersion':1,'slug':'character-parameters','recordedAt':stamp(),'windows':windows,
 'status':'revised-boundaries-pending-direct-review','totalUniqueSeconds':sum(w['durationSeconds'] for w in windows),
 'nativeExactSelectionApproved':False,'sourceAdoptionApproved':False,'finalCueUiApproved':False,
 'notes':'Exclude isolated idle tails, tooltip/dialogue/wipe and extended defeat result. Artemis ends after blocked action and before new draft. Native PTS, not browser autopause, defines exact half-open intervals.'}
write(PLAN,plan);QA.mkdir(parents=True)
state={'schemaVersion':1,'slug':'character-parameters','status':'running','pid':os.getpid(),'processCreateTime':psutil.Process().create_time(),'commandLine':sys.argv,'workingDirectory':str(ROOT),'sessionId':None,
 'cpuThreads':2,'gpuJobs':0,'resourceProof':'shared/output/character-parameters/preflight/resource-before-boundary-v1.json','planPath':str(PLAN.relative_to(ROOT)).replace('\\','/'),'planSha256':sha(PLAN),
 'children':[],'sources':[],'sourceAdoptionApproved':False,'nativeExactSelectionApproved':False,'externalResearchChanges':0,'rasterGitAdditions':0}
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18);cap=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def save():
 sp=STATE.with_name(STATE.name+'.session.json')
 if sp.exists():
  ss=json.loads(sp.read_text(encoding='utf-8-sig'))
  if ss['pid']==os.getpid():state['sessionId']=ss['sessionId']
 state['updatedAt']=stamp();write(STATE,state)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';before=qp.read_bytes();q=json.loads(before);item=next(i for i in q['items'] if i['slug']=='character-parameters')
 assert not item.get('videoId') and not any(item['checkpoints'].values())
 item.update(stage='native-trim-'+state['status'],updatedAt=stamp(),execution={k:state[k] for k in ['status','pid','processCreateTime','commandLine','workingDirectory','sessionId','cpuThreads','gpuJobs']})
 item['execution']['state']=str(STATE.relative_to(ROOT)).replace('\\','/');item['execution']['child']=state['children'][-1] if state['children'] else None
 item['nextAction']='Directly read all revised boundary boards and normal-speed selected action playback; source candidates/adoption before independent narration.'
 q['updatedAt']=q['lastProgressAt']=stamp();assert qp.read_bytes()==before;write(qp,q)
def compose(im,key):
 im=im.convert('RGB')
 if key=='gBbKFYZYvbc':
  out=im.resize((1920,1080),Image.Resampling.NEAREST)
  out.paste(im.crop((0,602,1280,657)).filter(ImageFilter.GaussianBlur(12)).resize((1920,95)),(0,985))
  out.paste(im.crop((16,657,315,720)).resize((449,95),Image.Resampling.NEAREST),(24,985))
  out.paste(im.crop((335,657,631,720)).resize((444,95),Image.Resampling.NEAREST),(1476,985))
  out.paste(im.crop((639,657,1280,720)).resize((462,45),Image.Resampling.LANCZOS),(729,1035))
 elif key=='a8nwpiCqyTQ':
  out=im.copy();out.paste(im.crop((406,870,1520,920)).filter(ImageFilter.GaussianBlur(12)).resize((1114,144)),(406,921))
  out.paste(im.crop((406,921,1520,1065)).resize((424,55),Image.Resampling.NEAREST),(1490,135))
 else:
  out=im.resize((1920,1080)).filter(ImageFilter.GaussianBlur(22));out.paste(im.resize((1920,960),Image.Resampling.NEAREST),(0,0))
 d=ImageDraw.Draw(out);text='캐릭터마다 규칙이 다릅니다.';b=d.textbbox((0,0),text,font=cap);bw=b[2]-b[0]+44;x=(1920-bw)//2;y=928
 d.rectangle((x+14,y+14,x+bw+14,y+98),fill='#073c32');d.rectangle((x,y,x+bw,y+84),fill='white',outline='#161b18',width=3);d.text((x+22,y+11-b[1]),text,font=cap,fill='#080b09');return out
try:
 save()
 for src in sources:
  key=src['sourceKey'];wins=[w for w in windows if w['sourceKey']==key]
  if not wins:continue
  p=ROOT/src['sourcePath'];assert sha(p)==src['sourceSha256']
  frames=json.loads((ROOT/src['nativePtsPath']).read_text(encoding='utf-8-sig'))['frames']
  selected={}
  for w in wins:
   for edge in [w['startFrame'],w['endFrameExclusive']]:
    for f in range(max(0,edge-3),min(len(frames),edge+4)):selected.setdefault(f,[]).append(w['key'])
  old={x['nativeFrame']:x for x in src['samples']}; sub=QA/key;sub.mkdir();new=[];samples=[]
  for f,keys in sorted(selected.items()):
   s={'nativeFrame':f,'pts':int(frames[f]['best_effort_timestamp']),'timeSeconds':float(frames[f]['best_effort_timestamp_time']),'windowKeys':sorted(set(keys))}
   if f in old:
    o=old[f];assert sha(ROOT/o['path'])==o['sha256'];s.update(path=o['path'],sha256=o['sha256'],reused=True)
   else:s.update(path=str((sub/f"pts-{s['pts']}.png").relative_to(ROOT)).replace('\\','/'),reused=False);new.append(s)
   samples.append(s)
  if new:
   expr='+'.join(f"eq(pts,{x['pts']})" for x in new);args=[FF,'-nostdin','-v','error','-threads','2','-filter_threads','2','-i',str(p),'-vf',"select='"+expr+"'",'-fps_mode','passthrough','-an','-threads','2',str(sub/'new-%04d.png')]
   log=sub/'extract.log'
   with log.open('wb') as stream:
    c=subprocess.Popen(args,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    child={'sourceKey':key,'pid':c.pid,'processCreateTime':psutil.Process(c.pid).create_time(),'commandLine':args,'workingDirectory':str(ROOT),'log':str(log.relative_to(ROOT)).replace('\\','/'),'status':'running'};state['children'].append(child);save();code=c.wait();child.update(status='exited',exitCode=code);assert code==0
   files=sorted(sub.glob('new-*.png'));assert len(files)==len(new)
   for f,s in zip(files,new):f.rename(ROOT/s['path']);s['sha256']=sha(ROOT/s['path'])
  for s in samples:
   t=sub/f"trial-{s['nativeFrame']}.png";compose(Image.open(ROOT/s['path']),key).save(t);s.update(trialPath=str(t.relative_to(ROOT)).replace('\\','/'),trialSha256=sha(t))
  boards=[]
  for off in range(0,len(samples),6):
   b=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(b)
   for n,s in enumerate(samples[off:off+6]):
    x=n%3*640;y=n//3*408;b.paste(Image.open(ROOT/s['trialPath']).resize((640,360)),(x,y+36));d.text((x+6,y+3),f"{key} f{s['nativeFrame']}",font=font,fill='white');d.text((x+6,y+384),f"PTS{s['pts']} {s['timeSeconds']:.6f}",font=font,fill='white')
   dest=sub/f'board-{off//6+1:03d}.jpg';b.save(dest,quality=93);boards.append({'path':str(dest.relative_to(ROOT)).replace('\\','/'),'sha256':sha(dest),'sampleRange':[off,min(off+6,len(samples))]})
  state['sources'].append({'sourceKey':key,'newExtractionCount':len(new),'reusedNativeCount':len(samples)-len(new),'samples':samples,'boards':boards});save()
 state['status']='prepared-awaiting-direct-review';state['totalSamples']=sum(len(s['samples']) for s in state['sources']);state['newExtractionCount']=sum(s['newExtractionCount'] for s in state['sources']);state['totalBoards']=sum(len(s['boards']) for s in state['sources']);save()
 print(json.dumps({k:state[k] for k in ['status','pid','processCreateTime','totalSamples','newExtractionCount','totalBoards']}),flush=True)
except BaseException:
 state['status']='failed';state['error']=traceback.format_exc();save();print(state['error'],flush=True);sys.exit(1)
