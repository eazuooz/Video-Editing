"""Read-only06.02 audio verification: measured seam annotations are not plan fields.

Imports the exact immutable V2 producer and preserves all of its checks. Only the
nested loop-plan comparison is replaced; no synthesis, FFmpeg, writes or workers.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,inspect,json,math,re,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PRODUCER_FILE=HERE/'prepare-prospect-refuge-audio-v2.py'
PRODUCER_SHA='a7692cdc0ca3fdda1916afa553a66c2d8d925878fe25579b9d35821d6990b1da'
SCHEMA='06-02-readonly-audio-verifier-v3'

def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))

def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

if sha(PRODUCER_FILE)!=PRODUCER_SHA:raise RuntimeError('Frozen selected audio producer changed')
producer=module('prospect_audio_v3_immutable_producer',PRODUCER_FILE)
base=producer.base;PROFILE=producer.PROFILE;Pending=producer.Pending


def require(ok,message):
 if not ok:raise Pending(message)


def _stereo_boundary(value,nullable):
 if value is None:return nullable
 return (type(value)is list and len(value)==2 and all(type(v)in(int,float)and math.isfinite(v)and abs(v)<=np.finfo(np.float32).max and float(np.float32(v))==v for v in value))


def _same_plan(a,b):
 if type(a)is not type(b):return False
 if type(b)is dict:return set(a)==set(b)and all(_same_plan(a[k],v)for k,v in b.items())
 if type(b)is list:return len(a)==len(b)and all(_same_plan(x,y)for x,y in zip(a,b))
 return a==b


def validate_loop_plan(actual,expected,result,folder):
 """Exact planned phase/clock; only measured stereo boundary fields may extend it."""
 require(type(actual)is dict and type(expected)is dict,'Music plan must be an object')
 extras={'sourceFloat32PcmSHA256','assembledFloat32PcmSHA256','actualMusicOnlyCrossfadeApplied','sourceArrayFloat32Stereo','actualListening'}
 require(set(actual)==set(expected)|extras,'Unknown/missing measured music-plan field')
 for key,value in expected.items():
  if key!='seams':require(_same_plan(actual.get(key),value),'Music repeat/source-phase plan differs: '+key)
 actual_seams=actual.get('seams');planned=expected['seams']
 require(type(actual_seams)is list and len(actual_seams)==len(planned),'Music seam count differs')
 for actual_seam,planned_seam in zip(actual_seams,planned):
  require(type(actual_seam)is dict and set(actual_seam)==set(planned_seam)|{'actualMusicBoundarySamples'},'Unknown/missing measured seam field')
  require(all(_same_plan(actual_seam[k],v)for k,v in planned_seam.items()),'Planned seam phase/range/curve changed')
  samples=actual_seam['actualMusicBoundarySamples']
  require(type(samples)is dict and set(samples)=={'before','at','lastOverlap','after'},'Measured seam boundary shape differs')
  a,z=planned_seam['destinationSampleRange']
  for name in samples:
   nullable=(name=='before'and a==0)or(name=='after'and z==expected['targetFrames'])
   require(_stereo_boundary(samples[name],nullable),'Measured seam samples must be exact finite stereoFloat32 values')
   if nullable:require(samples[name]is None,'Outside-source boundary must be null')
 for key in('sourceFloat32PcmSHA256','assembledFloat32PcmSHA256'):
  require(type(actual[key])is str and re.fullmatch('[0-9a-f]{64}',actual[key])is not None,'Measured music PCM hash malformed')
 require(actual['actualMusicOnlyCrossfadeApplied']is bool(planned)and actual['sourceArrayFloat32Stereo']is True and actual['actualListening']is False,'Measured music provenance flags differ')
 # Existing artifact verification has already checked every exact file hash.
 # Bind the measured annotations to this current immutable build, not an edited copy.
 require(result.get('musicLoopPlan')==actual,'Measured music receipt differs from actual current build')
 row=result.get('artifacts',{}).get('music-loop-plan.json',{})
 require(row.get('file')=='music-loop-plan.json'and sha(Path(folder)/'music-loop-plan.json')==row.get('sha256'),'Measured music-plan bytes are not pinned by current build')
 return dict(plannedSeamsVerified=len(planned),measuredAnnotationShapeVerified=True,measuredSamplesRecomputed=False,actualListening=False)


# Preserve every frozen producer check, replacing its one faulty nested comparison.
OLD_COMPARISON=" if any(actual_plan.get(k)!=v for k,v in expected_plan.items()):raise Pending('Music repeat/source-phase plan differs from approved1-second rule')"
NEW_COMPARISON=' validate_loop_plan(actual_plan,expected_plan,result,folder)'
original_verifier_source=inspect.getsource(producer.verified_audio_build)
if original_verifier_source.count(OLD_COMPARISON)!=1:raise RuntimeError('Frozen producer verifier comparison changed')
verified_source=original_verifier_source.replace(OLD_COMPARISON,NEW_COMPARISON)
_namespace=dict(producer.__dict__);_namespace['validate_loop_plan']=validate_loop_plan
exec(compile(verified_source,str(Path(__file__).resolve())+'::pinned-verifier','exec'),_namespace)
_checked_verifier=_namespace['verified_audio_build']


def verified_audio_build(path):
 if sha(PRODUCER_FILE)!=PRODUCER_SHA:raise Pending('Frozen selected audio producer changed')
 result=_checked_verifier(path)
 if sha(PRODUCER_FILE)!=PRODUCER_SHA:raise Pending('Frozen selected audio producer changed during verification')
 return result


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audio-build');a=p.parse_args()
 if not a.audio_build:
  print(json.dumps(dict(schemaVersion=SCHEMA,ready=False,reason='Exact actual audio-build path required',producer=pin(PRODUCER_FILE),writesPerformed=False,mediaModified=False,modelLoaded=False)));return
 try:
  result=verified_audio_build(a.audio_build)
  print(json.dumps(dict(schemaVersion=SCHEMA,ready=True,audioBuild=pin(a.audio_build),fingerprint=result['fingerprint'],mixWav=result['mixWav'],producer=pin(PRODUCER_FILE),measuredSeamAnnotations='hash-bound finite stereo samples; not independently re-decoded',writesPerformed=False,mediaModified=False,actualListening=False,humanApproval=False),ensure_ascii=False))
 except(Pending,ValueError,KeyError,FileNotFoundError)as error:
  print(json.dumps(dict(schemaVersion=SCHEMA,ready=False,reason=str(error),writesPerformed=False,mediaModified=False,modelLoaded=False),ensure_ascii=False))

if __name__=='__main__':main()
