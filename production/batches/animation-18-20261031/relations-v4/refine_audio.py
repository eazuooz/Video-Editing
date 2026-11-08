"""One finite retake for two uncertain newly-added passages; keep all old takes."""
from pathlib import Path
import json,sys,time,subprocess,hashlib,shutil
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';PY=R/'qwen3-tts/.venv/Scripts/python.exe';IDS=['A08','A11']
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert read(R/'shared/publishing/video-production-control.json')['animationRelationsRevision20261108']['ttsAuthorized']
sys.path.insert(0,str(R/'qwen3-tts'));from gpu_handoff_guard import schedule_gpu_handoff
while True:
 try:schedule_gpu_handoff('animation-relations-v4','cuda:0',False,8192);break
 except SystemExit as err:print('Waiting for current GPU job to finish:',err,flush=True);time.sleep(15)
chunks=L/'voice/chunks';before={f.stem:sha(f) for f in chunks.glob('A??-scene.wav')};assert len(before)==18
source=read(H/'added.ko.json');source['scenes']=[e for e in source['scenes'] if e['id'] in IDS];assert len(source['scenes'])==2
save(H/'added-retakes.ko.json',source);manifest=read(H/'tts-manifest.json');manifest['paths']['script']=(H/'added-retakes.ko.json').relative_to(R).as_posix();manifest['tts']['outputDir']=(L/'voice-retakes').relative_to(R).as_posix();manifest['tts']['filenameStem']='relations-pronunciation-retakes';save(H/'tts-retakes-manifest.json',manifest)
def run(args,log):
 with (L/log).open('w',encoding='utf-8') as f:subprocess.run([str(x) for x in args],cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
run([PY,'-X','utf8','-u',R/'qwen3-tts/render_narration.py','--project','animation-relations-v4','--manifest',(H/'tts-retakes-manifest.json').relative_to(R),'--batch-size','1'],'tts-retakes.log')
back=L/'before-pronunciation-retakes';back.mkdir(exist_ok=True)
for id in IDS:
 old=chunks/(id+'-scene.wav');assert not (back/old.name).exists(),'Do not overwrite the preserved first take.';shutil.copy2(old,back/old.name)
 asr=L/'asr'/(id+'.json')
 if asr.exists():shutil.copy2(asr,back/asr.name)
 shutil.copy2(L/'voice-retakes/chunks'/(id+'-scene.wav'),old)
after={f.stem:sha(f) for f in chunks.glob('A??-scene.wav')};assert all(before[k]==v for k,v in after.items() if k.split('-')[0] not in IDS)
save(L/'retake-provenance.json',{'selected':IDS,'reason':'Independent full and contextual ASR both left clothing/interpolation pronunciation uncertain. Preserve the same script and re-synthesize only these added paragraphs.','before':before,'after':after,'allOtherAddedPassagesUnchanged':True,'allExistingEpisodeAudioUntouched':True,'directReview':'pending'})
run([PY,'-X','utf8','-u',H/'asr_additions.py',*IDS],'asr-retakes.log')
print('Two targeted retakes ready for direct readback review; all other audio preserved',flush=True)
