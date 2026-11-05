"""Insert the sourced Actor/Pawn report into the approved newsroom cut."""
from pathlib import Path
import subprocess,sys,json,hashlib,math,shutil,os
from datetime import datetime,timezone
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
B=P/'production/local/newsroom-v3';L=P/'production/local/newsroom-v4';D=B/'sources'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,name):
 with (L/(name+'.log')).open('wb') as log:
  rc=subprocess.call(['ffmpeg','-y','-hide_banner','-nostdin',*map(str,args)],cwd=R,stdout=log,stderr=log)
 if rc:raise RuntimeError((L/(name+'.log')).read_text(encoding='utf-8',errors='replace')[-1400:])
sys.path.insert(0,str(R/'projects/animation-breaking-down-attack-animations/production/grid-v1'))
import caption_pipeline as cp
groups=[[(x.strip(),y.strip()) for x,y in (line.split(' | ') for line in block.splitlines())] for block in (H/'passages.txt').read_text('utf-8').strip().split('\n\n')]
def timing():
 old=read(B/'timeline.json');boundary=120+old['scenes'][3]['startFrame']
 assert boundary==4058
 start=boundary;extended=[];durations=[];spans=[]
 aliases={'언리얼엔진5':'언리얼엔진오','엔진파이브':'엔진오','엔진5':'엔진오','엑터':'액터','액타':'액터','버스':'verse','벌스':'verse','폰의':'폰에'}
 for i,lines in enumerate(groups,1):
  sid=f'{i:02}';wav=L/'voice/chunks'/f'{sid}-scene.wav';q=read(L/'voice/asr'/f'{sid}.json')
  dur=sf.info(wav).duration;assert q['audio_sha256']==sha(wav)
  words=[];last=0.
  for w in q['words']:
   a,b=w['timestamp'];a=max(last,a or 0.);b=min(dur,b if b is not None else dur)
   if b>a+.0001:words.append(dict(text=w['text'],timestamp=[a,b]));last=b
  text=' '.join(x for x,_ in lines);begins,ends,quality=cp.align_characters(text,words,dur,aliases,.89)
  n=math.ceil((.14+dur+.20)*60);offset=0;beats=[]
  for j,(ko,en) in enumerate(lines):
   size=len(cp.normalized(ko,aliases));a=round(start/60+.14+begins[offset],2);b=round(start/60+.14+ends[offset+size-1],2);offset+=size
   display=ko.replace('엔진 5','엔진 5').replace('버스로','Verse로')
   extended.append(dict(start=a,end=b,ko=display,en=en,scene='03.'+sid));beats.append(round(a*60)-start)
  spans.append({'id':sid,'frames':n,'start':start,'beats':[0]+beats[1:],'coverage':quality['matchingCharacterCoverage']})
  durations.append(n);start+=n
 added=sum(durations);cues=read(B/'cue-review.json')
 assert not any(c['start']<boundary/60<c['end'] for c in cues)
 cues=[dict(c,start=round(c['start']+(added/60 if c['start']>=boundary/60 else 0),2),end=round(c['end']+(added/60 if c['start']>=boundary/60 else 0),2)) for c in cues]+extended
 cues.sort(key=lambda c:c['start'])
 font=cp.measured_font(Path('C:/Windows/Fonts/malgun.ttf'),500);bold=cp.measured_font(Path('C:/Windows/Fonts/malgunbd.ttf'),700)
 for i,c in enumerate(cues):
  assert i==0 or c['start']>=cues[i-1]['end']-.001
  for lang in ['ko','en']:
   if c['scene'].startswith('03.'):
    parts=cp.wrap(c[lang],font);assert parts,(lang,c);c[lang]='\n'.join(parts)
  c['cue']=i+1;c['emphasis']={'ko':None,'en':None}
 for lang in ['ko','en']:
  (L/f'captions.{lang}.srt').write_text(''.join(f"{c['cue']}\n{cp.srt_stamp(c['start'])} --> {cp.srt_stamp(c['end'])}\n{c[lang]}\n\n" for c in cues),encoding='utf-8')
 old_events=(B/'captions.ko.ass').read_text('utf-8').splitlines()
 def sec(timestamp):
  h,m,s=timestamp.split(':');return 3600*int(h)+60*int(m)+float(s)
 def stamp(s):
  n=round(100*s);return f'{n//360000}:{(n//6000)%60:02}:{(n//100)%60:02}.{n%100:02}'
 revised=[]
 for line in old_events:
  if line.startswith('Dialogue:'):
   cols=line.split(',',9)
   if sec(cols[1])>=boundary/60-.01:
    cols[1]=stamp(sec(cols[1])+added/60);cols[2]=stamp(sec(cols[2])+added/60);line=','.join(cols)
  revised.append(line)
 for c in extended:
  # extended and cues contain the same newly timed row objects.
  revised.append(cp.ass_events(c,cp.geometry(c['ko'],font,bold,None),'ko').strip())
 (L/'captions.ko.ass').write_text('\n'.join(revised)+'\n',encoding='utf-8')
 save(L/'cue-review.json',cues)
 plan={'boundary':boundary,'totalFrames':old['totalFrames']+added,'originalTotalFrames':old['totalFrames'],'extra':spans,'addedFrames':added}
 save(L/'timeline.json',plan);print(plan,flush=True)
 return plan
