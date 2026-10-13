"""Lower backgrounds in two dense explanations, preserving narration and all other mix samples."""
from pathlib import Path
import sys,json,datetime,hashlib,subprocess,psutil,math
import numpy as np,soundfile as sf
from scipy.ndimage import uniform_filter1d
P=Path(__file__).resolve().parent;R=P.parents[3];FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
sys.stdout.reconfigure(encoding='utf-8')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state=P/'mix-duck-v2.json';assert not state.exists()
c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']=='hierarchical-game-outlines' and c['newProductionAuthorization']['fullProductionAuthorized']
prior=read(P/'mix-contexts-v1.json');assert prior['exitCode']==0
try:assert abs(psutil.Process(prior['pid']).create_time()-prior['createTime'])>.01
except psutil.NoSuchProcess:pass
me=psutil.Process();j=dict(status='running',at=now(),worker=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),resource=dict(cpu=psutil.cpu_percent(interval=1),ram=psutil.virtual_memory().available,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)),voiceChanged=False,reason='Two full/independent mixed ASR alternatives while original voice readbacks retained expected wording. Lower only backgrounds for narration clarity; no assertion of human pronunciation failure.')
assert j['resource']['cpu']<85 and j['resource']['ram']>8e9;write(state,j)
timeline=read(P/'final-timeline-v1.json');old=read(P/'mix-execution-v1.json')['completed'][-1];layers=old['layers'];sr=48000
base,rate=sf.read(P/'current-mix-prelimit-local.wav',dtype='float32');native,nr=sf.read(P/'native-stem-local.wav',dtype='float32');music,mr=sf.read(P/'lofi-stem-local.wav',dtype='float32');assert rate==nr==mr==sr
native*=10**(layers['native']['gainDb']/20);music*=10**(layers['lofi']['gainDb']/20)
atten=np.ones(len(base),np.float32)
for cut in timeline['pieces']:
 if not cut['kind'].startswith('ex'):atten[cut['startFrame']*800:(cut['startFrame']+cut['frames'])*800]=10**(-3/20)
music*=uniform_filter1d(atten,size=21600,mode='nearest')[:,None]
a=120*800;b=(120+timeline['bodyFrames'])*800;music[a:a+21600]*=np.linspace(0,1,21600)[:,None];music[b-21600:b]*=np.linspace(1,0,21600)[:,None]
modified=base.copy();windows=[]
for sid,pidx in [('01a',2),('06',0)]:
 sc=next(s for s in timeline['scenes'] if s['id']==sid);p=sc['paragraphs'][pidx];start=sc['startFrame']/60+max(0,p['startSeconds']-.2);end=sc['startFrame']/60+min(sc['frames']/60,p['endSeconds']+.25);a=round(start*sr);b=round(end*sr)
 w=np.ones(b-a,np.float32);fade=7200;w[:fade]=np.linspace(0,1,fade);w[-fade:]=np.linspace(1,0,fade)
 delta=native[a:b]*((10**(-9/20)-1)*w[:,None])+music[a:b]*((10**(-6/20)-1)*w[:,None]);modified[a:b]+=delta*10**(-1.05/20)
 windows.append(dict(scene=sid,start=start,end=end,gameGainDb=-9,lofiGainDb=-6))
changed=np.any(base!=modified,axis=1);outside=np.ones(len(base),bool)
for w in windows:outside[round(w['start']*sr):round(w['end']*sr)]=False
assert not changed[outside].any()
sf.write(P/'current-mix-prelimit-v2-local.wav',modified,sr,subtype='FLOAT')
def run(args):
 r=subprocess.run([FF,'-hide_banner','-nostdin','-n',*args],capture_output=True,creationflags=0x08000000);assert r.returncode==0,r.stderr.decode('utf-8','replace')[-2000:];return r.stdout,r.stderr.decode('utf-8','replace')
run(['-i',str(P/'current-mix-prelimit-v2-local.wav'),'-af','alimiter=limit=0.794328:attack=5:release=50:level=false:latency=true','-c:a','pcm_s24le',str(P/'current-mix-v2.wav')])
run(['-i',str(P/'current-mix-v2.wav'),'-c:a','aac','-b:a','192k','-ar','48000','-ac','2',str(P/'current-mix-v2.m4a')])
def decode(p):return np.frombuffer(run(['-i',str(p),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1'])[0],dtype='<f4').reshape(-1,2)
oldpcm=decode(P/'current-mix-v1.m4a');newpcm=decode(P/'current-mix-v2.m4a');assert oldpcm.shape==newpcm.shape
diff=np.any(oldpcm!=newpcm,axis=1);allowed=np.zeros(len(newpcm),bool)
for w in windows:allowed[max(0,round((w['start']-2)*sr)):min(len(allowed),round((w['end']+2)*sr))]=True
assert not diff[~allowed].any(),'AAC differences outside explicitly reviewed two-second joins; inspect instead of reusing evidence'
d=P/'mix-review-v2-local';d.mkdir()
for sc in timeline['scenes']:
 a=sc['startFrame']*800;b=(sc['startFrame']+sc['frames'])*800;sf.write(d/f'{sc["id"]}.wav',newpcm[a:b],sr,subtype='PCM_16')
_,loud=run(['-i',str(P/'current-mix-v2.m4a'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);measured=json.loads(loud[loud.rfind('{'):loud.rfind('}')+1]);assert float(measured['input_tp'])<=-1.5
inputs=read(P/'mix-final-inputs-v1.json');write(P/'mix-final-inputs-before-duck-v1.json',inputs);inputs.update(audio=(P/'current-mix-v2.m4a').relative_to(R).as_posix(),sha256=sha(P/'current-mix-v2.m4a'),scenes=[dict(id=sc['id'],path=(d/f'{sc["id"]}.wav').relative_to(R).as_posix(),sha256=sha(d/f'{sc["id"]}.wav')) for sc in timeline['scenes']]);write(P/'mix-final-inputs-v1.json',inputs)
request=read(P/'mix-context-plan-v1.json');request.update(mixSha256=inputs['sha256'],audio=inputs['audio'],reviewFolder='mix-review-v2-local',scope='Only two changed passages; all decoded AAC outside both windows plus two-second joins is byte exact to whole-reviewed V1.');write(P/'mix-context-plan-v2.json',request)
code=(P/'review-mix-contexts.py').read_text(encoding='utf-8').replace("'mix-contexts-v1.json'", "'mix-contexts-v2.json'").replace("'mix-context-plan-v1.json'", "'mix-context-plan-v2.json'").replace("sha(P/'current-mix-v1.m4a')", "sha(R/request['audio'])").replace("mix-review-local/", "mix-review-v2-local/").replace("mix-context-{r", "mix-context-v2-{r")
(P/'review-mix-contexts-v2.py').write_text(code,encoding='utf-8')
j.update(status='complete-pending-two-current-contexts',exitCode=0,endedAt=now(),windows=windows,unchangedPrelimitSamplesExact=True,unchangedDecodedAacOutsideWindowsAndTwoSecondJoinsExact=True,changedDecodedSamples=int(diff.sum()),reviewedPriorMixSha256=old['sha256'],currentMixSha256=inputs['sha256'],decodedAAC=measured);write(state,j);print(json.dumps(j,ensure_ascii=False))
