"""Scan the visible gameplay area in every current cut, excluding black margins."""
from pathlib import Path
import subprocess,json,re,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';O=P/'production/local/reference-preserving-v2/edit';plan=json.loads((P/'production/reference-preserving-v2/edit-plan.json').read_text());rows=[]
for c in plan['cuts']:
 if c['kind']!='independent-gameplay':continue
 f=O/(c['id']+'.mp4');r=subprocess.run(['ffmpeg','-hide_banner','-i',str(f),'-an','-vf','crop=1600:900:160:0,blackdetect=d=0.05:pic_th=0.95:pix_th=0.08','-f','null','-'],capture_output=True,check=True)
 log=r.stderr.decode(errors='replace');flags=re.findall(r'black_start:[^\r\n]+',log)
 rows.append({'cut':c['id'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'frames':c['frames'],'blackRegions':flags})
out={'scope':'All current independent-gameplay cuts, visible1600x900 region; >=3frame near-black transitions','rows':rows,'passed':not any(r['blackRegions'] for r in rows)};(O/'qa/gameplay-blackouts.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cuts':len(rows),'passed':out['passed'],'flags':[r for r in rows if r['blackRegions']]}));assert out['passed']
