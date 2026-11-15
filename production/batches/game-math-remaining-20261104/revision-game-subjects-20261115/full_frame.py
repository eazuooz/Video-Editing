"""One selected encoded 1080p frame and its mobile layout, with exact provenance."""
from subject_revision import *

def main(eid,sid,fraction=.5,label=None):
 e=EPISODES[eid];p=work(e);enc=read(p/'encoded.json');movie=Path(enc['files']['captioned']['path'])
 s=next(x for x in e['scenes'] if x['scene']==sid);frame=round((s['start']+(s['end']-s['start'])*fraction)*60)
 out=p/'full-picture-qa'/(label or sid);out.mkdir(parents=True,exist_ok=True);receipt=out/'evidence.json'
 if receipt.exists():
  previous=read(receipt);assert previous['movieSha256']==enc['files']['captioned']['sha256']
  assert previous['frame']==frame,'Choose a distinct label for another exact frame; do not silently reuse a different time'
  return
 prefix=max(0,frame//60-1);local=frame-prefix*60
 target=out/'1080p.png';assert not target.exists()
 subprocess.run([str(FF),'-v','error','-nostdin','-n','-threads','1','-ss',str(prefix),'-i',str(movie),'-frames:v','1','-vf',f'select=eq(n\\,{local})','-threads','1',str(target)],check=True,creationflags=prior.CREATE)
 Image.open(target).resize((375,210),Image.Resampling.LANCZOS).save(out/'mobile.png')
 save(receipt,dict(episode=eid,scene=sid,frame=frame,time=frame/60,movieSha256=enc['files']['captioned']['sha256'],actuallyInspected=False,humanReviewed=False))
 print(target,flush=True)

if __name__=='__main__':
 import sys
 main(sys.argv[1],sys.argv[2],float(sys.argv[3]) if len(sys.argv)>3 else .5,sys.argv[4] if len(sys.argv)>4 else None)
