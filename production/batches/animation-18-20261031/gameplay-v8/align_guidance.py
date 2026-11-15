"""Align new observation clauses to the actual mixed-voice word endpoints."""
from common import *
import ast,bisect,math,re
from difflib import SequenceMatcher

def aligner():
 p=ROOT/'projects/animation-breaking-down-attack-animations/production/grid-v1/caption_pipeline.py'
 tree=ast.parse(p.read_text(encoding='utf-8-sig'));names={'normalized','linear','align_characters'}
 nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 ns=dict(bisect=bisect,re=re,math=math,SequenceMatcher=SequenceMatcher)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns);return ns

def write_srt(p,rows):
 def stamp(t):
  n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,n=divmod(n,1000)
  return f'{h:02}:{m:02}:{s:02},{n:03}'
 Path(p).write_text(''.join(f"{i}\n{stamp(r['start'])} --> {stamp(r['end'])}\n{r['text']}\n\n" for i,r in enumerate(rows,1)),encoding='utf-8')

def main():
 ns=aligner();aliases={'DJ':'디제이'};evidence=[]
 for e in read(HERE/'plan.json')['episodes']:
  if e['id']=='A06':continue
  ep=e['id'];p=WORK/ep/'audio.json';m=read(p);changes=m['changes'];guides=[r for r in changes if r.get('kind')=='music-only-observation-guidance']
  if not guides:continue
  aligned={}
  for r in guides:
   asrpath=WORK/ep/'voice-qa'/(r['id']+'.json');asr=read(asrpath);assert asr['contentStatus'].startswith('passed-'),r['id']
   try:starts,ends,proof=ns['align_characters'](r['ko'],asr['asr']['chunks'],r['naturalDuration'],aliases,.93)
   except ValueError:
    # One verified clause has no internal cue boundary. A zero-width ASR word
    # cannot locate an internal character, but actual outer words locate this cue.
    intervals=[w['timestamp'] for w in asr['asr']['chunks'] if ns['normalized'](w.get('text',''),aliases)]
    assert len(r['units'])==1 and intervals and all(len(v)==2 and None not in v and 0<=v[0]<=v[1]<=r['naturalDuration']+.03 for v in intervals)
    assert any(a==b for a,b in intervals) and all(a[1]<=b[0]+.002 for a,b in zip(intervals,intervals[1:]))
    a,b=intervals[0][0],min(r['naturalDuration'],intervals[-1][1]);assert b>a
    count=len(ns['normalized'](r['ko'],aliases));starts=[a]*count;ends=[b]*count
    proof=dict(boundaryMethod='Single verified clause: first/last actual ASR-word endpoints; zero-width internal token does not define a cue boundary.',
     matchingCharacterCoverage=asr['coverage'],zeroWidthInternalWords=sum(a==b for a,b in intervals),outerEndpoints=[a,b])
   cursor=0;units=[]
   for u in r['units']:
    count=len(ns['normalized'](u['ko'],aliases));a=starts[cursor];b=ends[cursor+count-1];cursor+=count
    units.append(dict(start=r['newStartSeconds']+a,end=r['newStartSeconds']+b,ko=wrap_caption(u['ko']),en=wrap_caption(u['en'])))
   assert cursor==len(starts)
   aligned[r['id']]=units;evidence.append(dict(id=r['id'],asrFile=str(asrpath),asrSha256=sha(asrpath),units=units,alignment=proof))
  for lang in ['ko','en']:
   baseline=srt(next(f['path'] for f in e['baselineFiles'] if f['kind']==lang+'.srt'));lookup={r['captionIndex']:r for r in changes if r['captionIndex'] is not None};out=[]
   for i,c in enumerate(baseline):
    if i in lookup:
     r=lookup[i];out.append(dict(start=r['newStartSeconds'],end=r['newStartSeconds']+r['naturalDuration'],text=wrap_caption(r[lang])))
    else:out.append(dict(start=c['start']+(map_frame(round(c['start']*60),changes)-round(c['start']*60))/60,
                         end=c['end']+(map_frame(round(c['end']*60),changes)-round(c['end']*60))/60,text=c['text']))
   for units in aligned.values():out.extend(dict(start=u['start'],end=u['end'],text=u[lang]) for u in units)
   out.sort(key=lambda r:r['start']);assert all(a['end']<=b['start']+.002 for a,b in zip(out,out[1:])),ep
   write_srt(WORK/ep/(lang+'.srt'),out)
  m.update(captionAlignmentPending=False,guidanceCaptionAlignment='actual mixed-PCM Whisper words; ≥93%character matching; paired KO/EN units')
  save(p,m);print(ep,'guided clauses aligned',len(guides),flush=True)
 save(HERE/'guidance-caption-alignment.json',dict(records=evidence,allGuides=len(evidence),captionFontPx=48,timing='actual word endpoints',speechCompression=False))

if __name__=='__main__':main()
