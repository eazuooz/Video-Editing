"""Explicit changed startup-pose review; strict roundtrip and full-to-smoke parity."""
from pathlib import Path
import argparse,inspect,importlib.util,json
H=Path(__file__).resolve().parent
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def configured():
 adapter=load('pose_geometry30',H/'run-native-pose-warmup-v30.py');m=adapter.load('remaining-seven');m.BASE=m.DROOT/'remaining-seven/native-reviewed-pose-v35'if hasattr(m,'DROOT')else H.parents[2]/'shared/output/original-tech-twelve-20261115/remaining-seven/native-reviewed-pose-v35';m.PROTOCOL='original-tech-twelve-remaining-seven-native-reviewed-pose-v35';m.OWNER='original-tech-twelve-remaining-seven-native-reviewed-pose';m.runtime.PROTOCOL=m.PROTOCOL;m.runtime.OWNER=m.OWNER;m.native.guard.qualifier.BASE=m.BASE/'resource-observations';load('cooperative19',H/'cooperative-resource-policy-v19.py').install(m.native)
 source=inspect.getsource(m.verify);needle="prior_frames=read(prior['frameRgbManifest']['path'])['frames'];assert streamed['frames'][:32]==prior_frames,'Per-frame source pixels changed under batched callback scheduling'";assert source.count(needle)==1
 replacement="""prior_frames=read(prior['frameRgbManifest']['path'])['frames']
                if purpose=='smoke':
                    assert streamed['frames'][1:32]==prior_frames[1:32],'Changed existing frames beyond explicit startup correction'
                    if topic not in ['spiderman','ratchet','doom']:assert streamed['frames'][:32]==prior_frames
                    old_trace=read(prior['trace']['path']);assert [x['model']for x in trace['frames']]==[x['model']for x in old_trace['frames']],'Rule model changed'
                else:
                    baseline=read(BASE/'accepted-smoke.json');own=next(c for c in baseline['clips']if c['topic']==topic and c['mode']==mode and c['camera']==camera);assert streamed['frames'][:32]==read(own['frameRgbManifest']['path'])['frames'],'Full capture differs from explicitly reviewed corrected startup baseline'"""
 source=source.replace(needle,replacement);exec(compile(source,str(Path(__file__).resolve())+':explicit-verify','exec'),m.__dict__)
 m.reviewed_for_full=lambda p: (m.BASE/'smoke-visual-review-v35.json').exists()and m.read(m.BASE/'smoke-visual-review-v35.json')['fingerprint']==p['fingerprint']and m.read(m.BASE/'smoke-visual-review-v35.json')['allowedForFullCapture']and m.pin(m.BASE/'accepted-smoke.json')==m.read(m.BASE/'smoke-visual-review-v35.json')['smokeProof']
 m.release_own_library=lambda p:dict(removed=False,reason='Preserve this own regenerable Library; no deletion requested')
 return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');p.add_argument('--execute',action='store_true');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();m=configured();prepared=m.prepare()
 if a.stage:m.stage(prepared)
 r=m.execute(prepared,'full',a.wait_minutes)if a.execute else dict(sourceReady=True,fingerprint=prepared['fingerprint'],guardReason=m.busy(),executionResourcePolicy=m.native.cooperative_policy_proof)
 print(json.dumps(r))
if __name__=='__main__':main()
