"""V8 unchanged paragraph PCM -> one global voice gain -> standard game mix.

No added BGM, voice ducking, time stretch, paragraph renormalization or fades.
"""
from pathlib import Path
import importlib.util,json,math,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_mix_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
D=c.O/'mix';D.mkdir(parents=True,exist_ok=True)
def run(args,name):
 with (D/(name+'.log')).open('wb')as f:r=subprocess.run(['ffmpeg','-hide_banner','-loglevel','info','-nostdin','-n',*map(str,args)],cwd=c.R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 assert r.returncode==0,(D/(name+'.log')).read_text(encoding='utf8',errors='replace')[-2000:]
def loudness(p,name):
 cmd=['ffmpeg','-hide_banner','-nostdin','-threads','2','-filter_threads','2','-i',str(p),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json','-f','null','-']
 r=subprocess.run(cmd,capture_output=True);assert r.returncode==0;s=r.stderr.decode(errors='replace');(D/(name+'.log')).write_text(s,encoding='utf8');return json.loads(s[s.rfind('{'):s.rfind('}')+1])
def init(p,samples):
 with sf.SoundFile(p,'w',samplerate=48000,channels=2,subtype='FLOAT')as f:
  z=np.zeros((480000,2),np.float32)
  while f.tell()<samples:f.write(z[:min(len(z),samples-f.tell())])
def scale(a,b,gain):
 with sf.SoundFile(a)as src,sf.SoundFile(b,'w',samplerate=48000,channels=2,subtype='FLOAT')as dst:
  for x in src.blocks(blocksize=480000,dtype='float32',always_2d=True):dst.write(x*np.float32(10**(gain/20)))
def decode(src,start,frames,out,name):
 n=frames*800;run(['-threads','2','-ss',start,'-i',src,'-map','0:a:0','-vn','-af',f'aresample=48000,apad=whole_len={n},atrim=end_sample={n}','-ac','2','-c:a','pcm_f32le',out],name)
 x,sr=sf.read(out,dtype='float32',always_2d=True);assert sr==48000 and len(x)==n;return x
def main():
 c.authorized();t=c.read(H/'timeline.json');source=c.read(c.O/'audio/tts-current.json');assert len(source['scenes'])==13
 visual=c.read(H/'edit-plan.json');n=t['totalFrames']*800
 assert not (D/'final-mix.m4a').exists(),'Preserve completed mix; reuse its exact receipt or inspect before changes.'
 raw=D/'narration-placed-48k.wav';init(raw,n);rows=[]
 with sf.SoundFile(raw,'r+')as f:
  for s in t['scenes']:
   p=c.R/s['rawVoiceFile'];assert c.sha(p)==s['rawVoiceSha256'];x,sr=sf.read(p,dtype='float32');assert sr==24000 and x.ndim==1
   y=resample_poly(x,2,1);f.seek(s['startFrame']*800);f.write(np.repeat(y[:,None],2,axis=1));rows.append(dict(scene=s['id'],sourceSha256=s['rawVoiceSha256'],samples24k=len(x),startSample48k=s['startFrame']*800,sourceSpeed=1))
 stats=loudness(raw,'narration-placed-measurement');gain=min(-16-float(stats['input_i']),-2.3-float(stats['input_tp']));voice=D/'narration-normalized.wav';scale(raw,voice,gain)
 game=D/'game-normalized.wav';brand=D/'branding-original.wav';init(game,n);init(brand,n);games=[]
 with sf.SoundFile(game,'r+')as f:
  for cut in visual['liveGameCuts']:
   frames=cut['endFrameExclusive']-cut['startFrame'];src=c.R/cut['file'];assert cut['sourceAudioAllowed'] and c.sha(src)==cut['sourceSha256'];out=D/(cut['id']+'-original.wav');x=decode(src,cut['sourceStartFrame']/60,frames,out,cut['id']+'-decode');m=loudness(out,cut['id']+'-measurement');g=-23-float(m['input_i']);assert abs(g)<20
   x*=np.float32(10**(g/20));a=min(5760,len(x)//2);b=min(14400,len(x)//2);x[:a]*=np.linspace(0,1,a,dtype=np.float32)[:,None];x[-b:]*=np.linspace(1,0,b,dtype=np.float32)[:,None];f.seek(cut['startFrame']*800);f.write(x);games.append(dict(cut,sourceAudioTargetLufs=-23,gainDb=g,measurement=m,sourceSpeed=1))
 with sf.SoundFile(brand,'r+')as f:
  for name,item in t['branding'].items():
   src=c.R/item['file'];streams=[x for x in c.probe(src)['streams']if x['codec_type']=='audio']
   if not streams:continue
   x=decode(src,0,item['frames'],D/(name+'-original.wav'),name+'-decode');f.seek(item.get('startFrame',0)*800);f.write(x)
 duck=D/'game-ducked.wav';pre=D/'premix.wav'
 graph=f'[0:a]asplit=2[v][ctrl];[1:a][ctrl]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280:makeup=1,apad=whole_len={n},atrim=end_sample={n},asplit=2[go][gm];[v][gm][2:a]amix=inputs=3:normalize=0:duration=longest:dropout_transition=0[m]'
 run(['-threads','2','-filter_complex_threads','2','-i',voice,'-i',game,'-i',brand,'-filter_complex',graph,'-map','[go]','-c:a','pcm_f32le',duck,'-map','[m]','-c:a','pcm_f32le',pre],'game-only-duck-and-sum')
 pm=loudness(pre,'premix-measurement');pg=min(0,-2.3-float(pm['input_tp']));final=D/'final-mix.wav';scale(pre,final,pg)
 stems=[]
 for name,p in [('narration',voice),('game',duck),('branding',brand)]:
  dst=D/(name+'-final-stem.wav');scale(p,dst,pg);stems.append(dict(role=name,file=c.rel(dst),sha256=c.sha(dst)))
 aac=D/'final-mix.m4a';run(['-threads','2','-i',final,'-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',aac],'aac-encode');encoded=loudness(aac,'encoded-measurement');assert float(encoded['input_tp'])<=-1.5
 receipt=dict(revision='orientation-matrix-v8',inputs=dict(timelineSha256=c.sha(H/'timeline.json'),ttsCurrentSha256=c.sha(c.O/'audio/tts-current.json'),liveGameCuts=visual['liveGameCuts'],implementationSha256=c.sha(Path(__file__))),sourcePlacements=rows,sourceLineLevelPolicy='line-level-takes-v1 already applied; no additional paragraph gains',voiceGlobalGainDb=gain,voiceMeasurement=stats,programGlobalGainDb=pg,premixMeasurement=pm,encodedMeasurement=encoded,addedBgm=False,voiceDucking=False,voiceFades=False,timeStretch=False,amixNormalize=0,gameDucking=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280),games=games,stems=stems,outputs=[dict(file=c.rel(x),sha256=c.sha(x))for x in [raw,voice,game,brand,duck,final,aac]],audioMix=c.rel(final),encodedAudio=c.rel(aac),sampleRate=48000,channels=2,totalSamples=n,frames=t['totalFrames'],finalAsr='pending one current encoded batch',humanListening='pending')
 c.save(D/'mix-report.json',receipt);print(json.dumps(dict(seconds=t['duration'],encodedMeasurement=encoded,voiceGlobalGainDb=gain,programGlobalGainDb=pg)))
if __name__=='__main__':main()
