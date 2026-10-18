"""Current aligned SRT -> measured fixed white box captions, without speech edits."""
from pathlib import Path
import json,re,hashlib
from PIL import ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v2'
FONT=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(s,ass=False):
 scale=100 if ass else 1000;t=round(s*scale);h,t=divmod(t,3600*scale);m,t=divmod(t,60*scale);sec,ms=divmod(t,scale)
 return f'{h}:{m:02}:{sec:02}.{ms:02}' if ass else f'{h:02}:{m:02}:{sec:02},{ms:03}'
def seconds(t):
 h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
def wrap(t):
 if FONT.getlength(t)<=1570:return [t]
 words=t.split();choices=[([' '.join(words[:i]),' '.join(words[i:])]) for i in range(1,len(words))]
 choices=[ls for ls in choices if max(FONT.getlength(s) for s in ls)<=1570]
 assert choices,('Split aligned caption at a speech boundary; do not shrink it',t)
 return min(choices,key=lambda ls:abs(FONT.getlength(ls[0])-FONT.getlength(ls[1])))
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Text,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Box,Malgun Gothic,48,&H00FFFFFF,&H00FFFFFF,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def rectangle(x,y,w,h):return f'm {x:.2f} {y:.2f} l {x+w:.2f} {y:.2f} {x+w:.2f} {y+h:.2f} {x:.2f} {y+h:.2f}'
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 plan=read(P/'production/revision-v2/timeline.json');events=[];rows=[]
 assert plan.get('timing')=='measured-and-asr-aligned' and plan['fps']==60
 for path,digest in plan['inputHashes'].items():assert sha(R/path)==digest,('Stale timeline input',path)
 paired={}
 # Timeline builder writes final, branding-shifted SRTs. Never add2s twice.
 for lang in ['ko','en']:
  src=O/f'captions.{lang}.srt';assert src.exists(),src
  previous=0;paired[lang]=[]
  for block in src.read_text(encoding='utf8').strip().split('\n\n'):
   lines=block.splitlines();a,b=map(seconds,lines[1].split(' --> '));assert b>a and a>=previous-.002;previous=b
   paired[lang].append((a,b));expected=plan[lang+'Captions'][len(paired[lang])-1]
   assert abs(a-expected['start'])<=.001 and abs(b-expected['end'])<=.001,('Caption timeline mismatch or duplicate branding shift',lang,lines[0])
   assert ' '.join(' '.join(lines[2:]).split())==' '.join(expected['text'].split()),('Caption text changed after measured plan',lang,lines[0])
   assert a>=2-.001 and b<=(plan['totalFrames']-600)/60+.001,'Captions must remain between branding and member outro'
   if lang!='ko':continue
   ls=wrap(' '.join(lines[2:]));width=max(FONT.getlength(s) for s in ls)+44;height=len(ls)*62+22;x=960-width/2;y=970-height/2
   assert x>=150 and y>=880 and y+height+14<=1060
   when=f'{stamp(a,True)},{stamp(b,True)}'
   events.append(f'Dialogue: 10,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\bord0\\1c&H323C07&\\p1}}'+rectangle(x+14,y+14,width,height))
   events.append(f'Dialogue: 11,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\p1}}'+rectangle(x,y,width,height))
   for j,t in enumerate(ls):events.append(f'Dialogue: 12,{when},Text,,0,0,0,,{{\\an5\\pos(960,{970+(j-(len(ls)-1)/2)*62:.2f})}}'+t.replace('{','').replace('}',''))
   rows.append(dict(cue=int(lines[0]),start=a,end=b,text='\n'.join(ls),measuredTextWidths=[FONT.getlength(s) for s in ls],box=[x,y,width,height],center=[960,970],font=48))
 assert len(paired['ko'])==len(plan['koCaptions'])==len(paired['en'])==len(plan['enCaptions'])
 assert paired['ko']==paired['en'],'KO/EN final boundaries differ'
 (O/'captions.ko.ass').write_text(HEADER+'\n'.join(events)+'\n',encoding='utf8')
 (O/'caption-layout.json').write_text(json.dumps(dict(style='boxed-white-forest-v1',rows=rows,textWidthMaximum=1570,fontFile='C:/Windows/Fonts/malgun.ttf',koSrtSha256=sha(O/'captions.ko.srt'),enSrtSha256=sha(O/'captions.en.srt'),timelineSha256=sha(P/'production/revision-v2/timeline.json'),fixedAnchor=[960,970],pixelReview='pending'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(captionCount=len(rows),maximumWidth=max(max(c['measuredTextWidths']) for c in rows))))
if __name__=='__main__':main()
