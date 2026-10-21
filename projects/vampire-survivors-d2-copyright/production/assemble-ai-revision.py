"""Replace only selected paragraphs; retain exact source samples and independent ASR evidence."""
from pathlib import Path
import json,hashlib,sys,importlib.util,math,shutil
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';B=P/'production/local';L=P/'production/local-ai-copyright-v2';V=P/'production/revision-ai-copyright-v2'
sys.path.insert(0,str(R/'qwen3-tts'))
from align_project_subtitles import align_characters,normalized
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def quiet_edge(audio,sr,lo,hi):
 # Choose the center of a genuinely quiet10ms interval between recognized
 # utterances. Never crossfade, trim or fade speech to conceal an edit.
 # Word-ASR may put adjacent words at the same boundary. Search a bounded
 #300ms neighborhood only then, still requiring an actually quiet interval.
 if hi-lo<.01:lo-=.3;hi+=.3
 lo=max(0,round(lo*sr));hi=min(len(audio),round(hi*sr));size=round(.01*sr)
 assert hi-lo>=size,('Insufficient paragraph join interval',lo/sr,hi/sr)
 sq=np.r_[0,np.cumsum(audio[lo:hi].astype(np.float64)**2)];power=(sq[size:]-sq[:-size])/size
 minimum=float(power.min());candidates=np.flatnonzero(power<=max(minimum*2,1e-8));i=int(candidates[np.argmin(np.abs(candidates-(hi-lo-size)/2))]);at=lo+i+size//2
 rms=10*np.log10(max(float(power[i]),1e-20));assert rms<-35,('Join is not speech safe',at/sr,rms)
 return at,{'sample':at,'seconds':at/sr,'rms10msDbfs':rms,'method':'quiet10ms interval between independent recognized paragraph speech; no speech fade/crossfade'}

def main():
 assert not (L/'narration-source.wav').exists(),'Do not replace an already assembled voice.'
 a,sr=sf.read(B/'narration-source.wav',dtype='float32');b,br=sf.read(L/'changed-source.wav',dtype='float32');assert sr==br==24000
 old=rd(B/'timing.json');oldq=rd(B/'whole-source-asr-aligned.json');newq=rd(L/'changed-source-asr-aligned.json');assert newq['audio_sha256']==sha(L/'changed-source.wav')
 revision=rd(V/'revision.json');changed=revision['changedParagraphs'];spoken=[x for s in rd(P/'script/narration.spoken-ko.json')['scenes'] for x in s['lines']]
 text=' '.join(spoken[i-1] for i in changed);starts,ends,coverage=align_characters(text,newq['words'],len(b)/sr);cursor=0;bounds={}
 for i in changed:
  n=len(normalized(spoken[i-1]));bounds[i]=(float(starts[cursor]),float(ends[cursor+n-1]));cursor+=n
 oldedges=[0];oldjoins=[]
 for p,q in zip(old['paragraphs'],old['paragraphs'][1:]):
  if (p['index'] in changed)!=(q['index'] in changed):
   at,row=quiet_edge(a,sr,p['end'],q['start']);oldjoins.append(dict(row,afterParagraph=p['index']))
  else:at=round((p['end']+q['start'])/2*sr) # no edit: adjacent slices rejoin bit-for-bit
  oldedges.append(at)
 oldedges.append(len(a));newedges=[0];newjoins=[]
 for i,j in zip(changed,changed[1:]):
  if j!=i+1:
   at,row=quiet_edge(b,sr,bounds[i][1],bounds[j][0]);newjoins.append(dict(row,afterChangedParagraph=i))
  else:at=round((bounds[i][1]+bounds[j][0])/2*sr) # continuous generated passage
  newedges.append(at)
 newedges.append(len(b));parts=[];rows=[];words=[];offset=0
 # Match the replacement batch's speech-active level to the retained source.
 def active_db(x,words):
  mask=np.zeros(len(x),dtype=bool)
  for w in words:
   lo,hi=w['timestamp']
   if lo is not None and hi is not None:mask[round(lo*sr):round(hi*sr)]=True
  return 10*np.log10(max(float(np.mean(x[mask].astype(np.float64)**2)),1e-20))
 olddb=active_db(a,oldq['words']);newdb=active_db(b,newq['words']);gain=olddb-newdb
 assert abs(gain)<6,(olddb,newdb,gain)
 b=b*10**(gain/20)
 for i in range(1,61):
  replacement=i in changed;src=b if replacement else a;q=newq if replacement else oldq
  k=changed.index(i) if replacement else i-1;edges=newedges if replacement else oldedges;lo,hi=edges[k:k+2];piece=src[lo:hi].copy();parts.append(piece)
  row={'paragraph':i,'replacement':replacement,'sourceFile':'changed-source.wav' if replacement else 'production/local/narration-source.wav','sourceStartSample':lo,'sourceEndSample':hi,'destinationStartSample':offset,'destinationEndSample':offset+len(piece),'gainDb':gain if replacement else 0,'sourceSpeechStart':bounds[i][0] if replacement else old['paragraphs'][i-1]['start'],'sourceSpeechEnd':bounds[i][1] if replacement else old['paragraphs'][i-1]['end'],'sha256FloatSamples':hashlib.sha256(piece.tobytes()).hexdigest()}
  for w in q['words']:
   x,z=w['timestamp']
   if x is None or z is None or x>=hi/sr or z<=lo/sr:continue
   ww=dict(w);ww['timestamp']=[max(0,x-lo/sr)+offset/sr,min((hi-lo)/sr,z-lo/sr)+offset/sr];words.append(ww)
  offset+=len(piece);rows.append(row)
 output=np.concatenate(parts);sf.write(L/'narration-source.wav',output,sr,subtype='FLOAT')
 for row in rows:
  if row['replacement']:continue
  assert np.array_equal(output[row['destinationStartSample']:row['destinationEndSample']],a[row['sourceStartSample']:row['sourceEndSample']])
 wr(L/'pcm-splice-map.json',{'status':'assembled-speech-safe-joins-and-exact-unchanged-samples','baselineSha256':sha(B/'narration-source.wav'),'changedBatchSha256':sha(L/'changed-source.wav'),'resultSha256':sha(L/'narration-source.wav'),'oldSpeechActiveDbfs':olddb,'changedSpeechActiveDbfs':newdb,'replacementOnlyGainDb':gain,'timeStretch':False,'crossfade':False,'speechFades':False,'oldJoinEvidence':oldjoins,'replacementJoinEvidence':newjoins,'paragraphs':rows,'humanListening':'pending'})
 recognized=' '.join(w['text'] for w in words)
 wr(L/'whole-source-asr-aligned.json',{'audio_sha256':sha(L/'narration-source.wav'),'text':recognized,'words':words,'scope':'complete independent recognition evidence assembled from identical retained PCM plus one changed-batch ASR; current entire assembled source additionally recognized once separately','coverageChanged':coverage,'humanListening':'pending'})
 shutil.copy2(L/'whole-source-asr-aligned.json',L/'whole-source-asr.json')
 # Existing subscript creates bilingual clauses and measured timings.
 spec=importlib.util.spec_from_file_location('audio',P/'production/prepare-audio.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.L=L;m.align()
 print(json.dumps({'duration':len(output)/sr,'replacementOnlyGainDb':gain,'unchangedParagraphs':49,'sourceOutputSha256':sha(L/'narration-source.wav')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
