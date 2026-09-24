"""Local preview synthesis and measured bilingual timing. Does not render the full episode."""
from __future__ import annotations
import argparse, difflib, gc, hashlib, json, math, random, re, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
PREVIEW_ROOT = Path(__file__).resolve().parent
BASE = PREVIEW_ROOT
VERSION = 1
DEVICE = 'auto'
ASSETS = ROOT / 'motion-canvas/src/projects/game-dev-career/preview/assets'
SCRIPT = BASE / 'script.v1.json'
CONFIG = json.loads((ROOT / 'projects/game-dev-career/project.json').read_text(encoding='utf-8'))
PLAN = None
sys.path.insert(0, str(ROOT / 'qwen3-tts'))

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def run(args):
    p = subprocess.run(args, capture_output=True, encoding='utf-8', errors='replace', creationflags=0x08000000)
    if p.returncode:
        raise RuntimeError(p.stderr[-8000:])
    return p.stderr

def norm(s):
    return re.sub(r'[^a-z0-9가-힣]', '', s.lower().replace('c++','씨플러스플러스').replace('2d','이차원').replace('3d','삼차원'))

def synthesize():
    import torch
    from qwen_tts import Qwen3TTSModel
    from review_project_narration import acoustic_evidence
    torch.set_num_threads(6)
    tts = CONFIG['tts']
    device=('cuda:0' if torch.cuda.is_available() else 'cpu') if DEVICE=='auto' else DEVICE
    dtype=torch.bfloat16 if device.startswith('cuda') else torch.float32
    print('TTS device: '+device,flush=True)
    out = BASE / 'audio'; out.mkdir(exist_ok=True)
    model = Qwen3TTSModel.from_pretrained(str(ROOT / tts['model']), device_map=device, dtype=dtype)
    prompt = model.create_voice_clone_prompt(ref_audio=str(ROOT / tts['reference']),
        ref_text=(ROOT / tts['referenceText']).read_text(encoding='utf-8').strip(), x_vector_only_mode=False)
    reports=[]
    for scene in PLAN['scenes']:
        text=' '.join(scene['lines']); file=out / f"{scene['id']}.wav"; meta=file.with_suffix('.json')
        digest=hashlib.sha256(text.encode()).hexdigest()
        if VERSION > 1 and not file.exists():
            previous=PREVIEW_ROOT/'audio'/file.name
            previous_meta=previous.with_suffix('.json')
            if previous.exists() and previous_meta.exists() and json.loads(previous_meta.read_text(encoding='utf-8')).get('textSha256')==digest:
                for source in [previous,previous_meta,previous.with_suffix('.asr.json'),*previous.parent.glob(f"{scene['id']}-take*.wav")]:
                    if source.exists():shutil.copy2(source,out/source.name)
        if file.exists() and meta.exists() and json.loads(meta.read_text(encoding='utf-8')).get('textSha256')==digest:
            reports.append(json.loads(meta.read_text(encoding='utf-8'))); print('Reused '+scene['id'],flush=True); continue
        if file.exists(): raise RuntimeError('Existing different take preserved: '+str(file))
        for attempt in range(3):
            seed=43+int(scene['id'])+attempt*100
            random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
            print('Synthesizing '+scene['id']+' attempt '+str(attempt+1),flush=True)
            waves,sr=model.generate_voice_clone(text=text, language='Korean', voice_clone_prompt=prompt,
                non_streaming_mode=True,max_new_tokens=768)
            wav=np.asarray(waves[0],dtype=np.float32)
            take=out / f"{scene['id']}-take{attempt+1}.wav";sf.write(take,wav,sr)
            evidence=acoustic_evidence(take,tts)
            if not 3 < evidence['duration'] < 48: continue
            if evidence['endingHeuristicPassed'] or attempt==2:
                sf.write(file,wav,sr)
                report={'scene':scene['id'],'seed':seed,'textSha256':digest,'text':text,**evidence,'humanApproval':False}
                dump(meta,report);reports.append(report)
                print(f"Scene {scene['id']}: {len(wav)/sr:.2f}s tail={evidence['tailRatio']:.4f}",flush=True);break
        else: raise RuntimeError('Unable to produce bounded scene '+scene['id'])
    dump(BASE/'tts-report.json',{'scenes':reports,'model':tts['model'],'voice':'existing balanced reference','kind':'preview'})

