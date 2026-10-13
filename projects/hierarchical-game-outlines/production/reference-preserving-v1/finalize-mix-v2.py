"""Correct measured AAC overshoot using the existing mixed PCM, without remaking layers."""
from pathlib import Path
import os,subprocess,json,hashlib,datetime,math,psutil
P=Path(__file__).resolve().parent;ROOT=P.parents[3];FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
STATE=P/'mix-finalization-v2.json';assert not STATE.exists()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write():STATE.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(args):
 r=subprocess.run([FF,'-hide_banner','-nostdin','-n',*args],capture_output=True,creationflags=0x08000000)
 assert r.returncode==0,r.stderr.decode('utf-8','replace')[-2000:]
 return r.stdout,r.stderr.decode('utf-8','replace')
def measure(p):
 _,e=run(['-i',str(p),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);return json.loads(e[e.rfind('{'):e.rfind('}')+1])
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
s=dict(status='running',startedAt=now(),worker=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,exitCode=None,sourceWavSha256=sha(P/'current-mix-v1.wav'),failurePreserved='mix-execution-v2.json',fullLayerMixRepeated=False)
assert s['cpu']<85 and s['availableMemoryBytes']>8e9;write()
before=measure(P/'current-mix-v1.m4a');s['heldAAC']=before;gain=min(0,-2.0-float(before['input_tp']));s['correctionGainDb']=gain;write()
out=P/'current-mix-v2.m4a';run(['-threads','2','-i',str(P/'current-mix-v1.wav'),'-af',f'volume={gain}dB','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',str(out)])
after=measure(out);s['currentAAC']=after;s['sha256']=sha(out);write();assert float(after['input_tp'])<=-1.5,after
import numpy as np,soundfile as sf
b,_=run(['-i',str(out),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']);audio=np.frombuffer(b,dtype='<f4').reshape(-1,2)
plan=json.loads((P/'final-timeline-v1.json').read_text(encoding='utf-8'));d=P/'mix-review-v2-local';d.mkdir(exist_ok=False);rows=[]
for scene in plan['scenes']:
 a=scene['startFrame']*800;b=(scene['startFrame']+scene['frames'])*800;path=d/f'{scene["id"]}.wav';sf.write(path,audio[a:b],48000,subtype='PCM_16');rows.append(dict(id=scene['id'],path=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
inputs=dict(audio=out.relative_to(ROOT).as_posix(),sha256=sha(out),timelineSha256=sha(P/'final-timeline-v1.json'),scenes=rows)
(P/'mix-final-inputs-v1.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s.update(status='complete-pending-current-mixed-ASR',exitCode=0,finishedAt=now());write();print(json.dumps(s,ensure_ascii=False))
