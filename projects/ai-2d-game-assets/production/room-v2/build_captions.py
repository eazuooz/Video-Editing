"""Preserve original cues; align model-reviewed added clauses to independent ASR."""
from pathlib import Path
import json,difflib,importlib.util,hashlib
import numpy as np
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v2';OLD=P/'production/local'
spec=importlib.util.spec_from_file_location('previous_caption_helpers',P/'production/build_captions.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
plan=json.loads((H/'revision-plan.json').read_text('utf8'))['scenes'];tm=json.loads((L/'timeline.json').read_text('utf8'));oldtm=json.loads((OLD/'timeline.json').read_text('utf8'));oldcues=json.loads((OLD/'captions.json').read_text('utf8'));parts=json.loads((H/'caption-clauses.json').read_text('utf8'))['scenes']
cues=[];review=[]
for row in tm['scenes']:
 ident=row['id']
 if not ident.startswith('R'):
  before=next(s for s in oldtm['scenes'] if s['id']==ident);delta=row['start']-before['start']
  for c in oldcues:
   if c['scene']==ident:cues.append({**c,'start':c['start']+delta,'end':c['end']+delta})
  continue
 source=next(s for s in plan if s['id']==ident);clauses=next(s['parts'] for s in parts if s['id']==ident)
 asr=json.loads((L/'asr'/f'{ident}.json').read_text('utf8'));assert asr['audio_sha256']==row['sourceSha256']
 expected=helper.norm(source['ko']);recognized='';at=[]
 for w in asr['chunks']:
  a,b=w['timestamp'];n=helper.norm(helper.asr_spelling(w['text']))
  if a is None or b is None:continue
  recognized+=n;at.extend(np.linspace(a,b,max(1,len(n)),endpoint=False).tolist()[:len(n)])
 matcher=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);anchors={}
 for a,b,n in matcher.get_matching_blocks():
  for k in range(n):anchors[a+k]=at[b+k]
 if len(anchors)<2:raise ValueError(ident+' lacks alignment anchors')
 xs=np.array(sorted(anchors));ys=np.array([anchors[x] for x in xs]);mapped=np.interp(np.arange(len(expected)),xs,ys);mapped=np.maximum.accumulate(mapped)
 assert ''.join(''.join(p['ko'].split()) for p in clauses)==''.join(source['ko'].split()),ident
 assert ''.join(''.join(p['en'].split()) for p in clauses)==''.join(source['en'].split()),ident
 offset=0
 for part in clauses:
  n=len(helper.norm(part['ko']));a=float(mapped[min(offset,len(mapped)-1)]);offset+=n;b=float(mapped[offset]) if offset<len(mapped) else row['sourceDuration']
  cues.append({'scene':ident,'start':row['start']+a,'end':row['start']+b,'ko':helper.shown(part['ko']),'spoken':part['ko'],'en':part['en']})
 review.append({'id':ident,'expected':source['ko'],'recognized':asr['text'],'sequenceRatio':matcher.ratio(),'matched':len(anchors),'expectedCharacters':len(expected),'asrSha256':hashlib.file_digest((L/'asr'/f'{ident}.json').open('rb'),'sha256').hexdigest(),'humanListening':False})
for i,c in enumerate(cues):
 c['index']=i+1
 if i+1<len(cues):c['end']=min(c['end'],cues[i+1]['start'])
 if c['end']<=c['start']:raise ValueError(c)
(L/'captions.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2),'utf8');(H/'alignment-review.json').write_text(json.dumps({'method':'independent word ASR aligned to unchanged text; model-reviewed meaningful clauses; no human listening assertion','paragraphs':review},ensure_ascii=False,indent=2),'utf8')
for lang in ['ko','en']:
 s='\n\n'.join(f"{c['index']}\n{helper.stamp(c['start'])} --> {helper.stamp(c['end'])}\n{c[lang]}" for c in cues)+'\n'
 (L/f'captions.{lang}.srt').write_text(s,'utf8')
print('Aligned',len(cues),'cues; new min ratio',min(x['sequenceRatio'] for x in review))
