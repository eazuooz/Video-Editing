"""Reuse approved take B, recognize the full narration once, and derive scene PCM."""
from pathlib import Path
import json, sys, hashlib, subprocess, difflib
import numpy as np
import soundfile as sf
from revision_context import ROOT as R, PROJECT as P, paths, ensure_authorized
O,N,E,STEM=paths();ensure_authorized();N.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'qwen3-tts'))
from align_project_subtitles import align_characters, normalized

def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
script=read(P/'script/narration.ko.json');expected=' '.join(x for s in script['scenes'] for x in s['lines'])
raw=N/(STEM+'.wav');cache=N/'whole-source-asr.json'
stage=sys.argv[1]
if stage=='recognize':
    sources=[R/'output/tts-evaluation-20261018/yamyam-eleven-v4-take2.mp3',O/'scenes03-08-takeB.mp3']
    assert sha(sources[0])==read(P/'production/elevenlabs-revision-v2.json')['sampleSha256']
    sig={'sources':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in sources], 'joinSilenceSeconds':0.2,'sampleRate':24000}
    receipt=N/'source-assembly.json'
    if not(raw.exists() and receipt.exists() and read(receipt).get('inputs')==sig):
        parts=[];durations=[]
        for i,p in enumerate(sources):
            dest=N/f'source-{i+1}.wav'
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-ac','1','-ar','24000','-c:a','pcm_f32le',str(dest)],check=True)
            a,sr=sf.read(dest,dtype='float32');assert sr==24000 and np.isfinite(a).all()
            parts.append(a);durations.append(len(a)/sr)
        full=np.concatenate([parts[0],np.zeros(4800,dtype='float32'),parts[1]])
        sf.write(raw,full,24000,subtype='FLOAT')
        save(receipt,{'inputs':sig,'sourceDurations':durations,'duration':len(full)/24000,'sha256':sha(raw),'originalBytesRetained':True,'timeStretch':False})
    digest=sha(raw)
    if not(cache.exists() and read(cache).get('audio_sha256')==digest):
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(4)
        local=R/'qwen3-tts/models/whisper-large-v3-turbo'
        mid=str(local) if (local/'config.json').exists() else 'openai/whisper-large-v3-turbo'
        m=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float32,attn_implementation='eager',local_files_only=True)
        p=AutoProcessor.from_pretrained(mid,local_files_only=True)
        asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
        print('Recognizing full current narration on CPU; foreign GPU work untouched',flush=True)
        result=asr(str(raw),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        save(cache,{'audio_sha256':digest,'text':result['text'],'words':result['chunks'],'scope':'complete current source narration, one pass, no supplied expected prompt','device':'cpu','humanListening':'pending'})
    actual=read(cache)['text'];a,b=normalized(expected),normalized(actual);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
    save(N/'whole-source-comparison.json',{'expected':expected,'recognized':actual,'similarity':matcher.ratio(),'differences':[{'kind':op,'expected':a[i:j],'recognized':b[k:l]} for op,i,j,k,l in matcher.get_opcodes() if op!='equal'],'directReview':'pending'})
    print('Recognition ready for complete text review',flush=True)
elif stage=='split':
    q=read(cache);assert q['audio_sha256']==sha(raw)
    a,sr=sf.read(raw,dtype='float32');duration=len(a)/sr
    starts,ends,coverage=align_characters(expected,q['words'],duration)
    bounds=[0];cursor=0;contexts=[]
    for s in script['scenes'][:-1]:
        cursor+=len(normalized(' '.join(s['lines'])));end=float(ends[cursor-1])
        following=next(w for w in q['words'] if w['timestamp'][0] is not None and w['timestamp'][0]>=end-.005)
        begin=float(following['timestamp'][0]);lo=round(end*sr);hi=round(begin*sr)
        boundary=round((lo+hi)/2)
        assert hi>=lo-240, (s['id'],end,begin)
        bounds.append(boundary);contexts.append({'afterScene':s['id'],'lastWordEnd':end,'nextWord':following,'cut':boundary/sr,'gapSeconds':(hi-lo)/sr})
    bounds.append(len(a));chunks=N/'chunks';chunks.mkdir(exist_ok=True);asrdir=N/'asr';asrdir.mkdir(exist_ok=True);entries=[];reports=[]
    for s,lo,hi in zip(script['scenes'],bounds,bounds[1:]):
        f=chunks/(s['id']+'-scene.wav');sf.write(f,a[lo:hi],sr,subtype='FLOAT')
        words=[]
        for w in q['words']:
            x,y=w['timestamp']
            if x is None or y is None:continue
            # Whisper may start a new word before the preceding sentence ends
            # (the Fish title's I). Assign by its endpoint across the verified
            # silent split, rather than dropping it into the preceding scene.
            if y>lo/sr and y<=hi/sr+.001:words.append({'text':w['text'],'timestamp':[max(0,x-lo/sr),min((hi-lo)/sr,y-lo/sr)]})
        save(asrdir/(s['id']+'.json'),{'scene':s['id'],'audio_sha256':sha(f),'text':' '.join(w['text'].strip() for w in words),'words':words,'derivedFrom':{'path':str(cache.relative_to(R)),'sha256':sha(cache),'startSample':lo,'endSample':hi},'newRecognitionPass':False})
        for line in s['lines']:entries.append({'index':len(entries)+1,'scene_id':s['id'],'scene_title':s['title'],'text':line,'start':lo/sr,'end':hi/sr})
        reports.append({'scene':s['id'],'samples':hi-lo,'start':lo/sr,'duration':(hi-lo)/sr,'sha256':sha(f)})
    restored=np.concatenate([sf.read(chunks/(s['id']+'-scene.wav'),dtype='float32')[0] for s in script['scenes']]);assert np.array_equal(restored,a)
    save(N/(STEM+'.timing.json'),{'sample_rate':sr,'duration_seconds':duration,'render_mode':'continuous-source-split-on-speech-pause','entries':entries})
    save(N/'scene-split-review.json',{'matchingCoverage':coverage,'boundaries':contexts,'scenes':reports,'decodedSourceReconstructionIdentical':True,'humanListening':'pending'})
    manifest=read(P/'production/tts-manifest.json');manifest['revision']='elevenlabs-b-v2';manifest['tts'].update(engine='elevenlabs',model='Eleven v4',voiceId='jIRSnF8OWAsWEChVwCuK',outputDir=str(N.relative_to(R).as_posix()),filenameStem=STEM)
    for language in ['ko','en']:manifest['paths']['captions'+language.capitalize()]=str((O/f'body.{language}.srt').relative_to(R).as_posix())
    save(P/'production/elevenlabs-tts-manifest.json',manifest)
    print(json.dumps({'seconds':duration,'coverage':coverage,'scenes':len(reports)}))
else:raise ValueError(stage)
