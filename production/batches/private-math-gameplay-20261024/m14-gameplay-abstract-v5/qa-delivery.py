"""Changed-frame / stream / source-motion / preservation checks for M14 v5."""
from pathlib import Path
import json,subprocess,importlib.util,io,re
from PIL import Image,ImageChops,ImageStat,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',B.parent/'render-patches.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
slug='game-math-polygon-partition-v2';P=R/'projects'/slug;H=P/'production/gameplay-abstract-v5';O=P/'production/local/gameplay-abstract-v5';Q=R/'shared/output/private-math-gameplay-20261024/m14-v5/final-qa';Q.mkdir(parents=True,exist_ok=True)
plan=m.read(H/'plan.json');out=m.read(H/'outputs.json');dur=plan['introSeconds'];checks=[]
for row in out['outputs']:
 f=R/row['path'];assert m.sha(f)==row['sha256']
 if f.suffix=='.mp4':
  p=m.probe(f);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
  assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1' and int(v['nb_frames'])==plan['totalFrames']
  assert abs(float(v['duration'])-plan['seconds'])<1/60+.001 and a['sample_rate']=='48000'
  log=Q/(f.stem+'.decode.log');m.ff(['-v','error','-i',f,'-f','null','-'],log,Q);assert not log.read_text('utf8').strip()
  row=dict(row,frames=int(v['nb_frames']),seconds=float(v['duration']),fullDecodePassed=True)
 checks.append(row)
def parse_srt(p):
 out=[]
 for b in p.read_text('utf-8-sig').strip().split('\n\n'):
  r=b.splitlines();out.append((r[1],'\n'.join(r[2:])))
 return out
for lang in ['ko','en']:
 a=parse_srt(R/f'output/{slug}-gameplay-motion-v4/{slug}.{lang}.srt');b=parse_srt(R/f'output/{slug}-gameplay-abstract-v5/{slug}.{lang}.srt')
 assert [x[1] for x in b[len(plan['introCues']):]]==[x[1] for x in a]
audio=m.read(H/'audio-preservation.json');assert audio['bodySamplesUnchangedBeforeEncoding'];assert m.sha(P/'production/local/concept-fit-v2/audio/narration-matched.wav')==audio['originalNarrationSha256']
clean=next(x['path'] for x in checks if x['path'].endswith('.clean.mp4'));cap=next(x['path'] for x in checks if x['path'].endswith('.captioned.mp4'))
def frame(path,t,crop=None,size=(256,144)):
 vf=('crop='+':'.join(map(str,crop))+',' if crop else '')+f'scale={size[0]}:{size[1]}'
 data=subprocess.check_output(['ffmpeg','-v','error','-nostdin','-ss',str(t),'-i',str(R/path),'-frames:v','1','-vf',vf,'-f','image2pipe','-vcodec','png','pipe:1'])
 return Image.open(io.BytesIO(data)).convert('RGB')
def mae(a,b):return sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
native=[]
for b in plan['beats']:
 for dt in [.5,b['seconds']/2,b['seconds']-.3]:
  a=frame(b['source'],b['sourceIn']+dt,crop=(1920,740,0,145) if b['sourceKey']=='dorf' else (2560,986,0,193))
  z=frame(cap,2+b['start']+dt,crop=(1920,740,0,145));err=mae(a,z)
  native.append(dict(scene='abstract-'+b['id'],masterTime=2+b['start']+dt,sourceTime=b['sourceIn']+dt,mae=err))
e=m.read(H/'source-evidence.json');p=plan['patch'];pstart=p['oldStart']+dur
for dt in [.5,3,5,7,9,12.4]:
 a=frame(e['source'],e['inSeconds']+dt,crop=(960,540,0,300));z=frame(cap,pstart+dt,crop=(1280,720,0,130));native.append(dict(scene='QG06',masterTime=pstart+dt,sourceTime=e['inSeconds']+dt,mae=mae(a,z)))
