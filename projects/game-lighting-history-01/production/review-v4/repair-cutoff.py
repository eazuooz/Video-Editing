"""Clear the torso contour before the rapid orbit; retain every other patch."""
from assemble import *
import shutil
import overlay

def main():
 old=rd(H/'annotations.json');s=rd(D/'visual-execution.json')
 assert rd(D/'execution.json')['status']=='complete-awaiting-encoded-pixels'
 for src,name in [(H/'annotations.json','annotations-before-cutoff.json'),(O/'annotations.ass','annotations-before-cutoff.ass')]:
  assert not (O/name).exists();shutil.copyfile(src,O/name)
 w=next(w for w in old['windows'] if w['id']=='robot-outer')
 assert w['endFrame']==round(1021.05*60)
 w['endFrame']=round(1020.85*60)
 w['keyframes'][-1]['frame']=w['endFrame']
 wr(H/'annotations.json',old)
 source=H/'layout.py';text=source.read_text('utf8');assert text.count('1021.05')==2
 source.write_text(text.replace('1021.05','1020.85'),'utf8')
 overlay.build()
 new=rd(H/'annotations.json');before=rd(O/'annotations-before-cutoff.json')
 assert {a['id'] for a,b in zip(before['windows'],new['windows']) if a!=b}=={'robot-outer'}
 strip=lambda p:[l for l in p.read_text('utf-8-sig').splitlines() if ',Guide,robot-outer,' not in l]
 assert strip(O/'annotations-before-cutoff.ass')==strip(O/'annotations.ass')
 i=next(i for i,(a,b) in enumerate(s['windows']) if a<=w['startFrame'] and b>=w['endFrame'])
 dest=O/'superseded-pass2';dest.mkdir(exist_ok=False)
 paths=[D/n for n in ['visual-execution.json','execution.json','visual.mp4','captioned-video.mp4','clean.mp4','captioned.mp4',f'patch-{i}-clean.mp4',f'patch-{i}-captioned.mp4']]
 for path in paths:
  path.resolve().relative_to(O.resolve());target=(dest/path.name).resolve();target.relative_to(O.resolve());assert not target.exists();path.rename(target)
 s['completed']=[x for x in s['completed'] if x not in [f'{i}-clean',f'{i}-captioned']];s['outputs']={};s['retainedPackets']={}
 s['inputs']['annotationSha256']=sha(H/'annotations.json');s['inputs']['assSha256']=sha(O/'annotations.ass');s['status']='encoding-selected-ranges'
 s['targetedRepair']={'window':i,'reason':'Clear contour before fast torso orbit; preserve all other encoded patches.','unaffectedAssEventsIdentical':True}
 wr(D/'visual-execution.json',s);print('Only patch invalidated:',i)
if __name__=='__main__':main()
