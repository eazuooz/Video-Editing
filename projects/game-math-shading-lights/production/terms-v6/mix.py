"""Fit the eight complete replacement sentences in their original narration's breathing gaps."""
import os
os.environ.setdefault('CUDA_VISIBLE_DEVICES','-1')
import subprocess
import numpy as np
import soundfile as sf
from voice import WORK,VOICE,read,write

RATE=48000
BASE=WORK.parent/'render-v4/composite'
def ff(args, data=None):
    return subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',*map(str,args)],input=data,stdout=subprocess.PIPE,check=True,creationflags=subprocess.CREATE_NO_WINDOW).stdout
def quiet(audio,guess,beginning,low,high):
    left=max(low,guess-(.26 if beginning else .1))
    right=min(high,guess+(.10 if beginning else .28))
    left=int(left*RATE);right=max(left+800,int(right*RATE))
    audio.seek(max(0,left-300));sig=audio.read(right-left+600,dtype='float32').mean(axis=1)
    candidates=list(range(0,right-left,96))
    costs=[np.sqrt(np.mean(sig[j:j+600]**2)+1e-13)+.006*abs((left+j)/RATE-guess) for j in candidates]
    return left+candidates[int(np.argmin(costs))]
def active_edges(samples,rate):
    hop=max(1,round(.008*rate));chunk=len(samples)//hop
    energies=np.sqrt(np.mean(samples[:chunk*hop].reshape(chunk,hop)**2,axis=1))
    gate=max(.002,energies.max()*.045);active=np.where(energies>gate)[0]
    assert len(active)>0
    return max(0,(active[0]-2)*hop),min(len(samples),(active[-1]+3)*hop)
def voiced_level(x):
    hop=480;usable=len(x)//hop*hop
    rms=np.sqrt(np.mean(x[:usable].reshape(-1,hop)**2,axis=1)+1.e-12)
    return float(np.median(rms[rms>max(.004,float(rms.max())*.12)]))
def run():
    out=VOICE/'patched-whole.wav'
    # Create a plain float WAV; libsndfile cannot update FFmpeg's LIST-tagged header in place.
    with sf.SoundFile(BASE/'whole-mix.wav') as old, sf.SoundFile(out,'w',samplerate=old.samplerate,channels=old.channels,subtype='FLOAT') as result:
        for samples in old.blocks(blocksize=262144,dtype='float32'):
            result.write(samples)
    tasks=read(VOICE/'sentences.json')
    with sf.SoundFile(BASE/'narration-normalized.wav') as narr, sf.SoundFile(out,'r+') as master:
        assert narr.samplerate==master.samplerate==RATE and narr.channels==master.channels==2
        for t in tasks:
            t['beginSample']=quiet(narr,t['start'],True,t['paragraphStart'],t['paragraphEnd'])
            t['endSample']=quiet(narr,t['end'],False,t['paragraphStart'],t['paragraphEnd'])
        for a,b in zip(tasks,tasks[1:]):
            if a['endSample']>b['beginSample']:
                seam=(a['endSample']+b['beginSample'])//2;a['endSample']=b['beginSample']=seam
        for t in tasks:
            src=VOICE/'chunks'/(t['id']+'-01-scene.wav')
            raw,sr=sf.read(src,dtype='float32');assert raw.ndim==1
            ib,ie=active_edges(raw,sr);x=raw[ib:ie];t0,t1=t['beginSample'],t['endSample'];n=t1-t0
            margin=int(.026*RATE); ratio=len(x)/sr/((n-2*margin)/RATE)
            assert .65<ratio<1.4,(t['id'],ratio)
            dynamic=ff(['-f','f32le','-ar',sr,'-ac',1,'-i','-','-af',f'atempo={ratio:.9f},aresample=48000','-ar',RATE,'-ac',1,'-f','f32le','-'],x.tobytes())
            stretched=np.frombuffer(dynamic,np.float32)
            fresh=np.zeros(n,np.float32)
            count=min(n-margin,len(stretched));fresh[margin:margin+count]=stretched[:count]
            narr.seek(t0);original=narr.read(n,dtype='float32')
            gain=voiced_level(original.mean(axis=1))/voiced_level(fresh)
            fresh*=min(gain,.92/max(.001,np.max(np.abs(fresh))))
            # Crossfade only at selected low-energy joins. Original game-bed samples retain their mix.
            fade=np.clip(np.minimum(np.arange(n),np.arange(n)[::-1])/(.012*RATE),0,1)[:,None]
            master.seek(t0+2*RATE);old=master.read(n,dtype='float32')
            new=old+fade*(fresh[:,None]-original)
            master.seek(t0+2*RATE);master.write(new)
            sf.write(VOICE/(t['id']+'-fitted.wav'),fresh,RATE,subtype='PCM_24')
            t.update(take=str(src),tempo=round(ratio,5),gain=round(float(gain),4),duration=n/RATE,marginSeconds=margin/RATE,oldVoiceRms=float(np.sqrt(np.mean(original**2))),peak=float(np.max(np.abs(new))))
    ff(['-i',out,'-af','aresample=192000,alimiter=limit=0.831764:level=false:latency=true,aresample=48000','-ar',RATE,'-ac',2,'-c:a','aac','-b:a','192k',VOICE/'pair-audio.m4a'])
    write(VOICE/'mix.json',tasks)
if __name__=='__main__':run()
