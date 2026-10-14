"""Current one-guide change, measured KO/EN captions and retained frame geometry."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import ImageFont
import json,hashlib,copy,subprocess,psutil,math
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(R).as_posix()
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
sp=P/'part1-selected-guide-direct-review-v287.json';s=rd(sp);assert s['selectedForPrivateTechnicalProduction']
job=rd(R/'production/research/game-lighting-history/local/part1-selected-guide-v287/plan.json')['jobs'][0]
execution=rd(R/job['execution']);assert execution['exitCode']==0 and execution['status']=='complete'
assert not psutil.pid_exists(execution['ffmpegPid'])
video=R/job['output'];probe=json.loads(subprocess.run([str(FP),'-v','error','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,nb_read_frames','-of','json',str(video)],capture_output=True,text=True,check=True).stdout)
v=next(x for x in probe['streams'] if x['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',413)
decode=subprocess.run([str(FF),'-v','error','-nostdin','-threads','2','-i',str(video),'-f','null','NUL'],capture_output=True,text=True,check=True)
oldp=P/'part1-final-input-plan-v240.json';old=rd(oldp);new=copy.deepcopy(old)
row=next(x for x in new['paragraphs'] if x['id']=='outer-comparison-before');row['ko']=s['ko'];row['en']=s['en'];row['pcm']={k:s['selectedTake'][k] for k in ['path','sha256','sampleRate','samples']}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
texts={'ko':[s['ko'].split('. ')[0]+'.',s['ko'].split('. ')[1]],'en':['Reconstruction quality and\ndisplay frequency are different.','In The Outer Worlds, we inspect\nthe frame-generation multiplier.']}
times=[(0,132),(142,332)]
for lang in ['ko','en']:
 for i,c in enumerate(row[lang+'Cues']):
  c.update(text=texts[lang][i],fromFrame=44915+times[i][0],toFrame=44915+times[i][1])
  if lang=='ko':
   width=font.getlength(c['text']);assert width+44<=1340
   c.update(lineWidths=[width],boxWidth=math.ceil(width+44),from_=None)
   c.pop('from_',None);c['from']=times[i][0]/60;c['to']=times[i][1]/60
   c['sourceCharacters']=[0,len(texts['ko'][0])] if i==0 else [len(texts['ko'][0])+1,len(s['ko'])]
   c['recognizerWordIndices']=[0,4] if i==0 else [5,10]
   c.update(timingDirectlyReviewed=True,pixelsReviewed=False,wordAnchorEvidence='v286 raw full11 word timestamps; cue ends include natural tail')
  index=next(k for k,x in enumerate(new[lang+'Cues']) if x['id']==c['id']);new[lang+'Cues'][index]=copy.deepcopy(c)
cut=next(x for x in new['cuts'] if x['fromFrame']==44915);cut['video']={'path':rel(video),'sha256':sha(video)};cut['sourceStartFrame']=0;cut['pcm']={**row['pcm'],'firstSample':0,'exclusiveEndSample':132480};cut['preserveFullPcm']=True
unchanged=[p['id'] for p,q in zip(old['paragraphs'],new['paragraphs']) if p==q];assert len(unchanged)==76
assert len([1 for p,q in zip(old['cuts'],new['cuts']) if p==q])==93
for k in ['actualFrames','explanationFrames','bodyFrames','finalFrames','ratioErrorFrames','chapterRanges','branding','membership']:assert new[k]==old[k]
new.update(preparedAt=datetime.now(timezone.utc).isoformat(),currentGuideReplacement={'selection':{'path':rel(sp),'sha256':sha(sp)},'oldPlan':{'path':rel(oldp),'sha256':sha(oldp)},'changedGuide':row['id'],'unchanged76Paragraphs':unchanged,'allOriginal36ParagraphsAndPcmUnchanged':True,'allOther93CutFramesUnchanged':True,'preservedExplanationFrames':413,'newVoiceSamples':132480,'intentionalComparisonReadHoldFrames':81,'wholeSourceRender':{'path':rel(video),'sha256':sha(video),'probe':probe,'wholeDecodeExitCode':0},'allCurrentGuideMovingPixelsReviewed':False},allFinalPixelsReviewed=False,finalMixedAsrApproved=False)
new['bindings'].append({'path':rel(sp),'sha256':sha(sp)})
dest=P/'part1-final-input-plan-v288.json';assert not dest.exists();dest.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n','utf-8')
script=R/'production/research/game-lighting-history/prepare-part1-captions-v288.py';assert not script.exists();script.write_text((R/'production/research/game-lighting-history/prepare-part1-captions-v243.py').read_text('utf-8-sig').replace('input-plan-v240','input-plan-v288').replace('part1-captions-v243','part1-captions-v288').replace('caption-layout-v243','caption-layout-v288'),'utf-8')
subprocess.run([__import__('sys').executable,'-X','utf8',str(script)],cwd=R,check=True)
print(json.dumps({'finalPlan':rel(dest),'sha256':sha(dest),'original36Retained':True,'retainedOtherCuts':93,'totalFrames':89148,'currentGuideDecode':0,'newVoiceSeconds':5.52}))
