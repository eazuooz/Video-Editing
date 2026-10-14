"""Join original2s branding, measured lesson scenes, original-identity10s outro."""
from pathlib import Path
import json, subprocess, hashlib, shutil
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
OUT=ROOT/'shared/output'/SLUG
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def run(args):
 p=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace'))
 return p.stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
control=read(ROOT/'shared/publishing/video-production-control.json');assert control['selectedVideo']==SLUG
m=read(ROOT/f'projects/{SLUG}/project.json');data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
assert data['captionTimingStatus']=='asr-aligned'
files=[ROOT/'shared/output/motion-canvas/yamyam-intro-sample-v2-visual.mp4']
for s in data['scenes']:
 p=ROOT/f"shared/output/motion-canvas/ai-craft-scene-{s['id']}-v1.mp4"
 r=read(OUT/'composite'/s['id']/'render.json')
 assert r['encoded']['sha256']==sha(p)
 assert r['frames']==round(s['duration']*60)
 files.append(p)
files.append(ROOT/'shared/output/motion-canvas/ai-craft-membership-v1.mp4')
expected=120+sum(round(s['duration']*60) for s in data['scenes'])+600
inventory=[]
for i,p in enumerate(files):
 v=next(s for s in json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))['streams'] if s['codec_type']=='video')
 assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1'
 inventory.append({'path':p.relative_to(ROOT).as_posix(),'frames':int(v['nb_frames']),'sha256':sha(p)})
assert inventory[0]['frames']==120 and inventory[-1]['frames']==600
assert sum(f['frames'] for f in inventory)==expected
lst=OUT/'visuals.ffconcat';lst.write_text('ffconcat version 1.0\n'+'\n'.join(f"file '{p.as_posix()}'" for p in files)+'\n',encoding='utf-8')
audio=OUT/'audio/mix.m4a';assert read(OUT/'audio/mix-report.json')['totalFrames']==expected
target=ROOT/m['paths']['videoClean'];assert not target.exists(),'Preserve existing clean master; explicitly version a revision'
run(['ffmpeg','-v','error','-n','-f','concat','-safe','0','-i',str(lst),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(target)])
(OUT/'assembly.json').write_text(json.dumps({'inputs':inventory,'frames':expected,'duration':expected/60,'audioSha256':sha(audio),'cleanSha256':sha(target),'integrity':'pending-current-encoded-output-checks'},indent=2)+'\n',encoding='utf-8')
audio_target=ROOT/m['paths']['audioMix'];audio_target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(audio,audio_target)
shutil.copy2(OUT/'audio/mix.wav',audio_target.with_suffix('.wav'))
print(target)
