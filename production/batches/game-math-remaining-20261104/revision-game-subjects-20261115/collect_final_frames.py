"""Finite read-only movie sampling; never approves an episode."""
from subject_revision import *
import full_frame,motion_samples

def main():
 deadline=time.monotonic()+7200;rows=[]
 for eid,sid,fraction,motion_sid in [('M30','057',.85,'017'),('M31','013',.5,'013'),('M32','003',.85,'010'),('M33','029',.85,'029')]:
  p=work(EPISODES[eid])
  while not (p/'encoded.json').exists():
   assert time.monotonic()<deadline,'Finite snapshot wait expired; no review assumed'
   time.sleep(2)
  full_frame.main(eid,sid,fraction);motion_samples.main(eid,motion_sid)
  rows.append(dict(episode=eid,fullScene=sid,fraction=fraction,motionScene=motion_sid,status='extracted-needs-actual-viewing'))
  save(HERE/'snapshot-collection.json',dict(scope='M30–M33 final movie snapshots only',episodes=rows,humanReviewed=False,actuallyInspected=False))
  print(eid,'final frame/motion evidence extracted; actual viewing still pending',flush=True)
if __name__=='__main__':main()
