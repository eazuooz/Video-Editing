"""Join original2s branding, measured lesson scenes, original-identity10s outro."""
from pathlib import Path
import json, subprocess, hashlib, shutil
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
from revision_paths import workroot
OUT=workroot(ROOT)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def run(args):
 p=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace'))
 return p.stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
control=read(ROOT/'shared/publishing/video-production-control.json');assert control['selectedVideo']==SLUG
pending=OUT/'visual-revisions.pending.json'
assert not pending.exists() or not read(pending),'Resolve identified scene revisions before assembling the master'
m=read(ROOT/f'projects/{SLUG}/project.json');data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
assert data['captionTimingStatus']=='asr-aligned'
files=[ROOT/'shared/output/motion-canvas/yamyam-intro-sample-v2-visual.mp4']
for s in data['scenes']:
 p=ROOT/f"shared/output/motion-canvas/ai-craft-scene-{s['id']}-{m.get('revision',{}).get('id','v1')}.mp4"
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
# MP4 format.duration is rounded to milliseconds. Supplying the exact frame
# duration prevents that rounding from accumulating across the30 inputs.
lst=OUT/'visuals.ffconcat';lst.write_text('ffconcat version 1.0\n'+'\n'.join(f"file '{p.as_posix()}'\nduration {r['frames']/60:.9f}" for p,r in zip(files,inventory))+'\n',encoding='utf-8')
audio=OUT/'audio/mix.m4a';assert read(OUT/'audio/mix-report.json')['totalFrames']==expected
target=ROOT/m['paths']['videoClean'];assert not target.exists(),'Preserve existing clean master; explicitly version a revision'
run(['ffmpeg','-v','error','-n','-f','concat','-safe','0','-i',str(lst),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(target)])
packets=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time','-of','json',str(target)]))['packets']
pts=sorted(float(p['pts_time']) for p in packets)
assert len(pts)==expected and abs(pts[0])<.0001 and abs(pts[-1]-(expected-1)/60)<.0001
assert max(abs(b-a-1/60) for a,b in zip(pts,pts[1:]))<.0001,'Fix concat timing before caption encoding'
(OUT/'assembly.json').write_text(json.dumps({'inputs':inventory,'frames':expected,'duration':expected/60,'audioSha256':sha(audio),'cleanSha256':sha(target),'integrity':'pending-current-encoded-output-checks'},indent=2)+'\n',encoding='utf-8')
audio_target=ROOT/m['paths']['audioMix'];audio_target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(audio,audio_target)
shutil.copy2(OUT/'audio/mix.wav',audio_target.with_suffix('.wav'))
print(target)
