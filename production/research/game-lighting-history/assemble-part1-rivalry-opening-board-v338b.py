"""Reuse all six completed extracts; original source is 720p, retained cut is 1080p."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT/'production/research/game-lighting-history';P=m.ROOT/'projects/game-lighting-history-04/production'
OUT=R/'local/part1-rivalry-opening-v338';prior=P/'part1-rivalry-opening-execution-v338.json';state=m.read(prior)
assert state['status']=='failed' and len(state['commands'])==2 and all(x['exitCode']==0 for x in state['commands'])
plan=m.read(P/'part1-final-input-plan-v309.json');visual=m.read(P/'part1-final-visual-build-v332.json')
cut=next(x for x in plan['cuts'] if x['id']=='rivalry-surface-observation:native');current=next(x for x in visual['cuts'] if x['id']==cut['id'])
source=m.ROOT/cut['video']['path'];native=m.ROOT/current['path']
assert m.sha(source)==cut['video']['sha256'] and m.sha(native)==current['sha256']
canvas=Image.new('RGB',(1920*3,1130*2),'#151515');d=ImageDraw.Draw(canvas);frames=[]
for row,label in enumerate(['source','input']):
 for k in range(1,4):
  p=OUT/f'{label}-{k:02d}.png';im=Image.open(p).convert('RGB');size=im.size
  assert size==((1280,720) if row==0 else (1920,1080))
  if row==0:im=im.resize((1920,1080),Image.Resampling.NEAREST)
  canvas.paste(im,((k-1)*1920,row*1130+50));d.text(((k-1)*1920+12,row*1130+12),f'{label} original frame {29+k if row==0 else k-1}, native {size}',fill='white')
  frames.append(dict(path=m.rel(p),sha256=m.sha(p),type=label,frame=29+k if row==0 else k-1,nativeSize=list(size)))
board=OUT/'source-input-opening-board.png';assert not board.exists();canvas.save(board)
proof=dict(completedAt=m.stamp(),status='complete',priorExtract=dict(path=m.rel(prior),sha256=m.sha(prior)),source=dict(path=m.rel(source),sha256=m.sha(source)),input=dict(path=m.rel(native),sha256=m.sha(native)),frames=frames,board=dict(path=m.rel(board),sha256=m.sha(board)),reextracted=False,newGitImages=0,directlyReviewed=False)
m.save(P/'part1-rivalry-opening-board-v338b.json',proof);print(m.json.dumps(dict(board=m.rel(board),reextracted=False)))