def audio(plan):
 src,rate=sf.read(B/'final-mix.wav',dtype='float32');music,mr=sf.read(B/'music-stem.wav',dtype='float32');assert rate==mr==48000
 a=plan['boundary']*800;n=plan['addedFrames']*800;vo=np.zeros((n,2),np.float32)
 for s in plan['extra']:
  wav=L/'voice/chunks'/(s['id']+'-scene.wav');out=L/('voice-'+s['id']+'.wav')
  run(['-i',wav,'-af','acompressor=threshold=0.2:ratio=4:attack=2:release=80:makeup=1,pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-2.6:LRA=9','-ar',rate,'-c:a','pcm_s24le',out],'voice-normalize-'+s['id'])
  samples,r=sf.read(out,dtype='float32');k=(s['start']-plan['boundary'])*800+round(.14*rate);vo[k:k+len(samples)]=samples
 x=np.linspace(0,1,n)[:,None];w=np.clip((x-.35)/.30,0.,1.);bed=.6*(music[a:a+n]*(1-w)+music[a-n:a]*w);insert=vo+bed
 b=round(.03*rate);w=np.linspace(1.,0.,b)[:,None];insert[:b]=src[a:a+b]*w+insert[:b]*(1-w);insert[-b:]=insert[-b:]*w+src[a-b:a]*(1-w)
 dest=np.concatenate([src[:a],insert,src[a:]],axis=0)[:plan['totalFrames']*800];assert len(dest)==plan['totalFrames']*800
 sf.write(L/'final-mix.wav',dest,rate,subtype='PCM_24')
 run(['-i',L/'final-mix.wav','-ar',48000,'-ac',2,'-c:a','aac','-b:a','192k',L/'audio.m4a'],'aac')
def card(n):
 # Evidence labels occupy the upper-left corner of the real editor recording.
 labels=[
 ('UE5 · 화면 속 캐릭터','레벨에 놓인 오브젝트를 따라가 보자'),
 ('Actor  /  액터','레벨에 배치할 수 있는 게임 오브젝트'),
 ('Pawn  /  폰','플레이어나 AI가 조종할 수 있는 액터'),
 ('Character  /  캐릭터','액터  →  폰  →  캐릭터'),
 ('Controller  /  컨트롤러','폰을 조종하는 쪽'),
 ('조종 대상 바꾸기','컨트롤러 하나  ·  사람 폰  →  자동차 폰'),
 ('도쿄 발표에서 지목한 구조','액터  ·  블루프린트  ·  C++ 게임플레이 프레임워크'),
 ('기존 프로젝트에 미치는 영향','액터를 상속하는 폰의 조종 코드도 전환 대상'),
 ('폰을 대신할 클래스는?','도쿄 현장 보도에 일대일 대응 명칭 없음'),
 ('Scene Graph  /  씬 그래프','엔티티에 컴포넌트를 붙이고 Verse로 행동 작성')]
 top,bottom=labels[n];im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
 f=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',42);body=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',36)
 width=min(1810,math.ceil(max(d.textlength(top,font=f),d.textlength(bottom,font=body)))+62)
 d.rounded_rectangle((45,47,45+width,182),radius=14,fill=(12,22,21,238))
 d.text((73,62),top,font=f,fill='#f7d884');d.text((73,125),bottom,font=body,fill='white',anchor='lt')
 file=L/f'mark-{n:02}.png';im.save(file);return file
