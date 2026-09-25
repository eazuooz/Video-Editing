"""Full-page ASR alignment, measured timeline, KO SRT and narration mastering.

Every output is a review asset until ASR differences and listening are reviewed.
Optional --pages N --device cpu exercises the pipeline without occupying TTS GPU.
No source PDF edits. No music. No guessed membership avatars or badge images.
"""
from pathlib import Path
import argparse
import difflib
import gc
import hashlib
import json
import math
import re
import subprocess

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/renderformer-explained'
MC=ROOT/'motion-canvas/src/projects/renderformer-explained/full'


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def run(*args):
    return subprocess.run(args,check=True,capture_output=True,text=True,encoding='utf-8')


def norm(text):
    text=text.lower().replace('3차원','삼차원').replace('2차원','이차원')
    for a,b in [('q','큐'),('k','케이'),('v','브이'),('transformer','트랜스포머'),
                ('renderformer','렌더포머'),('softmax','소프트맥스'),('layernorm','레이어놈'),
                ('rmsnorm','알엠에스놈'),('rope','로프')]:text=text.replace(a,b)
    return re.sub(r'[^a-z0-9가-힣]','',text)


def split_caption(text):
    # Conservative 60 full-width units: at most two 44px lines in 1540px.
    parts=[];current=''
    weight=lambda s:sum(.58 if ord(c)<128 else 1 for c in s)
    for word in text.split():
        candidate=(current+' '+word).strip()
        if current and weight(candidate)>60:
            parts.append(current);current=word
        else:current=candidate
    if current:parts.append(current)
    return parts


