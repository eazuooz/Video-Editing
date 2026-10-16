"""Full encoded mix read-back with29s bounded contexts; no expected-text prompt."""
from pathlib import Path
import sys,json,hashlib,difflib,gc
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';O=P/'production/local/reference-preserving-v2/edit/original-deletion-v4';Q=O/'bounded-asr';Q.mkdir(exist_ok=True);sys.path.insert(0,str(R/'qwen3-tts'))
from review_project_narration import normalize
audio=O/'encoded-audio.wav';samples,sr=sf.read(audio,dtype='float32');assert sr==16000;duration=len(samples)/sr;digest=hashlib.file_digest(audio.open('rb'),'sha256').hexdigest()
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(6);mid='openai/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float32,attn_implementation='eager').to('cpu');processor=AutoProcessor.from_pretrained(mid);asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
words=[];proof=[]
for i,coreStart in enumerate(np.arange(0,duration,25)):
 coreEnd=min(duration,coreStart+25);start=max(0,coreStart-2);end=min(duration,coreEnd+2);cache=Q/f'{i:02}.json';signature={'encodedAudioSha256':digest,'start':float(start),'end':float(end),'coreStart':float(coreStart),'coreEnd':float(coreEnd),'model':mid,'dtype':'float32','device':'cpu'}
 if cache.exists() and json.loads(cache.read_text(encoding='utf8')).get('signature')==signature:r=json.loads(cache.read_text(encoding='utf8'))
 else:
  raw=asr({'array':samples[round(start*sr):round(end*sr)],'sampling_rate':sr},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');r={'signature':signature,'text':raw['text'],'words':raw['chunks']};cache.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 for w in r['words']:
  a,b=w['timestamp'];a=start+(a or 0);b=end if b is None else start+b;midpoint=(a+b)/2
  if coreStart<=midpoint<coreEnd:words.append({'text':w['text'],'timestamp':[a,b]})
 proof.append({'cache':cache.relative_to(R).as_posix(),**signature});print(f'Checked {i+1}/22 bounded contexts, through{coreEnd:.1f}s',flush=True);gc.collect()
actual=''.join(w['text'] for w in words);report={'audioSha256':digest,'text':actual,'words':words,'scope':'Entire encoded mix, covered by25s cores with2s context on either side, maximum29s input; retained words chosen by timestamp midpoint. No supplied expected-text prompt.','contexts':proof,'humanListening':'pending'};(O/'final-mix-asr.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
script=json.loads((P/'script/original-deletion-v4/narration.tts.ko.json').read_text(encoding='utf8'));expected=' '.join(l for s in script['scenes'] for l in s['lines']);a,b=normalize(expected),normalize(actual);match=difflib.SequenceMatcher(None,a,b,autojunk=False);diff=[{'kind':op,'expected':a[i:j],'recognized':b[k:l]} for op,i,j,k,l in match.get_opcodes() if op!='equal'];(O/'final-mix-text-comparison.json').write_text(json.dumps({'similarity':match.ratio(),'expected':expected,'recognized':actual,'differences':diff,'reviewStatus':'pending complete direct text comparison'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Full bounded read-back completed; similarity',match.ratio())
