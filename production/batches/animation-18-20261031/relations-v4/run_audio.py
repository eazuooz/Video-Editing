"""Serialize only the new narration and its independent ASR readback."""
from pathlib import Path
import json,sys,time,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
control=json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))['animationRelationsRevision20261108']
assert control['ttsAuthorized'] and control['episodes']==['A'+str(n).zfill(2) for n in range(1,19)]
sys.path.insert(0,str(R/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
while True:
 try:schedule_gpu_handoff('animation-relations-v4','cuda:0',False,8192);break
 except SystemExit as err:
  print('Preserving other work; waiting:',err,flush=True);time.sleep(15)
def run(args,name):
 with (L/name).open('w',encoding='utf-8') as log:
  result=subprocess.run([str(x) for x in args],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 result.check_returncode()
run([PY,'-X','utf8','-u',R/'qwen3-tts/render_narration.py','--project','animation-relations-v4','--manifest',H.relative_to(R)/'tts-manifest.json','--batch-size','1'],'tts-execution.log')
print('Additive TTS complete; starting18 complete paragraph ASR readbacks',flush=True)
run([PY,'-X','utf8','-u',H/'asr_additions.py'],'asr-execution.log')
print('18 new passages and independent readbacks complete. Existing episode audio untouched.',flush=True)
