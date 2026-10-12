"""Repair evidenced native inputs, keeping the sealed timeline."""
from pathlib import Path
import importlib.util, json, copy, psutil
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v240.json';plan=m.read(PP)
OP=P/'part1-input-overrides-v249.json';overrides=m.read(OP)
assert overrides['inputPlan']['sha256']==m.sha(PP)
assert overrides['timelineEquivalence']['sameParagraphsPcmMixCaptionsAndChapters']
sourceReview=m.read(P/'part1-native-overrides-direct-review-v249.json')
assert sourceReview['overridesSha256']==m.sha(OP) and sourceReview['allSelectedSourcesNormalPlaybackDirectlyReviewed']
asr=m.read(P/'part1-final-mixed-asr-execution-v243.json')
assert asr['status']=='complete' and asr['exitCode']==0, 'Preserve the single CPU ASR until it completes.'
for proc in psutil.process_iter(['pid','name','cmdline','create_time']):
 d=proc.info
 if any(t in ' '.join(d['cmdline'] or []) for t in ['review-part1-final-mix-v243.py','review-part1-artifact-contexts-v255.py']) and (d['name'] or '').lower().startswith('python'):
  raise RuntimeError('Actual mixed-ASR worker is still alive; no overlapping media job.')
BP=P/'part1-final-visual-build-v245.json';baseline=m.read(BP)
assert baseline['planSha256']==m.sha(PP) and baseline['wholeDecodeExitCode']==0
OUT=R/'production/research/game-lighting-history/local/part1-native-pixels-v250'
SP=P/'part1-native-pixels-execution-v250.json';assert not SP.exists() and not OUT.exists()
resources=m.resources();OUT.mkdir(parents=True)
state={'startedAt':m.stamp(),'status':'running','worker':m.worker(),'active':None,'commands':[],'results':[],
 'resourceObservation':resources,'planSha256':m.sha(PP),'overridesSha256':m.sha(OP),'baselineBuildSha256':m.sha(BP),
 'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False}
m.save(SP,state)
def checkpoint():
 p=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(p)
 j['episode04Part1NativePixelRepairV250']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'results':len(state['results']),'finalApproved':False}
 j['ownedActiveWork']={'type':'part1-observed-native-pixel-repair','execution':m.rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Direct corrected moving pixels and complete current mixed-ASR comparison'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Direct corrected moving pixels and current mixed-ASR approval'}
 j['updatedAt']=m.stamp();m.save(p,j)
def run(args,label):
 checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
def label_filter(text,name,x=32,y=22,size=28):
 p=OUT/(name+'.txt');p.write_text(text,'utf8')
 return f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(p)}':expansion=none:x={x}:y={y}:fontsize={size}:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
def encode_piece(c,index,source,start,frames,tracking,piece,offset):
 rect=c.get('cropRect');vf=([f'crop={rect[2]}:{rect[3]}:{rect[0]}:{rect[1]}'] if rect else [])+['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black','setsar=1','fps=60','setpts=PTS-STARTPTS']
 matte=c.get('captionMatteHeight',0)
 if matte:vf.extend([f'crop=1920:{1080-matte}:0:{0 if tracking and tracking.get("matteFrom")=="bottom" else matte}','pad=1920:1080:0:0:black'])
 vf.extend([f'trim=end_frame={frames}','settb=1/90000','setpts=N*1500'])
 for k,t in enumerate([c['identityLabel'],c.get('onScreenConditionLabel')]):
  if t:vf.append(label_filter(t,f'cut-{index}-piece-{piece}-condition-{k}',y=22+42*k,size=28 if k==0 else 24))
 if tracking:vf.append(label_filter(tracking['label'],f'cut-{index}-target',x=tracking['labelX'],y=tracking['labelY'],size=28))
 boxes=[b for b in (tracking or {}).get('boxes',[]) if b['from']<offset+frames/60 and b['to']>offset]
 if boxes:
  graph=['[0:v]'+','.join(vf)+'[base0]']
  for k,b in enumerate(boxes):
   duration=b['to']-b['from'];x=f"{b['x0']}+({b['x1']-b['x0']})*(t+{offset}-{b['from']})/{duration}";y=f"{b['y0']}+({b['y1']-b['y0']})*(t+{offset}-{b['from']})/{duration}"
   graph.append(f"color=c=black@0:s={b['width']}x{b['height']}:r=60:d={frames/60:.9f},format=rgba,drawbox=x=0:y=0:w=iw:h=ih:color={b['color']}:t=4:replace=1,settb=1/90000,setpts=N*1500[box{k}]")
   graph.append(f"[base{k}][box{k}]overlay=x='{x}':y='{y}':eval=frame:format=yuv420:shortest=1:enable='gte(t,{b['from']-offset})*lt(t,{b['to']-offset})'[base{k+1}]")
  filters=['-filter_complex_threads','2','-filter_complex',';'.join(graph),'-map',f'[base{len(boxes)}]']
 else:filters=['-filter_threads','2','-vf',','.join(vf),'-map','0:v:0']
 file=OUT/f'cut-{index:03d}-piece-{piece}.mp4'
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-reinit_filter','0','-ss',f'{start:.9f}','-i',source,*filters,'-frames:v',str(frames),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',file],f'repair-{index:03d}-piece-{piece}')
 proof=m.verify_video(file,frames,state,SP,OUT,f'verify-{index:03d}-piece-{piece}')
 return file,proof
