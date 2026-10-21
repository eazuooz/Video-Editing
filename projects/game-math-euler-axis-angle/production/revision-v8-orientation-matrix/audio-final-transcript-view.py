"""Prepare all76 current-master paragraphs for direct human/agent text review.

Recognized text is never prompted with the script. Raw decoder text/words are
retained; clock-restart removal only creates a separately labeled timing view.
"""
from pathlib import Path
import difflib,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_final_view_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_final_view_clocks',H/'voice-analysis.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def main():
 c.validate();selected=c.read(H/'audio-final-input.json');asrfile=c.O/'final-aac-asr.json';asr=c.read(asrfile);assert asr['masterSha256']==selected['masterSha256']and c.sha(c.R/selected['master'])==selected['masterSha256']
 t=c.read(H/'timeline.json');al={s['id']:s for s in c.read(c.O/'source-alignment.json')['scenes']};script={s['id']:s for s in c.read(H/'voice-input.json')['scenes']};words,events=v.monotonic_word_view(asr['words'])
 scenes=[];paragraphs=[]
 for scene in t['scenes']:
  sid=scene['id'];begin,end=scene['startFrame']/60,scene.get('endFrame',scene['startFrame']+scene['frames'])/60
  # Timelines use endFrameExclusive in newer plans and endFrame in older ones.
  if'endFrameExclusive'in scene:end=scene['endFrameExclusive']/60
  chosen=[w for w in words if begin<=(w['timestamp'][0]+w['timestamp'][1])/2<end];raw=[w for w in asr['words']if w['timestamp'][0]is not None and w['timestamp'][1]is not None and begin<=(w['timestamp'][0]+w['timestamp'][1])/2<end]
  grouped={r['line']:[]for r in al[sid]['lines']}
  for word in chosen:
   a,b=word['timestamp'];overlaps=[max(0,min(b,begin+r['takeEnd'])-max(a,begin+r['takeStart']))for r in al[sid]['lines']]
   if max(overlaps)>0:index=max(range(len(overlaps)),key=lambda k:overlaps[k])
   else:index=min(range(len(al[sid]['lines'])),key=lambda k:abs((a+b)/2-(begin+(al[sid]['lines'][k]['takeStart']+al[sid]['lines'][k]['takeEnd'])/2)))
   grouped[index+1].append(word)
  local=[]
  for line,expected in enumerate(script[sid]['lines'],1):
   recognized=''.join(w['text']for w in grouped[line]).strip();a,b=v.n.normalized(expected),v.n.normalized(recognized);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
   row=dict(id=f'{sid}.L{line:02}',scene=sid,line=line,expected=expected,recognized=recognized,actualWordCount=len(grouped[line]),
    range=[begin+al[sid]['lines'][line-1]['takeStart'],begin+al[sid]['lines'][line-1]['takeEnd']],
    differences=[dict(kind=k,expected=a[i:j],recognized=b[l:m])for k,i,j,l,m in matcher.get_opcodes()if k!='equal'],directFullTextReview='pending',humanListening='pending')
   if sid=='m07'and line==2:row['scopedPronunciationAlias']=al[sid]['lines'][1].get('scopedPronunciationTimingAlias')
   paragraphs.append(row);local.append(row['id'])
  scenes.append(dict(id=sid,range=[begin,end],rawRecognizedText=''.join(w['text']for w in raw).strip(),
   derivedMonotonicRecognizedText=''.join(w['text']for w in chosen).strip(),paragraphIds=local))
 outside=[w for w in words if not any(s['range'][0]<=(w['timestamp'][0]+w['timestamp'][1])/2<s['range'][1]for s in scenes)]
 assert len(scenes)==13 and len(paragraphs)==76
 c.save(c.O/'final-transcript-view.json',dict(revision='orientation-matrix-v8',master=selected['master'],masterSha256=selected['masterSha256'],
  inputs=dict(finalAsrSha256=c.sha(asrfile),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json'),timelineSha256=c.sha(H/'timeline.json'),implementationSha256=c.sha(Path(__file__))),
  rawWholeText=asr['text'],rawAsrUnchanged=True,derivedClockRestartEvents=events,scenes=scenes,paragraphs=paragraphs,nonBodyWords=outside,
  direct76ParagraphReview='pending',automaticSemanticPass=False,humanWholeListening='pending'))
 print('Prepared13 current-master scene texts and76 paragraph comparisons;direct read still required')
if __name__=='__main__':main()
