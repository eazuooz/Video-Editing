"""Extract every changed caption/cut plus moving explanation states for direct review."""
import pathlib,json,hashlib,math
from fractions import Fraction
import av
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/review-v3';D=O/'qa';D.mkdir(exist_ok=True)
rd=lambda p:json.loads(p.read_text(encoding='utf8'))
def main():
 assert not (D/'index.json').exists()
 plan=rd(O/'plan.json');v=rd(O/'pair/visual-execution.json');assert v['status']=='complete-awaiting-mix-and-pixel-review'
 delta=plan['frames']-145768;mf=lambda f:f if f<=64119 else f+delta
 windows=[(mf(a),mf(b)) for a,b in v['windows']];points={}
 def add(f,why):
  if 0<=f<plan['frames']:points.setdefault(int(f),[]).append(why)
 for a,b in windows:
  for f in [a-1,a,a+1,b-1,b,b+1]:add(f,'closed GOP join')
 for n in plan['nodes']:
  if any(a<n['endFrame'] and n['startFrame']<b for a,b in windows):
   for f in [n['startFrame']-1,n['startFrame'],n['endFrame']-1,n['endFrame']]:add(f,'cut '+n['id'])
  if (n.get('anchor') or '').startswith('08-r') or n.get('anchor')=='03-p7':
   for f in range(n['startFrame']+30,n['endFrame'],120):add(f,'motion '+n['anchor'])
 for c in rd(O/'captions.json')['cues']['ko']:
  a,b=round(c['startSeconds']*60),round(c['endSeconds']*60)
  if any(x<b and a<y for x,y in windows):
   add(a+2,'caption onset '+str(c['index']));add((a+b)//2,'caption midpoint '+str(c['index']));add(b-2,'caption end '+str(c['index']))
 for h in plan['termHeaders']:
  for f in [h['startFrame'],h['startFrame']+30,h['endFrame']-1]:add(f,'canonical header '+h['key'])
 for r in rd(P/'production/review-v3/measured-scene-plan.json')['scenes']:
  n=next(n for n in plan['nodes'] if n.get('anchor')==r['key'])
  for s in r['sentences']:add(n['startFrame']+round(s['seconds'][0]*60)+5,'spoken step '+r['key'])
 items=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 with av.open(str(O/'pair/captioned-video.mp4')) as c:
  st=c.streams.video[0];st.thread_type='SLICE';st.codec_context.thread_count=2
  for i,(f,why) in enumerate(sorted(points.items())):
   c.seek(f*1500,stream=st,backward=True)
   for frame in c.decode(st):
    if frame.pts*st.time_base<Fraction(f,60):continue
    assert frame.pts*st.time_base==Fraction(f,60)
    im=frame.to_image();path=D/f'{f:06}.png';im.save(path);items.append(dict(frame=f,seconds=f/60,path=path.relative_to(R).as_posix(),reasons=why));break
   else:raise AssertionError(f)
  for bi in range(math.ceil(len(items)/12)):
   group=items[bi*12:(bi+1)*12];board=Image.new('RGB',(1920,4*390),(23,23,23));d=ImageDraw.Draw(board)
   for j,item in enumerate(group):
    im=Image.open(R/item['path']);x=j%3*640;y=j//3*390;board.paste(im.resize((640,360)),(x,y+30));d.text((x+8,y+3),str(item['frame'])+' · '+item['reasons'][0],font=font,fill='white')
   board.save(D/f'board-{bi:02}.jpg',quality=92)
  mobile=Image.new('RGB',(1500,4*241),(23,23,23));d=ImageDraw.Draw(mobile)
  samples=[items[round(i*(len(items)-1)/15)] for i in range(16)]
  for j,item in enumerate(samples):
   x=j%4*375;y=j//4*241;mobile.paste(Image.open(R/item['path']).resize((375,211)),(x,y+30));d.text((x+5,y+4),str(item['frame']),font=font,fill='white')
  mobile.save(D/'mobile-375.jpg',quality=95)
 index=dict(videoSha256=v['outputs']['captioned-video.mp4'],changedWindows=windows,items=items,boards=math.ceil(len(items)/12),reviewed=False,method='Every caption overlapping changed closed-GOP ranges at onset/midpoint/end; all cuts/joins; moving new explanations every2s and every spoken step; unchanged packet ranges reuse matching v2 review.')
 (D/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('QA frames',len(items),'boards',index['boards'])
if __name__=='__main__':main()
