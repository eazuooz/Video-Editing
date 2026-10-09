"""Seal this already-performed manual source review; create no project or footage approval."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def save(p, data, expected_bytes=None):
    if expected_bytes is not None:
        assert p.read_bytes() == expected_bytes, 'Concurrent writer changed file; preserve it'
    tmp = p.with_name(p.name + '.score-preflight.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if expected_bytes is not None:
        assert p.read_bytes() == expected_bytes, 'Concurrent writer changed file; preserve it'
    os.replace(tmp, p)

def main():
    result = HERE/'source-direct-review-v1.json'
    assert not result.exists(), 'Existing sealed review preserved; do not repeat'
    notes = json.loads((HERE/'source-observation-notes-v1.json').read_text(encoding='utf-8'))
    stamp = datetime.now(timezone.utc).isoformat()
    for source in notes['sources']:
        ep = ROOT/source['sourceReviewExecution']
        execution = json.loads(ep.read_text(encoding='utf-8'))
        assert execution['exitCode'] == 0 and execution['wholeDecodeExit'] == 0
        assert sha(Path(execution['rawPath'])) == source['expectedSha256'] == execution['sha256']
        assert source['reviewedBoardNumbers'] == list(range(1,len(execution['boards'])+1))
        assert execution['samples'] == source['reviewedSampleCount']
        entries = []
        for board in execution['boards']:
            assert sha(Path(board['path'])) == board['sha256']
            for entry in board['entries']:
                assert sha(Path(entry['path'])) == entry['sha256']
                entries.append(entry['index'])
        assert entries == list(range(1, execution['samples']+1))
        source['technicalEvidence'] = {
            'executionSha256':sha(ep), 'rawPath':execution['rawPath'],
            'bytes':execution['bytes'], 'durationSeconds':execution['durationSeconds'],
            'wholeDecodeExit':0, 'originalDecodeNotRepeated':True,
            'allSampleAndBoardHashesMatched':True,
            'boards':execution['boards'], 'technicalExecutionRetainedUnchanged':True
        }
    notes.update(reviewedAt=stamp, status='sample-observation-sealed-native-adoption-pending',
                 totalBoards=42, totalSamples=246, allListedBoardsDirectlyRead=True,
                 evidenceHashesMatched=True)
    save(result, notes)
    qp = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    qb = qp.read_bytes()
    queue = json.loads(qb)
    item = next(x for x in queue['items'] if x['slug']=='presenting-game-scores')
    assert item['videoId'] is None and all(not v for v in item['checkpoints'].values())
    item.update(status='in-progress', stage='official-source-preflight-native-adoption-pending',
                requiredFutureExplanationStyle='research-black-v1',
                explanationStylePolicy='shared/publishing/explanation-style-policy.json')
    item['preflight'] = {
        'duplicateReport':'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json',
        'contentAndStudioDirectReview':'production/batches/sakurai-planning-game-design/proof-presenting-game-scores/content-studio-direct-review-v1.json',
        'verdict':'distinct',
        'inputsDigest':'091c2ba9c0d343ee40964d600e5dd8227be0f2990996e302f95b59badbf35f3c',
        'duplicateCheckExit':0,
        'sourceObservation':str(result.relative_to(ROOT)).replace('\\','/'),
        'sourceObservationSha256':sha(result),
        'officialSourcesTechnicallyVerified':2, 'observationBoardsRead':42,
        'observationSamplesRead':246, 'nativeIntervalsApproved':False,
        'footageAdopted':False, 'newProjectCreated':False,
        'needsCurrentDuplicateCheckBeforeProjectCreation':True,
        'recordedAt':stamp
    }
    item['ownedJob'] = {
        'type':'local-native-source-preview-helper', 'pid':27140,
        'sessionId':34307, 'creationDate':'2026-10-09T10:34:26.837781+09:00',
        'commandLine':'"C:\\Users\\eazuo\\miniconda3\\envs\\renderformer\\python.exe" -X utf8 production/batches/sakurai-planning-game-design/proof-presenting-game-scores/serve-native-review-v1.py',
        'url':'http://127.0.0.1:9250/',
        'status':'last-observed-running; verify actual command and creation before reuse',
        'cpuThreads':None, 'gpu':0, 'heavyWorkerRunning':False,
        'resourceObservation':'production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-resource-observation-v2.json',
        'researchPauseOrProcessChanges':0
    }
    item['closedSourceJobs'] = [
        {'name':'ballionaire-launch','sessionId':32685,'pid':28260,'exitCode':0},
        {'name':'balatro-official','sessionId':28001,'pid':51436,'exitCode':0}
    ]
    item['nextAction'] = notes['nextAction']
    item['blockers'] = []
    queue['progress'].update(inProgress=1, queued=7, remaining=8, remainingProduction=8)
    queue['currentSlug']='presenting-game-scores'
    queue['lastCompletedSlug']='similar-game-design'
    queue['updatedAt']=queue['lastProgressAt']=stamp
    save(qp, queue, qb)
    print(json.dumps({'sealed':str(result),'sha256':sha(result),'boards':42,'samples':246,
                      'sourceAdoption':False,'newProject':False,'tts':False,
                      'completedPrivate':15,'remaining':8},ensure_ascii=False))

if __name__ == '__main__':
    main()
