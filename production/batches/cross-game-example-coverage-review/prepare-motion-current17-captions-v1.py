"""Guarded current mixed-word captions; retain179 verified cues and add41 editable cues."""
from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,math,re
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OLD=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:re.sub(r'[^가-힣a-zA-Z0-9]','',s).lower()
review=read(R/'current17-mixed-complete-direct-review-v1.json');mix=read(R/'current-mix-execution-v1.json')
assert review['all17WholeAnd81IndependentContextsDirectlyCompared'] and review['currentMixedContentReviewPassed']
assert review['mixAacSha256']==mix['mixAacSha256']==sha(ROOT/mix['mixAac'])
outputs=['captions.ko.srt','captions.en.srt','captions.ko.ass','caption-alignment-v1.json','caption-layout-v1.json','measured-chapters-v1.json']
assert not any((R/v).exists() for v in outputs),'Never overwrite prepared captions.'
plan=read(R/'measured-current17-plan-v1.json');current={s['id']:s for s in plan['scenes']};previous={s['id']:s for s in plan['baselinePlan']['scenes']}
old=read(OLD/'caption-alignment-v1.json');oldlayout=read(OLD/'caption-layout-v1.json')
assert len(old['entries'])==179 and oldlayout['allCuesMeasured'] and not oldlayout['unresolvedLayoutErrors']
rows=[]
for cue in old['entries']:
 shift=(current[cue['scene']]['startFrame']-previous[cue['scene']]['startFrame'])/60
 rows.append({**cue,'start':cue['start']+shift,'end':cue['end']+shift,'retainedCue':cue['id'],'originalCueTextAndWrapPreserved':True})
groups=read(R/'current17-caption-editorial-groups-v1.json');assert groups['all15OriginalKoEnParagraphTextsPreserved']
contexts={v['id']:v for v in read(R/'current17-mixed-independent-context-plan-v1.json')['contexts']}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def wrap(text,limit):
 measure=lambda x:float(font.getlength(x))
 if measure(text)<=min(1050,limit):return [text],math.ceil(measure(text))+44
 words=text.split();options=[]
 for i in range(1,len(words)):
  lines=[' '.join(words[:i]),' '.join(words[i:])];widths=list(map(measure,lines))
  if max(widths)<=limit:options.append((abs(widths[0]-widths[1]),lines,widths))
 assert options,('Split cue editorially before rendering',text,limit)
 _,lines,widths=min(options,key=lambda v:v[0]);return lines,math.ceil(max(widths))+44
for sid in ['07b','08b','11b']:
 for paragraph in sorted(set(v['paragraph'] for v in groups['groups'] if v['scene']==sid)):
  units=[v for v in groups['groups'] if v['scene']==sid and v['paragraph']==paragraph]
  context=contexts[f'{sid}-p{paragraph:02d}'];path=R/f'current17-mixed-contexts-asr-v1/{context["id"]}.json';result=read(path)
  assert result['sourceSha256']==mix['decodedAacSha256'] and result['exactSourceStereoPcmBytesMatched']
  words=result['words'];expected=norm(''.join(v['ko'] for v in units));recognized=''.join(norm(v['text']) for v in words)
  indexes=[]
  for i,w in enumerate(words):indexes.extend([i]*len(norm(w['text'])))
  matcher=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);mapping={}
  for a,b,n in matcher.get_matching_blocks():
   for i in range(n):mapping[a+i]=b+i
  assert matcher.ratio()>.90,(sid,paragraph,'Inspect low-confidence timing instead of inferring')
  offset=0
  for unit in units:
   endoffset=offset+len(norm(unit['ko']));mapped=[mapping[i] for i in range(offset,endoffset) if i in mapping]
   assert mapped and len(mapped)/max(1,endoffset-offset)>.80,(unit['id'],'Timing needs manual boundary')
   first,last=words[indexes[min(mapped)]],words[indexes[max(mapped)]]
   assert first['timestamp'][0] is not None and last['timestamp'][1] is not None
   start=max(context['startSample']/48000,context['startSample']/48000+first['timestamp'][0]-.3)
   end=min(context['endSample']/48000,context['startSample']/48000+last['timestamp'][1]-.3)
   assert end-start>2/60
   # The re-framed PowerWash HUD retains its protected lower-left region.
   power=any(v.get('sourceKey')=='powerwash' and v['startFrame']/60<end and v['endFrame']/60>start for s in plan['scenes'] if not s['retainedBaseline'] for v in s['parts'])
   lines,width=wrap(unit['ko'],900 if power else 1570)
   rows.append(dict(scene=sid,paragraph=paragraph,start=start,end=end,ko=unit['ko'],en=unit['en'],lines=lines,boxWidth=width,newCue=True,editorialId=unit['id'],currentContextResultSha256=sha(path),contextAlignmentRatio=matcher.ratio(),unmatchedExpectedCharacters=endoffset-offset-len(mapped),timingSource='Directly compared current decoded-AAC independent paragraph words; word timestamps approximate and final audio/pixels required',finalCueTimingDirectlyReviewed=False))
   offset=endoffset
