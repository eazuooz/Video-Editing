"""Align the three approval excerpts, assemble narration, and compile preview data.
Run with qwen3-tts/.venv/Scripts/python.exe; no full-episode synthesis or approval.
"""
from pathlib import Path
import difflib
import hashlib
import json
import math
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/renderformer-explained'
OUT = PROJECT / 'preview'
ASSETS = ROOT / 'motion-canvas/src/projects/renderformer-explained/preview/assets'
SELECT = [('01', 3), ('14', 3), ('48', 5)]
EN = {
    '01': ['Can a Transformer learn to turn a 3D scene into an image?',
           'RenderFormer takes a scene made of triangles and predicts an image with lighting and shadows.',
           'Its name may be unfamiliar, but it starts with attention, the idea we know from language models.'],
    '14': ['We multiply the same input by different weight matrices to obtain Q, K, and V.',
           'Q describes what information we seek; K provides features for matching; V carries the information to combine.',
           'Think of them as a query, matching features, and the content to retrieve.'],
    '48': ['Let us connect the overall flow.',
           'First, mesh geometry, materials, and emission become triangle tokens.',
           'The triangles exchange information to build scene features.',
           'On the camera side, viewing rays are grouped into tokens.',
           'These ray tokens query the scene information, and the final decoder reconstructs an image.'],
}

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def norm(text):
    text=text.lower().replace('3차원','삼차원')
    for latin,spoken in [('q','큐'),('k','케이'),('v','브이')]:
        text=text.replace(latin,spoken)
    return re.sub(r'[^a-z0-9가-힣]', '', text)

def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, encoding='utf-8').stdout

