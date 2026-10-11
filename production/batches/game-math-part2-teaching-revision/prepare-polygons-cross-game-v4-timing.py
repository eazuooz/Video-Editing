"""Align only the new seven scenes, retaining all earlier current-hash timing."""
from pathlib import Path
import hashlib,importlib.util,json,re,sys
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
SLUG='game-math-polygons-cross-game-additions-v4'
sys.argv=[sys.argv[0],SLUG]
sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
spec=importlib.util.spec_from_file_location('revision_alignment',ROOT/'production/batches/game-math-part2-full-series/align.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
# Proper-name script/language aliases observed in complete raw read-backs.
# No numeral, condition, mathematical term or ASR data is substituted.
original_normalized=mod.normalized
def normalized(s):
 s=s.lower().replace('타이니','tiny').replace('글레이드','glade').replace('셰이프즈','shapes').replace('세이프즈','shapes')
 s=re.sub(r'(?<=shapes)\s+투',' 2',s)
 return original_normalized(s)
mod.normalized=normalized;mod.a.normalized=normalized
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
P=ROOT/'projects'/SLUG;m=read(P/'project.json');out=ROOT/m['tts']['outputDir']
O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons'
combined=read(O/'combined-addition-timing.json');old={k:v for k,v in combined.items() if v.get('ttsProject')!=SLUG}
ko=read(P/'script/narration.ko.json')['scenes'];en=read(P/'script/narration.en.json')['scenes'];pending=[]
for s,tr,ref in zip(ko,en,read(R/'polygons-v4-tts-map.json')):
 ident=ref['additionId'];wav=out/f'chunks/{s["id"]}-scene.wav';cache=out/f'asr/{s["id"]}.json'
 if not cache.exists():pending.append(ident);continue
 raw=read(cache);sha=hashlib.sha256(wav.read_bytes()).hexdigest();assert raw['audio_sha256']==sha
 samples,rate=sf.read(wav);duration=len(samples)/rate
 try:starts,ends,coverage=mod.a.align_characters(' '.join(s['lines']),raw['words'],duration)
 except ValueError as error:raise ValueError(f'{ident}/{s["id"]}: {error}') from error
 cursor=0;line_starts=[];line_ends=[];captions={'ko':[],'en':[]};sentences=[]
 for i,(line,english) in enumerate(zip(s['lines'],tr['lines'])):
  n=len(mod.normalized(line));line_starts.append(float(starts[cursor]));line_ends.append(float(ends[cursor+n-1]))
  count=max(len(mod.a.split_caption(line,32)),len(mod.a.split_caption(english,46)))
  offset=cursor
  for chunk,translated in zip(mod.a.partition_fixed(line,32,count),mod.a.partition_fixed(english,46,count)):
   length=len(mod.normalized(chunk));begin=float(starts[offset]);end=float(ends[offset+length-1]);assert end>begin
   for lang,text,width in [('ko',chunk,32),('en',translated,46)]:captions[lang].append({'start':begin,'end':end,'text':'\n'.join(mod.a.wrapped_lines(text,width)),'line':i})
   offset+=length
  assert offset==cursor+n;cursor+=n
  for sentence in re.split(r'(?<=[.!?])\s+',line):
   begin=sum(len(mod.normalized(x['text'])) for x in sentences);length=len(mod.normalized(sentence))
   sentences.append({'start':float(starts[begin]),'end':float(ends[begin+length-1]),'text':sentence})
 assert cursor==len(starts)
 combined[ident]={'id':ident,'ttsProject':SLUG,'ttsScene':s['id'],'sourceType':ref['sourceType'],'sceneSourceModule':ref['sceneSourceModule'],'voice':wav.relative_to(ROOT).as_posix(),'voiceSha256':sha,'voiceSeconds':duration,'seconds':duration+.6,'lineStarts':line_starts,'lineEnds':line_ends,'matchingCharacterCoverage':coverage,'captions':captions,'sentenceCues':sentences,'alignment':'current-hash word timestamps; raw meaning and listening reviewed separately'}
assert all(combined[k]==v for k,v in old.items())
assert not pending,('Complete current-hash ASR first',pending)
write(O/'combined-addition-timing.json',combined)
write(R/'polygons-v4-alignment-progress.json',{'alignedNew':len(ko),'earlierTimingExact':True,'pending':pending,'timingGate':.93,'humanListening':False,'movingPixels':False})
print(json.dumps({k:{'voiceSeconds':v['voiceSeconds'],'coverage':v['matchingCharacterCoverage']} for k,v in combined.items() if v.get('ttsProject')==SLUG}))
