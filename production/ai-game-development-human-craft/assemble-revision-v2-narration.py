"""Assemble current scene PCM and its once-per-hash complete ASR evidence."""
from pathlib import Path
import json,sys,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as renderer
from revision_paths import workroot
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert read(ROOT/'shared/publishing/video-production-control.json')['selectedVideo']==SLUG
m=read(ROOT/f'projects/{SLUG}/project.json');assert m['revision']['id']=='v2'
out=ROOT/m['tts']['outputDir'];stem=m['tts']['filenameStem'];prepared=read(workroot(ROOT)/'prepared.json')
script=read(ROOT/m['paths']['script']);current=[]
for s in script['scenes']:
 sid=s['id'];p=out/'chunks'/f'{sid}-scene.wav';a=read(out/'asr'/f'{sid}.json')
 assert a['audio_sha256']==sha(p),sid
 assert all(all(t is not None for t in w['timestamp']) for w in a['words']),sid+' incomplete ASR timestamp'
 current.append(a)
renderer.configure_project(SLUG);renderer.load_tts_dependencies()
assert not renderer.FINAL_WAV.exists(),'Resume the existing assembly; do not overwrite it'
renderer.assemble_scene_outputs(renderer.load_jobs())
timing=read(out/(stem+'.timing.json'));words=[];texts=[];evidence=[]
for s,a in zip(script['scenes'],current):
 sid=s['id'];origin=next(e['start'] for e in timing['entries'] if e['scene_id']==sid)
 for w in a['words']:
  start,end=w['timestamp'];words.append({'text':w['text'],'timestamp':[origin+start,origin+end]})
 texts.append(a['text']);evidence.append({'scene':sid,'origin':origin,'audioSha256':a['audio_sha256'],'asrCacheSha256':sha(out/'asr'/f'{sid}.json'),'status':'unchanged-approved-PCM-ASR-reused' if sid in prepared['retainedScenes'] else 'revised-complete-scene-context-ASR'})
full={'audio_sha256':sha(renderer.FINAL_WAV),'audio':str(renderer.FINAL_WAV),'timestampMode':'word','text':' '.join(texts),'chunks':words,'sceneEvidence':evidence,'method':'one current complete readback per scene hash; prior approved evidence retained only for identical unchanged PCM','humanListening':'pending'}
write(out/(stem+'.asr-review.timestamps.json'),full);(out/(stem+'.asr-review.txt')).write_text(full['text']+'\n',encoding='utf-8')
for command in [[sys.executable,'-X','utf8',f'production/{SLUG}/align-captions.py'],[sys.executable,'-X','utf8',f'production/{SLUG}/prepare-scenes.py']]:
 subprocess.run(command,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
write(workroot(ROOT)/'narration-assembly.json',{'sourceSha256':sha(renderer.FINAL_WAV),'scriptRevision':4,'sceneEvidence':evidence,'fullTextReview':'pending','joinReview':'pending','humanListening':'pending'})
