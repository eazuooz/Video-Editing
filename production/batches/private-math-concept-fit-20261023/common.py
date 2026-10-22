from pathlib import Path
import datetime,hashlib,json,os,subprocess,uuid
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
KEY='private-math-concept-fit-20261023'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def authorized(ident):
 a=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations'][KEY]
 assert a['status']=='active' and a['fullProductionAuthorized'] and ident in a['ids']
 assert not a['uploadAuthorized'] and not a['deleteAuthorized'] and not a['heartbeatEnabled']
 return a
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def run(args):subprocess.run([str(x) for x in args],check=True)
