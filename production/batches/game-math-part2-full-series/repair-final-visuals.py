"""Repair only explicitly selected final scenes; retain timing and all raw voices."""
from pathlib import Path
import sys,importlib.util,json,subprocess,hashlib,argparse,datetime
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('slug');parser.add_argument('ids',nargs='+')
parser.add_argument('--reason',default='Decimal matrix cells overlapped in final pixels; code emphasis also made paragraph-specific. All raw narration and measured timing preserved.')
parser.add_argument('--source',default='manim/projects/game-math-part2-full-series/lesson.py')
args=parser.parse_args();slug=args.slug;ids=args.ids
assert ids and all(i.isdigit() for i in ids)
source=(ROOT/args.source).resolve();assert source.is_relative_to(ROOT) and source.is_file()
from production_control import require_current_authorization
require_current_authorization(slug,'selected CPU final visual correction')
work=ROOT/'shared/output'/slug;base=ROOT/'projects'/slug
spec=importlib.util.spec_from_file_location('caption_tools',ROOT/'projects/game-math-polar-sample/production/build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.BASE=base;b.WORK=work;b.MF=base/'project.json'
timeline=b.read(base/'production/timeline.json')
assert len(ids)==len(set(ids)) and all(next(s for s in timeline['scenes'] if s['id']==sid)['classification']=='explanation' for sid in ids)
raw={str(p.relative_to(ROOT)):b.sha(p) for p in (ROOT/'shared/output/narration'/slug).rglob('chunks/*.wav')}
datafile=Path(__file__).parent/'lessons'/f'{slug}.json';stub=ROOT/f'manim/projects/{slug}/scene.py'
inputs={p:b.sha(p) for p in [source,datafile,stub]}
if source.name!='lesson.py':inputs[source.parent/'lesson.py']=b.sha(source.parent/'lesson.py')
data=b.read(datafile)
for path in data.get('sourceDependencies',[]):inputs[ROOT/path]=b.sha(ROOT/path)
vdir=work/'manim/videos/scene/1080p60'
b.run([sys.executable,'-m','manim','-qh','--disable_caching','--media_dir',work/'manim',ROOT/f'manim/projects/{slug}/scene.py',*['Scene'+i for i in ids]],'visual-repair-manim.log')
for sid in ids:
 s=next(s for s in timeline['scenes'] if s['id']==sid)
 target=work/'clips'/f'{sid}.mp4'
 b.ff(['-i',vdir/f'Scene{sid}.mp4','-vf','fps=60,setsar=1,tpad=stop_mode=clone:stop_duration=0.05','-frames:v',str(s['frames']),*b.ENC,target],f'visual-repair-{sid}.log')
 import shutil
 shutil.copy2(target,ROOT/f'motion-canvas/src/projects/{slug}/assets/{sid}.mp4')
assert b.read(base/'production/timeline.json')==timeline
assert all(b.sha(ROOT/path)==sha for path,sha in raw.items())
assert all(b.sha(path)==sha for path,sha in inputs.items()),'Render inputs changed during correction; preserve clips for review, never adopt stale fingerprints.'
receipts_path=work/'render-receipts.json';receipts=b.read(receipts_path) if receipts_path.exists() else {}
for sid in ids:
 slot=next(s for s in timeline['scenes'] if s['id']==sid)
 record={**receipts.get(sid,{}),'voiceSha256':slot['voiceSha256'],'lessonSha256':inputs[source],'dataSha256':inputs[datafile],'stubSha256':inputs[stub],'renderReserveSeconds':0,'renderedFinalFrames':slot['frames'],'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Explicit selected final-timeline visual correction; raw voices unchanged'}
 if source.name!='lesson.py':record['helperSha256']=inputs[source.parent/'lesson.py']
 if data.get('sourceDependencies'):record['dependencySha256']={path:inputs[ROOT/path] for path in data['sourceDependencies']}
 receipts[sid]=record
b.write(receipts_path,receipts)
b.write(work/'visual-repair.json',{'scenes':ids,'reason':args.reason,'timelineUnchanged':True,'rawNarrationUnchanged':True,'rawNarrationSha256':raw,'sourcePath':str(source.relative_to(ROOT)).replace('\\','/'),'sourceSha256':b.sha(source),'humanListening':'pending','repairedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
for stage in ['mix','burn','qa']:
 subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).parent/'build.py'),slug,stage],cwd=ROOT,check=True)
