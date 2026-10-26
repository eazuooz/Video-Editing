"""Independent ASR of actual PCM paragraphs; preserves the original full ASR.

No expected-text prompt, transcript substitutions or audio editing. Added ASR-only
silence is removed from timestamp coordinates, and never enters the video.
"""
from pathlib import Path
import argparse,importlib.util,json,sys,os,time,difflib
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('slug');args=ap.parse_args()
batch=json.loads((Path(__file__).with_name('batch.json')).read_text(encoding='utf8'))
assert args.slug in [i['slug'] for i in batch['projects']]
P=R/'projects'/args.slug;sys.path.insert(0,str(P/'production'))
import audio_revision as a
a.guard()
spec=importlib.util.spec_from_file_location('selected_asr',P/'production/transcribe.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
model_path=module.resolve_existing_asr_model();digest=a.sha(a.VOICE)
output=a.L/f'asr-voice-paragraphs-{digest[:12]}.json'
assert not output.exists(),'Preserve the earlier independent paragraph ASR.'
timing=a.read(a.VOICE.with_suffix('.timing.json'));assert timing['voiceSha256']==digest
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
with a.gpu_lease('independent-paragraph-asr-after-full-transcript-discrepancy') as lease:
    import numpy as np,soundfile as sf,torch
    from scipy.signal import resample_poly
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(3);torch.set_num_interop_threads(1)
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cuda')
    processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
    recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cuda')
    pcm,rate=sf.read(a.VOICE,dtype='float32');assert rate==24000 and pcm.ndim==1
    texts=[];chunks=[];rows=[]
    for e in timing['entries']:
        a.assert_owned_lease(lease)
        start=round(e['start']*rate);end=round(e['end']*rate)
        samples=resample_poly(pcm[start:end],2,3).astype(np.float32)
        pad=4800;inp=np.pad(samples,(pad,pad))
        result=recognize({'raw':inp,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        texts.append(result['text']);adjusted=[]
        for c in result['chunks']:
            times=[None if t is None else max(e['start'],min(e['end'],t-.3+e['start'])) for t in c['timestamp']]
            adjusted.append(dict(text=c['text'],timestamp=times))
        chunks.extend(adjusted);rows.append(dict(index=e['index'],startSample=start,endSample=end,raw=result,adjusted=adjusted))
        print(json.dumps({'paragraph':e['index'],'text':result['text']},ensure_ascii=False),flush=True)
    text=''.join(texts);expected=' '.join(e['text'] for e in timing['entries'])
    norm=lambda t:a.normalize_speech(t,{})
    report=dict(schemaVersion=1,revision=a.REVISION,role='voice',input=a.media_reference(a.VOICE),sha256=digest,fullInput=True,
        inputDurationSeconds=len(pcm)/rate,text=text,chunks=chunks,expected=expected,rawRecognitionUnmodified=True,expectedTextPromptUsed=False,
        paragraphs=rows,independentMethod='All real PCM paragraphs separately;300ms ASR-only leading/trailing silence; word time offsets mapped to actual PCM',
        normalizedMatch=norm(expected)==norm(text),similarity=difflib.SequenceMatcher(None,norm(expected),norm(text),autojunk=False).ratio(),humanListening='pending',
        originalFullAsrPreserved=True,completePcmSha256=digest,timingSha256=a.sha(a.VOICE.with_suffix('.timing.json')))
    assert a.sha(a.VOICE)==digest
    with output.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(output=str(output),similarity=report['similarity']),ensure_ascii=False))
