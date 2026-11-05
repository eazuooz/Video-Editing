"""Build the two full-length M21 masters from the source-frame timeline; V4 audio is stream-copied."""
import argparse,bisect,hashlib,io,math,os,re,shutil,subprocess,time,importlib.util,sys
from pathlib import Path
from PIL import Image, ImageDraw
from native import P,R,W,B,BAKE,HERO,read,write
from optics import paint,text,GOLD,WHITE,MUT,BG
SL=P.name;DEST=R/'output'/(SL+'-render-v5');OLD=R/'output'/(SL+'-render-v4');Q=read(W.parent/'render-v4/queue.json');AL=read(Q['wordAlignment']);D=W/'edit';D.mkdir(exist_ok=True);DEST.mkdir(exist_ok=True)
def module(p):sp=importlib.util.spec_from_file_location(p.stem,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
CAP=module(R/'projects/buckshot-roulette-reverse-engineering/production/assemble_documentary.py')
def ff(*a):
 subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y',*map(str,a)],cwd=D,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def sha(f):
 with open(f,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def probe(f):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]))
import json
def caption_text(s,t):
 if s in range(8,18):
  for a,b in [('엔 닷 엘','N·L'),('엔','N'),('엘','L'),('브이','V'),('에이치','H')]:t=re.sub(r'(?<![가-힣])'+a,b,t)
  t=re.sub(r'(?<![가-힣])알(?=이라고|이 됩|과 |도 )','R',t)
  t=t.replace('마이너스 L','−L').replace('이 곱하기 N·L','2 × (N·L)')
 for a,b in [('비알디에프','BRDF'),('로 나누기 파이','ρ/π'),('비율이 로에','비율이 ρ에'),('반사량이 로에','반사량이 ρ에'),('지를 로라고','지를 ρ라고'),('파이','π')]:
  if s in (22,23):t=t.replace(a,b)
 if s in range(60,69):
  for a,b in [('에스 엑스','sₓ'),('에스 와이','sᵧ'),('에스 제트','s_z'),('더블유','w'),('제트','z'),('와이','y'),('엑스','x'),('유 영점오','u = 0.5'),('x 영은','x = 0은')]:t=t.replace(a,b)
 if s==10:
  for a,b in [('마이너스 영점육, 영점팔,','−0.6, 0.8,'),('영, 일점육, 영이죠','(0, 1.6, 0)이죠'),('영, 일, 영이고','(0, 1, 0)이고'),('영점육, 영점팔,','0.6, 0.8,'),('영이면 내적은 영점팔','0이면 내적은 0.8'),('영이 됩니다','0이 됩니다')]:t=t.replace(a,b)
 if s==8:t=t.replace('길이를 일로','길이를 1로')
 if s==20:
  for a,b in [('코사인은 일','코사인은 1'),('육십 도 벌어지면 영점오','60° 벌어지면 0.5'),('구십 도면 영','90°면 0'),('영으로 제한','0으로 제한')]:t=t.replace(a,b)
 return t
KO=[dict(c,id=i+1,text=caption_text(int(c['scene']),c['text'])) for i,c in enumerate(AL['ko'])]
TERMS=['양방향 반사 분포 함수','하프웨이 벡터','표면 법선','라이트 프로브','구면 조화 함수','라이트맵','복사조도','복사휘도','정반사','난반사','환경광','발광','정점','픽셀']
HL={str(c['id']):{'text':next(term for term in TERMS if c['text'].count(term)==1),'role':'term'} for c in KO if any(c['text'].count(term)==1 for term in TERMS)}
def sidecars():
 # Preserve the exact cue timestamps and the old ASR/voice text.
 raw=(OLD/(SL+'.ko.srt')).read_text(encoding='utf-8-sig').strip().split('\n\n');assert len(raw)==len(KO)
 blocks=[]
 for block,orig,new in zip(raw,AL['ko'],KO):
  number,times,txt=block.split('\n',2);assert txt==orig['text'];blocks.append(number+'\n'+times+'\n'+new['text'])
 (DEST/(SL+'.ko.srt')).write_text('\n\n'.join(blocks)+'\n',encoding='utf-8')
 shutil.copyfile(OLD/(SL+'.en.srt'),DEST/(SL+'.en.srt'))
 write(W/'caption-delta.json',[{'scene':a['scene'],'cue':b['id'],'old':a['text'],'new':b['text']} for a,b in zip(AL['ko'],KO) if a['text']!=b['text']])