enc=['-r','60','-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0','-g','120','-bf','0','-pix_fmt','yuv420p','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
def picture(plan):
 base=B/'delivery/output'/P.name/(P.name+'.clean.mp4')
 shots=[('bp-preview',2),('bp-work',150),('bp-preview',7),('bp-work',165),('possess',0),('possess',0),('chicago',90),('bp-preview',23),('chicago',355),('graph',714)]
 parts=[];ledger=[]
 def trim(name,file,at,n,overlay=None):
  target=L/(name+'.mp4');args=['-ss',at,'-threads','3','-i',file]
  if overlay:args+=['-i',overlay,'-filter_complex_threads','2','-filter_complex','[0:v]fps=60,setsar=1[a];[a][1:v]overlay=0:0:format=auto,format=yuv420p[out]','-map','[out]']
  else:args+=['-map','0:v','-vf','fps=60,setsar=1']
  run([*args,'-an','-frames:v',n,*enc,target],name)
  count=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','default=nw=1:nk=1',target]))
  assert count==n,(name,count,n);parts.append(target)
 trim('original-before',base,0,plan['boundary']);i=0
 for span in plan['extra']:
  points=span['beats']+[span['frames']]
  for a,b in zip(points,points[1:]):
   source,point=shots[i];overlay=card(i)
   if source=='possess':
    sheet=Image.new('RGB',(1920,1080),'#17211e');dg=ImageDraw.Draw(sheet)
    doc=Image.open(L/'possess.png').convert('RGB');doc.thumbnail((1120,650))
    sheet.paste(doc,((1920-doc.width)//2,209));dg.text((55,842),'에픽 문서 예시 · UE4.27   /   한 컨트롤러가 서로 다른 캐릭터 폰을 선택',font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',32),fill='#e5ebdf')
    sheet.paste(Image.open(overlay),(0,0),Image.open(overlay).getchannel('A'));png=L/('doc-'+str(i)+'.png');sheet.save(png)
    target=L/('new-'+str(i)+'.mp4');run(['-loop','1','-framerate',60,'-i',png,'-an','-frames:v',b-a,*enc,target],'doc-'+str(i));parts.append(target)
   else:trim('new-'+str(i),D/(source+'.mp4'),point,b-a,overlay)
   ledger.append({'source':source,'sourceStart':point,'frames':b-a,'frame':span['start']+a});i+=1
 trim('original-after',base,plan['boundary']/60,plan['originalTotalFrames']-plan['boundary'])
 (L/'parts.txt').write_text(''.join("file '"+f.name+"'\n" for f in parts),encoding='ascii')
 run(['-f','concat','-safe','0','-i',L/'parts.txt','-c','copy',L/'picture.mp4'],'picture')
 args=['-filter_complex_threads','2','-threads','4','-i',L/'picture.mp4','-i',L/'audio.m4a','-filter_complex','[0:v]settb=1/60,setpts=N,split=2[c][in];[in]ass='+rel(L/'captions.ko.ass')+'[b]']
 for tag,name in [('c','clean'),('b','captioned')]:args+=['-map','['+tag+']','-map','1:a','-frames:v',plan['totalFrames'],'-t',plan['totalFrames']/60,*enc,'-c:a','copy','-movflags','+faststart',L/(name+'.mp4')]
 run(args,'pair');save(H/'added-cut-ledger.json',ledger)
if __name__=='__main__':
 plan=timing();audio(plan);picture(plan)
 sys.path.insert(0,str(P/'production'))
 import finish
 finish.L=L;finish.verify(plan)
