"""One finite30.2s mix from retained approved PCM; never generates TTS.

Constant speech gain is measured after duplication to the final stereo layout.
Only music is voice-ducked. Final peak limiting is brief protection, not adaptive
speech normalization. This script must be called after the parent's handoff.
"""
from __future__ import annotations
import argparse,json,math,re,subprocess
from pathlib import Path
import numpy as np
from importlib.util import spec_from_file_location,module_from_spec

spec=spec_from_file_location('portrait_renderer',Path(__file__).with_name('render-short.py'))
renderer=module_from_spec(spec);spec.loader.exec_module(renderer)
R,P,O=renderer.ROOT,renderer.PROJECT,renderer.OUT
RATE,SECONDS,VOICE_END=48000,30.2,30.1

def loudness(path):
    args=[renderer.FFMPEG,'-hide_banner','-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']
    result=renderer.run(args);matches=re.findall(r'\{\s*"input_i"[\s\S]*?\}',result.stderr.decode(errors='replace'))
    assert matches,'Missing measured loudness';return json.loads(matches[-1])
def read_exact(path,rate=RATE,channels=2,duration=None):
    args=[renderer.FFMPEG,'-v','error','-i',str(path),'-vn']
    if duration is not None:args+=['-t',str(duration)]
    args+=['-ar',str(rate),'-ac',str(channels),'-f','f32le','pipe:1']
    return np.frombuffer(renderer.run(args).stdout,dtype='<f4').reshape(-1,channels).copy()
def write_pcm(path,values,rate):
    args=[renderer.FFMPEG,'-v','warning','-n','-f','f32le','-ar',str(rate),'-ac',str(values.shape[1]),'-i','pipe:0','-c:a','pcm_f32le',str(path)]
    renderer.run(args,input=np.asarray(values,dtype='<f4').tobytes())
def windows(values,rate,step=.1,size=.4):
    n,hop=round(size*rate),round(step*rate)
    for i in range(0,len(values)-n+1,hop):
        rms=float(np.sqrt(np.mean(values[i:i+n].astype(np.float64)**2)))
        yield dict(start=i/rate,end=(i+n)/rate,rmsDbfs=20*math.log10(max(rms,1e-12)))
