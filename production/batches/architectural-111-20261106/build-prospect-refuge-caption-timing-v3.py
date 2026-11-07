"""06.02 caption V3: two exact same-PCM word-end display supports.

The frozen V2 handles all103 raw/96 logical clocks unchanged. This private
adapter adds only p010-c04's measured whole-word end after 만드는. Raw 다섯/5
recognition differences remain visible; no alias, model, decoder or time ratio.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import hashlib,importlib.util,sys
HERE=Path(__file__).resolve().parent
PREVIOUS=HERE/'build-prospect-refuge-caption-timing-v2.py'
PREVIOUS_SHA='1b15170b292d6acc557e4bd1b0dbbbf6aaf4a7cd4d64a8a51c800b693df6fee8'

def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

if sha(PREVIOUS)!=PREVIOUS_SHA:raise RuntimeError('Frozen103/96 V2 caption source changed')
_path=list(sys.path)
try:
 sys.path.insert(0,str(HERE));_spec=importlib.util.spec_from_file_location('prospect_caption_v3_private_frozen_v2',PREVIOUS);previous=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(previous)
finally:sys.path[:]=_path
ROOT=previous.ROOT;PROJECT=previous.PROJECT;MEDIA=previous.MEDIA
read=previous.read;pin=previous.pin;digest=previous.digest;Pending=previous.Pending;require=previous.require;assert_pin=previous.assert_pin
SUPPORT=PROJECT/'caption-word-boundary-support-v3.json'
SUPPORT_SHA='0ac7a0c3912e8f3ae60a051f0954556ed3829305c06b2f6205cf3d0e4a7a9b82'
SCHEMA='06.02-selected-caption-timing-v3'
POLICY=dict(previous.POLICY,explicitDisplaySupport='Existingp14 + exactp10 whole-left-word end; no numeral alias/ASR rewrite/withinword interpolation')
_p14_boundary_support=previous.boundary_support

def __getattr__(name):
 """Preserve the frozen raw voice/ASR/public literal binding API."""
 return getattr(previous,name)

def validate_added_support(proof,binding):
 require(proof.get('schemaVersion')=='06.02-explicit-raw-word-boundary-support-v3'and proof.get('topicId')=='06.02'and proof.get('status')=='root-accepted-exact-word-end-for-display-clock-only','Only scoped V3 whole-word display proof allowed')
 require(proof.get('sourceNarration')==pin(previous.NARRATION)and proof.get('semanticComponents')==pin(previous.COMPONENTS)and proof.get('previousSupport')==pin(previous.SUPPORT),'Current immutable source/103logical plan/p14 support pins differ')
 require(all(proof.get(k)is False for k in('aliasesApplied','recognitionModified','pcmModified','actualListening','automaticSpeechPass','humanApproval'))and proof.get('platformActions')==[],'Display support cannot imply recognition/PCM modification or hearing approval')
 require(proof.get('physicalComponentCount')==103 and proof.get('logicalGroupCount')==96 and proof.get('voiceFingerprint')==binding['voiceFingerprint'],'V3 display proof belongs to another103 raw voice')
 for role in('sourceVoiceEvidence','sourceAsrReview','sourceAsrJob'):assert_pin(proof[role])
 voice=read(proof['sourceVoiceEvidence']['path']);review=read(proof['sourceAsrReview']['path']);job=read(proof['sourceAsrJob']['path'])
 require(voice['fingerprint']==review['voiceFingerprint']==job['identity']['voiceFingerprint']==binding['voiceFingerprint']and review['fingerprint']==job['fingerprint'],'Pinned immutable raw voice and blind ASR proof disagree')
 rows=proof.get('bindings',[]);require(len(rows)==1,'Only one additional p010 display boundary supported');row=rows[0]
 require(row.get('id')=='p010-c04-after-mandeuneun'and row.get('sceneId')=='p010-c04'and row.get('canonicalCharOffsets')==[42,43]and row.get('canonicalLeftWord')=='만드는'and row.get('method')=='explicit-one-sided-actual-whole-word-end','Additional proof changed its exact canonical whole-word scope')
 ss=next((s for s in binding['sentences']if s['sceneId']=='p010-c04'),None)
 require(ss is not None and ss.get('physicalSceneIds')==['p010-c04']and ss['canonicalKo']==row['canonicalKo'],'Additional support must remain one unchanged physical/logical sentence')
 for k in('sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames'):require(ss['rawWav'][k]==row['rawWav'][k],'Exact same p010 physical raw identity required: '+k)
 require(all(row.get(k)is True for k in('reuseOnlyIfSameRawWavAndPcm','requireCurrentBlindWordRecordSameLocalTimestamp','noFallbackToCharacterRatio')),'Whole-word support must retain same-PCM and no-ratio conditions')
 require(row.get('recognizedWordIndex')==8 and row.get('recognizedWordLiteral')==' 만드는'and row.get('recognizedWordLocalSeconds')==[4.68,5.18]and row.get('boundaryRawSampleInTake')==124320,'p010 whole-word end must remain the measured124320 sample')
 require(row.get('followingRecognizedWordIndex')==9 and row.get('followingRecognizedWordLiteral')==' 5요소입니다.'and row.get('followingWordLocalOnsetSeconds')==5.18,'Following raw recognition must remain unchanged, no numeral alias')
 assert_pin(row['rawWav']);assert_pin(row['sourceAsrRecord']);origin=read(row['sourceAsrRecord']['path'])
 require(origin['task']['sceneId']=='p010-c04'and origin['task']['pcmIdentity']['pcmSHA256']==row['rawWav']['pcmSHA256']and origin['fingerprint']==review['fingerprint'],'Actual measured source word record belongs to another raw take')
 words=origin['rawRecognition']['chunks'];require(words[8]==dict(text=row['recognizedWordLiteral'],timestamp=row['recognizedWordLocalSeconds'])and words[9]['text']==row['followingRecognizedWordLiteral']and words[9]['timestamp'][0]==5.18,'Pinned measured source word/next onset differs')
 return dict(row,supportProof=pin(SUPPORT))

def boundary_support(binding):
 inherited=_p14_boundary_support(binding)
 require(SUPPORT.is_file()and sha(SUPPORT)==SUPPORT_SHA,'Exact additional V3 display-word proof changed/missing')
 row=validate_added_support(read(SUPPORT),binding);require(row['sceneId']not in inherited,'Additional proof must not override inheritedp14')
 return dict(inherited,**{row['sceneId']:row})

# This module instance is private; the immutable V2 file and all other callers
# retain their original validation. Only this scoped hook supplies measured rows.
previous.boundary_support=boundary_support

def prepare(asr_review=None,voice_evidence=None,audio_build=None,clock_proof=None):
 result=previous.prepare(asr_review,voice_evidence,audio_build,clock_proof)
 result['schemaVersion']=SCHEMA
 for row in result['inputs']:
  if row['role']=='captionAdapter':row['role']='previousCaptionAdapter'
 result['inputs']+= [dict(role='captionAdapter',**pin(__file__)),dict(role='additionalWholeWordDisplaySupport',**pin(SUPPORT))]
 result['policy']=POLICY;result['fingerprint']=digest(dict(inputs=result['inputs'],policy=POLICY));return result

def verify_existing(path):
 path=Path(path).resolve();actual=read(path);require(actual.get('schemaVersion')==SCHEMA and actual.get('topicId')=='06.02','Not selected06 captionV3 timing')
 refs={r['role']:r for r in actual.get('inputs',[])}
 for row in refs.values():assert_pin(row)
 fresh=prepare(refs['rawAsrReview']['path'],refs['voiceEvidence']['path']);require(actual==fresh,'Existing V3 artifact differs from exact current source/ASR/whole-word display support')
 require(path==(MEDIA/'caption-timing-v3'/fresh['fingerprint'][:24]/'caption-timing.json').resolve(),'CaptionV3 timing escaped immutable selected output')
 return dict(timing=actual,voice=read(refs['voiceEvidence']['path']),asr=read(refs['rawAsrReview']['path']))

def write_outputs(result):
 target=MEDIA/'caption-timing-v3'/result['fingerprint'][:24];files={'caption-timing.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n','captions.ko.srt':previous.old.base.srt(result['captions']['ko'],'ko'),'captions.en.srt':previous.old.base.srt(result['captions']['en'],'en')}
 for name,text in files.items():
  if(target/name).exists():require((target/name).read_text(encoding='utf8')==text,'Preserve different prior captionV3 output')
 for row in result['inputs']:assert_pin(row)
 target.mkdir(parents=True,exist_ok=True)
 for name,text in files.items():
  if not(target/name).exists():
   with(target/name).open('x',encoding='utf8')as f:f.write(text)
 return target

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--asr-review');p.add_argument('--voice-evidence');p.add_argument('--write',action='store_true');p.add_argument('--verify-existing');a=p.parse_args()
 try:
  result=verify_existing(a.verify_existing)['timing']if a.verify_existing else prepare(a.asr_review,a.voice_evidence);output=str(write_outputs(result))if a.write else None;print(json.dumps(dict(ready=True,fingerprint=result['fingerprint'],physicalComponents=103,logicalGroups=96,output=output,written=a.write,modelStarted=False)))
 except(Pending,FileNotFoundError)as e:
  if a.write:raise
  print(json.dumps(dict(ready=False,reason=str(e),written=False,modelStarted=False,rendererStarted=False)))
if __name__=='__main__':main()
