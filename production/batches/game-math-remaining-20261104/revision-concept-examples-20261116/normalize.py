"""CPU-only preparation of completed takes, without claiming stale takes are final."""
import sys,math,subprocess,argparse
from prepare import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true');args=ap.parse_args()
 import numpy as np,soundfile as sf
 sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as q
 q.np=np;q.sf=sf
 stale={'M21-02','M23-01','M26-02','M28-01','M28-02','M29-01'};items=[];texts=read(HERE/'local/voice/take-texts.json') if (HERE/'local/voice/take-texts.json').exists() else {}
 for e in read(HERE/'plan.json')['episodes']:
  for s in e['inserts']:
   raw=HERE/'local/voice/raw'/(s['key']+'.wav');x,sr=sf.read(raw,dtype='float32');original=x.copy();n=round(sr*.02)
   rms=np.sqrt(np.array([np.mean(x[i:i+n]**2) for i in range(0,len(x),n)]));active=np.flatnonzero(rms>max(.0005,float(rms.max())*.025));a=max(0,int(active[0]*n-.10*sr));z=min(len(x),int((active[-1]+1)*n+.22*sr));x=x[a:z]
   rms=np.sqrt(np.array([np.mean(x[i:i+n]**2) for i in range(0,len(x),n)]));speech=rms[rms>rms.max()*.0562];median=float(20*np.log10(np.median(speech)+1e-12));gain=min(10,max(-10,-22-median));x*=10**(gain/20);x=np.pad(x,(round(.12*sr),round(.18*sr)))
   out=HERE/'local/voice'/(s['key']+'.wav');stage=out.with_suffix('.float.wav');sf.write(stage,x,sr,subtype='FLOAT')
   subprocess.run([FF,'-v','error','-nostdin','-y','-i',str(stage),'-af',f'aresample=192000,alimiter=limit=0.78:level=false:latency=true,aresample={sr}','-c:a','pcm_s16le',str(out)],check=True,creationflags=subprocess.CREATE_NO_WINDOW);stage.unlink();x,sr=sf.read(out,dtype='float32')
   tail=float(q._tail_ratio(original,sr));decay=float(q._tail_decay_ms(original,sr));legacy=bool(q._passes_quality(tail,decay))
   def tail_db(ms):return float(20*np.log10(np.sqrt(np.mean(original[-round(sr*ms/1000):]**2))+1e-12))
   # A50ms/whole-paragraph ratio can flag a fully finished short sentence:
   # the vowel is in that window although the final10ms are already silent.
   # Only admit that alternative with a long measured decay AND a quiet actual
   # endpoint. Final ASR beginning/ending content review remains mandatory.
   acoustic=bool(decay>=120 and tail_db(10)<=-70 and tail_db(20)<=-45 and abs(float(original[-1]))<.0001)
   ok=legacy or acoustic
   record=texts.get(s['key'],{});current=s['key'] not in stale or (record.get('sha256')==sha(raw) and record.get('text')==' '.join(s['ko']))
   if args.final:assert current,('stale source take',s['key'])
   items.append(dict(key=s['key'],file=str(out),sha256=sha(out),rawSha256=sha(raw),seconds=len(x)/sr,sampleRate=sr,sourceText=' '.join(s['ko']) if current else 'STALE TAKE - regenerate against selected text',expectedText=' '.join(s['ko']),contentCurrent=current,qualityPassed=bool(ok and current),legacyEndingHeuristicPassed=legacy,measuredLongDecayAndSilentEndpoint=acoustic,rawTailRatio=tail,rawTailDecayMs=decay if math.isfinite(decay) else None,tail10msDbfs=tail_db(10),tail20msDbfs=tail_db(20),finalSample=float(original[-1]),gainDb=gain,peakDbfs=float(20*np.log10(abs(x).max()+1e-12)),originalLectureVoiceUntouched=True,humanListening=False,generationDevice=record.get('device','cuda-initial-take')))
 save(HERE/'voice.json',dict(status='new-bridges-normalized-awaiting-final-ASR' if args.final else 'provisional; flagged-takes-await-repair',items=items,paidApi=False))
 print('Prepared completed takes on CPU. Ready:',[e['id'] for e in read(HERE/'plan.json')['episodes'] if all(next(v for v in items if v['key']==s['key'])['qualityPassed'] for s in e['inserts'])])
if __name__=='__main__':main()
