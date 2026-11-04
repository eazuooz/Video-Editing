from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent
for cid in ['A02-E015','A02-E004','A02-E005','A02-E011','A02-E013','A02-E014']:
 subprocess.run([sys.executable,'-u','-X','utf8',str(H/'render_unreal.py'),cid],check=True)
 subprocess.run([sys.executable,'-u','-X','utf8',str(H/'compose_unreal.py'),cid],check=True)
 print('CAPTURED AND COMPOSED',cid,flush=True)
