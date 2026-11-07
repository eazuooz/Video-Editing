"""Exact four-frame early encoded QA. Default read-only; one explicit CPU decode."""

from __future__ import annotations

import argparse,datetime,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,time,uuid

from fractions import Fraction

from pathlib import Path

sys.dont_write_bytecode=True

ROOT=Path('D:/Github/VideoEditing');BATCH=ROOT/'production/batches/architectural-111-20261106'

MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106');BASE=MEDIA/'shorts-leveldesign-06-02'

MANIFEST=BASE/'render-attempts-v2/20261107-040447-8eaa151aeb/render-manifest.json';MANIFEST_SHA='35d0322f59ff40bf530fdf75d04c28b91fe754798c2778b498b0cbf49694cc4c'

MASTER=MANIFEST.parent/'shorts-leveldesign-06-02.captioned.mp4';MASTER_SHA='8a4daeaa2b87c50290f1b852d7a6067116a429aaa39d65b010013d74c4359630'

TIMELINE=BASE/'film-timelines-v2/f698557a95210fdb9e42d484/timeline.json';TIMELINE_SHA='bd9974dbab5f3becaaf4d5221bdb16df88fff72006fbdd89f72d13992081e734'

COLLECTOR=BATCH/'collect-prospect-refuge-review.py';COLLECTOR_SHA='e716380c55c30cbbf603b1214652c87698af51ba09c47d35ae2e08a5d02d60cd'

RENDERER=BATCH/'render-prospect-refuge-film-v2.py';RENDERER_SHA='3ba569d8b8340e338f5ab58e2be1c0944af58e6466bca8b1b69f8d75b421abe9'

FRAMES=[510,5435,13097,28251];TOTAL=28311;TASK='06-02-early-encoded-four-frame-layout-v2'

DEST=BASE/'early-encoded-layout-v2'

KNOWN={'collect-prospect-refuge-review.py','review-prospect-refuge-encoded-audio.py','render-prospect-refuge-film-v2.py','run-prospect-refuge-mix-asr.py','run-prospect-refuge-voice-qa.py','run-prospect-refuge-voice-qa-v2.py','run-prospect-refuge-diagrams-v3.py','run-prospect-refuge-native.py','run-prospect-refuge-closeup.py','run-prospect-refuge-corrections-native.py','run-prospect-refuge-supplement-native.py','run-prospect-refuge-voice-repair-v2.py','prepare-prospect-refuge-audio-v2.py','extract-06-02-extra-encoded-samples.py'}

def require(ok,why):

 if not ok:raise RuntimeError(why)

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):

 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))

def save(p,x):

 p=Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(p)

def load_collector():

 require(sha(COLLECTOR)==COLLECTOR_SHA,'Pinned collector changed')

 old=list(sys.path)

 try:

  sys.path.insert(0,str(BATCH));spec=importlib.util.spec_from_file_location('early_four_pinned_collector',COLLECTOR);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m

 finally:sys.path[:]=old

def verify_inputs(rehash_master=True):

 require(FRAMES==[510,5435,13097,28251]and len(set(FRAMES))==4 and all(type(f)is int and 0<=f<TOTAL for f in FRAMES),'Exact four-frame selection changed')

 require(sha(MANIFEST)==MANIFEST_SHA and sha(TIMELINE)==TIMELINE_SHA and sha(RENDERER)==RENDERER_SHA and sha(COLLECTOR)==COLLECTOR_SHA,'Current input/source pin changed')

 r=read(MANIFEST)

 require(r.get('schemaVersion')=='06-02-render-manifest-v2'and r.get('topicId')=='06.02'and r.get('complete')is True and r.get('format')==dict(width=1080,height=1920,fps=60)and r.get('totalFrames')==TOTAL and r.get('gpuEncoding')is False and r.get('modelsStarted')is False,'Exact complete software FHD60 manifest required')

 require(r['timeline']==dict(path=str(TIMELINE),sha256=TIMELINE_SHA)and r['outputs']['captioned']==dict(path=str(MASTER),sha256=MASTER_SHA),'Current manifest/timeline/master relation changed')

 require([x for x in r['inputs']if x.get('role')=='renderer']==[dict(path=str(RENDERER),sha256=RENDERER_SHA,role='renderer')],'Actual renderer input pin differs')

 if rehash_master:require(sha(MASTER)==MASTER_SHA,'Actual captioned file bytes changed')

 return dict(renderManifest=pin(MANIFEST),timeline=pin(TIMELINE),captionedMaster=dict(path=str(MASTER),sha256=MASTER_SHA),renderer=pin(RENDERER),collector=pin(COLLECTOR),helper=pin(__file__),frames=FRAMES,totalFrames=TOTAL,format=r['format'])

