"""Restore standard game sound only; packet-copy both reviewed video streams."""
from pathlib import Path
import json, hashlib, importlib.util, shutil, math, subprocess, sys
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
V3=P/'production/local/revision-v3';O=P/'production/local/revision-v4-clarity';O.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('audio_helpers',P/'production/revision-v2/build-audio.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read=h.read;sha=h.sha;save=h.save;rel=h.relative
def run(args,name):return h.run(args,name,O)
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
selected();t=read(P/'production/revision-v3/timeline.json');old=read(V3/'audio-build.json');frames=t['totalFrames'];duration=frames/60
assert frames==93100 and old['music']['addedBgm'] is False
for name in ['narration-stem.wav','captions.ko.srt','captions.en.srt']:
 dst=O/name
 if not dst.exists():shutil.copy2(V3/name,dst)
 assert sha(dst)==sha(V3/name)
game=np.zeros((frames*800,2),dtype=np.float32);rows=[];cache=O/'game-audio';cache.mkdir(exist_ok=True)
for c in t['cuts']:
 selected();prior=read(V3/'game-audio'/(c['id']+'.json'));raw=V3/'game-audio'/(c['id']+'-raw.wav')
 assert prior['inputs']['sourceSha256']==c['sourceSha256'] and prior['inputs']['frames']==c['frames'] and prior['inputs']['sourceStart']==c['sourceStart']
 stats=prior['measurement'];silent=prior.get('silentSource',False);lufs=float(stats['input_i']);tp=float(stats['input_tp'])
 gain=0. if silent else min(12.,-23-lufs,-6-tp)
 out=cache/(c['id']+'.wav');sig=dict(rawSha256=sha(raw),gameTargetLufs=-23,gainDb=gain,frames=c['frames'],sourceSpeed=1,peakSafetyCeilingDbtp=-6)
 receipt=out.with_suffix('.json')
 if not (out.exists() and receipt.exists() and read(receipt)['inputs']==sig):
  run(['-i',raw,'-af',f'volume={gain}dB:precision=double,afade=t=in:d=0.025,afade=t=out:st={c["seconds"]-.025}:d=0.025','-ar',48000,'-ac',2,'-c:a','pcm_f32le',out],c['id']+'-restore-native')
  save(receipt,dict(inputs=sig,sha256=sha(out)))
 samples,rate=sf.read(out,dtype='float32',always_2d=True);assert rate==48000
 count=c['frames']*800;at=c['globalStartFrame']*800;game[at:at+min(count,len(samples))]=samples[:count]
 rows.append(dict(cut=c['id'],sourceId=c['sourceId'],start=c['globalStartFrame']/60,seconds=c['seconds'],rawSha256=sig['rawSha256'],sourceIntegratedLufs=lufs if math.isfinite(lufs) else None,oldGainDb=prior['gainDb'],gainDb=gain,gameGainChangeDb=gain-prior['gainDb'],nominalPostGainLufs=lufs+gain if math.isfinite(lufs) else None,silentSource=silent,sourceMusicSeparationClaim=False))
 print(c['id'],'native sound restored',round(gain-prior['gainDb'],2),'dB; silent',silent,flush=True)
# Only the new encoded-ASR masking concern in the Zelda definition receives
# a short speech-priority ride. General game sound remains the standard level.
ride=dict(start=1195.55,end=1216.7,fadeSeconds=.3,gainDb=-8,reason='Current mixed ASR obscured length/information words that remain clear in source PCM and previous quieter mix.')
left=round(ride['start']*48000);right=round(ride['end']*48000);fade=round(ride['fadeSeconds']*48000);gain=10**(ride['gainDb']/20)
envelope=np.ones(len(game),dtype=np.float32);envelope[left:right]=gain;envelope[left-fade:left]=np.linspace(1,gain,fade);envelope[right:right+fade]=np.linspace(gain,1,fade)
game*=envelope[:,None];del envelope
gamefile=O/'game-stem.wav';sf.write(gamefile,game,48000,subtype='PCM_24');del game
graph='[0:a]asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[game];[voice][game]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
mix=O/'final-mix.wav';run(['-i',O/'narration-stem.wav','-i',gamefile,'-filter_complex',graph,'-map','[out]','-t',duration,'-ar',48000,'-ac',2,'-c:a','pcm_s24le',mix],'restore-game-mix')
aac=O/'final-mix.m4a';run(['-i',mix,'-ar',48000,'-ac',2,'-c:a','aac','-b:a','192k',aac],'final-aac')
stats=h.loudness_stats(run(['-i',aac,'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],'encoded-loudness'));assert float(stats['input_tp'])<=-1.5
report=dict(old,revision='standard-game-audio-v4',music=dict(addedBgm=False,externalMusicStem=None),voiceDucked=False,sourceAudioUsed=True,gameAudio=rows,gameTargetLufs=-23,sidechain=graph,encodedLoudnessMeasurement=stats,narrationUnchanged=dict(old=rel(V3/'narration-stem.wav'),current=rel(O/'narration-stem.wav'),sha256=sha(O/'narration-stem.wav')),outputs=[dict(file=rel(f),sha256=sha(f),bytes=f.stat().st_size) for f in [O/'narration-stem.wav',gamefile,mix,aac]],sourceToStemToEncodedSpeechContinuity='pending current mix',currentFinalMixFullAsr='pending one pass',humanWholeListening='pending')
report.pop('visualOnlyRebind',None)
report['speechPriorityGameRide']=ride
save(O/'audio-build.json',report);outputs={};video_equivalence=[]
for kind in ['clean','captioned']:
 selected();src=V3/f'euler-{kind}.mp4';dst=O/f'euler-{kind}.mp4'
 run(['-i',src,'-i',aac,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',dst],kind+'-audio-remux')
 outputs[kind]=dict(file=rel(dst),sha256=sha(dst))
 def streamhash(f):
  return subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
 a,b=streamhash(src),streamhash(dst);assert a==b
 video_equivalence.append(dict(kind=kind,previousFile=rel(src),previousSha256=sha(src),currentFile=rel(dst),currentSha256=sha(dst),elementaryVideoSha256=a,exactCompressedVideoStreamEqual=True))
save(O/'pair-source.json',dict(inputs=dict(timelineSha256=sha(P/'production/revision-v3/timeline.json'),audioSha256=sha(aac)),outputs=outputs))
save(H/'video-reuse-proof.json',dict(revision='standard-game-audio-v4',frames=frames,fps=60,priorVisualReview='production/revision-v3/visual-review.json',priorVisualReviewSha256=sha(P/'production/revision-v3/visual-review.json'),streams=video_equivalence,visualChanges=False,captionTimingChanges=False))
run(['-i',O/'euler-captioned.mp4','-vn','-ar',16000,'-ac',1,'-c:a','pcm_s16le',O/'encoded-audio.wav'],'encoded-asr-input')
save(O/'encoded-audio-source.json',dict(inputs=dict(videoSha256=outputs['captioned']['sha256'],rate=16000,channels=1,format='pcm_s16le'),audioSha256=sha(O/'encoded-audio.wav')))
for label,base in [('before',V3),('after',O)]:
 run(['-ss',429.5,'-i',base/'final-mix.m4a','-t',45,'-vn','-c:a','pcm_s16le',O/f'comparison-{label}-45s.wav'],label+'-comparison')
print('Audio-only revision built; reviewed compressed video streams and narration stem unchanged.',flush=True)
