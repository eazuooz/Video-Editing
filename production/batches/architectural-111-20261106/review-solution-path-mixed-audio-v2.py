"""Read-only exact mix2 recognition/PCM analysis; --write saves a new review only.

No decoder, model, resource mutation, gain, audio transformation or old-QA rerun.
The unchanged numerical policy is evaluated on full actual mixed words.
"""
from __future__ import annotations
import argparse,ast,hashlib,importlib.util,json,math,sys,types,unicodedata
from fractions import Fraction
from pathlib import Path
import numpy as np
import soundfile as sf
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MIXED=HERE/'run-solution-path-mix-asr-v2.py'
MIXED_SHA='f677b0cddf08539add3117e2a8158285a91815341376856bdb46bf91be7ac5ac'
MATH=HERE/'first-level-continuity-review.py'
MATH_SHA='545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544'
BUILD=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05/audio-preparation-v6/f757aa2cb5fc7c9e9c0adb1a/audio-build.json')
JOB=BUILD.parent/'review/mixed-asr-v2/06da97bb600f0e63b75d482c/job.json'
REVIEW=JOB.parent/'review.json'
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def need(v,s):
 if not v:raise ValueError(s)
def norm(s):return ''.join(c for c in unicodedata.normalize('NFC',s).casefold() if c.isalnum())
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def math_functions():
 need(sha(MATH)==MATH_SHA,'Numerical policy source changed')
 tree=ast.parse(MATH.read_text(encoding='utf-8-sig'))
 policy=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLICY' for t in n.targets))
 names={'db','levels','trend','sample_window','scale_window'}
 nodes=[policy]+[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 scope=dict(np=np,math=math,Fraction=Fraction);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(MATH),'exec'),scope)
 return types.SimpleNamespace(**scope)
def prefix_words(words,expected):
 target=norm(expected);current='';found=[]
 for word in words:
  a,b=word['timestamp'];need(math.isfinite(a) and math.isfinite(b) and 0<=a<b,'Nonpositive whole ASR word; do not invent an edge')
  current+=norm(word['text']);found.append(word)
  need(target.startswith(current) or current==target,'Literal whole-word prefix does not match the explanation')
  if current==target:return found
 raise ValueError('Full explanation lacks exact complete recognized words')
