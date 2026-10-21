from pathlib import Path
import hashlib, importlib.util, json, subprocess
H=Path(__file__).resolve().parent; R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v8-orientation-matrix';S=P/'script/revision-v8-orientation-matrix';FPS=60
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def module(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def authorized():
 a=read(H/'authorization.json');d=read(R/'shared/publishing/video-production-control.json')['scopedProductionAuthorizations'][P.name]
 assert a['fullProductionAuthorized'] and d['fullProductionAuthorized'] and d['revision']=='orientation-matrix-v8'
 assert a['approvedScriptSha256']==sha(S/'narration.ko.json')==d['approvedScriptSha256']
 return a
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
