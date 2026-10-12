"""Compare equivalent source time: normalized60 frame30 is original30fps frame15."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw,ImageStat
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT/'production/research/game-lighting-history';P=m.ROOT/'projects/game-lighting-history-04/production'
plan=m.read(P/'part1-final-input-plan-v309.json');c=next(x for x in plan['cuts'] if x['id']=='rivalry-surface-observation:native')
source=m.ROOT/c['video']['path'];assert m.sha(source)==c['video']['sha256']
probeCmd=[m.FP,'-v','error','-show_entries','stream=r_frame_rate,avg_frame_rate,width,height','-of','json',source]
probe=json.loads(m.subprocess.run(list(map(str,probeCmd)),capture_output=True,text=True,check=True).stdout)
assert probe['streams'][0]['r_frame_rate']=='30/1' and c['proposedCuts'][0]['inFrame']==30
OUT=R/'local/part1-rivalry-rate-aligned-opening-v338c';SP=P/'part1-rivalry-rate-aligned-opening-execution-v338c.json'
assert not OUT.exists() and not SP.exists();resources=m.resources();OUT.mkdir()
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],resources=resources,directlyReviewed=False,newGitImages=0)
m.save(SP,state)
try:
 m.run([m.FF,'-n','-v','error','-nostdin','-threads','2','-i',source,'-vf',"select='between(n,15,17)'",'-frames:v','3','-fps_mode','passthrough','-threads','2',OUT/'source-%02d.png'],'rate-aligned-source-three-frames',state,SP,OUT)
 board=Image.new('RGB',(3840,1130*3),'#151515');d=ImageDraw.Draw(board);frames=[]
 for k in range(1,4):
  for col,label in enumerate(['source','input']):
   p=OUT/f'source-{k:02d}.png' if col==0 else R/f'local/part1-rivalry-opening-v338/input-{k:02d}.png'
   im=Image.open(p).convert('RGB');size=im.size;w,h=size;luma=ImageStat.Stat(im.convert('L').crop((w//8,h//6,7*w//8,5*h//6))).mean[0]
   if col==0:im=im.resize((1920,1080),Image.Resampling.NEAREST)
   x=col*1920;y=(k-1)*1130;board.paste(im,(x,y+50));d.text((x+12,y+12),f'{label} frame {14+k if col==0 else k-1}; source30fps / input60fps; central luma {luma:.3f}',fill='white')
   frames.append(dict(type=label,frame=14+k if col==0 else k-1,path=m.rel(p),sha256=m.sha(p),centralLuma=luma,nativeSize=list(size)))
 bp=OUT/'rate-aligned-source-input-board.png';board.save(bp)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),probe=probe,probeCommand=list(map(str,probeCmd)),source=dict(path=m.rel(source),sha256=m.sha(source)),sourceRate=30,inputRate=60,sourceStartSeconds=.5,sourceStartFrame=15,normalizedStartFrame=30,frames=frames,board=dict(path=m.rel(bp),sha256=m.sha(bp)),supersededWrongRateComparison=['part1-rivalry-opening-board-v338b.json','part1-rivalry-opening-repair-proposal-v339.json'],failedUnusedRepair='part1-rivalry-opening-repair-execution-v340.json',current333Unmodified=True)
 m.save(SP,state);print(json.dumps(dict(status=state['status'],sourceRate=30,current333Unmodified=True)))
except BaseException as e:
 state.update(status='failed',error=repr(e));m.save(SP,state);raise
