"""Native-action-only variant of the established split-screen renderer."""
from pathlib import Path
import importlib.util,sys,math
spec=importlib.util.spec_from_file_location('base',Path(__file__).resolve().parent.parent/'render-patches.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=m.guides
def guides(p,s):
 text=original(p,s)
 rows=[]
 def event(a,b,t,layer=3):
  rows.append(f'Dialogue: {layer},{m.stamp(a)},{m.stamp(b)},Default,,0,0,0,,{t}')
 for a,b,label in p.get('phases',[]):
  event(a,b,'{\\pos(36,862)\\fs39\\1c&HA2D380&}'+label)
 for track in p.get('tracks',[]):
  for one,two in zip(track['points'],track['points'][1:]):
   a,x,y,r=one;b,xx,yy,rr=two;k=r*.55228475
   shape=f'm 0 {r} b 0 {r-k} {r-k} 0 {r} 0 b {r+k} 0 {2*r} {r-k} {2*r} {r} b {2*r} {r+k} {r+k} {2*r} {r} {2*r} b {r-k} {2*r} 0 {r+k} 0 {r}'
   event(a,b,'{\\an7\\move('+f'{x*1280-r:.1f},{130+y*720-r:.1f},{xx*1280-r:.1f},{130+yy*720-r:.1f}'+')\\p1\\bord5\\shad0\\1a&HFF&\\3c&HA2D380&}'+shape,1)
 return text+'\n'.join(rows)+'\n'
if __name__=='__main__':
 p=m.read(sys.argv[1]);assert p['revision']=='gameplay-motion-v4'
 for patch in p['patches']:
  assert all(s['kind']=='motion' for s in patch['segments']), 'No freeze padding in this revision'
  assert patch.get('sourceReview') and patch.get('speechMapping'), 'Inspect source action and speech first'
 m.guides=guides;m.main()
