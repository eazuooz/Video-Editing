"""Reuse exact content/geometry identities with the new authorized start gate."""
from pathlib import Path
import argparse,importlib.util,json
HERE=Path(__file__).resolve().parent
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['placement','temporal','remaining-seven'],required=True);p.add_argument('--stage',action='store_true');p.add_argument('--execute',action='store_true');p.add_argument('--mode',choices=['smoke','full'],default='smoke');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert 0<=a.wait_minutes<=180
 adapter=load('exact12_existing_geometry',HERE/'run-native-completion-v6.py');m=adapter.load(a.case);policy=load('exact12_cooperative_policy',HERE/'cooperative-resource-policy-v19.py');policy.install(m.native);save=m.save
 def observed_save(path,d):
  path=Path(path)
  if path.name=='launch.json':d=dict(d,utilizationBelow=35,executionResourcePolicy=m.native.cooperative_policy_proof,cooperativeLauncher=m.pin(__file__))
  if path.name in ['accepted-smoke.json','accepted-full.json']and not path.exists():d=dict(d,executionResourcePolicy=m.native.cooperative_policy_proof,cooperativeLauncher=m.pin(__file__))
  return save(path,d)
 m.save=observed_save;prepared=m.prepare()
 if a.stage:m.stage(prepared)
 r=m.execute(prepared,a.mode,a.wait_minutes)if a.execute else dict(sourceReady=True,fingerprint=prepared['fingerprint'],guardReason=m.busy(),executionResourcePolicy=m.native.cooperative_policy_proof,gpuStarted=False)
 print(json.dumps(r),flush=True)
if __name__=='__main__':main()
