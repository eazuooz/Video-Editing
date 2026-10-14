"""Seal actual native-boundary sample review, preserving partial playback scope."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp=datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p):return str(p.relative_to(ROOT)).replace('\\','/')
def new(p,d):
    assert not p.exists(),str(p)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ep=P/'chicory-trimmed-framing-execution-v2.json';original=ep.read_bytes();e=json.loads(original)
np=P/'chicory-trimmed-observations-v2.json';notes=json.loads(np.read_text(encoding='utf-8'))
assert e['pid']==43952 and e['sessionId']==33844 and e['status']=='exited-awaiting-direct-review'
assert all(c['exitCode']==0 and c['status']=='exited' for c in e['children'])
assert e['totalUniqueSourceSamples']==283 and e['newEndpointSamples']==40 and e['reusedSourceSamples']==243 and e['totalBoards']==56
assert notes['all56BoardsAnd283SamplesDirectlyRead'] and len(notes['cuts'])==16
check=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert check.returncode==0,check.stdout+check.stderr
for path,h in e['protectedInputs'].items():assert sha(ROOT/path)==h
for s in e['sources']:
    assert sha(ROOT/s['sourcePath'])==s['sourceSha256'] and s['actualMissingSelectedPtsVerified']
    for f in s['sampleMap']:assert f['pts']==f['nativeFrame']*256 and sha(ROOT/f['path'])==f['sha256']
verified=[]
for c in e['cuts']:
    n=next(n for n in notes['cuts'] if n['key']==c['key'])
    assert n['samples']==len(c['samples']) and n['boards']==list(range(1,len(c['boards'])+1))
    for f in c['samples']:
        assert f['pts']==f['nativeFrame']*256
        assert sha(ROOT/f['framedPath'])==f['framedSha256'] and sha(ROOT/f['captionTestPath'])==f['captionTestSha256']
    for b in c['boards']:assert sha(ROOT/b['path'])==b['sha256']
    verified.append({'key':c['key'],'source':c['source'],'startFrame':c['startFrame'],'endFrameExclusive':c['endFrameExclusive'],'startPts':c['startPts'],'endPtsExclusive':c['endPtsExclusive'],'framingUpPixels':c['framingUpPixels'],'sampleCount':len(c['samples']),'boards':c['boards'],'observation':n})
dp=P/'chicory-trimmed-playback-partial-v2.dom.txt';dom=dp.read_text(encoding='utf-8')
eventline=next(line.removeprefix('- generic: ') for line in dom.splitlines() if line.startswith('- generic: "['))
events=json.loads(json.loads(eventline))
assert len([x for x in events if x['kind']=='end'])==2
assert events[-1]['kind']=='pause' and events[-1]['key']=='palette-contours' and events[-1]['current']>245.5
play={'schemaVersion':2,'recordedAt':stamp,'events':events,'actualCompletedWindows':2,'plannedWindows':16,'all16TrimmedPlaybackObserved':False,'allIntermediateFramesViewed':False,'fullContinuousListening':False,'screenPixelsObservedForCompletedWindows':False,'failure':'Browser reconnected as IAB3; viewport reported zero width. Semantic click timed out, AX play/pause remained available. Palette requestVideoFrameCallback did not advance; paused manually at378.506268, invalid overshoot133.006268 seconds beyond245.5. No completion inferred. Temporary viewport and visibility overrides restored.','dom':rel(dp),'domSha256':sha(dp),'ax':rel(P/'chicory-trimmed-playback-partial-v2.ax.txt'),'axSha256':sha(P/'chicory-trimmed-playback-partial-v2.ax.txt'),'exactCutsUseNativePtsOnly':True}
new(P/'chicory-trimmed-playback-partial-observations-v2.json',play)
result={'schemaVersion':2,'slug':'limited-color-world','recordedAt':stamp,'execution':rel(ep),'executionSha256':sha(ep),'actualOuterSessionId':33844,'actualOuterExitCode':0,'actualExitDirectlyObserved':'write_stdin aaa6c6, exit0','freshOwnPidAbsent':'exec10e6cc CIM43952 absent','verifiedCuts':verified,'observations':rel(np),'observationsSha256':sha(np),'totalUniqueSourceSamples':283,'newEndpointSamples':40,'reusedSourceSamples':243,'totalBoards':56,'allSamplesAndBoardsDirectlyRead':True,'allHashesAndSelectedNativePtsVerified':True,'exactTrimmedSampleBoundariesApproved':True,'fixed48pxTwoLinePlaceholderFramingSamplesApproved':True,'captionTest':e['captionTest'],'normalSourceActionPlaybackBasis':'chicory-native-playback-observations-v1.json, actual16 starts/ends; native source sample scope','trimmedDynamicFramingPlaybackApproved':False,'allIntermediateNativeFramesViewed':False,'finalCaptionCueApproved':False,'sourceFootageAdopted':False,'publicRightsApproved':False,'newProjectScriptTtsMcOrFinalMedia':False,'currentDistinctCheck':{'exitCode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},'researchManipulated':False,'ownResearchResumeClaim':False,'gitImagesOrMediaAdded':0}
out=P/'chicory-trimmed-sample-direct-review-v2.json';new(out,result);assert ep.read_bytes()==original
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';before=qp.read_bytes();q=json.loads(before)
foreign=json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False)
i=next(i for i in q['items'] if i['slug']=='limited-color-world');assert i['videoId'] is None and not any(i['checkpoints'].values())
i.update(stage='chicory-trimmed-samples-sealed-dynamic-review-pending',trimmedSourceReview=rel(out),trimmedSourceReviewSha256=sha(out),updatedAt=stamp)
i['execution'].update(status='exited',actualOuterExitCode=0,endedObservedAt=stamp)
i['nextAction']='Reuse native sources and existing9250 helper; resolve zero-width browser/independent autopause and observe trimmed dynamic framing. Keep sample approval distinct from final cues and source adoption.'
q['updatedAt']=q['lastProgressAt']=stamp
assert foreign==json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False) and qp.read_bytes()==before
tmp=qp.with_name(qp.name+'.limited-trimmed-seal.tmp');tmp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,qp)
print(json.dumps({'samples':283,'boards':56,'newEndpointFrames':40,'reused':243,'currentDistinctExit':0,'dynamicPlaybackApproved':False,'adopted':False}))
