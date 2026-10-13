"""Inspect the already encoded V2; never rerun the mix after its strict reuse check failed."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,psutil
import numpy as np,soundfile as sf
P=Path(__file__).resolve().parent;R=P.parents[3];FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
sys.stdout.reconfigure(encoding='utf-8')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']=='hierarchical-game-outlines' and c['newProductionAuthorization']['fullProductionAuthorized']
s=read(P/'mix-duck-v2.json')
try:assert abs(psutil.Process(s['worker']['pid']).create_time()-s['worker']['createTime'])>.01
except psutil.NoSuchProcess:pass
assert not (P/'mix-duck-existing-verification-v2.json').exists()
s.update(status='encoded-output-held-strict-reuse-check-failed',exitCode=1,actualSession=81041,completionChunk='bc434b',workerDead=True,error='Decoded AAC differed outside the two requested changes plus two-second joins. Reuse assertion failed; encoded outputs preserved and not regenerated.')
write(P/'mix-duck-v2.json',s)
me=psutil.Process();resource=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),cpu=psutil.cpu_percent(interval=1),ram=psutil.virtual_memory().available)
assert resource['cpu']<85 and resource['ram']>8e9
t=read(P/'final-timeline-v1.json');windows=[]
for sid,pidx in [('01a',2),('06',0)]:
 sc=next(x for x in t['scenes'] if x['id']==sid);p=sc['paragraphs'][pidx]
 windows.append(dict(scene=sid,start=sc['startFrame']/60+max(0,p['startSeconds']-.2),end=sc['startFrame']/60+min(sc['frames']/60,p['endSeconds']+.25),gameGainDb=-9,lofiGainDb=-6))
def ff(args):
 r=subprocess.run([FF,'-hide_banner','-nostdin','-n',*args],capture_output=True,creationflags=0x08000000);assert r.returncode==0,r.stderr.decode('utf-8','replace')[-2000:];return r.stdout,r.stderr.decode('utf-8','replace')
def decode(p):return np.frombuffer(ff(['-i',str(p),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1'])[0],dtype='<f4').reshape(-1,2)
old=decode(P/'current-mix-v1.m4a');new=decode(P/'current-mix-v2.m4a');assert old.shape==new.shape
a,sr=sf.read(P/'current-mix-v1.wav',dtype='float32');b,br=sf.read(P/'current-mix-v2.wav',dtype='float32');assert sr==br==48000 and a.shape==b.shape
allowed=np.zeros(len(new),bool)
for w in windows:allowed[max(0,round((w['start']-.1)*sr)):min(len(allowed),round((w['end']+.1)*sr))]=True
assert np.array_equal(a[~allowed[:len(a)]],b[~allowed[:len(b)]]),'PCM changed beyond ducking/limiter joins'
delta=(old-new)[~allowed];nonzero=np.any(delta!=0,axis=1)
d=P/'mix-review-v2-local';d.mkdir(exist_ok=False)
for sc in t['scenes']:
 start=sc['startFrame']*800;end=(sc['startFrame']+sc['frames'])*800;sf.write(d/f'{sc["id"]}.wav',new[start:end],sr,subtype='PCM_16')
_,loud=ff(['-i',str(P/'current-mix-v2.m4a'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);measured=json.loads(loud[loud.rfind('{'):loud.rfind('}')+1]);assert float(measured['input_tp'])<=-1.5
inputs=read(P/'mix-final-inputs-v1.json');write(P/'mix-final-inputs-before-duck-v1.json',inputs)
inputs.update(audio=(P/'current-mix-v2.m4a').relative_to(R).as_posix(),sha256=sha(P/'current-mix-v2.m4a'),scenes=[dict(id=sc['id'],path=(d/f'{sc["id"]}.wav').relative_to(R).as_posix(),sha256=sha(d/f'{sc["id"]}.wav')) for sc in t['scenes']]);write(P/'mix-final-inputs-v1.json',inputs)
j=dict(at=now(),resource=resource,sourceFailure='mix-duck-v2.json',noReencoding=True,voiceUnchanged=True,windows=windows,pcmOutsideChangesAnd100msLimiterJoinsExact=True,decodedAacOutsideChangesExact=not bool(nonzero.any()),aacDifferenceOutsideWindows=dict(changedSamples=int(nonzero.sum()),maxAbsolute=float(np.abs(delta).max()),rms=float(np.sqrt(np.mean(delta**2)))),currentMixSha256=inputs['sha256'],decodedAAC=measured,wholeCurrentAsrRequired=True,humanListening=False)
write(P/'mix-duck-existing-verification-v2.json',j)
code=(P/'review-audio-v1.py').read_text(encoding='utf-8').replace("STATE=OUT/f'{MODE}-asr-v1.json'", "assert MODE=='mix'\nSTATE=OUT/'mix-asr-v2.json'")
(P/'review-audio-v2.py').write_text(code,encoding='utf-8')
print(json.dumps(j,ensure_ascii=False))
