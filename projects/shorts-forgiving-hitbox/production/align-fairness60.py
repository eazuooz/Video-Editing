"""Inspect real word times and quiet edit candidates before locking the60s timeline."""
from pathlib import Path
import json,re,sys,hashlib
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local/fairness-60s'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def norm(s):return re.sub(r'[^가-힣a-z0-9]','',s.lower()).replace('허트박스에요','허트박스예요')
def map_words(asr,lines):
 words=asr['chunks'];actual=''.join(norm(w['text']) for w in words);expected=''.join(norm(s) for s in lines)
 assert actual==expected,('Resolve ASR differences before timing',actual,expected)
 spans=[];pos=0
 for w in words:
  n=len(norm(w['text']));spans.append((pos,pos+n,w['timestamp']));pos+=n
 def at(c,edge):
  for a,b,(s,e) in spans:
   if (a<=c<b) if edge=='start' else (a<c<=b):return s+(e-s)*(c-a)/max(1,b-a)
  return spans[-1][2][1]
 result=[];pos=0
 for i,line in enumerate(lines):
  n=len(norm(line));result.append(dict(index=i,text=line,start=at(pos,'start'),end=at(pos+n,'end')));pos+=n
 return result
def inspect():
 src=R/'shared/output/narration/shorts-forgiving-hitbox/fairness60-additions-v1/fairness60-additions-v1.wav';key=hashlib.sha256(src.read_bytes()).hexdigest()[:12];asr=read(L/f'asr-additions-{key}.json');lines=read(P/'script/fairness-60s/additions.ko.json')['scenes'][0]['lines'];rows=map_words(asr,lines);wav,sr=sf.read(src);wav=wav.mean(axis=1) if wav.ndim==2 else wav;cuts=[]
 for after in [2,3,5]:
  left,right=rows[after]['end'],rows[after+1]['start'];target=(left+right)/2;candidates=[]
  for t in np.arange(max(0,left-.12),min(len(wav)/sr,right+.08),.005):
   v=wav[max(0,round((t-.025)*sr)):round((t+.025)*sr)];rms=float(np.sqrt(np.mean(v*v)));candidates.append((rms,abs(t-target),float(t)))
  quiet=[x for x in candidates if x[0]<.004];best=min(quiet,key=lambda x:x[1]) if quiet else min(candidates);cuts.append(dict(afterLine=after,asrEnd=left,nextStart=right,candidate=round(best[2],4),windowRms=best[0],quiet=best[0]<.004))
 out=dict(source=str(src.relative_to(R)),sourceSha256=hashlib.sha256(src.read_bytes()).hexdigest(),seconds=len(wav)/sr,lines=rows,candidateCuts=cuts,status='Inspect candidates and waveform ranges before locking edits')
 save(L/'additions-timing-inspection.json',out);print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':globals()[sys.argv[1]]()
