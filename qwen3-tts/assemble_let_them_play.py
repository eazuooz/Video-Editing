"""Assemble continuous approved takes; keep exact 1:1:1 picture sections.

Does not resynthesize, stretch speech, or add silent slots before examples.
Run review_project_narration.py first, then align_project_subtitles.py afterwards.
"""
import csv, json, math, hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
from align_project_subtitles import align_characters

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'projects/let-them-play'
m=json.loads((P/'project.json').read_text(encoding='utf-8'))
assert m['approvals']['voice'].startswith('approved')
script=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))
out=ROOT/m['tts']['outputDir']; stem=m['tts']['filenameStem']; fps=m['video']['fps']
chunks=[]; entries=[]; scenes=[]; cursor=0; rate=None
for s in script['scenes']:
    file=out/'chunks'/f"{s['id']}-scene.wav"
    audio,sr=sf.read(file,dtype='float32'); rate=rate or sr
    assert rate==sr and audio.ndim==1
    asr=json.loads((out/'asr'/f"{s['id']}.json").read_text(encoding='utf-8'))
    assert hashlib.sha256(file.read_bytes()).hexdigest()==asr['audio_sha256']
    begin,end,coverage=align_characters(' '.join(s['lines']),asr['words'],len(audio)/sr)
    # Quantize each third, not each paragraph. Speech remains continuous.
    third=math.ceil((len(audio)/sr+m['tts']['sceneGapSeconds'])*fps/3)
    frames=third*3; origin=cursor/fps
    sample_count=round(frames/fps*sr)
    n=min(round(.006*sr),len(audio)//2)
    audio[:n]*=np.linspace(0,1,n); audio[-n:]*=np.linspace(1,0,n)
    chunks.append(np.pad(audio,(0,sample_count-len(audio))))
    from align_project_subtitles import normalized
    c=0; boundaries=[]
    for i,line in enumerate(s['lines']):
        length=len(normalized(line)); a=float(begin[c]); b=float(end[c+length-1])
        entries.append({'index':len(entries)+1,'scene_id':s['id'],'scene_title':s['title'],
                        'text':line,'start':origin if i==0 else origin+a,'voice_start':origin+a,'end':origin+b})
        if i in (2,4): boundaries.append(a)
        c+=length
    offsets=[round(boundaries[k]-(k+1)*third/fps,3) for k in range(2)]
    if max(abs(x) for x in offsets)>6:
        raise ValueError(f"Scene {s['id']}: narration/third transition differs by >6s: {offsets}; editorial review required")
    scenes.append({'id':s['id'],'startFrame':cursor,'frames':frames,'segmentFrames':third,
                   'voiceSeconds':len(audio)/sr,'asrCoverage':coverage,'paragraphTransitionOffsetsSeconds':offsets})
    cursor+=frames
credits_frames=0
chunks.append(np.zeros(round(credits_frames/fps*rate),dtype=np.float32))
sf.write(out/f'{stem}.wav',np.concatenate(chunks),rate)
timing={'sample_rate':rate,'duration_seconds':(cursor+credits_frames)/fps,'render_mode':'scene',
        'example_seconds':m['editing']['exampleSeconds'],'narration_placement':m['editing']['narrationPlacement'],
        'entries':entries,'visualTiming':scenes,'creditsSeconds':0}
(out/f'{stem}.timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
visual={'fps':fps,'scenes':scenes,'contentFrames':cursor,'creditsFrames':credits_frames,'totalFrames':cursor+credits_frames,'voiceAligned':True,
        'policy':'Continuous natural-speed takes, equal picture thirds per chapter, frame-quantized chapter breaths; ASR offsets recorded explicitly.'}
(ROOT/'motion-canvas/src/projects/let-them-play/timeline.generated.json').write_text(json.dumps(visual,indent=2)+'\n',encoding='utf-8')
# Regenerate editing cues and publishing chapter times from the same frame grid.
with (P/'planning/edit-cues.measured.csv').open('w',encoding='utf-8',newline='') as handle:
    writer=csv.writer(handle); writer.writerow(['scene','segment','start_seconds','end_seconds','frames'])
    for s in scenes:
        for k,kind in enumerate(m['editing']['segmentOrder']):
            writer.writerow([s['id'],kind,(s['startFrame']+k*s['segmentFrames'])/fps,(s['startFrame']+(k+1)*s['segmentFrames'])/fps,s['segmentFrames']])
for lang in ('ko','en'):
    narration=json.loads((P/f'script/narration.{lang}.json').read_text(encoding='utf-8'))
    lines=[]
    for scene,spoken in zip(scenes,narration['scenes']):
        sec=scene['startFrame']//fps
        lines.append(f"{sec//60:02d}:{sec%60:02d} {spoken['title']}")
    (P/f'publishing/chapters.generated.{lang}.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(visual,indent=2))