def stamp(seconds):
    ms=round(seconds*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pages',type=int,default=88)
    parser.add_argument('--device',choices=['cuda','cpu'],default='cuda')
    args=parser.parse_args()
    if not 1<=args.pages<=88:raise ValueError('pages must be 1..88')
    import numpy as np
    import soundfile as sf
    manifest=json.loads((PROJECT/'project.json').read_text(encoding='utf-8'))
    items=json.loads((ROOT/manifest['paths']['script']).read_text(encoding='utf-8'))['scenes'][:args.pages]
    audio_dir=ROOT/manifest['tts']['outputDir']
    out=PROJECT/'production'/('body-review' if args.pages==88 else f'proof-{args.pages:02}')
    out.mkdir(parents=True,exist_ok=True)
    transcriber=None
    scenes=[];captions=[];reports=[];cursor=0;rate=48000
    # Stream the long WAV to disk instead of holding the whole lecture in memory.
    with sf.SoundFile(out/'body-unmastered.wav',mode='w',samplerate=rate,channels=2,subtype='PCM_16') as mix:
        for scene in items:
            sid=scene['id'];wav=audio_dir/f'chunks/{sid}-scene.wav'
            if not wav.exists():raise FileNotFoundError(wav)
            digest=hashlib.sha256(wav.read_bytes()).hexdigest()
            cache=audio_dir/f'asr/page{sid}.json'
            asr=json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else {}
            if asr.get('sha256')!=digest:
                if transcriber is None:
                    import torch
                    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
                    torch.set_num_threads(4)
                    name='openai/whisper-large-v3-turbo'
                    dtype=torch.float16 if args.device=='cuda' else torch.float32
                    model=AutoModelForSpeechSeq2Seq.from_pretrained(name,dtype=dtype,
                        low_cpu_mem_usage=True,attn_implementation='eager').to(args.device)
                    processor=AutoProcessor.from_pretrained(name)
                    transcriber=pipeline('automatic-speech-recognition',model=model,
                        tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,
                        device=0 if args.device=='cuda' else -1,dtype=dtype)
                print('ASR full page',sid,flush=True)
                raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
                asr={'sha256':digest,'text':raw['text'],'words':raw['chunks']}
                dump(cache,asr)
            expected=norm(''.join(scene['lines']))
            observed=''.join(norm(w['text']) for w in asr['words'])
            matcher=difflib.SequenceMatcher(None,expected,observed,autojunk=False)
            mapping={}
            for block in matcher.get_matching_blocks():
                mapping.update({block.a+k:block.b+k for k in range(block.size)})
            char_times=[]
            source_seconds=sf.info(wav).duration
            invalid_timestamp=False
            for word in asr['words']:
                a,b=word['timestamp']
                if a is None or b is None:
                    invalid_timestamp=True;a=0 if a is None else a;b=source_seconds if b is None else b
                char_times.extend([(a,b)]*len(norm(word['text'])))
            if not mapping:raise ValueError(f'No alignment matches on page {sid}')
            def char_time(index,end=False):
                nearest=min(mapping,key=lambda k:abs(k-index))
                return char_times[mapping[nearest]][int(end)]
            normalized=out/f'page{sid}-normalized.wav'
            run('ffmpeg','-v','error','-y','-i',str(wav),'-af','loudnorm=I=-16:TP=-2:LRA=7',
                '-ar',str(rate),'-ac','2',str(normalized))
            samples,sr=sf.read(normalized,dtype='float32',always_2d=True)
            lead=.35;frames=math.ceil((lead+len(samples)/sr+.8)*60)
            segment=np.zeros((frames*800,2),dtype=np.float32)
            edge=min(round(.006*rate),len(samples)//2)
            samples[:edge]*=np.linspace(0,1,edge)[:,None];samples[-edge:]*=np.linspace(1,0,edge)[:,None]
            first=round(lead*rate);segment[first:first+len(samples)]=samples;mix.write(segment)
            local=[];char_cursor=0;bad_cue=False
            for line_id,line in enumerate(scene['lines']):
                for part in split_caption(line):
                    length=len(norm(part))
                    start=max(lead,lead+char_time(char_cursor)-.04)
                    end=min(frames/60-.2,lead+char_time(char_cursor+length-1,True)+.06)
                    if local:
                        start=max(start,local[-1]['start']+.08)
                        local[-1]['end']=min(local[-1]['end'],start)
                        if local[-1]['end']<=local[-1]['start']:bad_cue=True
                    if end<=start:bad_cue=True;end=min(frames/60-.2,start+.1)
                    cue={'start':start,'end':end,'ko':part,'sourceLine':line_id+1}
                    local.append(cue);char_cursor+=length
            for cue in local:
                captions.append({**cue,'start':cue['start']+cursor/60,'end':cue['end']+cursor/60,'page':int(sid)})
            scenes.append({'id':sid,'sourcePage':int(sid),'title':scene['title'],'frames':frames,
                           'duration':frames/60,'firstFrame':cursor,'cues':local,'audioMeasured':True})
            end_score=difflib.SequenceMatcher(None,expected[-35:],observed[-35:],autojunk=False).ratio()
            flagged=matcher.ratio()<.90 or end_score<.70 or invalid_timestamp or bad_cue
            reports.append({'page':int(sid),'similarity':matcher.ratio(),'endingSimilarity':end_score,
                'needsReview':flagged,'invalidTimestamp':invalid_timestamp,'invalidCue':bad_cue,
                'expected':' '.join(scene['lines']),'recognized':asr['text'],
                'sha256':digest,'sourceSeconds':source_seconds,'humanListeningApproved':False})
            cursor+=frames
            dump(out/'progress.json',{'stage':'asr-and-alignment','pages':len(scenes),'total':args.pages,
                                     'flaggedPages':[r['page'] for r in reports if r['needsReview']]})
    del transcriber;gc.collect()
    measurement=run('ffmpeg','-hide_banner','-i',str(out/'body-unmastered.wav'),'-af',
                    'loudnorm=I=-16:TP=-2:LRA=7:print_format=json','-f','null','-')
    levels=json.loads(measurement.stderr[measurement.stderr.rfind('{'):measurement.stderr.rfind('}')+1])
    filt=('loudnorm=I=-16:TP=-2:LRA=7:linear=true:'+f'measured_I={levels["input_i"]}:'+ 
          f'measured_TP={levels["input_tp"]}:measured_LRA={levels["input_lra"]}:'+ 
          f'measured_thresh={levels["input_thresh"]}:offset={levels["target_offset"]}')
    run('ffmpeg','-v','error','-y','-i',str(out/'body-unmastered.wav'),'-af',filt,
        '-ar',str(rate),'-c:a','pcm_s16le',str(out/'narration-mastered.wav'))
    run('ffmpeg','-v','error','-y','-i',str(out/'narration-mastered.wav'),'-c:a','aac','-b:a','192k',str(out/'narration-mastered.m4a'))
    data={'kind':'full-page-narrated-body-review','fps':60,'totalFrames':cursor,'duration':cursor/60,
          'pages':args.pages,'scenes':scenes,'captions':captions,'bgm':None,'membershipOutroIncluded':False,
          'voiceDirectionApproved':True,'publishReady':False,'englishStatus':'pending-translation'}
    dump(out/'timing.json',data);dump(out/'asr-review.json',{'scenes':reports,'humanListeningApproved':False})
    dump(out/'mastering.json',{'targetI':-16,'targetTP':-2,'firstPass':levels,'music':None})
    (out/'renderformer.ko.srt').write_text('\n\n'.join(
        f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["ko"]}' for i,c in enumerate(captions))+'\n',encoding='utf-8')
    # Independent scene wrappers point to one measured timeline and one mastered mix.
    target=MC/('narrated' if args.pages==88 else f'proof-{args.pages:02}')
    target.mkdir(parents=True,exist_ok=True)
    dump(target/'timing.generated.json',data)
    import shutil
    shutil.copy2(out/'narration-mastered.wav',target/'narration.wav')
    imports=[];clean_imports=[];names=[]
    for i,scene in enumerate(scenes):
        name=f'page{scene["id"]}';names.append(name)
        (target/f'{name}.tsx').write_text("import {makeScene2D} from '@motion-canvas/2d';\n"+
            "import {lectureSlide} from '../slide';\nimport timing from './timing.generated.json';\n"+
            f'export default makeScene2D(function* (view) {{yield* lectureSlide(view,timing.scenes[{i}],true);}});\n',encoding='utf-8')
        imports.append(f"import {name} from './{name}?scene';")
        (target/f'{name}-clean.tsx').write_text("import {makeScene2D} from '@motion-canvas/2d';\n"+
            "import {lectureSlide} from '../slide';\nimport timing from './timing.generated.json';\n"+
            f'export default makeScene2D(function* (view) {{yield* lectureSlide(view,timing.scenes[{i}],false);}});\n',encoding='utf-8')
        clean_imports.append(f"import {name} from './{name}-clean?scene';")
    (target/'project.ts').write_text("import {makeProject} from '@motion-canvas/core';\nimport audio from './narration.wav';\n"+
        '\n'.join(imports)+"\nexport default makeProject({name:'RenderFormer — 본편 음성 검토', audio, scenes:["+
        ','.join(names)+']});\n',encoding='utf-8')
    (target/'clean.ts').write_text("import {makeProject} from '@motion-canvas/core';\nimport audio from './narration.wav';\n"+
        '\n'.join(clean_imports)+"\nexport default makeProject({name:'RenderFormer — 무자막 본편 검토', audio, scenes:["+
        ','.join(names)+']});\n',encoding='utf-8')
    shutil.copy2(MC.parent/'preview/project.meta',target/'project.meta')
    shutil.copy2(MC.parent/'preview/project.meta',target/'clean.meta')
    dump(out/'progress.json',{'stage':'audio-ready-for-review-render','pages':args.pages,'duration':cursor/60,
                             'flaggedPages':[r['page'] for r in reports if r['needsReview']],
                             'pending':['English subtitles','human listening','membership original screenshot'],
                             'publishReady':False})
    print(f'Prepared {args.pages} full pages, {cursor/60:.2f}s. Review assets, not publish-ready.',flush=True)


if __name__=='__main__':main()
