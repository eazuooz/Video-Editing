"""Trim silence, verify new speech, and align only the changed bilingual sentences."""
import hashlib
import os
from pathlib import Path
import re
import sys
from difflib import SequenceMatcher

from prepare import BATCH,HERE,ROOT,WORK,VOICE_LOCAL,read,save
from finish_episode import sha


def main():
    os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',CUDA_VISIBLE_DEVICES='-1')
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
    sys.path.insert(0,str(BATCH/'contrast-v5/review-notes-20261110'))
    from read_observations import initialize,norm
    sys.path.insert(0,str(ROOT/'projects/animation-breaking-down-attack-animations/production/grid-v1'))
    import caption_pipeline
    recognize=None
    records=read(HERE/'narration-patches.json')['records']
    for r in records:
        raw=VOICE_LOCAL/'patch-voice/chunks'/(r['id']+'-scene.wav')
        samples,rate=sf.read(raw,dtype='float32')
        assert samples.ndim==1 and np.isfinite(samples).all()
        active=np.flatnonzero(abs(samples)>=max(abs(samples))*.018)
        assert len(active)
        a=max(0,active[0]-round(.04*rate));b=min(len(samples),active[-1]+round(.09*rate))
        trimmed=VOICE_LOCAL/'patch-voice/trimmed'/raw.name
        trimmed.parent.mkdir(parents=True,exist_ok=True)
        sf.write(trimmed,samples[a:b],rate,subtype='PCM_16')
        duration=(b-a)/rate
        available=r['end']-r['start']
        assert duration+.04<=available,(r['id'],'retake naturally; no time compression',duration,available)
        proof=VOICE_LOCAL/'patch-voice/asr'/(r['id']+'.json')
        digest=sha(trimmed)
        if not proof.exists() or read(proof).get('audio_sha256')!=digest:
            if recognize is None: recognize=initialize()
            result=recognize(str(trimmed),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word',batch_size=1)
            save(proof,{'audio_sha256':digest,'text':result['text'],'words':result['chunks'],'humanListened':False})
        recognized=read(proof)['text']
        score=SequenceMatcher(None,norm(r['ko']),norm(recognized)).ratio()
        assert score>=.92,(r['id'],score,recognized,r['ko'])
        r.update(audioFile=str(trimmed),asrFile=str(proof),audioSha256=digest,voiceSeconds=duration,
                 rawAudioSha256=sha(raw),voiceAt=r['start']+.02,recognized=recognized,readbackScore=score)
        print(r['id'],round(duration,3),round(score,3),recognized,flush=True)
    save(WORK/'narration-patches-checked.json',{'records':records,'humanListened':False})
    for ep in dict.fromkeys(r['episode'] for r in records):
        folder=WORK/ep/'patch-captions'
        base=next(e['baseline'] for e in read(HERE/'plan.json')['episodes'] if e['id']==ep)
        def routed(value):
            path=Path(value).resolve();assert path.is_relative_to(folder.resolve());return path
        caption_pipeline.routed_write_path=routed
        paragraphs=[]
        for r in records:
            if r['episode']!=ep:continue
            paragraphs.append({'id':r['id'],'scene':'native-animation','start':r['voiceAt'],'duration':r['voiceSeconds'],
                'ko':r['ko'],'en':r['en'],'audioFile':r['audioFile'],'asrFile':r['asrFile'],
                'captionUnits':[{'ko':r['ko'],'en':r['en'],'twoLineReason':'Keep the complete corrected demonstration sentence and its visible action together.'}]})
        paragraphs.sort(key=lambda p:p['start'])
        caption_pipeline.build({'fps':60,'bodyEndFrame':base['frames']-600,'paragraphs':paragraphs},folder)
    print('All new demonstration sentences fit naturally and have aligned bilingual captions.',flush=True)


if __name__=='__main__':main()
