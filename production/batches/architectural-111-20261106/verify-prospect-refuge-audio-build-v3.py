"""Small CPU-only measured-loop annotation regression fixtures; no media/processes."""
import copy,hashlib,importlib.util,json,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audio_readonly_v3_fixtures',HERE/'verified-prospect-refuge-audio-build-v3.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def check(name,fn):
 fn();checks.append(name)
def fixture():
 expected=m.producer.loop_plan(100000,180000,48000);actual=copy.deepcopy(expected)
 actual.update(sourceFloat32PcmSHA256='a'*64,assembledFloat32PcmSHA256='b'*64,actualMusicOnlyCrossfadeApplied=True,sourceArrayFloat32Stereo=True,actualListening=False)
 for seam in actual['seams']:seam['actualMusicBoundarySamples']=dict(before=[0.,0.],at=[.125,-.25],lastOverlap=[-.5,.25],after=[0.,0.])
 return expected,actual

def run_case(mutator=None,accepted=False):
 expected,actual=fixture()
 if mutator:mutator(actual)
 with tempfile.TemporaryDirectory()as d:
  folder=Path(d);p=folder/'music-loop-plan.json';p.write_text(json.dumps(actual),encoding='utf-8')
  result=dict(musicLoopPlan=copy.deepcopy(actual),artifacts={'music-loop-plan.json':dict(file=p.name,sha256=m.sha(p))})
  try:m.validate_loop_plan(actual,expected,result,folder)
  except m.Pending:
   if accepted:raise
  else:
   if not accepted:raise AssertionError('Invalid measured plan was accepted')

def change_seam(key,value):return lambda x:x['seams'][0].__setitem__(key,value)
def change_sample(key,value):return lambda x:x['seams'][0]['actualMusicBoundarySamples'].__setitem__(key,value)
check('finite hash-bound stereo measurements extend unchanged exact plan',lambda:run_case(accepted=True))
for name,mutate in [
 ('changed source frame count',lambda x:x.__setitem__('sourceFrames',100001)),
 ('changed target count',lambda x:x.__setitem__('targetFrames',180001)),
 ('changed output duration',lambda x:x.__setitem__('outputDurationSeconds',4.)),
 ('changed source reset phase',lambda x:x['segments'][1].__setitem__('sourceSampleRange',[1,128001])),
 ('changed segment destination',lambda x:x['segments'][1].__setitem__('destinationSampleRange',[52001,180000])),
 ('changed playback speed',lambda x:x['segments'][1].__setitem__('sourcePlaybackRate',.9)),
 ('changed incoming seam phase',change_seam('incomingSourceSampleRange',[1,48001])),
 ('changed outgoing seam range',change_seam('outgoingSourceSampleRange',[52001,100001])),
 ('changed seam destination',change_seam('destinationSampleRange',[52001,100001])),
 ('changed curve',change_seam('curve','equal-power')),
 ('changed speech flag',change_seam('speechAffected',True)),
 ('unknown seam annotation',change_seam('inventedMeasurement',0)),
 ('unknown top annotation',lambda x:x.__setitem__('unknownProof',{})),
 ('missing samples',lambda x:x['seams'][0].pop('actualMusicBoundarySamples')),
 ('nonfinite sample',change_sample('at',[float('nan'),0.])),
 ('nonstereo sample',change_sample('at',[0.])),
 ('bool masquerading sample',change_sample('at',[True,0.])),
 ('unmeasured inner sample null',change_sample('at',None)),
 ('non-float32 exact sample',change_sample('at',[.1,0.])),
 ('extra measured channel key',change_sample('invented',0)),
 ('malformed PCM hash',lambda x:x.__setitem__('sourceFloat32PcmSHA256','not-a-hash')),
 ('listening claim',lambda x:x.__setitem__('actualListening',True)),
 ('bool replaced by one',lambda x:x.__setitem__('speechSamplesChanged',0)),
]:check(name,lambda mutate=mutate:run_case(mutate))

def detached():
 expected,actual=fixture()
 with tempfile.TemporaryDirectory()as d:
  p=Path(d)/'music-loop-plan.json';p.write_text(json.dumps(actual));result=dict(musicLoopPlan=actual,artifacts={p.name:dict(file=p.name,sha256='0'*64)})
  try:m.validate_loop_plan(actual,expected,result,p.parent)
  except m.Pending:return
  raise AssertionError('Detached artifact hash accepted')
check('changed current artifact hash rejected',detached)

def old_all_checks_preserved():
 assert m.verified_source.replace(m.NEW_COMPARISON,m.OLD_COMPARISON)==m.original_verifier_source
 assert m.sha(m.PRODUCER_FILE)==m.PRODUCER_SHA
 assert 'exec'not in m.verified_source and 'execute('not in m.verified_source
check('all frozen verifier checks retained except exact comparison',old_all_checks_preserved)
print(json.dumps(dict(passed=len(checks),checks=checks,sourceSHA256=m.sha(HERE/'verified-prospect-refuge-audio-build-v3.py'),modelLoaded=False,mediaModified=False),ensure_ascii=False))
