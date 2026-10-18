"""Finite narration mix, fixed captions, final pair and hash-specific technical QA."""
from pathlib import Path
import json,hashlib,subprocess,re,math,sys
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local';S=P.name
BIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin');FF=str(BIN/'ffmpeg.exe');FP=str(BIN/'ffprobe.exe')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(args,**kw):
 r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-3000:])
 return r
def loud(path):
 r=run([FF,'-hide_banner','-i',str(path),'-af','loudnorm=I=-18:TP=-1.5:LRA=9:print_format=json','-f','null','-']);return json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}',r.stderr.decode(errors='replace'))[-1])
def pcm(path):return np.frombuffer(run([FF,'-v','error','-i',str(path),'-ar','48000','-ac','2','-f','f32le','pipe:1']).stdout,dtype='<f4').reshape(-1,2).copy()
def db(a):return 20*math.log10(max(float(np.sqrt(np.mean(a.astype(np.float64)**2))),1e-12))
def check():assert read(R/'shared/publishing/video-production-control.json')['shortsRecurringAuthorization']['selectedShort']==S
def audio():
 check();assert not (L/'final-mix.m4a').exists(),'Preserve prior mix'
 narration=pcm(L/'narration-timeline.wav');assert len(narration)==1440000
 # Match complete speech phrases before applying gentle peak compression.
 # Cuts are already at verified quiet boundaries; no fade touches speech.
 phraseLevels=[]
 for p in read(L/'pcm-edit.json')['parts']:
  a,b=round(p['dest']*48000),round(p['destinationEnd']*48000);section=narration[a:b]
  levels=[db(section[i:i+19200]) for i in range(0,max(1,len(section)-19200),4800)]
  active=[v for v in levels if v>-45];reference=float(np.median(active));change=-22-reference
  narration[a:b]*=10**(change/20);phraseLevels.append(dict(start=p['dest'],end=p['destinationEnd'],sourceActiveMedianDbfs=reference,clipGainDb=change))
 sf.write(L/'narration-level-matched.wav',narration,48000,subtype='FLOAT')
 compression='acompressor=threshold=0.12:ratio=3:attack=5:release=140:makeup=1'
 run([FF,'-v','error','-n','-i',str(L/'narration-level-matched.wav'),'-af',compression,'-c:a','pcm_f32le',str(L/'narration-prepared-stem.wav')])
 narration=pcm(L/'narration-prepared-stem.wav');before=loud(L/'narration-prepared-stem.wav');gain=min(10**((-18-float(before['input_i']))/20),.75/max(abs(narration).max(),1e-9));stem=narration*gain
 src=read(P/'sources/source-map.json')['music'];music=R/src['path'];assert sha(music)==src['sha256']
 bed=pcm(music)[480000:1920000];assert len(bed)==1440000
 sf.write(L/'music-excerpt.wav',bed,48000,subtype='FLOAT');bg=loud(L/'music-excerpt.wav');bed*=10**((-31-float(bg['input_i']))/20)
 env=np.sqrt(np.mean(stem**2,axis=1));kernel=np.ones(24000)/24000;activity=np.convolve(env[::240],np.ones(100)/100,mode='same');duck=1-.42*np.minimum(1,activity/.04);bed*=np.interp(np.arange(1440000),np.arange(len(activity))*240,duck)[:,None]
 fade=np.ones(1440000);n=21600;fade[:n]=np.linspace(0,1,n);fade[-n:]=np.linspace(1,0,n);bed*=fade[:,None]
 effect=np.zeros_like(stem);tr=read(L/'capture-full-v1/trace.json')['frames'];events=[]
 for a,b in zip(tr,tr[1:]):
  if b['health']<a['health'] and b['shot']==a['shot']:
   start=round(b['frame']/60*48000);t=np.arange(7200)/48000;z=.05*np.sin(2*np.pi*(180*t+350*t*t))*np.exp(-35*t);effect[start:start+len(z)]+=z[:,None];events.append(dict(seconds=b['frame']/60,kind='authored-impact-sound',cause='actual health decrement'))
 summed=stem+bed+effect;overall=min(1,10**(-1.8/20)/max(abs(summed).max(),1e-9));stem*=overall;bed*=overall;effect*=overall;summed*=overall
 for name,a in [('narration-stem.wav',stem),('background-stem.wav',bed+effect),('final-mix.wav',summed)]:sf.write(L/name,a,48000,subtype='FLOAT')
 run([FF,'-v','warning','-n','-i',str(L/'final-mix.wav'),'-t','30','-c:a','aac','-b:a','192k',str(L/'final-mix.m4a')]);measured=loud(L/'final-mix.m4a');assert float(measured['input_tp'])<=-1.5
 save(L/'audio-build.json',dict(narrationSource=sha(L/'narration-timeline.wav'),preparedStemSha256=sha(L/'narration-prepared-stem.wav'),phraseLevels=phraseLevels,compression=compression,musicSha256=sha(music),speechGainDb=20*math.log10(gain*overall),backgroundTargetLufs=-31,voiceDucked=False,musicDucked=True,speechFades=False,speed=1,actualHitSoundEvents=events,finalMeasured=measured,mixSha256=sha(L/'final-mix.m4a')));print(json.dumps(measured))
