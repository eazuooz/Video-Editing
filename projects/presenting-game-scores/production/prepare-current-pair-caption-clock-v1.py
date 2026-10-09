"""Prepare the exact reviewed full-video caption clock; render remains gated."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(W/'plan.json');cap=read(W/'captions.json');review=read(ROOT/p['selectedInputReview'])
assert sha(ROOT/p['selectedInputReview'])==p['selectedInputReviewSha256'] and review['allInputCaptionPixelsReviewed']
assert cap['allCurrentCueTextsDirectlyRead'] and cap['allInputCuePixelsReviewed']
assert (cap['koCueCount'],cap['enCueCount'])==(168,68)
assert not (W/'caption-clock-adoption.json').exists(),'Preserve the current clock; never repeat preparation.'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def stamp(t):
 n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
lines=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','WrapStyle: 2','ScaledBorderAndShadow: yes','','[V4+ Styles]',
 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
 'Style: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1','','[Events]',
 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
for c in cap['ko']:
 assert len(c['lines'])==1 and c['center']==[960,970]
 text=c['ko'];assert not any(a in text for a in '{}\\')
 width=math.ceil(font.getlength(text))+44;height=84;x=960-width/2;y=928
 assert width<=1570 and 2<=c['startSeconds']<c['endSeconds']<=18452/60+.001
 a,b=stamp(c['startSeconds']),stamp(c['endSeconds']);prefix=lambda layer:f'Dialogue: {layer},{a},{b},Default,,0,0,0,,'
 shape=f'm 0 0 l {width} 0 {width} {height} 0 {height}'
 lines.extend([prefix(0)+f'{{\\an7\\pos({x+14:g},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}'+shape,
  prefix(1)+f'{{\\an7\\pos({x:g},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+shape,
  prefix(2)+'{\\an5\\pos(960,970)\\bord0\\shad0}'+text])
ass=W/'captions.ko.ass';ass.write_text('\n'.join(lines)+'\n','utf-8')
clock=dict(preparedAt=datetime.now(timezone.utc).isoformat(),planSha256=sha(W/'plan.json'),captionJsonSha256=sha(W/'captions.json'),
 finalAssSha256=sha(ass),koSrtSha256=sha(W/'presenting-game-scores.ko.srt'),enSrtSha256=sha(W/'presenting-game-scores.en.srt'),
 koCueCount=168,enCueCount=68,captionCenter=[960,970],fontPx=48,koMaxLines=1,enMaxLines=2,
 style='boxed-white-forest-v1',clockIncludesOriginalTwoSecondIntro=True,inputCuePixelsReviewed=True,
 allFinalPixels=False,pairRendered=False,finalMixedAsrApproved=False,preparedOnly=True,imagesCreated=0)
(W/'caption-clock-adoption.json').write_text(json.dumps(clock,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(ko=168,en=68,assPrepared=True,pairRendered=False,allFinalPixels=False)))
