"""Align approved script to one cached full word-ASR pass; fixed brand caption box."""
from pathlib import Path
import json,re,difflib,hashlib
import numpy as np
from PIL import ImageFont
P=Path(__file__).resolve().parents[1];L=P/'production/local/full-video-v4'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def norm(s):return ''.join(c.lower() for c in s if c.isalnum())
def tc(t,ass=False):
 n=round(t*(100 if ass else 1000));h,n=divmod(n,360000 if ass else 3600000);m,n=divmod(n,6000 if ass else 60000);s,n=divmod(n,100 if ass else 1000)
 return f'{h}:{m:02}:{s:02}.{n:02}' if ass else f'{h:02}:{m:02}:{s:02},{n:03}'
display={'챗지피티':'ChatGPT','휴머노이드':'Humanoid','케이킷':'KayKit','홀리즈나 씨씨제로':'HoliznaCC0','트리포':'Tripo','메쉬':'Meshy','컴피유아이':'ComfyUI','혼위안 쓰리디':'Hunyuan3D','블록벤치':'Blockbench','머티리얼 메이커':'Material Maker','믹사모':'Mixamo','딥모션':'DeepMotion','코덱스':'Codex','유니티':'Unity','에이치 삼 점 일':'H3.1','아이케이':'IK','엠씨피':'MCP','씨엘아이':'CLI','피비알':'PBR','제이슨':'JSON','피시':'PC','로파이':'LOFI','유알피':'URP','에프비엑스':'FBX','리토포':'Retopo','로컬스토리지':'localStorage'}
def shown(s):
 for a,b in sorted(display.items(),key=lambda x:-len(x[0])):s=s.replace(a,b)
 return s
def asr_spelling(s):
 for a,b in sorted(display.items(),key=lambda x:-len(x[1])):s=re.sub(re.escape(b),a,s,flags=re.I)
 return s
def parts(s,limit=29):
 spans=[];a=0
 for m in re.finditer(r'[고며서면데],\s+',s):
  if m.end()-a>=12:spans.append((a,m.end()));a=m.end()
 if a<len(s):spans.append((a,len(s)))
 out=[]
 for a,b in spans:
  start=a;last=a;local=[]
  for w in re.finditer(r'\S+',s[a:b]):
   ws,we=a+w.start(),a+w.end()
   if we-start>limit and last>start:local.append((start,last));start=ws
   last=we
  if last>start:local.append((start,last))
  if len(local)>1 and local[-1][1]-local[-1][0]<=8:
   if local[-1][1]-local[-2][0]<=35:local[-2:]=[(local[-2][0],local[-1][1])]
   else:
    pa,pb=local[-2];word=list(re.finditer(r'\S+',s[pa:pb]))[-1];split=pa+word.start()
    if split>pa:local[-2:]=[(pa,split),(split,local[-1][1])]
  out.extend(local)
 return out
def en_parts(s,weights):
 words=s.split();out=[];start=0;cum=np.cumsum([len(w) for w in words]);targets=np.cumsum(weights)/sum(weights)*cum[-1]
 for i in range(len(weights)):
  end=len(words) if i==len(weights)-1 else max(start+1,min(len(words)-(len(weights)-i-1),int(np.searchsorted(cum,targets[i]))+1))
  out.append(' '.join(words[start:end]));start=end
 return out
