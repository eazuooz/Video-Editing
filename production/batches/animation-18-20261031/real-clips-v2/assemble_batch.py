"""Sequential assembly of the explicitly selected animation revisions."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,sys,json
H=Path(__file__).resolve().parent;L=H.parent/'local/real-clips-v2'
episodes=sys.argv[1:] or ['A02','A03','A04','A05','A06','A07','A08','A09','A10','A11','A13','A14','A15','A16']
allowed={f'A{i:02}' for i in range(2,17)}-{'A12'}
assert set(episodes)<=allowed
status={'startedAt':datetime.now(timezone.utc).isoformat(),'episodes':episodes,'completed':[],'humanReviewed':False}
for ep in episodes:
    status['current']=ep;(L/'assembly-progress.json').write_text(json.dumps(status,indent=2),'utf-8')
    print('Starting',ep,flush=True)
    subprocess.run([sys.executable,'-X','utf8',str(H/'assemble_revision.py'),ep],check=True)
    subprocess.run([sys.executable,'-X','utf8',str(H/'review_frames.py'),ep],check=True)
    status['completed'].append(ep)
status['current']=None;status['endedAt']=datetime.now(timezone.utc).isoformat()
(L/'assembly-progress.json').write_text(json.dumps(status,indent=2),'utf-8')
