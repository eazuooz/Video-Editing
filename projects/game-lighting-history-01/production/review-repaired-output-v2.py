"""Extract only altered GOP ranges/joins; verify unchanged H.264 payloads."""
import pathlib,json,hashlib,datetime,av
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[3];O=R/'projects/game-lighting-history-01/production/local/final-edit-v1';D=O/'repair-v2';Q=D/'qa'
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 e=rd(D/'execution.json');assert e['exitCode']==0;assert not (D/'qa-execution.json').exists();Q.mkdir(exist_ok=True)
 ranges=e['captionPatchRanges'];old=rd(O/'encoded-qa/execution.json');plan=rd(D/'plan.json')
 # Identical encoded payload plus identical SPS/PPS and retained closed GOPs.
 def retained(p):
  result={}
  with av.open(str(p)) as c:
   s=c.streams.video[0];extra=s.codec_context.extradata
   for packet in c.demux(s):
    if packet.dts is None:continue
    if not any(a*1500-3000<=packet.dts<b*1500-3000 for a,b in ranges):result[packet.dts]=(packet.pts,hashlib.sha256(bytes(packet)).hexdigest())
  return extra,result
 a,base=retained(O/'captioned.mp4');b,cur=retained(D/'captioned.mp4');assert a==b and base==cur
 frames={x['frame'] for x in old['images'] if any(a<=x['frame']<b for a,b in ranges)}
 for a,b in ranges:frames.update([a-1,a,b-1,b]);frames.update(range(a,b,60))
 for n in plan['nodes']:
  if n['id'] in ['s014','s015','s018a','s018b','s076']:frames.update([n['startFrame']-1,n['startFrame'],n['endFrame']-1,n['endFrame']])
 images=[]
 for index,f in enumerate(sorted(frames),1):
  with av.open(str(D/'captioned.mp4')) as c:
   s=c.streams.video[0];s.codec_context.thread_count=2;c.seek(f*1500,stream=s,backward=True)
   for frame in c.decode(s):
    if frame.pts==f*1500:
     dest=Q/f'frame-{index:03}.png';frame.to_image().save(dest);images.append(dict(index=index,frame=f,path=dest.relative_to(R).as_posix(),sha256=sh(dest)));break
    assert frame.pts<=f*1500
   else:raise AssertionError(f)
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);boards=[]
 for start in range(0,len(images),6):
  rows=images[start:start+6];im=Image.new('RGB',(1920,1740),'#151515');draw=ImageDraw.Draw(im)
  for i,x in enumerate(rows):
   dx=(i%2)*960;dy=(i//2)*580;draw.text((dx+10,dy+8),f"{x['index']} frame{x['frame']}",font=font,fill='white');im.paste(Image.open(R/x['path']).resize((960,540)),(dx,dy+40))
  dest=Q/f'board-{len(boards)+1:03}.jpg';im.save(dest,quality=92);boards.append(dict(path=dest.relative_to(R).as_posix(),sha256=sh(dest),indices=[x['index'] for x in rows]))
 result=dict(status='extracted-awaiting-direct-review',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceSha256=e['outputs']['captioned']['sha256'],retainedPacketsVerified=len(cur),sameSpsPps=True,unchangedClosedGopPayloadsIdentical=True,allFinalPixelsApproved=False,images=images,boards=boards)
 (D/'qa-execution.json').write_text(json.dumps(result,indent=2)+'\n');print(len(images),'images',len(boards),'boards; retained packet equivalence',len(cur))
if __name__=='__main__':main()
