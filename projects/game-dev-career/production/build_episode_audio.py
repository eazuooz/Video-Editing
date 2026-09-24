"""Measured full-episode alignment and mix. Raw takes and previous previews stay intact."""
from pathlib import Path
import argparse, difflib, gc, hashlib, json, math, re, subprocess, sys
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
CFG=json.loads((BASE.parent/'project.json').read_text(encoding='utf-8'))
KO=json.loads((ROOT/CFG['paths']['script']).read_text(encoding='utf-8'))['scenes']
EN=json.loads((BASE.parent/'script/narration.en.json').read_text(encoding='utf-8'))['scenes']
OUT=ROOT/CFG['tts']['outputDir']; STEM=CFG['tts']['filenameStem']
MC=ROOT/'motion-canvas/src/projects/game-dev-career'; ASSETS=MC/'assets'
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(s):return re.sub(r'[^가-힣a-z0-9]','',s.lower())
def run(args):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(p.stderr[-4000:])
    return p.stderr
def parts(s,n):
    words=s.split();result=[];cursor=0
    for k in range(n-1):
        target=sum(len(w)+1 for w in words[cursor:])/(n-k);length=0;end=cursor
        while end<len(words)-(n-k-1):
            length+=len(words[end])+1;end+=1
            if length>=target:break
        result.append(' '.join(words[cursor:end]));cursor=end
    result.append(' '.join(words[cursor:]));return result
