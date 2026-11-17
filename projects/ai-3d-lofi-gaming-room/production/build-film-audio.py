"""Frame-aligned, unsped narration plus the actual licensed room music."""
from pathlib import Path
import json,math,hashlib,subprocess
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v1';N=L/'narration/chunks'
def run(a):return subprocess.run(list(map(str,a)),capture_output=True,text=True,check=True)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
rows=json.loads((P/'script/narration.ko.json').read_text('utf-8'))['scenes'];time=2;parts=[np.zeros(48000,dtype=np.float32)];timeline=[];levels=[]
for i,r in enumerate(rows):
 f=N/(r['id']+'-scene.wav');a,sr=sf.read(f,dtype='float32');assert sr==24000
 if a.ndim>1:a=a.mean(axis=1)
 dur=len(a)/sr;frames=math.ceil((dur+(.28 if i<len(rows)-1 else 0))*60)
 win=1200;v=np.array([np.sqrt(np.mean(a[j:j+win]**2)+1e-12) for j in range(0,len(a)-win,win)])
 db=20*np.log10(np.maximum(v,1e-8));active=db[db>db.max()-25];median=float(np.median(active));gain=float(np.clip(-22-median,-12,12));a=a*10**(gain/20)
 n=144;a[:n]*=np.linspace(0,1,n);a[-n:]*=np.linspace(1,0,n)
 pad=round(frames/60*sr)-len(a);parts.extend([a,np.zeros(pad,dtype=np.float32)])
 timeline.append({'id':r['id'],'title':r['title'],'start':time,'speechEnd':time+dur,'duration':frames/60,'frames':frames,'source':str(f),'sourceSha256':sha(f),'sourceDuration':dur})
 levels.append({'id':r['id'],'activeMedianDbfs':median,'gainDb':gain,'postTakeSilenceSeconds':pad/sr});time+=frames/60
parts.append(np.zeros(10*24000,dtype=np.float32));raw=L/'narration-aligned.wav';sf.write(raw,np.concatenate(parts),24000,subtype='FLOAT')
total=time+10;tm={'fps':60,'intro':2,'outro':10,'duration':total,'frames':round(total*60),'scenes':timeline};(L/'timeline.json').write_text(json.dumps(tm,ensure_ascii=False,indent=2)+'\n','utf-8')
music=R/'sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3';mix=L/'final-mix.wav';fire=R/'unity/LofiGamingRoomWeb/Assets/LofiRoom/Audio/fireplace.ogg'
fireStart=next(s['start'] for s in timeline if s['id']=='21');fireEnd=next(s['speechEnd'] for s in timeline if s['id']=='22');fireDuration=fireEnd-fireStart
filt=f'[0:a]loudnorm=I=-16:TP=-2:LRA=11,aformat=channel_layouts=stereo[n];[1:a]atrim=duration={total},asetpts=PTS-STARTPTS,loudnorm=I=-31:TP=-6:LRA=6,afade=t=in:d=1,afade=t=out:st={total-2}:d=2[m];[2:a]atrim=duration={fireDuration},asetpts=PTS-STARTPTS,loudnorm=I=-32:TP=-6:LRA=6,afade=t=in:d=0.8,afade=t=out:st={fireDuration-1}:d=1,adelay={round(fireStart*1000)}:all=1[f];[n][m][f]amix=inputs=3:normalize=0,alimiter=limit=0.79:level=false:latency=true[a]'
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,'-stream_loop','-1','-i',music,'-stream_loop','-1','-i',fire,'-filter_complex',filt,'-map','[a]','-t',str(total),'-ar','48000','-ac','2','-c:a','pcm_s24le',mix])
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',mix,'-c:a','aac','-b:a','192k',L/'final-mix.m4a'])
def meter(p):
 s=run(['ffmpeg','-hide_banner','-i',p,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr;return json.loads(s[s.rfind('{'):s.rfind('}')+1])
qa={'duration':total,'narrationSha256':sha(raw),'mixSha256':sha(mix),'measuredFinal':meter(mix),'measuredEncoded':meter(L/'final-mix.m4a'),'lineLevels':levels,'bgm':'Morning Coffee / HoliznaCC0 / CC0, same asset used by game, -31 LUFS bed; explicitly requested LOFI scope','fire':{'sourceSha256':sha(fire),'creator':'PaGDev','license':'CC0','start':fireStart,'end':fireEnd,'targetLufs':-32},'speechSpeed':'unaltered','wholeHumanListening':'pending','asr':'pending'}
assert float(qa['measuredEncoded']['input_tp'])<=-1.5,qa['measuredEncoded']
(P/'production/full-video-audio-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8');print('Audio timeline',total,'seconds')
