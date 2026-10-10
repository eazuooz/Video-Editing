from pathlib import Path
from datetime import datetime, timezone
import json, psutil
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
pair=read(OUT/'final-pair-execution-v3.json')
assert pair['exitCode']==0 and pair['protectedBaselineUnchanged']
assert not psutil.pid_exists(pair['pid']) or psutil.Process(pair['pid']).create_time()!=pair['createTime']
assert all(v['wholeDecodeExitCode']==0 and v['all54115Pts1500Verified'] and v['identicalReviewedWholeAacAndPcm'] for v in pair['pair'])
state=read(OUT/'final-pixel-extraction-execution-v2.json')
assert psutil.Process(state['pid']).create_time()==state['createTime']
now=datetime.now(timezone.utc).isoformat()
file=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json'
q=read(file)
assert q['execution']['heavyJob']['sessionId']==4207
completed=dict(q['execution']['heavyJob'])
completed.update(actualExitCode=0,actualOuterExitCode=0,exitObservedChunk='427721',processAbsenceObservedChunk='db2e58',allFinalPixelsApproved=False)
q['execution']['completedJobs'].append(completed)
q['execution'].update(stage='polar-final-cue-cut-pixel-extraction-running',heavyJob={
 'sessionId':58791,'pid':state['pid'],'createTime':state['createTime'],'commandLine':state['commandLine'],
 'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/final-pixel-extraction-execution-v2.json',
 'resourceEvidence':state['resourceEvidence'],'cpuThreads':2,'gpuJobs':0,'actualExitCode':None},
 next='Observe actual extraction exit/CIM, directly review all listed final samples and whole normal-speed playback, then adopt/collect only after both manual gates pass.')
item=next(v for v in q['items'] if v['slug']=='game-math-polar-3d')
item['review'].update(technicalQaPassed=True,currentMixedAudioPassed=True)
item['technicalQaEvidence']='projects/game-math-polar-3d/revision-teaching-clarity-v1/final-pair-execution-v3.json'
item['reviewScopeNote']='Actual v3 pair exit0, both whole decodes and all54115 PTS1500, identical reviewed44-context AAC/PCM and loudness passed. Final pixel/flow/collection/settings/Git/replacement schedule are pending; human listening/public rights remain false.'
q['updatedAt']=now
file.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pairActualOuterExit':0,'finalPixelSession':58791,'finalPixelPid':state['pid'],'finalPixelsApproved':False}))
