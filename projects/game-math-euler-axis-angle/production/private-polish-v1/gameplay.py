"""Retain the original FHD cuts; draw verified screen guides only at matched speech."""
import argparse,copy,math
import common as c
b=c.module('original_guide_renderer',c.P/'production/revision-v2/render-edit.py')
SOURCE=c.P/'production/local/revision-v2/sources/FvSgGn941U0.mp4'
SOURCE_HASH='971fe625c85eb7eb178cb945568dbb2541240eb9cd1f744252b04fdff67975ed'
G=c.O/'gameplay';G.mkdir(exist_ok=True)

def ass(cut,windows):
 events=[];marks=[];duration=cut['frames']/60
 for w in windows:
  if w['scene']!=cut['scene']:continue
  low=max(w['sourceIn'],cut['sourceIn']);high=min(w['sourceOutExclusive'],cut['sourceIn']+duration)
  if high<=low:continue
  a,z=low-cut['sourceIn'],high-cut['sourceIn'];label=w['label']
  events.append(f'Dialogue: 4,{b.stamp(a)},{b.stamp(z)},Label,,0,0,0,,{{\\pos(100,130)}}'+label)
  events.append(f'Dialogue: 4,{b.stamp(a)},{b.stamp(z)},Label,,0,0,0,,{{\\pos(100,196)\\fs32}}화면 관찰용 안내선')
  for f in range(math.ceil(a*60),min(cut['frames'],math.ceil(z*60))):
   t=cut['sourceIn']+f/60;p=b.interpolate(w['keyframes'],t)
   if not p:continue
   cx,cy=p['center'];rx,ry=p['ellipseRadius']
   reveal=min(1,(f/60-a+.0167)/.35)
   angles=[-math.pi/2+math.tau*reveal*i/48 for i in range(49)]
   # ASS closes polygons. A filled annular strip avoids a false chord across
   # the observed body while the ring is being traced.
   pts=[(cx+(rx+5)*math.cos(q),cy+(ry+5)*math.sin(q)) for q in angles]
   pts += [(cx+(rx-5)*math.cos(q),cy+(ry-5)*math.sin(q)) for q in reversed(angles)]
   path='m '+' '.join(('' if i==0 else 'l ')+f'{x:.2f} {y:.2f}' for i,(x,y) in enumerate(pts))
   events.append(f'Dialogue: 2,{b.stamp(f/60)},{b.stamp((f+1)/60)},Guide,,0,0,0,,{{\\an7\\pos(0,0)\\1a&H00&\\1c&H57D5F4&\\bord2\\3c&H101010&\\p1}}'+path)
   # Leader points to the ring boundary, never paints over the observed limbs.
   dx,dy=cx-650,cy-170;scale=1/math.sqrt((dx/rx)**2+(dy/ry)**2)
   target=(cx-dx*scale,cy-dy*scale)
   leaders=['m 100 185 l 650 185',f'm 650 185 l {target[0]:.2f} {target[1]:.2f}']
   for leader in leaders:
    for color,layer,width in [('101010',1,5),('57D5F4',2,2.5)]:events.append(b.guide_event(f/60,(f+1)/60,leader,color,layer,width))
   if cut['scene']=='20':
    events.append(b.guide_event(f/60,(f+1)/60,b.ellipse(cx,cy,8,8),'E8A354',3,5))
    past=[k['center'] for k in w['keyframes'] if low<=k['sourceTime']<=t]+[[cx,cy]]
    if len(past)>1:
     for first,last in zip(past,past[1:]):
      trail=f'm {first[0]:.2f} {first[1]:.2f} l {last[0]:.2f} {last[1]:.2f}'
      events.append(b.guide_event(f/60,(f+1)/60,trail,'E8A354',3,4))
  marks.append({'sourceWindow':[low,high],'label':label,'meaning':w['meaning'],
    'originalSpeech':w['narrationCueText'],'keyframes':w['keyframes'],'clearAtCut':True})
 return b.HEADER+'\n'.join(events)+'\n',marks

def main():
 c.authorized();ap=argparse.ArgumentParser();ap.add_argument('--scene',action='append');args=ap.parse_args()
 assert c.sha(SOURCE)==SOURCE_HASH
 v=c.video(SOURCE);assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 windows=c.read(c.P/'sources/annotation-plan-v2.json')['windows'];report=[]
 for sid,s in c.SCENES.items():
  if not s.get('cuts') or (args.scene and sid not in args.scene):continue
  files=[];cuts=[]
  for j,original in enumerate(s['cuts']):
   cut={**original,'scene':sid};name=f'{sid}-{j+1:02}';path=G/f'{name}.ass';target=G/f'{name}.mp4';receipt=G/f'{name}.json'
   body,marks=ass(cut,windows);path.write_text(body,encoding='utf8')
   sig={'sourceHash':SOURCE_HASH,'sourceIn':cut['sourceIn'],'frames':cut['frames'],'assHash':c.sha(path),'encoder':c.ENC}
   if not(target.exists() and receipt.exists() and c.read(receipt)==sig):
    c.ff(['-ss',cut['sourceIn'],'-i',SOURCE,'-vf',f'fps=60,setsar=1,ass={path.name}',
          '-frames:v',cut['frames'],'-an',*c.ENC,target],f'gameplay-{name}.log',G);c.save(receipt,sig)
   assert int(c.video(target)['nb_frames'])==cut['frames']
   files.append(target);cuts.append({'originalCut':original,'file':c.rel(target),'sha256':c.sha(target),'guides':marks})
  concat=G/f'{sid}-concat.txt';concat.write_text('\n'.join("file '"+x.as_posix()+"'" for x in files)+'\n',encoding='utf8')
  c.ff(['-f','concat','-safe','0','-i',concat,'-c','copy','-an','-video_track_timescale','60000','-movflags','+faststart',c.O/'clips'/f'{sid}.mp4'],f'gameplay-{sid}-concat.log')
  assert int(c.video(c.O/'clips'/f'{sid}.mp4')['nb_frames'])==s['frames']
  report.append({'scene':sid,'frames':s['frames'],'cuts':cuts});print('Original gameplay restored + guides',sid,flush=True)
 c.save(c.H/'gameplay-placement.json',{'source':c.rel(SOURCE),'sourceSha256':SOURCE_HASH,'decoded':[1920,1080,60],
  'narrationAndOriginalCutsUnchanged':True,'sourceSpeed':1,'screenSpaceEditorialGuidesOnly':True,
  'descriptionCredit':'Superflight gameplay — Morkala; https://www.youtube.com/watch?v=FvSgGn941U0 (free-to-use uploader gameplay)',
  'sourceAudioUsed':False,'noNewOnScreenCreditLine':True,'reports':report})

if __name__=='__main__':main()
