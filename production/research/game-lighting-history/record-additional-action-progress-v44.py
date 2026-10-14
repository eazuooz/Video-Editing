"""Observe the single running acquisition and preserve partial candidate playback evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os, psutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):
 t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');t.replace(p)
execution=ROOT/'production/research/game-lighting-history/local/episode04-additional-action-v44/execution.json'
state=read(execution);me=psutil.Process(state['parentPid']);assert 'acquire-episode04-additional-action-v44' in ' '.join(me.cmdline())
record={'recordedAt':stamp(),'status':'partial-source-playback-and-silent-acquisition','sessionId':37029,
 'worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':me.cwd()},
 'execution':{'path':execution.relative_to(ROOT).as_posix(),'sha256AtObservation':sha(execution)},'actualWorkerAlive':True,'cpuThreads':2,'gpuJobs':0,
 'candidatePlayback':[
  {'id':'inGlMVhYB1s','tab':14,'url':'https://www.youtube.com/watch?v=inGlMVhYB1s&t=2430s','rate':1,'muted':True,'observedTimes':[2442.384117,2465.381529,2494.057261],
   'before':'Colored clipmap bands on the ground, wheel and shadow.','action':'Return from debug visualization to the ordinary editor scene.','after':'Normal ferris-wheel/sky/shadow view.','exclude':'Console autocomplete obstructs the lower viewport around2465; select narrower exact clean ranges after native sample review.','fullWindowMotionApproved':False},
  {'id':'inGlMVhYB1s','tab':14,'url':'https://www.youtube.com/watch?v=inGlMVhYB1s&t=2530s','rate':1,'muted':True,
   'finding':'Playback advanced beyond the candidate to2736s while independent work continued. Only earlier actual observed512/256/128MB resource views remain evidence; elapsed playback alone does not prove every intermediate frame was inspected.','fullWindowMotionApproved':False},
  {'id':'inGlMVhYB1s','tab':14,'url':'https://www.youtube.com/watch?v=inGlMVhYB1s&t=1500s','rate':1,'muted':True,'observedTimes':[1564.240745,1611.81071],
   'before':'Editor shows a selected spline surrounding grass paths.','after':'Two road barriers in the ordinary shaded scene.','candidateOnly':True,'fullWindowMotionApproved':False},
  {'id':'rSswLKbKREk','tab':40,'url':'https://www.youtube.com/watch?v=rSswLKbKREk&t=684s','rate':1,'muted':True,'observedTimes':[712.238055,773.945678],
   'decision':'reject-observed-half-precision-window-for-action-quota','reason':'Observed mobile-preview image is embedded in a mostly static lecture slide, followed by presenter. No live shader-setting before/action/after established.','researchOnly':True,'finalUseApproved':False},
  {'id':'nZlVkI3j7Xs','tab':40,'url':'https://www.youtube.com/watch?v=nZlVkI3j7Xs&t=1450s','rate':1,'muted':True,'observedTimes':[1516.611453,1564.19221],
   'finding':'Device Profile texture LOD table and console-variable table appear within the lecture frame; recorded editor operations must be distinguished from a static screenshot. Native crop/continuous motion review pending.','candidateOnly':True,'fullWindowMotionApproved':False}
 ],
 'allocation':{'record':'projects/game-lighting-history-04/production/measured-additive-physical-split-v39.json','minimumAdditionalActionBeforeNewOpeningsAndConclusionsSeconds':2053.8166666666666,'paddingAllowed':False,'originalExplanationAndPcmPreserved':True,'part1ScopedOpeningStillRequired':True},
 'original87AndAdded24Regenerated':False,'newNarrationWritten':False,'newTtsStarted':False,'newFinalRenderStarted':False,'allFinalPixelsReviewed':False,'bodyRatioApproved':False,'uploaded':False,'newGitImages':0,
 'next':'Directly read acquired candidate boards, select exact meaningful non-overlapping action intervals and exclusions, then write matching independent KO/EN guides and physical-part openings/conclusions before safe TTS.'}
target=P/'additional-action-browser-progress-v44.json';assert not target.exists();write(target,record)
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j['episode04AdditionalActionV44']={'progress':target.relative_to(ROOT).as_posix(),'execution':execution.relative_to(ROOT).as_posix(),'sessionId':37029,'worker':record['worker'],'actualWorkerAlive':True,'current':state['current'],'completed':len(state['completed']),'finalUseApproved':False}
j['ownedActiveWork']={'type':'single-silent-source-acquisition-CPU2-GPU0','sessionId':37029,'worker':record['worker'],'execution':execution.relative_to(ROOT).as_posix(),'next':record['next']};j['updatedAt']=stamp();write(cp,j)
print(json.dumps({'record':target.relative_to(ROOT).as_posix(),'workerAlive':True,'sessionId':37029,'finalUseApproved':False,'uploaded':False}))
