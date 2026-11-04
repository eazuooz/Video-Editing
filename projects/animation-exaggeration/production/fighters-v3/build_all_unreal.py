"""Only the six selected A02 explanations, with isolated saved assets."""
from pathlib import Path
import sys,subprocess,json
H=Path(__file__).resolve().parent;L=H.parent/'local/fighters-v3'
for cid in ['A02-E015','A02-E004','A02-E005','A02-E011','A02-E013','A02-E014']:
 (L/'unreal/build-job.json').write_text(json.dumps({'id':cid}))
 subprocess.run([sys.executable,'-u','-X','utf8',str(H/'run_unreal_job.py'),'build_unreal_stage.py','--wait'],check=True)
 print('BUILT',cid,flush=True)
