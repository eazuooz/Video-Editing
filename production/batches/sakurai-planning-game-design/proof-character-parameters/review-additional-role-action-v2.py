"""One new12s official action candidate; preserve every earlier bank and sample."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import psutil
ROOT=Path(__file__).resolve().parents[4];PROOF=Path(__file__).resolve().parent
QA=ROOT/'shared/output/character-parameters/preflight/additional-role-action-v2'
STATE=PROOF/'additional-role-action-execution-v2.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000 and resource['ownHeavyJobs']==0
lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
assert lease['project']=='character-parameters' and lease['state']=='waiting_for_current_job_boundary', 'Leave model execution exclusive; run this short CPU preparation only while research is still training'
assert not STATE.exists() and not QA.exists()
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
old=read(PROOF/'official-source-review-execution-v1.json')
src=next(s for s in old['sources'] if Path(s['localPath']).stem=='gBbKFYZYvbc')
p=ROOT/src['localPath'];assert sha(p)==src['sha256']
frames=read(ROOT/'shared/output/character-parameters/preflight/official-coarse-v1/gBbKFYZYvbc/native-pts.json')['frames']
assert all(int(b['best_effort_timestamp'])-int(a['best_effort_timestamp'])==3000 for a,b in zip(frames,frames[1:]))
a,b=8040,8400 #268–280s; earlier sealed window07 ends8040 half-open.
assert all(not (w['sourceKey']=='gBbKFYZYvbc' and max(a,w['startFrame'])<min(b,w['endFrameExclusive'])) for w in read(PROOF/'native-trim-plan-v4.json')['windows'])
indices=sorted(set(range(a,b,15))|set(range(a-3,a+4))|set(range(b-4,b+4)))
QA.mkdir(parents=True);native=QA/'native';native.mkdir();trial=QA/'fullscreen-v4';trial.mkdir()
samples=[];new=[];previous={r['pts']:r for r in src['samples']}
for i in indices:
 pts=int(frames[i]['best_effort_timestamp']);out=native/f'pts-{pts}.png'
 row=dict(nativeFrame=i,pts=pts,timeSeconds=pts/90000,path=rel(out),insideCandidate=a<=i<b)
 if pts in previous:
  oldrow=previous[pts];assert sha(ROOT/oldrow['path'])==oldrow['sha256'];os.link(ROOT/oldrow['path'],out);row['reusedCoarsePath']=oldrow['path']
 else:new.append(row)
 samples.append(row)
me=psutil.Process()
state=dict(startedAt=now(),status='single-CPU2-new-candidate-extraction',pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),cpuThreads=2,gpuJobs=0,sourcePath=src['localPath'],sourceSha256=src['sha256'],candidate=dict(key='rivals-match-09',sourceKey='gBbKFYZYvbc',startFrame=a,endFrameExclusive=b,startPts=a*3000,endPtsExclusive=b*3000,timeBase='1/90000',seconds=12,purpose='Fresh ground/air spacing and current-state action for role conclusion; not global character ranking or a mechanic multiplier.'),priorBankPath=rel(PROOF/'source-action-bank-v1.json'),priorBankSha256=sha(PROOF/'source-action-bank-v1.json'),protectedRequest=rel(ROOT/'projects/character-parameters/production/voice-clarity-v2/request.json'),resource=args.resource,samples=samples,boards=[],samplePixelReviewApproved=False,boundaryApproved=False,sourceAdoptionApproved=False,allFinalCueUiApproved=False,allNativeFramesReviewed=False,processOrResearchControlChanges=0,rasterGitAdditions=0)
def save():STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
save()
expr='+'.join(f"eq(pts,{r['pts']})" for r in new)
command=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-nostdin','-v','error','-threads','2','-filter_threads','2','-i',str(p),'-vf',"select='"+expr+"'",'-fps_mode','passthrough','-an','-threads','2',str(native/'extract-%04d.png')]
with (QA/'extraction.log').open('wb') as log:
 child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 state['child']=dict(pid=child.pid,createTime=psutil.Process(child.pid).create_time(),commandLine=command,log=rel(QA/'extraction.log'));save();code=child.wait()
 state['child'].update(exitCode=code,endedAt=now());save();assert code==0
files=sorted(native.glob('extract-*.png'));assert len(files)==len(new)
for f,r in zip(files,new):f.rename(ROOT/r['path'])
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
small=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
text='강점은 선택으로 이어집니다.'
for r in samples:
 im=Image.open(ROOT/r['path']).convert('RGB');assert im.size==(1280,720);out=im.resize((1920,1080),Image.Resampling.NEAREST)
 out.paste(im.crop((0,602,1280,657)).filter(ImageFilter.GaussianBlur(12)).resize((1920,95),Image.Resampling.BILINEAR),(0,985))
 out.paste(im.crop((16,657,315,720)).resize((449,95),Image.Resampling.NEAREST),(24,985))
 out.paste(im.crop((335,657,631,720)).resize((444,95),Image.Resampling.NEAREST),(1476,985))
 out.paste(im.crop((639,657,1280,720)).resize((462,45),Image.Resampling.LANCZOS),(729,1035))
 d=ImageDraw.Draw(out);box=d.textbbox((0,0),text,font=font);width=box[2]-box[0]+44;x=(1920-width)//2;y=928
 assert x>485 and x+width+14<1460
 d.rectangle((x+14,y+14,x+width+14,y+84+14),fill='#073c32');d.rectangle((x,y,x+width,y+84),fill='white',outline='#161b18',width=3);d.text((x+22,y+11-box[1]),text,font=font,fill='#080b09')
 tp=trial/Path(r['path']).name;out.save(tp);r.update(sha256=sha(ROOT/r['path']),trialPath=rel(tp),trialSha256=sha(tp))
for kind,field in [('native','path'),('trial','trialPath')]:
 for off in range(0,len(samples),6):
  board=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(board)
  for n,r in enumerate(samples[off:off+6]):
   x=n%3*640;y=n//3*408;im=Image.open(ROOT/r[field]).convert('RGB');im.thumbnail((640,360));board.paste(im,(x+(640-im.width)//2,y+36+(360-im.height)//2));d.text((x+6,y+3),f"native f{r['nativeFrame']} {kind}",font=small,fill='white');d.text((x+6,y+384),f"PTS{r['pts']} t{r['timeSeconds']:.6f}",font=small,fill=(180,230,230))
  bp=QA/f'{kind}-board-{off//6+1:03d}.jpg';board.save(bp,quality=93);state['boards'].append(dict(kind=kind,path=rel(bp),sha256=sha(bp),sampleRange=[off,min(off+6,len(samples))]))
assert sha(p)==src['sha256'] and sha(PROOF/'source-action-bank-v1.json')==state['priorBankSha256']
for r in read(ROOT/state['protectedRequest'])['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
state.update(status='new-candidate-extracted-awaiting-direct-review',finishedAt=now(),actualExtractExitCode=code,newExtractedCount=len(new),reusedCoarseSamples=len(samples)-len(new),sampleCount=len(samples));save()
print(json.dumps(dict(samples=len(samples),boards=len(state['boards']),actualExtractionExit=code,adopted=False,priorBankUnchanged=True),ensure_ascii=False))
