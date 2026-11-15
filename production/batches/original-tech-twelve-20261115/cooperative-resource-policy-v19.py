"""User-authorized utilization change, scoped to this exact12 process only.

Retain every legacy process, app-activity, memory, lease and ownership check.
Only the utilization gate changes. No shared/legacy module file is modified.
"""
from pathlib import Path
import ast,hashlib,inspect,json,os,subprocess
import psutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
KEY='explicitOriginalTechTwelve20261115';UTIL_BELOW=35
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def authority():
 p=HERE/'resource-policy-v19.json';d=json.loads(p.read_text('utf-8-sig'))
 assert d['userAuthorized']and d['gpuUtilizationBelowPercent']==UTIL_BELOW and d['scope']==KEY
 c=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))[KEY]
 assert c['automaticAdvanceWithinExactList']and not c['intermediateApprovalRequired']and c.get('status')not in ['stopped','paused','cancelled']
 return pin(p)
def install(native):
 authority()
 if getattr(native,'cooperative_policy_v19',False):return
 rt=native.guard.rt;original=inspect.getsource(rt.busy_reason)
 assert original.count('use>25')==1 and 'free<8192'in original
 revised=original.replace('use>25','use>=35')
 # Reviewable proof: changing this one comparison is the complete difference.
 assert revised.replace('use>=35','use>25')==original
 tree=ast.parse(revised);assert len(tree.body)==1 and isinstance(tree.body[0],ast.FunctionDef)
 namespace=dict(rt.__dict__);exec(compile(tree,str(HERE/'cooperative-resource-policy-v19.py'),'exec'),namespace)
 cloned=namespace['busy_reason']
 def base_busy(token=None):
  authority();namespace['PROTOCOL']=rt.PROTOCOL;namespace['OWNER']=rt.OWNER
  return cloned(token)
 rt.busy_reason=base_busy
 def busy(token=None):
  authority();reason=native.guard.busy_reason(token)
  if reason:return reason
  raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=native.CREATE)
  free,use=map(int,raw.splitlines()[0].replace(' ','').split(','))
  return f'Cooperative GPU start requires8192MiB free and utilization below35%; actual{free}MiB/{use}%'if free<8192 or use>=UTIL_BELOW else None
 native.busy=busy;native.CREATE|=getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)
 if os.name=='nt':psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
 native.cooperative_policy_v19=True
 native.cooperative_policy_proof=dict(policy=authority(),adapter=pin(__file__),utilizationBelow=UTIL_BELOW,legacyBaseFunctionSHA256=hashlib.sha256(original.encode()).hexdigest(),onlyBaseComparisonChanged=True,processAndAppChecksPreserved=True,memoryChecksPreserved=True,exclusiveLeasePreserved=True,foreignProcessesModified=False)
