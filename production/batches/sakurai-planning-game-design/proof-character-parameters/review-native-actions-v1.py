"""Single CPU2 extraction of new native samples and trial caption-safe framing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,subprocess,sys,traceback,math
from fractions import Fraction
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import psutil
ROOT=Path(__file__).resolve().parents[4];PROOF=Path(__file__).resolve().parent
QA=ROOT/'shared/output/character-parameters/preflight/native-actions-v1'
STATE=PROOF/'native-action-execution-v1.json';PLAN=PROOF/'native-action-plan-v1.json'
recovery='--recovery-v2' in sys.argv
prior=None
if recovery:
 prior=json.loads(STATE.read_text(encoding='utf-8-sig'))
 assert prior['status']=='failed' and 'pkt_duration' in prior['error']
 STATE=PROOF/'native-action-execution-v2.json';PLAN=PROOF/'native-action-plan-v2.json';QA=QA.with_name('native-actions-v2')
QUEUE=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp=lambda:datetime.now(timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
if STATE.exists() or PLAN.exists():raise SystemExit('Existing native review; inspect state instead of repeating.')
for name in ['official-coarse-direct-review-v1.json','dungeons-coarse-direct-review-v1.json']:
 r=json.loads((PROOF/name).read_text(encoding='utf-8-sig'));assert r['coarseSamplePixelReviewApproved']
resource=json.loads((ROOT/'shared/output/character-parameters/preflight/resource-before-native-v1.json').read_text(encoding='utf-8-sig'))
age=datetime.now().astimezone()-datetime.fromisoformat(resource['observedAt'])
if age.total_seconds()>600:raise SystemExit('Refresh actual resources before this new CPU job.')
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
old=json.loads((PROOF/'official-source-review-execution-v1.json').read_text(encoding='utf-8-sig'))
d=json.loads((PROOF/'dungeons-source-execution-v2.json').read_text(encoding='utf-8-sig'))
sources={Path(s['localPath']).stem:s for s in old['sources']}
sources['a8nwpiCqyTQ']={**d['source'],'video':d['video'],'samples':d['samples'],'ptsPath':'shared/output/character-parameters/preflight/dungeons-coarse-v2/native-pts.json'}
windows=[]
for key,end in [('zetterburn-gameplay1',300),('zetterburn-gameplay2',137),('orcane-gameplay1',155),('orcane-gameplay2',210),('forsburn-gameplay1',255),('forsburn-gameplay2',167)]:
 windows.append({'key':key,'sourceKey':key,'startFrame':0,'endFrameExclusive':end,'stepSeconds':.25,'purpose':'Distinct fire/water/clone or smoke rule shown by official native gameplay; no web looping.'})
for i,(a,b) in enumerate([(12,24),(24,44),(48,60),(84,108),(120,148),(184,216),(246,268),(310,340)]):
 windows.append({'key':f'rivals-match-{i+1:02}','sourceKey':'gBbKFYZYvbc','startFrame':a*30,'endFrameExclusive':b*30,'stepSeconds':.5,'purpose':'Historical Etalus/Ori movement, pressure, spacing or armor-like state; no universal balance ranking.'})
for key,a,b,purpose in [('slade-steal',1698,1818,'STEAL hit and coin change; temporary dice state, not base-stat claim.'),('hamir-react',1860,2088,'REACT hit adds DEF followed by a blocked enemy attack.'),('artemis-stun',2115,2388,'STUN hit changes opposing dice state, followed by STRONG action.'),('fleet-snipe',2418,2577,'SNIPE attack and stamina indicators.'),('fleet-strike',4515,4674,'Different boss STRIKE action and1HP loss; exclude result.')]:
 windows.append({'key':key,'sourceKey':'a8nwpiCqyTQ','startFrame':a,'endFrameExclusive':b,'stepSeconds':.1,'purpose':purpose})
plan={'schemaVersion':1,'slug':'character-parameters','recordedAt':stamp(),'windows':windows,'nativeExactSelectionApproved':False,'sourceAdoptionApproved':False,'newScriptTtsOrRender':False,'loopOrSlowdown':False,'sourceAudioUse':False,'framingTrial':{'gBbKFYZYvbc':'Full width at original aspect; upward120px with same-frame bottom extension; restore broadcast names bar and timer from this same source frame. Direct check required for high aerial actions. Actual narration cues must be single-line at960970.','a8nwpiCqyTQ':'Full width unchanged aspect, upward168px with same-frame bottom extension; preserve native upper stat table and character-name area from the same frame. Direct check required.','officialShorts':'Native2:1 pixel art nearest-neighbour full width1920x960, same-frame extension below; single-line captions over empty bottom region.'},'nextAction':'Directly review every native/trial board; trim or change framing on observed collision, not on automated color checks.'}
write(PLAN,plan);QA.mkdir(parents=True,exist_ok=False)
state={'schemaVersion':1,'slug':'character-parameters','status':'initializing','startedAt':stamp(),'pid':os.getpid(),'processCreateTime':psutil.Process().create_time(),'commandLine':sys.argv,'workingDirectory':str(ROOT),'sessionId':None,'cpuThreads':2,'gpuJobs':0,'resourceProof':'shared/output/character-parameters/preflight/resource-before-native-v1.json','planPath':str(PLAN.relative_to(ROOT)).replace('\\','/'),'planSha256':sha(PLAN),'children':[],'sources':[],'windows':windows,'nativeExactSelectionApproved':False,'sourceAdoptionApproved':False,'finalCueUiApproved':False,'newScriptTtsOrRender':False,'externalResearchChanges':0}
if prior:
 state['sources']=prior['sources']
 state['recovery']={'priorState':'production/batches/sakurai-planning-game-design/proof-character-parameters/native-action-execution-v1.json','priorOuterExitCode':1,'failure':'Last source frame lacks pkt_duration; no assumed endpoint duration.','repair':'Use validated constant native PTS difference as last frame duration.','completedSourcesReused':[s['sourceKey'] for s in prior['sources']],'completedExtractionRepeated':False}
def save(status):
 state.update(status=status,updatedAt=stamp());sp=STATE.with_name(STATE.name+'.session.json')
 if sp.exists():
  ss=json.loads(sp.read_text(encoding='utf-8-sig'))
  if ss['pid']==os.getpid():state['sessionId']=ss['sessionId']
 write(STATE,state)
 before=QUEUE.read_bytes();q=json.loads(before);item=next(x for x in q['items'] if x['slug']=='character-parameters')
 assert not item.get('videoId') and not any(item['checkpoints'].values())
 item.update(stage='native-action-'+status,updatedAt=stamp(),execution={k:state[k] for k in ['status','pid','processCreateTime','commandLine','workingDirectory','sessionId','cpuThreads','gpuJobs']})
 item['execution'].update(phase='exact-native-sampling-and-caption-framing-trial',state=str(STATE.relative_to(ROOT)).replace('\\','/'),child=state['children'][-1] if state['children'] else None)
 item['nextAction']=plan['nextAction'];q['updatedAt']=q['lastProgressAt']=stamp();assert QUEUE.read_bytes()==before;write(QUEUE,q)
def run(args,label):
 log=QA/(label+'.log')
 with log.open('wb') as f:
  c=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  r={'label':label,'pid':c.pid,'processCreateTime':psutil.Process(c.pid).create_time(),'commandLine':args,'workingDirectory':str(ROOT),'log':str(log.relative_to(ROOT)).replace('\\','/'),'startedAt':stamp(),'status':'running'};state['children'].append(r);save('single-cpu-job-running')
  code=c.wait();r.update(status='exited',exitCode=code,endedAt=stamp())
  if code:raise RuntimeError(f'{label} exit{code}; preserve failed output.')
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18);captionfont=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def frame_trial(im,key):
 im=im.convert('RGB');w,h=im.size
 full=im.resize((1920,round(h*1920/w)),Image.Resampling.NEAREST if w==400 else Image.Resampling.LANCZOS)
 bg=im.resize((1920,1080),Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(22))
 if key=='gBbKFYZYvbc':
  bg.paste(full,(0,-120));bg.paste(full.crop((0,0,1920,54)),(0,0));bg.paste(full.crop((825,54,1110,111)),(825,54))
 elif key=='a8nwpiCqyTQ':
  bg.paste(full,(0,-168));bg.paste(full.crop((530,0,1385,340)),(530,0));bg.paste(full.crop((0,0,490,130)),(0,0))
 else:bg.paste(full,(0,0))
 draw=ImageDraw.Draw(bg);text='캐릭터의 규칙을 함께 살펴봅시다.';box=draw.textbbox((0,0),text,font=captionfont);bw=box[2]-box[0]+44;bh=84;x=(1920-bw)//2;y=970-bh//2
 draw.rectangle((x+14,y+14,x+bw+14,y+bh+14),fill='#073c32');draw.rectangle((x,y,x+bw,y+bh),fill='white',outline='#161b18',width=3);draw.text((x+22,y+11-box[1]),text,font=captionfont,fill='#080b09')
 return bg
def board(files,samples,dest,trial=False):
 out=[]
 for off in range(0,len(files),6):
  b=Image.new('RGB',(1920,816),(24,24,24));draw=ImageDraw.Draw(b)
  for n,(p,s) in enumerate(zip(files[off:off+6],samples[off:off+6])):
   x=n%3*640;y=n//3*408;im=Image.open(p).convert('RGB');im.thumbnail((640,360));b.paste(im,(x+(640-im.width)//2,y+36+(360-im.height)//2));draw.text((x+6,y+3),str(s['nativeFrame'])+' '+','.join(s['windowKeys']),font=font,fill='white');draw.text((x+6,y+384),f"PTS{s['pts']} t{s['timeSeconds']:.6f}"+(' trial' if trial else ''),font=font,fill=(180,230,230))
  p=dest/f'board-{off//6+1:03d}.jpg';b.save(p,quality=92);out.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'sampleRange':[off,min(off+6,len(files))]})
 return out
try:
 save('initializing')
 for key,src in sources.items():
  wins=[x for x in windows if x['sourceKey']==key]
  if not wins:continue
  p=ROOT/src['localPath'];assert sha(p)==src['sha256']
  ptsPath=src.get('ptsPath',f'shared/output/character-parameters/preflight/official-coarse-v1/{key}/native-pts.json')
  frames=json.loads((ROOT/ptsPath).read_text(encoding='utf-8-sig'))['frames'];indices=set();mapping={}
  delta=int(frames[1]['best_effort_timestamp'])-int(frames[0]['best_effort_timestamp'])
  assert delta>0 and all(int(b['best_effort_timestamp'])-int(a['best_effort_timestamp'])==delta for a,b in zip(frames,frames[1:]))
  for win in wins:
   a,b=win['startFrame'],win['endFrameExclusive'];assert 0<=a<b<=len(frames)
   win['startPts']=int(frames[a]['best_effort_timestamp']);win['endPtsExclusive']=int(frames[b]['best_effort_timestamp']) if b<len(frames) else int(frames[-1]['best_effort_timestamp'])+delta
   win['timeBase']=src['video']['time_base'];win['durationSeconds']=float((win['endPtsExclusive']-win['startPts'])*Fraction(win['timeBase']))
   step=max(1,round(win['stepSeconds']/float(frames[1]['best_effort_timestamp_time'])))
   sel=set(range(a,b,step))|set(range(max(0,a-3),min(len(frames),a+4)))|set(range(max(0,b-4),min(len(frames),b+4)))
   for i in sel:indices.add(i);mapping.setdefault(i,[]).append(win['key'])
  if any(s['sourceKey']==key for s in state['sources']):continue
  samples=[{'nativeFrame':i,'pts':int(frames[i]['best_effort_timestamp']),'timeSeconds':float(frames[i]['best_effort_timestamp_time']),'windowKeys':mapping[i]} for i in sorted(indices)]
  sub=QA/key;sub.mkdir();raw=sub/'native';raw.mkdir();trial=sub/'trial-single-line';trial.mkdir()
  previous={s['pts']:s for s in src['samples']};new=[]
  for s in samples:
   out=raw/f"pts-{s['pts']}.png"
   if s['pts'] in previous:
    old=previous[s['pts']];assert sha(ROOT/old['path'])==old['sha256'];os.link(ROOT/old['path'],out);s['reusedCoarsePath']=old['path']
   else:new.append(s)
   s['path']=str(out.relative_to(ROOT)).replace('\\','/')
  if new:
   expr='+'.join(f"eq(pts,{s['pts']})" for s in new)
   run([FF,'-nostdin','-v','error','-threads','2','-filter_threads','2','-i',str(p),'-vf',"select='"+expr+"'",'-fps_mode','passthrough','-an','-threads','2',str(raw/'extract-%04d.png')],key+'-new-native-extract')
   files=sorted(raw.glob('extract-*.png'));assert len(files)==len(new)
   for f,s in zip(files,new):f.rename(ROOT/s['path'])
  original=[];framed=[]
  for s in samples:
   f=ROOT/s['path'];s['sha256']=sha(f);original.append(f);tf=trial/f.name;frame_trial(Image.open(f),key).save(tf);s['trialPath']=str(tf.relative_to(ROOT)).replace('\\','/');s['trialSha256']=sha(tf);framed.append(tf)
  state['sources'].append({'sourceKey':key,'sourcePath':src['localPath'],'sourceSha256':src['sha256'],'nativeVideo':src['video'],'nativePtsPath':ptsPath,'samples':samples,'nativeBoards':board(original,samples,raw),'trialBoards':board(framed,samples,trial,True),'actualNewExtractionCount':len(new),'reusedCoarseSamples':len(samples)-len(new),'nativeReviewed':False,'trialFramingApproved':False})
  save('source-extracted-awaiting-direct-review')
 write(PLAN,plan);state['planSha256']=sha(PLAN);state['totalNativeSamples']=sum(len(x['samples']) for x in state['sources']);state['totalNativeBoards']=sum(len(x['nativeBoards']) for x in state['sources']);state['totalTrialBoards']=sum(len(x['trialBoards']) for x in state['sources']);save('extracted-awaiting-direct-review')
 print(json.dumps({'status':state['status'],'nativeSamples':state['totalNativeSamples'],'nativeBoards':state['totalNativeBoards'],'trialBoards':state['totalTrialBoards'],'adopted':False}),flush=True)
except BaseException:
 state['error']=traceback.format_exc()
 try:save('failed')
 except Exception:write(STATE,state)
 print(state['error'],flush=True);sys.exit(1)
