"""Inspect three original native frames and their retained cut counterparts; no rerender."""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT/'production/research/game-lighting-history';P=m.ROOT/'projects/game-lighting-history-04/production'
plan=m.read(P/'part1-final-input-plan-v309.json');visual=m.read(P/'part1-final-visual-build-v332.json')
cut=next(x for x in plan['cuts'] if x['id']=='rivalry-surface-observation:native')
current=next(x for x in visual['cuts'] if x['id']==cut['id'])
assert cut['proposedCuts']==[{'inFrame':30,'outFrame':1036}] and current['fromFrame']==82995
source=m.ROOT/cut['video']['path'];native=m.ROOT/current['path']
assert m.sha(source)==cut['video']['sha256'] and m.sha(native)==current['sha256']
OUT=R/'local/part1-rivalry-opening-v338';SP=P/'part1-rivalry-opening-execution-v338.json'
assert not OUT.exists() and not SP.exists()
resources=m.resources();OUT.mkdir()
state=dict(startedAt=m.stamp(),status='extracting-three-original-and-three-input-frames',worker=m.worker(),resourceObservation=resources,active=None,commands=[],newGitImages=0,directlyReviewed=False)
m.save(SP,state)
try:
 for label,path,start in [('source',source,30),('input',native,0)]:
  m.run([m.FF,'-n','-v','error','-nostdin','-threads','2','-i',path,'-vf',f"select='between(n,{start},{start+2})'",'-frames:v','3','-fps_mode','passthrough','-threads','2',OUT/(label+'-%02d.png')],label,state,SP,OUT)
 canvas=Image.new('RGB',(1920*3,1130*2),'#151515');d=ImageDraw.Draw(canvas)
 frames=[]
 for row,label in enumerate(['source','input']):
  for k in range(1,4):
   p=OUT/f'{label}-{k:02d}.png';im=Image.open(p).convert('RGB');assert im.size==(1920,1080)
   canvas.paste(im,((k-1)*1920,row*1130+50));d.text(((k-1)*1920+12,row*1130+12),f'{label} original frame {29+k if row==0 else k-1}',fill='white')
   frames.append(dict(path=m.rel(p),sha256=m.sha(p),type=label,frame=29+k if row==0 else k-1))
 board=OUT/'source-input-opening-board.png';canvas.save(board)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),source=dict(path=m.rel(source),sha256=m.sha(source)),input=dict(path=m.rel(native),sha256=m.sha(native)),frames=frames,board=dict(path=m.rel(board),sha256=m.sha(board)),directlyReviewed=False)
 m.save(SP,state);print(m.json.dumps(dict(status=state['status'],frames=len(frames),board=m.rel(board))))
except Exception as e:
 state.update(status='failed',error=str(e),failedAt=m.stamp());m.save(SP,state);raise
