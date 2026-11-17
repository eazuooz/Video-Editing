"""Serialize the selected build, voice and final film without touching other apps."""
from pathlib import Path
import json,time,subprocess,sys
H=Path(__file__).resolve().parent;R=H.parents[2];PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def run(args):
 print('START',str(args[1]),flush=True)
 subprocess.run(list(map(str,args)),cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
report=H/'local/living-room-v10/web-build.json'
while not report.exists():time.sleep(8)
j=json.loads(report.read_text('utf-8-sig'));assert j['result']=='Succeeded' and j['errors']==0,j
run([sys.executable,'-X','utf8',H/'prepare-web-v10-delivery.py'])
run([sys.executable,H/'sofa-v10-tools.py','exit'])
# The Editor processes the normal exit message before the GPU identity check.
import psutil
while any((p.info.get('name') or '').lower()=='unity.exe' and 'Unity Hub' not in (p.info.get('exe') or '') for p in psutil.process_iter(['name','exe'])):time.sleep(3)
run([PY,'-X','utf8','-u',H/'render-tutorial-v3-voice.py'])
run([PY,'-X','utf8','-u',H/'render-tutorial-v3-voice.py','--finish-film'])
run([sys.executable,'-X','utf8','-u',H/'verify-tutorial-v3-after-render.py'])
print('SOFA V4 FULL LOCAL MEDIA COMPLETE',flush=True)
