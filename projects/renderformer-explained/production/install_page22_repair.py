"""Verify replacement speech, preserve old takes, and keep all page boundaries fixed."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import numpy as np
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from prepare_full import norm, stamp, dump, run

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/renderformer-explained'
BASE=PROJECT/'production/body-review'
MC=ROOT/'motion-canvas/src/projects/renderformer-explained/full/narrated'
raw=ROOT/'shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v2-repair/22-scene.wav'
timing=json.loads((BASE/'timing.json').read_text(encoding='utf-8'))
scene=timing['scenes'][21]
target=scene['duration']-.35-.8
ratio=sf.info(raw).duration/target
if not .9<=ratio<=1.1:raise ValueError(f'Retake differs too much for subtle duration matching: {ratio}')
adjusted=BASE/'page22-normalized-v2.wav'
run('ffmpeg','-v','error','-y','-i',str(raw),'-af',f'atempo={ratio:.12f},loudnorm=I=-16:TP=-2:LRA=7,apad,atrim=duration={target}',
 '-ar','48000','-ac','2',str(adjusted))
torch.set_num_threads(4)
name='openai/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(name,dtype=torch.float16,low_cpu_mem_usage=True,attn_implementation='eager').to('cuda')
p=AutoProcessor.from_pretrained(name)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,device=0,dtype=torch.float16)
recognized=asr(str(adjusted),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
dump(BASE/'page22-asr-v2.json',recognized)
print(recognized['text'],flush=True)
if not any(prefix in recognized['text'][:20] for prefix in ['지금까지는','여기까지는']):
    raise ValueError('Replacement still has suspect opening; do not install')
# The replacement says the synonymous 여기까지는. Keep captions faithful to
# the observed complete opening; the original approved script/take is preserved.
opening='여기까지는' if '여기까지는' in recognized['text'][:20] else '지금까지는'
scene['cues'][0]['ko']=scene['cues'][0]['ko'].replace('지금까지는',opening,1)
expected=norm(''.join(c['ko'] for c in scene['cues']))
observed=''.join(norm(w['text']) for w in recognized['chunks'])
matcher=difflib.SequenceMatcher(None,expected,observed,autojunk=False)
if matcher.ratio()<.90:raise ValueError('Replacement needs manual ASR review')
mapping={}
for b in matcher.get_matching_blocks():mapping.update({b.a+k:b.b+k for k in range(b.size)})
times=[]
for w in recognized['chunks']:
    if None in w['timestamp']:raise ValueError('Invalid word timestamps')
    times.extend([w['timestamp']]*len(norm(w['text'])))
def char_time(i,end=False):return times[mapping[min(mapping,key=lambda k:abs(k-i))]][int(end)]
offset=0;local=[]
for old in scene['cues']:
    length=len(norm(old['ko']))
    start=max(.35,.35+char_time(offset)-.04)
    end=min(scene['duration']-.2,.35+char_time(offset+length-1,True)+.06)
    if local:
        start=max(start,local[-1]['start']+.08);local[-1]['end']=min(local[-1]['end'],start)
    if end<=start:raise ValueError('Invalid replacement cue')
    local.append({**old,'start':start,'end':end});offset+=length
# Preserve every original input and revision; output filenames are controlled here.
for name in ['timing.json','renderformer.ko.srt','renderformer.en.srt']:
    before=BASE/name;backup=BASE/(before.stem+'.before-page22-repair'+before.suffix)
    if backup.exists():raise FileExistsError('Repair already applied or interrupted: '+str(backup))
    shutil.copy2(before,backup)
scene['cues']=local
new_captions=[]
for s in timing['scenes']:
    new_captions.extend({**c,'start':c['start']+s['firstFrame']/60,'end':c['end']+s['firstFrame']/60,'page':s['sourcePage']} for c in s['cues'])
timing['captions']=new_captions;timing['englishStatus']='translated-regenerate-for-page22-timing'
segment=np.zeros((scene['frames']*800,2),dtype=np.float32)
samples,sr=sf.read(adjusted,dtype='float32',always_2d=True)
edge=288;samples[:edge]*=np.linspace(0,1,edge)[:,None];samples[-edge:]*=np.linspace(1,0,edge)[:,None]
segment[16800:16800+len(samples)]=samples
replacement=BASE/'body-unmastered-v2.wav'
with sf.SoundFile(BASE/'body-unmastered.wav') as src,sf.SoundFile(replacement,'w',samplerate=48000,channels=2,subtype='PCM_16') as dest:
    for s in timing['scenes']:
        original=src.read(s['frames']*800,dtype='float32',always_2d=True)
        dest.write(segment if s['sourcePage']==22 else original)
measurement=run('ffmpeg','-hide_banner','-nostats','-i',str(replacement),'-af','loudnorm=I=-16:TP=-2:LRA=7:print_format=json','-f','null','-')
levels=json.loads(measurement.stderr[measurement.stderr.rfind('{'):measurement.stderr.rfind('}')+1])
filt=('loudnorm=I=-16:TP=-2:LRA=7:linear=true:'+f'measured_I={levels["input_i"]}:measured_TP={levels["input_tp"]}:'+f'measured_LRA={levels["input_lra"]}:measured_thresh={levels["input_thresh"]}:offset={levels["target_offset"]}')
run('ffmpeg','-v','error','-y','-i',str(replacement),'-af',filt,'-ar','48000','-c:a','pcm_s16le',str(BASE/'narration-mastered-v2.wav'))
run('ffmpeg','-v','error','-y','-i',str(BASE/'narration-mastered-v2.wav'),'-c:a','aac','-b:a','192k',str(BASE/'narration-mastered-v2.m4a'))
for ext in ['wav','m4a']:
    shutil.copy2(BASE/f'narration-mastered.{ext}',BASE/f'narration-mastered-before-page22-repair.{ext}')
    shutil.copy2(BASE/f'narration-mastered-v2.{ext}',BASE/f'narration-mastered.{ext}')
dump(BASE/'timing.json',timing);dump(MC/'timing.generated.json',timing)
shutil.copy2(BASE/'narration-mastered.wav',MC/'narration.wav')
(BASE/'renderformer.ko.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["ko"]}' for i,c in enumerate(new_captions))+'\n',encoding='utf-8')
dump(BASE/'page22-repair.json',{'page':22,'rawTake':str(raw.relative_to(ROOT)),'atempo':ratio,'pageFramesUnchanged':scene['frames'],
 'totalFramesUnchanged':timing['totalFrames'],'asr':recognized['text'],'similarity':matcher.ratio(),
 'reason':'Two independent ASR passes omitted the opening 지금 on v1; full scene regenerated using the same approved script. The complete synonymous opening 여기까지는 is preserved in the active Korean caption.',
 'humanListeningApproved':False,'mastering':levels})
print('Replacement installed in audio and timing. Remux clean video; regenerate both SRT and caption overlays.',flush=True)
