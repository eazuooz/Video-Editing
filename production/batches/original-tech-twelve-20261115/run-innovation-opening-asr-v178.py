"""Recognize changed opening audio; reuse previous recognition only for exact PCM."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');C=M/'innovation-openings-v178';OLD=M/'innovation-openings-v176'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('existing_intro_asr178',H/'run-innovation-opening-asr-v176.py');read,pin,pcm=m.read,m.pin,m.pcm
m.P=ROOT/'projects/shorts-mario64-lakitu-camera';m.BASE=C/'asr';m.VOICE=C/'voice/voice-generation-complete-proof.json';m.PROTOCOL='original-tech-twelve-innovation-source-asr-v178';m.OWNER='original-tech-twelve-innovation-source-asr';m.runtime.PROTOCOL=m.PROTOCOL;m.runtime.OWNER=m.OWNER;m.native.guard.qualifier.BASE=m.BASE/'resource-observations'
def prepare():
 m.native.authority()
 if not m.VOICE.exists():return None
 v=read(m.VOICE);n=read(H/'innovation-opening-narration-v178.json');prior=Path(read(OLD/'asr/status.json')['review']['path']);oldr=read(prior);old_by={x['task']['key']:x for x in oldr['results']};assert len(v['rawChunks'])==len(n['units'])==25
 for p in v['identity']['sourceInputs']:assert pin(p['path'])==p
 assert pin(v['canonical']['path'])['sha256']==v['canonical']['sha256']
 entries=read(v['unitTiming']['path'])['entries'];alltasks=[]
 for raw,u,e in zip(v['rawChunks'],n['units'],entries):
  assert pin(raw['path'])['sha256']==raw['sha256'];alltasks.append(dict(key='unit-'+u['id'],kind='unit',unit=u['id'],paragraph=u['paragraph'],path=raw['path'],sha256=raw['sha256'],startSample=0,endSample=raw['frames'],offsetSample=round(e['start']*24000),expected=u['ko']))
 for e,p in zip(read(v['paragraphTiming']['path'])['entries'],n['paragraphs']):alltasks.append(dict(key='paragraph-'+p['id'],kind='paragraph',paragraph=p['id'],path=v['canonical']['path'],sha256=v['canonical']['sha256'],startSample=e['startSample'],endSample=e['endSample'],offsetSample=e['startSample'],expected=p['ko']))
 fresh=[];reuse=[]
 for task in alltasks:
  old=old_by.get(task['key']);same=False
  if old and old['task']['expected']==task['expected']:
   x,y=old['task'],task
   oldpcm=pcm(x['path'],x['startSample'],x['endSample']);newpcm=pcm(y['path'],y['startSample'],y['endSample']);same=oldpcm==newpcm
  if same:reuse.append(dict(task=task,sourceReview=pin(prior),sourceTaskKey=task['key'],pcmSHA256=hashlib.sha256(newpcm).hexdigest()))
  else:fresh.append(task)
 assert len(fresh)==13 and len(reuse)==24 and len(alltasks)==37
 assert m.sha(m.TRUSTED)==m.APPROVED['trustedSHA256'] and m.sha(m.LEVEL)==m.APPROVED['firstLevelPrimitiveSHA256']
 identity=dict(executionResourcePolicy=m.native.cooperative_policy_proof,protocol=m.PROTOCOL,adapter=pin(__file__),worker=pin(H/'run-innovation-opening-asr-v176.py'),voiceProof=pin(m.VOICE),lockedNarration=pin(H/'innovation-opening-narration-v178.json'),trusted=pin(m.TRUSTED),modelPins=m.APPROVED['modelPins'],profile=m.APPROVED['profile'],tasks=fresh,reusedTasks=reuse,allTasks=alltasks,previousRecognition=pin(prior),previousLevels=pin(prior.parent/'levels.json'))
 fp=m.digest(identity);return dict(fingerprint=fp,identity=identity,output=str(m.BASE/fp[:24]))
m.prepare=prepare
def merge(job):
 folder=Path(job['output']);new=read(folder/'review.json');prior=read(job['identity']['previousRecognition']['path']);old_by={r['task']['key']:r for r in prior['results']};new_by={r['task']['key']:r for r in new['results']};reuse_by={r['task']['key']:r for r in job['identity']['reusedTasks']};records=[]
 for task in job['identity']['allTasks']:
  if task['key']in new_by:r=new_by[task['key']]
  else:
   proof=reuse_by[task['key']];assert hashlib.sha256(pcm(task['path'],task['startSample'],task['endSample'])).hexdigest()==proof['pcmSHA256'];r=dict(fingerprint=job['fingerprint'],task=task,rawRecognition=old_by[task['key']]['rawRecognition'],expectedPrompt=None,humanListening=False,recognitionReusedOnlyForByteExactPcm=proof)
  records.append(r)
 result=dict(fingerprint=job['fingerprint'],job=pin(folder/'job.json'),results=records,newRecognition=pin(folder/'review.json'),reusedSourceReview=job['identity']['previousRecognition'],newModelTaskCount=13,reusedTaskCount=24,wordTimestamps=True,actualListening=False,humanApproval=False)
 m.immutable(folder/'review-combined.json',result)
 levelref=m.levels(job);newlevels=read(levelref['path']);oldlevels=read(job['identity']['previousLevels']['path']);rows=newlevels['paragraphs']+[r for r in oldlevels['paragraphs']if r['key']in reuse_by];flags=newlevels['flags']+[f for f in oldlevels['flags']if f.get('taskKey')in reuse_by];assert len(rows)==37
 m.immutable(folder/'levels-combined.json',dict(fingerprint=job['fingerprint'],asrReview=pin(folder/'review-combined.json'),paragraphs=rows,flags=flags,newLevels=levelref,reusedLevels=job['identity']['previousLevels'],reusedNumericLevelsOnlyForByteExactPcm=True,actualListening=False,humanApproval=False))
 m.save(m.BASE/'status.json',dict(status='targeted-source-ASR-complete-combined-exact-PCM-evidence',review=pin(folder/'review-combined.json'),levels=pin(folder/'levels-combined.json'),modelCompleted=True,newTasks=13,reusedTasks=24));return dict(review=pin(folder/'review-combined.json'),levels=pin(folder/'levels-combined.json'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);a=ap.parse_args();assert a.project==m.P.name
 if a.execute:
  assert a.wait_minutes==15;m.BOOTSTRAP_PINS=module('intro178_bootstrap',H/'bootstrap-parent-identity-v1.py').install(m.native,__file__,a.project,m.BASE,m.PROTOCOL,m.OWNER);r=m.execute(15)
  if r.get('completed')or r.get('reusedExisting'):r=merge(prepare())
 else:
  job=prepare();r=dict(sourceReady=job is not None,newTasks=None if job is None else len(job['identity']['tasks']),modelStarted=False,guardReason=m.busy())
 print(json.dumps(r),flush=True)
if __name__=='__main__':main()
