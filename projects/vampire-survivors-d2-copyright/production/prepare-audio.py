"""One continuous own-voice take; one hash-cached complete ASR per audio input."""
from pathlib import Path
import sys,json,hashlib,subprocess,difflib,re,math
import numpy as np
import soundfile as sf
from PIL import ImageFont
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/'production/local'
sys.path.insert(0,str(R/'qwen3-tts'))
from align_project_subtitles import align_characters,normalized,partition_fixed
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):subprocess.run(a,check=True)
def guard():
 c=rd(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def recognize(raw,cache):
 digest=sha(raw)
 if cache.exists() and rd(cache).get('audio_sha256')==digest:return rd(cache)
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(4);local=R/'qwen3-tts/models/whisper-large-v3-turbo'
 m=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float32,attn_implementation='eager',local_files_only=True)
 p=AutoProcessor.from_pretrained(str(local),local_files_only=True)
 asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
 print('Complete CPU ASR, no expected-text prompt:',raw,flush=True)
 q=asr(str(raw),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 v={'audio_sha256':digest,'text':q['text'],'words':q['chunks'],'scope':'whole current audio, one recognition pass, no expected prompt','device':'cpu','humanListening':'pending'};wr(cache,v);return v
def compare(q,name):
 expected=' '.join(x for s in rd(P/'script/narration.spoken-ko.json')['scenes'] for x in s['lines'])
 a,b=normalized(expected),normalized(q['text']);m=difflib.SequenceMatcher(None,a,b,autojunk=False)
 wr(L/(name+'-comparison.json'),{'expected':expected,'recognized':q['text'],'similarity':m.ratio(),'differences':[{'kind':op,'expected':a[i:j],'recognized':b[k:l]} for op,i,j,k,l in m.get_opcodes() if op!='equal'],'directReview':'pending'})
def stamp(t,ass=False):
 u=100 if ass else 1000;v=round(t*u);h,v=divmod(v,3600*u);m,v=divmod(v,60*u);s,v=divmod(v,u)
 return f'{h}:{m:02}:{s:02}.{v:02}' if ass else f'{h:02}:{m:02}:{s:02},{v:03}'
font=ImageFont.truetype('C:/Windows/Fonts/NotoSansKR-VF.ttf',48);font.set_variation_by_axes([500])
def wrap(s):
 lines=[];line=''
 for w in s.split():
  new=(line+' '+w).strip()
  if line and font.getlength(new)>1570:lines.append(line);line=w
  else:line=new
 if line:lines.append(line)
 return lines
def pieces(s):
 # Prefer sentence/clause boundaries. Long clauses are split at a complete word.
 out=[]
 for part in re.split(r'(?<=[.!?])\s+|(?<=,)\s+',s):
  words=part.split();temp=[]
  for w in words:
   if temp and (len(temp)>=10 or font.getlength(' '.join(temp+[w]))>1500):out.append(' '.join(temp));temp=[]
   temp.append(w)
  if temp:out.append(' '.join(temp))
 return out
def align():
 spoken=rd(P/'script/narration.spoken-ko.json');ko=rd(P/'script/narration.ko.json');en=rd(P/'script/narration.en.json')
 raw=L/'narration-source.wav';a,sr=sf.read(raw,dtype='float32');duration=len(a)/sr;q=rd(L/'whole-source-asr.json');assert q['audio_sha256']==sha(raw)
 expected=' '.join(x for s in spoken['scenes'] for x in s['lines']);starts,ends,coverage=align_characters(expected,q['words'],duration)
 cursor=0;paras=[];cues=[];scene_rows=[]
 for sk,ss,se in zip(ko['scenes'],spoken['scenes'],en['scenes']):
  scene_start=len(paras)
  for k,s,e in zip(sk['lines'],ss['lines'],se['lines']):
   n=len(normalized(s));begin=float(starts[cursor]);end=float(ends[cursor+n-1]);chunks=pieces(k)
   # The displayed aliases have different character counts; align display locally
   # to this paragraph's actual ASR window, retaining every display word.
   localwords=[dict(w,timestamp=[max(begin,w['timestamp'][0] or begin),min(end,w['timestamp'][1] or end)]) for w in q['words'] if (w['timestamp'][1] or 0)>begin and (w['timestamp'][0] or 0)<end]
   try:cs,ce,_=align_characters(k,localwords,duration)
   except ValueError:
    # Only display D2/year aliases differ. Map via equal characters plus monotonic interpolation.
    ak,bk=normalized(k),normalized(s);m=difflib.SequenceMatcher(None,ak,bk,autojunk=False);x=[];ys=[];ye=[]
    for block in m.get_matching_blocks():
     for d in range(block.size):x.append(block.a+d);ys.append(starts[cursor+block.b+d]);ye.append(ends[cursor+block.b+d])
    cs=np.interp(np.arange(len(ak)),x,ys);ce=np.interp(np.arange(len(ak)),x,ye)
   ec=partition_fixed(e,70,len(chunks));off=0;indices=[]
   for kk,ee in zip(chunks,ec):
    count=len(normalized(kk));lo=max(begin,float(cs[off]));hi=min(end,float(ce[off+count-1]));off+=count
    if cues:lo=max(lo,cues[-1]['end'])
    assert hi>lo,(kk,lo,hi)
    lines=wrap(kk);assert len(lines)<=2
    emph=None
    for term,role in [('이용허락','concept'),('구체적인 표현','concept'),('저작권 침해','caution'),('자동으로 허용','caution'),('성장 체감','result'),('무료','concept')]:
     if term in kk:emph={'text':term,'role':role};break
    cues.append({'index':len(cues)+1,'scene':sk['id'],'paragraph':len(paras)+1,'start':lo,'end':hi,'ko':kk,'en':ee,'lines':lines,'emphasis':emph});indices.append(len(cues))
   assert off==len(normalized(k))
   paras.append({'index':len(paras)+1,'scene':sk['id'],'start':begin,'end':end,'ko':k,'en':e,'cues':indices})
   cursor+=n
  scene_rows.append({'id':sk['id'],'title':sk['title'],'start':paras[scene_start]['start'],'end':paras[-1]['end'],'paragraphs':[p['index'] for p in paras[scene_start:]]})
 body_frames=math.ceil(duration*60);actual_frames=round(body_frames*.6)
 wr(L/'timing.json',{'sourceSha256':sha(raw),'continuousSpeech':True,'timeStretch':False,'duration':duration,'bodyFrames':body_frames,'actualFrames':actual_frames,'explanationFrames':body_frames-actual_frames,'coverage':coverage,'scenes':scene_rows,'paragraphs':paras,'cues':cues})
 for lang in ['ko','en']:
  (L/f'final.{lang}.srt').write_text('\n\n'.join(f"{c['index']}\n{stamp(c['start']+2)} --> {stamp(c['end']+2)}\n{c[lang]}" for c in cues)+'\n',encoding='utf8')
 head='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Noto Sans KR,48,&H00090B08,&H00090B08,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 events=[]
 def event(layer,a,z,text):events.append(f'Dialogue: {layer},{stamp(a,True)},{stamp(z,True)},Default,,0,0,0,,{text}')
 for c in cues:
  a,z=c['start']+2,c['end']+2;lines=c['lines'];w=max(font.getlength(x) for x in lines)+44;h=62*len(lines)+22;x=960-w/2;y=970-h/2
  poly=f'm 0 0 l {w:.2f} 0 {w:.2f} {h:.2f} 0 {h:.2f}'
  event(0,a,z,f'{{\\an7\\pos({x+14:.2f},{y+14:.2f})\\p1\\c&H323C07&}}{poly}')
  event(1,a,z,f'{{\\an7\\pos({x:.2f},{y:.2f})\\p1\\c&HFFFFFF&\\bord3\\3c&H181B16&}}{poly}')
  for i,line in enumerate(lines):
   label=line
   if c['emphasis'] and c['emphasis']['text'] in label:
    color={'concept':'666B0B','result':'377F1A','caution':'1823B4'}[c['emphasis']['role']];term=c['emphasis']['text'];label=label.replace(term,f'{{\\c&H{color}&\\b700}}{term}{{\\c&H090B08&\\b0}}')
   yy=970+(i-(len(lines)-1)/2)*62
   event(2,a,z,f'{{\\an5\\pos(960,{yy:.2f})}}{label}')
 (L/'captions.ass').write_text(head+'\n'.join(events)+'\n',encoding='utf8')
 print(json.dumps({'duration':duration,'coverage':coverage,'paragraphs':len(paras),'cues':len(cues),'frames':body_frames}),flush=True)
if __name__=='__main__':
 guard();stage=sys.argv[1]
 if stage=='recognize':
  raw=L/'narration-source.wav'
  if not raw.exists():run(['ffmpeg','-v','error','-i',str(L/'narration-elevenlabs-b.mp3'),'-ac','1','-ar','24000','-c:a','pcm_f32le',str(raw)])
  compare(recognize(raw,L/'whole-source-asr.json'),'whole-source')
 elif stage=='align':align()
 elif stage=='final-asr':
  raw=L/'final-mix-asr.wav'
  if not raw.exists():run(['ffmpeg','-v','error','-i',str(L/'final.captioned.mp4'),'-vn','-ac','1','-ar','24000','-c:a','pcm_f32le',str(raw)])
  compare(recognize(raw,L/'whole-final-mix-asr.json'),'whole-final-mix')
 else:raise ValueError(stage)
