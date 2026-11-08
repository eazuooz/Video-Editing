"""One clarity revision of A08/A11 additions, queued behind the active render lease."""
from pathlib import Path
import json, sys, time, subprocess, hashlib, shutil, os
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
ids=['A08','A11'];cpu='--cpu' in sys.argv
control=read(R/'shared/publishing/video-production-control.json')['animationRelationsRevision20261108'];assert control['ttsAuthorized'] and all(id in control['episodes'] for id in ids)
if not cpu:
 sys.path.insert(0,str(R/'qwen3-tts'));from gpu_handoff_guard import schedule_gpu_handoff
 while True:
  try:schedule_gpu_handoff('animation-relations-v4','cuda:0',False,8192);break
  except SystemExit as err:print('Preserving GPU owner; clarity retakes wait:',err,flush=True);time.sleep(15)
else:
 os.environ.update(OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4')
 print('CPU4 threads: same approved Qwen model and voice; active GPU apps preserved.',flush=True)
control=read(R/'shared/publishing/video-production-control.json')['animationRelationsRevision20261108'];assert control['ttsAuthorized'] and all(id in control['episodes'] for id in ids)
source=read(H/'added.ko.json');source['scenes']=[s for s in source['scenes'] if s['id'] in ids]
save(H/'added-clarity-retakes.ko.json',source)
manifest=read(H/'tts-manifest.json');manifest['paths']['script']=(H/'added-clarity-retakes.ko.json').relative_to(R).as_posix();manifest['tts']['outputDir']=(L/'voice-clarity-retakes').relative_to(R).as_posix();manifest['tts']['filenameStem']='relations-clarity-retakes';save(H/'tts-clarity-retakes-manifest.json',manifest)
before={p.stem:sha(p) for p in (L/'voice/chunks').glob('A??-scene.wav')}
def run(args,name):
 with (L/name).open('w',encoding='utf-8') as log:subprocess.run([str(x) for x in args],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
run([PY,'-X','utf8','-u',H/'run_cpu_tts.py' if cpu else R/'qwen3-tts/render_narration.py','--project','animation-relations-v4','--manifest',(H/'tts-clarity-retakes-manifest.json').relative_to(R),'--batch-size','1',*(['--device','cpu'] if cpu else [])],'tts-clarity-retakes.log')
backup=L/'before-clarity-retakes';backup.mkdir(exist_ok=True)
for id in ids:
 old=L/'voice/chunks'/(id+'-scene.wav');assert not (backup/old.name).exists(),'Preserve previously saved take';shutil.copy2(old,backup/old.name)
 asr=L/'asr'/(id+'.json');shutil.copy2(asr,backup/asr.name)
 shutil.copy2(L/'voice-clarity-retakes/chunks'/(id+'-scene.wav'),old)
after={p.stem:sha(p) for p in (L/'voice/chunks').glob('A??-scene.wav')};assert all(before[k]==v for k,v in after.items() if k.split('-')[0] not in ids)
save(L/'clarity-retake-provenance.json',{'selected':ids,'reason':'Repeated independent full/contextual ASR left two first-word pronunciations ambiguous. Rewrite only the connective wording with the same concept/order; keep the canonical interpolation definition in unchanged body.','before':before,'after':after,'allOtherAddedPassagesUnchanged':True,'allExistingEpisodeAudioUntouched':True,'directReview':'pending'})
run([PY,'-X','utf8','-u',H/'asr_additions.py',*ids,*(['--cpu'] if cpu else [])],'asr-clarity-retakes.log')
run([PY,'-X','utf8',H/'build_timing.py',*ids],'timing-clarity-retakes.log')
print('Two clarity paragraphs ready for direct transcript comparison. All16 other additions and every body PCM preserved.',flush=True)
