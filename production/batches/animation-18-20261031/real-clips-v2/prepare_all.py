"""Rebuild all selected source-derived study definitions, without starting renders."""
from pathlib import Path
import subprocess,sys,json
H=Path(__file__).resolve().parent;L=H.parent/'local/real-clips-v2'
for script in ['prepare_series.py','prepare_supplements.py','prepare_a03.py','prepare_a02.py','prepare_a09.py','prepare_a15.py','prepare_direction.py']:
    subprocess.run([sys.executable,'-X','utf8',str(H/script)],check=True)
rows=[dict(key=p.stem,file=str(p)) for p in sorted((L/'studies').glob('A*.json')) if p.stem not in ('A04-jab','A11-upper')]
(L/'study-build-request.json').write_text(json.dumps(rows,indent=2),'utf-8')
print('Prepared definitions only:',len(rows))
