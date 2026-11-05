"""Check that all samples outside the approved eight sentence intervals still match the V5 source mix."""
import soundfile as sf
import numpy as np
from voice import WORK,VOICE,read,write
from mix import BASE,RATE

def run():
    tasks=read(VOICE/'mix.json')
    intervals=[(2*RATE+t['beginSample'],2*RATE+t['endSample']) for t in tasks]
    matched=0;seams=[]
    with sf.SoundFile(BASE/'whole-mix.wav') as old, sf.SoundFile(VOICE/'patched-whole.wav') as new:
        assert (len(old),old.samplerate,old.channels)==(len(new),RATE,2)
        start=0
        for a,b in intervals+[(len(new),len(new))]:
            for k in range(start,a,262144):
                n=min(262144,a-k);old.seek(k);new.seek(k)
                assert np.array_equal(old.read(n,dtype='float32'),new.read(n,dtype='float32'))
                matched+=n
            if b<len(new):
                for k in [a,b]:
                    old.seek(k-1);new.seek(k-1);before=old.read(2,dtype='float32');after=new.read(2,dtype='float32')
                    seams.append(float(np.max(abs(np.diff(after,axis=0)-np.diff(before,axis=0)))))
            start=b
    assert max(seams)<.012,seams
    write(VOICE/'pcm-integrity.json',dict(unchangedSampleFrames=matched,changedSentenceIntervals=intervals,maxExcessSeamStep=max(seams),sampleRate=RATE))
if __name__=='__main__':run()
