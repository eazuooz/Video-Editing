"""Resolve observed ASR seam artifacts with independent complete contexts."""
from pathlib import Path
import json,hashlib,subprocess,re
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/'production/local'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=rd(L/'whole-source-asr.json');words=[];repairs=[]
norm=lambda s:re.sub('[^가-힣a-z0-9]','',s.lower())
for i,w in enumerate(raw['words']):
 a,z=w['timestamp']
 if a is None or z is None:continue
 if words and a<words[-1]['timestamp'][0]-1:
  removed=[]
  while words and words[-1]['timestamp'][1]>a+.001:removed.append(words.pop())
  repairs.append({'kind':'backtracking-overlapping-ASR-window','sourceWordIndex':i,'restartAt':a,'removed':list(reversed(removed)),'resolution':'later complete context owns overlapping time; no source audio edited'})
 if words:
  prev=words[-1];pa,pz=prev['timestamp']
  if a<=pa+.03 and z>=pz-.03 and norm(w['text']).startswith(norm(prev['text'])):
   repairs.append({'kind':'overlapping-same-token-prefix','removed':words.pop(),'kept':w,'resolution':'same acoustic time, not a second utterance'})
 words.append(w)
q=dict(raw,text=' '.join(w['text'].strip() for w in words),words=words,derivedFromSha256=sha(L/'whole-source-asr.json'),seamRepairs=repairs,sourcePcmChanged=False)
wr(L/'whole-source-asr-aligned.json',q)
cache=L/'independent-source-contexts.json'
if not cache.exists():
 torch.set_num_threads(8);mid='openai/whisper-large-v3-turbo';m=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float32,attn_implementation='eager',local_files_only=True);p=AutoProcessor.from_pretrained(mid,local_files_only=True)
 asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
 contexts=[('opening-seam',14,43),('passive-balance',121,153),('rules-expression-seam',292,324),('notice-files-seam',385,442),('three-match-example',350,376)]
 rows=[]
 for key,a,z in contexts:
  dest=L/(key+'.wav')
  if not dest.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(a),'-i',str(L/'narration-source.wav'),'-t',str(z-a),'-c:a','pcm_f32le',str(dest)],check=True)
  print('Independent complete context',key,flush=True)
  result=asr(str(dest),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps=True)
  rows.append({'id':key,'sourceStart':a,'sourceEnd':z,'audioSha256':sha(dest),'text':result['text'],'segments':result['chunks'],'noExpectedPrompt':True})
  wr(L/'independent-source-contexts-progress.json',rows)
 wr(cache,{'sourceSha256':raw['audio_sha256'],'wholeAsrSha256':sha(L/'whole-source-asr.json'),'scope':'only ambiguous complete contexts; not a second whole-source pass','contexts':rows,'directReview':'pending'})
print('Seam derivative and independent contexts ready',flush=True)
