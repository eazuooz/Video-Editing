from pathlib import Path
import sys,os,json,hashlib,datetime,subprocess,psutil
from PIL import Image
from captions import image as caption_image
P=Path(__file__).resolve().parent;R=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['fullProductionAuthorized']
mode=sys.argv[1]
if mode=='preflight':
 dest=P/'native-caption-preflight-local.png';assert not dest.exists()
 source=next(r for r in read(P/'source-inspection.json')['samples'] if r['originalSecondsApprox']==1032)
 assert sha(R/source['file'])==source['sha256']
 intermediate=P/'native-preflight-bg-local.png'
 cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-loglevel','error','-nostdin','-n','-i',str(R/source['file']),'-filter_complex_threads','1','-filter_complex','[0:v]split=2[bg][fg];[bg]scale=1920:1080:flags=neighbor,boxblur=32:2[blur];[fg]scale=960:864:flags=neighbor[front];[blur][front]overlay=480:12,setsar=1[v]','-map','[v]','-frames:v','1','-threads','2',str(intermediate)]
 subprocess.run(cmd,check=True,creationflags=0x08000000)
 timeline=read(P/'final-timeline-v1.json');cue=next(c for c in timeline['captionsKo'] if c['startFrame']<=46*60<c['endFrame'])
 bg=Image.open(intermediate).convert('RGBA');bg.alpha_composite(caption_image(cue['text']));bg.convert('RGB').save(dest)
 write(P/'caption-timing-direct-review.json',dict(at=now(),timelineSha256=sha(P/'final-timeline-v1.json'),all27PairedParagraphsRead=True,koCues=55,enCues=56,languageCueMapping='final-timeline-v1.json paragraphs koCues/enCues',changedVoiceBoundToActualWords=True,retainedCueTimingShiftedWithRetainedVoice=True,referenceNames=0,bodyRatio={'actual':11022,'explanation':7348,'errorFrames':0},sourcePreflight=dict(path=dest.relative_to(R).as_posix(),sha256=sha(dest),sourceSha256=source['sha256'],cue=cue),pixelsApproved=False))
 print(dest)
elif mode=='render':
 assert read(P/'native-caption-preflight-review.json')['pixelsApproved']
 state=P/'white-render-wrapper-v1.json';assert not state.exists()
 me=psutil.Process();anc={a.pid for a in me.parents()};active=[]
 for pr in psutil.process_iter(['pid','cmdline','create_time'],ad_value=None):
  cmd=' '.join(pr.info['cmdline'] or []).replace('\\','/')
  if pr.pid in anc|{me.pid} or 'powershell.exe' in cmd.lower():continue
  if '/pokemon-opening-v2/' in cmd and any(x in cmd for x in ['render-','review-','build-current-v1.py']):active.append(pr.info)
 resource=dict(at=now(),cpu=psutil.cpu_percent(interval=1),ram=psutil.virtual_memory().available,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True),otherOwnedWorkers=active)
 assert not active and resource['cpu']<85 and resource['ram']>8e9
 j=dict(status='starting',worker=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),resource=resource)
 write(state,j);command=['node',str(P/'render-pokemon.cjs'),'hierarchical-game-outlines','v1']
 child=subprocess.Popen(command,cwd=R,creationflags=0x08000000);j.update(childPid=child.pid,command=command,status='rendering');write(state,j)
 code=child.wait();j.update(actualChildExit=code,status='rendered-pending-final-output-pixels' if code==0 else 'failed',endedAt=now());write(state,j);sys.exit(code)
