"""Exact-boundary native game inserts; accepted explanation pictures are copied by GOP."""
import os,sys,math,re,bisect,subprocess,shutil,datetime,argparse
from pathlib import Path
from prepare import *
OUT=ROOT/'output/game-math-concept-examples-20261116'
WORK=Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingWork/game-math-concept-examples-20261116'
def run(args,cwd=HERE,name='command',capture=False):
 args=list(map(str,args));cwd.mkdir(parents=True,exist_ok=True)
 if capture:
  p=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  if p.returncode:raise RuntimeError(p.stderr.decode('utf8','replace')[-3000:])
  return p.stdout
 with open(cwd/(name+'.log'),'w',encoding='utf8') as f:p=subprocess.run(args,cwd=cwd,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 if p.returncode:raise RuntimeError((cwd/(name+'.log')).read_text(encoding='utf8',errors='replace')[-3000:])
def ff(args,cwd=HERE,name='ffmpeg',capture=False):return run([FF,'-v','warning','-hide_banner','-nostdin','-y',*args],cwd,name,capture)
def streams(p):return read_json(run([FP,'-v','error','-show_streams','-of','json',p],capture=True))['streams']
def read_json(b):return json.loads(b.decode('utf8'))
def video(p):return next(x for x in streams(p) if x['codec_type']=='video')
def clock(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def unclock(x):
 h,m,s=map(float,x.replace(',','.').split(':'));return h*3600+m*60+s
def read_srt(p):
 result=[]
 for block in Path(p).read_text(encoding='utf-8-sig').strip().replace('\r','').split('\n\n'):
  ls=block.splitlines()
  if len(ls)>=3 and ' --> ' in ls[1]:
   a,z=map(unclock,ls[1].split(' --> '));result.append(dict(start=a,end=z,text='\n'.join(ls[2:])))
 return result
def write_srt(p,cues):
 cues=sorted(cues,key=lambda x:x['start']);Path(p).write_text('\n\n'.join(f'{i}\n{clock(x["start"])} --> {clock(x["end"])}\n{x["text"]}' for i,x in enumerate(cues,1))+'\n',encoding='utf8')
def ac(t):return clock(t).replace(',','.')[1:-1]
def ass_header():return '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,맑은 고딕,43,&H00FFFFFF,&H00FFFFFF,&H00100805,&H00100805,-1,0,0,0,100,100,0,0,1,3,0,2,100,100,22,1
Style: Mark,맑은 고딕,33,&H0064D6F2,&H0064D6F2,&H00100805,&H00100805,-1,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def wrap(text,font,maxwidth):
 rows=[];row=''
 for word in text.split():
  candidate=(row+' '+word).strip()
  if row and font.getlength(candidate)>maxwidth:rows.append(row);row=word
  else:row=candidate
 if row:rows.append(row)
 return rows
def card(s,source,p):
 im=Image.new('RGBA',(1920,1080),'#070b10');d=ImageDraw.Draw(im);f='C:/Windows/Fonts/malgun.ttf';bold='C:/Windows/Fonts/malgunbd.ttf'
 def text(x,y,t,size=30,color='#EDF1F5',width=1800,b=False):
  font=ImageFont.truetype(bold if b else f,size)
  for row in wrap(t,font,width):d.text((x,y),row,font=font,fill=color);y+=size*1.48
  return y
 text(42,18,'개념에서 실제 게임으로',29,'#72D8CF',b=True)
 text(42,60,s['concept'],40,'#E9D087',b=True,width=1500)
 text(1580,30,'얌얌코딩',29,'#EDF1F5',b=True,width=300)
 # Transparent viewport: the entire original game image is scaled, never cropped.
 im.paste((0,0,0,0),(40,150,1480,960))
 y=text(1518,160,'지금 볼 장면',29,'#72D8CF',width=350,b=True)
 y=text(1518,y+18,source['game'],28,width=350,b=True)
 d.line([(1518,y+28),(1870,y+28)],fill='#48525E',width=2)
 y=text(1518,y+66,'관찰 포인트',31,'#E9D087',width=350,b=True)
 text(1518,y+22,s['question'],37,width=350,b=True)
 text(1518,760,'앞에서 배운 개념과\n눈앞의 움직임을\n연결해서 보세요.',27,'#B7C2CC',width=350)
 text(42,112,source['game'],23,'#AAB8C5')
 im.save(p/'layout.png')
 # No fabricated engine vectors. Short screen-space attention guides only at
 # directly inspected, stable targets; otherwise keep the action unobscured.
 marks=[];kind=s['candidate'];a=s['sourceIn']
 cases={
  'car-speed':(22,35,.94,.88,.095,.15),
  'kart-start':(8,15,.50,.67,.19,.29),
  'kart-turn':(45,51,.50,.63,.20,.30),
  'beam-climb':(35,41,.49,.65,.34,.40),
  'suspension':(8,14,.48,.55,.29,.40),
  'beam-joints':(74,80,.48,.56,.29,.40),
  'cannon':(176,179,.49,.68,.22,.22),
  'portal-occlude':(429,434,.83,.46,.19,.64),
  'maker-corner':(222,227,.60,.39,.35,.36),
  'maker-path':(222,227,.60,.39,.35,.36),
 }
 if kind in cases:
  aa,zz,cx,cy,w,h=cases[kind];aa=max(0,aa-a);zz=min(s['frames']/60,zz-a)
  if zz>aa:
   x0=40+(cx-w/2)*1440;y0=150+(cy-h/2)*810;x1=x0+w*1440;y1=y0+h*810
   # Open corners leave the original visible object intact.
   L=25;th=5
   for x,y,sx,sy in [(x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)]:
    shape=f'm {x:.1f} {y:.1f} l {x+sx*L:.1f} {y:.1f} {x+sx*L:.1f} {y+th:.1f} {x+sx*th:.1f} {y+th:.1f} {x+sx*th:.1f} {y+sy*L:.1f} {x:.1f} {y+sy*L:.1f}'
    marks.append(f'Dialogue: 1,{ac(aa)},{ac(zz)},Mark,,0,0,0,,{{\\an7\\pos(0,0)\\bord0\\shad0\\1c&H64D6F2&\\p1}}{shape}{{\\p0}}')
 (p/'marks.ass').write_text(ass_header()+'\n'.join(marks)+'\n',encoding='utf8')
def captions(s,p):
 cues=read(HERE/'alignment.json')['items'][s['key']]['cues']
 for lang in ('ko','en'):write_srt(p/(lang+'.srt'),[dict(start=x['start'],end=x['end'],text=x[lang]) for x in cues])
 cap=[]
 for c in cues:cap.append(f'Dialogue: 3,{ac(c["start"])},{ac(c["end"])},Caption,,0,0,0,,'+c['ko'].replace('\n',r'\N'))
 (p/'captions.ass').write_text(ass_header()+'\n'.join(cap)+'\n',encoding='utf8')
def codec():return ['-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','60','-g','120','-keyint_min','120','-sc_threshold','0','-bf','2','-video_track_timescale','90000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
def insert(s,source):
 p=WORK/'inserts'/s['key'];p.mkdir(parents=True,exist_ok=True);card(s,source,p);captions(s,p)
 outputs=[p/(k+'.mp4') for k in ('clean','captioned')]
 receipt=p/'video.json';sig=sha(HERE/'plan.json')+sha(HERE/'alignment.json')+sha(Path(__file__))
 if receipt.exists() and read(receipt).get('signature')==sig and all(f.exists() for f in outputs):return outputs
 graph='[0:v]fps=60,scale=1440:810:flags=lanczos,setsar=1,setpts=PTS-STARTPTS,pad=1920:1080:40:150:color=black[g];[g][1:v]overlay=0:0:shortest=1,ass=marks.ass,split=2[clean][c];[c]ass=captions.ass[cap]'
 args=['-threads','2','-ss',s['sourceIn'],'-i',source['file'],'-loop','1','-i','layout.png','-filter_complex_threads','2','-filter_complex',graph]
 for label,f in zip(['[clean]','[cap]'],outputs):args+=['-map',label,'-an','-frames:v',s['frames'],*codec(),f]
 ff(args,p,'encode')
 for f in outputs:assert int(video(f)['nb_frames'])==s['frames']
 save(receipt,dict(signature=sig,frames=s['frames'],sourceIn=s['sourceIn'],sourceOut=s['sourceIn']+s['frames']/60,sourceSha256=source['sha256'],nativeSpeed=1,loop=False,freezePadding=False))
 return outputs
def joint_keys(e,p):
 f=p/'keys.json'
 if f.exists():return read(f)
 both=[]
 for k in ('clean','captioned'):
  frames=read_json(run([FP,'-v','error','-skip_frame','nokey','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',e['baselineFiles'][k]['path']],capture=True))['frames']
  both.append({0,e['baselineFrames'],*[round(float(x['best_effort_timestamp_time'])*60) for x in frames if 'best_effort_timestamp_time' in x]})
 out=sorted(both[0]&both[1]);save(f,out);return out
def pieces(a,z,keys):
 mid_a=min((k for k in keys if k>=a),default=z);mid_z=max((k for k in keys if k<=z),default=a)
 if mid_a>=mid_z:return [(a,z,False)] if z>a else []
 out=[]
 if a<mid_a:out.append((a,mid_a,False))
 out.append((mid_a,mid_z,True))
 if mid_z<z:out.append((mid_z,z,False))
 return out
def original_piece(e,a,z,copy,p):
 out=[]
 for kind in ('clean','captioned'):
  f=p/f'original-{a}-{z}.{kind}.mp4';out.append(f)
  if f.exists() and int(video(f).get('nb_frames',0))==z-a:continue
  args=['-threads','2','-ss',a/60,'-i',e['baselineFiles'][kind]['path'],'-map','0:v:0','-an','-frames:v',z-a]
  args+=['-c:v','copy','-video_track_timescale','90000'] if copy else ['-vf','setsar=1,setpts=PTS-STARTPTS',*codec()]
  ff([*args,f],p,f'original-{a}-{z}-{kind}');assert int(video(f)['nb_frames'])==z-a
 return out
def mix_insert(s,source,p):
 f=p/(s['key']+'.wav')
 voice=HERE/'local/voice'/(s['key']+'.wav');dur=s['frames']/60
 prepared=read(HERE/'speech-free-game-audio.json')['items'].get(s['key']) if (HERE/'speech-free-game-audio.json').exists() else None
 if prepared:assert prepared['frames']==s['frames'] and abs(prepared['sourceIn']-s['sourceIn'])<.0001
 signature='mix-v3|'+sha(voice)+'|'+str(s['frames'])+'|'+(prepared['sha256'] if prepared else source.get('audioSha256',source['sha256']))
 cache=p/(s['key']+'-mix.json')
 if f.exists() and cache.exists() and read(cache).get('signature')==signature:return f
 import numpy as np,wave
 def speech_median(x,sr):
  n=round(sr*.05);x=x[:len(x)//n*n].reshape(-1,n);r=np.sqrt(np.mean(x*x,axis=1));active=r[r>max(1e-5,float(r.max())*.0562)];return float(20*np.log10(np.median(active)+1e-12))
 ref=ff(['-ss',max(0,s['referenceTime']-5),'-t',4,'-i',s['referenceFile'],'-map','0:a:0','-ac','1','-ar','24000','-f','f32le','-'],p,'reference',True)
 target=max(-24,min(-17,speech_median(np.frombuffer(ref,dtype='<f4'),24000)))
 with wave.open(str(voice),'rb') as w:sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype('float32')/32768
 current=speech_median(x,sr);gain=min(8,max(-8,target-current));peak=float(abs(x).max())*10**(gain/20);gain-=max(0,20*math.log10(max(peak,1e-9)/.76))
 save(p/(s['key']+'-levels.json'),dict(sourceSpeechMedianDbfs=current,adjacentLectureMedianDbfs=target,bridgeGainDb=gain,gameIntegratedTargetLufs=-23,duck=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280),noAddedLectureBgm=True))
 inputs=['-i',voice];graph=f'[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.5f}dB,apad,atrim=end_sample={s["frames"]*800},asetpts=PTS-STARTPTS,asplit=2[n][sc];'
 if source['hasAudio'] or source.get('audioFile'):
  inputs+=['-ss',0 if prepared else s['sourceIn'],'-t',dur,'-i',prepared['path'] if prepared else source.get('audioFile',source['file'])]
  norm='' if prepared else 'loudnorm=I=-23:TP=-3:LRA=11,'
  graph+=f'[1:a]{norm}aresample=48000,aformat=channel_layouts=stereo,afade=t=in:st=0:d=0.04,afade=t=out:st={dur-.05:.6f}:d=0.05[g];[g][sc]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[d];[n][d]amix=inputs=2:duration=first:normalize=0,aresample=192000,alimiter=limit=0.831764:level=false:latency=true,aresample=48000[a]'
 else:graph+='[sc]anullsink;[n]anull[a]'
 ff([*inputs,'-filter_complex_threads','2','-filter_complex',graph,'-map','[a]','-t',dur,'-c:a','pcm_s16le',f],p,s['key']+'-audio');save(cache,dict(signature=signature,preparedAudio=prepared,voiceSha256=sha(voice),sourceAudioMethod='commentary-separated residual game audio; no extra boost' if prepared else 'same-recording audio with standard game-sound mix'));return f
def combined_audio(e,p,sources):
 out=p/'audio.m4a';inputs=['-i',e['baselineFiles']['clean']['path']];n=len(e['inserts']);graph=[f'[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit={n+1}'+''.join(f'[b{i}]' for i in range(n+1))];labels=[];cursor=0
 for i,s in enumerate(e['inserts']):
  graph.append(f'[b{i}]atrim=start_sample={cursor*800}:end_sample={s["atFrame"]*800},asetpts=PTS-STARTPTS[o{i}]');labels.append(f'[o{i}]')
  f=mix_insert(s,sources[s['source']],p);inputs+=['-i',f];graph.append(f'[{i+1}:a]atrim=end_sample={s["frames"]*800},asetpts=PTS-STARTPTS[i{i}]');labels.append(f'[i{i}]');cursor=s['atFrame']
 graph.append(f'[b{n}]atrim=start_sample={cursor*800}:end_sample={e["baselineFrames"]*800},apad,atrim=end_sample={(e["baselineFrames"]-cursor)*800},asetpts=PTS-STARTPTS[o{n}]');labels.append(f'[o{n}]')
 graph.append(''.join(labels)+f'concat=n={len(labels)}:v=0:a=1[a]')
 ff([*inputs,'-filter_complex_threads','2','-filter_complex',';'.join(graph),'-map','[a]','-c:a','aac','-b:a','192k',out],p,'audio');return out
def packet_grid(p,count):
 ps=read_json(run([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts','-of','json',p],capture=True))['packets'];assert len(ps)==count
 assert sorted(int(x['pts']) for x in ps)==list(range(0,count*1500,1500));ds=[int(x['dts']) for x in ps];assert all(x<y for x,y in zip(ds,ds[1:]));return dict(frames=count,all60fpsPresentationTimestamps=True,monotonicDecode=True)
def episode(e):
 receipt=HERE/'deliveries'/(e['id']+'.json')
 if receipt.exists():
  old=read(receipt)
  if all(Path(x['path']).exists() and sha(x['path'])==x['sha256'] for x in old['files'].values()):print(e['id'],'already rendered',flush=True);return
 p=WORK/'episodes'/e['id'];p.mkdir(parents=True,exist_ok=True);dest=OUT/e['id'];dest.mkdir(parents=True,exist_ok=True)
 assert shutil.disk_usage(dest.resolve().anchor).free>2*1024**3,('insufficient output drive space',dest.resolve())
 sources=read(HERE/'sources.json');voices={x['key']:x for x in read(HERE/'voice.json')['items']}
 assert all(voices[s['key']]['qualityPassed'] and voices[s['key']].get('contentCurrent',True) for s in e['inserts']),('unfinished new bridge QA',e['id'])
 reviewed=read(HERE/'bridge-review.json');assert reviewed['allSelectedNewBridgeTextReviewed']
 assert all(reviewed['items'][s['key']]['rawAudioSha256']==sha(HERE/'local/voice/raw'/(s['key']+'.wav')) for s in e['inserts']),('new voice changed after content review',e['id'])
 keys=joint_keys(e,p);sequence=[];cursor=0;offset=0
 for s in e['inserts']:
  for a,z,c in pieces(cursor,s['atFrame'],keys):sequence.append(dict(files=original_piece(e,a,z,c,p),frames=z-a,original=[a,z],copied=c))
  # Enough native motion for observation, with at most a short useful interval
  # after the sentence. Never freeze, repeat or speed up to fit a voice.
  v=voices[s['key']];duration=max(v['seconds']+.6,min(18,s['sourceOut']-s['sourceIn']))
  s['frames']=math.ceil(duration*60-1e-7);assert s['frames']/60<=s['sourceOut']-s['sourceIn']+.001,(s['key'],'voice longer than observed action',duration)
  s['referenceFile']=e['baselineFiles']['clean']['path'];s['referenceTime']=s['atFrame']/60
  s['startFrame']=s['atFrame']+offset;sequence.append(dict(files=insert(s,sources[s['source']]),frames=s['frames'],insert=s['key']));offset+=s['frames'];cursor=s['atFrame']
 for a,z,c in pieces(cursor,e['baselineFrames'],keys):sequence.append(dict(files=original_piece(e,a,z,c,p),frames=z-a,original=[a,z],copied=c))
 audio=combined_audio(e,p,sources);total=e['baselineFrames']+offset;files={};qa=[]
 for i,kind in enumerate(('clean','captioned')):
  playlist=p/(kind+'.ffconcat');playlist.write_text('ffconcat version 1.0\n'+''.join("file '"+x['files'][i].as_posix()+"'\nduration "+f'{x["frames"]/60:.9f}\n' for x in sequence),encoding='utf8')
  f=dest/(e['slug']+'.'+kind+'.mp4');ff(['-f','concat','-safe','0','-i',playlist,'-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy','-bsf:v','setts=pts=PTS:dts=N*1500-4500:duration=1500','-video_track_timescale','90000','-movflags','+faststart',f],p,'assemble-'+kind)
  v=video(f);assert int(v['nb_frames'])==total and v['width']==1920 and v['height']==1080 and abs(float(v['duration'])-total/60)<.0001,(e['id'],kind,v)
  ff(['-threads','2','-v','error','-xerror','-i',f,'-map','0:v','-map','0:a','-f','null','-'],p,'decode-'+kind);grid=packet_grid(f,total);files[kind]=dict(path=str(f),sha256=sha(f));qa.append(dict(kind=kind,fullDecode=True,clock=grid))
 # Shift EVERY original bilingual cue by cumulative inserted duration.
 alignment=read(HERE/'alignment.json')['items']
 for lang in ('ko','en'):
  cues=read_srt(e['baselineFiles'][lang]['path']);count=len(cues)
  for c in cues:
   assert not any(c['start']+.03<s['atFrame']/60<c['end']-.03 for s in e['inserts']),('split spoken cue',e['id'],c)
   shift=sum(s['frames']/60 for s in e['inserts'] if s['atFrame']/60<=c['start']+.03);c['start']+=shift;c['end']+=shift
  for s in e['inserts']:
   for c in alignment[s['key']]['cues']:cues.append(dict(start=s['startFrame']/60+c['start'],end=s['startFrame']/60+c['end'],text=c[lang]))
  f=dest/(e['slug']+'.'+lang+'.srt');write_srt(f,cues);files[lang]=dict(path=str(f),sha256=sha(f));assert len(read_srt(f))>=count
 save(receipt,dict(id=e['id'],slug=e['slug'],title=e['title'],workDir=str(p),frames=total,duration=total/60,baselineFrames=e['baselineFrames'],addedFrames=offset,baselineFiles=e['baselineFiles'],files=files,inserts=e['inserts'],qa=qa,status='encoded-final-visual-and-audio-boundary-review-pending',explanationOrderPreserved=True,sourceVoiceTempo=1,platformChanged=False,humanReviewed=False))
 # Reproducible chunks only; preserve accepted masters, new inserts and voices.
 for x in sequence:
  if 'original' in x:
   for f in x['files']:assert f.resolve().is_relative_to(p.resolve());f.unlink()
 print(e['id'],'rendered with',len(e['inserts']),'actual-game observations',flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('episodes',nargs='*');a=ap.parse_args()
 assert read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['conceptExamplesRevision20261116']['renderAuthorized']
 for e in read(HERE/'plan.json')['episodes']:
  if not a.episodes or e['id'] in a.episodes:episode(e)
if __name__=='__main__':main()
