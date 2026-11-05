"""New shot offsets from natural speech lengths. Keep V6 audio sample-for-sample outside revised shots."""
import json,math,wave
from pathlib import Path
from narration import LESSONS
BASE=Path(__file__).resolve().parents[2]/'production/local'
WORK=BASE/'render-v7';VOICE=WORK/'speech'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def construct():
    cuts=read(BASE/'render-v4/queue.json')['cuts'];rows=[];frame=120
    for i,c in enumerate(cuts):
        sid=int(c['scene']);changed=sid in LESSONS and c['kind']=='explanation';n=c['frames']
        if changed:
            with wave.open(str(VOICE/'chunks'/f'{sid:03}-scene.wav')) as inp:duration=inp.getnframes()/inp.getframerate()
            n=math.ceil((duration+.16)*60)
        rows.append(dict(i=i,sid=sid,kind=c['kind'],oldStart=120+c['globalStartFrame'],oldFrames=c['frames'],start=frame,frames=n,newSpeech=changed));frame+=n
    write(WORK/'timeline.json',rows);return rows
def mix():
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
    import subprocess
    rate=48000;rows=construct();receipts=[]
    source=BASE/'render-v6/voice/patched-whole.wav';bedfile=BASE/'render-v4/composite/game-bed.wav'
    def level(wav):
        usable=len(wav)//480*480;rms=np.sqrt(np.mean(wav[:usable].reshape(-1,480)**2,axis=1)+1e-12)
        return float(np.median(rms[rms>max(.004,float(rms.max())*.12)]))
    with sf.SoundFile(source) as src,sf.SoundFile(bedfile) as bed,sf.SoundFile(VOICE/'whole.wav','w',samplerate=rate,channels=2,subtype='FLOAT') as out:
        assert src.samplerate==bed.samplerate==rate
        src.seek(0);out.write(src.read(120*800,dtype='float32'))
        for r in rows:
            src.seek(r['oldStart']*800);old=src.read(r['oldFrames']*800,dtype='float32')
            if not r['newSpeech']:out.write(old);continue
            bed.seek((r['oldStart']-120)*800);amb=bed.read(len(old),dtype='float32')
            assert np.max(np.abs(amb))<.0001,(r['sid'],'non-silent game bed requires retention')
            raw,sr=sf.read(VOICE/'chunks'/f'{r["sid"]:03}-scene.wav',dtype='float32')
            sig=resample_poly(raw,rate//math.gcd(rate,sr),sr//math.gcd(rate,sr))
            gain=min(level(old.mean(axis=1))/level(sig),.92/max(.001,abs(sig).max()))
            sig*=gain
            fade=min(len(sig)//2,480);sig[:fade]*=np.linspace(0,1,fade);sig[-fade:]*=np.linspace(1,0,fade)
            new=np.zeros(r['frames']*800,np.float32);at=round(.06*rate);new[at:at+len(sig)]=sig
            out.write(np.repeat(new[:,None],2,axis=1))
            receipts.append(dict(scene=r['sid'],seconds=len(sig)/rate,tempo=1,linearGain=float(gain),originalBedPeak=float(np.max(abs(amb)))))
        src.seek(-600*800,2);out.write(src.read(600*800,dtype='float32'))
    dest=VOICE/'pair.m4a';subprocess.run(['ffmpeg','-nostdin','-hide_banner','-y','-v','error','-i',str(VOICE/'whole.wav'),'-af','aresample=192000,alimiter=limit=0.831764:level=false:latency=true,aresample=48000','-ac','2','-ar','48000','-c:a','aac','-b:a','192k',str(dest)],check=True)
    write(WORK/'mix.json',receipts)
if __name__=='__main__':mix()
