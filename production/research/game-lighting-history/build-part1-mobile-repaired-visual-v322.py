"""Assemble four directly reviewed native repairs; preserve the other90 exact inputs."""
from pathlib import Path
import importlib.util,copy,json,os,psutil
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v309.json';plan=m.read(PP)
RP=P/'part1-mobile-native-input-direct-review-v321.json';review=m.read(RP)
EP=P/'part1-mobile-native-preview-execution-v320.json';execution=m.read(EP)
assert review['allFourFullInputIntervalsActuallyPlayed'] and review['allFourSelectedForCurrentPrivateTechnicalPair']
assert review['execution']['sha256']==m.sha(EP) and execution['status']=='complete-awaiting-direct-review' and execution['exitCode']==0
assert review['proposal']['sha256']==m.sha(R/review['proposal']['path'])
prior=m.read(P/'part1-final-visual-build-v316.json')
assert prior['planSha256']==m.sha(PP) and prior['wholeDecodeExitCode']==0 and prior['all89148PtsExact1500']
approved={r['id']:r for r in review['records']};assert len(approved)==4
for r in approved.values():
 assert r['fullSelectedIntervalActuallyPlayed'] and r['playbackRate']==1 and r['normalSpeedInputPixelsApproved'] and r['selectedForCurrentPrivateTechnicalPair']
 assert m.sha(R/r['native']['path'])==r['native']['sha256'] and m.sha(R/r['preview']['path'])==r['preview']['sha256']
 assert r['technical']['wholeDecode']['exitCode']==0 and r['technical']['allPresentationPtsContinuous']
ancestors={p.pid for p in psutil.Process().parents()}|{os.getpid()}
for proc in psutil.process_iter(['pid','name','cmdline']):
 d=proc.info;cmd=' '.join(d['cmdline'] or [])
 if d['pid'] not in ancestors and (d['name'] or '').lower().startswith('python') and 'game-lighting-history' in cmd and any(t in cmd for t in ['build-part1','build-mobile-native','review-part1','compare-part1']):raise RuntimeError('Preserve active owned media worker')
resources=m.resources();OUT=R/'production/research/game-lighting-history/local/part1-mobile-repaired-visual-v322';SP=P/'part1-mobile-repaired-visual-execution-v322.json'
assert not OUT.exists() and not SP.exists();OUT.mkdir(parents=True)
state={'startedAt':m.stamp(),'status':'running','worker':m.worker(),'active':None,'commands':[],'results':[],'resourceObservation':resources,'cpuThreads':2,'gpuJobs':0,'newTts':0,'newAudioMix':0,'allFinalPixelsReviewed':False,'uploaded':False}
m.save(SP,state)
def checkpoint():
 cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part1MobileVisualV322']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'finalApproved':False}
 j['ownedActiveWork']={'type':'four-reviewed-mobile-input-master-assembly','execution':m.rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Current clean/captioned pair then fresh encoded regions'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Current pair then encoded pixels/QA/private upload'}
 m.save(cp,j)
try:
 cuts=copy.deepcopy(prior['cuts']);files=[R/plan['branding']['path']];changed=[]
 for cut in cuts:
  assert m.sha(R/cut['path'])==cut['sha256']
  if cut['id'] in approved:
   r=approved[cut['id']];assert cut['frames']==r['frames']
   cut.update(path=r['native']['path'],sha256=r['native']['sha256'],sourceCuts=r['sourcePieces'],technical=r['technical'],retainedByteIdenticalToV316=False,inputDirectReview={'path':m.rel(RP),'sha256':m.sha(RP)},repair=r['actualObservation']);changed.append(cut['id'])
  else:cut['retainedByteIdenticalToV316']=True
  files.append(R/cut['path'])
 assert len(cuts)==94 and len(changed)==4;files.append(R/plan['membership']['path'])
 concat=OUT/'master.concat.txt';concat.write_text('\n'.join("file '"+str(f).replace('\\','/')+"'" for f in files)+'\n','utf8')
 visual=OUT/'silent-visual.mp4';checkpoint()
 m.run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',visual],'master-concat',state,SP,OUT)
 technical=m.verify_video(visual,plan['finalFrames'],state,SP,OUT,'verify-master')
 proof={'builtAt':m.stamp(),'planSha256':m.sha(PP),'path':m.rel(visual),'sha256':m.sha(visual),'frames':plan['finalFrames'],'cuts':cuts,'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'inputOverrides':{'previous':prior['inputOverrides'],'mobileReview':{'path':m.rel(RP),'sha256':m.sha(RP)},'changedInputs':changed,'other90InputsExactV316':True},'retainedOther90InputsByteIdentical':True,'wholeDecodeExitCode':0,'all89148PtsExact1500':True,'technical':technical,'sourceModelsRerendered':0,'nativeCutsReframed':0,'newTts':0,'newAudioMix':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newGitImages':0}
 m.save(P/'part1-final-visual-build-v322.json',proof)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint();print(json.dumps({'frames':plan['finalFrames'],'changedCuts':4,'retainedCuts':90,'pixelsApproved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
