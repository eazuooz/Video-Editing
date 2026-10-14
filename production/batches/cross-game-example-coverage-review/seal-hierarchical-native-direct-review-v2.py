"""Seal the remaining33 actually read boards, inheriting the prior31 without replay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import psutil

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,o):
    t=p.with_name(p.name+'.'+str(os.getpid())+'.writing')
    t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
out=V/'native-candidate-direct-review-v2.json'
assert not out.exists(), 'Completed direct review must not be repeated'
previous_path=V/'native-candidate-partial-direct-review-v1.json'
previous=read(previous_path)
assert previous['viewedBoardCount']==31 and previous['reviewedBoundNativeSampleCount']==181
closed=read(V/'native-candidate-extraction-execution-v1.session.json')
assert closed['actualOuterExitCode']==0 and closed['exactWorkerDead'] and closed['exactChildrenDead']
groups=[]
for g in previous['groups']:
    assert sha(ROOT/g['indexPath'])==g['indexSha256']
    groups.append(dict(**g,reviewMode='Exact unchanged index SHA inherits the31 already read boards and181 file hashes; no reread/replay/re-extraction.'))
for name,boards_count,samples_count in [('storm-conditions',7,37),('storm-building-ui',26,153)]:
    index_path=V/'native-candidate-pixels-v1'/name/'index.json';index=read(index_path)
    assert len(index['boards'])==boards_count and len(index['samples'])==samples_count
    for item in index['boards']+index['samples']:
        assert sha(ROOT/item['path'])==item['sha256'],item['path']
    groups.append(dict(group=name,indexPath=index_path.relative_to(ROOT).as_posix(),indexSha256=sha(index_path),
        sourceSha256=index['localSourceSha256'],boardCount=boards_count,sampleCount=samples_count,
        allBoardsDirectlyViewed=True,allBoundSampleFileHashesMatched=True,
        allFullResolutionSourceFramesIndividuallyViewed=False,finalCutApproval=False,
        viewedBoards=[dict(path=b['path'],sha256=b['sha256'],sampleIndices=b['sampleIndices']) for b in index['boards']],
        reviewMode='Directly read all33new boards/190bound sample images. Building boards1..21 were completed earlier; only22..26 were read after continuation.'))
proof=dict(schemaVersion=2,reviewedAt=now(),previousReview=dict(path=previous_path.relative_to(ROOT).as_posix(),sha256=sha(previous_path)),
    viewedBoardCount=64,reviewedBoundNativeSampleCount=371,newBoardsDirectlyRead=33,newNativeSamplesBound=190,
    completedBoardRereads=0,groups=groups,findings=previous['findings']+[
        'Against the Storm official developer1.5preview qaK2FWQB7DE:315..675 Forge conditions/effects/penalty/result panels and radial menus are explanation-led. The console good.addall at355s is developer injection, not normal earned resources.555..625s road/world placement is a candidate only, not final quota.',
        'Storm2930..2938 Shelter placement/footprints,2959..2970 roof/construction,2990..3018 Mine selection/construction UI,3080..3116 Small Fishing Hut placement/bait configuration are precise-action candidates. Paused PRESS SPACE TO RESUME housing2950-era screens, ambient forest pans and long static tooltips are excluded from action quota.',
        'Storm developer console at3030..3040(effect.add FishScraps),3204..3208,3268..3272(MasterBlueprint) and3460 is excluded. Do not infer normal unlock/resource acquisition or production output.3372s shows You Lost; it must not be narrated as success.',
        'Storm3384..3452 shows caravan/embarkation/map/settings and a start-game confirmation.3456 is loading,3460 console,3464..3484 paused-world/Haunted Druids Hut ruin panel,3488 yellow encounter flash. These last27 samples add no selected normal-action quota; ruin outcomes and hidden face-obscured fields are not inferred.',
        'Storm source face overlays shift from lower-left to lower-right. Needed world/controls must be directly visible outside the overlay before selecting a cut; masking faces does not recover obscured original UI. Full-resolution native UI, actual1x precise intervals, narration tracking and final960/970 caption clearance remain pending.'
    ],all64CandidateBoardsReviewed=True,fourGameTeachingApproved=False,
    allSourceIntermediateFramesApproved=False,finalActionSelectionApproved=False,newNarrationWritten=False,
    humanWholeListeningApproved=False,publicRightsApproved=False,imagesLocalOnly=True,
    extractionTimingLimitation='The v1 extraction selected exactly371bounded native PTS. Its output -to argument did not stop sparse selection decoding at the intended endpoint; it may scan later source frames. No repeated standalone whole-QA decode was run. Future v2 uses input -t before -i.',
    next='Reuse actual additional Timberborn source-acquisition v2 session36150/current state. After actual outer exit and closure, extract only new Timberborn discovery pixels and new precise action points; do not repeat completed371samples/64boards, original3downloads/whole-decodes or recorded normal intervals.')
save(out,proof)
state_path=V/'source-acquisition-execution-v2.json';state=read(state_path)
worker=state['worker'];alive=False;actual=None
try:
    p=psutil.Process(worker['pid']);alive=abs(p.create_time()-worker['createTime'])<.02
    if alive:
        actual=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd())
        assert actual['command']==worker['command'] and actual['cwd']==worker['cwd']
except psutil.NoSuchProcess:pass
cp_path=V/'latest-checkpoint.json';raw=cp_path.read_bytes();cp=read(cp_path)
cp.update(recordedAt=proof['reviewedAt'],nativeCandidateDirectReview=out.relative_to(ROOT).as_posix(),
    candidateBoardsViewed=64,candidateNativeSamplesBound=371,timberbornShortHeld=True,fourGameTeachingApproved=False,
    activeOwnedWorkers=int(alive),additionalSourceExecution=state_path.relative_to(ROOT).as_posix(),
    additionalSourceOuterSession=36150,additionalSourceOuterExitCode=state['actualOuterExitCode'],
    actualAdditionalSourceWorker=actual,next=proof['next'])
assert cp_path.read_bytes()==raw;save(cp_path,cp)
qpath=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';raw=qpath.read_bytes();q=read(qpath)
q['currentHierarchicalReview'].update(nativeCandidateDirectReview=out.relative_to(ROOT).as_posix(),candidateBoardsViewed=64,
    candidateNativeSamplesBound=371,stage='all-first64-candidate-boards-reviewed;additional-timberborn-source-running',
    activeOwnedWorkers=int(alive),actualAdditionalSourceWorker=actual)
q.update(updatedAt=proof['reviewedAt'],next=proof['next'])
assert qpath.read_bytes()==raw;save(qpath,q)
print(json.dumps(dict(boardsViewed=64,nativeSamplesBound=371,newBoardsRead=33,priorBoardRereads=0,
    additionalSourceWorkerAlive=alive,additionalSourceWorker=actual,fourGameTeachingApproved=False)))
