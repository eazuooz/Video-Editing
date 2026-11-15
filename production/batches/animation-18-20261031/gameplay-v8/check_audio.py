"""Read back every changed sentence from the actual new mix; cache by PCM hash."""
from common import *
import os,re,difflib,math
os.environ['OMP_NUM_THREADS']='4';os.environ['MKL_NUM_THREADS']='4'
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

def normalized(s):
 s=re.sub(r'DJ','디제이',s,flags=re.IGNORECASE)
 s=re.sub(r'(육십|예순|60)(?=\s*(프레임|도))','sixty',s)
 for a,b in [('60','예순'),('48','마흔여덟'),('36','서른여섯'),('12','열두'),('8','여덟'),('0','영'),('1','일')]:s=s.replace(a,b)
 return re.sub('[^가-힣a-z]','',s.lower())
def active_level(x,rate):
 w=round(rate*.12);rms=np.array([np.sqrt(np.mean(x[i:i+w]**2)) for i in range(0,len(x)-w,w//2)])
 active=rms[rms>.018]
 return float(20*np.log10(np.median(active))) if len(active) else None

def main():
 model=None;transcriber=None;allrows=[]
 for e in read(HERE/'plan.json')['episodes']:
  if e['id']=='A06':continue
  ep=e['id'];m=read(WORK/ep/'audio.json');folder=WORK/ep/'voice-qa';folder.mkdir(exist_ok=True)
  cues=srt(WORK/ep/'ko.srt')
  for r in m['changes']:
   with sf.SoundFile(m['audio']) as f:
    start=round(r['newStartSeconds']*f.samplerate);f.seek(start);samples=f.read(round(r['naturalDuration']*f.samplerate),dtype='float32',always_2d=True).mean(axis=1);rate=f.samplerate
    previous_cues=[c for c in cues if c['end']<=r['newStartSeconds']+.002][-2:];context_parts=[]
    for cue in previous_cues:
     f.seek(round(cue['start']*rate));context_parts.append(f.read(round((cue['end']-cue['start'])*rate),dtype='float32',always_2d=True).mean(axis=1))
    context=np.concatenate(context_parts) if context_parts else np.zeros(0,dtype='float32')
   snippet=folder/(r['id']+'.wav');mono=resample_poly(samples,1,3).astype('float32');pcm_digest=hashlib.sha256(mono.tobytes()).hexdigest()
   same=False
   if snippet.exists():
    prior_pcm,prior_rate=sf.read(snippet,dtype='float32');same=prior_rate==16000 and np.array_equal(prior_pcm,mono)
   if not same:sf.write(snippet,mono,16000,subtype='FLOAT')
   digest=sha(snippet)
   cache=folder/(r['id']+'.json')
   previous=read(cache) if cache.exists() else {}
   if previous.get('pcmSha256')==pcm_digest:raw=previous['asr']
   else:
    if transcriber is None:
     import torch
     from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
     torch.set_num_threads(4);modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
     modelid=str(modelpath) if modelpath.is_dir() else 'openai/whisper-large-v3-turbo'
     model=AutoModelForSpeechSeq2Seq.from_pretrained(modelid,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
     processor=AutoProcessor.from_pretrained(modelid,local_files_only=True)
     transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    raw=transcriber(dict(array=mono,sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   a,b=normalized(r['ko']),normalized(raw['text']);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
   coverage=sum(x.size for x in matcher.get_matching_blocks())/max(1,len(a));ratio=matcher.ratio()
   voicelevel=active_level(samples,rate);contextlevel=active_level(context,rate)
   result=dict(id=r['id'],episode=ep,audioSha256=digest,pcmSha256=pcm_digest,sourceMixSha256=m['audioSha256'],expected=r['ko'],recognized=raw['text'],asr=raw,coverage=coverage,similarity=ratio,
    differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l]) for t,i,j,k,l in matcher.get_opcodes() if t!='equal'],
    speechActiveLevelDbfs=voicelevel,precedingContextActiveLevelDbfs=contextlevel,
    activeLevelDifferenceDb=voicelevel-contextlevel if voicelevel is not None and contextlevel is not None else None,contextCues=previous_cues,
    samplePeakDbfs=float(20*np.log10(max(1e-10,np.max(np.abs(samples))))),
    contentStatus='passed-asr-readback' if coverage>=.93 and ratio>=.9 else 'inspect-asr-difference',actualMix=True,humanListening=False)
   decisions=read(HERE/'asr-difference-decisions.json') if (HERE/'asr-difference-decisions.json').exists() else {}
   decision=decisions.get(r['id'])
   if decision and decision['audioSha256']==digest and decision['recognized']==raw['text']:
    result.update(contentStatus='passed-reviewed-asr-spelling',asrDifferenceDecision=decision)
   save(cache,result);allrows.append(result);print(r['id'],f'{coverage:.3f}',raw['text'],flush=True)
 summary=dict(records=allrows,changedSentences=len(allrows),flagged=[r['id'] for r in allrows if not r['contentStatus'].startswith('passed-')],
  levelFlags=[r['id'] for r in allrows if r['activeLevelDifferenceDb'] is not None and abs(r['activeLevelDifferenceDb'])>6],
  scope='Every changed sentence from the actual mix; exact unchanged-PCM ranges reuse baseline evidence. No duplicated full ASR of byte-identical original speech.',
  unchangedPcmProofs=[str(WORK/e/'audio.json') for e in SCOPE],humanFullListening='pending-local-user-review',updatedAt=stamp())
 save(HERE/'audio-verification.json',summary)

if __name__=='__main__':main()
