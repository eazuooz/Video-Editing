"""Current-hash word alignment for the fourteen new scenes, never old PCM."""
from pathlib import Path
import hashlib,importlib.util,json,re,sys
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3';SLUG='game-math-quaternion-cross-game-additions-v3'
sys.argv=[sys.argv[0],SLUG];sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
spec=importlib.util.spec_from_file_location('revision_alignment',ROOT/'production/batches/game-math-part2-full-series/align.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
# The observed read-back spells the game name 비시지 as BCG. Match only that
# proper name for timing; never alias inverse terms, signs or vector numerals.
math_normalized=mod.normalized
def observed_game_name_normalized(value):
 value=value.lower().replace('비시지','bcg')
 value=value.replace('하나를','1을').replace('하나는','1은').replace('하나','1')
 # 사이 means "between", not the adjacent component numerals 사, 이.
 value=re.sub(r'(?<![가-힣])사이(?=의|에|에서|\s|$)','between',value)
 # The observed algebra name D, and the explicitly spoken component 1은.
 value=re.sub(r'(?<![가-힣])디(?=는|를|의|\s|$)','d',value)
 value=re.sub(r'(?<![가-힣])일(?=은)','1',value)
 return math_normalized(value)
mod.normalized=observed_game_name_normalized
mod.a.normalized=observed_game_name_normalized
read=lambda p:json.loads(p.read_text(encoding='utf8'))
P=ROOT/'projects'/SLUG;m=read(P/'project.json');out=ROOT/m['tts']['outputDir']
ko=read(P/'script/narration.ko.json')['scenes'];en=read(P/'script/narration.en.json')['scenes']
mapping=read(R/'tts-map.json');combined={};assert len(ko)==len(en)==len(mapping)==14
for s,tr,ref in zip(ko,en,mapping):
 assert s['id']==tr['id']==ref['ttsScene']
 ident=ref['additionId'];wav=out/f'chunks/{s["id"]}-scene.wav';cache=out/f'asr/{s["id"]}.json'
 raw=read(cache);sha=hashlib.sha256(wav.read_bytes()).hexdigest();assert raw['audio_sha256']==sha
 samples,rate=sf.read(wav);duration=len(samples)/rate
 print('Aligning current addition',ident,s['id'],flush=True)
 starts,ends,coverage=mod.a.align_characters(' '.join(s['lines']),raw['words'],duration)
 cursor=0;line_starts=[];line_ends=[];captions={'ko':[],'en':[]};sentences=[]
 for i,(line,english) in enumerate(zip(s['lines'],tr['lines'])):
  n=len(mod.normalized(line));line_starts.append(float(starts[cursor]));line_ends.append(float(ends[cursor+n-1]))
  count=max(len(mod.a.split_caption(line,32)),len(mod.a.split_caption(english,46)));offset=cursor
  for chunk,translated in zip(mod.a.partition_fixed(line,32,count),mod.a.partition_fixed(english,46,count)):
   length=len(mod.normalized(chunk));begin=float(starts[offset]);end=float(ends[offset+length-1]);assert end>begin
   for lang,text,width in [('ko',chunk,32),('en',translated,46)]:captions[lang].append(dict(start=begin,end=end,text='\n'.join(mod.a.wrapped_lines(text,width)),line=i))
   offset+=length
  assert offset==cursor+n;cursor+=n
  for sentence in re.split(r'(?<=[.!?])\s+',line):
   begin=sum(len(mod.normalized(x['text'])) for x in sentences);length=len(mod.normalized(sentence))
   sentences.append(dict(start=float(starts[begin]),end=float(ends[begin+length-1]),text=sentence))
 assert cursor==len(starts)
 reveals={};fragment_cues={}
 module=ROOT/'manim/projects/game-math-part2-teaching-revision/quaternion_four_game_v3.py'
 fragments=set(re.findall(r"sentence\('([^']+)'",module.read_text(encoding='utf8')))|{'현재 방향','달라지고','와이축으로'}
 normalized_script=mod.normalized(' '.join(s['lines']))
 for fragment in fragments:
  index=normalized_script.find(mod.normalized(fragment))
  if index>=0:fragment_cues[fragment]=float(starts[index])
 for color,word in {'red':'빨간','blue':'파란'}.items():
  index=mod.normalized(' '.join(s['lines'])).find(mod.normalized(word))
  if index>=0:reveals[color+'At']=float(starts[index])
 combined[ident]=dict(id=ident,ttsProject=SLUG,ttsScene=s['id'],sourceType=ref['sourceType'],sceneSourceModule='quaternion_four_game_v3',voice=wav.relative_to(ROOT).as_posix(),voiceSha256=sha,voiceSeconds=duration,seconds=duration+.6,lineStarts=line_starts,lineEnds=line_ends,matchingCharacterCoverage=coverage,captions=captions,sentenceCues=sentences,fragmentCues=fragment_cues,annotationReveal=reveals,alignment='Current-hash word timestamps; raw meaning and human listening reviewed separately')
(R/'combined-addition-timing.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:dict(voiceSeconds=v['voiceSeconds'],coverage=v['matchingCharacterCoverage']) for k,v in combined.items()}))
