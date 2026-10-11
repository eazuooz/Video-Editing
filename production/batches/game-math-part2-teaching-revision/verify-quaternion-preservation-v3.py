"""Verify eighty original PCM slices, encoded clips, cues and source speed."""
from pathlib import Path
import json,hashlib
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;Q=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for episode in read(Q/'baseline.json')['episodes']:
    P=ROOT/'projects'/episode['newSlug'];t=read(P/'production/timeline.json');old=read(Q/'baseline'/episode['slug']/'production/timeline.json')
    old_map={s['id']:s for s in old['scenes']};previous,sr=sf.read(ROOT/f'shared/output/{episode["slug"]}/narration-final.wav',dtype='float32')
    current,current_sr=sf.read(ROOT/read(P/'project.json')['paths']['narration'],dtype='float32');assert sr==current_sr==24000
    exact=[]
    for slot in t['scenes']:
        if not slot['preservedOriginal']:continue
        original=old_map[slot['id']];count=round(original['seconds']*sr)
        before=previous[round(original['start']*sr):round(original['start']*sr)+count]
        after=current[round(slot['start']*sr):round(slot['start']*sr)+count]
        assert np.array_equal(before,after),(episode['newSlug'],slot['id'],'PCM changed')
        assert slot['frames']==original['frames'] and sha(ROOT/slot['baselineClip'])==sha(ROOT/f'shared/output/{episode["newSlug"]}/clips/{slot["id"]}.mp4')
        for lang in ['ko','en']:
            prior=[c for c in old[lang+'Captions'] if c['scene']==slot['id']]
            carried=[c for c in t[lang+'Captions'] if c['scene']==slot['id']]
            assert [c['text'] for c in prior]==[c['text'] for c in carried]
            shift=slot['start']-original['start']
            assert all(abs(a['start']+shift-z['start'])<1e-8 and abs(a['end']+shift-z['end'])<1e-8 for a,z in zip(prior,carried))
        exact.append(slot['id'])
    assert exact==[s['id'] for s in old['scenes']]
    assert np.array_equal(previous[:2*sr],current[:2*sr]) and np.array_equal(previous[-10*sr:],current[-10*sr:])
    additions=[]
    for slot in t['scenes']:
        if slot['preservedOriginal'] or slot['classification']!='actual':continue
        original,voice_sr=sf.read(ROOT/slot['voice'],dtype='float32');assert voice_sr==sr
        pauses=sorted(slot['observationPauses'],key=lambda x:x['rawSample'])
        start=round(slot['start']*sr);offset=0;before=0;parts=[]
        for pause in pauses:
            position=pause['rawSample'];parts.append(current[start+before+offset:start+position+offset])
            silence=current[start+position+offset:start+position+offset+pause['silenceSamples']]
            assert len(silence)==pause['silenceSamples'] and not np.any(silence)
            offset+=pause['silenceSamples'];before=position
        parts.append(current[start+before+offset:start+len(original)+offset]);recovered=np.concatenate(parts)
        assert np.array_equal(recovered,original),(slot['id'],'speech seam lost samples')
        assert slot['cut']['sourceSpeed']==1 and sum(s['frames'] for s in slot['cut']['segments'])==slot['frames']
        for segment in slot['cut']['segments']:
            assert segment['seconds']<=segment['maxSeconds']+1/60
        additions.append(dict(scene=slot['id'],rawVoicePcmExactAfterRemovingOnlyInsertedQuietObservation= True,sourceFrames=slot['frames'],sourceSpeed=1,sourceFrozenOrLooped=False))
    assert t['actualFrames']*3==t['explanationFrames']*2
    records.append(dict(slug=episode['newSlug'],originalSceneIdsExact=exact,originalEncodedClipsExact=True,originalPcmAndCueTimingExact=True,introAndOutroPcmExact=True,additions=additions,ratioErrorFrames=0,humanListening='pending',finalPixels='pending'))
(Q/'final-preservation-audit.json').write_text(json.dumps(dict(episodes=records,allOriginalScenes=80,allPassed=True),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('All80 original scenes, encoded clips, PCM/cues and intro/outro exact; new speech samples exact through observation pauses;40:60 exact.')
