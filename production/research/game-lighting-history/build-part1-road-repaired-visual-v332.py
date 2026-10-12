"""Replace one source interval after direct review; retain all other93 exact inputs."""
from pathlib import Path
import importlib.util,copy,json
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v309.json';plan=m.read(PP)
RP=P/'part1-road-native-input-direct-review-v331.json';review=m.read(RP)
assert review['allOneFullInputIntervalsActuallyPlayed'] and review['allOneSelectedForCurrentPrivateTechnicalPair']
assert review['execution']['sha256']==m.sha(R/review['execution']['path']) and review['proposal']['sha256']==m.sha(R/review['proposal']['path'])
priorPath=P/'part1-final-visual-build-v322.json';prior=m.read(priorPath)
assert prior['planSha256']==m.sha(PP) and prior['wholeDecodeExitCode']==0 and prior['all89148PtsExact1500']
r=review['records'][0];assert r['id']=='geometry-road-mask:native' and r['fullSelectedIntervalActuallyPlayed'] and r['playbackRate']==1
assert r['normalSpeedInputPixelsApproved'] and r['cue204GreenRegionConfirmed'] and r['selectedForCurrentPrivateTechnicalPair']
assert m.sha(R/r['native']['path'])==r['native']['sha256'] and m.sha(R/r['preview']['path'])==r['preview']['sha256']
resources=m.resources();OUT=R/'production/research/game-lighting-history/local/part1-road-repaired-visual-v332';SP=P/'part1-road-repaired-visual-execution-v332.json'
assert not OUT.exists() and not SP.exists();OUT.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],results=[],resources=resources,cpuThreads=2,gpuJobs=0,newTts=0,newAudioMix=0,newGitImages=0,allFinalPixelsReviewed=False,uploaded=False)
def checkpoint():
 cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part1RoadVisualV332']=dict(execution=m.rel(SP),status=state['status'],worker=state['worker'],active=state['active'],finalApproved=False)
 j['ownedActiveWork']=dict(type='one-reviewed-road-input-master-assembly',execution=m.rel(SP),worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,next='Current pair then1037-frame changed region and remaining moving QA') if state['status']=='running' else dict(status='no-active-owned-media-worker',execution=m.rel(SP),next='Current pair then changed-region/remaining moving QA')
 m.save(cp,j)
m.save(SP,state);checkpoint()
try:
 cuts=copy.deepcopy(prior['cuts']);files=[R/plan['branding']['path']];changed=[]
 for cut in cuts:
  assert m.sha(R/cut['path'])==cut['sha256']
  if cut['id']==r['id']:
   assert cut['frames']==r['frames']==1037
   for key in list(cut):
    if key.startswith('retainedByteIdentical') or key in ['technicalProofs','technical','inputDirectReview']:cut.pop(key)
   cut.update(path=r['native']['path'],sha256=r['native']['sha256'],sourceCuts=r['sourcePieces'],technical=r['technical'],retainedByteIdenticalToV322=False,
    inputDirectReview={'path':m.rel(RP),'sha256':m.sha(RP)},repair=review['resolvedIssue']);changed.append(cut['id'])
  else:cut['retainedByteIdenticalToV322']=True
  files.append(R/cut['path'])
 assert len(cuts)==94 and changed==['geometry-road-mask:native'];files.append(R/plan['membership']['path'])
 concat=OUT/'master.concat.txt';concat.write_text('\n'.join("file '"+str(f).replace('\\','/')+"'" for f in files)+'\n','utf8')
 visual=OUT/'silent-visual.mp4'
 m.run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',visual],'master-concat',state,SP,OUT)
 technical=m.verify_video(visual,plan['finalFrames'],state,SP,OUT,'verify-master')
 proof=copy.deepcopy(prior)
 proof.update(builtAt=m.stamp(),path=m.rel(visual),sha256=m.sha(visual),cuts=cuts,technical=technical,
  previousVisual={'path':m.rel(priorPath),'sha256':m.sha(priorPath)},retainedOther93InputsByteIdenticalToV322=True,
  retainedOther90InputsByteIdentical=False,sourceModelsRerendered=0,nativeCutsReframed=1,newTts=0,newAudioMix=0,
  allFinalPixelsReviewed=False,allMovingPixelsReviewed=False,qaApproved=False,uploaded=False,newGitImages=0)
 proof['inputOverrides'].update(roadReview={'path':m.rel(RP),'sha256':m.sha(RP)},roadChangedInput='geometry-road-mask:native',
  other93InputsExactV322=True,other90InputsExactV316=False,other89InputsExactV316=True)
 proof['inputOverrides']['other90InputsExactV316']=False
 m.save(P/'part1-final-visual-build-v332.json',proof)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint();print(json.dumps(dict(frames=plan['finalFrames'],changedInputs=1,retainedInputs=93,pixelsApproved=False)))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
