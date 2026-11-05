"""Checkpointed full-paragraph word ASR of completed, original narration.

Never counts ASR as human listening, rewrites audio, or creates replacement TTS.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,atexit,difflib,hashlib,json,os,re,subprocess,uuid,time

ROOT=Path(__file__).resolve().parents[3]
MODEL=Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
LEASE=ROOT/'shared/output/GPU_HANDOFF.json';owned=None
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'[^a-z0-9가-힣]','',s.lower())
def now():return datetime.now(timezone.utc).isoformat()

def load_recognizer(device):
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    assert not torch.cuda.is_initialized() and (MODEL/'model.safetensors').exists()
    dtype=torch.float32
    if device=='cuda':
        free,total=torch.cuda.mem_get_info();assert free>=9*1024**3
        torch.cuda.set_per_process_memory_fraction(7*1024**3/total);dtype=torch.float16
    # Word timestamps require decoder cross-attention.
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(MODEL),dtype=dtype,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to(device).eval()
    processor=AutoProcessor.from_pretrained(str(MODEL))
    return pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=dtype,device=0 if device=='cuda' else 'cpu')

def recognize(pipe,samples,sr):
    from math import gcd
    import numpy as np
    import torch
    from scipy.signal import resample_poly
    g=gcd(sr,16000)
    data=resample_poly(samples,16000//g,sr//g).astype(np.float32)
    with torch.inference_mode():
        return pipe({'array':data,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word',chunk_length_s=28,stride_length_s=4)

def paragraph_record(result,e,voice_hash,device):
    chunks=[]
    for word in result.get('chunks',[]):
        begin,end=word['timestamp']
        chunks.append({'text':word['text'],'timestamp':[None if begin is None else e['start']+float(begin),None if end is None else e['start']+float(end)]})
    match=difflib.SequenceMatcher(None,norm(e['text']),norm(result['text']),autojunk=False)
    return {'schemaVersion':1,'at':now(),'audio_sha256':voice_hash,'entry':e,'text':result['text'],'chunks':chunks,'device':device,'humanListening':False,
            'comparison':{'rawCharacterSimilarity':match.ratio(),'opcodes':match.get_opcodes(),'status':'requires-content-review-not-automatic-pass'}}

def main():
    global owned
    ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--audio-revision',default='audio-v1');ap.add_argument('--transcribe',action='store_true');ap.add_argument('--device',choices=['cpu','cuda'],default='cpu');ap.add_argument('--lease-id');a=ap.parse_args()
    control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
    assert control['productionAllowedNow'] and a.project in control['projectSlugs']
    assert re.fullmatch(r'audio-v\d+',a.audio_revision)
    base=ROOT/'projects'/a.project/'production/local'/a.audio_revision;review=base/'review';review.mkdir(exist_ok=True)
    # A previously started follow-on and the finite course worker can reach the
    # last take together. Serialize them at the actual audio revision on Windows.
    import msvcrt
    word_lock=(review/'source-words.lock').open('a+b')
    if not word_lock.tell():word_lock.write(b'1');word_lock.flush()
    word_lock.seek(0)
    while True:
        try:msvcrt.locking(word_lock.fileno(),msvcrt.LK_NBLCK,1);break
        except OSError:time.sleep(3)
    atexit.register(word_lock.close)
    timing=read(base/'narration.timing.json');voice=base/'narration.wav';voice_hash=sha(voice)
    assert read(base/'tts-gpu-coordination.json')['state']=='finished','Only transcribe a finished speech edition'
    group=ROOT/'projects'/a.project/'planning/part2-delivery-edition.json'
    cpu_only=(a.device=='cpu' and not a.lease_id and group.is_file() and read(group)['audioRevision']==a.audio_revision)
    if a.lease_id:
        held=read(LEASE);assert held.get('id')==a.lease_id and held.get('owner')==a.project+'-word-review','Only exact parent-owned lease can be inherited'
        owned=a.lease_id
    elif not cpu_only:assert not LEASE.exists(),'Preserve active costly job'
    import soundfile as sf
    import numpy as np
    pcm,sr=sf.read(voice,dtype='float32');assert pcm.ndim==1
    assert abs(len(pcm)/sr-timing['duration_seconds'])<.002
    completed=[];pending=[]
    for e in timing['entries']:
        path=review/'paragraphs'/f"{e['scene_id']}-{e['paragraph']:02}.json"
        if path.exists():
            d=read(path);assert d['audio_sha256']==voice_hash and d['entry']==e
            completed.append(d)
        else:
            early=base/'review/early-pcm'/path.name
            if early.exists():
                sample=read(early)
                x=pcm[round(e['start']*sr):round(e['end']*sr)]
                matches=(sample['model']==str(MODEL) and sample['sampleRate']==sr and sample['sourceText']==e['text']
                         and sample['pcmSha256']==hashlib.sha256(x.tobytes()).hexdigest())
                if matches:
                    d=paragraph_record(sample['recognized'],e,voice_hash,'cpu')
                    d['earlyReview']={'verifiedPcmSha256':sample['pcmSha256'],'samples':len(x),'receiptSha256':sha(early)}
                    save(path,d);completed.append(d);continue
            pending.append((e,path))
    if pending and not a.transcribe:
        print(json.dumps({'ready':True,'pending':len(pending),'completed':len(completed),'device':a.device,'modelLoaded':False}));return
    if pending:
        os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
        if a.device=='cpu':os.environ['CUDA_VISIBLE_DEVICES']=''
        if cpu_only:
            import psutil
            # Matching cached PCM only reads files. A new model run, even on the
            # CPU, takes the same exclusive costly-job slot as the video renderer.
            while not owned:
                assert read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['productionAllowedNow']
                if psutil.virtual_memory().available>=8*1024**3:
                    token=str(uuid.uuid4())
                    try:
                        with LEASE.open('x',encoding='utf-8') as f:json.dump({'owner':a.project+'-word-review','id':token,'pid':os.getpid(),'createdAt':now(),'device':'cpu'},f)
                    except FileExistsError:pass
                    else:owned=token;break
                time.sleep(20)
        elif not owned:
            owned=str(uuid.uuid4())
            with LEASE.open('x',encoding='utf-8') as f:json.dump({'owner':a.project+'-word-review','id':owned,'pid':os.getpid(),'createdAt':now()},f)
        pipe=load_recognizer(a.device)
        for e,path in pending:
            # Each complete paragraph is its own timestamp origin. Resampling
            # never changes the untouched source WAV or its breathing gaps.
            x=pcm[round(e['start']*sr):round(e['end']*sr)]
            d=paragraph_record(recognize(pipe,x,sr),e,voice_hash,a.device)
            save(path,d);completed.append(d)
            save(review/'progress.json',{'status':'transcribing','completed':len(completed),'total':len(timing['entries']),'last':e['scene_id'],'updatedAt':now(),'humanListening':False})
            print(f"ASR {len(completed)}/{len(timing['entries'])}: {e['scene_id']} {d['comparison']['rawCharacterSimilarity']:.3f}",flush=True)
    completed.sort(key=lambda d:d['entry']['index'])
    assert len(completed)==len(timing['entries'])
    save(review/'source-full-asr.timestamps.json',{'audio_sha256':voice_hash,'timingSha256':sha(base/'narration.timing.json'),'model':str(MODEL),'devices':sorted(set(d['device'] for d in completed)),'humanListening':False,'timestampMode':'word','text':' '.join(d['text'] for d in completed),'chunks':[w for d in completed for w in d['chunks']],'paragraphs':[{'id':d['entry']['scene_id'],'similarity':d['comparison']['rawCharacterSimilarity']} for d in completed]})
    save(review/'progress.json',{'status':'full-word-ASR-complete-content-review-pending','completed':len(completed),'total':len(completed),'updatedAt':now(),'humanListening':False})
if __name__=='__main__':
    try:main()
    finally:
        if owned and LEASE.exists() and read(LEASE).get('id')==owned:LEASE.unlink()
