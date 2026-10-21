"""Finite restoration steps for the existing private upload. No network/TTS/upload."""
import argparse,copy,os,shutil
import common as c
from PIL import ImageFont

def prepare():
 c.authorized()
 source=c.P/'production/local/revision-v2/baseline-studio-review-720p30.mp4'
 v=c.video(source);assert v['width']==1280 and v['height']==720
 audio=c.O/'baseline-audio.m4a'
 c.ff(['-i',source,'-vn','-c:a','copy',audio],'restore-audio.log')
 c.save(c.H/'restoration.json',{
  'baselineVideoId':'iv9esV7vv_g','durationSeconds':c.T['seconds'],'frames':c.T['frames'],
  'audio':{'source':c.rel(source),'sourceSha256':c.sha(source),'method':'AAC stream copy from existing Studio review download; narration performance/timing unchanged',
           'output':c.rel(audio),'sha256':c.sha(audio),'originalPcmAvailable':False,'compressedAudioRecovery':True,'newTts':False},
  'video':'Review download pixels are never production input. Restore original Manim/brand source and original FHD gameplay; reuse native Unity explanation captures.',
  'timelineSha256':c.sha(c.P/'production/timeline.json'),'originalLessonSha256':c.sha(c.R/'production/batches/game-math-part2-full-series/lessons/game-math-euler-axis-angle.json'),
  'backgroundMusic':False,'gameAudio':'Original uploaded lecture was narration-only; preserve existing audio in this visual-only polish.',
  'newOutputDirectory':'output/game-math-euler-axis-angle-private-polish','previousOutputsPreserved':True})
 geometry=c.module('polish_caption_geometry',c.P/'production/revision-v6/captions.py');geometry.O=c.O
 font=ImageFont.truetype(str(geometry.FONT),48);bold=ImageFont.truetype(str(geometry.BOLD),48)
 cues=[]
 for i,(ko,en) in enumerate(zip(c.T['koCaptions'],c.T['enCaptions'])):
  assert abs(ko['start']-en['start'])<.001 and abs(ko['end']-en['end'])<.001
  row={'id':f'original-{i+1:03}','start':ko['start'],'end':ko['end']}
  for lang,text in [('ko',ko['text']),('en',en['text'])]:
   text=text.replace('\n',' ')
   row[lang]=text;row[lang+'Lines']=geometry.wrap(text,font,bold,None);row['emphasis'+lang.title()]=None
  cues.append(row)
 for lang in ['ko','en']:
  text='\n\n'.join(f'{i+1}\n{geometry.timestamp(x["start"])} --> {geometry.timestamp(x["end"])}\n'+ '\n'.join(x[lang+'Lines']) for i,x in enumerate(cues))+'\n'
  (c.O/f'captions.{lang}.srt').write_text(text,encoding='utf8')
  geometry.ass(cues,lang)
 c.save(c.O/'caption-layout.json',{'cues':cues,'size':48,'center':[960,970],'unchangedCueTimesAndWords':True,'sourceTimelineSha256':c.sha(c.P/'production/timeline.json')})
 print('Original audio recovered;253 bilingual cues retained.',flush=True)

def flat():
 c.authorized();env=dict(os.environ,MATH_RENDER_TIMING=str(c.P/'production/timeline.json'),PYTHONIOENCODING='utf-8')
 folder=c.O/'manim';scenes=['BrandIntro','Scene01','Scene13','Scene16','Scene24','Scene25','Scene26','MemberOutro']
 for name in scenes:
  target=folder/'videos/flat-scenes/1080p60'/f'{name}.mp4'
  if not target.exists():
   c.run([c.R/'manim/.venv/Scripts/python.exe','-m','manim','--renderer','cairo','--format','mp4','-r','1920,1080','--fps','60','--media_dir',folder,str(c.H/'flat-scenes.py'),name],f'manim-{name}.log',env=env)
  sid='intro' if name=='BrandIntro' else 'outro' if name=='MemberOutro' else name[-2:]
  count=120 if sid=='intro' else 600 if sid=='outro' else c.SCENES[sid]['frames']
  dest=c.O/'clips'/f'{sid}.mp4';dest.parent.mkdir(exist_ok=True)
  if not dest.exists():c.ff(['-i',target,'-vf','fps=60,tpad=stop_mode=clone:stop_duration=0.1,setsar=1','-frames:v',count,'-an',*c.ENC,dest],f'normalize-{sid}.log')
  assert int(c.video(dest)['nb_frames'])==count
  print('Restored original code',sid,count,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','flat']);a=p.parse_args();globals()[a.stage]()