def transcribe_and_assemble():
    from review_project_narration import acoustic_evidence
    # Preserve all raw takes; if the ending heuristic rejected every take, use
    # the least abrupt one and retain the failed heuristic for listening review.
    for scene in PLAN['scenes']:
        file=BASE/'audio'/f"{scene['id']}.wav";meta=file.with_suffix('.json')
        report=json.loads(meta.read_text(encoding='utf-8'))
        if not report['endingHeuristicPassed']:
            candidates=[]
            for candidate in (BASE/'audio').glob(f"{scene['id']}-take*.wav"):
                evidence=acoustic_evidence(candidate,CONFIG['tts'])
                if not 3<evidence['duration']<48:continue
                score=max(evidence['tailRatio']/.07,70/max(evidence['decayMs'] or 10000,1))
                candidates.append((score,candidate,evidence))
            _,chosen,evidence=min(candidates,key=lambda x:x[0])
            wav,rate=sf.read(chosen);sf.write(file,wav,rate)
            report.update(evidence);report['selectedTake']=chosen.name
            report['seed']=43+int(scene['id'])+(int(chosen.stem.split('take')[-1])-1)*100
            dump(meta,report);print('Selected quietest ending: '+chosen.name,flush=True)
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(6)
    device=('cuda:0' if torch.cuda.is_available() else 'cpu') if DEVICE=='auto' else DEVICE
    dtype=torch.float16 if device.startswith('cuda') else torch.float32
    model_id='openai/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=dtype,low_cpu_mem_usage=True,
        use_safetensors=True,attn_implementation='eager',local_files_only=True).to(device)
    processor=AutoProcessor.from_pretrained(model_id,local_files_only=True)
    asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,dtype=dtype,device=device)
    timeline=[]; audio=[]; frame=0; captions=[]; reports=[]
    ASSETS.mkdir(parents=True,exist_ok=True)
    for scene in PLAN['scenes']:
        file=BASE/'audio'/f"{scene['id']}.wav"; wav,sr=sf.read(file,dtype='float32')
        if sr!=24000: raise RuntimeError('Unexpected Qwen sample rate')
        cache=BASE/'audio'/f"{scene['id']}.asr.json"; digest=hashlib.sha256(file.read_bytes()).hexdigest()
        if cache.exists() and json.loads(cache.read_text(encoding='utf-8')).get('sha256')==digest:
            result=json.loads(cache.read_text(encoding='utf-8'))
        else:
            print('Read-back '+scene['id'],flush=True)
            result=asr(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            result['sha256']=digest;dump(cache,result)
        expected=norm(''.join(scene['lines'])); recognized=''; times=[]
        for word in result['chunks']:
            chars=norm(word['text']); a,b=word['timestamp']; a=0 if a is None else a;b=len(wav)/sr if b is None else b
            for j,c in enumerate(chars):
                recognized+=c;times.append((a+(b-a)*j/max(1,len(chars)),a+(b-a)*(j+1)/max(1,len(chars))))
        matcher=difflib.SequenceMatcher(None,expected,recognized,autojunk=False)
        mapping={}
        for block in matcher.get_matching_blocks():
            for j in range(block.size):mapping[block.a+j]=times[block.b+j]
        if not mapping:raise RuntimeError('No ASR alignment')
        def mapped(i):return mapping.get(i,mapping[min(mapping,key=lambda k:abs(k-i))])
        duration=len(wav)/sr;lead=.30;frames=math.ceil((duration+lead+.85)*60)
        padded=np.pad(wav,(round(lead*sr),frames*400-round(lead*sr)-len(wav)))
        audio.append(padded);cursor=0;marks=[]
        for i,line in enumerate(scene['lines']):
            count=len(norm(line));a=max(0,mapped(cursor)[0]);b=min(duration,mapped(cursor+count-1)[1]);cursor+=count
            marks.append({'start':a+lead,'end':b+lead,'ko':line,'en':scene['en'][i]})
        for i,m in enumerate(marks):
            stop=marks[i+1]['start']-.05 if i+1<len(marks) else duration+lead+.15
            end=min(stop,max(m['end']+.12,m['start']+.5))
            captions.append({**m,'start':frame/60+m['start'],'end':frame/60+end})
        timeline.append({**scene,'firstFrame':frame,'frames':frames,'duration':frames/60,'speechDuration':duration,'cues':marks})
        reports.append({'scene':scene['id'],'expected':' '.join(scene['lines']),'recognized':result['text'],'similarity':matcher.ratio()})
        frame+=frames
    del asr,model;gc.collect();torch.cuda.empty_cache()
    sf.write(ASSETS/f'narration-v{VERSION}.wav',np.concatenate(audio),24000)
    dump(BASE/'asr-review.json',reports)
    dump(ASSETS.parent/'timing.generated.json',{'fps':60,'totalFrames':frame,'duration':frame/60,'scenes':timeline,'captions':captions})
    def stamp(s):
        ms=round(s*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    def wrap(text,limit):
        words=text.split();lines=[];line=''
        for word in words:
            if line and len(line)+len(word)+1>limit:lines.append(line);line=word
            else:line=(line+' '+word).strip()
        if line:lines.append(line)
        return '\n'.join(lines)
    for lang,limit in [('ko',30),('en',54)]:
        srt='\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{wrap(c[lang],limit)}" for i,c in enumerate(captions))+'\n'
        (BASE/f'game-dev-career-preview-v{VERSION}.{lang}.srt').write_text(srt,encoding='utf-8')
    print(f'Measured preview: {frame} frames, {frame/60:.3f}s',flush=True)

def mix():
    timing=json.loads((ASSETS.parent/'timing.generated.json').read_text(encoding='utf-8'));seconds=timing['duration']
    if CONFIG['audio']['backgroundMusic']['approvalStatus']!='approved':raise RuntimeError('Music not selected')
    music=ROOT/CONFIG['audio']['backgroundMusic']['file']
    def normalize(src,out,target):
        log=run(['ffmpeg','-hide_banner','-i',str(src),'-af',f'loudnorm=I={target}:TP=-2:LRA=11:print_format=json','-f','null','-'])
        values=json.loads(log[log.rfind('{'):log.rfind('}')+1])
        filt=f"loudnorm=I={target}:TP=-2:LRA=11:measured_I={values['input_i']}:measured_TP={values['input_tp']}:measured_LRA={values['input_lra']}:measured_thresh={values['input_thresh']}:offset={values['target_offset']}:linear=true"
        run(['ffmpeg','-y','-v','error','-i',str(src),'-af',filt,'-ar','48000','-ac','2',str(out)])
        return values
    narration=BASE/'audio/narration-normalized.wav';bgm=BASE/'audio/bgm-normalized.wav'
    n=normalize(ASSETS/f'narration-v{VERSION}.wav',narration,-16)
    excerpt=BASE/'audio/discovery-excerpt.wav'
    run(['ffmpeg','-y','-v','error','-ss','24','-i',str(music),'-t',str(seconds),'-ar','48000','-ac','2',str(excerpt)])
    b=normalize(excerpt,bgm,-28)
    fc=f'[0:a]asplit=2[n][side];[1:a]afade=t=in:d=0.45,afade=t=out:st={seconds-.65}:d=0.65[m];[m][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[bg];[n][bg]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]'
    run(['ffmpeg','-y','-v','error','-i',str(narration),'-i',str(bgm),'-filter_complex',fc,'-map','[mix]','-t',str(seconds),'-ar','48000','-ac','2',str(ASSETS/f'preview-mix-v{VERSION}.wav')])
    run(['ffmpeg','-y','-v','error','-i',str(ASSETS/f'preview-mix-v{VERSION}.wav'),'-c:a','aac','-b:a','192k',str(ASSETS/f'preview-mix-v{VERSION}.m4a')])
    log=run(['ffmpeg','-hide_banner','-i',str(ASSETS/f'preview-mix-v{VERSION}.m4a'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
    measured=json.loads(log[log.rfind('{'):log.rfind('}')+1])
    if float(measured['input_tp']) > -1.5:raise RuntimeError('Encoded true peak too high')
    dump(BASE/'mix-report.json',{'kind':'narrated-preview','duration':seconds,'narrationTargetLufs':-16,'bgmTargetLufs':-28,'bgmSource':str(music.relative_to(ROOT)),'excerptStart':24,'continuousBgm':True,'sourceFootageAudio':'not applicable: original motion graphics preview','narrationAnalysis':n,'bgmAnalysis':b,'encodedMix':measured,'humanListeningApproval':False})
    print('Preview audio mixed: '+str(measured),flush=True)

def caption_audio():
    if VERSION!=2:raise RuntimeError('Caption sample uses preview v2')
    timing=json.loads((ASSETS.parent/'timing.generated.json').read_text(encoding='utf-8'))
    seconds=timing['scenes'][0]['duration']
    target=ROOT/'motion-canvas/src/projects/game-dev-career/caption-sample/assets'
    target.mkdir(parents=True,exist_ok=True)
    run(['ffmpeg','-v','error','-y','-i',str(ASSETS/'preview-mix-v2.wav'),'-t',str(seconds),'-af',f'afade=t=out:st={seconds-.45}:d=0.45','-ar','48000','-ac','2',str(target/'preview-mix-v2.wav')])
    run(['ffmpeg','-v','error','-y','-i',str(target/'preview-mix-v2.wav'),'-c:a','aac','-b:a','192k',str(target/'preview-mix-v2.m4a')])
    print(f'Caption sample audio: {seconds:.3f}s')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['tts','assemble','mix','caption-audio']);p.add_argument('--version',type=int,choices=[1,2],default=1);p.add_argument('--device',choices=['auto','cpu','cuda:0'],default='auto');args=p.parse_args()
    VERSION=args.version
    DEVICE=args.device
    BASE=PREVIEW_ROOT if VERSION==1 else PREVIEW_ROOT/f'v{VERSION}'
    ASSETS=ROOT/f'motion-canvas/src/projects/game-dev-career/{"preview" if VERSION==1 else f"preview-v{VERSION}"}/assets'
    SCRIPT=PREVIEW_ROOT/f'script.v{VERSION}.json'
    PLAN=json.loads(SCRIPT.read_text(encoding='utf-8'))
    BASE.mkdir(parents=True,exist_ok=True)
    {'tts':synthesize,'assemble':transcribe_and_assemble,'mix':mix,'caption-audio':caption_audio}[args.stage]()
