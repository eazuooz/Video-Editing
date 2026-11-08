"""Finite11.05 repair:45 unchanged current raw copies plus3 missing-only raw takes.

Default is read-only. Only explicit --execute may acquire this project's voice
singleton, stage copies, or invoke Qwen. Qwen alone owns the shared GPU lease.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, os, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if str(HERE)not in sys.path:sys.path.insert(0,str(HERE))
PREPARER=HERE/'prepare-solution-path-voice-repair-v3.py'
PREPARER_SHA='3f4b18d0505e304e0216698b2a1c8287a3ae00587f1ddb2d3568102e89e25819'
LIFECYCLE=HERE/'run-selected-voice-repair-v4.py'
LIFECYCLE_SHA='c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366'
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
def sha(path):
 with Path(path).open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def check_sources():
 if sha(__file__)!=SELF_SHA or sha(PREPARER)!=PREPARER_SHA or sha(LIFECYCLE)!=LIFECYCLE_SHA:raise RuntimeError('Frozen scoped repair source changed')
 if 'prep'in globals():prep.check_sources() # Includes separately pinned Dvenv/cfg/Cbase; no resource calls.
check_sources()
prep=load('solution_voice_repair_v3_preparation',PREPARER)
life=load('solution_voice_repair_v3_private_lifecycle',LIFECYCLE)
base=life.base;life.REPAIR_PROTOCOL=prep.PROTOCOL
life.__file__=str(Path(__file__).resolve()) # Exact new adapter bytes, not old topic source, enter subset pins.
base.prep=prep.prep
base.zen.busy_reason=prep.voice_entry.audited_native_busy # Exact9429 classifier +unchanged8192/<15 Qwen gate.
resource=prep.voice_entry.resource
original_process_reason=resource.process_reason

def execute_parent_matches(info,own,parent):
 """Classify ONLY this exact eight-argv Dvenv->Cbase execute launcher.

 Actual V1 evidence: both command tails match but argv0/exe differ. This is
 process identity only, never lease ownership, completion or resource waiver.
 """
 try:
  fields=('pid','ppid','create_time','name','exe','cmdline')
  if any(any(k not in row or row[k]is None for k in fields)for row in(info,own,parent)):return False
  if any(type(row[k])is not int or row[k]<=0 for row in(info,own,parent)for k in('pid','ppid')):return False
  if any(type(row['create_time'])not in(int,float)or not math.isfinite(row['create_time'])or row['create_time']<=0 for row in(info,own,parent)):return False
  if own['pid']==parent['pid']or own['ppid']!=parent['pid']or info['pid']!=parent['pid']or info['ppid']!=parent['ppid']:return False
  args,pargs=own['cmdline'],parent['cmdline']
  if not isinstance(args,list)or not isinstance(pargs,list)or len(args)!=8 or len(pargs)!=8 or not all(isinstance(a,str)for a in args+pargs):return False
  if args[1:]!=pargs[1:]or info['cmdline']!=pargs or args[1:4]!=['-u','-X','utf8']or args[5:]!=['--execute','--wait-hours','6']:return False
  if Path(args[4]).resolve()!=Path(__file__).resolve():return False
  launcher=Path(prep.RUNTIME_PINS[0]['path']).resolve();body=Path(prep.RUNTIME_PINS[2]['path']).resolve()
  return (Path(pargs[0]).resolve()==Path(parent['exe']).resolve()==Path(info['exe']).resolve()==launcher
          and Path(args[0]).resolve()==Path(own['exe']).resolve()==body
          and own['name'].lower()==parent['name'].lower()==info['name'].lower()=='python.exe'
          and abs(info['create_time']-parent['create_time'])<.001 and 0<=own['create_time']-parent['create_time']<30)
 except(KeyError,TypeError,ValueError,OSError):return False

def own_wrapper_marker(record,own):
 """Additional restriction: an actual current singleton, not a new grant."""
 try:
  return (isinstance(record,dict)and record.get('protocol')==base.PROTOCOL
          and record.get('owner')=='architectural-111-11-05-voice'and record.get('topicId')=='11.05'
          and record.get('stage')=='voice'and isinstance(record.get('token'),str)and bool(record['token'])
          and record.get('pid')==own['pid']and type(record.get('createTime'))in(int,float)
          and math.isfinite(record['createTime'])and abs(record['createTime']-own['create_time'])<.001
          and record.get('argv')==own['cmdline']and record.get('commandSHA256')==base.digest(own['cmdline'])
          and record.get('child')is None)
 except(KeyError,TypeError,ValueError):return False

def scoped_process_reason(info,own_pid,qualified=frozenset()):
 if os.name=='nt'and own_pid==os.getpid()and info.get('pid')==os.getppid():
  try:
   fields=['pid','ppid','create_time','name','exe','cmdline'];own=resource.psutil.Process(os.getpid()).as_dict(fields);parent=resource.psutil.Process(own['ppid']).as_dict(fields)
   marker=Path(base.MEDIA)/'11-05-voice-worker.json';record=base.read(marker)
   if own_wrapper_marker(record,own)and execute_parent_matches(info,own,parent)and base.read(marker)==record:return None
  except(resource.psutil.NoSuchProcess,resource.psutil.AccessDenied,OSError,ValueError,KeyError,TypeError):pass
 return original_process_reason(info,own_pid,qualified)

resource.process_reason=scoped_process_reason # This new private9429 instance only; original source unchanged.
original_save=base.save
CURRENT=None
CURRENT_ARGS=None

def prepared(args):
 check_sources()
 if args.topic!='11.05':raise prep.Pending('Only selected11.05 repair supported')
 return prep.prepare(args.repair_plan,args.native_evidence,args.native_qa,args.narration)

def active_prepared(args):
 global CURRENT,CURRENT_ARGS
 CURRENT_ARGS=args;CURRENT=prepared(args);life.CURRENT=CURRENT;return CURRENT

def fresh_stage(full):
 """Recheck current root plan/narration/native pins before any stage/copy."""
 check_sources()
 if CURRENT_ARGS is None:raise RuntimeError('No current scoped repair invocation')
 fresh=prepared(CURRENT_ARGS)['_basePrepared']
 if full!=fresh:raise prep.Pending('Repair preparation inputs changed before staging')
 return prep.prep.core.immutable_stage(fresh)

def retry_owner_token(path,value):
 """Bounded WinError5 retry ONLY exact current owned JSON paths, never PCM."""
 try:
  marker=Path(base.MEDIA)/'11-05-voice-worker.json';record=base.read(marker);me=base.identity();owner='architectural-111-11-05-voice'
  if not any(Path(a).resolve()==Path(__file__).resolve()for a in me['argv']if isinstance(a,str)):return False
  if record.get('protocol')!=base.PROTOCOL or record.get('owner')!=owner or record.get('pid')!=me['pid']or abs(record.get('createTime',0)-me['createTime'])>=.01 or record.get('argv')!=me['argv']or record.get('commandSHA256')!=base.digest(me['argv'])or not record.get('token'):return False
  path=Path(path).resolve();media=Path(base.MEDIA).resolve()
  if path==media/'11-05-voice-progress.json':return record['token']if value.get('protocol')==base.PROTOCOL and value.get('owner')==owner and value.get('pid')==me['pid']and value.get('token')==record['token']else False
  if CURRENT is None or CURRENT['repair']['identity']['protocol']!=prep.PROTOCOL:return False
  if value.get('protocol')!=base.PROTOCOL or value.get('fingerprint')!=CURRENT['fingerprint']:return False
  if path==base.output_of(CURRENT)/'scene-progress.json':return record['token']
  return record['token']if path==media/'11-05-voice-evidence.json'and value.get('topicId')=='11.05'else False
 except(OSError,ValueError,TypeError,KeyError):return False

def metadata_save(path,value):
 token=retry_owner_token(path,value)
 if not token:return original_save(path,value)
 error=None
 for attempt in range(10):
  if attempt and retry_owner_token(path,value)!=token:raise error
  try:return original_save(path,value)
  except PermissionError as caught:
   error=caught
   if getattr(caught,'winerror',None)!=5 or attempt==9 or retry_owner_token(path,value)!=token:raise
   time.sleep(min(.05*(attempt+1),.25))

def install_hooks():
 # Reuse ONLY generic lifecycle/PCM/pending functions; all historical07 prose,
 # counts, source paths and plan validators are replaced before any invocation.
 life.prepared=prepared;life.active_prepared=active_prepared;life.original_stage=fresh_stage
 life.install_hooks();base.prepared=active_prepared;base.save=metadata_save

def arguments(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--topic',default='11.05');p.add_argument('--repair-plan',default=str(prep.PLAN));p.add_argument('--native-evidence');p.add_argument('--native-qa');p.add_argument('--narration',default=str(prep.NARRATION));p.add_argument('--execute',action='store_true');p.add_argument('--wait-hours',type=float,default=6);a=p.parse_args(argv);a.semantic_components=None
 if a.topic!='11.05'or not math.isfinite(a.wait_hours)or not 0<a.wait_hours<=6:raise ValueError('Only finite0..6hour selected11.05 repair supported')
 return a

def main(argv=None):
 a=arguments(argv);install_hooks()
 try:
  prov=active_prepared(a) # An unready source never creates a singleton/stage/queue.
  if a.execute:return base.execute(a)
  out=base.output_of(prov);complete=life.verify_complete(prov,out)if(out/'voice-complete-proof.json').is_file()else None
  print(json.dumps(dict(ready=True,topicId='11.05',fullVoiceFingerprint=prov['fingerprint'],repairFingerprint=prov['repair']['fingerprint'],fullSceneCount=48,reuseCount=45,missingOnlyCount=3,engineSceneIds=[s['id']for s in prov['repair']['missing']],existingComplete=bool(complete),staged=False,reuseCopied=False,modelStarted=False,gpuLeaseMutated=False),ensure_ascii=False))
 except(prep.Pending,base.prep.Pending,FileNotFoundError)as error:
  print(json.dumps(dict(ready=False,reason=str(error),staged=False,reuseCopied=False,modelStarted=False,gpuLeaseMutated=False),ensure_ascii=False))
  if a.execute:raise SystemExit(2)
if __name__=='__main__':main()
