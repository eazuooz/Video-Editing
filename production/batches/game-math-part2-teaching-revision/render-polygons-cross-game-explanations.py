"""Render measured explanations on CPU, one independent scene per addition."""
from pathlib import Path
import json,os,subprocess,sys,hashlib,ast
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons'
timing=json.loads((O/'combined-addition-timing.json').read_text(encoding='utf8'))
for slug in ['game-math-polygon-centers-v2','game-math-polygon-partition-v2']:
    timeline_path=ROOT/f'projects/{slug}/production/timeline.json'
    if not timeline_path.exists():continue
    for slot in json.loads(timeline_path.read_text(encoding='utf8'))['scenes']:
        if not slot['preservedOriginal'] and slot['classification']=='explanation':
            assert timing[slot['id']]['voiceSha256']==slot['voiceSha256']
            timing[slot['id']]=slot
classes=sys.argv[1:] or ['QF04','QB11','QB12','QB13','QB14']
assert classes and all(k in timing and timing[k]['sourceType']!='actual-footage' for k in classes)
source=ROOT/'manim/projects/game-math-part2-teaching-revision/polygons_cross_game.py'
tree=ast.parse(source.read_text(encoding='utf8'))
for node in ast.walk(tree):
    if not isinstance(node,ast.If) or not isinstance(node.test,ast.Compare):continue
    test=node.test
    if not isinstance(test.left,ast.Attribute) or test.left.attr!='sid' or len(test.comparators)!=1 or not isinstance(test.comparators[0],ast.Constant):continue
    ident=test.comparators[0].value
    if ident not in classes:continue
    for child in (n for statement in node.body for n in ast.walk(statement)):
        if isinstance(child,ast.Call) and isinstance(child.func,ast.Name) and child.func.id=='sentence':
            fragment=child.args[0].value
            assert sum(fragment in cue['text'] for cue in timing[ident]['sentenceCues'])==1,(ident,fragment)
runtime_sha=hashlib.sha256(source.read_bytes()).hexdigest()
env=os.environ.copy();env.update(REVISION_FINAL_TIMING='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
command=[str(ROOT/'manim/.venv/Scripts/python.exe'),'-X','utf8','-m','manim','-qh','--disable_caching','--media_dir',str(O/'caption-safe-v2'),str(source),*classes]
log=O/('explanations-render-'+('-'.join(classes) if sys.argv[1:] else 'all')+'.log')
with log.open('w',encoding='utf8') as out:subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
p=O/'caption-safe-polygons_cross_game-receipts.json';records=json.loads(p.read_text(encoding='utf8')) if p.exists() else {}
for ident in classes:
    video=O/f'caption-safe-v2/videos/polygons_cross_game/1080p60/{ident}.mp4'
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)],text=True,creationflags=subprocess.CREATE_NO_WINDOW));v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==runtime_sha,'Source changed during render'
    records[ident]={'sourceSha256':runtime_sha,'voiceSha256':timing[ident]['voiceSha256'],'lineStarts':timing[ident]['lineStarts'],'seconds':timing[ident]['seconds'],'frames':int(v['nb_frames']),'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'pixelApproval':False}
p.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'rendered':classes,'currentHashTiming':True,'pixelApproval':False}))

