"""Seal directly read native samples. No decode/render/source adoption."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess
ROOT=Path(__file__).resolve().parents[4]
PROOF=Path(__file__).resolve().parent
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp=datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p):return str(p.relative_to(ROOT)).replace('\\','/')
def new(p,d):
    assert not p.exists(), f'Preserve {p}'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
execution_path=PROOF/'chicory-native-candidate-execution-v1.json'
original=execution_path.read_bytes();e=json.loads(original)
npath=PROOF/'chicory-native-observations-v1.json';notes=json.loads(npath.read_text(encoding='utf-8'))
assert e['status']=='exited-awaiting-direct-review' and e['pid']==58872 and e['sessionId']==12384
assert all(c['status']=='exited' and c['exitCode']==0 for c in e['children'])
assert e['totalUniqueSamples']==404 and e['newSamples']==226 and e['reusedCoarseSamples']==178 and e['totalBoards']==76
assert notes['allBoardsDirectlyRead'] and len(notes['windows'])==16
check=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert check.returncode==0,check.stdout+check.stderr
verified=[]
for s in e['sources']:
    assert sha(ROOT/s['sourcePath'])==s['sourceSha256']
    assert s['actualSelectedPtsVerified'] and s['extractExitCode']==0
    for p in s['sampleMap']:
        assert p['pts']==p['nativeFrame']*256 and sha(ROOT/p['path'])==p['sha256']
for w in e['windows']:
    n=next(x for x in notes['windows'] if x['key']==w['key'])
    assert n['boards']==list(range(1,len(w['boards'])+1)) and n['sampleCount']==len(w['samples'])
    for b in w['boards']:assert sha(ROOT/b['path'])==b['sha256']
    verified.append({'key':w['key'],'source':w['source'],'samples':w['samples'],'boards':w['boards'],'observation':n})
dom_path=PROOF/'chicory-native-playback-dom-v1.txt';dom=dom_path.read_text(encoding='utf-8')
events=json.loads(dom[dom.index('[{\"kind\"'):])
for key in [w['key'] for w in e['windows']]:
    start=[x for x in events if x['key']==key and x['kind']=='start'];end=[x for x in events if x['key']==key and x['kind']=='end']
    assert len(start)==len(end)==1 and start[0]['muted'] and start[0]['rate']==1 and not start[0]['paused']
    assert end[0]['muted'] and end[0]['rate']==1 and end[0]['paused']
overshoots=[x['current']-next(w['endSecondsExclusive'] for w in e['windows'] if w['key']==x['key']) for x in events if x['kind']=='end']
playback={'schemaVersion':1,'recordedAt':stamp,'events':events,'all16ActualStartsAndEndsObserved':True,'muted':True,'rate':1,'endOvershootSeconds':[min(overshoots),max(overshoots)],'exactCutsUseNativePtsOnly':True,'allIntermediateFramesViewed':False,'fullContinuousListening':False,'browserEndpointsAreNotNativeCutBoundaries':True,'dom':rel(dom_path),'domSha256':sha(dom_path),'ax':rel(PROOF/'chicory-native-playback-v1.ax.txt'),'axSha256':sha(PROOF/'chicory-native-playback-v1.ax.txt')}
new(PROOF/'chicory-native-playback-observations-v1.json',playback)
result={'schemaVersion':1,'slug':'limited-color-world','recordedAt':stamp,'execution':rel(execution_path),'executionSha256':sha(execution_path),'actualOuterSessionId':12384,'actualOuterExitCode':0,'actualExitDirectlyObserved':'write_stdin dbf253, exit0','freshCimOwnPidAbsent':'exec81ff3d, all Python/FFmpeg process commandlines and creation times read; PID58872 absent','observations':rel(npath),'observationsSha256':sha(npath),'verifiedWindows':verified,'totalUniqueSamples':404,'newSamples':226,'reusedCoarseSamples':178,'totalBoards':76,'allSamplesAndBoardsDirectlyRead':True,'allHashesAndSelectedNativePtsVerified':True,'currentDistinctCheck':{'exitCode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},'candidateTrimmedSeconds':101.5,'trimmedBoundaryAndFramingApproved':False,'allIntermediateNativeFramesViewed':False,'wholeContinuousPlaybackOrListeningApproved':False,'finalCaptionCueApproved':False,'sourceFootageAdopted':False,'publicRightsApproved':False,'newProjectScriptTtsMcOrFinalMedia':False,'researchManipulated':False,'ownResearchResumeClaim':False,'gitImagesOrMediaAdded':0}
out=PROOF/'chicory-native-sample-direct-review-v1.json';new(out,result)
assert execution_path.read_bytes()==original
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';before=qpath.read_bytes();q=json.loads(before)
foreign=json.dumps([x for x in q['items'] if x['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False)
item=next(x for x in q['items'] if x['slug']=='limited-color-world');assert item['videoId'] is None and not any(item['checkpoints'].values())
item.update(stage='chicory-native-samples-reviewed-trimmed-framing-pending',nativeSourceReview=rel(out),nativeSourceReviewSha256=sha(out),updatedAt=stamp)
item['execution'].update(status='exited',actualOuterExitCode=0,endedObservedAt=stamp)
item['nextAction']='Inspect new trimmed endpoint frames and reframed existing samples with fixed caption test; seal native action bank before footage adoption or independent KOEN.'
q['updatedAt']=q['lastProgressAt']=stamp
assert foreign==json.dumps([x for x in q['items'] if x['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False)
assert qpath.read_bytes()==before
t=qpath.with_name(qpath.name+'.limited-native-seal.tmp');t.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,qpath)
print(json.dumps({'nativeSamples':404,'boards':76,'playbackWindows':16,'currentDistinctExit':check.returncode,'trimmedSeconds':101.5,'adopted':False},ensure_ascii=False))