def resource_reason(c,own_token=None):

 c.authorize()

 import psutil

 for p in MEDIA.glob('06-02-*-worker.json'):

  try:x=read(p)

  except Exception:return 'Uninspectable known06 worker preserved: '+str(p)

  if p==c.WORKER and own_token and x.get('token')==own_token:continue

  if c.owned_alive(x)or c.native.alive(x.get('child'))or any(c.native.alive(y)for y in x.get('children',[]))or('launch'in str(x.get('phase','')).lower()):return 'Live or uncertain known06 worker preserved: '+str(p)

 for p in psutil.process_iter(['name','cmdline']):

  try:

   if p.pid==os.getpid():continue

   name=(p.info.get('name')or'').lower();args=p.info.get('cmdline')

   if args is None and name in{'python.exe','pythonw.exe','node.exe','ffmpeg.exe','ffprobe.exe','unity.exe'}:return 'Uninspectable possible model/media/Editor preserved'

   if args and any(Path(a).name in KNOWN for a in args)and'--execute'in args:return 'Known06 executable stage still active'

   hub_service=args==['C:\\Program Files\\Unity Hub\\resources\\unity.exe','serve'] and str(Path(p.exe()).resolve()).casefold()==str(Path('C:/Program Files/Unity Hub/resources/unity.exe').resolve()).casefold()
   if name in{'ffmpeg.exe','ffprobe.exe','unity.exe'}and not(name=='unity.exe'and hub_service):return 'Active media/Editor preserved: '+name

   if args and any(a in{'--recognize','--recognize-context','--worker-child'}for a in args)and any('asr'in a.lower()or'qwen'in a.lower()for a in args):return 'Active foreign model child preserved'

  except psutil.NoSuchProcess:continue

  except psutil.AccessDenied:return 'Uninspectable process preserved'

 if psutil.virtual_memory().available<2*1024**3:return 'At least2GiB available RAM required'

 if shutil.disk_usage(BASE).free<2*1024**3+4*(1080*1920+375*667)*4:return 'PNG output plus2GiB disk reserve required'

 return None

