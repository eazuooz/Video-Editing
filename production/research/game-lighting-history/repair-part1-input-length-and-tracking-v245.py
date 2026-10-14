"""Repair three whole-file reuse mistakes and two temporal overlays only.

The original v244 execution and all completed cuts remain immutable. Overlay
coordinates use the overlay filter's frame-evaluated time, not drawbox's
thickness variable. No narration, caption timing or source model is rebuilt.
"""
from pathlib import Path
import importlib.util, json, hashlib
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v240.json';plan=m.read(PP)
BP=P/'part1-final-visual-execution-v244.json';baseline=m.read(BP)
assert baseline['status']=='failed' and len(baseline['results'])==51
assert baseline['plan']['sha256']==m.sha(PP)
layersPath=P/'part1-visual-layers-v244.json';layers=m.read(layersPath)
assert layers['inputPlan']['sha256']==m.sha(PP)
OUT=R/'production/research/game-lighting-history/local/part1-input-repair-v245'
SP=P/'part1-input-repair-execution-v245.json';assert not SP.exists() and not OUT.exists()
resources=m.resources();OUT.mkdir(parents=True)
state={'startedAt':m.stamp(),'status':'running','worker':m.worker(),'active':None,'commands':[],
 'results':[],'resourceObservation':resources,'planSha256':m.sha(PP),'baselineExecutionSha256':m.sha(BP),
 'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False}
m.save(SP,state)
def checkpoint():
 p=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(p)
 j['episode04Part1InputRepairV245']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'results':len(state['results']),'finalApproved':False}
 j['ownedActiveWork']={'type':'part1-length-and-tracking-repair','execution':m.rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Direct moving pixels and current mixed-ASR'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Direct moving pixels and current mixed-ASR'}
 j['updatedAt']=m.stamp();m.save(p,j)
def run(args,label):
 checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
def label_filter(text,name,x=32,y=22,size=28):
 p=OUT/(name+'.txt');p.write_text(text,'utf8')
 return f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(p)}':expansion=none:x={x}:y={y}:fontsize={size}:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
def encode_piece(c,index,source,start,frames,tracking=None,piece=0,offset=0):
 rect=c.get('cropRect');vf=([f'crop={rect[2]}:{rect[3]}:{rect[0]}:{rect[1]}'] if rect else [])+['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black','setsar=1','fps=60','setpts=PTS-STARTPTS']
 matte=c.get('captionMatteHeight',0)
 if matte:vf.extend([f'crop=1920:{1080-matte}:0:{0 if tracking and tracking.get("matteFrom")=="bottom" else matte}', 'pad=1920:1080:0:0:black'])
 if c.get('oneSilentVideoTailFrame'):vf.append('tpad=stop_mode=clone:stop_duration=0.016666667')
 vf.extend([f'trim=end_frame={frames}','settb=1/90000','setpts=N*1500'])
 if c['id']=='first:original-overview-1':
  vf.append(label_filter('렌더링 역사 ④ 전체 안내 · 이번 분할편: 그림자·TSR·모바일',f'cut-{index}-scope',x=420,y=16,size=24))
 if not c.get('originalChapter') and c['kind']=='actual':
  for k,t in enumerate([c['identityLabel'],c.get('onScreenConditionLabel')]):
   if t:vf.append(label_filter(t,f'cut-{index}-piece-{piece}-condition-{k}',y=22+42*k,size=28 if k==0 else 24))
 if tracking:
  vf.append(label_filter(tracking['label'],f'cut-{index}-target',x=tracking['labelX'],y=tracking['labelY'],size=28))
  graph=['[0:v]'+','.join(vf)+'[base0]']
  for k,b in enumerate(tracking['boxes']):
   duration=b['to']-b['from'];x=f"{b['x0']}+({b['x1']-b['x0']})*(t+{offset}-{b['from']})/{duration}";y=f"{b['y0']}+({b['y1']-b['y0']})*(t+{offset}-{b['from']})/{duration}"
   graph.append(f"color=c=black@0:s={b['width']}x{b['height']}:r=60:d={frames/60:.9f},format=rgba,drawbox=x=0:y=0:w=iw:h=ih:color={b['color']}:t=4:replace=1,settb=1/90000,setpts=N*1500[box{k}]")
   graph.append(f"[base{k}][box{k}]overlay=x='{x}':y='{y}':eval=frame:format=yuv420:shortest=1:enable='gte(t,{b['from']-offset})*lt(t,{b['to']-offset})'[base{k+1}]")
  filters=['-filter_complex_threads','2','-filter_complex',';'.join(graph),'-map',f'[base{len(tracking["boxes"])}]']
 else:filters=['-filter_threads','2','-vf',','.join(vf),'-map','0:v:0']
 file=OUT/f'cut-{index:03d}-piece-{piece}.mp4'
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-reinit_filter','0','-ss',f'{start:.9f}','-i',source,*filters,'-frames:v',str(frames),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',file],f'repair-{index:03d}-piece-{piece}')
 proof=m.verify_video(file,frames,state,SP,OUT,f'verify-{index:03d}-piece-{piece}')
 return file,proof
