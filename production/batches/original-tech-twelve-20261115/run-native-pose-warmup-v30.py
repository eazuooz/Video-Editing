"""Explicit D-drive native recovery identities; unchanged full resource guard."""
from pathlib import Path
import argparse,copy,importlib.util,json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z';DROOT=ROOT/'shared/output/original-tech-twelve-20261115'
CONFIG={'placement':('run-bounded-native-v3.py','shorts-horizon-gpu-placement','native-bounded-v3'),'temporal':('run-streamed-native-v2.py','shorts-inside-temporal-antialiasing','native-stream-v2'),'remaining-seven':('run-remaining-selected-native-v5.py','remaining-seven','native-stream-v2')}
def load(case):
 helper,slug,oldversion=CONFIG[case];s=importlib.util.spec_from_file_location('exact12_native_completion_'+case,HERE/helper);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.configure(case);original_prepare=m.prepare;original_busy=m.busy;original_verify=m.verify
 m.BASE=DROOT/slug/'native-pose-warmup-v30';m.PROTOCOL='original-tech-twelve-'+case+'-native-pose-warmup-v30';m.OWNER='original-tech-twelve-'+case+'-native-completion';m.runtime.PROTOCOL=m.PROTOCOL;m.runtime.OWNER=m.OWNER;m.native.guard.qualifier.BASE=m.BASE/'resource-observations'
 def prepare():
  p=original_prepare();d=m.read(HERE/'native-pose-warmup-v30/source-review.json');entry=next(x for x in d['cases']if x['case']==case);p=copy.deepcopy(p)
  for f in p['files']:
   hit=next((x for x in entry['replacements']if Path(x['original']['path']).resolve()==Path(f['source']).resolve()),None)
   if hit:
    assert m.pin(f['source'])==hit['original']and m.pin(hit['derived']['path'])==hit['derived'];f.update(source=hit['derived']['path'],sha256=hit['derived']['sha256'])
  compiler=Path(entry['compiler']['path']);assert m.pin(compiler)==entry['compiler'];c=m.read(compiler);assert c['staticCompilationPassed'];assert {str(Path(f['source']).resolve()):f['sha256']for f in p['files']if Path(f['source']).suffix=='.cs'}=={str(Path(x['path']).resolve()):x['sha256']for x in c['sourceInputs']}
  contract=dict(p['contract'],minimumFreeMediaBytes=2*1073741824,minimumFreeRepoBytes=512*1048576,initialRenderWarmup=(case=='remaining-seven'))
  fp=m.digest(dict(files=p['files'],generated=p['generated'],contract=contract,adapter=m.pin(__file__),originalAdapter=m.pin(HERE/helper),derivation=m.pin(HERE/'native-pose-warmup-v30/source-review.json'),compiler=entry['compiler'],encoder=p['encoder'],codecFixture=p['codecFixture']))
  p.update(fingerprint=fp,contract=contract,project=str(m.BASE/'projects'/fp[:16]),protocol=m.PROTOCOL,compiler=entry['compiler'],derivation=m.pin(HERE/'native-pose-warmup-v30/source-review.json'));return p
 def busy(token=None):
  if shutil.disk_usage(MEDIA).free<2*1073741824:return'Preserve2GiB media reserve'
  prior=MEDIA/slug/oldversion/'accepted-smoke.json';d=m.read(prior);clips=d['clips']
  if case=='remaining-seven':clips=[c for c in clips if c['camera']==('overview'if c['topic']in['spiderman','ratchet']else'detail')]
  estimate=sum(Path(c['video']['path']).stat().st_size for c in clips)*720/32*1.25+256*1048576
  if shutil.disk_usage(ROOT).free<512*1048576+estimate:return'Preserve512MiB plus source-derived full-capture estimate,25% margin and isolated Library'
  return original_busy(token)
 def reviewed(prep):
  path=m.BASE/'smoke-visual-review-v30.json'
  if not path.exists():return False
  d=m.read(path);assert d['fingerprint']==prep['fingerprint']and d['actualSourceFramesInspected']and m.pin(d['smokeProof']['path'])==d['smokeProof'];return d['allowedForFullCapture']is True
 m.prepare=prepare;m.busy=busy;m.reviewed_for_full=reviewed
 return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CONFIG,required=True);p.add_argument('--stage',action='store_true');p.add_argument('--execute',action='store_true');p.add_argument('--mode',choices=['smoke','full'],default='smoke');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert 0<=a.wait_minutes<=180;m=load(a.case);prepared=m.prepare()
 if a.stage:m.stage(prepared)
 r=m.execute(prepared,a.mode,a.wait_minutes)if a.execute else dict(sourceReady=True,staged=a.stage,fingerprint=prepared['fingerprint'],project=prepared['project'],guardReason=m.busy(),gpuStarted=False,unityStarted=False);print(json.dumps(r),flush=True)
if __name__=='__main__':main()
