"""Replace stale top-level handoff text with observed execution and prepared gates."""
from pathlib import Path
import importlib.util,psutil
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production';cp=R/'production/research/game-lighting-history/checkpoint.json'
s=m.read(P/'part1-final-mixed-asr-execution-v243.json');j=m.read(cp)
w=s['worker'];alive=psutil.pid_exists(w['pid']) and abs(psutil.Process(w['pid']).create_time()-w['createTime'])<.01
if s['status']!='complete':assert alive,'Read and resolve the actual stopped worker before updating progress'
j.setdefault('historicalTopLevelStageBeforeV260',j.get('stage'))
j['status']='episode04-physical01-current-final-mixed-ASR-and-native-pixel-corrections'
j['stage']=j['status']
j['ownedJobsRunning']=[dict(type='current-part1-mixed-ASR',**w)] if alive else []
j['next']='Read all30 current mixed-ASR windows; resolve evidenced chunk/number concerns in complete independent current PCM. Render five observed native fixes once, review their normal moving pixels, then gate clean/captioned pair, every final cue/cut, QA/collection/private settings/Git.'
j['episode04Part1PreparedDeliveryV252']={'recordedAt':m.stamp(),'observedExecution':'projects/game-lighting-history-04/production/part1-final-mixed-asr-execution-v243.json',
 'actualWorker':w,'actualWorkerAliveAtObservation':alive,'asrResultsCompletedAtObservation':len(s['results']),'asrTotal':s['total'],'currentWindowAtObservation':s['currentWindow'],
 'directProgress':'projects/game-lighting-history-04/production/part1-final-mixed-asr-direct-progress-v251.json',
 'nativeCorrectionsPrepared':5,'unchangedMovingRowsReviewed':9,'nativeSourceReview':'projects/game-lighting-history-04/production/part1-native-overrides-direct-review-v249.json',
 'pairProducer':'production/research/game-lighting-history/build-part1-reviewed-pair-v252.py','pairProducerExecuted':False,
 'finalPixelPlan':'projects/game-lighting-history-04/production/part1-final-pixel-review-request-v253.json','finalPixelFramesPlanned':2266,'imagesExtracted':0,
 'cpuThreads':2,'gpuJobs':0,'finalMixedAsrApproved':False,'allFinalPixelsReviewed':False,'qaApproved':False,'collected':False,'uploaded':False,
 'completedPart3Reuse':{'videoId':'ydW9Glmh0nM','receipt':'projects/game-lighting-history-04-3/publishing/youtube-upload.json','regenerationRequired':False},'seriesCompleted':False}
j['updatedAt']=m.stamp();m.save(cp,j)
print(m.json.dumps({'observedWorkerAlive':alive,'completedAsrResults':len(s['results']),'preparedPairOnly':True,'finalApproved':False}))
