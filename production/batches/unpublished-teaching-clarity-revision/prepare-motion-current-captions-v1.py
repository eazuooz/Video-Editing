"""Prepared retiming of KO/EN, fixed ASS, chapters and ending together.

Original166 cue texts and wraps are retained. New13 editable cues follow
directly compared current whole words. No model, render, old-file overwrite.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math,re
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:re.sub(r'[^가-힣a-zA-Z0-9]','',s)
plan=read(R/'measured-additive-plan-v1.json')
review=read(R/'current-mixed-complete-direct-review-v1.json')
mix=read(R/'current-mix-execution-v1.json')
assert review['currentMixedContentReviewPassed'] and review['all14WholeAnd66IndependentContextsDirectlyCompared']
assert review['mixAacSha256']==mix['mixAacSha256']
paths=[R/n for n in ['captions.ko.srt','captions.en.srt','captions.ko.ass','caption-layout-v1.json','caption-alignment-v1.json','measured-chapters-v1.json']]
assert not any(p.exists() for p in paths),'Inspect prepared captions; never overwrite completed work.'
base=ROOT/'projects/motion-sickness-games/production/final-v1'
old=read(base/'caption-alignment.json');oldplan=read(base/'plan.json')
oldlayout=read(base/'caption-layout-qa.json')
oldwrap={}
for c in oldlayout['cues']:oldwrap.setdefault(c['cue'],c)
current={s['id']:s for s in plan['scenes']};previous={s['id']:s for s in oldplan['scenes']}
rows=[]
for i,c in enumerate(old['entries'],1):
    shift=current[c['scene']]['start']-previous[c['scene']]['start']
    rows.append({**c,'start':c['start']+shift,'end':c['end']+shift,
      'lines':oldwrap[i]['lines'],'boxWidth':oldwrap[i]['width'],
      'retainedCue':i,'originalCueTextPreserved':True,'wrapMeasurement':'retained verified original Malgun48 canvas measurement'})
groups={
'00a':[
 (1,'게임의 목표를 따라가면서도 화면은 덜 돌릴 수 있을까요?',"Can we follow a game's target while turning the whole view less?"),
 (2,'청소 게임의 조준과 시점,','We will examine aiming and viewing in a cleaning game,'),
 (2,'퍼즐에서 방향이 바뀐 뒤','then, after the view changes in a puzzle game,'),
 (2,'목표를 찾는 단서를 차례로 보겠습니다.','the cues for recognizing a target.'),
 (3,'이 관찰을 멀미를 고려한 카메라 설정과','We will connect these observations to motion-sickness-aware camera choices'),
 (3,'되돌리기 기능의 설계로 연결해 보죠.','and a way to restore the original settings.'),
 (4,'먼저 물줄기로 바닥의 때를 지우는 장면에서,','First, as water removes dirt from the floor,'),
 (4,'빨간선으로 표시한 물줄기 방향과','watch the red line marking the spray direction'),
 (4,'파란 기둥 표시를 따로 보세요.','and the blue marker on the background post separately.')],
'06b':[
 (1,'조준을 나눠도, 다른 방향을 본 뒤에는','Even with separate aiming, after looking in another direction,'),
 (1,'목표를 다시 알아볼 수 있어야 합니다.','we must be able to recognize the target again.'),
 (2,'다음 예고편의 서로 다른 장면에서,','In the next trailer’s separate excerpts,'),
 (2,'벽과 바닥이 목표를 찾는 어떤 단서가 되는지 보겠습니다.','we will examine how walls and floors help us recognize a target.')]
}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def wrap(text,limit):
    measure=lambda s:float(font.getlength(s))
    if measure(text)<=min(1050,limit):return [text],math.ceil(measure(text))+44
    words=text.split();options=[]
    for i in range(1,len(words)):
        lines=[' '.join(words[:i]),' '.join(words[i:])];widths=list(map(measure,lines))
        if max(widths)<=limit:options.append((abs(widths[0]-widths[1])-(65 if lines[0].endswith(',') else 0),lines,widths))
    assert options,('Editorial split needed',text,limit)
    _,lines,widths=min(options,key=lambda v:v[0]);return lines,math.ceil(max(widths))+44
for sid,g in groups.items():
    result=read(R/f'current-mixed-whole-asr-v1/{sid}.json');words=result['words']
    recognized=''.join(norm(w['text']) for w in words)
    expected=''.join(norm(t[1]) for t in g)
    assert recognized==expected,('New cue groups differ from directly read whole',sid)
    charwords=[]
    for w in words:charwords.extend([w]*len(norm(w['text'])))
    offset=0
    for paragraph,text,en in g:
        endoffset=offset+len(norm(text));first,last=charwords[offset],charwords[endoffset-1]
        start=max(0,first['timestamp'][0]-.3)+current[sid]['start']
        end=min(current[sid]['voiceSeconds'],last['timestamp'][1]-.3)+current[sid]['start']
        assert end-start>2/60
        limit=900 if any(c['sourceId']=='PF5L_2g9UVQ' and start<c['timelineEnd'] and end>c['timelineStart'] for c in plan['cuts']) else 1570
        lines,width=wrap(text,limit)
        rows.append(dict(scene=sid,paragraph=paragraph,start=start,end=end,ko=text,en=en,
          lines=lines,boxWidth=width,newCue=True,wrapMeasurement='Actual Windows Malgun48 TTF advance via Pillow; final ASS pixels remain mandatory',
          currentWholeResultSha256=sha(R/f'current-mixed-whole-asr-v1/{sid}.json')))
        offset=endoffset
assert len(rows)==179
rows.sort(key=lambda c:c['start'])
def timestamp(t,ass=False):
    b=100 if ass else 1000;n=round(t*b)
    return f'{n//(b*3600):0{1 if ass else 2}d}:{n//(b*60)%60:02d}:{n//b%60:02d}{"." if ass else ","}{n%b:0{2 if ass else 3}d}'
ass=(base/'captions.ko.ass').read_text('utf-8-sig').split('[Events]')[0]+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
placements=[];errors=[]
for i,c in enumerate(rows,1):
    c['id']=i;start,end=c['start'],c['end'];assert start>=2 and end<=plan['bodyEnd']
    if i>1:assert start>=rows[i-2]['end']-.001
    w=c['boxWidth'];height=len(c['lines'])*62+22;x=round(960-w/2);y=round(970-height/2)
    bounds=sorted(set([round(t*100)/100 for t in [start,end]+[t for k in plan['cuts'] for t in [k['timelineStart'],k['timelineEnd']] if start+.001<t<end-.001]]))
    for a,b in zip(bounds,bounds[1:]):
        if b<=a:continue
        cut=next((k for k in plan['cuts'] if k['timelineStart']<=(a+b)/2<k['timelineEnd']),None)
        protected=[[27,969,475,1058],[1818,849,1900,1078]] if cut and cut['sourceId']=='PF5L_2g9UVQ' else ([] if cut else [[100,240,1820,883]])
        overlap=any(x<r[2] and x+w+14>r[0] and y<r[3] and y+height+14>r[1] for r in protected)
        if len(c['lines'])>2 or w>1614 or x<2 or x+w+16>1920 or y+height+16>1080 or overlap:errors.append(dict(cue=i,start=a,end=b,overlap=overlap))
        def event(layer,text):
            global ass
            ass+=f'Dialogue: {layer},{timestamp(a,True)},{timestamp(b,True)},Default,,0,0,0,,{text}\n'
        def box(xx,yy,color,border):return '{\\an7\\pos('+f'{xx},{yy}'+')\\p1\\bord'+str(border)+'\\shad0\\1c&H'+color+'&\\3c&H181B16&}m 0 0 l '+f'{w} 0 {w} {height} 0 {height}'
        event(0,box(x+14,y+14,'323C07',0));event(1,box(x,y,'FFFFFF',3))
        for n,line in enumerate(c['lines']):event(2,'{\\an5\\pos('+f'960,{y+42+n*62}'+')\\bord0\\shad0}'+line.replace('{','').replace('}',''))
        placements.append(dict(cue=i,start=a,end=b,scene=c['scene'],cut=cut['id'] if cut else None,
          lines=c['lines'],width=w,height=height,x=x,y=y,centerX=960,centerY=970,shadowBottom=y+height+14,
          protectedRegions=protected,overlap=overlap,finalCuePixelsReviewed=False))
assert not errors,errors
for lang in ['ko','en']:
    (R/f'captions.{lang}.srt').write_text('\n\n'.join(f'{c["id"]}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n'+('\n'.join(c['lines']) if lang=='ko' else c['en']) for c in rows)+'\n','utf-8')
(R/'captions.ko.ass').write_text(ass,'utf-8')
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
write(R/'caption-alignment-v1.json',dict(entries=rows,current14ScenesRetimedTogether=True,
  retainedCueCount=166,newCueCount=13,paragraphCount=66,originalCueTextsAndWrapsPreserved=True,
  mixAacSha256=mix['mixAacSha256'],planSha256=sha(R/'measured-additive-plan-v1.json')))
write(R/'caption-layout-v1.json',dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),
  style='boxed-white-forest-v1',font='Malgun Gothic',fontSize=48,allCuesMeasured=True,unresolvedLayoutErrors=errors,
  cueCount=len(rows),segmentCount=len(placements),cues=placements,
  ass=(R/'captions.ko.ass').relative_to(ROOT).as_posix(),assSha256=sha(R/'captions.ko.ass'),
  allFinalCuePixelsReviewed=False,humanListeningApproved=False))
write(R/'measured-chapters-v1.json',dict(chapters=[dict(scene=s['id'],title=s['title'],start=s['start'],startFrame=s['startFrame']) for s in plan['scenes']],
  intro=dict(startFrame=0,frames=120),membershipEnding=dict(startFrame=plan['totalFrames']-600,start=plan['bodyEnd'],frames=600,end=plan['seconds']),
  source='Actual measured14 PCM placement/plan; platform chapter consolidation pending',mixAacSha256=mix['mixAacSha256'],savedOnPlatform=False))
print(json.dumps(dict(cues=179,retained=166,new=13,allCuesMeasured=True,finalPixelReview=False)))
