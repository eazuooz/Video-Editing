from pathlib import Path
from datetime import datetime,timezone
from PIL import ImageFont
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-03/production/local/captions-v15'
plan=json.loads((BASE/'caption-plan.json').read_text('utf-8'))
out=BASE/'captions.ko.ass'
assert not out.exists(),'Preserve existing caption preparation'
fontPath=Path('C:/Windows/Fonts/malgun.ttf');font=ImageFont.truetype(str(fontPath),48)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def timestamp(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
events=[];metrics=[]
for c in plan['ko']:
 lines=c['text'].split('\n');assert len(lines)<=2 and not any(any(x in line for x in ['{','}','\\'])for line in lines)
 widths=[font.getlength(line)for line in lines];w=math.ceil(max(widths)+44);h=len(lines)*62+22
 assert w<=1570,'Split the cue; do not shrink or move it'
 x=math.floor(960-w/2);y=970-h/2
 start,end=timestamp(c['from']),timestamp(c['to']);assert start!=end
 def event(layer,text):events.append(f'Dialogue: {layer},{start},{end},Default,,0,0,0,,{text}')
 rectangle=f'm 0 0 l {w} 0 {w} {h} 0 {h}'
 event(0,f'{{\\an7\\pos({x+14},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&\\3c&H181B16&}}'+rectangle)
 event(1,f'{{\\an7\\pos({x},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+rectangle)
 for i,line in enumerate(lines):
  cy=970-(len(lines)-1)*31+i*62;event(2,f'{{\\an5\\pos(960,{cy})\\bord0\\shad0}}'+line)
 actualStart=math.ceil(round(c['from']*100)/100*60-1e-7);actualEnd=math.ceil(round(c['to']*100)/100*60-1e-7)
 assert abs(actualStart-c['firstFrame'])<=1 and abs(actualEnd-c['exclusiveEndFrame'])<=1
 metrics.append(dict(id=c['id'],text=c['text'],widths=widths,box=dict(x=x,y=y,width=w,height=h,center=[960,970],border=3,shadow=[14,14]),assTime=[start,end],assFirstFrame=actualStart,assExclusiveEndFrame=actualEnd,encodedPixelsReviewed=False))
out.write_text(header+'\n'.join(events)+'\n','utf-8')
proof=dict(preparedAt=datetime.now(timezone.utc).isoformat(),plan=dict(path=(BASE/'caption-plan.json').relative_to(ROOT).as_posix(),sha256=sha(BASE/'caption-plan.json')),font=dict(path=str(fontPath),sha256=sha(fontPath),size=48),ass=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(out)),cueCount=len(metrics),maximumBoxWidth=max(c['box']['width']for c in metrics),center=[960,970],maximumLines=2,allTextPreserved=True,metrics=metrics,newImages=0,allEncodedPixelsReviewed=False,captionTimingApproved=False,finalUseApproved=False)
(BASE/'caption-layout-measurement.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(cues=len(metrics),maxWidth=proof['maximumBoxWidth'],newImages=0,pixelsApproved=False)))
