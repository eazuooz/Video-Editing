"""Keep the complete wrist paragraph visible; derive silhouette from actual coach pixels."""
from common import *
import visuals as v,render,qa,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from functools import lru_cache

base_draw=v.draw;base_points=qa.points

@lru_cache(1)
def body_silhouette():
 photo=v.detail('ring',150).crop((50,150,430,830))
 pixels=np.asarray(photo);mask=Image.fromarray((np.min(pixels,axis=2)<248).astype('uint8')*255).copy()
 seed=(220,290);assert mask.getpixel(seed)==255
 ImageDraw.floodfill(mask,seed,128)
 selected=np.asarray(mask)==128;ys,xs=np.where(selected)
 assert .1<selected.mean()<.6 and ys.min()<100 and ys.max()>600
 # Select the connected actual body; the disconnected instructional arrow,
 # card text and timer are excluded. Preserve the real empty space above the head.
 art=Image.new('RGB',photo.size,v.BG);art.paste(v.WHITE,mask=Image.fromarray(selected.astype('uint8')*255).copy())
 return photo,art

def draw(ep,row,span,local_frame,absolute_frame):
 seconds=absolute_frame/60;cues=row['bodyNarrationCues']
 if ep=='A08' and cues[60]['start']<=seconds<cues[64]['start']:
  im=v.backdrop(ep,span['key'],row['title'],'ring','wrist-bend').copy();d=ImageDraw.Draw(im)
  d.rectangle((55,93,1510,145),fill=v.BG);v.text(d,(55,103),'팔뚝 → 손목 → 손끝의 방향',33,v.TEAL,1440)
  v.principle_header(im,'팔뚝에서 손끝까지 이어지는 방향')
  v.graph_panel(im,'wrist-bend',min(.5,(seconds-cues[60]['start'])/4),span['key'],full=True)
  d.rectangle((55,752,1880,897),fill=v.BG);v.text(d,(960,835),'같은 팔뚝 · 다른 손끝 방향',41,v.YELLOW,1760,anchor='mm')
  for cx in [500,1400]:
   d.line((cx-52,585,cx+52,585),fill=v.WHITE,width=5);d.ellipse((cx-10,575,cx+10,595),fill=v.YELLOW)
  return im
 if ep=='A08' and cues[56]['start']<=seconds<cues[58]['start']:
  im=v.backdrop(ep,span['key'],row['title'],'ring','pose').copy();d=ImageDraw.Draw(im)
  v.text(d,(65,184),'실제 게임의 안내 자세',36,v.TEAL,880);v.text(d,(1030,184),'Silhouette (실루엣)',36,v.RED,830)
  photo,art=body_silhouette();v.fit(im,photo,(65,245,850,545));v.fit(im,art,(1030,245,820,545))
  v.text(d,(1030,815),'색을 단순화해 팔과 몸 사이의 빈 공간 확인',28,v.MUTED,820)
  return im
 return base_draw(ep,row,span,local_frame,absolute_frame)
v.draw=draw;render.draw=draw

def points(e,audio):
 rows=base_points(e,audio);index={r['frame']:r for r in rows}
 for t,role in [(239,'study:actual-coach-silhouette'),(257,'study:continuous-wrist-comparison')]:
  n=map_frame(round(t*60),audio['changes']);index.setdefault(n,dict(frame=n,roles=[]))['roles'].append(role)
 return [index[n] for n in sorted(index)]
qa.points=points

def main(preview=False):
 plan=read(HERE/'plan.json');e=next(e for e in plan['episodes'] if e['id']=='A08')
 for s in e['studyDefinitions'].values():s.update(rendererAdapter=str(Path(__file__)),rendererAdapterSha256=sha(__file__))
 e['queuedVisualEnhancement']=dict(stage='previewed-pending-encode',reason='Keep the complete253.753–270.903s wrist explanation on one consistent hand-axis comparison instead of swapping back when the word wrist is absent. Show actual coach silhouette at238.273–245.988s.',silhouetteSource='ring bank150, connected nonwhite body pixels; disconnected arrow/text/timer excluded',audioChanged=False)
 save(HERE/'plan.json',plan)
 if preview:
  for name,t in [('silhouette',239),('wrist',257)]:
   old=round(t*60);s=next(s for s in e['replacementSpans'] if s['start']<=old<s['end']);new=map_frame(old,read(WORK/'A08/audio.json')['changes'])
   im=draw('A08',e,dict(s,newFrame=new),120,old);im.save(WORK/'A08'/('clarified-'+name+'.png'));im.resize((375,211)).save(WORK/'A08'/('clarified-'+name+'-mobile.png'))
  return
 render.render_episode(e)
 plan=read(HERE/'plan.json');next(e for e in plan['episodes'] if e['id']=='A08')['queuedVisualEnhancement']['stage']='encoded-awaiting-internal-review';save(HERE/'plan.json',plan)
if __name__=='__main__':main('--preview' in sys.argv)
