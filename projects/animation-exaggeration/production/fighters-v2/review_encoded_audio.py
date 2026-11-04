from pathlib import Path
import os,json,subprocess,hashlib,difflib,re
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import audio_pipeline as ap,caption_pipeline as cp
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v2'
def main():
 ap.require_authorized('recognize');aac=L/'edit/pair-audio.m4a';out=L/'qa/audio';out.mkdir(parents=True,exist_ok=True)
 source=out/'encoded.wav';subprocess.run(['ffmpeg','-y','-v','error','-i',str(aac),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(source)],check=True)
 import soundfile as sf,numpy as np,torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 from huggingface_hub import try_to_load_from_cache
 target=out/'full-encoded-asr.json';digest=ap.sha(aac)
 if target.exists() and ap.read(target)['aacSha256']==digest:result=ap.read(target)['result']
 else:
  with ap.batch_asr_lease('cpu'):
   torch.set_num_threads(4);model=Path(try_to_load_from_cache('openai/whisper-large-v3-turbo','config.json')).parent
   m=AutoModelForSpeechSeq2Seq.from_pretrained(str(model),dtype=torch.float32,attn_implementation='sdpa',local_files_only=True);p=AutoProcessor.from_pretrained(str(model),local_files_only=True)
   pipe=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,device=-1)
   y,sr=sf.read(source,dtype='float32');result=pipe({'array':y,'sampling_rate':sr},chunk_length_s=25,stride_length_s=3,generate_kwargs={'language':'korean','task':'transcribe','num_beams':1},return_timestamps='word')
   ap.save(target,{'aacSha256':digest,'sourceWavSha256':ap.sha(source),'model':str(model),'expectedPrompt':None,'result':result,'actualListeningPerformed':False})
 script=(H.parents[1]/'script/fighters-v2/narration.spoken-ko.txt').read_text(encoding='utf-8');paras=script.strip().split('\n\n')
 aliases={'킹오프파이터스15':'킹오브파이터즈피프틴','킹오브파이터즈15':'킹오브파이터즈피프틴','쏠도':'솔도','릭':'리그','오버슛':'오버슈트'}
 expected=cp.normalized(script,aliases);actual=cp.normalized(result['text'],aliases);matcher=difflib.SequenceMatcher(None,expected,actual,autojunk=False)
 matched=set();misses=[]
 for tag,a,b,c,d in matcher.get_opcodes():
  if tag=='equal':matched.update(range(a,b))
  elif tag in ('replace','delete'):misses.append({'expected':expected[a:b],'heardByAsr':actual[c:d],'start':a,'end':b})
 n=0;rows=[]
 for i,p in enumerate(paras,1):
  size=len(cp.normalized(p,aliases));coverage=len(matched.intersection(range(n,n+size)))/size
  rows.append({'paragraph':i,'coverage':coverage,'unexpected':[x for x in misses if n<=x['start']<n+size]});n+=size
 ap.save(H/'final-audio-asr-review.json',{'aac':ap.artifact(aac),'recognition':ap.artifact(target),'matchedCharacterCoverage':len(matched)/len(expected),'paragraphs':rows,'actualListeningPerformed':False,'note':'Unprompted full encoded-audio text comparison; minor Korean spacing/phonetic aliases are alignment only, never replacements of recorded speech.'})
 print(json.dumps({'coverage':len(matched)/len(expected),'paragraphs':rows},ensure_ascii=False))
if __name__=='__main__':main()
