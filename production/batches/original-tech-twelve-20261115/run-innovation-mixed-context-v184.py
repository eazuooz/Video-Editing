"""One independent complete mixed utterance for the ambiguous temporal-AA term."""
from pathlib import Path
import argparse,importlib.util,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
wrapper=module('intro184_mixed_parent',H/'run-innovation-mixed-asr-v182.py');m=wrapper.m;read,pin=m.read,m.pin;m.BASE=C/'mixed-context-v184';m.PROTOCOL='original-tech-twelve-innovation-mixed-context-v184';m.OWNER='original-tech-twelve-innovation-mixed-context';m.runtime.PROTOCOL=m.PROTOCOL;m.runtime.OWNER=m.OWNER;m.native.guard.qualifier.BASE=m.BASE/'resource-observations'
def prepare():
 m.native.authority();vp=C/'voice/voice-generation-complete-proof.json';v=read(vp);np=H/'innovation-opening-narration-v181.json';n=read(np);unit=next(u for u in n['units']if u['id']=='o05u02');timing=read(v['unitTiming']['path'])['entries'];t=next(x for x in timing if x['scene_id']=='o05u02');para=next(x for x in read(v['paragraphTiming']['path'])['entries']if x['id']=='o05');mp=C/'shorts-inside-temporal-antialiasing/audio-build-v182.json';mix=read(mp);a=round(t['start']*24000)-para['startSample'];b=round(t['end']*24000)-para['startSample'];assert 0<=a<b<=mix['introSamples'];assert pin(mix['mix']['path'])==mix['mix']
 task=dict(key='take-complete-o05u02',kind='independent-complete-mixed-utterance',paragraph='o05',path=mix['mix']['path'],sha256=mix['mix']['sha256'],startSample=a,endSample=b,offsetSample=a,expected=unit['ko'])
 identity=dict(protocol=m.PROTOCOL,executionResourcePolicy=m.native.cooperative_policy_proof,adapter=pin(__file__),underlyingWorker=pin(H/'run-audible-mixed-asr-v146.py'),originalWholeMixReview=pin(C/'mixed-asr-v182/0e25224ba7a178792c9e4db1/review.json'),mixProof=pin(mp),voiceProof=pin(vp),sourceNarration=pin(np),trusted=pin(m.TRUSTED),modelPins=m.APPROVED['modelPins'],profile=m.APPROVED['profile'],tasks=[task],expectedTextNotUsedAsPrompt=True,productionPcmModified=False)
 fp=m.digest(identity);return dict(fingerprint=fp,identity=identity,output=str(m.BASE/fp[:24]))
m.prepare=prepare
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);a=ap.parse_args();assert a.project==m.P.name
 if a.execute:
  assert a.wait_minutes==15;m.BOOTSTRAP_PINS=module('intro184_context_bootstrap',H/'bootstrap-parent-identity-v1.py').install(m.native,__file__,a.project,m.BASE,m.PROTOCOL,m.OWNER);r=m.execute(15)
 else:r=dict(sourceReady=True,guardReason=m.busy(),modelStarted=False)
 print(json.dumps(r),flush=True)
if __name__=='__main__':main()
