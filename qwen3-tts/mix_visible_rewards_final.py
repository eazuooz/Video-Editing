"""Full A narration / quiet licensed gameplay / continuous Wanderlust mix."""
import argparse, json, math, re, shutil
from pathlib import Path
import numpy as np
import soundfile as sf
from prepare_visible_rewards_review import ffmpeg, measure
from mix_visible_rewards_review import duration

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--version', type=int, default=1)
version=parser.parse_args().version
if version not in (1,2): raise ValueError('Supported mix revisions: 1, 2')
mfile=ROOT/'projects/visible-rewards/project.json'
m=json.loads(mfile.read_text(encoding='utf-8'))
assert m['approvals']['voice']=='approved-A-balanced'
music=m['audio']['backgroundMusic']
assert music['approvalStatus']=='approved' and music['title']=='Wanderlust'
timing=(ROOT/'motion-canvas/src/projects/visible-rewards/timing.ts').read_text(encoding='utf-8')
starts=json.loads('['+re.search(r'SCENE_STARTS = \[([^]]+)',timing).group(1).strip().rstrip(',')+']')
total=float(re.search(r'TOTAL_DURATION = ([\d.]+)',timing).group(1))
length=m['editing']['exampleSeconds']
assets=ROOT/'motion-canvas/src/projects/visible-rewards/assets'
out=ROOT/f'shared/output/visible-rewards/audio-final-v{version}';out.mkdir(parents=True,exist_ok=True)
wav=out/'final-mix.wav';aac=out/'final-mix.m4a'
if wav.exists() or aac.exists(): raise FileExistsError('Retain prior mix; choose a new version')
source=ROOT/music['file']; n=ROOT/m['paths']['editorNarration']
stats=measure(source);gain=m['audio']['bgmTargetLufs']-float(stats['input_i'])
count=math.ceil((total-1)/(duration(source)-1))
args=['-n','-i',str(n)]
for _ in range(count): args+=['-i',str(source)]
gameplay='gameplay' if version==1 else 'gameplay-v2'
for i in range(len(starts)): args+=['-i',str(assets/f'{gameplay}/scene{i+1:02}.mp4')]
filters=[f'[0:a]aresample=48000,pan=stereo|c0=0.70710678*c0|c1=0.70710678*c0,apad,atrim=duration={total},asplit=2[n][side]']
for i in range(count):filters.append(f'[{i+1}:a]aresample=48000,volume={gain}dB[m{i}]')
prev='m0'
for i in range(1,count):filters.append(f'[{prev}][m{i}]acrossfade=d=1:c1=tri:c2=tri[j{i}]');prev=f'j{i}'
# Smooth, continuous -3 dB dip only while a real example's source sound exists.
ramps='+'.join(f'(between(t,{s},{s+length})*min(1,min((t-{s})/0.45,({s+length}-t)/0.45)))' for s in starts)
envelope=f'pow(10,(-3*({ramps}))/20)'
filters.append(f"[{prev}]atrim=duration={total},asetpts=PTS-STARTPTS,afade=t=in:d=0.45,afade=t=out:st={total-.45}:d=0.45,volume='{envelope}':eval=frame,asplit=2[bgm][musicreview]")
for i,s in enumerate(starts):
 filters.append(f'[{1+count+i}:a]aresample=48000,atrim=duration={length},asetpts=PTS-STARTPTS,adelay={round(s*48000)}S:all=1[g{i}]')
filters.append(''.join(f'[g{i}]' for i in range(len(starts)))+f'amix=inputs={len(starts)}:normalize=0:duration=longest,apad,atrim=duration={total},asplit=2[game][gamereview]')
filters.append('[bgm][game]amix=inputs=2:normalize=0:duration=first[bed]')
filters.append(f'[bed][side]sidechaincompress=threshold={m["audio"]["duckingThreshold"]}:ratio={m["audio"]["duckingRatio"]}:attack=15:release=280:makeup=1,asplit=2[duck][bedreview]')
filters.append('[n][duck]amix=inputs=2:normalize=0:duration=first,aresample=192000,alimiter=limit=0.75:level=false:latency=true:attack=5:release=80,aresample=48000[mix]')
ffmpeg(args+['-filter_complex',';'.join(filters),'-map','[mix]','-c:a','pcm_s16le',str(wav),'-map','[musicreview]','-c:a','pcm_s16le',str(out/'bgm-only.wav'),'-map','[gamereview]','-c:a','pcm_s16le',str(out/'game-only.wav'),'-map','[bedreview]','-c:a','pcm_s16le',str(out/'background-only.wav')])
ffmpeg(['-n','-i',str(wav),'-c:a','aac','-b:a','192k','-movflags','+faststart',str(aac)])
report={'durationSeconds':total,'humanListening':'pending','loudness':{k:measure(p) for k,p in [('wav',wav),('aac',aac)]},'windows':[],'gameplayLufs':'-23; foreign commentary cuts -31','bgmLufs':-28,'bgmDuringGameplayDb':-3,'narrationUnchanged':True}
for kind in ['bgm','game','background']:
 data,sr=sf.read(out/f'{kind}-only.wav',always_2d=True)
 for i,start in enumerate(starts):
  for part,offset in [('example',3),('explanation',length+3)]:
   a=round((start+offset)*sr);rms=float(np.sqrt(np.mean(data[a:a+2*sr]**2)))
   if kind!='game' and rms<1e-6:raise RuntimeError('Missing continuous background')
   if kind=='game' and part=='example' and rms<1e-6:raise RuntimeError('Missing game sound')
   if kind=='game' and part=='explanation' and rms>1e-6:raise RuntimeError('Game sound leaked into explanation')
   report['windows'].append({'layer':kind,'scene':i+1,'part':part,'rmsDbfs':round(20*math.log10(max(rms,1e-10)),2)})
assert all(float(v['input_tp'])<=-1.5 for v in report['loudness'].values())
assert abs(duration(wav)-total)<.03 and abs(duration(aac)-total)<.05
stem='final-mix' if version==1 else f'final-mix-v{version}'
shutil.copy2(wav,assets/f'{stem}.wav');shutil.copy2(aac,assets/f'{stem}.m4a')
m['paths']['editorAudioMix']=f'motion-canvas/src/projects/visible-rewards/assets/{stem}.wav'
m['paths']['audioMix']=f'motion-canvas/src/projects/visible-rewards/assets/{stem}.m4a'
m['paths']['audioMeasurements']=f'shared/output/visible-rewards/audio-final-v{version}/report.json'
m['audio']['mixStatus']='full-mix-human-review-pending';m['status']='video-production';m['publishReady']=False
m['audio']['gameCommentaryTargetLufs']=-31
mfile.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report['loudness'],indent=2),flush=True)
