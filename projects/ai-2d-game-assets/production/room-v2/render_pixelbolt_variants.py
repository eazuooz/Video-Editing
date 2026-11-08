from pathlib import Path
import json,subprocess,hashlib,shutil
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'projects/ai-2d-game-assets';TOOL=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/Pixelbolt')
base=json.loads((TOOL/'examples/forest-spirit.json').read_text())
variants={'rain':{'d':'#244c64','l':'#6cabc2','L':'#cae6ed','h':'#acd8df','k':'#1b3447','p':'#dcaeac','s':'#283d5130','g':'#dae6b2'},'snow':{'d':'#4c6274','l':'#a6cad4','L':'#f1f3dc','h':'#d7e9e7','k':'#243944','p':'#e6a9af','s':'#283d5130','g':'#f2e6bc'},'night':{'d':'#35445e','l':'#9fa2ce','L':'#ecdfb5','h':'#cbc1dc','k':'#252941','p':'#dca5af','s':'#17213530','g':'#f6e7a8'}}
records=[]
for name,palette in variants.items():
 spec=json.loads(json.dumps(base));spec['name']='spirit-'+name;spec['palette']=palette
 recipe=P/'production/room-v2'/f'spirit-{name}.pixel.json';recipe.write_text(json.dumps(spec,indent=2),encoding='utf8')
 out=P/'production/local/room-v2/pixelbolt'/name
 cmd=['node',str(TOOL/'bin/pixelbolt.js'),'render',str(recipe),'--out',str(out)]
 subprocess.run(cmd,check=True)
 target=ROOT/'sites/yamyam-cartographers-room/dist/assets/pixelbolt';target.mkdir(parents=True,exist_ok=True)
 files=[]
 for f in out.glob('*'):
  if f.suffix in ['.png','.json']:
   dest=target/f.name;shutil.copy2(f,dest);files.append({'file':dest.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 records.append({'variant':name,'command':cmd,'files':files,'palette':palette})
(P/'production/room-v2/pixelbolt-execution.json').write_text(json.dumps({'tool':'Pixelbolt','actualExecution':True,'operation':'same forest-spirit recipe, weather-specific palette, native per-frame durations retained','records':records},indent=2),encoding='utf8')