def stamp(t,ass=False):
 n=round(t*(100 if ass else 1000));base=100 if ass else 1000;s,n=divmod(n,base);m,s=divmod(s,60);h,m=divmod(m,60);return f'{h}:{m:02}:{s:02}.{n:02}' if ass else f'{h:02}:{m:02}:{s:02},{n:03}'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',60)
def wrap(s):
 out=[];line=''
 for word in s.split():
  a=(line+' '+word).strip()
  if font.getlength(a)>796 and line:out.append(line);line=word
  else:line=a
 out.append(line);assert len(out)<=2,(s,out);return out
def captions():
 cues=read(P/'script/captions.json')['cues'];norm=lambda s:re.sub(r'[^가-힣A-Za-z0-9]','',s)
 assert norm(' '.join(c['ko'] for c in cues))==norm((P/'script/narration.ko.txt').read_text(encoding='utf8'))
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Text,Malgun Gothic,60,&H00090B08,&H00090B08,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Box,Malgun Gothic,60,&H00FFFFFF,&H00FFFFFF,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 ev=[];rows=[]
 for i,c in enumerate(cues,1):
  lines=wrap(c['ko']);w=max(font.getlength(x) for x in lines)+44;h=len(lines)*78+26;x=510-w/2;y=1380-h/2;assert x>=80 and x+w<=930
  when=f"{stamp(c['start'],True)},{stamp(c['end'],True)}"
  for layer,dx,dy,color in [(10,12,12,'&H323C07&'),(11,0,0,'&HFFFFFF&')]:
   a,b=x+dx,y+dy;poly=f'm {a:.1f} {b:.1f} l {a+w:.1f} {b:.1f} {a+w:.1f} {b+h:.1f} {a:.1f} {b+h:.1f}'
   ev.append(f'Dialogue: {layer},{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\1c{color}\\p1}}'+poly)
  for k,line in enumerate(lines):ev.append(f'Dialogue: 12,{when},Text,,0,0,0,,{{\\an5\\pos(510,{1380+(k-(len(lines)-1)/2)*78:.1f})}}'+line)
  rows.append(dict(cue=i,start=c['start'],end=c['end'],lines=lines,box=[x,y,w,h]))
 (L/'captions.ko.ass').write_text(header+'\n'.join(ev)+'\n',encoding='utf8')
 for lang in ['ko','en']:(L/f'captions.{lang}.srt').write_text('\n\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(wrap(c[lang])) for i,c in enumerate(cues,1))+'\n',encoding='utf8')
 save(L/'caption-layout.json',dict(rows=rows,center=[510,1380],font=60,maxLines=2))
def pair():
 check();captions();visual=R/'shared/output/motion-canvas/shorts-forgiving-hitbox-full-v2.mp4';mix=L/'final-mix.m4a'
 clean=L/f'{S}.clean.mp4';captioned=L/f'{S}.captioned.mp4'
 run([FF,'-v','warning','-n','-i',str(visual),'-i',str(mix),'-map','0:v:0','-map','1:a:0','-t','30','-c','copy','-movflags','+faststart',str(clean)])
 ass=str((L/'captions.ko.ass').resolve()).replace('\\','/').replace(':','\\:')
 run([FF,'-v','warning','-n','-i',str(clean),'-vf',f"ass=filename='{ass}'",'-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-c:a','copy','-movflags','+faststart',str(captioned)])
 save(L/'pair-build.json',dict(cleanSha256=sha(clean),captionedSha256=sha(captioned),mixSha256=sha(mix),visualSha256=sha(visual),frames=1800,seconds=30));print('Final clean/captioned pair encoded.')
def qa():
 final=L/f'{S}.captioned.mp4';q=L/'qa'/sha(final)[:16];q.mkdir(parents=True,exist_ok=True)
 report=q/'technical.json'
 if report.exists():print(str(report));return
 files={}
 for kind in ['clean','captioned']:
  f=L/f'{S}.{kind}.mp4';meta=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(f)]).stdout);v=next(s for s in meta['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',1800)
  assert abs(float(v['duration'])-30)<.0001
  run([FF,'-v','error','-n','-i',str(f),'-map','0:v:0','-f','framehash',str(q/f'{kind}.framehash'),'-map','0:a:0','-c:a','pcm_f32le',str(q/f'{kind}-decoded.wav')])
  lines=[l for l in (q/f'{kind}.framehash').read_text().splitlines() if not l.startswith('#')];assert len(lines)==1800
  pts=[int(l.split(',')[2]) for l in lines];assert pts==list(range(1800)),pts[:10]
  aac=q/f'{kind}.m4a';run([FF,'-v','error','-n','-i',str(f),'-vn','-c:a','copy',str(aac)])
  files[kind]=dict(path=str(f.relative_to(R)),sha256=sha(f),frames=1800,ptsUniform=True,fullDecode=True,aacSha256=sha(aac))
 assert files['clean']['aacSha256']==files['captioned']['aacSha256']
 src=pcm(L/'narration-prepared-stem.wav');stem,sr=sf.read(L/'narration-stem.wav');decoded,sr=sf.read(q/'captioned-decoded.wav');assert 1440000<=len(decoded)<=1441024;decoded=decoded[:1440000];gain=10**(read(L/'audio-build.json')['speechGainDb']/20);assert np.max(abs(stem-src*gain))<2e-6
 windows=[];flags=[]
 for i in range(0,1440000-19200,4800):
  a=stem[i:i+19200];b=decoded[i:i+19200];level=db(a)
  if level< -45:continue
  transfer=float(np.sum(a*b)/max(np.sum(a*a),1e-12));delta=20*math.log10(max(transfer,1e-9));row=dict(start=i/48000,end=(i+19200)/48000,sourceDbfs=level,encodedTransferDb=delta);windows.append(row)
  if delta< -3:flags.append(row)
 # Only continuous attenuation of >=0.5s is flagged as an induced drop.
 sustained=[]
 for i in range(len(flags)-1):
  if flags[i+1]['start']-flags[i]['start']<.101:sustained.append(flags[i])
 save(q/'audio-continuity.json',dict(constantSpeechGainVerified=True,windowSeconds=.4,stepSeconds=.1,windows=windows,attenuationCandidates=flags,sustainedAttenuationFlags=sustained,humanListening='pending'))
 assert not sustained,'Review flagged encoded speech attenuation before delivery'
 cues=read(P/'script/captions.json')['cues'];times=set(round(x*.5,3) for x in range(60))
 for c in cues:
  times.update([round(max(0,c['start']-1/60),3),round(c['start']+1/60,3),round((c['start']+c['end'])/2,3),round(c['end']-1/60,3)])
 samples=[]
 for n,t in enumerate(sorted(times)):
  image=q/f'sample-{n:03}.png';run([FF,'-v','error','-n','-ss',str(t),'-i',str(final),'-frames:v','1',str(image)]);im=Image.open(image).convert('RGB');im.resize((375,667),Image.Resampling.LANCZOS).save(q/f'mobile-{n:03}.jpg',quality=94);samples.append(dict(index=n,seconds=t,native=image.name,mobile=f'mobile-{n:03}.jpg'))
 for first in range(0,len(samples),12):
  sheet=Image.new('RGB',(1125,4*694),'#242424');d=ImageDraw.Draw(sheet)
  for j,s in enumerate(samples[first:first+12]):
   x=(j%3)*375;y=(j//3)*694;sheet.paste(Image.open(q/s['mobile']),(x,y+27));d.text((x+8,y+5),f"{s['index']:03} | {s['seconds']:.3f}s",fill='white')
  sheet.save(q/f'contact-{first//12+1:02}.jpg',quality=94)
 save(q/'samples.json',samples);save(report,dict(status='technical-pass-pixel-review-pending',files=files,seconds=30,frames=1800,speechAttenuationFlags=len(sustained),sampleCount=len(samples),wholeAsr='separate cached report',humanListening='pending'));print(json.dumps(dict(qa=str(q),samples=len(samples))))
if __name__=='__main__':globals()[sys.argv[1]]()
