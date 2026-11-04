"""A02: same speech-window voice/background measurements, not auditory proof."""
import json
import numpy as np
import soundfile as sf
import audio_pipeline as ap
from storage_paths import HERE,LOCAL

def db(x):return float(20*np.log10(max(1e-12,np.sqrt(np.mean(x.astype('float64')**2)))))

def main():
    edit=LOCAL/'edit';build=ap.read(edit/'audio-build.json')
    paths={k:edit/f'{k}-stem.wav' for k in ('narration','music','game')}
    known={r['path']:r['sha256'] for r in build['outputs']}
    for p in paths.values():assert known[ap.relative(p)]==ap.sha(p)
    rows=[];flags=[]
    with sf.SoundFile(paths['narration']) as v,sf.SoundFile(paths['music']) as m,sf.SoundFile(paths['game']) as g:
        rate=v.samplerate;assert rate==m.samplerate==g.samplerate==48000
        for scene in build['scenes']:
            recognition=ap.read(LOCAL/f"voice/asr/{scene['scene']}.json")
            n=scene['sourceSamples'];offset=scene['voiceStartSample']
            mask=ap.mask_words(n,rate,recognition['words'])
            for f in (v,m,g):f.seek(offset)
            voice=v.read(n,dtype='float32');music=m.read(n,dtype='float32');game=g.read(n,dtype='float32')
            for start in range(0,n,rate//2):
                end=min(n,start+rate);active=mask[start:end]
                if active.sum()<rate//4:continue
                vd=db(voice[start:end][active]);md=db(music[start:end][active]);gd=db(game[start:end][active]);bd=db((music[start:end]+game[start:end])[active])
                row={'scene':scene['scene'],'sceneLocalStart':start/rate,'timelineStart':(offset+start)/rate,'speechActiveSamples':int(active.sum()),'voiceDbfs':vd,'musicDbfs':md,'gameDbfs':gd,'combinedBackgroundDbfs':bd,'voiceOverBackgroundDb':vd-bd}
                rows.append(row)
                if vd-bd<3:flags.append(row)
    # 3 dB is a diagnostic review trigger, not an audibility acceptance score.
    out=LOCAL/'qa/audio-v1/speech-mix-balance.json'
    ap.save(out,{'status':'needs-contextual-listening' if flags else 'no-background-dominance-trigger','inputs':[ap.artifact(edit/'audio-build.json'),*[ap.artifact(p) for p in paths.values()]],'scope':'Identical speech-active masks, one-second windows at 0.5-second stride; background is actual summed game+music stems. Threshold is a diagnostic trigger only; spectral masking, word intelligibility, artistic balance and pronunciation still require listening.','diagnosticThresholdVoiceOverBackgroundDb':3,'windows':rows,'flags':flags,'minimumVoiceOverBackgroundDb':min(r['voiceOverBackgroundDb'] for r in rows),'actualListeningPerformed':False,'reviewedAt':ap.now()})
    print(json.dumps({'status':'needs-contextual-listening' if flags else 'no-background-dominance-trigger','windows':len(rows),'minimumVoiceOverBackgroundDb':min(r['voiceOverBackgroundDb'] for r in rows),'flags':flags},ensure_ascii=False))

if __name__=='__main__':main()
