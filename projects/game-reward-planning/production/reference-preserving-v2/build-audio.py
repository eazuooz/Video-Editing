"""Duration-preserving narration repair and narration-first continuous mix."""
from pathlib import Path
import json,subprocess,re,hashlib
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';N=R/'shared/output/narration/game-reward-planning/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit';O.mkdir(parents=True,exist_ok=True)
plan=json.loads((P/'production/reference-preserving-v2/edit-plan.json').read_text(encoding='utf8'));duration=plan['totalFrames']/60
def run(args,name):
 log=O/(name+'.log');p=subprocess.run(['ffmpeg','-hide_banner','-y',*args],cwd=R,capture_output=True);log.write_bytes(p.stderr)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2500:])
 return p.stderr.decode(errors='replace')
def measure(args,name):
 s=run([*args,'-af','loudnorm=I=-17:TP=-2:LRA=9:print_format=json','-f','null','-'],name);return json.loads(s[s.rfind('{'):s.rfind('}')+1])
sr=24000;parts=[np.zeros(sr*2,dtype=np.float32)]
sourceHashes=[]
for i in range(1,12):
 source=N/'chunks'/f'{i:02}-scene.wav';leveled=N/'leveled'/f'{i:02}-float.wav';patch=N/'leveled-patched'/f'{i:02}-float.wav';leveled=patch if patch.exists() else leveled;a,r=sf.read(leveled,dtype='float32');assert r==sr
 report=json.loads((N/'leveled'/f'{i:02}.json').read_text());assert report['sourceSha256']==hashlib.sha256(source.read_bytes()).hexdigest()
 parts.extend([a,np.zeros(round(sr*.3),dtype=np.float32)]) if i<11 else parts.append(a)
 sourceHashes.append(report['sourceSha256'])
parts.append(np.zeros(sr*10,dtype=np.float32));joined=np.concatenate(parts)
sf.write(O/'voice-smooth-float.wav',joined,sr,subtype='FLOAT')
run(['-i',str(O/'voice-smooth-float.wav'),'-af','acompressor=threshold=0.1:ratio=2:attack=20:release=250:makeup=1,pan=stereo|c0=c0|c1=c0','-ar','48000','-c:a','pcm_f32le',str(O/'voice-compressed-float.wav')],'voice-compress')
stats=measure(['-i',str(O/'voice-compressed-float.wav')],'voice-loudness-measure')
norm='loudnorm=I=-17:TP=-2:LRA=9:linear=true:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}'.format(**stats)
run(['-i',str(O/'voice-compressed-float.wav'),'-af',norm,'-ar','48000','-ac','2','-t',str(duration),'-c:a','pcm_s24le',str(O/'narration-stem.wav')],'voice-normalize')
# Preserve useful original game sound quietly; official stills and diagrams are silent.
rate=48000;game=np.zeros((round(duration*rate),2),dtype=np.float32);gameEvidence=[]
for c in plan['cuts']:
 if c['kind']!='independent-gameplay':continue
 target=O/(c['id']+'-source-audio.wav');d=c['frames']/60
 sourceSegments=c.get('sourceSegments',[{'start':c['sourceStart'],'frames':c['frames']}]);audioParts=[]
 for j,s in enumerate(sourceSegments):
  part=target.with_stem(target.stem+'-'+str(j));run(['-ss',str(s['start']),'-i',c['sourceFile'],'-t',str(s['frames']/60),'-vn','-ar','48000','-ac','2','-c:a','pcm_f32le',str(part)],c['id']+'-audio-'+str(j));v,r=sf.read(part,dtype='float32');audioParts.append(v[:round(s['frames']/60*rate)])
 a=np.concatenate(audioParts);n=round(d*rate);a=a[:n];fade=min(960,len(a)//2);a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None]
 # Fixed per-cut gain to a quiet RMS reference. No time-varying boost of silence.
 rms=float(np.sqrt(np.mean(a*a)));gain=min(1.,10**(-34/20)/max(rms,1e-9));a*=gain
 start=round(c['startFrame']/60*rate);game[start:start+len(a)]+=a
 gameEvidence.append({'cut':c['id'],'sourceRmsDbfs':20*np.log10(max(rms,1e-9)),'fixedGainDb':20*np.log10(gain),'note':'original mixed game effects/ambience/music retained quietly; no claim of isolated effects'})
sf.write(O/'game-stem.wav',game,rate,subtype='PCM_24')
music=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
# Existing approved Nimbus style starts at-28LUFS and is ducked by narration.
run(['-stream_loop','-1','-i',str(music),'-t',str(duration),'-af',f'loudnorm=I=-28:TP=-4:LRA=7,afade=t=in:st=0:d=1,afade=t=out:st={duration-2}:d=2','-ar','48000','-ac','2','-c:a','pcm_s24le',str(O/'music-stem.wav')],'music-level')
graph='[0:a]asplit=3[voice][side1][side2];[1:a][side1]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];[2:a][side2]sidechaincompress=threshold=0.035:ratio=2:attack=15:release=250[game];[voice][bg][game]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
run(['-i',str(O/'narration-stem.wav'),'-i',str(O/'music-stem.wav'),'-i',str(O/'game-stem.wav'),'-filter_complex',graph,'-map','[out]','-t',str(duration),'-ar','48000','-c:a','pcm_s24le',str(O/'final-mix.wav')],'final-mix')
report={'sourcePcmHashes':sourceHashes,'sourcePcmPreserved':True,'duration':duration,'normalization':stats,'narrationTargetLufs':-17,'limiterDbtp':-2,'music':'Nimbus — Eveningland (YouTube Audio Library)','musicSha256':hashlib.sha256(music.read_bytes()).hexdigest(),'musicInitialLufs':-28,'ducking':'voice controls music and game stems; voice gain never follows background; amix normalize=0','gameAudio':gameEvidence,'localLevelAndFinalAsr':'pending; not inferred from integrated loudness'}
(O/'audio-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print('Built duration-preserving narration stem and final mix',duration)
