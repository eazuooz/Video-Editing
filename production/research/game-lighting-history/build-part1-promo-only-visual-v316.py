"""Replace exactly six promotional frames; preserve current audio, captions and all93 other cuts."""
from pathlib import Path
import importlib.util,copy,psutil,os,json
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production';PP=P/'part1-final-input-plan-v309.json';plan=m.read(PP)
RP=P/'part1-promo-boundary-proposal-v315.json';review=m.read(RP)
assert review['allImagesDirectlyRead'] and review['fullProposedSourceNormalSpeedReviewed'] and review['normalSpeedSourceReview']['movingSourceApproved']
assert review['sourcePromoFramesInclusive']==[900,905] and review['finalPromoFramesInclusive']==[48066,48071]
prior=m.read(P/'part1-final-visual-build-v310.json');pair=m.read(P/'part1-reviewed-pair-execution-v313.json');comparison=m.read(P/'part1-decoded-comparison-execution-v314.json')
assert pair['status']=='complete' and pair['exitCode']==0 and comparison['status']=='complete' and comparison['exitCode']==0
assert prior['planSha256']==m.sha(PP) and prior['wholeDecodeExitCode']==0 and prior['all89148PtsExact1500']
ancestors={p.pid for p in psutil.Process().parents()}|{os.getpid()}
for proc in psutil.process_iter(['pid','name','cmdline']):
 d=proc.info
 if d['pid'] not in ancestors and (d['name'] or '').lower().startswith('python') and 'game-lighting-history' in ' '.join(d['cmdline'] or []) and any(t in ' '.join(d['cmdline'] or []) for t in ['build-part1','review-part1','compare-part1']):raise RuntimeError('Preserve live independent owned worker')
resources=m.resources();OUT=R/'production/research/game-lighting-history/local/part1-promo-only-visual-v316';SP=P/'part1-promo-only-visual-execution-v316.json'
assert not SP.exists() and not OUT.exists();OUT.mkdir(parents=True)
state={'startedAt':m.stamp(),'status':'running','worker':m.worker(),'active':None,'commands':[],'results':[],'resourceObservation':resources,'newTts':0,'newAudioMix':0,'gpuJobs':0,'allFinalPixelsReviewed':False,'uploaded':False}
m.save(SP,state)
def checkpoint():
 cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp();j['episode04Part1PromoOnlyVisualV316']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'completedCommands':len(state['commands']),'finalApproved':False};j['ownedActiveWork']={'type':'six-promo-frames-native-only-repair','execution':m.rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Current pair and fresh changed pixels'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Current reviewed pair, all encoded pixels/motion then private upload'};m.save(cp,j)
def run(args,label):
 checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
try:
 overrides=m.read(P/'part1-input-overrides-v289.json');c=copy.deepcopy(next(x for x in overrides['effectiveCuts'] if x['id']==review['id']));assert c['video']==review['source'];source=R/c['video']['path'];assert m.sha(source)==c['video']['sha256'];assert m.sha(R/c['pcm']['path'])==c['pcm']['sha256'];c['proposedCuts']=review['proposedCuts'];pieces=[]
 for k,cut in enumerate(c['proposedCuts']):
  frames=cut['outFrame']-cut['inFrame'];vf=['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black','setsar=1','fps=60','setpts=PTS-STARTPTS','crop=1920:900:0:180','pad=1920:1080:0:0:black',f'trim=end_frame={frames}','settb=1/90000','setpts=N*1500']
  for n,text in enumerate([c['identityLabel'],c['onScreenConditionLabel']]):
   t=OUT/f'piece-{k}-label-{n}.txt';t.write_text(text,'utf8');vf.append(f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{m.rel(t)}':expansion=none:x=32:y={22+42*n}:fontsize={28 if n==0 else 24}:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8")
  piece=OUT/f'piece-{k}.mp4';run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-reinit_filter','0','-ss',f"{cut['inFrame']/60:.9f}",'-i',source,'-filter_threads','2','-vf',','.join(vf),'-map','0:v:0','-frames:v',str(frames),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',piece],f'piece-{k}')
  proof=m.verify_video(piece,frames,state,SP,OUT,f'verify-piece-{k}');state['results'].append(proof);pieces.append(piece)
 def concat(files,file,label):
  txt=OUT/(label+'.concat.txt');txt.write_text('\n'.join("file '"+str(f).replace('\\','/')+"'" for f in files)+'\n','utf8');run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',txt,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',file],label)
 joined=OUT/'cyber-surface-native.mp4';concat(pieces,joined,'join-native');nativeProof=m.verify_video(joined,1508,state,SP,OUT,'verify-native')
 cuts=copy.deepcopy(prior['cuts']);files=[R/plan['branding']['path']];changed=0
 for cut in cuts:
  assert m.sha(R/cut['path'])==cut['sha256']
  if cut['id']==review['id']:
   cut.update(path=m.rel(joined),sha256=m.sha(joined),sourceCuts=c['proposedCuts'],retainedByteIdenticalToV310=False,repair='Exact6source900–905promo frames replaced by unused710–715actual plaza action; all source mapping from final48072unchanged.',technicalProofs=state['results'],technical=nativeProof);changed+=1
  else:cut['retainedByteIdenticalToV310']=True
  files.append(R/cut['path'])
 assert changed==1 and len(cuts)==94;files.append(R/plan['membership']['path']);visual=OUT/'silent-visual.mp4';concat(files,visual,'master-concat');technical=m.verify_video(visual,plan['finalFrames'],state,SP,OUT,'verify-master')
 proof={'builtAt':m.stamp(),'planSha256':m.sha(PP),'path':m.rel(visual),'sha256':m.sha(visual),'frames':plan['finalFrames'],'cuts':cuts,'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'inputOverrides':{'path':m.rel(RP),'sha256':m.sha(RP),'changedInput':review['id'],'other93InputsExactV310':True},'retainedOther93InputsByteIdentical':True,'wholeDecodeExitCode':0,'all89148PtsExact1500':True,'technical':technical,'sourceModelsRerendered':0,'nativeCutsReframed':1,'newTts':0,'newAudioMix':0,'currentMixSettings':{'path':m.rel(P/'part1-final-mix-settings-v310.json'),'sha256':m.sha(P/'part1-final-mix-settings-v310.json')},'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newGitImages':0};m.save(P/'part1-final-visual-build-v316.json',proof)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint();print(json.dumps({'frames':plan['finalFrames'],'changedCuts':1,'retainedCuts':93,'newTts':0,'newMix':0,'pixelsApproved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