rows=json.loads((P/'script/narration.ko.json').read_text('utf-8'))['scenes'];en={r['id']:' '.join(r['lines']) for r in json.loads((P/'script/narration.en.json').read_text('utf-8'))['scenes']};tm=json.loads((L/'timeline.json').read_text());asr=json.loads((L/'qa/narration.timestamps.json').read_text('utf-8'));assert asr['audio_sha256']==sha(L/'narration-aligned.wav') and asr['timestampMode']=='word'
cues=[];review=[]
for r,t in zip(rows,tm['scenes']):
 text=' '.join(r['lines']);exp=norm(text);astr='';at=[]
 for w in asr['chunks']:
  a,b=w['timestamp']
  if a is None or b is None or b<=t['start'] or a>=t['speechEnd']:continue
  s=norm(asr_spelling(w['text']));astr+=s;at.extend(np.linspace(a,b,max(1,len(s)),endpoint=False).tolist()[:len(s)])
 seq=difflib.SequenceMatcher(None,exp,astr,autojunk=False);anchors={}
 for a,b,n in seq.get_matching_blocks():
  for j in range(n):anchors[a+j]=at[b+j]
 assert len(anchors)>5,r['id']
 xs=sorted(anchors);ys=[anchors[x] for x in xs];mapped=np.maximum.accumulate(np.clip(np.interp(np.arange(len(exp)),xs,ys),t['start'],t['speechEnd']))
 orig=[];ni=0
 for ch in text:orig.append(min(ni,len(mapped)-1));ni+=int(ch.isalnum())
 span=[]
 for s in re.finditer(r'[^.!?]+[.!?]?',text):
  if not s.group().strip():continue
  a=s.start()+len(s.group())-len(s.group().lstrip());ss=text[a:s.end()]
  span.extend((a+u,a+v) for u,v in parts(ss))
 translations=en_parts(en[r['id']],[b-a for a,b in span])
 for k,((a,b),english) in enumerate(zip(span,translations)):
  start=float(mapped[orig[a]]);end=t['speechEnd'] if k==len(span)-1 else float(mapped[orig[span[k+1][0]]]);end=max(start+.12,end)
  cues.append({'index':len(cues)+1,'scene':r['id'],'start':start,'end':end,'ko':shown(text[a:b]),'spoken':text[a:b],'en':english})
 review.append({'id':r['id'],'ratio':seq.ratio(),'expected':text,'recognized':astr,'missingSpans':[exp[a:a+n] for tag,a,b,c,d in seq.get_opcodes() if tag=='delete' for n in [b-a] if n>=8]})
for i,v in enumerate(cues[:-1]):v['end']=min(v['end'],cues[i+1]['start']);assert v['end']>v['start'],v
for lang in ('ko','en'):(L/f'captions.{lang}.srt').write_text('\n\n'.join(f"{v['index']}\n{tc(v['start'])} --> {tc(v['end'])}\n{v[lang]}" for v in cues)+'\n','utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/NotoSansKR-VF.ttf',48)
try:font.set_variation_by_name('Medium')
except ValueError:pass
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Narration,Noto Sans KR,48,&H00090B08,&H00090B08,&H00090B08,&H00090B08,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def event(layer,v,text):return f"Dialogue: {layer},{tc(v['start'],True)},{tc(v['end'],True)},Narration,,0,0,0,,{text}\n"
def vector(x,y,w,h,col):return '{\\an7\\pos(0,0)\\bord0\\shad0\\c&H'+col+'&\\p1}'+f'm {x} {y} l {x+w} {y} {x+w} {y+h} {x} {y+h}'+'{\\p0}'
for v in cues:
 w=round(font.getlength(v['ko']))+44;assert w<=1614,(v['ko'],w);h=84;x=960-w//2;y=928
 ass+=event(0,v,vector(x+14,y+14,w,h,'323C07'))
 ass+=event(1,v,vector(x-3,y-3,w+6,h+6,'181B16'))
 ass+=event(2,v,vector(x,y,w,h,'FFFFFF'))
 label=v['ko'].replace('{','').replace('}','')
 term=next((s for s in ('Tripo','Unity','PBR','Normal','Roughness','Metallic','IK','MCP','CLI','JSON') if s in label),None)
 if term:
  start=label.index(term);v['emphasis']={'start':start,'end':start+len(term),'role':'term','color':'#0b6b66'}
  label=label.replace(term,'{\\c&H666B0B&\\b700}'+term+'{\\c&H090B08&\\b500}',1)
 ass+=event(3,v,'{\\an5\\pos(960,970)\\q2\\b500}'+label)
(L/'captions.ko.ass').write_text(ass,'utf-8');(L/'captions.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2),'utf-8');(L/'alignment-review.json').write_text(json.dumps({'audioSha256':asr['audio_sha256'],'paragraphs':review,'englishTiming':'Paragraph translation divided over matching KO clause durations; human final review pending','style':'boxed-white-forest-v1'},ensure_ascii=False,indent=2),'utf-8');print('Built',len(cues),'cues; min ASR',min(v['ratio'] for v in review))
