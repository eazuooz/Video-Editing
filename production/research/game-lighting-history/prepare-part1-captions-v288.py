"""Measure fixed caption boxes; export text tracks. No encoded pixel approval."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import ImageFont
import json,math,hashlib,re
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v288.json';plan=json.loads(PP.read_text('utf8'))
OUT=ROOT/'production/research/game-lighting-history/local/part1-captions-v288';assert not OUT.exists();OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fontpath=Path('C:/Windows/Fonts/malgun.ttf');font=ImageFont.truetype(str(fontpath),48)
def ass_time(frame):
 cs=round(frame*100/60);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def srt_time(frame):
 ms=round(frame*1000/60);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
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
for c in plan['koCues']:
 lines=c['text'].split('\n');assert len(lines)<=2 and not any(x in c['text'] for x in ['{','}','\\'])
 widths=[font.getlength(line) for line in lines];w=math.ceil(max(widths)+44);h=len(lines)*62+22
 assert w<=1570,(c['id'],w,c['text'])
 x=math.floor(960-w/2);y=970-h/2;start,end=ass_time(c['fromFrame']),ass_time(c['toFrame']);assert start!=end
 def event(layer,t):events.append(f'Dialogue: {layer},{start},{end},Default,,0,0,0,,{t}')
 rectangle=f'm 0 0 l {w} 0 {w} {h} 0 {h}'
 event(0,f'{{\\an7\\pos({x+14},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&\\3c&H181B16&}}'+rectangle)
 event(1,f'{{\\an7\\pos({x},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+rectangle)
 for i,line in enumerate(lines):event(2,f'{{\\an5\\pos(960,{970-(len(lines)-1)*31+i*62})\\bord0\\shad0}}'+line)
 af=math.ceil(round(c['fromFrame']*100/60)/100*60-1e-7);az=math.ceil(round(c['toFrame']*100/60)/100*60-1e-7)
 assert abs(af-c['fromFrame'])<=1 and abs(az-c['toFrame'])<=1
 metrics.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'fromFrame':c['fromFrame'],'toFrame':c['toFrame'],'widths':widths,'box':{'x':x,'y':y,'width':w,'height':h,'center':[960,970],'border':3,'shadow':[14,14]},'assTime':[start,end],'assFirstFrame':af,'assExclusiveEndFrame':az,'encodedPixelsReviewed':False})
ass=OUT/'captions.ko.ass';ass.write_text(header+'\n'.join(events)+'\n','utf8')
tracks=[]
for lang in ['ko','en']:
 cues=plan[lang+'Cues'];file=OUT/('game-lighting-history-04-1.'+lang+'.srt')
 file.write_text('\n\n'.join(str(i+1)+'\n'+srt_time(c['fromFrame'])+' --> '+srt_time(c['toFrame'])+'\n'+c['text'] for i,c in enumerate(cues))+'\n','utf8')
 for p in plan['paragraphs']:
  related=[c for c in cues if c['entryId']==p['id']]
  norm=lambda t:re.sub(r'\s+','',t)
  assert norm(''.join(c['text'] for c in related))==norm(p[lang]),(lang,p['id'])
 tracks.append({'language':lang,'path':file.relative_to(ROOT).as_posix(),'sha256':sha(file),'cueCount':len(cues),'all77ParagraphTextsPreserved':True,'englishTimingsMeasured':False if lang=='en' else None})
proof={'preparedAt':datetime.now(timezone.utc).isoformat(),'planSha256':sha(PP),'font':{'path':str(fontpath),'sha256':sha(fontpath),'size':48},'ass':{'path':ass.relative_to(ROOT).as_posix(),'sha256':sha(ass)},'cueCount':len(metrics),'maximumBoxWidth':max(c['box']['width'] for c in metrics),'captionStyle':'boxed-white-forest-v1','center':[960,970],'maximumLines':2,'allTextPreserved':True,'metrics':metrics,'tracks':tracks,'newImages':0,'allEncodedPixelsReviewed':False,'captionTimingApproved':False,'finalUseApproved':False}
(P/'part1-caption-layout-v288.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'cues':len(metrics),'maxWidth':proof['maximumBoxWidth'],'tracks':[t['cueCount'] for t in tracks],'approved':False}))