def repair(c,index):
 source=R/c['video']['path'];assert m.sha(source)==c['video']['sha256']
 tracking=layers['layers'].get(c['id']);proofs=[];pieces=[];offset=0
 cuts=c.get('proposedCuts') or [{'inFrame':c.get('sourceStartFrame',0),'outFrame':c.get('sourceStartFrame',0)+c['frames']}]
 for k,cut in enumerate(cuts):
  file,proof=encode_piece(c,index,source,cut['inFrame']/60,cut['outFrame']-cut['inFrame'],tracking,k,offset)
  pieces.append(file);proofs.append(proof);offset+=(cut['outFrame']-cut['inFrame'])/60
 assert sum(q['outFrame']-q['inFrame'] for q in cuts)==c['frames']
 if len(pieces)>1:
  concat=OUT/f'cut-{index:03d}.concat.txt';concat.write_text('\n'.join("file '"+str(x).replace('\\','/')+"'" for x in pieces)+'\n','utf8');file=OUT/f'cut-{index:03d}.mp4'
  run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',file],f'join-{index:03d}')
 return file,{'id':c['id'],'path':m.rel(file),'sha256':m.sha(file),'frames':c['frames'],'kind':c['kind'],'fromFrame':c['fromFrame'],'toFrame':c['toFrame'],'reusedByteIdentical':False,'repair':'exact-source-range' if not tracking else 'frame-evaluated-temporal-overlay','technicalProofs':proofs,'inputStartUnchangedByOverlayLoops':True}
try:
 files=[R/plan['branding']['path']];repairs=[]
 oldmap={q['id']:q for q in baseline['results']}
 for index,c in enumerate(plan['cuts'],1):
  old=oldmap.get(c['id'])
  if old:assert m.sha(R/old['path'])==old['sha256']
  needed=not old or (c.get('originalChapter') and c.get('sourceStartFrame',0)==0) or c['id'] in layers['layers']
  if needed:file,row=repair(c,index);repairs.append(row)
  else:file=R/old['path'];row={**old,'retainedByteIdenticalToV244':True}
  files.append(file);state['results'].append(row);checkpoint()
 assert len(repairs)==46;files.append(R/plan['membership']['path'])
 concat=OUT/'master.concat.txt';concat.write_text('\n'.join("file '"+str(x).replace('\\','/')+"'" for x in files)+'\n','utf8')
 visual=OUT/'silent-visual.mp4'
 run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',visual],'master-concat')
 technical=m.verify_video(visual,plan['finalFrames'],state,SP,OUT,'master')
 proof={'builtAt':m.stamp(),'planSha256':m.sha(PP),'path':m.rel(visual),'sha256':m.sha(visual),'frames':plan['finalFrames'],'cuts':state['results'],'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'repairs':repairs,'retainedCuts':48,'technical':technical,'wholeDecodeExitCode':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newTts':0,'sourceModelsRerendered':0,'newGitImages':0,'editableVisualLayers':{'path':m.rel(layersPath),'sha256':m.sha(layersPath)},'overlayDocumentation':'https://ffmpeg.org/ffmpeg-filters.html#overlay'}
 m.save(P/'part1-final-visual-build-v245.json',proof)
 state.update(status='complete-awaiting-direct-pixels',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint()
 print(json.dumps({'frames':plan['finalFrames'],'repairedOrResumedCuts':46,'retainedCuts':48,'decodeExit':0,'pixelsApproved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
