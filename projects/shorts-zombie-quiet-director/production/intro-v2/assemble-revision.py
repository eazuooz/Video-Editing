"""Prepend the new editable intro, retaining every existing body video frame."""
from pathlib import Path
import argparse,json,hashlib,math,subprocess,importlib.util,copy,re
from PIL import ImageFont,Image,ImageDraw
import soundfile as sf
P=Path(__file__).resolve().parents[2];R=P.parents[1];L=P/'production/local/intro-v2';B=L/'baseline'
BIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin');FF=str(BIN/'ffmpeg.exe');FP=str(BIN/'ffprobe.exe')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,a):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):
 p=subprocess.run(a,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-4000:])
 return p.stdout
def norm(s):return re.sub('[^가-힣a-z0-9]','',s.lower())
def guard():
 a=read(R/'shared/publishing/video-production-control.json')['shortsRecurringAuthorization'];assert a['selectedShort']==P.name and a['latestSelection']['selectedRevision']=='zombie-quiet-intro-v2'
 record=read(P/'production/revisions/intro-v2.json')
 for rel,data in record['body'].items():assert sha(P/rel)==data['sha256'],'Retained body changed: '+rel
def load_caption_helpers():
 spec=importlib.util.spec_from_file_location('zombie_caption_helpers',P/'production/time-captions.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def timing():
 guard();m=read(P/'production/intro-v2/tts-manifest.json');voice=R/m['tts']['outputDir']/(m['tts']['filenameStem']+'.wav');asr=read(L/f'asr-intro-{sha(voice)[:12]}.json')
 text=read(P/'script/intro-v2/narration.ko.json')['scenes'][0]['lines'][0];assert norm(text)==norm(asr['text']),'Review new intro ASR before timing'
 seconds=sf.info(voice).duration;frames=math.ceil((.15+seconds+.30)*60-1e-8);intro=frames/60
 old=read(B/'script/captions.json');words=asr['chunks'];a='게임에서는 몬스터와의 전투 빈도를';b='의도적으로 조절하기도 합니다.'
 cursor=0;split=None
 for w in words:
  n=len(norm(w['text']))
  if cursor==len(norm(a)):split=float(w['timestamp'][0]);break
  cursor+=n
 assert split is not None,'Clause split must be a measured word boundary'
 stamp=lambda t:round((t+.15)*60)/60
 first=stamp(float(words[0]['timestamp'][0]));last=stamp(float(words[-1]['timestamp'][1]));mid=stamp(split)
 intro_cues=[dict(id='intro-a',lineIndex=0,spoken=a,ko='게임에서는 몬스터와의\n전투 빈도를',en='Some games control\nhow often you fight,',start=first,end=mid),dict(id='intro-b',lineIndex=0,spoken=b,ko='의도적으로\n조절하기도 합니다.',en='deliberately.',start=mid,end=last)]
 cues=intro_cues+[{**c,'lineIndex':c['lineIndex']+1,'start':(c['startFrame']+frames)/60,'end':(c['endFrame']+frames)/60,'startFrame':c['startFrame']+frames,'endFrame':c['endFrame']+frames} for c in old['cues']]
 for c in intro_cues:c.update(startFrame=round(c['start']*60),endFrame=round(c['end']*60))
 full={**old,'status':'intro-v2 timed; unchanged body shifted by exact intro frames','frames':frames+old['frames'],'durationSeconds':intro+44.2,'introFrames':frames,'introSeconds':intro,'voiceOffsetSeconds':.15,'voiceParts':[{'role':'intro','sha256':sha(voice),'destinationSeconds':.15},{'role':'retained-body','sha256':old['timingInputs']['voiceSha256'],'destinationSeconds':intro+.2}],'cues':cues}
 save(P/'script/captions.json',full)
 helpers=load_caption_helpers();font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',60)
 def srt(items,lang):
  return '\n\n'.join(f"{i}\n{helpers.stamp(c['start'])} --> {helpers.stamp(c['end'])}\n"+'\n'.join(helpers.wrap(c[lang],font)) for i,c in enumerate(items,1))+'\n'
 for lang in ['ko','en']:(L/f'captions.{lang}.srt').write_text(srt(cues,lang),encoding='utf8')
 events=[]
 for c in intro_cues:
  lines=helpers.wrap(c['ko'],font);width=max(font.getlength(x) for x in lines)+44;height=len(lines)*78+26;x=510-width/2;y=1380-height/2
  assert x>=80 and x+width<=930
  when=helpers.stamp(c['start'],True)+','+helpers.stamp(c['end'],True)
  for layer,dx,dy,col in [(10,12,12,'&H323C07&'),(11,0,0,'&HFFFFFF&')]:
   xx=x+dx;yy=y+dy;poly=f'm {xx:.1f} {yy:.1f} l {xx+width:.1f} {yy:.1f} {xx+width:.1f} {yy+height:.1f} {xx:.1f} {yy+height:.1f}'
   events.append(f'Dialogue: {layer},{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\1c{col}\\p1}}'+poly)
  for i,line in enumerate(lines):events.append(f"Dialogue: 12,{when},Text,,0,0,0,,{{\\an5\\pos(510,{1380+(i-(len(lines)-1)/2)*78:.1f})}}"+line)
 (L/'intro.ko.ass').write_text(helpers.ASS_HEADER+'\n'.join(events)+'\n',encoding='utf8')
 for lang in ['ko','en']:
  doc=read(B/f'script/narration.{lang}.json');doc['scenes']=read(P/f'script/intro-v2/narration.{lang}.json')['scenes']+doc['scenes'];doc['status']='intro-v2 locked; unchanged body PCM retained';save(P/f'script/narration.{lang}.json',doc);(P/f'script/narration.{lang}.txt').write_text('\n'.join(line for s in doc['scenes'] for line in s['lines'])+'\n',encoding='utf8')
 oldtiming=read(B/'production/visual-timing.json');sections=[dict(id='intro-v2',kind='explanation',start=0,end=intro)]+[{**s,'start':s['start']+intro,'end':s['end']+intro} for s in oldtiming['sections']]
 value=dict(revision='zombie-quiet-intro-v2',introSeconds=intro,introFrames=frames,totalSeconds=intro+44.2,totalFrames=frames+2652,voiceOffsetSeconds=.15,introVoiceSeconds=seconds,bodyOffsetSeconds=intro,sections=sections,oldBodyFrames=2652,oldBodyDurationSeconds=44.2,bodyVideoRerendered=False,bodyPcmRemixed=False,newCaptionCues=intro_cues)
 save(P/'production/intro-v2/timing.json',value);print(json.dumps(value,ensure_ascii=False))
def pair():
 guard();t=read(P/'production/intro-v2/timing.json');source=R/'shared/output/motion-canvas/shorts-zombie-quiet-director-intro-v2.mp4';intro_captioned=L/'intro-captioned.mp4'
 assert not (L/'captioned.mp4').exists()
 if not intro_captioned.exists():run([FF,'-v','error','-n','-i',str(source),'-vf','ass='+str((L/'intro.ko.ass').relative_to(R)).replace('\\','/'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-an',str(intro_captioned)])
 for name,first in [('clean',source),('captioned',intro_captioned)]:
  body=P/f'production/local/{name}.mp4';lst=L/f'{name}-concat.txt';lst.write_text("file '"+first.as_posix()+"'\nfile '"+body.as_posix()+"'\n",encoding='utf8')
  video=L/f'{name}-visual.mp4';run([FF,'-v','warning','-n','-f','concat','-safe','0','-i',str(lst),'-map','0:v:0','-an','-c:v','copy',str(video)])
  run([FF,'-v','warning','-n','-i',str(video),'-i',str(L/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(L/f'{name}.mp4')])
 save(L/'pair-build.json',dict(introFrames=t['introFrames'],totalFrames=t['totalFrames'],cleanSha256=sha(L/'clean.mp4'),captionedSha256=sha(L/'captioned.mp4'),introOnlyRendering=True,retainedBodyStreamCopy=True,aac=sha(L/'final-mix.m4a')))
def integrity():
 guard();t=read(P/'production/intro-v2/timing.json');reports=[];audios=[]
 for name in ['clean','captioned']:
  f=L/f'{name}.mp4';run([FF,'-v','error','-xerror','-i',str(f),'-f','null','-']);info=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in info['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',t['totalFrames'])
  raw=json.loads(run([FP,'-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(f)]))['frames'];pts=[float(x['best_effort_timestamp_time']) for x in raw];assert len(pts)==t['totalFrames'] and all(abs(p-i/60)<2e-6 for i,p in enumerate(pts))
  def frames(path,start=0):
   filters=f'trim=start_frame={start},setpts=PTS-STARTPTS' if start else 'null'
   data=run([FF,'-v','error','-i',str(path),'-map','0:v:0','-an','-vf',filters,'-f','framemd5','-']).decode();return [line.split(',')[-1].strip() for line in data.splitlines() if line and not line.startswith('#')]
  old=frames(P/f'production/local/{name}.mp4');retained=frames(f,t['introFrames']);assert old==retained,'Body decoded pixels changed'
  aac=run([FF,'-v','error','-i',str(f),'-map','0:a:0','-c','copy','-f','adts','pipe:1']);audios.append(hashlib.sha256(aac).hexdigest());reports.append(dict(name=name,sha256=sha(f),frames=len(pts),regularPts60=True,decoded=True,retainedBodyFrameHashesIdentical=True,format=info['format']))
 assert audios[0]==audios[1];save(L/'integrity.json',dict(status='pass',outputs=reports,identicalAac=True,aacHash=audios[0],body2652DecodedFramesPreserved=True))
def qa():
 t=read(P/'production/intro-v2/timing.json');out=L/'qa';out.mkdir(exist_ok=True);times=sorted(set([.2,t['introSeconds']*.32,t['introSeconds']*.52,t['introSeconds']*.8,t['introSeconds']-.03,t['introSeconds']+.05,t['introSeconds']+.7]+[(c['start']+c['end'])/2 for c in t['newCaptionCues']]))
 sheet=Image.new('RGB',(375*3,700*math.ceil(len(times)/3)),'#242424');draw=ImageDraw.Draw(sheet)
 for i,when in enumerate(times):
  f=out/f'frame-{i:02}.png';run([FF,'-v','error','-n','-ss',str(when),'-i',str(L/'captioned.mp4'),'-frames:v','1',str(f)]);im=Image.open(f).convert('RGB');im.thumbnail((375,666));x=i%3*375;y=i//3*700;sheet.paste(im,(x,y));draw.text((x+4,y+670),f'{when:.3f}s',fill='white')
 sheet.save(out/'intro-and-join.jpg',quality=94);save(out/'index.json',dict(times=times,scope='new intro and join; full retained body pixel equality permits prior26cue/motion evidence reuse'))
def main():
 a=argparse.ArgumentParser();a.add_argument('command',choices=['timing','pair','integrity','qa']);globals()[a.parse_args().command]()
if __name__=='__main__':main()