def imageset(sid,c):
 s=int(sid);lo=round(c['sourceIn']*60);n=c['frames'];hi=lo+n
 if s in HERO:
  od=W/'optical'/sid;od.mkdir(parents=True,exist_ok=True)
  manifest=od/'complete.json';source=sha(B/'optics.py')
  if sid not in os.environ.get('M21_REFRESH_SCENES','').split(',') and manifest.exists() and read(manifest).get('source')==source:return {int(k):od/v for k,v in read(manifest)['keys'].items()}
  # Time ranges outside these intervals are genuinely steady; motion is rendered at the master frame times.
  anim={1:[(1.6,3.9),(15.9,20.2)],2:[(5.1,6.4),(7.4,8.7)],3:[(7.6,14.3),(15,17.6)],4:[(3.2,3.5),(4.5,6.1),(10.7,11)],7:[(18.7,25.1)],8:[(0,1.5),(3.3,4.8),(5.9,7.4),(12.7,14.2),(17.3,18.7)],9:[(0,4.6),(5,7.6),(9,14.2)],10:[(0,4.6),(5,7.6),(9,14.2),(20,20.3)],11:[(0,6.8),(8.15,10.9)],16:[(3.8,8.8),(12.7,15.2),(16.7,19.2)],17:[(0,3.95)],20:[(0,2.8),(4.8,6.05),(6.95,8.1),(16.5,18.05)],55:[(4.75,7.35)],51:[(0,2.1),(12.3,16.95)]}[s]
  keys={lo,hi-1};
  for a,b in anim:keys.update(range(max(lo,int(a*60)),min(hi,int(b*60)+2)))
  for t in KO:
   if int(t['scene'])==s:
    f=math.ceil(t['start']*60-c['globalStartFrame']+lo)
    if lo<=f<hi:keys.add(f)
  entries={};prev=None;path=None
  for f in sorted(keys):
   img=paint(s,f/60);raw=io.BytesIO();img.save(raw,format='JPEG',quality=96,subsampling=0);data=raw.getvalue()
   if data!=prev:path=od/f'{f:06}.jpg';path.write_bytes(data);prev=data;entries[f-lo]=path.name
  write(manifest,dict(source=source,keys=entries));return {k:od/v for k,v in entries.items()}
 group='bake-jobs' if int(sid) in BAKE else 'fit-jobs' if int(sid) in {53,56,58} and (W/'fit-override.json').is_file() else 'native-jobs'
 j=read(W/group/(sid+'.json'));od=Path(j['output'])
 if not (od/'capture-success.json').exists():raise RuntimeError('Pending Unity scene '+sid)
 assert read(od/'capture-success.json')['completed']==len(j['sampleFrames'])
 return {k-lo:od/f'frame-{k:06}.jpg' for k in j['sampleFrames']}
def grid(c):
 od=W/'closing';od.mkdir(exist_ok=True);imgs=[]
 for n,(sid,label) in enumerate([(9,'표면점의 반사'),(37,'면 · 정점 · 픽셀'),(74,'고정된 그림자'),(76,'움직이는 물체와 프로브')]):
  cut=next(i for i in Q['cuts'] if i['kind']=='explanation' and int(i['scene'])==sid)
  if sid==9:im=paint(9,14.5).crop((180,175,1140,915))
  elif sid==37:
   paths=imageset('037',cut);im=Image.open(list(paths.values())[-1]).crop((270,230,1650,830))
  elif (W/'bake-override.json').exists():
   paths=imageset(f'{sid:03}',cut);im=Image.open(list(paths.values())[-1]).crop((270,220,1670,834))
  else:
   f=od/f'real-bake-{sid}.jpg';ff('-ss',(120+cut['globalStartFrame']+cut['frames']*.72)/60,'-i',OLD/(SL+'.clean.mp4'),'-frames:v',1,'-update',1,f);im=Image.open(f).crop((270,220,1670,834))
  imgs.append((im.copy(),label))
 conf=read(W.parent/'render-v2/cues/078.json');times=[0]+[max(0,math.ceil(t*60)) for t in conf['stepTimes']]
 result={}
 for phase,k in enumerate(times):
  im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);text(d,(96,65),'빛 한 점에서 게임 화면까지',54,GOLD,True)
  for n,(sm,label) in enumerate(imgs):
   x=100+n%2*875;y=170+n//2*355;box=sm.copy();box.thumbnail((805,258));im.paste(box,(x+(810-box.width)//2,y));d.rectangle((x,y,x+811,y+259),outline=GOLD if n==max(0,phase-1) else '#384446',width=4);text(d,(x,y+269),label,42,WHITE,True)
  f=od/f'grid-{phase}.jpg';im.save(f,quality=96);result[k]=f
 return result
def listjpg(jpg,n,rows,file):
 # Put subtitle boundaries on the sparse input as well; output FPS then duplicates only literally static images.
 keyed=sorted(jpg);assert keyed[0]==0
 changes=set(keyed)
 for a in rows:
  for t in [a['start'],a['end']]:
   for off in [-1,0,1]:
    k=round(t*60)+off
    if 0<=k<n:changes.add(k)
 keys=sorted(k for k in changes if 0<=k<n);out=['ffconcat version 1.0'];us=lambda f: round(f*1e6/60)
 for i,k in enumerate(keys):
  p=jpg[keyed[bisect.bisect_right(keyed,k)-1]]
  assert p.exists(),p
  out += ["file '"+p.as_posix()+"'",'option framerate 60',f'duration {(us(keys[i+1] if i+1<len(keys) else n)-us(k))/1e6:.6f}']
 out+=["file '"+jpg[keyed[-1]].as_posix()+"'",'option framerate 60'];file.write_text('\n'.join(out)+'\n',encoding='utf-8')