def repair(c,index):
 source=R/c['video']['path'];assert m.sha(source)==c['video']['sha256']
 change=overrides['changes'][c['id']];tracking=change.get('tracking');proofs=[];pieces=[];offset=0
 for k,cut in enumerate(c['proposedCuts']):
  frames=cut['outFrame']-cut['inFrame'];file,proof=encode_piece(c,index,source,cut['inFrame']/60,frames,tracking,k,offset)
  pieces.append(file);proofs.append(proof);offset+=frames/60
 assert round(offset*60)==c['frames']
 if len(pieces)>1:
  concat=OUT/f'cut-{index:03d}.concat.txt';concat.write_text('\n'.join("file '"+str(x).replace('\\','/')+"'" for x in pieces)+'\n','utf8');file=OUT/f'cut-{index:03d}.mp4'
  run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',file],f'join-{index:03d}')
 return file,{'id':c['id'],'path':m.rel(file),'sha256':m.sha(file),'frames':c['frames'],'kind':c['kind'],'fromFrame':c['fromFrame'],'toFrame':c['toFrame'],'reusedByteIdentical':False,'repair':change['reason'],'sourceCuts':c['proposedCuts'],'captionMatteHeight':c.get('captionMatteHeight',0),'editableTracking':tracking,'technicalProofs':proofs}
try:
 files=[R/plan['branding']['path']];repairs=[];oldmap={q['id']:q for q in baseline['cuts']}
 for index,c in enumerate(overrides['effectiveCuts'],1):
  old=oldmap[c['id']];assert m.sha(R/old['path'])==old['sha256']
  if c['id'] in overrides['changes']:file,row=repair(c,index);repairs.append(row)
  else:file=R/old['path'];row={**old,'retainedByteIdenticalToV245':True}
  files.append(file);state['results'].append(row);checkpoint()
 assert len(repairs)==len(overrides['changes']) and len(state['results'])==94;files.append(R/plan['membership']['path'])
 concat=OUT/'master.concat.txt';concat.write_text('\n'.join("file '"+str(x).replace('\\','/')+"'" for x in files)+'\n','utf8');visual=OUT/'silent-visual.mp4'
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',visual],'master-concat')
 technical=m.verify_video(visual,plan['finalFrames'],state,SP,OUT,'master')
 proof={'builtAt':m.stamp(),'planSha256':m.sha(PP),'path':m.rel(visual),'sha256':m.sha(visual),'frames':plan['finalFrames'],'cuts':state['results'],'effectiveCuts':overrides['effectiveCuts'],'inputOverrides':{'path':m.rel(OP),'sha256':m.sha(OP)},'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'repairs':repairs,'retainedCuts':94-len(repairs),'technical':technical,'wholeDecodeExitCode':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newTts':0,'sourceModelsRerendered':0,'newGitImages':0}
 m.save(P/'part1-final-visual-build-v250.json',proof)
 state.update(status='complete-awaiting-direct-pixels',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint()
 print(json.dumps({'frames':plan['finalFrames'],'repairedCuts':len(repairs),'retainedCuts':94-len(repairs),'decodeExit':0,'pixelsApproved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
