"""Decode both current masters and verify identical AAC, measured frames and BGM."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, math
import soundfile as sf
import numpy as np
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent; WORK=BASE/'final-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'; FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text(encoding='utf8')); now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
r=read(WORK/'render-result.json'); plan=read(WORK/'plan.json'); mix=read(WORK/'mix-settings.json')
assert r['done'] and r['exactFramePts']['allFramePtsExact']
state={'pid':os.getpid(),'status':'running','startedAt':now(),'commands':[],'automaticApproval':False}
def save():state['updatedAt']=now();(WORK/'technical-execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
def run(args,label,capture=False):
 log=WORK/(label+'.log')
 with log.open('w',encoding='utf8') as f:
  p=subprocess.Popen(args,stdout=subprocess.PIPE if capture else f,stderr=f); state['activeChild']=p.pid; save(); stdout=p.communicate()[0]; code=p.returncode
 state['commands'].append({'command':args,'pid':p.pid,'exitCode':code,'log':log.relative_to(ROOT).as_posix()});state['activeChild']=None;save();assert code==0,(label,code)
 return stdout.decode('utf8') if capture else log.read_text(encoding='utf8')
save(); videos=[]
for kind in ['clean','captioned']:
 file=ROOT/r[kind];assert sha(file)==r[kind+'Sha256']
 probe=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(file)],kind+'-probe',True));v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1','60/1',32100)
 assert abs(float(v['duration'])-plan['finalFrames']/60)<.000001 and a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
 pts=json.loads(run([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(file)],kind+'-frame-pts',True))['frames']
 assert v['time_base']=='1/90000' and len(pts)==32100
 for n,f in enumerate(pts):assert int(f['best_effort_timestamp'])==n*1500,(kind,n,f)
 errors=run([FF,'-v','error','-threads','2','-i',str(file),'-map','0:v:0','-map','0:a:0','-f','null','-'],kind+'-full-decode'); assert not errors.strip(),errors
 out=WORK/(kind+'-audio-check.aac');assert not out.exists();run([FF,'-v','error','-i',str(file),'-map','0:a:0','-c:a','copy','-f','adts',str(out)],kind+'-audio-extract')
 videos.append({'kind':kind,'path':r[kind],'sha256':sha(file),'bytes':file.stat().st_size,'probe':probe,'fullDecodeExitCode':0,'fullDecodeErrorCount':0,'aacSha256':sha(out)})
assert videos[0]['aacSha256']==videos[1]['aacSha256']
bgm,rate=sf.read(WORK/'bgm-before-ducking.wav',dtype='float32',always_2d=True); assert rate==48000 and len(bgm)==32100*800 and sha(WORK/'bgm-before-ducking.wav')==mix['bgmSha256']
intervals=[{'id':'branding','startFrame':0,'frames':120}]+plan['scenes']+[{'id':'membership','startFrame':31500,'frames':600}]
levels=[]
for s in intervals:
 x=bgm[s['startFrame']*800:(s['startFrame']+s['frames'])*800];rms=float(np.sqrt(np.mean(x.astype('float64')**2)));assert rms>0
 levels.append({'id':s['id'],'rmsDbFS':20*math.log10(rms),'nonzeroSamples':int(np.count_nonzero(x))})
voice,rate=sf.read(WORK/'voice-normalized.wav',dtype='int16',always_2d=True);assert not np.count_nonzero(voice[:96000])
out={'status':'technical-measurements-passed-awaiting-direct-content-gates','observedAt':now(),'frames':32100,'seconds':32100/60,'videos':videos,'identicalAAC':True,'mixSha256':mix['wavSha256'],'mixAACSha256':mix['aacSha256'],'loudness':mix['finalAacMeasurement'],'bgmContinuousAllScenes':True,'bgmIntervals':levels,'brandingVoiceSilent':True,'humanFullListening':'pending','publicRights':'pending','originalNimbusIdentity':'pending','finalApproved':False}
(WORK/'technical-measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');state.update(status='finished',exitCode=0,endedAt=now());save();print(json.dumps({'frames':32100,'twoDecodesPassed':True,'identicalAAC':True,'bgmContinuous':True}))
