"""Source text timed against the single cached word-ASR pass; paired translations."""
from pathlib import Path
import json,re,difflib,hashlib,math
import numpy as np
P=Path(__file__).resolve().parents[1];L=P/'production/local'
def norm(s):return ''.join(c.lower() for c in s if c.isalnum())
def stamp(t,ass=False):
 n=round(t*(100 if ass else 1000)); h,n=divmod(n,360000 if ass else 3600000);m,n=divmod(n,6000 if ass else 60000);s,n=divmod(n,100 if ass else 1000)
 return f'{h}:{m:02}:{s:02}.{n:02}' if ass else f'{h:02}:{m:02}:{s:02},{n:03}'
def sha(f):return hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
def chunks(text,limit=29):
 words=list(re.finditer(r'\S+',text));out=[];start=0;end=0
 for w in words:
  if w.end()-start>limit and end>start:out.append((start,end));start=w.start()
  end=w.end()
 if end>start:out.append((start,end))
 # Keep a short final predicate with its preceding phrase; avoid lone
 # "합니다."/"것입니다." cues after a nearly full line.
 if len(out)>1:
  a,b=out[-1];pa,pb=out[-2]
  if len(text[a:b].strip())<=7 and b-pa<=34:
   out[-2:]=[(pa,b)]
 return out
def engparts(text,n,weights):
 words=text.split();out=[];start=0;total=sum(len(w) for w in words);cum=np.cumsum([len(w) for w in words]);targets=np.cumsum(weights)/sum(weights)*total
 for i in range(n):
  end=len(words) if i==n-1 else max(start+1,min(len(words)-(n-i-1),int(np.searchsorted(cum,targets[i]))+1))
  out.append(' '.join(words[start:end]));start=end
 return out
display={'컴피유아이':'ComfyUI','일러스트리어스 엑스엘':'Illustrious XL','노벨에이아이':'NovelAI','챗지피티':'ChatGPT','로라':'LoRA','코야 에스에스':'kohya_ss','원트레이너':'OneTrainer','브이에이이':'VAE','픽셀아트 사쿠라이크 일러스트리어스':'PixelArt SakuLike ILXL','아세프라이트':'Aseprite','투디 이미지 투 모션':'2dimg2motion','스프라이트 젠':'sprite-gen','픽셀 에프엑스':'pixelfx','픽셀 오이':'PixelOE','픽셀 스내퍼':'Pixel Snapper','에이전트 스프라이트 포지':'Agent Sprite Forge','코디셀':'Codixel','픽셀볼트':'Pixelbolt','제이슨':'JSON','스프라이트 시트 디퓨전':'Sprite Sheet Diffusion','피엔지':'PNG','픽셀 퍼 유닛':'Pixels Per Unit','엠아이티':'MIT','아파치':'Apache','칠백육십팔':'768','천삼백사십사':'1344','아흔여섯':'96','백예순여덟':'168','여덟 배':'8배','열네 프레임':'14프레임','스무 장에서 쉰 장':'20~50장'}
def asr_spelling(s):
 for spoken,visible in sorted(display.items(),key=lambda x:-len(x[1])):
  if not re.search(r'\d',visible):s=re.sub(re.escape(visible),spoken,s,flags=re.I)
 nums={'768':'칠백육십팔','1344':'천삼백사십사','96':'아흔여섯','168':'백예순여덟','20':'스무','50':'쉰','14':'열네','8':'여덟','3':'세'}
 s=re.sub(r'(?<!\d)(1344|768|168|96|20|50|14|8|3)(?!\d)',lambda m:nums[m.group()],s)
 return re.sub(r'\bAI\b','에이아이',s,flags=re.I)
def shown(s):
 for a,b in sorted(display.items(),key=lambda x:-len(x[0])):s=s.replace(a,b)
 return s
