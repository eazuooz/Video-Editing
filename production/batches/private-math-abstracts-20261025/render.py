"""Replace only the selected opening. Stream-copy the unchanged body and audio."""
from pathlib import Path
import subprocess,json,hashlib,sys,shutil,math,datetime
R=Path('D:/Github/VideoEditing'); B=Path(__file__).resolve().parent
ENC=['-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-video_track_timescale','60000']
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Malgun Gothic,42,&H00EFF5F5,&H00FFFFFF,&H00120D09,&H00120D09,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def ff(args,log,cwd):
 with Path(log).open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-v','warning','-nostdin','-y',*map(str,args)],stdout=f,stderr=f,cwd=cwd,check=True)
def auth(id):
 a=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations'][B.name]
 assert a['status']=='active' and a['renderAuthorized'] and id in a['episodeIds'] and not a['newTtsAuthorized'] and not a['uploadAuthorized']
def stamp(t):
 n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
def guides(p):
 rows=[];end=p['abstractEnd']
 def event(a,b,s):rows.append(f'Dialogue: 0,{stamp(a)},{stamp(b)},Default,,0,0,0,,{s}')
 def text(a,b,x,y,s,size=42,c='EFF5F5'):
  event(a,b,'{\\pos('+f'{x},{y}'+')\\fs'+str(size)+'\\1c&H'+c+'&}'+s)
 def line(a,b,pts,c='A2D380'):
  # ASS closes paths implicitly: separate each stroke so an open leader
  # never becomes a triangular outline across the game.
  drawing=' '.join(f'm {a[0]:.1f} {a[1]:.1f} l {b[0]:.1f} {b[1]:.1f}' for a,b in zip(pts,pts[1:]))
  event(a,b,'{\\an7\\pos(0,0)\\p1\\bord5\\shad0\\1a&HFF&\\3c&H'+c+'&}'+drawing)
 text(2,end,44,15,p['headline'],52,'73D7FF')
 for s in p['segments']:
  text(s['start'],s['end'],44,77,s['game']+' · 실제 게임',30,'BCC0A7')
  for g in s['guides']:
   a=s['start']+g['from'];b=min(s['end'],s['start']+g['to']);cx=280+1360*g['xy'][0];cy=110+765*g['xy'][1];r=g.get('radius',60)
   leaderY=450 if s['sourceKey']=='totk' else 290
   text(a,b,32,leaderY-55,g['label'],38)
   # These are short-lived editorial marks over inspected stable targets.
   # Native game rotation handles remain visible; no invented world axes.
   if g.get('kind')=='arc':angles=[-.8*math.pi+i*1.5*math.pi/32 for i in range(33)]
   else:angles=[i*2*math.pi/40 for i in range(41)]
   pts=[(cx+r*math.cos(v),cy+r*math.sin(v)) for v in angles]
   for j in range(1,len(pts)):line(a+.45*(j-1)/(len(pts)-1),b,pts[j-1:j+1])
   line(a+.45,b,[(245,leaderY),(265,leaderY),(cx-r,cy)])
   if g.get('kind')=='arc':
    x,y=pts[-1];v=angles[-1]+math.pi/2
    line(a+.45,b,[(x-20*math.cos(v-.5),y-20*math.sin(v-.5)),(x,y),(x-20*math.cos(v+.5),y-20*math.sin(v+.5))])
 return HEADER+'\n'.join(rows)+'\n'
def keyframe(file,after):
 j=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-skip_frame','nokey','-read_intervals',f'0%{after+10}','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(file)]))
 return next(round(float(x['best_effort_timestamp_time'])*60)/60 for x in j['frames'] if float(x['best_effort_timestamp_time'])>=after-.00001)
