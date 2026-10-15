"""Invalidate only the changed character GOP, preserving the first pass evidence."""
from assemble import *
def main():
 old=rd(O/'annotations-before-tracking-fix.json');new=rd(H/'annotations.json')
 oldrows={w['id']:w for w in old['windows']};newrows={w['id']:w for w in new['windows']}
 assert {k for k in oldrows if oldrows[k]!=newrows[k]}=={'character'}
 strip=lambda p:[l for l in p.read_text('utf-8-sig').splitlines() if ',Guide,character,' not in l]
 assert strip(O/'annotations-before-tracking-fix.ass')==strip(O/'annotations.ass')
 s=rd(D/'visual-execution.json');w=newrows['character'];i=next(i for i,(a,b) in enumerate(s['windows']) if a<=w['startFrame'] and b>=w['endFrame'])
 dest=O/'superseded-pass1';dest.mkdir(exist_ok=False)
 paths=[D/'visual-execution.json',D/'visual.mp4',D/'captioned-video.mp4',D/f'patch-{i}-clean.mp4',D/f'patch-{i}-captioned.mp4']
 for path in paths:
  path.resolve().relative_to(O.resolve());target=(dest/path.name).resolve();target.relative_to(O.resolve());assert not target.exists();path.rename(target)
 s['completed']=[x for x in s['completed'] if x not in [f'{i}-clean',f'{i}-captioned']];s['outputs']={};s['retainedPackets']={}
 s['inputs']['annotationSha256']=sha(H/'annotations.json');s['inputs']['assSha256']=sha(O/'annotations.ass');s['status']='encoding-selected-ranges'
 s['targetedRepair']={'window':i,'reason':'Sparse manual keys lagged behind actual selected character; per-frame observed anchor and label clearance repair.','unaffectedAssEventsIdentical':True}
 wr(D/'visual-execution.json',s);print('Only patch invalidated:',i)
if __name__=='__main__':main()
