"""Two full lectures: measured narration, exact40:60, no music, retained sample.

Reuse the reviewed caption geometry/decode QA from the sample without editing it.
"""
from pathlib import Path
import sys,importlib.util,json,math,shutil
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]
slug=sys.argv[1];stage=sys.argv[2]
spec=importlib.util.spec_from_file_location('caption_tools',ROOT/'projects/game-math-polar-sample/production/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.BASE=ROOT/'projects'/slug;b.WORK=ROOT/'shared/output'/slug;b.MC=ROOT/'motion-canvas/src/projects'/slug;b.MF=b.BASE/'project.json';b.WORK.mkdir(parents=True,exist_ok=True)
BASE=b.BASE;WORK=b.WORK;MC=b.MC;FPS=60
D=b.read(Path(__file__).parent/('lesson-data.json' if slug.endswith('2d') else 'part2-data.json'))[slug]
def plan():
 m=b.read(b.MF);out=ROOT/m['tts']['outputDir'];tim=b.read(out/(m['tts']['filenameStem']+'.timing.json'));assert tim.get('alignment')
 raw={};minimum={};groups={k:[s['id'] for s in D['scenes'] if s['kind']==k] for k in ['actual','explanation']}
 for s in D['scenes']:
  f=out/'chunks'/f'{s["id"]}-scene.wav';a,sr=sf.read(f,dtype='float32');assert sr==24000 and a.ndim==1
  raw[s['id']]=(a,sr,f);minimum[s['id']]=math.ceil((len(a)/sr+.6)*FPS)
 body=math.ceil(max(sum(minimum[i] for i in groups['actual'])/.4,sum(minimum[i] for i in groups['explanation'])/.6)/5)*5
 frames=minimum.copy()
 for kind,share in [('actual',.4),('explanation',.6)]:
  ids=groups[kind];target=round(body*share)
  while sum(frames[i] for i in ids)<target:
   eligible=[i for i in ids if kind!='actual' or frames[i]<math.floor(next(s['maxSeconds'] for s in D['scenes'] if s['id']==i)*FPS)]
   assert eligible,'Secure more reviewed footage rather than looping or slowing a clip'
   key=min(eligible,key=lambda i:frames[i]/minimum[i]);frames[key]+=1
 scenes=[];start=2;voice=np.zeros(round((body/FPS+12)*24000),dtype='float32')
 cuts=b.read(BASE/'sources/gameplay-cuts.json')
 for s in D['scenes']:
  i=s['id'];a,sr,f=raw[i];entries=[e for e in tim['entries'] if e['scene_id']==i];origin=entries[0]['start']
  cues=[{'start':e['start']-origin,'end':e['end']-origin,'text':e['text'],'line':e.get('line_index')} for e in entries]
  slot={'id':i,'title':s['title'],'start':start,'frames':frames[i],'seconds':frames[i]/FPS,'voice':b.rel(f),'voiceSeconds':len(a)/sr,'voiceSha256':b.sha(f),'rawOrigin':origin,'cues':cues,'lineStarts':[e['start']-origin for e in entries],'classification':s['kind'],'manimClass':'Scene'+i if s['kind']=='explanation' else None}
  if s['kind']=='actual':
   cut=next(c for c in cuts['cuts'] if c['scene']==i);cut['duration']=slot['seconds'];assert cut['duration']<=cut['maxSeconds'],(i,slot['voiceSeconds'],cut['maxSeconds']);slot['cut']=cut
   source_segments=cut.get('sourceSegments')
   if source_segments and frames[i]>math.floor(source_segments[0]['maxSeconds']*FPS):
    assert len(source_segments)==2
    hint=slot['lineStarts'][min(cut.get('switchLine',3),len(slot['lineStarts'])-1)]
    lower=frames[i]-math.floor(source_segments[1]['maxSeconds']*FPS);upper=math.floor(source_segments[0]['maxSeconds']*FPS)
    first=max(lower,min(upper,round(hint*FPS)));counts=[first,frames[i]-first]
    cut['segments']=[{**x,'frames':count,'seconds':count/FPS} for x,count in zip(source_segments,counts)]
   else:cut['segments']=[{'in':cut['in'],'maxSeconds':source_segments[0]['maxSeconds'] if source_segments else cut['maxSeconds'],'frames':frames[i],'seconds':slot['seconds']}]
  scenes.append(slot);at=round(start*sr);voice[at:at+len(a)]=a;start+=slot['seconds']
 p={'fps':60,'frames':body+720,'seconds':body/60+12,'bodyFrames':body,'bodySeconds':body/60,'actualFrames':round(body*.4),'explanationFrames':round(body*.6),'actualShare':.4,'explanationShare':.6,'introSeconds':2,'outroSeconds':10,'scenes':scenes,'backgroundMusic':False}
 sf.write(ROOT/m['paths']['narration'],voice,24000)
 for lang in ['ko','en']:
  final=[]
  for c in b.parse_srt(BASE/f'script/voice-aligned.{lang}.srt'):
   s=next(s for s in reversed(scenes) if c['start']>=s['rawOrigin']-.004)
   final.append({**c,'start':s['start']+c['start']-s['rawOrigin'],'end':s['start']+c['end']-s['rawOrigin'],'scene':s['id']})
  p[lang+'Captions']=final;b.write(ROOT/m['paths']['captions'+lang.title()],b.srt(final))
 assert [(c['start'],c['end']) for c in p['koCaptions']]==[(c['start'],c['end']) for c in p['enCaptions']]
 b.write(BASE/'sources/gameplay-cuts.json',cuts);b.write(BASE/'production/timeline.json',p)
 m['video']['durationSeconds']=p['seconds'];m['editing'].update(actualGameplaySeconds=p['actualFrames']/60,actualExplanationSeconds=p['explanationFrames']/60,actualGameplayShare=.4,actualCommercialGameplaySeconds=p['actualFrames']/60,actualDevelopmentFootageSeconds=0,actualPrototypeExplanationSeconds=0,timingStatus='measured-speech-and-aligned-bilingual-cues',finalBodyFrames={'total':body,'actual':p['actualFrames'],'explanation':p['explanationFrames'],'ratioErrorFrames':0})
 m['editing']['openingOverview']['narrationSeconds']=scenes[0]['voiceSeconds'];b.write(b.MF,m);records()
 print(json.dumps({'slug':slug,'seconds':p['seconds'],'actualSeconds':p['actualFrames']/60,'explanationSeconds':p['explanationFrames']/60,'cueCount':len(p['koCaptions']),'slots':[(s['id'],s['seconds'],s['voiceSeconds']) for s in scenes]}),flush=True)
def records():
 p=b.read(BASE/'production/timeline.json');scenes=p['scenes']
 for s in scenes:
  if s.get('cut'):
   c=s['cut'];s['cuts']=[];offset=0
   for seg in c['segments']:
    s['cuts'].append({'source':c['sourceFile'],'sourceIn':seg['in'],'sourceOut':seg['in']+seg['seconds'],'outputStart':s['start']+offset,'durationSeconds':seg['seconds'],'frames':seg['frames'],'classification':'actual-existing-game','sourceAudioUsed':False});offset+=seg['seconds']
 b.write(BASE/'production/timeline.json',p)
 b.write(MC/'timing.ts',f'export const TOTAL_DURATION={p["seconds"]};\nexport const TOTAL_FRAMES={p["frames"]};\nexport const SCENE_STARTS={json.dumps([s["start"] for s in scenes])} as const;\nexport const SCENE_DURATIONS={json.dumps([s["seconds"] for s in scenes])} as const;\n')
 b.write(BASE/'audio/mix-report.md',f'# 내레이션 전용 강의\n\nBGM 없음. 입력은 승인된 Qwen 내레이션 WAV 하나뿐이며 게임 원음·OST·Nimbus를 혼합하지 않는다.48kHz stereo AAC, 목표-16LUFS/true peak≤-1.5dBTP. 전체{p["seconds"]:.3f}초. 사람의 전체 청취 승인 대기.\n')
def render():
 vdir=WORK/'manim/videos/scene/1080p60';vdir.mkdir(parents=True,exist_ok=True)
 original=ROOT/'shared/output/game-math-polar-sample/manim/videos/scene/1080p60'
 for cls in ['BrandIntro','MemberOutro']:shutil.copy2(original/(cls+'.mp4'),vdir/(cls+'.mp4'))
 slots=b.read(BASE/'production/timeline.json')['scenes'];records=b.read(WORK/'render-receipts.json') if (WORK/'render-receipts.json').exists() else {}
 classes=[]
 for s in slots:
  if s['classification']!='explanation':continue
  target=vdir/(s['manimClass']+'.mp4');r=records.get(s['id'],{})
  current=(r.get('voiceSha256')==s['voiceSha256'] and r.get('lessonSha256')==b.sha(ROOT/'manim/projects/game-math-polar-lecture/lesson.py') and r.get('dataSha256')==b.sha(Path(__file__).parent/('lesson-data.json' if slug.endswith('2d') else 'part2-data.json')))
  if target.exists() and current:
   stream=next(v for v in b.probe(target)['streams'] if v['codec_type']=='video')
   if int(stream['nb_frames'])>=s['frames']-1:print('Reusing current validated',s['manimClass'],flush=True);continue
  classes.append(s['manimClass'])
 if not classes:print('All independent explanation scenes are current');return
 b.run([sys.executable,'-m','manim','-qh','--disable_caching','--media_dir',WORK/'manim',ROOT/f'manim/projects/{slug}/scene.py',*classes],'manim-render.log')
 print('Rendered',len(classes),'independent explanation scenes',flush=True)
def assemble(reuse=False):
 m=b.read(b.MF);p=b.read(BASE/'production/timeline.json');vdir=WORK/'manim/videos/scene/1080p60';clipdir=WORK/'clips';clipdir.mkdir(exist_ok=True);assets=MC/'assets';assets.mkdir(exist_ok=True);clips=[]
 for sid,cls,count in [('intro','BrandIntro',120),*[(s['id'],s['manimClass'],s['frames']) for s in p['scenes']],('outro','MemberOutro',600)]:
  target=clipdir/(sid+'.mp4')
  if not reuse:
   if cls:
    source=vdir/(cls+'.mp4');v=next(x for x in b.probe(source)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])>=count-1,(cls,v['nb_frames'],count)
    b.ff(['-i',source,'-vf','fps=60,setsar=1,tpad=stop_mode=clone:stop_duration=0.05','-frames:v',str(count),*b.ENC,target],f'clip-{sid}.log')
   else:
    s=next(s for s in p['scenes'] if s['id']==sid);c=s['cut'];credit=c.get('credit','Brotato - MezzyGameplay')
    source_id='eDL84EC5mkQ' if slug.endswith('2d') else 'WJVRoLR6KvY'
    credit_line=credit+' | CC BY | edited excerpt, muted'
    source_line='youtu.be/'+source_id+' | creativecommons.org/licenses/by/4.0'
    vf="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='"+credit_line+"':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=808,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='"+source_line+"':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=834"
    segments=c['segments'];pieces=[]
    for j,seg in enumerate(segments):
     piece=target if len(segments)==1 else clipdir/f'{sid}-source-{j+1}.mp4'
     b.ff(['-ss',str(seg['in']),'-i',ROOT/c['sourceFile'],'-vf',vf,'-frames:v',str(seg['frames']),*b.ENC,piece],f'clip-{sid}-source-{j+1}.log');pieces.append(piece)
    if len(pieces)>1:
     listing=clipdir/f'{sid}-concat.txt';b.write(listing,'\n'.join("file '"+f.as_posix()+"'" for f in pieces)+'\n')
     b.ff(['-f','concat','-safe','0','-i',listing,'-c:v','copy','-an','-movflags','+faststart',target],f'clip-{sid}-concat.log')
  v=next(x for x in b.probe(target)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==count and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1'
  clips.append(target);shutil.copy2(target,assets/f'{sid}.mp4');print('Verified',sid,count,'frames',flush=True)
 # Exactly one audio input. No music file, amix, loop, game audio or sidechain.
 lv=b.loudness(ROOT/m['paths']['narration'],-16,-1.7)
 f=f'loudnorm=I=-16:TP=-1.7:LRA=11:measured_I={lv["input_i"]}:measured_TP={lv["input_tp"]}:measured_LRA={lv["input_lra"]}:measured_thresh={lv["input_thresh"]}:offset={lv["target_offset"]}:linear=true,aresample=48000,aformat=channel_layouts=stereo'
 b.ff(['-i',ROOT/m['paths']['narration'],'-af',f,'-c:a','pcm_s16le',ROOT/m['paths']['editorAudioMix']],'narration-only-master.log')
 b.ff(['-i',ROOT/m['paths']['editorAudioMix'],'-c:a','aac','-b:a','192k',ROOT/m['paths']['audioMix']],'audio-aac.log')
 measure=b.loudness(ROOT/m['paths']['audioMix'],-16,-1.5)
 # Measure the encoded stereo delivery, then correct only its measured gain.
 # Mono-to-stereo conversion and AAC can change the first-pass LUFS result.
 corrections=[]
 for attempt in range(2):
  if abs(float(measure['input_i'])+16)<=.35:break
  gain=-16-float(measure['input_i']);assert abs(gain)<=6 and float(measure['input_tp'])+gain<=-1.7,measure
  pcm=ROOT/m['paths']['editorAudioMix'];corrected=WORK/'narration-gain-corrected.wav'
  b.ff(['-i',pcm,'-af',f'volume={gain}dB','-c:a','pcm_s16le',corrected],f'narration-gain-{attempt+1}.log');shutil.copy2(corrected,pcm)
  b.ff(['-i',pcm,'-c:a','aac','-b:a','192k',ROOT/m['paths']['audioMix']],f'audio-aac-gain-{attempt+1}.log')
  corrections.append({'encodedBefore':measure,'gainDb':gain});measure=b.loudness(ROOT/m['paths']['audioMix'],-16,-1.5)
 assert abs(float(measure['input_i'])+16)<=.65 and float(measure['input_tp'])<=-1.45,measure
 # Verify that the un-narrated branding and outro remain silent in the PCM mix.
 audio,sr=sf.read(ROOT/m['paths']['editorAudioMix']);assert np.max(np.abs(audio[:int(1.8*sr)]))==0 and np.max(np.abs(audio[-int(9*sr):]))==0
 b.write(BASE/'audio/mix-measurements.json',{'voiceInput':lv,'encodedGainCorrections':corrections,'final':measure,'audioInputs':[m['paths']['narration']],'backgroundMusic':False,'sourceAudioUsed':False,'brandingOutroSilenceVerified':True,'humanListening':'pending','seconds':p['seconds']})
 b.write(WORK/'concat.txt','\n'.join("file '"+f.as_posix()+"'" for f in clips)+'\n')
 b.ff(['-f','concat','-safe','0','-i',WORK/'concat.txt','-i',ROOT/m['paths']['audioMix'],'-map','0:v','-map','1:a','-c','copy','-t',str(p['seconds']),'-movflags','+faststart',ROOT/m['paths']['videoClean']],'final-clean.log')
 print('Full lecture assembled with narration only',flush=True)
def qa():
 b.qa();q=b.read(BASE/'production/qa.json');q.update(rightsReview='Uploader CC metadata checked; game-IP review pending before public publication',upload='Private upload authorized; platform settings not verified yet',backgroundMusic=False,narrationOnlyMix=b.read(BASE/'audio/mix-measurements.json'));b.write(BASE/'production/qa.json',q)
stages={'plan':plan,'records':records,'render':render,'assemble':assemble,'mix':lambda:assemble(True),'burn':b.burn,'qa':qa}
stages[stage]()
