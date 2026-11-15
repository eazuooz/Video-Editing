"""Finite, serialized final visual corrections for this authorized revision only."""
from common import *
import sys,subprocess
JOBS=[('A04','render_a04_detail.py'),('A05','render_a05_principles.py'),('A08','render_a08_wrist.py'),('A13','render_a13_guard.py'),('A14','render_a14_glyph.py'),('A16','render_a16_weapon.py')]
def main():
 # Main batch must already have stopped. The caller verifies its completion.
 for ep,script in JOBS:
  c=read(ROOT/'shared/publishing/video-production-control.json')[KEY]
  assert c['renderAuthorized'] and ep in c['scope'] and not c['youtubeAuthorized']
  p=WORK/'scoped-jobs.json';state=read(p) if p.exists() else dict(completed=[])
  if ep in state['completed']:continue
  state.update(current=ep,script=script,stage='encoding',updatedAt=stamp());save(p,state)
  print('SCOPED START',ep,script,flush=True)
  r=subprocess.run([sys.executable,'-X','utf8',str(HERE/script)],creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  if r.returncode:raise RuntimeError((ep,script,r.returncode))
  state['completed'].append(ep);state.update(stage='encoded-awaiting-internal-review',updatedAt=stamp());save(p,state)
  print('SCOPED DONE',ep,flush=True)
 print('All scoped visual encodes finished. User review is still pending.',flush=True)
if __name__=='__main__':main()
