"""Create the selected Nintendo revision without changing its reviewed v2 inputs."""
from pathlib import Path
import json, shutil, hashlib
R=Path(__file__).resolve().parents[4]; P=R/'projects/game-math-euler-axis-angle'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 edits=read(P/'production/revision-v3/gameplay-script.json')
 ko=read(P/'script/revision-v2/narration.ko.json');en=read(P/'script/revision-v2/narration.en.json');lesson=read(P/'production/revision-v2/lesson.json')
 changed=set(edits['scenes']);assert changed=={'01','02','05','08','11','14','17','20','23'}
 for a,b,c in zip(ko['scenes'],en['scenes'],lesson['scenes']):
  sid=a['id'];assert sid==b['id']==c['id']
  if sid in changed:
   e=edits['scenes'][sid];assert len(e['ko'])==len(e['en'])==len(e['beats'])
   a.update(title=e['title'],lines=e['ko']);b.update(title=e['title'],lines=e['en'])
   c.update(title=e['title'],ko=e['ko'],en=e['en'],beats=e['beats'],boundaryLink=e['boundaryLink'])
   for key in ['sourceId','sourceSegments','observationPurpose']:c.pop(key,None)
   c['sourceSelection']='sources/cut-plan-v3.json';c['annotationSelection']='sources/annotation-plan-v3.json'
 for obj in (ko,en,lesson):obj['revision']='nintendo-annotated-no-bgm-v3'
 lesson['retainedExplanationScenes']=[s['id'] for s in lesson['scenes'] if s['id'] not in changed]
 save(P/'script/revision-v3/narration.ko.json',ko);save(P/'script/revision-v3/narration.en.json',en);save(P/'production/revision-v3/lesson.json',lesson)
 m=read(P/'production/revision-v2/tts-manifest.json')
 m['revision']='nintendo-annotated-no-bgm-v3'
 m['paths']={k:v.replace('revision-v2','revision-v3') for k,v in m['paths'].items()}
 old=R/m['tts']['outputDir'];m['tts']['outputDir']=m['tts']['outputDir'].replace('teaching-rules-v2','nintendo-annotated-no-bgm-v3');m['tts']['filenameStem']='euler-nintendo-v3'
 m['executionState']='selected-nine-scenes-pending';m['preserveScenes']=lesson['retainedExplanationScenes']
 save(P/'production/revision-v3/tts-manifest.json',m)
 dest=R/m['tts']['outputDir'];proof=[]
 for sid in m['preserveScenes']:
  for sub,file in [('chunks',sid+'-scene.wav'),('asr',sid+'.json')]:
   source=old/sub/file;target=dest/sub/file;assert source.exists(),source
   target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():assert sha(target)==sha(source),'Do not replace an existing distinct artifact'
   else:shutil.copy2(source,target)
   proof.append(dict(scene=sid,file=target.relative_to(R).as_posix(),fromFile=source.relative_to(R).as_posix(),sha256=sha(target)))
 save(P/'production/local/revision-v3/preserved-voice.json',dict(changedScenes=sorted(changed),preserved=proof))
 # Reuse the bounded, cooperative GPU implementation, with selected paths only.
 runner=(P/'production/render-voice-v2.py').read_text(encoding='utf8').replace('revision-v2','revision-v3')
 runner=runner.replace("{'03','12','15'}",repr(changed)).replace('Only the current three reviewed clarity retakes are authorized here','Only selected Nintendo gameplay and overview retakes are authorized here')
 runner=runner.replace('    worker.render_chunks(items,1,force_scenes)',"    items=[item for item in items if item.key.split('-')[0] in "+repr(changed)+"]\n    worker.render_chunks(items,1,force_scenes)")
 runner=runner.replace("allowed.update({'nvidia overlay.exe','unity hub.exe','microsoft.media.player.exe','edgegameassist.exe'})", "allowed.update({'nvidia overlay.exe','unity hub.exe','microsoft.media.player.exe','edgegameassist.exe','winword.exe','windowsterminal.exe'})  # Microsoft-signed installed desktop apps, verified2026-10-19.")
 (P/'production/render-voice-v3.py').write_text(runner,encoding='utf8')
 for name in ['review-voice','align-voice']:
  (P/f'production/{name}-v3.py').write_text((P/f'production/{name}-v2.py').read_text(encoding='utf8').replace('revision-v2','revision-v3'),encoding='utf8')
 print(json.dumps(dict(changed=sorted(changed),preserved=len(m['preserveScenes']))))
if __name__=='__main__':main()
