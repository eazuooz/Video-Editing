from pathlib import Path
import json,math,hashlib,subprocess
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parents[1]; L=P/'production/local'; N=L/'narration'
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
  adj=audio*(10**(gain/20));peak=float(abs(adj).max());assert peak<.99,(r['id'],peak)
  fade=round(sr*.006);adj[:fade]*=np.linspace(0,1,fade);adj[-fade:]*=np.linspace(1,0,fade)
  pad=round(r['frames']/60*sr)-len(adj);assert pad>=0
  parts.extend([adj,np.zeros(pad,dtype=np.float32)])
  report.append({'id':r['id'],'sourceSha256':r['sourceSha256'],'activeMedianBeforeDbfs':median,'gainDb':gain,'activeMedianAfterDbfs':median+gain,'peak':peak,'postTakeSilenceSeconds':pad/sr,'rawSamplesPreservedExcept6msEdgeFadeAndConstantGain':True})
 parts.append(np.zeros(10*sr,dtype=np.float32));a=np.concatenate(parts)
 raw=L/'narration-aligned.wav';sf.write(raw,a,sr,subtype='PCM_24');save(L/'line-levels.json',report)
 measure=run(['ffmpeg','-hide_banner','-i',raw,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
 meter=json.loads(measure.stderr[measure.stderr.rfind('{'):measure.stderr.rfind('}')+1]);g=-16-float(meter['input_i'])
 mixed=L/'final-mix.wav';ff=run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,'-af',f'volume={g}dB','-ar','48000','-c:a','pcm_s24le',mixed])
 final=run(['ffmpeg','-hide_banner','-i',mixed,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
 fm=json.loads(final.stderr[final.stderr.rfind('{'):final.stderr.rfind('}')+1]);assert abs(float(fm['input_i'])+16)<.2;assert float(fm['input_tp'])<-1
 run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',mixed,'-c:a','aac','-b:a','192k',L/'final-mix.m4a'])
 save(P/'production/audio-qa.json',{'source':'one full paragraph per take','duration':len(a)/sr,'narrationSha256':sha(raw),'mixSha256':sha(mixed),'globalGainDb':g,'measuredNarration':meter,'measuredFinal':fm,'lineLevels':report,'bgm':'none, lecture default','naturalSpeechSpeed':'unaltered','wholeHumanListening':'pending','asr':'pending current narration and current mix'})
 print('Built audio',len(a)/sr,'seconds',fm)
if __name__=='__main__':build()
