"""Extract only changed-visual/caption/transition evidence from the final pair."""
from pathlib import Path
import argparse,json,math,hashlib,re,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).resolve().parents[4]
M=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def ts(s):
 h,m,v=s.split(':');return 3600*int(h)+60*int(m)+float(v.replace(',','.'))
def balance(parts):
 if len(parts)==1:return parts[0]
 k=len(parts)//2;return '('+balance(parts[:k])+'+'+balance(parts[k:])+')'

ap=argparse.ArgumentParser();ap.add_argument('--slug',required=True,choices=['limited-color-world','computer-controlled-players']);ap.add_argument('--version',default='v1');a=ap.parse_args()
out=M/a.slug/('composite-'+a.version);build=read(out/'pair-build.json');file=Path(build['outputs']['captioned']['path']);assert sha(file)==build['outputs']['captioned']['sha256']
plan=read(R/'projects'/a.slug/'production/unity-visual-v2/visual-plan.json')
qa=out/'qa';png=qa/'frames';png.mkdir(parents=True,exist_ok=True)
cuts=[c for c in plan['cuts'] if c['operation']=='replace-explanation-visual'];frames=set();rows={};caption_ranges=[]
src=R/next(f['path'] for f in plan['frozenInputs'] if f['key']=='captionsKo')
for block in re.split(r'\n\s*\n',src.read_text('utf-8-sig').strip()):
 lines=block.splitlines()
 if len(lines)<3:continue
 start,end=lines[1].split(' --> ');caption_ranges.append((ts(start),ts(end),' '.join(lines[2:])))
for c in cuts:
 local={0,min(30,c['frames']-1),*[int((c['frames']-1)*r) for r in [.2,.4,.6,.8,1]]}
 if a.slug=='computer-controlled-players' and c['id']=='cut032':local|={155,156,157,167,168,169}
 if a.slug=='computer-controlled-players' and c['id']=='cut024':local|={315,316,470,471,581,582,612}
 if a.slug=='limited-color-world' and c['id']=='cut015':local|={2,3,50,51,92,93,94}
 for cue in c.get('speechCueSecondsWithinCut',[]):
  if 0<=cue<c['frames']/60:local.add(min(c['frames']-1,round(cue*60)+2))
 cutframes={c['startFrame']+x for x in local}
 for start,end,text in caption_ranges:
  lo=max(c['startFrame']/60,start);hi=min(c['endFrame']/60,end)
  if hi>lo:cutframes.add(min(c['endFrame']-1,round((lo+hi)*30)))
 cutframes|={c['startFrame']-1,c['endFrame']}
 rows[c['id']]=sorted(cutframes);frames|=cutframes
ordered=sorted(frames);assert ordered
receipt=qa/'frame-index.json'
if not receipt.exists():
 assert not list(png.glob('*.png')),'Preserve incomplete prior QA; choose new output version'
 select=balance([f'eq(n\\,{n})' for n in ordered])
 cmd=[shutil.which('ffmpeg'),'-hide_banner','-nostdin','-v','warning','-threads','3','-i',str(file),'-an','-vf','select='+select,'-fps_mode','passthrough','-frames:v',str(len(ordered)),'-compression_level','1','-threads','2','-n',str(png/'%04d.png')]
 subprocess.run(cmd,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 mapping={f:png/f'{i+1:04d}.png' for i,f in enumerate(ordered)}
 assert len(list(png.glob('*.png')))==len(ordered)
 receipt.write_text(json.dumps({'master':str(file),'masterSha256':sha(file),'scope':'Every changed cut: all7temporal states, spoken cue boundaries, every overlapping caption midpoint and neighbouring cut edges.','frames':[{'frame':f,'time':f/60,'path':str(p),'sha256':sha(p)} for f,p in mapping.items()],'cuts':rows},ensure_ascii=False,indent=2)+'\n','utf-8')
else:
 old=read(receipt);assert old['masterSha256']==sha(file);mapping={x['frame']:Path(x['path']) for x in old['frames']}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for cid,group in rows.items():
 for page in range(math.ceil(len(group)/8)):
  subset=group[page*8:page*8+8]
  for width in [375,640]:
   height=round(width*1080/1920);board=Image.new('RGB',(width*2,(height+26)*math.ceil(len(subset)/2)),(20,20,20));d=ImageDraw.Draw(board)
   for i,f in enumerate(subset):
    im=Image.open(mapping[f]).convert('RGB').resize((width,height),Image.Resampling.LANCZOS);x=i%2*width;y=i//2*(height+26);board.paste(im,(x,y));d.text((x+4,y+height+2),f'{cid} {f}f {f/60:.3f}s',font=font,fill='white')
   board.save(qa/f'{cid}-{width}-{page+1:02}.jpg',quality=95)
print(json.dumps({'slug':a.slug,'master':str(file),'changedCuts':len(cuts),'nativeFrames':len(ordered),'qa':str(qa)}))
