"""19 whole mixed chapter spans and19 independent complete paragraph contexts."""
from final_cpu_common import *
import argparse, traceback
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);parser.add_argument('--attempt',choices=['v1','v2'],default='v1');a=parser.parse_args()
plan=read(FINAL/'plan.json');cap=read(ROOT/plan['captionCandidate']);settings=read(FINAL/'mix-settings.json');mix=FINAL/'final-mix.wav'
assert sha(mix)==settings['wavSha256'] and settings['planSha256']==sha(FINAL/'plan.json')
assert read(FINAL/'framed-visual-execution.json')['exitCode']==0
name='mixed-asr' if a.attempt=='v1' else 'mixed-asr-v2'
dest=FINAL/('mixed-asr-'+a.attempt);assert not dest.exists()
paragraphs=sorted(cap['paragraphs'],key=lambda p:p['startSeconds']);ids=list(dict.fromkeys(p['logicalScene'] for p in plan['pieces']))
assert len(ids)==19
windows=[]
for sid in ids:
    pieces=[p for p in plan['pieces'] if p['logicalScene']==sid];lo=min(p['startFrame'] for p in pieces)/60;hi=max(p['endFrame'] for p in pieces)/60
    expected=[p for p in paragraphs if lo-1e-6<=p['startSeconds'] and p['endSeconds']<=hi+1e-6]
    windows.append(dict(label='scene-'+sid,scene=sid,fromSeconds=lo,toSeconds=hi,expectedKo=[p['ko'] for p in expected],expectedParagraphs=[dict(scene=p['scene'],paragraph=p['paragraph'],pieceId=p['pieceId']) for p in expected],scope='Entire logical chapter span including the interleaved new guides when present; compare all chronological text.'))
for sid in ids:
    own=[p for p in paragraphs if p['scene']==sid]
    if int(sid)>=12:
        lo=paragraphs.index(own[0]);hi=paragraphs.index(own[-1]);parts=paragraphs[max(0,lo-1):min(len(paragraphs),hi+2)]
    else:parts=own[-2:]
    lo=max(120/60,parts[0]['startSeconds']-.30);hi=min(22970/60,parts[-1]['endSeconds']+.30)
    if hi-lo>29.4:
        parts=own;lo=parts[0]['startSeconds']-.3;hi=parts[-1]['endSeconds']+.3
    assert hi-lo<=29.4,(sid,hi-lo)
    windows.append(dict(label=sid+'-complete-context',scene=sid,fromSeconds=lo,toSeconds=hi,expectedKo=[p['ko'] for p in parts],expectedParagraphs=[dict(scene=p['scene'],paragraph=p['paragraph'],pieceId=p['pieceId']) for p in parts],scope='Independent complete paragraphs; guides include both adjacent complete paragraphs where under29.4s. No chunking or expected recognizer prompt.'))
assert len(windows)==38
w=Worker(name,a.resource,'Directly compare all19current mixed chapter spans and19independent complete contexts, including joins/end sounds/omission/repetition/pronunciation. No heuristic-only approval. Then pair/finalpixels/QA/collect/private/Git and pause24. No next queued.');w.state.update(mixSha256=sha(mix),planSha256=sha(FINAL/'plan.json'),totalScenes=19,totalWindows=38,completed=0,device='cpu',expectedWasRecognizerPrompt=False,automaticApproval=False,humanWholeListening='pending',humanPronunciation='pending',log=rel(FINAL/('mixed-asr-'+a.attempt+'.log')))
dest.mkdir();request=FINAL/('mixed-asr-request.json' if a.attempt=='v1' else 'mixed-asr-request-v2.json')
write(request,dict(createdAt=now(),mixSha256=sha(mix),planSha256=sha(FINAL/'plan.json'),windows=windows,expectedWasRecognizerPrompt=False,automaticApproval=False))
write(FINAL/'mixed-asr-current.json',dict(attempt=a.attempt,execution=rel(w.path),request=rel(request),results=rel(dest/'asr.json'),session=rel(FINAL/(name+'-session.json')),mixSha256=sha(mix),planSha256=sha(FINAL/'plan.json'),previousFailurePreserved=rel(FINAL/'mixed-asr-execution.json') if a.attempt=='v2' else None))
original=os.sys.stdout;originalerr=os.sys.stderr
class Tee:
    def __init__(self,f):self.f=f
    def write(self,s):original.write(s);original.flush();self.f.write(s);self.f.flush();return len(s)
    def flush(self):original.flush();self.f.flush()
with (FINAL/('mixed-asr-'+a.attempt+'.log')).open('x',encoding='utf-8') as log:
    os.sys.stdout=Tee(log);os.sys.stderr=os.sys.stdout
    try:
        w.checkpoint();import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        results=[]
        for win in windows:
            path=dest/(win['label']+'.wav');w.ff(['-v','error','-i',mix,'-af',f'atrim=start={win["fromSeconds"]}:end={win["toSeconds"]},asetpts=PTS-STARTPTS','-ar','16000','-ac','1','-c:a','pcm_s16le',path],'CPU-current-mix-window')
            w.state['status']='transcribing-'+win['label'];w.checkpoint()
            kwargs=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            if win['label'].startswith('scene-'):kwargs['chunk_length_s']=30
            raw=transcriber(str(path),**kwargs)
            row={**win,'windowPath':rel(path),'windowSha256':sha(path),'mixSha256':settings['wavSha256'],'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False}
            write(dest/(win['label']+'.json'),row);results.append(row)
            write(dest/'asr.json',dict(mixSha256=settings['wavSha256'],planSha256=sha(FINAL/'plan.json'),complete=len(results)==38,results=results,humanWholeListening='pending',automaticallyApproved=False))
            w.state['completed']=len(results);w.checkpoint();print(json.dumps(dict(label=win['label'],text=raw['text']),ensure_ascii=False),flush=True)
        assert sha(mix)==settings['wavSha256'];w.close('closed-current-mixed-ASR-awaiting-direct-review')
    except BaseException:
        w.close('closed-current-mixed-ASR-failed',1,traceback.format_exc());raise
    finally:os.sys.stdout=original;os.sys.stderr=originalerr
