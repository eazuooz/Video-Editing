from pathlib import Path
import json,math,hashlib,subprocess
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parents[2]; L=P/'production/local'; N=L/'narration'
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args):return subprocess.run([str(x) for x in args],capture_output=True,text=True,check=True)
def timeline(require_all=True):
 rows=json.loads((P/'script/content.json').read_text('utf-8'))['paragraphs'];out=[];start=2
 for i,row in enumerate(rows):
  f=N/'chunks'/f"{row['id']}-scene.wav"
  if not f.exists():
   if require_all:raise FileNotFoundError(f)
   break
  info=sf.info(f);gap=.28 if i<len(rows)-1 else 0
  frames=math.ceil((info.duration+gap)*60)
  out.append({'id':row['id'],'start':start,'speechEnd':start+info.duration,'duration':frames/60,'frames':frames,'source':str(f),'sourceSha256':sha(f),'sourceDuration':info.duration})
  start+=frames/60
 result={'fps':60,'intro':2,'outro':10,'scenes':out,'duration':start+10,'frames':round((start+10)*60)}
 save(L/'timeline.json',result);return result
def build():
 j=timeline();parts=[];report=[];sr=24000
 parts.append(np.zeros(2*sr,dtype=np.float32))
 for r in j['scenes']:
  audio,sr0=sf.read(r['source'],dtype='float32');assert sr0==sr
  if audio.ndim>1:audio=audio.mean(axis=1)
  n=round(sr*.05);rms=np.array([np.sqrt(np.mean(audio[k:k+n]**2)+1e-12) for k in range(0,len(audio)-n,n)])
  db=20*np.log10(np.maximum(rms,1e-8));active=db[db>db.max()-25];median=float(np.median(active));gain=float(np.clip(-22-median,-12,12))
  adj=audio*(10**(gain/20));peak=float(abs(adj).max())
  fade=round(sr*.006);adj[:fade]*=np.linspace(0,1,fade);adj[-fade:]*=np.linspace(1,0,fade)
  pad=round(r['frames']/60*sr)-len(adj);assert pad>=0
  parts.extend([adj,np.zeros(pad,dtype=np.float32)])
  report.append({'id':r['id'],'sourceSha256':r['sourceSha256'],'activeMedianBeforeDbfs':median,'gainDb':gain,'activeMedianAfterDbfs':median+gain,'peak':peak,'postTakeSilenceSeconds':pad/sr,'rawSamplesPreservedExcept6msEdgeFadeAndConstantGain':True})
 parts.append(np.zeros(10*sr,dtype=np.float32));a=np.concatenate(parts)
 # Float intermediate preserves peaks above0dBFS without integer clipping.
 raw=L/'narration-aligned.wav';sf.write(raw,a,sr,subtype='FLOAT');save(L/'line-levels.json',report)
 measure=run(['ffmpeg','-hide_banner','-i',raw,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
 meter=json.loads(measure.stderr[measure.stderr.rfind('{'):measure.stderr.rfind('}')+1]);g=-16-float(meter['input_i'])-10*math.log10(2)
 mixed=L/'final-mix.wav';limit=10**(-2.6/20)
 limiter=f'alimiter=limit={limit}:attack=5:release=80:level=false:latency=true'
 # One common gain plus peak protection, never time-varying per-paragraph AGC.
 ff=run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,'-af',f'pan=stereo|c0=c0|c1=c0,volume={g}dB,{limiter}','-ar','48000','-ac','2','-c:a','pcm_s24le',mixed])
 final=run(['ffmpeg','-hide_banner','-i',mixed,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
 fm=json.loads(final.stderr[final.stderr.rfind('{'):final.stderr.rfind('}')+1])
 # Stereo conversion and peak protection make gain/level slightly nonlinear.
 # Re-measure the changed common gain rather than loosening the delivery target.
 iterations=[]
 for attempt in range(4):
  iterations.append({'gainDb':g,'measured':fm})
  save(L/'mix-normalization-iterations.json',iterations)
  if abs(float(fm['input_i'])+16)<=.15:break
  g+=-16-float(fm['input_i'])
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,'-af',f'pan=stereo|c0=c0|c1=c0,volume={g}dB,{limiter}','-ar','48000','-ac','2','-c:a','pcm_s24le',mixed])
  final=run(['ffmpeg','-hide_banner','-i',mixed,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);fm=json.loads(final.stderr[final.stderr.rfind('{'):final.stderr.rfind('}')+1])
 assert abs(float(fm['input_i'])+16)<.3,fm;assert float(fm['input_tp'])<-1.2,fm
 post_trim=0
 for attempt in range(3):
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',mixed,'-c:a','aac','-b:a','192k',L/'final-mix.m4a'])
  encoded=run(['ffmpeg','-hide_banner','-i',L/'final-mix.m4a','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
  em=json.loads(encoded.stderr[encoded.stderr.rfind('{'):encoded.stderr.rfind('}')+1])
  if float(em['input_tp'])<=-1.5:break
  post_trim+=float(em['input_tp'])+1.6
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,'-af',f'pan=stereo|c0=c0|c1=c0,volume={g}dB,{limiter},volume={-post_trim}dB','-ar','48000','-ac','2','-c:a','pcm_s24le',mixed])
 assert float(em['input_tp'])<=-1.5
 final=run(['ffmpeg','-hide_banner','-i',mixed,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);fm=json.loads(final.stderr[final.stderr.rfind('{'):final.stderr.rfind('}')+1])
 save(P/'production/audio-qa.json',{'source':'one full paragraph per take','duration':len(a)/sr,'narrationSha256':sha(raw),'mixSha256':sha(mixed),'globalGainDb':g,'codecHeadroomTrimDb':post_trim,'peakProtection':{'filter':limiter,'sampleFractionAboveThreshold':float(np.mean(abs(a)*10**(g/20)>limit)),'purpose':'Explicit unity-gain L/R duplication before global peak protection; no automatic mono-to-stereo attenuation after limiting. No per-scene ducking/AGC. Float intermediate prevents clipping.'},'measuredNarration':meter,'measuredFinal':fm,'measuredEncoded':em,'lineLevels':report,'bgm':'none, lecture default','naturalSpeechSpeed':'unaltered','wholeHumanListening':'pending','asr':'pending current narration and current mix'})
 print('Built audio',len(a)/sr,'seconds',fm)
if __name__=='__main__':build()
