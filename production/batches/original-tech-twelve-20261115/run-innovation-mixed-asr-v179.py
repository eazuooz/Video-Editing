"""One guarded blind full-mix and new-boundary review for the exact twelve."""
from pathlib import Path
import argparse,importlib.util,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');C=M/'innovation-openings-v178'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('existing_guarded_mixed_asr_177',H/'run-audible-mixed-asr-v146.py');read,pin=m.read,m.pin
m.P=ROOT/'projects/shorts-mario64-lakitu-camera';m.BASE=C/'mixed-asr-v179';m.PROTOCOL='original-tech-twelve-innovation-mixed-asr-v179';m.OWNER='original-tech-twelve-innovation-mixed-asr';m.runtime.PROTOCOL=m.PROTOCOL;m.runtime.OWNER=m.OWNER;m.native.guard.qualifier.BASE=m.BASE/'resource-observations'
def prepare():
 m.native.authority();p=C/'all-mixes-v179.json'
 if not p.exists():return None
 allmixes=read(p);plan=read(H/'innovation-opening-plan-v178.json');n=read(H/'innovation-opening-narration-v178.json');tasks=[]
 assert len(allmixes['mixes'])==len(plan['rows'])==12
 for ref,row in zip(allmixes['mixes'],plan['rows']):
  assert pin(ref['path'])==ref;d=read(ref['path']);assert d['bodyFloatPcmByteExact']and d['bodyVoiceMusicAndGameAudioUnmodified'];assert pin(d['mix']['path'])==d['mix']
  blocks=Path(row['baseline']['artifacts']['subtitlesKo']['path']).read_text('utf8').strip().split('\n\n');body=' '.join(' '.join(b.splitlines()[2:])for b in blocks);intro=row['newOpening']['ko']
  tasks.append(dict(key=f'take-o{row["order"]:02}',kind='whole-mix',order=row['order'],paragraph=f'o{row["order"]:02}',path=d['mix']['path'],sha256=d['mix']['sha256'],startSample=0,endSample=d['frames'],offsetSample=0,expected=intro+' '+body))
  second=n['paragraphs'][row['order']-1]['ko'];a=max(0,d['introSamples']-6*24000);b=min(d['frames'],d['introSamples']+12*24000)
  tasks.append(dict(key=f'join-o{row["order"]:02}',kind='new-opening-to-body-join',order=row['order'],path=d['mix']['path'],sha256=d['mix']['sha256'],startSample=a,endSample=b,offsetSample=a,boundarySample=d['introSamples'],sourceMixProof=ref))
 assert m.sha(m.TRUSTED)==m.APPROVED['trustedSHA256']and m.sha(m.LEVEL)==m.APPROVED['firstLevelPrimitiveSHA256']
 identity=dict(executionResourcePolicy=m.native.cooperative_policy_proof,protocol=m.PROTOCOL,adapter=pin(__file__),existingGuardedRecognizer=pin(H/'run-audible-mixed-asr-v146.py'),mixes=pin(p),sourcePlan=pin(H/'innovation-opening-plan-v178.json'),sourceVoiceReview=pin(C/'voice/technical-voice-review-v179.json'),trusted=pin(m.TRUSTED),modelPins=m.APPROVED['modelPins'],profile=m.APPROVED['profile'],recognizerProjection='stereo float24k mean to mono int16 for recognition only; production PCM unmodified',tasks=tasks)
 fp=m.digest(identity);return dict(fingerprint=fp,identity=identity,output=str(m.BASE/fp[:24]))
m.prepare=prepare
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);a=ap.parse_args();assert a.project==m.P.name
 if a.execute:
  assert a.wait_minutes==15;m.BOOTSTRAP_PINS=module('innovation_mixed_bootstrap177',H/'bootstrap-parent-identity-v1.py').install(m.native,__file__,a.project,m.BASE,m.PROTOCOL,m.OWNER);result=m.execute(15)
 else:
  job=prepare();result=dict(sourceReady=job is not None,tasks=None if job is None else len(job['identity']['tasks']),guardReason=m.busy(),modelStarted=False)
 print(json.dumps(result),flush=True)
if __name__=='__main__':main()
