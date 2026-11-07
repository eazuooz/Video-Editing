"""Exact extra148 encoded QA frames; default read-only, --execute root-only.

No probe/render/model/encode/platform/Git/publishing mutation. One software
decode selects only the148 complement frames. The existing384 remain untouched.
The pinned06 review singleton is intentionally SHARED with the frozen collector,
so a live or unknown orphan here also prevents a competing collector start.
"""
from __future__ import annotations
import argparse,datetime,hashlib,importlib.util,json,math,os,re,shutil,subprocess,sys,uuid
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('D:/Github/VideoEditing');BATCH=ROOT/'production/batches/architectural-111-20261106'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106');BASE=MEDIA/'shorts-leveldesign-06-02'
PLAN=MEDIA/'06-02-encoded-visual-priority-plan.json';PLAN_SHA='7205c8fd1b2bd13d54269a2ce15bc50aab5a72207213ded9d4d3305fcc7c8d5f'
MANIFEST=BASE/'render-attempts-v2/20261107-024807-6ecb9bc5d6/render-manifest.json';MANIFEST_SHA='c12c6a4560abd333971c355ec61f56302a8cc471d191e052469fe70d88971395'
MASTER=MANIFEST.parent/'shorts-leveldesign-06-02.captioned.mp4';MASTER_SHA='5fb5621f810943510371c7f394490de0dae7f73619262358a1854d81f89c136e'
TIMELINE=BASE/'film-timelines-v2/cfe82dc4de2c78d9058e5d44/timeline.json';TIMELINE_SHA='de5c4deaccf6f089ded52a040e2dee61886a5c211dc6a7ec5323e758c528e41b'
COLLECTOR=BATCH/'collect-prospect-refuge-review.py';COLLECTOR_SHA='5b58bfeea05c8b799ffe4c68c72e75da336170923340e26f73e19988eac1a0c7'
PRIOR_COLLECTOR_SHA='45d12786ff00b07ba554aaf732f92c46e6cad6e22f13384d7defaa1c8e868982'
BALANCE_REVIEW=BASE/'review-collector-source-history/before-balanced-select-v1/balanced-select-fix-review-v1.json';BALANCE_REVIEW_SHA='c90a72acc5ded29c299da494aa32c87c3ddce173c98a562f98b748d499aff1a0'
DEST=BASE/'extra-encoded-samples-v1';TASK='architectural111-06-02-extra148-encoded-samples-v1'
KNOWN_WORKERS=['review','encoded-audio-review','composite','voice','asr','asr-v2','mix-asr','audio','native','closeup','corrections-native','supplement-native','mc','mc-v2','mc-v3']
KNOWN_SCRIPTS={'collect-prospect-refuge-review.py','review-prospect-refuge-encoded-audio.py','render-prospect-refuge-film-v2.py','run-prospect-refuge-mix-asr.py','run-prospect-refuge-voice-qa.py','run-prospect-refuge-voice-qa-v2.py','run-prospect-refuge-diagrams.py','run-prospect-refuge-diagrams-v2.py','run-prospect-refuge-diagrams-v3.py','run-prospect-refuge-native.py','run-prospect-refuge-closeup.py','run-prospect-refuge-corrections-native.py','run-prospect-refuge-supplement-native.py','run-prospect-refuge-voice-repair-v2.py','prepare-prospect-refuge-audio-v2.py'}
class Pending(RuntimeError):pass
def require(ok,message):
 if not ok:raise Pending(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(p,data):
 p=Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(p)
def load_collector():
 require(sha(COLLECTOR)==COLLECTOR_SHA,'Frozen collector changed; review before using its singleton/helpers')
 old=list(sys.path)
 try:
  sys.path.insert(0,str(BATCH));spec=importlib.util.spec_from_file_location('extra148_pinned_collector',COLLECTOR);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
 finally:sys.path[:]=old

def frame_contract(total,base,extra):
 require(type(total)is int and total==28311,'Exact known current encoded frame clock required')
 require(len(base)==384 and base==sorted(set(base))and all(type(f)is int and 0<=f<total for f in base),'Exact384 baseline selection required')
 require(len(extra)==148 and extra==sorted(set(extra))and all(type(f)is int and 0<=f<total for f in extra),'Exact148 unique in-range missing frames required')
 require(not set(base)&set(extra)and len(set(base)|set(extra))==532,'Extra frames must be the disjoint148 complement; collector512 bound remains unchanged')
 return list(extra)
def select_expression(frames,collector):return collector.selection_expression(frames)
def parse_showinfo(text,frames):
 bases={(int(n),int(d))for n,d in re.findall(r'config in time_base:\s*(\d+)/(\d+)',text)};require(len(bases)==1,'One actual source time-base proof required');num,den=next(iter(bases))
 rows=[(int(n),int(pts))for n,pts in re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:',text)]
 require(len(rows)==len(frames)and[n for n,p in rows]==list(range(len(frames))),'Selected showinfo ordinal count/order differs')
 for(_,pts),f in zip(rows,frames):require(Fraction(pts*num,den)==Fraction(f,60),'Actual selected PTS differs from requested encoded frame/60')
 return[dict(outputOrdinal=i+1,encodedFrame=f,sourcePts=pts,timeBase=[num,den],ptsSeconds=f/60)for i,((_,pts),f)in enumerate(zip(rows,frames))]

def prepare(review_receipt=None):
 require(sha(PLAN)==PLAN_SHA and sha(MANIFEST)==MANIFEST_SHA and sha(TIMELINE)==TIMELINE_SHA,'Fixed plan/render/timeline source changed')
 p=read(PLAN);r=read(MANIFEST);t=read(TIMELINE);collector=load_collector()
 require(r.get('schemaVersion')=='06-02-render-manifest-v2'and r.get('topicId')=='06.02'and r.get('complete')is True and r.get('totalFrames')==28311,'Completed exact current renderer receipt required')
 require(r['timeline']==dict(path=str(TIMELINE),sha256=TIMELINE_SHA)and r['outputs']['captioned']==dict(path=str(MASTER),sha256=MASTER_SHA),'Manifest does not bind exact selected timeline/master')
 _,baseline=collector.section_contract(t);frames=frame_contract(t['totalFrames'],baseline,p['criticalTransitionCoverage']['missingFrameIds'])
 require(p.get('timeline')==pin(TIMELINE)and p.get('collector')==dict(path=str(COLLECTOR),sha256=PRIOR_COLLECTOR_SHA),'Extra plan belongs to another original timeline/baseline collector')
 require(sha(BALANCE_REVIEW)==BALANCE_REVIEW_SHA,'Reviewed balanced-expression-only bridge changed')
 bridge=read(BALANCE_REVIEW);require(bridge['newCollector']==pin(COLLECTOR)and bridge['preservedFailedCollector']['sha256']==PRIOR_COLLECTOR_SHA and bridge['minimalSourceDiffVerified']['actualIndicesUnchanged']is True and bridge['minimalSourceDiffVerified']['actualSelectionCount']==384,'New collector must preserve exactly the old384 frame indices')
 require(sha(bridge['preservedFailedCollector']['path'])==PRIOR_COLLECTOR_SHA,'Preserved original baseline collector changed')
 context=dict(taskProtocol=TASK,renderManifest=pin(MANIFEST),timeline=pin(TIMELINE),priorityPlan=pin(PLAN),collector=pin(COLLECTOR),balancedSelectionBridge=pin(BALANCE_REVIEW),source=dict(path=str(MASTER),sha256=MASTER_SHA),totalFrames=28311,baseline384=baseline,extra148=frames,reviewReceipt=None)
 if review_receipt is not None:
  rp=Path(review_receipt).resolve();require(rp.name=='review-receipt.json'and rp.parent.parent==(BASE/'local-final-review').resolve(),'Exact selected post-collector review receipt required')
  rr=read(rp);require(rr.get('status')=='technical-four-output-qa-complete-visual-listening-review-pending'and Path(rr['output']).resolve()==rp.parent and rp.parent.name==rr['fingerprint'][:24]and rr['pins']['renderManifest']==pin(MANIFEST)and rr['pins']['reviewHelperSHA256']==COLLECTOR_SHA,'Current completed immutable review receipt identity differs')
  require(rr['metadata']['masterSHA256']==MASTER_SHA and rr['deliverables']['captioned']['sha256']==MASTER_SHA,'Review contains another captioned master')
  artifacts={q['file']:q for q in rr['reviewArtifacts']};require(len(artifacts)==len(rr['reviewArtifacts']),'Duplicate review artifacts')
  for name in['mobile-samples.json','technical-qa.json']:
   require(name in artifacts and sha(rp.parent/name)==artifacts[name]['sha256'],'Post-collector technical/sample artifact changed')
  samples=read(rp.parent/'mobile-samples.json');require([q['frame']for q in samples['samples']]==baseline and all(q['captionedMasterSHA256']==MASTER_SHA for q in samples['samples']),'Actual collected384 frames or source master differ')
  qa=read(rp.parent/'technical-qa.json');require(qa.get('wholeDecodePerformed')is True and qa['videos']['captioned']['decodedFrames']==28311,'Actual final master technical decode/PTS review required')
  context.update(reviewReceipt=pin(rp),baselineSamples=pin(rp.parent/'mobile-samples.json'),baselineTechnicalQa=pin(rp.parent/'technical-qa.json'))
 return collector,context

def launch_pending(record):
 if not record or'launch'not in str(record.get('phase','')).lower():return False
 command=record.get('launchCommand')
 if not command:return True
 import psutil
 for p in psutil.process_iter(['name','cmdline']):
  try:
   if(p.info.get('name')or'').lower()==Path(command[0]).name.lower()and(p.info.get('cmdline')is None or p.info['cmdline']==command):return True
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:return True
 return False
def resource_reason(collector,own_token=None):
 collector.authorize()  # Exact111, current06.02, local-only; no mutation.
 import psutil
 for label in KNOWN_WORKERS:
  path=MEDIA/('06-02-'+label+'-worker.json')
  if not path.exists():continue
  try:record=read(path)
  except Exception:return 'Uninspectable known06 worker preserved: '+str(path)
  if path==collector.WORKER and own_token and record.get('token')==own_token:continue
  if collector.owned_alive(record)or collector.native.alive(record.get('child'))or any(collector.native.alive(x)for x in record.get('children',[]))or launch_pending(record):return 'Live/unknown known06 worker or child preserved: '+str(path)
 for p in psutil.process_iter(['name','cmdline']):
  try:
   if p.pid==os.getpid():continue
   args=p.info.get('cmdline')
   if args is None and(p.info.get('name')or'').lower()in{'python.exe','pythonw.exe','node.exe','ffmpeg.exe','ffprobe.exe','unity.exe'}:return 'Uninspectable possible model/media/Editor process preserved'
   if args and'--execute'in args and any(Path(a).name in KNOWN_SCRIPTS for a in args):return 'Known06 executable stage still active before/during its worker lease'
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:return 'Uninspectable known process preserved'
 if psutil.virtual_memory().available<2*1024**3:return 'At least2GiB free host RAM required for bounded CPU decode'
 required=148*(1080*1920*3+375*667*3)+2*1024**3
 if shutil.disk_usage(BASE).free<required:return 'Insufficient C space for148 fresh PNG pairs plus2GiB reserve'
 return None

def completed_reuse(context):
 if not DEST.exists():return None
 for path in sorted(DEST.glob('*/sample-manifest.json')):
  value=read(path)
  if value.get('jobFingerprint')!=context['jobFingerprint']:continue
  require(value.get('complete')is True and value.get('inputs')==context and value.get('sourceCaptionedMasterSHA256')==MASTER_SHA and[q['encodedFrame']for q in value['samples']]==context['extra148'],'Prior extra sample receipt differs')
  require(Path(value['output']).resolve()==path.parent.resolve(),'Prior extra sample directory differs')
  for i,row in enumerate(value['samples'],1):
   require(row['outputOrdinal']==i,'Prior output ordinal differs')
   for kind,prefix,size in[('native','1080',(1080,1920)),('mobile','375',(375,667))]:
    q=row[kind];require(q['file']==f'{prefix}-{i:03}.png'and(q['width'],q['height'])==size and sha(path.parent/q['file'])==q['sha256'],'Prior extra sample changed; preserve rather than overwrite')
  require(sha(path.parent/value['decodeLog']['file'])==value['decodeLog']['sha256'],'Prior exact-frame decode log changed')
  mapped=parse_showinfo((path.parent/value['decodeLog']['file']).read_text(encoding='utf8',errors='replace'),context['extra148'])
  require(all(all(row[k]==v for k,v in actual.items())for row,actual in zip(value['samples'],mapped)),'Prior selected-frame/PTS mapping differs from actual decode log')
  return value
 return None
def execute(review_receipt):
 collector,context=prepare(review_receipt);require(context['reviewReceipt']is not None,'Post-collector receipt required before execution')
 reason=resource_reason(collector);require(reason is None,reason)
 # SHAREDreview kernel guard and marker make rootcollector and extra job
 # mutually exclusive, including the durable Popen->identity orphan window.
 worker=collector.native.SingleWorker(collector.WORKER,is_alive=collector.owned_alive).acquire();out=None
 try:
  worker.update(stage='extra148-encoded-frames-only',taskProtocol=TASK,sourceCaptionedMasterSHA256=MASTER_SHA)
  reason=resource_reason(collector,worker.record['token']);require(reason is None,reason)
  require(sha(MASTER)==MASTER_SHA,'Actual completed captioned master changed before extra decode')
  ff=collector.FF.resolve();require(ff.is_file(),'Installed software FFmpeg is missing')
  context.update(helper=pin(__file__),ffmpeg=pin(ff));context['jobFingerprint']=digest(context)
  old=completed_reuse(context)
  if old is not None:return old
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10];out=DEST/stamp;out.mkdir(parents=True,exist_ok=False);save(out/'input-record.json',context)
  graph='[0:v]select='+select_expression(context['extra148'],collector)+',showinfo,split[full][small];[small]scale=375:-1[mobile]'
  command=[str(ff),'-hide_banner','-nostdin','-n','-v','info','-threads','2','-hwaccel','none','-i',str(MASTER),'-filter_complex_threads','1','-filter_complex',graph,'-map','[full]','-fps_mode','passthrough','-threads:v','2','-start_number','1',str(out/'1080-%03d.png'),'-map','[mobile]','-fps_mode','passthrough','-threads:v','2','-start_number','1',str(out/'375-%03d.png')]
  reason=resource_reason(collector,worker.record['token']);require(reason is None,reason)
  log=out/'software-select.log';worker.update(phase='launching-owned-review-tool',launchCommand=command,launchStartedAt=__import__('time').time(),child=None,extraOutput=str(out))
  with log.open('xb')as handle:
   child=subprocess.Popen(command,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0));worker.update(phase='owned-review-tool',child=collector.native.identity(child.pid));code=child.wait()
  worker.update(phase='extra-sample-verification',child=None,launchCommand=None);require(code==0,'Bounded software decode failed; preserve log and partial PNGs')
  mapping=parse_showinfo(log.read_text(encoding='utf8',errors='replace'),context['extra148']);require(len(list(out.glob('1080-*.png')))==len(list(out.glob('375-*.png')))==148,'Actual PNG pair count differs from exact148 selection')
  from PIL import Image
  rows=[]
  for row in mapping:
   item=dict(row,sourceCaptionedMasterSHA256=MASTER_SHA,actualAgentVisualInspection='pending')
   for key,prefix,size in[('native','1080',(1080,1920)),('mobile','375',(375,667))]:
    p=out/(prefix+f'-{row["outputOrdinal"]:03}.png')
    with Image.open(p)as image:image.load();require(image.size==size,'Actual decoded PNG dimensions differ')
    item[key]=dict(file=p.name,sha256=sha(p),width=size[0],height=size[1])
   rows.append(item)
  require(sha(MASTER)==MASTER_SHA and sha(MANIFEST)==MANIFEST_SHA and sha(PLAN)==PLAN_SHA,'Source inputs changed during decode; preserve partial outputs without pass')
  result=dict(schemaVersion='06-02-extra148-encoded-samples-v1',complete=True,topicId='06.02',jobFingerprint=context['jobFingerprint'],output=str(out),sourceCaptionedMasterSHA256=MASTER_SHA,inputs=context,samples=rows,decodeLog=dict(file=log.name,sha256=sha(log)),command=command,softwareOnly=True,decodeInvocations=1,probes=0,modelsStarted=False,existing384Modified=False,totalSupplementalFrames=148,combined384Plus148=532,collector512BoundChanged=False,actualEncodedPixelInspection=False,actualFullMotionReviewed=False,actualListening=False,humanApproval=False,platformActions=[])
  save(out/'sample-manifest.json',result);return result
 except BaseException as error:
  if out and out.exists():save(out/'failed.json',dict(complete=False,error=str(error),partialOutputsPreserved=True,actualEncodedPixelInspection=False,actualFullMotionReviewed=False,actualListening=False))
  raise
 finally:worker.close(remove=not collector.child_pending_or_alive(worker.record))

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--review-receipt');parser.add_argument('--execute',action='store_true');args=parser.parse_args()
 if args.execute:
  require(args.review_receipt,'Explicit --review-receipt after completed collector is required');r=execute(args.review_receipt);print(json.dumps(dict(complete=True,output=r['output'],samples=148,sourceSHA256=MASTER_SHA,actualVisualApproval=False)));return
 try:
  collector,context=prepare(args.review_receipt);reason=resource_reason(collector)
  print(json.dumps(dict(ready=context['reviewReceipt']is not None and reason is None,dryRun=True,reason=reason or('Post-collector review receipt required'if context['reviewReceipt']is None else None),frames=148,minimum=min(context['extra148']),maximum=max(context['extra148']),baseline=384,union=532,mediaStarted=False,sourceMasterBytesRehashed=False,outputsCreated=False)))
 except(RuntimeError,AssertionError,ValueError,FileNotFoundError,KeyError)as error:print(json.dumps(dict(ready=False,dryRun=True,reason=str(error),mediaStarted=False,outputsCreated=False)))
if __name__=='__main__':main()
