"""CPU-only current-timing renders; originals and narration remain unchanged."""
from pathlib import Path
import json,os,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'shared/output/game-math-part2-teaching-revision'
kind=sys.argv[1]
if kind not in ('bridges','supplements'):raise SystemExit('Choose bridges or supplements')
timing=json.loads((O/('bridge-timing.json' if kind=='bridges' else 'supplement-timing.json')).read_text(encoding='utf8'))
classes=sys.argv[2:] or list(timing)
assert all(x in timing for x in classes)
assert classes,'No measured current-hash timings'
env=os.environ.copy();env.update(REVISION_FINAL_TIMING='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
command=[str(ROOT/'manim/.venv/Scripts/python.exe'),'-X','utf8','-m','manim','-qh','--disable_caching','--media_dir',str(O/'caption-safe-v2'),str(ROOT/f'manim/projects/game-math-part2-teaching-revision/{kind}.py'),*classes]
log=O/f'caption-safe-{kind}-v2.log'
with log.open('w',encoding='utf8') as out:subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
receipt=O/f'caption-safe-{kind}-receipts.json'
records=json.loads(receipt.read_text(encoding='utf8')) if receipt.exists() else {}
source=ROOT/f'manim/projects/game-math-part2-teaching-revision/{kind}.py'
for ident in classes:
 target=O/f'caption-safe-v2/videos/{kind}/1080p60/{ident}.mp4'
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(target)],text=True,creationflags=subprocess.CREATE_NO_WINDOW))
 video=next(s for s in info['streams'] if s['codec_type']=='video')
 records[ident]={'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'voiceSha256':timing[ident]['voiceSha256'],'lineStarts':timing[ident]['lineStarts'],'seconds':timing[ident]['seconds'],'frames':int(video['nb_frames']),'videoSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'pixelApproval':False}
receipt.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'rendered':classes,'log':str(log),'pixelApproval':False}))
