"""Inspect encoded annotation motion, joins, actual captions and mobile layout."""
from probe import *
import math,hashlib,sys
def main():
 d=rd(H/'annotations.json');state=rd(O/'pair/visual-execution.json');q=O/'qa';q.mkdir(exist_ok=True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);items=[]
 for w in d['windows']:
  if w['status']=='omitted':continue
  if len(sys.argv)>1 and w['id'] not in sys.argv[1:]:continue
  a,b=w['startFrame'],w['endFrame'];i=next(i for i,(lo,hi) in enumerate(state['windows']) if lo<=a and hi>=b);lo,hi=state['windows'][i]
  step=6 if w['id'] in ['character','robot-outer','csm-area'] else 15
  keys=w['keyframes'] if len(w['keyframes'])<40 else w['keyframes'][::step]
  fs=sorted(set([max(lo,a-1),a,min(a+5,b-1),b-1,min(hi-1,b)]+list(range(a,b,step))+[k['frame'] for k in keys if a<=k['frame']<b]))
  with av.open(str(O/f'pair/patch-{i}-captioned.mp4')) as c:
   c.streams.video[0].thread_type='AUTO'
   for page in range(math.ceil(len(fs)/12)):
    sub=fs[page*12:(page+1)*12];board=Image.new('RGB',(1440,4*300),'#141414');dr=ImageDraw.Draw(board)
    for j,f in enumerate(sub):
     im=frame(c,f-lo);x=j%3*480;y=j//3*300;board.paste(im.resize((480,270)),(x,y+26));dr.text((x+4,y+4),f'{w["id"]} {f/60:.3f}s',font=font,fill='white')
    path=q/f'{w["id"]}-{page}.jpg';board.save(path,quality=93)
   mid=(a+b)//2;im=frame(c,mid-lo);im.save(q/(w['id']+'.png'));im.resize((375,211)).save(q/(w['id']+'-375.png'))
  items.append(dict(id=w['id'],patch=i,start=(a-lo)/60,end=(b-lo)/60,frames=fs,boards=math.ceil(len(fs)/12)))
  print('QA',w['id'],len(fs),flush=True)
 if len(sys.argv)>1:
  old=rd(q/'index.json')['items'];by={x['id']:x for x in items};items=[by.get(x['id'],x) for x in old]
 wr(q/'index.json',dict(items=items,source='encoded patches; final packet identity verified by assembly',allMotionApproved=False))
 body='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>렌더링1편 · 표식 검수</title><style>body{background:#080b0b;color:white;font:18px sans-serif;margin:20px}video{width:min(96vw,1280px);display:block}button{padding:10px;margin:5px;font-size:17px}#status{margin:12px}select{font-size:18px} </style><h1>실제 영상 표식 · 인코딩 결과</h1><select id="choose"></select><button id="play">선택 구간 재생</button><button id="next">다음 구간</button><div id="status"></div><video id="v" controls muted></video><script>const items=ITEMS;const v=document.querySelector('#v');const select=document.querySelector('#choose');for(const [i,x] of items.entries()){select.add(new Option(x.id,i))}let active=0;function start(){active=+select.value;const x=items[active];v.src='../pair/patch-'+x.patch+'-captioned.mp4';v.onloadedmetadata=()=>{v.currentTime=Math.max(0,x.start-.1);v.play()}}document.querySelector('#play').onclick=start;document.querySelector('#next').onclick=()=>{select.value=(active+1)%items.length;start()};v.ontimeupdate=()=>{const x=items[active];document.querySelector('#status').textContent=x.id+' | '+v.currentTime.toFixed(2)+' / '+x.end.toFixed(2)+'초';if(v.currentTime>x.end+.15)v.pause()};</script>'''.replace('ITEMS',json.dumps(items))
 (q/'motion-review.html').write_text(body,'utf8')
if __name__=='__main__':main()
