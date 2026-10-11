"""Read-only QA copies of generated lines while the exclusive TTS batch continues."""
from pathlib import Path
import json,copy,shutil,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-polygons-teaching-additions-v2'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
m=read(ROOT/f'projects/{slug}/project.json');script=read(ROOT/m['paths']['script']);out=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-raw-line-review';(out/'chunks').mkdir(parents=True,exist_ok=True)
rows=[];copied=[]
for scene in script['scenes']:
 for i,line in enumerate(scene['lines'],1):
  ident=f'{scene["id"]}-{i:02}';rows.append({'id':ident,'title':scene['title'],'lines':[line]})
  source=ROOT/m['tts']['outputDir']/f'chunks/{ident}.wav';target=out/f'chunks/{ident}-scene.wav'
  if source.exists():
   shutil.copy2(source,target);copied.append({'id':ident,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
script_file=B/'polygons-raw-line-review-script.json';script_file.write_text(json.dumps({'scenes':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
m=copy.deepcopy(m);m['paths']['script']=script_file.relative_to(ROOT).as_posix();m['tts']['outputDir']=out.relative_to(ROOT).as_posix();m['tts']['filenameStem']='polygons-raw-lines'
(B/'polygons-raw-line-review-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(out/'copy-provenance.json').write_text(json.dumps(copied,indent=2)+'\n',encoding='utf8')
print('QA copied only; no synthesis settings or in-flight output changed:',len(copied))
