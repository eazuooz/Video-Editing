"""Replace inspected loading/intro cuts, preserving all voice, music and timing."""
from pathlib import Path
import json,subprocess,shutil,hashlib,datetime,sys
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit';followup='--followup' in sys.argv;B=O/('first-repair' if followup else 'first-pass')
cumulative=['cut00','cut13','cut14','cut16','cut28'];changed=['cut00'] if followup else cumulative
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard():
 c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'));assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def ff(args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*args],cwd=R,check=True)
guard();assert not B.exists(),'Repair already started; inspect receipt instead of overwriting evidence'
B.mkdir();shutil.copytree(O/'qa',B/'qa')
if (O/'active-inpoint-repair.json').exists():shutil.copy2(O/'active-inpoint-repair.json',B/'active-inpoint-repair.json')
for name in ['making-game-sequels-v2-clean.mp4','making-game-sequels-v2-captioned.mp4','final-mix.wav','final-mix.m4a','game-stem.wav','audio-build.json']:
 shutil.copy2(O/name,B/name)
retained={p.name:sha(p) for p in [O/'narration-stem.wav',O/'music-stem.wav',O/'captions.ko.ass',O/'captions.ko.srt',O/'captions.en.srt']}
cutHashes={p.stem:sha(p) for p in O.glob('cut??.mp4')}
state={'changedCuts':cumulative,'rerenderedCuts':changed,'repairGeneration':2 if followup else 1,'reason':'Direct final-pixel review found black/loading/versus transitions; replace with inspected active gameplay','retainedInputs':retained,'status':'footage','startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
receipt=O/'active-inpoint-repair.json'
def save():receipt.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
save();guard();subprocess.run([sys.executable,'-X','utf8',str(V/'render-footage.py')],cwd=R,check=True)
assert all(sha(O/(k+'.mp4'))==v for k,v in cutHashes.items() if k not in changed)
state['status']='matching-game-audio';save();guard()
plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));game,rate=sf.read(O/'game-stem.wav',dtype='float32',always_2d=True);assert rate==48000
records=[]
for c in plan['cuts']:
 if c['id'] not in changed:continue
 d=c['frames']/60;f=O/(c['id']+'-game.wav');ff(['-ss',str(c['sourceStart']),'-i',c['sourceFile'],'-t',str(d),'-vn','-ar','48000','-ac','2','-c:a','pcm_f32le',str(f)])
 a,_=sf.read(f,dtype='float32',always_2d=True);count=c['frames']*800;a=a[:count];assert len(a)==count
 rms=float(np.sqrt(np.mean(a*a)));gain=min(1.,10**(-33/20)/max(rms,1e-9));a*=gain;fade=min(960,len(a)//2);a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None]
 start=c['startFrame']*800;game[start:start+count]=a
 records.append({'cut':c['id'],'sourceStart':c['sourceStart'],'sourceRmsDbfs':20*np.log10(max(rms,1e-10)),'gainDb':20*np.log10(gain),'mixedOriginalAudio':True})
sf.write(O/'game-stem.wav',game,rate,subtype='PCM_24');del game
graph='[0:a]asplit=3[voice][side1][side2];[1:a][side1]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];[2:a][side2]sidechaincompress=threshold=0.035:ratio=2:attack=15:release=250[game];[voice][bg][game]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
ff(['-i',str(O/'narration-stem.wav'),'-i',str(O/'music-stem.wav'),'-i',str(O/'game-stem.wav'),'-filter_complex',graph,'-map','[out]','-t',str(plan['totalFrames']/60),'-ar','48000','-c:a','pcm_s24le',str(O/'final-mix.wav')])
report=json.loads((O/'audio-build.json').read_text(encoding='utf8'));replacement={r['cut']:r for r in records};report['gameAudio']=[replacement.get(r['cut'],r) for r in report['gameAudio']];report['activeInpointRepair']=records;(O/'audio-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert all(sha(O/k)==v for k,v in retained.items())
state['status']='pair-encoding';state['unchangedCutHashes']={k:v for k,v in cutHashes.items() if k not in cumulative};state['retainedFromPreviousRepair']={k:v for k,v in cutHashes.items() if k in cumulative and k not in changed};save();guard()
subprocess.run([sys.executable,'-X','utf8',str(V/'compose-video.py'),'pair'],cwd=R,check=True)
state['status']='repaired-masters-ready-for-QA';state['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('Repaired',len(changed),'active-play cuts and corresponding game audio; all narration/music/caption inputs and other cut files preserved.')
