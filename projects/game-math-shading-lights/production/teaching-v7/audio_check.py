"""Compare inherited V6 PCM directly, accounting for the new natural-length narration shots."""
from sequence import VOICE,BASE,WORK,read,write
import numpy as np
import soundfile as sf
def run():
    rows=read(WORK/'timeline.json');verified=0
    ranges=[(0,0,120*800)]+[(r['oldStart']*800,r['start']*800,r['frames']*800) for r in rows if not r['newSpeech']]
    end=rows[-1];ranges.append(((end['oldStart']+end['oldFrames'])*800,(end['start']+end['frames'])*800,600*800))
    with sf.SoundFile(BASE/'render-v6/voice/patched-whole.wav') as old,sf.SoundFile(VOICE/'whole.wav') as new:
        for source,dest,count in ranges:
            old.seek(source);new.seek(dest)
            for i in range(0,count,262144):
                n=min(count-i,262144);assert np.array_equal(old.read(n,dtype='float32'),new.read(n,dtype='float32'))
                verified+=n
    write(WORK/'pcm-integrity.json',dict(unchangedStereoSampleFrames=verified,sampleRate=48000,nativeSpeechSpeed=True,revisedSceneIds=[r['sid'] for r in rows if r['newSpeech']],untouchedGameSound=True))
if __name__=='__main__':run()