def stamp(s):
    ms=round(s*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
def wrap(s,width):
    words=s.split();lines=[];line=''
    for w in words:
        if line and len(line)+len(w)+1>width:lines.append(line);line=w
        else:line=(line+' '+w).strip()
    return '\n'.join(lines+[line])

def align():
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(6)
    model_id='openai/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cuda:0')
    proc=AutoProcessor.from_pretrained(model_id,local_files_only=True)
    asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device='cuda:0')
    audios=[];scenes=[];captions=[];entries=[];reports=[];frame=0
    for scene,en in zip(KO,EN,strict=True):
        assert scene['id']==en['id'] and len(scene['lines'])==len(en['lines'])
        file=OUT/'chunks'/f"{scene['id']}-scene.wav";wav,sr=sf.read(file,dtype='float32');assert sr==24000
        cache=BASE/'asr'/f"{scene['id']}.json";digest=hashlib.sha256(file.read_bytes()).hexdigest()
        if cache.exists() and json.loads(cache.read_text(encoding='utf-8')).get('sha256')==digest:result=json.loads(cache.read_text(encoding='utf-8'))
        else:
            print('Read-back '+scene['id'],flush=True)
            result=asr(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');result['sha256']=digest;dump(cache,result)
        duration=len(wav)/sr;expected=norm(''.join(scene['lines']));recognized='';times=[]
        for word in result['chunks']:
            chars=norm(word['text']);a,b=word['timestamp'];a=0 if a is None else a;b=duration if b is None else b
            for j,c in enumerate(chars):recognized+=c;times.append((a+(b-a)*j/max(1,len(chars)),a+(b-a)*(j+1)/max(1,len(chars))))
        matcher=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);mapping={}
        for block in matcher.get_matching_blocks():
            for j in range(block.size):mapping[block.a+j]=times[block.b+j]
        if not mapping:raise RuntimeError('No ASR alignment')
        def mapped(i):return mapping.get(i,mapping[min(mapping,key=lambda k:abs(k-i))])
        lead=.25;frames=math.ceil((duration+lead+.72)*60)
        fade=min(144,len(wav)//2);wav[:fade]*=np.linspace(0,1,fade);wav[-fade:]*=np.linspace(1,0,fade)
        audios.append(np.pad(wav,(round(lead*sr),frames*400-round(lead*sr)-len(wav))))
        cursor=0;local=[]
        for line,eng in zip(scene['lines'],en['lines'],strict=True):
            count=len(norm(line));a=max(0,mapped(cursor)[0]);b=min(duration,mapped(cursor+count-1)[1])
            entries.append({'index':len(entries)+1,'scene_id':scene['id'],'scene_title':scene['title'],'text':line,'start':frame/60+a+lead,'end':frame/60+b+lead})
            n=max(1,math.ceil(len(line)/56),math.ceil(len(eng)/100))
            for kp,ep in zip(parts(line,n),parts(eng,n),strict=True):
                size=len(norm(kp));start=max(0,mapped(cursor)[0]);end=min(duration,mapped(cursor+size-1)[1]);cursor+=size
                local.append({'start':lead+start,'end':lead+end,'ko':kp,'en':ep})
        for i,c in enumerate(local):
            following=local[i+1]['start']-.04 if i+1<len(local) else duration+lead+.15
            c['end']=min(following,max(c['end']+.10,c['start']+.3))
            if c['end']<=c['start']:raise RuntimeError('Non-monotonic ASR timing '+scene['id'])
            captions.append({**c,'start':frame/60+c['start'],'end':frame/60+c['end'],'scene':scene['id']})
        scenes.append({'id':scene['id'],'title':scene['title'],'firstFrame':frame,'frames':frames,'duration':frames/60,'speechDuration':duration,'cues':local})
        reports.append({'scene':scene['id'],'expected':' '.join(scene['lines']),'recognized':result['text'],'similarity':matcher.ratio(),'unmatched':[{'expected':expected[a:b],'recognized':recognized[c:d]} for tag,a,b,c,d in matcher.get_opcodes() if tag!='equal']})
        frame+=frames;print(f"Scene {scene['id']}: {duration:.2f}s, similarity {matcher.ratio():.3f}",flush=True)
    del asr,model;gc.collect();torch.cuda.empty_cache()
    ASSETS.mkdir(parents=True,exist_ok=True)
    full=np.concatenate(audios);sf.write(OUT/f'{STEM}.wav',full,24000);sf.write(ASSETS/'narration.wav',full,24000)
    timing={'fps':60,'totalFrames':frame,'duration':frame/60,'scenes':scenes,'captions':captions}
    dump(MC/'timing.generated.json',timing);dump(BASE/'asr-review.json',reports)
    dump(OUT/f'{STEM}.timing.json',{'sample_rate':24000,'duration_seconds':frame/60,'render_mode':'scene','example_seconds':CFG['editing']['exampleSeconds'],'narration_placement':CFG['editing']['narrationPlacement'],'entries':entries,'alignment':'Whisper word timestamps with approved-script character alignment','scene_starts':[s['firstFrame']/60 for s in scenes]})
    for lang,width,pathkey in [('ko',30,'captionsKo'),('en',52,'captionsEn')]:
        content='\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{wrap(c[lang],width)}" for i,c in enumerate(captions))+'\n'
        (ROOT/CFG['paths'][pathkey]).write_text(content,encoding='utf-8')
    (OUT/f'{STEM}.asr-review.txt').write_text('\n\n'.join(f"Scene {r['scene']} ({r['similarity']:.3f})\nSCRIPT: {r['expected']}\nASR: {r['recognized']}" for r in reports),encoding='utf-8')
    (MC/'timing.ts').write_text('// GENERATED by production/build_episode_audio.py; measured at 60fps\nexport const NARRATION_FPS=60;\n'+f"export const TOTAL_DURATION={frame/60};\nexport const TOTAL_FRAMES={frame};\n"+f"export const SCENE_STARTS={json.dumps([s['firstFrame']/60 for s in scenes])} as const;\nexport const SCENE_DURATIONS={json.dumps([s['duration'] for s in scenes])} as const;\nexport const SCENE_TITLES={json.dumps([s['title'] for s in scenes],ensure_ascii=False)} as const;\n",encoding='utf-8')
    print(f'ASSEMBLED: {frame/60:.3f}s / {frame} frames / {len(captions)} paired cues',flush=True)

def mix(revision='v1'):
    suffix='' if revision=='v1' else '-'+revision
    timing=json.loads((MC/'timing.generated.json').read_text(encoding='utf-8'));seconds=timing['duration'];work=BASE/('audio'+suffix);work.mkdir(exist_ok=True)
    footage=None if revision=='v1' else json.loads((BASE/f'media-sources-{revision}.json').read_text(encoding='utf-8'))
    if CFG['audio']['backgroundMusic']['approvalStatus']!='approved':raise RuntimeError('Music not approved')
    def normalize(src,out,target):
        log=run(['ffmpeg','-hide_banner','-i',str(src),'-af',f'loudnorm=I={target}:TP=-2:LRA=11:print_format=json','-f','null','-']);values=json.loads(log[log.rfind('{'):log.rfind('}')+1])
        if values['input_i']=='-inf':return values
        filt=f"loudnorm=I={target}:TP=-2:LRA=11:measured_I={values['input_i']}:measured_TP={values['input_tp']}:measured_LRA={values['input_lra']}:measured_thresh={values['input_thresh']}:offset={values['target_offset']}:linear=true"
        run(['ffmpeg','-y','-v','error','-i',str(src),'-af',filt,'-ar','48000','-ac','2',str(out)]);return values
    n=normalize(ASSETS/'narration.wav',work/'narration.wav',CFG['audio']['narrationTargetLufs'])
    b=normalize(ROOT/CFG['audio']['backgroundMusic']['file'],work/'music.wav',CFG['audio']['bgmTargetLufs'])
    music,rate=sf.read(work/'music.wav',dtype='float32');assert rate==48000
    # Start after the long opening, then crossfade the whole selected track when needed.
    loop=music.copy();music=music[24*rate:];total=round(seconds*rate);cross=rate
    while len(music)<total:
        fade=np.linspace(0,1,cross,dtype='float32')[:,None]
        music=np.concatenate([music[:-cross],music[-cross:]*(1-fade)+loop[:cross]*fade,loop[cross:]])
    music=music[:total];original=np.zeros((total,2),dtype='float32');atten=np.ones(total,dtype='float32');sources=[]
    for s in timing['scenes']:
        file=ASSETS/('examples'+suffix)/f"{s['id']}.mp4" if footage else (ASSETS/'examples'/f"{s['id']}.mp4" if s['id'] in ('06','07') else ASSETS/'example-audio'/f"{s['id']}.wav")
        # Every normalized source clip contains real source sound or the prototype's own effects.
        target=next(c['targetLufs'] for c in footage['scenes'] if c['id']==s['id']) if footage else (-31 if s['id'] in ('06','07') else CFG['audio']['gameAudioTargetLufs'])
        out=work/f"source-{s['id']}.wav";measurement=normalize(file,out,target)
        if measurement['input_i']=='-inf':sources.append({'scene':s['id'],'silent':True});continue
        example_length=CFG['editing'].get('exampleSecondsByScene',{}).get(s['id'],CFG['editing']['exampleSeconds'])
        wav,sr=sf.read(out,dtype='float32');start=round(s['firstFrame']/60*rate);count=min(len(wav),round(example_length*rate),total-start);wav=wav[:count]
        fadein=min(round(.12*rate),count);fadeout=min(round(.3*rate),count);wav[:fadein]*=np.linspace(0,1,fadein)[:,None];wav[-fadeout:]*=np.linspace(1,0,fadeout)[:,None];original[start:start+count]+=wav
        ramp=min(round(.45*rate),count//2);dip=np.full(count,10**(CFG['audio']['bgmDuringGameplayDb']/20),dtype='float32');dip[:ramp]=np.linspace(1,dip[0],ramp);dip[-ramp:]=np.linspace(dip[-1],1,ramp);atten[start:start+count]=np.minimum(atten[start:start+count],dip)
        sources.append({'scene':s['id'],'targetLufs':target,'analysis':measurement})
    music*=atten[:,None];fade=round(.45*rate);music[:fade]*=np.linspace(0,1,fade)[:,None];music[-fade:]*=np.linspace(1,0,fade)[:,None]
    sf.write(work/'background.wav',music+original,rate)
    fc='[0:a]asplit=2[n][side];[1:a][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[bg];[n][bg]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]'
    run(['ffmpeg','-y','-v','error','-i',str(work/'narration.wav'),'-i',str(work/'background.wav'),'-filter_complex',fc,'-map','[mix]','-t',str(seconds),'-ar','48000','-ac','2',str(ASSETS/f'final-mix{suffix}.wav')])
    run(['ffmpeg','-y','-v','error','-i',str(ASSETS/f'final-mix{suffix}.wav'),'-c:a','aac','-b:a','192k',str(ASSETS/f'final-mix{suffix}.m4a')])
    log=run(['ffmpeg','-hide_banner','-i',str(ASSETS/f'final-mix{suffix}.m4a'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);measurement=json.loads(log[log.rfind('{'):log.rfind('}')+1])
    if float(measurement['input_tp'])>-1.5:raise RuntimeError('True peak exceeds target')
    dump(BASE/f'mix-report{suffix}.json',{'duration':seconds,'narration':n,'bgm':b,'music':'Discovery — Scott Buckley','continuous':True,'crossfadeSeconds':1,'sources':sources,'encodedMix':measurement,'humanListeningApproval':False})
    print('MIX READY '+json.dumps(measurement),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['align','mix']);p.add_argument('--revision',default='v1',choices=['v1','v2','v3']);args=p.parse_args()
    if args.stage=='mix':mix(args.revision)
    else:align()
