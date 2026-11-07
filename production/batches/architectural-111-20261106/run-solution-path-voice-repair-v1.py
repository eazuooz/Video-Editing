"""Finite11.05 repair:42 unchanged raw copies plus6 missing-only raw takes.

Default is read-only. Only explicit --execute may acquire this project's voice
singleton, stage copies, or invoke Qwen. Qwen alone owns the shared GPU lease.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if str(HERE)not in sys.path:sys.path.insert(0,str(HERE))
PREPARER=HERE/'prepare-solution-path-voice-repair-v1.py'
PREPARER_SHA='97e3e87ee7e95a06e7b0837b8bb7214c5fbf50b506124981ade184b1ad6339de'
LIFECYCLE=HERE/'run-selected-voice-repair-v4.py'
LIFECYCLE_SHA='c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366'
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
def sha(path):
 with Path(path).open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def check_sources():
 if sha(__file__)!=SELF_SHA or sha(PREPARER)!=PREPARER_SHA or sha(LIFECYCLE)!=LIFECYCLE_SHA:raise RuntimeError('Frozen scoped repair source changed')
check_sources()
prep=load('solution_voice_repair_v1_preparation',PREPARER)
life=load('solution_voice_repair_v1_private_lifecycle',LIFECYCLE)
base=life.base;life.REPAIR_PROTOCOL=prep.PROTOCOL
life.__file__=str(Path(__file__).resolve()) # Exact new adapter bytes, not old topic source, enter subset pins.
base.prep=prep.prep
base.zen.busy_reason=prep.voice_entry.audited_native_busy # Exact9429 classifier +unchanged8192/<15 Qwen gate.
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
  print(json.dumps(dict(ready=True,topicId='11.05',fullVoiceFingerprint=prov['fingerprint'],repairFingerprint=prov['repair']['fingerprint'],fullSceneCount=48,reuseCount=42,missingOnlyCount=6,engineSceneIds=[s['id']for s in prov['repair']['missing']],existingComplete=bool(complete),staged=False,reuseCopied=False,modelStarted=False,gpuLeaseMutated=False),ensure_ascii=False))
 except(prep.Pending,base.prep.Pending,FileNotFoundError)as error:
  print(json.dumps(dict(ready=False,reason=str(error),staged=False,reuseCopied=False,modelStarted=False,gpuLeaseMutated=False),ensure_ascii=False))
  if a.execute:raise SystemExit(2)
if __name__=='__main__':main()