assert len(rows)==220
rows.sort(key=lambda x:x['start']);header=(OLD/'captions.ko.ass').read_text('utf-8-sig').split('[Events]')[0]
ass=header+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
def timestamp(t,ass=False):
 b=100 if ass else 1000;n=round(t*b)
 return f'{n//(b*3600):0{1 if ass else 2}d}:{n//(b*60)%60:02d}:{n//b%60:02d}{"." if ass else ","}{n%b:0{2 if ass else 3}d}'
placements=[];errors=[]
cuts=plan['baselinePlan']['cuts'];parts=[v for s in plan['scenes'] if not s['retainedBaseline'] for v in s['parts']]
retainedCuts=[]
for cut in cuts:
 sid=cut['scene'];shift=(current[sid]['startFrame']-previous[sid]['startFrame'])/60
 retainedCuts.append({**cut,'timelineStart':cut['timelineStart']+shift,'timelineEnd':cut['timelineEnd']+shift})
windows=retainedCuts+[dict(id=v['id'],sourceId='PF5L_2g9UVQ' if v.get('sourceKey')=='powerwash' else v.get('sourceKey'),timelineStart=v['startFrame']/60,timelineEnd=v['endFrame']/60) for v in parts]
for i,c in enumerate(rows,1):
 c['id']=i;a,b=c['start'],c['end'];assert 2<=a<b<=plan['bodyEnd']/60
 if i>1:assert a>=rows[i-2]['end']-.001,(i,a,rows[i-2]['end'],'Resolve overlapping timestamps')
 width=c['boxWidth'];height=len(c['lines'])*62+22;x=round(960-width/2);y=round(970-height/2)
 bounds=sorted(set(round(t*100)/100 for t in [a,b]+[t for w in windows for t in [w['timelineStart'],w['timelineEnd']] if a+.001<t<b-.001]))
 for start,end in zip(bounds,bounds[1:]):
  if end<=start:continue
  cut=next((v for v in windows if v['timelineStart']<=(start+end)/2<v['timelineEnd']),None)
  protected=[[27,969,475,1058],[1818,849,1900,1078]] if cut and cut['sourceId']=='PF5L_2g9UVQ' else []
  overlap=any(x<r[2] and x+width+14>r[0] and y<r[3] and y+height+14>r[1] for r in protected)
  if len(c['lines'])>2 or width>1614 or x<2 or x+width+16>1920 or y+height+16>1080 or overlap:errors.append(dict(cue=i,start=start,end=end,overlap=overlap))
  def event(layer,text):
   global ass
   ass+=f'Dialogue: {layer},{timestamp(start,True)},{timestamp(end,True)},Default,,0,0,0,,{text}\n'
  def box(xx,yy,color,border):return '{\\an7\\pos('+f'{xx},{yy}'+')\\p1\\bord'+str(border)+'\\shad0\\1c&H'+color+'&\\3c&H181B16&}m 0 0 l '+f'{width} 0 {width} {height} 0 {height}'
  event(0,box(x+14,y+14,'323C07',0));event(1,box(x,y,'FFFFFF',3))
  for n,line in enumerate(c['lines']):event(2,'{\\an5\\pos('+f'960,{y+42+n*62}'+')\\bord0\\shad0}'+line.replace('{','').replace('}',''))
  placements.append(dict(cue=i,start=start,end=end,scene=c['scene'],cut=cut['id'] if cut else None,lines=c['lines'],width=width,height=height,x=x,y=y,centerX=960,centerY=970,shadowBottom=y+height+14,protectedRegions=protected,overlap=overlap,finalCuePixelsReviewed=False))
assert not errors,errors
for lang in ['ko','en']:
 (R/f'captions.{lang}.srt').write_text('\n\n'.join(f'{c["id"]}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n'+('\n'.join(c['lines']) if lang=='ko' else c['en']) for c in rows)+'\n','utf-8')
(R/'captions.ko.ass').write_text(ass,'utf-8')
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
write(R/'caption-alignment-v1.json',dict(entries=rows,retainedCueCount=179,newCueCount=41,paragraphCount=81,allOriginalCueTextsAndWrapsPreserved=True,mixAacSha256=mix['mixAacSha256'],planSha256=sha(R/'measured-current17-plan-v1.json'),allNewCueTimingDirectlyReviewed=False))
write(R/'caption-layout-v1.json',dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),style='boxed-white-forest-v1',font='Malgun Gothic',fontSize=48,allCuesMeasured=True,unresolvedLayoutErrors=errors,cueCount=len(rows),segmentCount=len(placements),cues=placements,ass=(R/'captions.ko.ass').relative_to(ROOT).as_posix(),assSha256=sha(R/'captions.ko.ass'),mixAacSha256=mix['mixAacSha256'],allFinalCuePixelsReviewed=False,humanListeningApproved=False))
write(R/'measured-chapters-v1.json',dict(chapters=[dict(scene=s['id'],title=s.get('title',s['id']),start=s['startFrame']/60,startFrame=s['startFrame']) for s in plan['scenes']],intro=dict(startFrame=0,frames=120),membershipEnding=dict(startFrame=plan['totalFrames']-600,start=plan['bodyEnd']/60,frames=600,end=plan['seconds']),source='Actual current17 PCM mapping; platform chapter consolidation pending',mixAacSha256=mix['mixAacSha256'],savedOnPlatform=False))
print(json.dumps(dict(cues=220,retained=179,new=41,allCuesMeasured=True,finalPixelReview=False)))