def run(id):
 pp=B/'plans'/f'{id}.json';p=read(pp);auth(id);assert p['status'] in ['sources-reviewed','rendering','encoded-qa-pending']
 W=Path(p['work']);D=R/p['output'];old=R/p['oldOutput'];slug=p['slug'];W.mkdir(parents=True,exist_ok=True)
 if (W/'render-receipt.json').exists():return read(W/'render-receipt.json')
 assert sha(old/f'{slug}.captioned.mp4')==p['oldMasterSha256']
 cut=keyframe(old/f'{slug}.clean.mp4',p['abstractEnd']);assert keyframe(old/f'{slug}.captioned.mp4',cut)==cut
 n=round(cut*60);p.update(status='rendering',copyBodyFromFrame=n,copyBodyFromSeconds=cut);save(pp,p)
 (W/'guides.ass').write_text(guides(p),encoding='utf8')
 shutil.copyfile(R/'projects'/slug/'production/local/concept-fit-v2/captions.ko.ass',W/'captions.ass')
 parts=[]
 for s in p['segments']:
  f=W/f'game-{s["index"]}.mp4';parts.append(f)
  if not f.exists():
   auth(id)
   ff(['-ss',s['sourceIn'],'-i',R/s['source'],'-filter_threads','2','-vf','scale=1360:765:flags=lanczos,pad=1920:1080:280:110:color=0x090D12,setsar=1,fps=60,setpts=N/(60*TB)','-frames:v',round(s['seconds']*60),'-an',*ENC,f],W/f'game-{s["index"]}.log',W)
 listing=W/'games.txt';listing.write_text('\n'.join("file '"+x.as_posix()+"'" for x in parts)+'\n',encoding='utf8')
 ff(['-f','concat','-safe','0','-i',listing,'-an','-c:v','copy',W/'game.mp4'],W/'game-join.log',W)
 # Old first two seconds and the transition to the first copied keyframe stay.
 graph=f'[1:v]setpts=PTS-STARTPTS+2/TB[g];[0:v][g]overlay=eof_action=pass:repeatlast=0:enable=gte(t\\,2)*lt(t\\,{p["abstractEnd"]}),ass=guides.ass,split=2[clean][c];[c]ass=captions.ass[captioned]'
 args=['-i',old/f'{slug}.clean.mp4','-i',W/'game.mp4','-filter_complex_threads','2','-filter_complex',graph]
 for kind in ['clean','captioned']:args+=['-map',f'[{kind}]','-frames:v',n,'-an',*ENC,W/f'prefix-{kind}.mp4']
 auth(id);ff(args,W/'prefix.log',W)
 outputs=[]
 for kind in ['clean','captioned']:
  source=old/f'{slug}.{kind}.mp4';suffix=W/f'suffix-{kind}.mp4'
  ff(['-ss',cut,'-i',source,'-map','0:v:0','-an','-c:v','copy','-avoid_negative_ts','disabled',suffix],W/f'suffix-{kind}.log',W)
  listing=W/f'{kind}.txt';listing.write_text("file '"+(W/f'prefix-{kind}.mp4').as_posix()+"'\nfile '"+suffix.as_posix()+"'\n",encoding='utf8')
  target=D/f'{slug}.{kind}.mp4'
  ff(['-f','concat','-safe','0','-i',listing,'-i',source,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',target],W/f'final-{kind}.log',W)
  meta=probe(target);v=next(x for x in meta['streams'] if x['codec_type']=='video')
  assert int(v['nb_frames'])==p['totalFrames'],(id,v['nb_frames'],p['totalFrames'])
  assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1'
  outputs.append(dict(path=target.relative_to(R).as_posix(),bytes=target.stat().st_size,sha256=sha(target)))
 for lang in ['ko','en']:
  target=D/f'{slug}.{lang}.srt';shutil.copyfile(old/target.name,target);assert sha(target)==sha(old/target.name)
  outputs.append(dict(path=target.relative_to(R).as_posix(),bytes=target.stat().st_size,sha256=sha(target)))
 result=dict(id=id,status='encoded-qa-pending',outputs=outputs,copyBodyFromFrame=n,copyBodyFromSeconds=cut,totalFrames=p['totalFrames'],seconds=p['seconds'],humanReview='pending',newTts=False)
 save(W/'render-receipt.json',result);save(R/'projects'/slug/'production/actual-abstract-v6/outputs.json',result);p['status']='encoded-qa-pending';save(pp,p)
 print(id,'encoded',p['seconds'],'seconds',flush=True);return result
if __name__=='__main__':
 for id in sys.argv[1:]:run(id)