def main():
 rows=json.loads((P/'script/content.json').read_text('utf-8'))['paragraphs'];en=json.loads((P/'script/english-sentences.json').read_text('utf-8'))
 timing=json.loads((L/'timeline.json').read_text('utf-8'))
 asr=json.loads((L/'qa/narration.timestamps.json').read_text('utf-8'))
 assert asr['timestampMode']=='word';assert asr['audio_sha256']==sha(L/'narration-aligned.wav')
 cues=[];review=[];sentenceMap=[]
 for row,tm in zip(rows,timing['scenes']):
  assert row['id']==tm['id'];text=row['ko'];ss=list(re.finditer(r'[^.!?]+[.!?]?',text));ss=[s for s in ss if s.group().strip()]
  assert len(ss)==len(en[row['id']]),(row['id'],len(ss),len(en[row['id']]))
  ac=[w for w in asr['chunks'] if w['timestamp'][0] is not None and w['timestamp'][1] is not None and w['timestamp'][1]>tm['start'] and w['timestamp'][0]<tm['speechEnd']]
  astr='';atimes=[]
  for w in ac:
   st,ed=w['timestamp'];n=norm(asr_spelling(w['text']));astr+=n
   atimes.extend(np.linspace(st,ed,max(1,len(n)),endpoint=False).tolist()[:len(n)])
  expected=norm(text);seq=difflib.SequenceMatcher(None,expected,astr,autojunk=False);anchors={}
  for a,b,n in seq.get_matching_blocks():
   for k in range(n):anchors[a+k]=atimes[b+k]
  if len(anchors)<2:raise ValueError('No alignment anchors '+row['id'])
  xs=np.array(sorted(anchors));ys=np.array([anchors[x] for x in xs]);mapped=np.interp(np.arange(len(expected)),xs,ys)
  mapped=np.clip(mapped,tm['start'],tm['speechEnd']);mapped=np.maximum.accumulate(mapped)
  orig=[];ni=0
  for char in text:
   orig.append(min(ni,len(mapped)-1));ni+=int(char.isalnum())
  entries=[]
  for s,english in zip(ss,en[row['id']]):
   trim=len(s.group())-len(s.group().lstrip());a=s.start()+trim;b=s.end();sentence=text[a:b];parts=chunks(sentence)
   translations=engparts(english,len(parts),[v-u for u,v in parts])
   sentenceStart=float(mapped[orig[a]]);sentenceEnd=tm['speechEnd'] if b>=len(text)-1 else float(mapped[orig[min(len(text)-1,b+1)]])
   sentenceMap.append({'id':row['id'],'text':sentence,'english':english,'start':sentenceStart,'end':sentenceEnd})
   for k,((u,v),translation) in enumerate(zip(parts,translations)):
    start=float(mapped[orig[a+u]]);end=sentenceEnd if k==len(parts)-1 else float(mapped[orig[a+parts[k+1][0]]])
    end=max(start+.15,end);entry={'index':len(cues)+1,'scene':row['id'],'start':start,'end':end,'ko':shown(sentence[u:v]),'spoken':sentence[u:v],'en':translation};cues.append(entry);entries.append(entry['index'])
  review.append({'id':row['id'],'expected':text,'recognized':' '.join(w['text'] for w in ac),'sequenceRatio':seq.ratio(),'matchedCharacters':len(anchors),'expectedCharacters':len(expected),'cues':entries,'sourceStart':tm['start'],'sourceEnd':tm['speechEnd']})
 # Preserve ordered, nonoverlapping clause cues. No subtitles over branding/outro.
 for i,cue in enumerate(cues):
  if i+1<len(cues):cue['end']=min(cue['end'],cues[i+1]['start'])
  assert cue['end']>cue['start'],cue
 for lang in ('ko','en'):
  body='\n\n'.join(f"{x['index']}\n{stamp(x['start'])} --> {stamp(x['end'])}\n{x[lang]}" for x in cues)+'\n'
  (L/f'captions.{lang}.srt').write_text(body,'utf-8')
 ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Narration,Malgun Gothic,48,&H00343F15,&H00343F15,&H00F7FEFF,&H00F7FEFF,1,0,0,0,100,100,0,0,3,12,0,5,80,80,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 for x in cues:
  text=x['ko'];term=next((v for v in ['ComfyUI','LoRA','PixelOE','Pixelbolt','pixelfx','Sprite Sheet Diffusion','Pixels Per Unit'] if v in text),None)
  if term:text=text.replace(term,'{\\c&H005479&}'+term+'{\\c&H343F15&}',1)
  ass+=f"Dialogue: 0,{stamp(x['start'],True)},{stamp(x['end'],True)},Narration,,0,0,0,,{{\\an5\\pos(960,970)}}{text}\n"
 (L/'captions.ko.ass').write_text(ass,'utf-8')
 for name,obj in [('captions.json',cues),('sentence-cues.json',sentenceMap),('alignment-review.json',{'asrSha256':sha(L/'qa/narration.timestamps.json'),'paragraphs':review,'manualReview':'pending','timing':'ASR character anchors, unmatched spans interpolated within paragraph','translations':'sentence-paired direct translation; identical KO/EN cue timings'})]:
  (L/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),'utf-8')
 print('Created',len(cues),'paired clause cues; min alignment',min(r['sequenceRatio'] for r in review))
if __name__=='__main__':main()
