"""Ease the music bed under the soft last phrase and recover during the silent credit."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np,soundfile as sf


def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def balance(directory,plan):
    src=directory/'final-mix.wav'; stem=directory/'narration-stem.wav'
    receipt=directory/'coda-music-balance.json'
    signature=digest(src)
    if receipt.exists() and json.loads(receipt.read_text(encoding='utf-8'))['balancedMixSha256']==signature:
        return
    scene=plan['scenes'][-1]
    assert scene['id']=='17' and scene['duration']==31.92
    origin=2+scene['voiceStart']
    begin=origin+28.0; attenuated=origin+28.6
    release=origin+scene['duration'];end=release+1.5
    minimum=10**(-12/20)
    corrected=directory/'final-mix-balanced.tmp.wav'
    with sf.SoundFile(src) as original,sf.SoundFile(stem) as speech,sf.SoundFile(
        corrected,'w',samplerate=48000,channels=2,subtype='PCM_24') as output:
        assert len(original)==len(speech) and original.samplerate==speech.samplerate==48000
        while original.tell()<len(original):
            index=original.tell();raw=original.read(48000,dtype='int32')
            if (index+len(raw))/48000<=begin or index/48000>=end:
                output.write(raw);continue
            speech.seek(index);voice=speech.read(len(raw),dtype='float64')
            mixed=raw.astype('float64')/(2**31)
            t=(index+np.arange(len(raw)))/48000
            down=.5-.5*np.cos(np.pi*np.clip((t-begin)/(attenuated-begin),0,1))
            up=.5-.5*np.cos(np.pi*np.clip((t-release)/(end-release),0,1))
            gain=1-(1-minimum)*down*(1-up)
            output.write(voice+(mixed-voice)*gain[:,None])
    corrected.replace(src)
    receipt.write_text(json.dumps({'unbalancedMixSha256':signature,'balancedMixSha256':digest(src),
        'voiceStemSha256':digest(stem),'gainDbBelowLastPhrase':-12,'begin':begin,'fullyAttenuated':attenuated,
        'releaseStarts':release,'restoredAt':end,'speechStemAppliedGainDb':0,
        'reason':'The last phrase in the final Qwen take decays towards the music bed. Duck only the residual music, then recover over the first 1.5 s of credits.'},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    from edition import LOCAL,EXTENDED
    assert EXTENDED
    archive=LOCAL/'qa/pre-coda-balance';archive.mkdir(parents=True,exist_ok=True)
    if (LOCAL/'audio.m4a').exists() and not (archive/'audio.m4a').exists():
        shutil.copyfile(LOCAL/'audio.m4a',archive/'audio.m4a')
    balance(LOCAL,json.loads((LOCAL/'timeline.json').read_text(encoding='utf-8')))
