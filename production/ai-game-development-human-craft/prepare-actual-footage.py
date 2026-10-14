"""Inspect/normalize exact selected source cuts. Never loop or slow footage."""
from pathlib import Path
import argparse,json,subprocess,hashlib,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft';FLAGS=subprocess.CREATE_NO_WINDOW
p=argparse.ArgumentParser();p.add_argument('--normalize',action='store_true');p.add_argument('--inspect',action='store_true');a=p.parse_args()
plan=ROOT/f'projects/{SLUG}/planning/actual-footage-plan.json';d=json.loads(plan.read_text(encoding='utf-8'))
assert d['actualFrames']==d['targetActualFrames']
from revision_paths import workroot
out=workroot(ROOT)/'actual-footage';out.mkdir(parents=True,exist_ok=True)
review=out/'review';review.mkdir(exist_ok=True)
def run(args):return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=FLAGS)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_info={};images=[];records=[]
for cut in d['cuts']:
 source=ROOT/cut['sourcePath'];key=cut['source']
 if key not in source_info:
  probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]).stdout)
  source_info[key]={'sha256':sha(source),'duration':float(probe['format']['duration'])}
 assert cut['sourceOutSeconds']<=source_info[key]['duration']+.02,cut['id']
 if a.inspect:
  # Every selected cut, at four-second intervals and both boundaries.
  stamps=sorted(set([.1,max(.1,cut['frames']/60-.15)]+[i+2 for i in range(0,math.floor(cut['frames']/60-2),4)]))
  for i,local in enumerate(stamps):
   path=review/f'{cut["id"]}-{i:02d}.jpg';stamp=cut['sourceInSeconds']+local
   if not path.exists():run(['ffmpeg','-v','error','-ss',str(stamp),'-i',str(source),'-frames:v','1','-vf','scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2','-q:v','3',str(path)])
   images.append({'cut':cut['id'],'source':key,'sourceTime':stamp,'localTime':local,'path':path.relative_to(ROOT).as_posix()})
 if a.normalize:
  target=out/(cut['id']+'.mp4');receipt=out/(cut['id']+'.json')
  inputs={'cut':cut,'sourceSha256':source_info[key]['sha256'],'vf':'fps=60,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1','encoder':'h264_nvenc-p5-cq18'}
  if target.exists():assert receipt.exists() and json.loads(receipt.read_text(encoding='utf-8'))['inputs']==inputs,'Changed existing clip: '+cut['id']
  else:
   run(['ffmpeg','-v','error','-n','-ss',str(cut['sourceInSeconds']),'-i',str(source),'-an','-vf',inputs['vf'],'-frames:v',str(cut['frames']),'-c:v','h264_nvenc','-preset','p5','-cq','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)])
   probe=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(target)]).stdout);v=probe['streams'][0]
   assert int(v['nb_frames'])==cut['frames'],(cut['id'],v['nb_frames'])
   receipt.write_text(json.dumps({'inputs':inputs,'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'frames':int(v['nb_frames'])},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  records.append(dict(cut,path=target.relative_to(ROOT).as_posix(),sha256=json.loads(receipt.read_text(encoding='utf-8'))['sha256']))
 print(cut['id'],flush=True)
if images:
 for page in range(math.ceil(len(images)/12)):
  canvas=Image.new('RGB',(1920,1560),'#151515');draw=ImageDraw.Draw(canvas)
  for i,row in enumerate(images[page*12:(page+1)*12]):
   x=i%3*640;y=i//3*390;canvas.paste(Image.open(ROOT/row['path']),(x,y));draw.text((x+7,y+366),f'{row["cut"]} {row["source"]} {row["sourceTime"]:.2f}s (+{row["localTime"]:.2f})',fill='white')
  canvas.save(review/f'contact-{page+1:02d}.jpg',quality=92)
 (review/'mapping.json').write_text(json.dumps({'planSha256':sha(plan),'samples':images,'pages':math.ceil(len(images)/12)},indent=2)+'\n',encoding='utf-8')
if records:
 (out/'selection.json').write_text(json.dumps({'planSha256':sha(plan),'cuts':records,'actualFrames':sum(r['frames'] for r in records)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
