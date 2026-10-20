"""CPU paragraph-clip gain plan for sustained source-TTS level decay.

No source samples or timings change. Only selected sustained-decay scenes use
constant gains on complete paragraph groups; transitions are inside verified
80ms quiet. Phrase emphasis and word/terminal-syllable dynamics stay intact.
"""
from pathlib import Path
import hashlib,importlib.util,json,math,runpy,sys
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v6_gain_pacing',H/'voice-pacing.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
R,P,V=p.R,p.P,p.O
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.asarray(x,dtype=np.float64)**2)))
def curve(row,samples,rate=48000):
 """Linear-in-dB joins occupy ONLY the independently verified quiet window."""
 out=np.full(samples,row['groups'][0]['constantGainDb'],dtype=np.float32)
 for boundary,group in zip(row['boundaries'],row['groups'][1:]):
  a=round(boundary['quietWindowSamples'][0]*rate/24000);b=round(boundary['quietWindowSamples'][1]*rate/24000)
  assert 0<=a<b<=samples
  old=float(out[a]);new=group['constantGainDb']
  out[a:b]=np.linspace(old,new,b-a,dtype=np.float32);out[b:]=new
 return np.power(np.float32(10),out/np.float32(20))
def main():
 assert p.read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 alignment_file=V/'voice-alignment.json';alignment=p.read(alignment_file);mapping_file=V/'current-pcm.json'
 assert alignment['inputs']['currentPcmMappingSha256']==p.sha(mapping_file) and not alignment['pendingSeams']
 spoken={s['id']:s for s in p.read(H/'voice-input.ko.json')['scenes']}
 old=sys.argv[:];sys.argv=[sys.argv[0],P.name]
 try:helpers=runpy.run_path(str(R/'production/batches/game-math-part2-full-series/align.py'),run_name='v6_gain_alignment_helpers')
 finally:sys.argv=old
 spec=importlib.util.spec_from_file_location('v6_gain_normalize',H/'voice-normalize.py');aliases=importlib.util.module_from_spec(spec);spec.loader.exec_module(aliases);normalize=aliases.install(helpers)
 primary=p.read(V/'seam-pending-review.json');breathing=p.read(V/'breathing-pending-review.json');rows=[]
 for scene in alignment['scenes']:
  sid=scene['id'];source=R/scene['wav'];asr=p.read(R/scene['asrFile']);assert p.sha(source)==scene['wavSha256']==asr['audio_sha256']
  x,rate=sf.read(source,dtype='float32');assert rate==24000
  words,_,_=p.calibrated_word_boundaries(sid,asr,scene['wavSha256'],x,rate,spoken[sid]['lines'],normalize,primary)
  words,_=p.calibrated_breathing_words(sid,words,scene['wavSha256'],x,rate,spoken[sid]['lines'],normalize,breathing)
  mask=np.zeros(len(x),bool)
  for word in words:
   a,b=word['timestamp'];mask[max(0,round(a*rate)):min(len(x),round(b*rate))]=True
  paragraph=[]
  for line in scene['lines']:
   lo,hi=round(line['rawStart']*rate),round(line['rawEnd']*rate);active=x[lo:hi][mask[lo:hi]];assert len(active)>rate*.4
   paragraph.append(dict(line=line['line'],sourceSpeechRmsDbfs=db(rms(active)),speechSamples=len(active),rawRange=[line['rawStart'],line['rawEnd']]))
  levels=[r['sourceSpeechRmsDbfs'] for r in paragraph];span=max(levels)-min(levels)
  # These are whole, several-second paragraphs, rather than low consonant or
  # sentence-tail windows. The retained scene32 take has no sustained6dB span.
  selected=span>=6 and len(paragraph)>=3
  text=normalize(' '.join(w['text'] for w in words));prefix='';word_rows=[]
  for word in words:
   begin=len(normalize(prefix));prefix+=' '+word['text'];end=len(normalize(prefix));word_rows.append(dict(word=word,begin=begin,end=end))
  boundaries=[];unavailable=[]
  if selected:
   for number in range(1,len(scene['lines'])):
    left=normalize(spoken[sid]['lines'][number-1])[-12:];right=normalize(spoken[sid]['lines'][number])[:8];opts=[]
    for j,w in enumerate(word_rows[:-1]):
     terminal=w['word'];following=word_rows[j+1]['word'];a,b=terminal['timestamp'][1],following['timestamp'][0]
     if abs(a-scene['lines'][number-1]['rawEnd'])>.35:continue
     if not text[:w['end']].endswith(left) or not text[w['end']:].startswith(right):continue
     quiet=p.quiet_seam(x,rate,a,b) if b>a else None
     if quiet:opts.append((abs(a-scene['lines'][number-1]['rawEnd']),quiet,terminal,following))
    if opts:
     _,q,terminal,following=min(opts,key=lambda z:z[0]);boundaries.append(dict(afterLine=number,sampleOffset=q['sampleOffset'],quietWindowSamples=q['quietWindowSamples'],quietRms=q['quietRms'],quietPeak=q['quietPeak'],terminalWord=terminal,nextWord=following,completeApprovedParagraphAndNextPrefixMatched=True))
    else:unavailable.append(dict(afterLine=number,action='Same constant-gain group across this boundary; no word-internal change or invented quiet.'))
  groups=[];starts=[0,*[b['sampleOffset'] for b in boundaries]];ends=[*[b['sampleOffset'] for b in boundaries],len(x)];first_line=1
  for i,(lo,hi) in enumerate(zip(starts,ends)):
   last_line=boundaries[i]['afterLine'] if i<len(boundaries) else len(paragraph)
   level=db(rms(x[lo:hi][mask[lo:hi]]));gain=-20-level;assert abs(gain)<24
   groups.append(dict(firstLine=first_line,lastLine=last_line,sourceSampleStart=lo,sourceSampleEnd=hi,sourceSpeechRmsDbfs=level,constantGainDb=gain,targetSpeechRmsDbfs=-20));first_line=last_line+1
  assert len(groups)==len(boundaries)+1 and all(a['sampleOffset']<b['sampleOffset'] for a,b in zip(boundaries,boundaries[1:]))
  rows.append(dict(id=sid,sourceFile=scene['wav'],sourceSha256=scene['wavSha256'],sourceSamples=len(x),sampleRate=rate,
   sustainedParagraphSpanDb=span,sourceParagraphs=paragraph,selectedForParagraphGroupGain=selected and len(groups)>1,
   reason='Whole-paragraph sustained source decay exceeds6dB; constant complete-group levels with unchanged intra-phrase prosody.' if selected else 'Retain one scene gain; no sustained6dB whole-paragraph span.',
   groups=groups,boundaries=boundaries,unavailableParagraphBoundaries=unavailable,sourcePcmChanged=False,timingChanged=False,humanListening='pending'))
 report=dict(schemaVersion=1,revision='article-flow-v6',scope='Processed narration only; actual whole-paragraph source decay evidence; no PCM/timing/ASR modification, no word compression.',
  inputs=dict(alignmentSha256=p.sha(alignment_file),currentPcmMappingSha256=p.sha(mapping_file),timingAliasesSha256=p.sha(H/'voice-normalize.py'),implementationSha256=p.sha(Path(__file__))),
  targetSpeechRmsDbfs=-20,normalization='One constant gain per verified complete-paragraph group;80ms quiet-only dB joins; one global LUFS/true-peak gain follows.',
  sceneCount=41,paragraphCount=250,selectedSceneCount=sum(r['selectedForParagraphGroupGain'] for r in rows),scenes=rows,humanWholeListening='pending')
 p.save(V/'paragraph-gain-plan.json',report);print('CPU paragraph gain plan:',report['selectedSceneCount'],'sustained-decay scenes;',sum(len(s['boundaries']) for s in rows),'verified quiet joins; no audio written.')
if __name__=='__main__':main()