assert max(r['mae'] for r in native)<25,native
preserved=[]
for t in [0.8,2.2,40,85,170,285,381.8,395.8,430,540,650,665]:
 dst=t if t<2 else t+dur;e1=mae(frame(plan['bodySource'],t),frame(clean,dst));preserved.append(dict(originalTime=t,newTime=dst,mae=e1));assert e1<4,(t,e1)
# Four sampled frames/second, source-versus-output changes. Source-native rests
# are distinguished from an added cloned-frame interval.
motion=[]
clips=[dict(id='QG06',file=cap,start=pstart,source=e['source'],sourceStart=e['inSeconds'],seconds=13,fcrop=(1280,720,0,130),scrop=(960,540,0,300))]
for b in plan['beats']:
 clips.append(dict(id='abstract-'+b['id'],file=cap,start=2+b['start'],source=b['source'],sourceStart=b['sourceIn'],seconds=b['seconds'],fcrop=(1920,740,0,145),scrop=(1920,740,0,145) if b['sourceKey']=='dorf' else (2560,986,0,193)))
def seq(path,t,seconds,crop):
 vf='crop='+':'.join(map(str,crop))+',fps=4,scale=128:72,format=gray'
 raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(R/path),'-t',str(seconds),'-vf',vf,'-f','rawvideo','pipe:1']);return [Image.frombytes('L',(128,72),raw[i:i+9216]) for i in range(0,len(raw)-9215,9216)]
for c in clips:
 a=seq(c['source'],c['sourceStart'],c['seconds'],c['scrop']);z=seq(c['file'],c['start'],c['seconds'],c['fcrop']);n=min(len(a),len(z));flags=[]
 for i in range(1,n):
  sa=sum(ImageStat.Stat(ImageChops.difference(a[i-1],a[i])).mean);sz=sum(ImageStat.Stat(ImageChops.difference(z[i-1],z[i])).mean)
  if sa>1 and sz<.1:flags.append(i/4)
 assert not flags,(c['id'],flags)
 motion.append(dict(scene=c['id'],sampledFrames=n,addedFreezeFlags=flags))
# Actual final-resolution frames and 375px mobile versions for agent inspection.
times=[('abstract-A',4.3),('abstract-B',2+plan['beats'][1]['start']+1.3),('abstract-C',2+plan['beats'][2]['start']+plan['beats'][2]['seconds']-.8),('intro-body-join',2+dur+.4),('cut',pstart+2),('rotation',pstart+5.5),('result',pstart+10.5),('return',pstart+13.4)]
items=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);sheet=Image.new('RGB',(750,260*4),'#101412');draw=ImageDraw.Draw(sheet)
for i,(name,t) in enumerate(times):
 im=frame(cap,t,size=(1920,1080));f=Q/(name+'.png');im.save(f);small=im.resize((375,211));small.save(Q/(name+'-375.png'));x=i%2*375;y=i//2*260;sheet.paste(small,(x,y+26));draw.text((x+5,y+3),f'{name} {t:.2f}s',font=font,fill='white');items.append(dict(name=name,time=t,path=m.rel(f)))
sheet.save(Q/'mobile-sheet.png')
m.save(H/'technical-qa.json',dict(checks=checks,bodyNarrationSourceHashPreserved=True,bodyCaptionTextPreservedBothLanguages=True,bodyFrameComparisons=preserved,nativeComparisons=native,motionChecks=motion,freezePaddingSeconds=0,actualWholeListening=False,continuousPlayback=False,humanReview='pending',frames=items,visualInspection='pending'))
print(json.dumps(dict(seconds=plan['seconds'],frames=plan['totalFrames'],nativeMaxMae=max(r['mae'] for r in native),preservedMaxMae=max(r['mae'] for r in preserved),mobile=m.rel(Q/'mobile-sheet.png')),ensure_ascii=False),flush=True)
