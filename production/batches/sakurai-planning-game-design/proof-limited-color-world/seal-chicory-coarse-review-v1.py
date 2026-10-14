"""Seal existing directly read source samples; no decode, render or adoption."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp = datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()
def write_new(p, data):
    assert not p.exists(), f'Preserve existing {p}'
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

out = PROOF/'chicory-coarse-direct-review-v1.json'
assert not out.exists()
execution_path = PROOF/'chicory-official-source-execution-v1.json'
execution_bytes = execution_path.read_bytes()
execution = json.loads(execution_bytes)
notes_path = PROOF/'chicory-coarse-observations-v1.json'
notes = json.loads(notes_path.read_text(encoding='utf-8'))
assert execution['pid']==38236 and execution['sessionId']==8506
assert execution['totalSamples']==854 and execution['totalBoards']==143
assert notes['allCoarsePixelsReviewed'] and not notes['sourceAdoptionApproved']
assert all(c['status']=='exited' and c['exitCode']==0 for c in execution['children'])
check = subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
assert check.returncode==0, check.stdout+check.stderr
verified=[]
for i,s in enumerate(execution['sources'], 1):
    assert sha(ROOT/s['localPath'])==s['sha256']
    assert s['wholeDecodeExitCode']==0 and s['nativePtsMonotonic']
    frames=json.loads((ROOT/s['nativePts']).read_text(encoding='utf-8'))['frames']
    assert len(frames)==s['decodedFrames']
    assert all(int(f['best_effort_timestamp'])==n*256 for n,f in enumerate(frames))
    covered=[b for n in notes['observations'] if n['source']==i for b in n['boards']]
    assert covered==list(range(1,len(s['boards'])+1))
    for sample in s['samples']:
        assert sample['pts']==sample['nativeFrame']*256
        assert sha(ROOT/sample['path'])==sample['sha256']
    for board in s['boards']: assert sha(ROOT/board['path'])==board['sha256']
    verified.append({'source':s['key'],'path':s['localPath'],'sha256':s['sha256'],
        'nativePtsPath':s['nativePts'],'nativePtsSha256':sha(ROOT/s['nativePts']),
        'video':s['video'],'decodedFrames':s['decodedFrames'],
        'wholeDecodeExitCode':0,'coarseExtractExitCode':0,
        'allActualNativePtsEqualFrameTimes256':True,
        'directlyReadSampleCount':len(s['samples']),'directlyReadBoardCount':len(s['boards']),
        'samples':s['samples'],'boards':s['boards']})
terminal = {'schemaVersion':1,'recordedAt':stamp,'source':'chicory-b-roll-2',
    'observedProbeExitCode':0,'probeArguments':['ffprobe','-v','error','-select_streams','v:0','-read_intervals','206%','-show_packets','-show_entries','packet=pts,pts_time,dts,dts_time,duration,flags','-of','json'],
    'containerDurationSeconds':'206.983333','metadataNbFrames':12419,
    'actualDecodedNativeFrames':12418,'lastDecodedFrame':{'index':12417,'pts':3178752,'timeSeconds':206.95},
    'observedTerminalPacket':{'pts':3179776,'pts_time':'207.016667','dts':3178496,'dts_time':'206.933333','duration':256,'flags':'_D_'},
    'inference':'The discard-flagged terminal packet beyond container duration is consistent with the metadata count exceeding the decoded native count by one. This is a bounded inference, not a VFR/duplicate-frame diagnosis.',
    'sourceUnmodified':True,'wholeDecodeRepeated':False,'terminalRegionAdopted':False}
write_new(PROOF/'chicory-b-roll-2-terminal-packet-observation-v1.json', terminal)
result={'schemaVersion':1,'slug':'limited-color-world','recordedAt':stamp,
    'scope':notes['reviewScope'],'execution':str(execution_path.relative_to(ROOT)).replace('\\','/'),
    'executionSha256':sha(execution_path),'observations':str(notes_path.relative_to(ROOT)).replace('\\','/'),
    'observationsSha256':sha(notes_path), 'actualOuterSessionId':8506,'actualOuterExitCode':0,
    'outerExitDirectlyObservedInTool':'write_stdin 4956eb; completed exit0',
    'ownPidNotAliveInFreshCim':True,'currentDistinctCheck':{'exitCode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},
    'verifiedSources':verified,'totalSamples':854,'totalBoards':143,
    'allSourceSampleAndBoardHashesVerified':True,'allCoarseSamplesDirectlyRead':True,
    'allIntermediateNativeFramesReviewed':False,'fullContinuousPlaybackReviewed':False,
    'sourceAudioListeningApproved':False,'sourceFootageAdopted':False,'finalCueUiReviewApproved':False,
    'publicRightsApproved':False,'newProjectScriptTtsMcOrFinalMedia':False,
    'researchManipulated':False,'researchResumedByThisWork':False,'gitMediaOrImagesAdded':0}
assert execution_path.read_bytes()==execution_bytes
write_new(out,result)
queue_path=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
before=queue_path.read_bytes(); q=json.loads(before)
other_before=json.dumps([x for x in q['items'] if x['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False)
item=next(x for x in q['items'] if x['slug']=='limited-color-world')
assert item['videoId'] is None and not any(item['checkpoints'].values())
item['stage']='official-chicory-coarse-reviewed-native-action-selection-pending'
item['coarseSourceReview']=str(out.relative_to(ROOT)).replace('\\','/')
item['coarseSourceReviewSha256']=sha(out)
item['execution'].update(status='exited',actualOuterExitCode=0,endedObservedAt=stamp)
item['nextAction']='Inspect exact native action windows and full-size caption/UI pixels before source adoption, independent KOEN narration or scene creation.'
q['updatedAt']=q['lastProgressAt']=item['updatedAt']=stamp
assert json.dumps([x for x in q['items'] if x['slug']!='limited-color-world'],sort_keys=True,ensure_ascii=False)==other_before
assert queue_path.read_bytes()==before
temp=queue_path.with_name(queue_path.name+'.limited-seal.tmp')
temp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,queue_path)
print(json.dumps({'seal':str(out.relative_to(ROOT)).replace('\\','/'),'sampleHashes':854,'boardHashes':143,'directRead':True,'adopted':False,'checkExit':check.returncode},ensure_ascii=False))