def build():
    renderer.check_render_authorization()
    source=renderer.read(P/'sources/source-map.json');voice=R/source['narration']['path'];music=R/source['music']['path']
    assert renderer.sha(voice)==source['narration']['sha256']
    assert renderer.sha(music)==source['music']['sha256']
    signature=dict(code=renderer.sha(__file__),voice=source['narration']['sha256'],music=source['music']['sha256'],voiceEnd=VOICE_END,seconds=SECONDS,targetSpeechLufs=-16,targetMusicLufs=-31,rate=RATE)
    receipt=O/'audio-build.json';final=O/'final-mix.m4a'
    if receipt.exists() and final.exists():
        old=renderer.read(receipt)
        if old.get('signature')==signature and old['files']['aac']['sha256']==renderer.sha(final):return old
        raise RuntimeError('Existing audio revision differs; preserve it under a distinct revision first.')
    O.mkdir(parents=True,exist_ok=True)
    info=json.loads(renderer.run([renderer.FFPROBE,'-v','error','-show_streams','-of','json',str(voice)]).stdout)
    source_stream=next(x for x in info['streams'] if x['codec_type']=='audio');sr=int(source_stream['sample_rate']);channels=source_stream['channels']
    assert sr==24000 and channels==1,'Inspect approved source layout before any conversion.'
    raw=read_exact(voice,rate=sr,channels=channels,duration=VOICE_END)
    assert raw.shape[0]==round(VOICE_END*sr)
    # Last3ms are already measured below-60dBFS, after the complete final word.
    n=round(.003*sr);raw[-n:]*=np.linspace(1,0,n,dtype=np.float32)[:,None]
    retained=O/'retained-voice-24k.wav';write_pcm(retained,raw,sr)
    prepared=O/'voice-input-stereo.wav'
    renderer.run([renderer.FFMPEG,'-v','warning','-n','-i',str(retained),'-af',f'aresample={RATE},apad=whole_dur={SECONDS},atrim=duration={SECONDS}', '-ar',str(RATE),'-ac','2','-c:a','pcm_f32le',str(prepared)])
    before=loudness(prepared);gain=-16-float(before['input_i'])
    stem=O/'narration-stem.wav'
    # alimiter latency compensation preserves original speech alignment.
    renderer.run([renderer.FFMPEG,'-v','warning','-n','-i',str(prepared),'-af',f'volume={gain:.9f}dB,alimiter=limit=0.841395:attack=5:release=50:level=0:latency=1', '-c:a','pcm_f32le',str(stem)])
    speech=read_exact(stem);count=round(SECONDS*RATE);assert len(speech)==count
    bgm_unscaled=O/'music-input.wav'
    renderer.run([renderer.FFMPEG,'-v','warning','-n','-stream_loop','-1','-i',str(music),'-t',str(SECONDS),'-ar',str(RATE),'-ac','2','-c:a','pcm_f32le',str(bgm_unscaled)])
    music_before=loudness(bgm_unscaled);music_gain=-31-float(music_before['input_i']);bgm=read_exact(bgm_unscaled)[:count]*10**(music_gain/20)
    assert len(bgm)==count
    #100ms RMS envelope with80ms attack/500ms recovery. Only BGM changes gain.
    sample_times=np.arange(count)/RATE
    window_rows=list(windows(speech,RATE,.1,.1));centers=np.array([(x['start']+x['end'])/2 for x in window_rows])
    active=np.array([1.0 if x['rmsDbfs']>-43 else 0.0 for x in window_rows])
    target=np.interp(sample_times,centers,active,left=active[0],right=active[-1]);smooth=np.empty_like(target);level=target[0]
    attack=math.exp(-1/(.08*RATE));release=math.exp(-1/(.5*RATE))
    for i,value in enumerate(target):
        coefficient=attack if value>level else release;level=coefficient*level+(1-coefficient)*value;smooth[i]=level
    duck=10**((-4*smooth)/20)
    fade=np.ones(count,dtype=np.float64);fade[:round(.18*RATE)]=np.linspace(0,1,round(.18*RATE));fade[-round(.22*RATE):]=np.linspace(1,0,round(.22*RATE))
    bgm=bgm*(duck*fade)[:,None];music_stem=O/'music-stem.wav';write_pcm(music_stem,bgm,RATE)
    unprotected=O/'mix-before-peak-protection.wav';write_pcm(unprotected,speech+bgm,RATE)
    final_wav=O/'final-mix.wav'
    renderer.run([renderer.FFMPEG,'-v','warning','-n','-i',str(unprotected),'-af','alimiter=limit=0.803526:attack=5:release=50:level=0:latency=1','-c:a','pcm_f32le',str(final_wav)])
    renderer.run([renderer.FFMPEG,'-v','warning','-n','-i',str(final_wav),'-c:a','aac','-b:a','192k','-ar',str(RATE),'-ac','2',str(final)])
    measurements=dict(sourceStereo=before,narration=loudness(stem),musicInput=music_before,finalWav=loudness(final_wav),encoded=loudness(final))
    assert float(measurements['encoded']['input_tp'])<=-1.5,'Encoded true peak exceeds ceiling; retain current evidence and adjust only peak protection.'
    assert -17.5<=float(measurements['narration']['input_i'])<=-14.5,'Inspect speech gain; do not hide an unexpected voice-level shift.'
    encoded=read_exact(final)[:count];sw=list(windows(speech,RATE));ew=list(windows(encoded,RATE));transfers=[]
    for a,b in zip(sw,ew):
        if a['rmsDbfs']>-43:transfers.append(dict(start=a['start'],end=a['end'],stemDbfs=a['rmsDbfs'],encodedDbfs=b['rmsDbfs'],deltaDb=b['rmsDbfs']-a['rmsDbfs']))
    flags=[x for x in transfers if x['deltaDb']<-2.5]
    report=dict(signature=signature,files={name:dict(path=renderer.rel(path),sha256=renderer.sha(path),bytes=path.stat().st_size) for name,path in [('retained',retained),('narration',stem),('music',music_stem),('wav',final_wav),('aac',final)]},constantNarrationGainDb=gain,initialMusicGainDb=music_gain,voiceDuckApplied=False,musicDuckDb=[-4,0],musicWorkingLufs=-31,originalGameAudioIncluded=False,foreignCommentaryIncluded=False,sourceCutSeconds=VOICE_END,postSourceSilenceSeconds=.1,declickLastSeconds=.003,measurements=measurements,speechActiveTransferWindows=transfers,flaggedTransferWindows=flags,wholeFinalMixAsr='pending-one-current-pass',humanListening='pending',sourceUnmodifiedPcmPreserved=True)
    renderer.write(receipt,report);return report
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build',action='store_true');args=parser.parse_args()
    if not args.build:parser.error('--build required; importing does not start media work')
    report=build();print(json.dumps(dict(path=report['files']['aac']['path'],flaggedWindows=len(report['flaggedTransferWindows']),newTtsJobs=0)))
if __name__=='__main__':main()