def parse_showinfo(text):

 bases={(int(n),int(d))for n,d in re.findall(r'config in time_base:\s*(\d+)/(\d+)',text)};require(len(bases)==1,'One decoded input timebase required');num,den=next(iter(bases));rows=[(int(n),int(pts))for n,pts in re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:',text)]

 require(len(rows)==4 and[n for n,p in rows]==list(range(4)),'Exact four selected showinfo frames required')

 require(all(Fraction(pts*num,den)==Fraction(frame,60)for(_,pts),frame in zip(rows,FRAMES)),'Decoded PTS differs from exact encoded frame/60')

 return[dict(outputOrdinal=i+1,encodedFrame=f,sourcePts=pts,timeBase=[num,den],ptsSeconds=f/60)for i,((_,pts),f)in enumerate(zip(rows,FRAMES))]

def execute():

 c=load_collector();inputs=verify_inputs();reason=resource_reason(c);require(reason is None,reason)

 worker=c.native.SingleWorker(c.WORKER,is_alive=c.owned_alive).acquire();out=None

 try:

  worker.update(stage='early-four-frame-encoded-layout-only',taskProtocol=TASK,sourceCaptionedMasterSHA256=MASTER_SHA)

  reason=resource_reason(c,worker.record['token']);require(reason is None,reason)

  require(verify_inputs()==inputs,'Inputs changed before launch');ff=c.FF.resolve();require(ff.is_file(),'Installed FFmpeg missing');inputs['ffmpeg']=pin(ff)

  out=DEST/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);out.mkdir(parents=True,exist_ok=False);save(out/'input-record.json',inputs)

  graph='[0:v]select='+c.selection_expression(FRAMES)+',showinfo,split[full][small];[small]scale=375:-1[mobile]'

  command=[str(ff),'-hide_banner','-nostdin','-n','-v','info','-threads','2','-hwaccel','none','-i',str(MASTER),'-filter_complex_threads','1','-filter_complex',graph,'-map','[full]','-fps_mode','passthrough','-threads:v','2','-start_number','1',str(out/'1080-%03d.png'),'-map','[mobile]','-fps_mode','passthrough','-threads:v','2','-start_number','1',str(out/'375-%03d.png')]

  reason=resource_reason(c,worker.record['token']);require(reason is None,reason)

  log=out/'software-select.log';worker.update(phase='launching-owned-review-tool',launchCommand=command,launchStartedAt=time.time(),child=None,earlyOutput=str(out))

  with log.open('xb')as handle:

   child=subprocess.Popen(command,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0));worker.update(phase='owned-review-tool',child=c.native.identity(child.pid));code=child.wait()

  worker.update(phase='early-four-frame-verification',child=None,launchCommand=None);require(code==0,'Software extraction failed; preserve log/partial outputs')

  mapped=parse_showinfo(log.read_text(encoding='utf8',errors='replace'));require(len(list(out.glob('1080-*.png')))==len(list(out.glob('375-*.png')))==4,'Exact four PNG pairs required')

  from PIL import Image

  for row in mapped:

   row.update(sourceCaptionedMasterSHA256=MASTER_SHA,actualPixelApproval=False)

   for key,prefix,size in[('native','1080',(1080,1920)),('mobile','375',(375,667))]:

    p=out/f'{prefix}-{row["outputOrdinal"]:03}.png'

    with Image.open(p)as im:im.load();require(im.size==size,'Decoded PNG dimensions differ')

    row[key]=dict(file=p.name,sha256=sha(p),width=size[0],height=size[1])

  after=verify_inputs();require(after=={k:v for k,v in inputs.items()if k!='ffmpeg'},'Inputs changed during extraction');reason=resource_reason(c,worker.record['token']);require(reason is None,reason)

  result=dict(schemaVersion='06-02-early-encoded-layout-check-v2',complete=True,topicId='06.02',output=str(out),inputs=inputs,sourceCaptionedMasterSHA256=MASTER_SHA,samples=mapped,softwareDecodeInvocations=1,probeInvocations=0,modelsStarted=False,command=command,decodeLog=dict(file=log.name,sha256=sha(log)),actualPixelApproval=False,actualFullMotionReviewed=False,actualListening=False,humanApproval=False,platformActions=[])

  save(out/'sample-manifest.json',result);return result

 except BaseException as e:

  if out is not None:save(out/'failed.json',dict(complete=False,error=str(e),partialFilesPreserved=True,actualPixelApproval=False))

  raise

 finally:worker.close(remove=not c.child_pending_or_alive(worker.record))

def main():

 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');args=parser.parse_args()

 if args.execute:

  x=execute();print(json.dumps(dict(complete=True,output=x['output'],frames=FRAMES,actualPixelApproval=False)));return

 c=load_collector();x=verify_inputs(rehash_master=False);reason=resource_reason(c);print(json.dumps(dict(ready=reason is None,reason=reason,dryRun=True,frames=FRAMES,mediaStarted=False,sourceMasterRehashed=False,outputsCreated=False,inputs=x)))

if __name__=='__main__':main()