def analyze():
 need(sha(__file__)==SELF_SHA and sha(MIXED)==MIXED_SHA,'Reviewed mixed analysis source changed')
 m=module('current_mixed2_numerical_source',MIXED);job=read(JOB);review=read(REVIEW);build=read(BUILD)
 need(m.digest(job['identity'])==job['fingerprint']=='06da97bb600f0e63b75d482c13b31bf5c35cb9cbd81a8dd59ed5cf75324458ec','Exact mixed job required')
 need(sha(BUILD)==job['identity']['audioBuildSHA256'] and review['fullActualMixCoverage'] and review['coveredSamples']==10579202,'Actual build/mix coverage differs')
 for row in job['sourcePins']:need(sha(row['path'])==row['sha256'],'Mixed source pin changed: '+row['path'])
 for task in job['identity']['tasks']:need(m.cached(job,task) is not None,'Actual mixed cache is incomplete')
 def existing(path,value):need(Path(path).resolve()==REVIEW.resolve() and value==review,'Mixed summary differs from actual caches')
 scope=dict(m.summary.__globals__,qa=types.SimpleNamespace(voice=types.SimpleNamespace(immutable_json=existing)))
 rebuilt=types.FunctionType(m.summary.__code__,scope,'read_only_current_mixed_summary')(job)
 need(rebuilt==review and len(review['takes'])==14 and len(review['boundaryWindows'])==13,'Exact27 actual mixed results required')
 q=math_functions();raw_frames=build['rawVoice']['frames'];files={
  'raw':(Path(build['rawVoice']['path']),24000,1,raw_frames),
  'normalized':(BUILD.parent/'narration-component-normalized.wav',24000,1,raw_frames),
  'prepared':(BUILD.parent/'narration-prepared-stem.wav',48000,2,raw_frames*2),
  'voice':(BUILD.parent/'narration-stem.wav',48000,2,raw_frames*2),
  'music':(BUILD.parent/'music-stem.wav',48000,2,raw_frames*2),
  'mix':(Path(build['mixWav']['path']),48000,2,raw_frames*2)}
 arrays={}
 for stage,(path,rate,channels,frames) in files.items():
  expected=build['rawVoice']['sha256'] if stage=='raw' else build['artifacts'][path.name]['sha256']
  need(sha(path)==expected,'Actual stage PCM changed: '+stage)
  info=sf.info(path);need((info.samplerate,info.channels,info.frames)==(rate,channels,frames),'Actual stage sample grid changed')
  arrays[stage]=sf.read(path,dtype='float32',always_2d=True)[0]
 paragraphs=[];flags=[]
 for para in review['paragraphs']:
  words=[]
  for w in para['globalWords']:
   a,b=w['timestamp']
   if not math.isfinite(a) or not math.isfinite(b) or a<0 or b<=a:
    flags.append(dict(kind='nonpositive-mixed-word-not-used-as-anchor',paragraph=para['paragraph'],word=w));continue
   row=dict(text=w['text'],startSeconds=a,endSeconds=b,durationSeconds=b-a,levels={})
   for stage,(_,rate,_,frames) in files.items():
    first,last=q.sample_window(a,b,rate);need(0<=first<last<=frames,'Mixed word exceeds actual PCM')
    row['levels'][stage]=q.levels(arrays[stage][first:last],rate)
   words.append(row)
  trends={stage:q.trend(words,stage) for stage in ['raw','normalized','prepared','voice','mix']}
  for stage,trend in trends.items():
   if trend['suspect']:flags.append(dict(kind='sustained-word-body-decline',scope='paragraph',paragraph=para['paragraph'],stage=stage,trend=trend))
  paragraphs.append(dict(paragraph=para['paragraph'],comparison=para['comparison'],words=words,trends=trends))
 groups=[];levels=read(BUILD.parent/'line-levels.json')['components']
 for p,ids in [(8,['p008-c01a','p008-c01b']),(13,['p013-c01a','p013-c01b','p013-c01c'])]:
  rows=[next(row for row in levels if row['sceneId']==sid) for sid in ids]
  expected=' '.join(row['text'] for row in rows);actual=prefix_words(review['paragraphs'][p-1]['globalWords'],expected)
  # These are whole recognized words from the actual mixed paragraph, not a
  # character-ratio or interpolation across the internal physical utterances.
  words=paragraphs[p-1]['words'][:len(actual)];need([norm(w['text']) for w in actual]==[norm(w['text']) for w in words],'Whole explanation word indexing differs')
  trends={stage:q.trend(words,stage) for stage in ['raw','normalized','prepared','voice','mix']}
  for stage,trend in trends.items():
   if trend['words']<q.POLICY['longTrendMinimumWords'] or trend['spanSeconds']<q.POLICY['longTrendMinimumSeconds'] or trend['suspect']:
    flags.append(dict(kind='whole-explanation-range-or-decline-hold',paragraph=p,stage=stage,trend=trend))
  groups.append(dict(paragraph=p,sceneIds=ids,expected=expected,recognized=' '.join(w['text'].strip() for w in actual),wholeWords=actual,trends=trends))
 for boundary in review['boundaryWindows']:
  for flag in boundary['boundaryFlags']:flags.append(dict(kind='mixed-boundary-window-flag',key=boundary['task']['key'],flag=flag))
 differences=[dict(paragraph=p['paragraph'],differences=p['comparison']['characterDifferences']) for p in paragraphs if p['comparison']['characterDifferences']]
 hard=any(f['kind'] in ('sustained-word-body-decline','whole-explanation-range-or-decline-hold') for f in flags)
 result=dict(schemaVersion='11.05-mixed-stage-word-level-review-v2',inputs=[pin(__file__),pin(MIXED),pin(MATH),pin(JOB),pin(REVIEW),pin(BUILD)]+[pin(v[0]) for v in files.values()],policy=q.POLICY,paragraphs=paragraphs,wholeExplanations=groups,retainedLiteralDifferences=differences,flags=flags,numericalHold=hard,otherFlagDisposition='Nonpositive words are excluded from numerical anchors and retained for explicit content review; boundary flags are preserved, not automatically approved.',actualMixedRecognitionComplete=True,fullActualMixCoverage=True,encodedAACChecked=False,actualListening=False,humanApproval=False,automaticSpeechPass=False,finalVideoComplete=False)
 need(sha(__file__)==SELF_SHA and sha(MIXED)==MIXED_SHA,'Source changed during numerical review')
 return result
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args();result=analyze()
 data=(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode();fingerprint=hashlib.sha256(data).hexdigest()
 path=JOB.parent/'mixed-stage-word-level-review-v2'/fingerprint[:24]/'review.json'
 if args.write:
  if path.exists():need(path.read_bytes()==data,'Preserve differing numerical review')
  else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 print(json.dumps(dict(ready=True,review=pin(path) if path.exists() else str(path),numericalHold=result['numericalHold'],flags=result['flags'],retainedLiteralDifferenceParagraphs=[r['paragraph'] for r in result['retainedLiteralDifferences']],wholeExplanationTrends=[dict(paragraph=g['paragraph'],trends=g['trends']) for g in result['wholeExplanations']],actualListening=False),ensure_ascii=False))
if __name__=='__main__':main()
