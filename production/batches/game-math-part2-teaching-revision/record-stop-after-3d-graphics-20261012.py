"""Record a future stop boundary without interrupting unfinished Part 2 work."""
from pathlib import Path
import datetime,json,os

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,value):
    tmp=p.with_name(p.name+'.tmp-'+str(os.getpid()))
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    os.replace(tmp,p)

queue=read(B/'queue.json')
terminal='game-math-normal-transform-uv'
assert queue['items'][-1]['slug']==terminal
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
policy=dict(
    schemaVersion=1,recordedAt=now,
    userEvidence='3차원 그래픽스까지 끝나면 작업 일단 중단해줘~',
    scope='This task and its owned Game Math Part 2 continuation',
    stopAfterSlug=terminal,
    stopAfterTitleKo=queue['items'][-1]['titleKo'],
    remainingOwnedSlugs=[item['slug'] for item in queue['items']],
    completionBoundary='Finish required teaching/four-game revisions, reviewed renders, output collection, private uploads, publishing settings, actual schedule replacements, corresponding authorized baseline handling and selective Git delivery through the final 3D graphics lesson.',
    unfinishedWorkRemainsActive=True,
    startSubsequentLectures=False,
    startRemainingSakuraiSix=False,
    supersedes='Earlier continuation from current unpublished revisions to six new Sakurai/game-design productions',
    actionAtBoundary='Pause this task and any owned continuation; preserve completed reservations and checkpoints; report completion and the pause.',
    resumeAfterBoundaryRequiresExplicitUserInstruction=True,
    pauseTriggered=False,
    unrelatedProcessesOrAutomationsModified=False,
)
record=B/'stop-after-3d-graphics-20261012.json'
write(record,policy)
queue['execution'].update(
    stopAfterSlug=terminal,
    stopAfterScope='Game Math Part 2 through the final 3D graphics lesson',
    stopAfterCompletionRecord=record.relative_to(ROOT).as_posix(),
    stopAtBoundaryRequested=True,
    startSubsequentLectures=False,
    startRemainingSakuraiSix=False,
    resumeAfterBoundaryRequiresExplicitUserInstruction=True,
)
queue['authorization']['nextBatchAfterPart2']='Pause; explicit new user instruction required'
write(B/'queue.json',queue)
assert read(B/'queue.json')['execution']['mode']==queue['execution']['mode']
print(json.dumps(dict(stopAfterSlug=terminal,currentMode=queue['execution']['mode'],pauseTriggered=False,record=record.relative_to(ROOT).as_posix())))