def stamp(sec):
    ms = round(sec*1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def main():
    import numpy as np
    import soundfile as sf
    script = json.loads((PROJECT/'script/narration.ko.json').read_text(encoding='utf-8'))
    ASSETS.mkdir(parents=True, exist_ok=True)
    transcriber = None
    scenes, captions, audio, reports = [], [], [], []
    frame_cursor = 0
    rate = 48000
    for sid, count in SELECT:
        item = next(s for s in script['scenes'] if s['id']==sid)
        lines = item['lines'][:count]
        wav = OUT/f'audio/page{sid}.wav'
        digest = hashlib.sha256(wav.read_bytes()).hexdigest()
        cache = OUT/f'asr/page{sid}.json'
        asr = json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else {}
        if asr.get('sha256') != digest:
            if transcriber is None:
                import torch
                from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
                torch.set_num_threads(2)
                name = 'openai/whisper-large-v3-turbo'
                model = AutoModelForSpeechSeq2Seq.from_pretrained(name, dtype=torch.float16,
                    low_cpu_mem_usage=True, attn_implementation='eager').to('cuda:0')
                processor = AutoProcessor.from_pretrained(name)
                transcriber = pipeline('automatic-speech-recognition', model=model,
                    tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor,
                    device='cuda:0', dtype=torch.float16)
            print('ASR page', sid, flush=True)
            raw = transcriber(str(wav), generate_kwargs={'language':'korean','task':'transcribe'}, return_timestamps='word')
            asr = {'sha256':digest, 'text':raw['text'], 'words':raw['chunks']}
            dump(cache, asr)
        expected = norm(''.join(lines))
        observed = ''.join(norm(w['text']) for w in asr['words'])
        match = difflib.SequenceMatcher(None, expected, observed, autojunk=False)
        score = match.ratio()
        if score < .85:
            raise ValueError(f'ASR mismatch {sid}: {score:.3f}: {asr["text"]}')
        char_times = []
        for w in asr['words']:
            a,b = w['timestamp']
            if a is None or b is None: raise ValueError('Missing word timestamp')
            char_times.extend([(a,b)]*len(norm(w['text'])))
        mapping = {}
        for block in match.get_matching_blocks():
            for k in range(block.size): mapping[block.a+k] = block.b+k
        def char_time(index, end=False):
            nearest = min(mapping, key=lambda k:abs(k-index))
            return char_times[mapping[nearest]][1 if end else 0]
        normalized = OUT/f'audio/page{sid}-normalized.wav'
        run('ffmpeg','-v','error','-y','-i',str(wav),'-af','loudnorm=I=-16:TP=-2:LRA=7',
            '-ar',str(rate),'-ac','2',str(normalized))
        samples,sr = sf.read(normalized, dtype='float32', always_2d=True)
        leading = .35
        frames = math.ceil((leading+len(samples)/sr+.8)*60)
        segment = np.zeros((frames*800,2),dtype=np.float32)
        first = round(leading*rate)
        # Six-millisecond edge fade does not remove any spoken samples.
        fade = min(round(.006*rate),len(samples)//2)
        samples[:fade] *= np.linspace(0,1,fade)[:,None]
        samples[-fade:] *= np.linspace(1,0,fade)[:,None]
        segment[first:first+len(samples)] = samples
        audio.append(segment)
        cursor=0; cues=[]
        for i,line in enumerate(lines):
            length=len(norm(line))
            start=max(leading,leading+char_time(cursor)-.06)
            end=min(frames/60-.2,leading+char_time(cursor+length-1,True)+.08)
            if cues: cues[-1]['end']=min(cues[-1]['end'],start)
            display=line.replace('큐','Q').replace('케이','K').replace('브이','V').replace('삼차원','3차원')
            cues.append({'start':start,'end':end,'ko':display,'en':EN[sid][i]})
            cursor+=length
        for cue in cues:
            captions.append({**cue,'start':cue['start']+frame_cursor/60,'end':cue['end']+frame_cursor/60,'page':int(sid)})
        emphasis=[]
        if sid=='14':
            emphasis=[{'key':key,'time':leading+char_time(expected.index(norm(term)))}
                      for key,term in [('Q','큐는'),('K','케이는'),('V','브이는')]]
        scenes.append({'id':sid,'sourcePage':int(sid),'title':item['title'], 'frames':frames,
            'duration':frames/60,'firstFrame':frame_cursor,'cues':cues,'audioMeasured':True,'emphasis':emphasis})
        reports.append({'page':int(sid),'similarity':score,'expected':' '.join(lines),'recognized':asr['text'],
                        'audioSha256':digest,'sourceDuration':len(samples)/sr})
        frame_cursor+=frames
    raw_mix=OUT/'audio/preview-unmastered.wav'
    sf.write(raw_mix,np.concatenate(audio),rate,subtype='PCM_16')
    measurement=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw_mix),'-af',
        'loudnorm=I=-16:TP=-2:LRA=7:print_format=json','-f','null','-'],
        check=True,capture_output=True,text=True,encoding='utf-8')
    levels=json.loads(measurement.stderr[measurement.stderr.rfind('{'):measurement.stderr.rfind('}')+1])
    filt=('loudnorm=I=-16:TP=-2:LRA=7:linear=true:'
          f'measured_I={levels["input_i"]}:measured_TP={levels["input_tp"]}:'
          f'measured_LRA={levels["input_lra"]}:measured_thresh={levels["input_thresh"]}:'
          f'offset={levels["target_offset"]}')
    run('ffmpeg','-v','error','-y','-i',str(raw_mix),'-af',filt,'-ar',str(rate),'-c:a','pcm_s16le',str(ASSETS/'preview-narration.wav'))
    dump(OUT/'audio/mastering.json',{'method':'two-pass-loudnorm','targetI':-16,'targetTP':-2,'firstPass':levels,'bgm':False})
    run('ffmpeg','-v','error','-y','-i',str(ASSETS/'preview-narration.wav'),'-c:a','aac','-b:a','192k',str(ASSETS/'preview-narration.m4a'))
    data={'kind':'three-page-excerpt-not-full-episode','fps':60,'totalFrames':frame_cursor,
          'duration':frame_cursor/60,'scenes':scenes,'captions':captions,'bgm':None,'humanVoiceApproval':False}
    dump(ASSETS.parent/'timing.generated.json',data)
    dump(OUT/'asr-review.json',{'scenes':reports,'humanApproval':False})
    for lang in ['ko','en']:
        text='\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}' for i,c in enumerate(captions))+'\n'
        (OUT/f'renderformer-preview-v1.{lang}.srt').write_text(text,encoding='utf-8')
    print(json.dumps({'frames':frame_cursor,'duration':frame_cursor/60,'scenes':len(scenes)},indent=2),flush=True)

if __name__=='__main__': main()
