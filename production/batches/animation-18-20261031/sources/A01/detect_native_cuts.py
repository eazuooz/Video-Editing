from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, json, re
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
core=json.loads((P/'selected-footage.json').read_text(encoding='utf-8'))['sources']
extra=json.loads((P/'additional-fighters-inventory.json').read_text(encoding='utf-8'))
items={**core,**extra}
def run(item):
 key,s=item
 cmd=['ffmpeg','-hide_banner','-threads','2','-i',s['path'],'-vf',"scale=320:-2,select='gt(scene,0.20)',showinfo",'-an','-f','null','-']
 r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
 ts=[float(x) for x in re.findall(r'pts_time:([0-9.]+)',r.stderr)]
 (P/f'cut-detector-{key}.log').write_text(r.stderr,encoding='utf-8')
 print(key,ts,flush=True)
 return key,{'candidates':ts,'returnCode':r.returncode,'method':'FFmpeg scene threshold .20 at 320px; detector candidates, NOT automatically verified edits'}
with ThreadPoolExecutor(max_workers=2) as pool: out=dict(pool.map(run,items.items()))
(P/'native-cut-detector.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
