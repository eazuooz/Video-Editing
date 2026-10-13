"""One local-only atlas of authored action states from the encoded assets."""
import pathlib,json,hashlib,datetime
import av
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01/production';O=P/'local/threejs-revision-v1/asset-review';O.mkdir(parents=True,exist_ok=True)
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'index.json').exists(),'Reuse the existing review atlas'
timing=rd(R/'motion-canvas/src/projects/game-lighting-history-01/explanation-assets-v1/data.json');blocks={b['paragraphKey']:b for c in timing['chapters'] for b in c['blocks']}
records=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
assets=rd(P/'local/threejs-revision-v1/three/execution.json')['completed']+rd(P/'local/threejs-revision-v1/manim/execution.json')['completed']
for a in assets:
 b=blocks[a['key']];frames=sorted(set([0,b['frames']-1]+[min(b['frames']-1,s['actionStartFrame']+s['actionDurationFrames']) for s in b['actionSteps']]))
 with av.open(str(R/a['path'])) as c:
  v=c.streams.video[0];v.thread_type='SLICE';v.codec_context.thread_count=1
  for target in frames:
   c.seek(int(target/60/v.time_base),stream=v,backward=True)
   frame=next(f for f in c.decode(v) if round(f.pts*f.time_base*60)>=target)
   observed=round(frame.pts*frame.time_base*60);assert observed==target,(a['key'],target,observed)
   image=frame.to_image();file=O/f'{a["key"]}-{target:05d}.png';image.save(file)
   records.append({'key':a['key'],'frame':target,'path':file.relative_to(R).as_posix(),'sha256':sh(file),'assetSha256':a['sha256']})
boards=[]
for j in range(0,len(records),4):
 group=records[j:j+4];board=Image.new('RGB',(1920,1152),'#191919');d=ImageDraw.Draw(board)
 for k,x in enumerate(group):
  col,row=k%2,k//2;im=Image.open(R/x['path']).resize((960,540),Image.Resampling.LANCZOS);board.paste(im,(col*960,row*576+36));d.text((col*960+10,row*576+6),f'{x["key"]}  frame {x["frame"]}',font=font,fill='white')
 file=O/f'board-{j//4+1:02d}.png';board.save(file);boards.append({'path':file.relative_to(R).as_posix(),'sha256':sh(file),'items':group})
index={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assets':len(assets),'images':records,'boards':boards,'directlyReviewed':False,'movingPlaybackReviewed':False,'finalCaptionPixelsReviewed':False,'localOnly':True}
(O/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n','utf8');print(len(records),'encoded states',len(boards),'boards')