def enc():
 return ['-c:v','libx264','-threads','3','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p','-g','120','-bf','0','-color_primaries','bt709','-colorspace','bt709','-color_trc','bt709','-video_track_timescale','90000']
def frames(p):return int(next(w for w in probe(p)['streams'] if w['codec_type']=='video')['nb_frames'])
def render(c,i):
 sid=c['scene'];n=c['frames'];secs=c['globalStartFrame']/60; name=f'{i:03}-{sid}';target=D/(name+'.mp4');cap=D/(name+'-cap.mp4');ok=D/(name+'.done.json')
 if ok.is_file() and sid not in os.environ.get('M21_REFRESH_SCENES','').split(','):assert target.is_file() and cap.is_file();return
 rows=[dict(v,start=max(0,v['start']-secs),end=min(n/60,v['end']-secs)) for v in KO if v['end']>secs+1e-7 and v['start']<secs+n/60-1e-7]
 layout=CAP.caption_ass(D/(name+'.ass'),rows,0,HL);assert all(len(v['lines'])<=2 for v in layout)
 if c['kind']!='explanation' or int(sid) in BAKE and not (W/'bake-override.json').is_file():
  args=['-ss',(secs+2),'-threads','2','-i',OLD/(SL+'.clean.mp4')]
  fmt='setsar=1,format=yuv420p'
 else:
  jpg=grid(c) if int(sid)==78 else imageset(sid,c);listing=D/(name+'.ffconcat');listjpg(jpg,n,rows,listing)
  args=['-threads','1','-f','concat','-safe','0','-i',listing];fmt='scale=in_range=full:out_range=tv:out_color_matrix=bt709,setsar=1,format=yuv420p'
 filt=f'[0:v]{fmt},fps=60,split=2[clean][two];[two]ass={name}.ass[cap]'
 ff(*args,'-filter_complex_threads','2','-filter_complex',filt,'-map','[clean]','-an','-frames:v',n,*enc(),target,'-map','[cap]','-an','-frames:v',n,*enc(),cap)
 assert n==frames(target)==frames(cap),(name,n,frames(target),frames(cap))
 write(ok,{'frames':n,'clean':sha(target),'captioned':sha(cap),'captionCues':len(rows),'source':c['kind'],'originalRoomReused':int(sid) in BAKE and not (W/'bake-override.json').is_file()})
def join():
 table=Q['cuts'];raw=OLD/(SL+'.clean.mp4');book=[]
 for name,start,n in [('brand',0,120),('member',120+Q['bodyFrames'],600)]:
  p=D/(name+'.mp4')
  if not p.is_file() or frames(p)!=n:
   at=0.
   if name=='member':
    # V4 preserved all frames but its concat timestamps drift by ~24 ms at the tail.
    rows=subprocess.check_output(['ffprobe','-v','error','-read_intervals',f'{start/60-6:.4f}%','-select_streams','v:0','-show_entries','packet=pts_time','-of','csv=p=0',str(raw)]).decode().splitlines()
    pts=sorted(float(x.split(',')[0]) for x in rows if x.strip());assert len(pts)>n
    at=(pts[-n-1]+pts[-n])/2
   fresh=D/(name+'-verified.mp4');ff('-ss',f'{at:.6f}','-i',raw,'-map','0:v:0','-an','-vf','setpts=N/(60*TB)','-fps_mode','passthrough','-frames:v',n,*enc(),fresh)
   assert frames(fresh)==n;os.replace(fresh,p)
  assert frames(p)==n;book.append((p,n))
 for typ in ['clean','captioned']:
  files=[book[0]]+[(D/(f'{i:03}-{c["scene"]}'+('-cap' if typ=='captioned' else '')+'.mp4'),c['frames']) for i,c in enumerate(table)]+[book[1]];lst=D/f'{typ}-join.ffconcat';acc=0;lines=['ffconcat version 1.0']
  for p,n in files:
   lines.extend(["file '"+p.as_posix()+"'",'duration %.6f'%((round((acc+n)*1e6/60)-round(acc*1e6/60))/1e6)]);acc+=n
  lst.write_text('\n'.join(lines)+'\n',encoding='utf-8');final=DEST/(SL+'.'+typ+'.mp4')
  temp=final.with_suffix('.joining.mp4');ff('-f','concat','-safe','0','-i',lst,'-i',raw,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',temp);assert frames(temp)==Q['bodyFrames']+720;os.replace(temp,final)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--priority',action='store_true');ap.add_argument('--one');ap.add_argument('--all',action='store_true');ap.add_argument('--join',action='store_true');a=ap.parse_args()
 sidecars()
 if a.join:join();return
 cuts=list(enumerate(Q['cuts']));cuts.sort(key=lambda x: (0 if x[1]['scene'] in ['008','009','010','011','003'] else 1,x[0]))
 for i,c in cuts:
  if a.one and c['scene']!=a.one:continue
  if a.priority and int(c['scene']) not in HERO:continue
  render(c,i);print('encoded',i,c['scene'],flush=True)
 if a.all:join()
if __name__=='__main__':main()
