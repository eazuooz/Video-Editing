"""CPU-only recovery of the exact11.05 construction pilot; no launch or GPU lease.

Default verifies existing capture data without writing. --collect exports only
validated editable files and subset evidence under the existing singleton lock.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
RUNNER=HERE/'run-solution-path-native.py'
RUNNER_SHA='7a35ea90be67054a1a7167cc99aa31389462ff70b581ada01f09a5ae1c8355fe'
sys.path.insert(0,str(HERE))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
if sha(RUNNER)!=RUNNER_SHA:raise RuntimeError('Review changed native validator before CPU recovery')
spec=importlib.util.spec_from_file_location('solution_cpu_existing_recovery',RUNNER);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
TARGETS=['construction']
def verify():
 m.need(sha(RUNNER)==RUNNER_SHA,'Native validator changed during CPU recovery')
 prov=m.authorize();found=m.scan(prov,TARGETS)
 m.need(set(found)==set(TARGETS),'Existing pilot is incomplete or invalid; CPU recovery never starts a replacement job')
 return prov,found
def collect():
 worker=m.rt.SingleWorker(m.WORKER,is_alive=m.live).acquire()
 try:
  old=m.read(m.STATE)if m.STATE.exists()else{}
  m.need(not m.live(old)and not m.pending_child(old),'Preserve a live or uninspected prior native child')
  prov,found=verify();request=m.request_fp(prov['physicalInputFingerprint'],TARGETS)
  result=m.export_and_record(prov,TARGETS,found,request)
  state=dict(protocol=m.PROTOCOL,owner=m.OWNER,**m.rt.identity(),token=worker.record['token'],status='native-subset-complete-visual-review-pending',phase='cpu-recovery-complete',child=None,fingerprint=request,physicalInputFingerprint=prov['physicalInputFingerprint'],requestedModes=TARGETS,output=None,gpuStarted=False,completed=True,captureComplete=result['captureComplete'],evidence=m.pin(m.EVIDENCE),recoveredExistingModes={mode:str(path)for mode,path in found.items()},sourceValidator=m.pin(RUNNER),cpuRecoveryOnly=True,recoveredAt=time.time(),actualVisualReview=False)
  m.save(m.STATE,state);return result
 finally:worker.close(remove=True)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--collect',action='store_true');a=parser.parse_args()
 if a.collect:
  result=collect();out=dict(topicId='11.05',cpuOnly=True,collected=True,capturedModes=result['capturedModes'],captureComplete=result['captureComplete'],voicePreparationAllowed=result['voicePreparationAllowed'],evidence=m.pin(m.EVIDENCE),gpuStarted=False,unityLaunched=False)
 else:
  prov,found=verify();out=dict(topicId='11.05',cpuOnly=True,collected=False,verifiedModes=list(found),physicalInputFingerprint=prov['physicalInputFingerprint'],validatorFingerprint=prov['validatorFingerprint'],gpuStarted=False,unityLaunched=False)
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
