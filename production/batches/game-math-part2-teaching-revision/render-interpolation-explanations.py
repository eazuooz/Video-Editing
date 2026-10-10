"""Render measured explanations on CPU, one independent scene per addition."""
from pathlib import Path
import json,os,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'
timing=json.loads((O/'combined-addition-timing.json').read_text(encoding='utf8'))
for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
    for slot in json.loads((ROOT/f'projects/{slug}/production/timeline.json').read_text(encoding='utf8'))['scenes']:
        if not slot['preservedOriginal'] and slot['classification']=='explanation':
            assert timing[slot['id']]['voiceSha256']==slot['voiceSha256']
            timing[slot['id']]=slot
classes=sys.argv[1:] or [k for k,v in timing.items() if v['sourceType']!='actual-footage']
assert classes and all(k in timing and timing[k]['sourceType']!='actual-footage' for k in classes)
source=ROOT/'manim/projects/game-math-part2-teaching-revision/interpolation_additions.py'
env=os.environ.copy();env.update(REVISION_FINAL_TIMING='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
command=[str(ROOT/'manim/.venv/Scripts/python.exe'),'-X','utf8','-m','manim','-qh','--disable_caching','--media_dir',str(O/'caption-safe-v2'),str(source),*classes]
log=O/'explanations-render.log'
with log.open('w',encoding='utf8') as out:subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
p=O/'caption-safe-interpolation_additions-receipts.json';records=json.loads(p.read_text(encoding='utf8')) if p.exists() else {}
for ident in classes:
    video=O/f'caption-safe-v2/videos/interpolation_additions/1080p60/{ident}.mp4'
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)],text=True,creationflags=subprocess.CREATE_NO_WINDOW));v=next(s for s in info['streams'] if s['codec_type']=='video')
    records[ident]={'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'voiceSha256':timing[ident]['voiceSha256'],'lineStarts':timing[ident]['lineStarts'],'seconds':timing[ident]['seconds'],'frames':int(v['nb_frames']),'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'pixelApproval':False}
p.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'rendered':classes,'currentHashTiming':True,'pixelApproval':False}))
