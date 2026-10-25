"""Record actual selected-batch outputs without inferring listening or publication."""
from pathlib import Path
import datetime
import hashlib
import json

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[2]
AUTH = 'explicit-ten-distinctive-shorts-20261025'

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()

def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    batch = read(BATCH / 'batch.json')
    selected = {row['slug']: row for row in batch['projects']}
    work_path = ROOT / 'shared/publishing/shorts-worklist.json'
    work = read(work_path)
    results = []
    for row in work['rows']:
        slug = row.get('slug')
        if slug not in selected:
            continue
        project = ROOT / 'projects' / slug
        state_path = project / 'production/local/finite-finalizer-v1/state.json'
        state = read(state_path) if state_path.exists() else {}
        delivery = state.get('delivery')
        manifest_path = project / 'project.json'
        manifest = read(manifest_path)
        checkpoint_path = project / 'production/checkpoint.json'
        checkpoint = read(checkpoint_path)
        ledger_path = project / 'production/review-ledger.json'
        ledger = read(ledger_path) if ledger_path.exists() else {'schemaVersion':1,'humanFinalReview':False}
        result = dict(slug=slug, order=selected[slug]['order'], stage=state.get('currentStage'),
                      status=state.get('status', 'not-yet-generated'), humanReview='pending')
        if delivery:
            for item in delivery['files']:
                path = Path(item['path'])
                if not path.is_file() or sha(path) != item['sha256']:
                    raise RuntimeError('Delivery missing or changed: ' + str(path))
            if len(delivery['files']) != 4:
                raise RuntimeError('Four exact outputs required: ' + slug)
            result.update(masterSha256=delivery['masterSha256'], directory=delivery['directory'],
                          captioned=delivery['captioned'], title=delivery['title'])
            row.update(status='awaiting-final-review', production='four-local-outputs-generated',
                       review='automated-checks-and-scoped-visual-review; actual-listening-and-human-review-pending',
                       humanReview='pending', platform='not-uploaded', youtube='not-uploaded', drive='not-requested',
                       outputFolder=delivery['directory'], captionedVideo=delivery['captioned'],
                       masterSha256=delivery['masterSha256'], title=delivery['title'], updatedAt=now)
            manifest.update(status='local-review-files-generated', publishReady=False)
            ledger.setdefault('audio', {}).update(ttsGenerated=True, listened=False, asr=True, mix=True)
            ledger['currentDelivery'] = dict(delivery=delivery, recordedAt=now,
                automatedEvidence=delivery['evidence'], humanReview='pending', actualListeningPerformed=False,
                fullMotionPlaybackPerformed=False,
                visualReview='See visual entries for exact sampled frames and hashes; not full-speed playback.')
            checkpoint.update(stage='local-final-review', previewOnly=False, blockedBy=None,
                lastCompleted=['Approved-voice PCM', 'Full unprompted ASR and measured caption alignment',
                    'Native FHD60 visual rendering', 'BGM and four local hashed outputs',
                    'Full video decode and audio signal checks; scoped visual evidence in review ledger'],
                next=['Actual full listening and human review of this exact captioned version'],
                currentDelivery=result)
            if 'actualWork' in checkpoint:
                checkpoint['actualWork'].update(ttsStarted=True, finalOutputs=True,
                    movingFinalReviewComplete=False, actualListeningPerformed=False)
            if 'actualPcmVisualPreparation' in checkpoint:
                checkpoint['actualPcmVisualPreparation'].update(executedAgainstActualPcm=True,
                    actualTimingPrepared=True, finalPlaybackReviewed=False)
        else:
            row.update(production=state.get('status', 'production-in-progress'),
                       review='not-ready-for-final-review', updatedAt=now)
            checkpoint.update(stage=state.get('currentStage', 'production-in-progress'),
                              blockedBy=state.get('reason'), currentProductionState=result)
        checkpoint.update(updatedAt=now, noPlatformMutation=True)
        checkpoint.setdefault('finiteBatchRuntime', {}).update(snapshotAt=now, snapshotState=result['status'],
            internalListening='pending', actualHumanReview='pending')
        write(manifest_path, manifest)
        write(ledger_path, ledger)
        write(checkpoint_path, checkpoint)
        results.append(result)
    if set(r['slug'] for r in results) != set(selected):
        raise RuntimeError('Selected worklist rows incomplete')
    work['updatedAt'] = now
    write(work_path, work)
    count = sum('masterSha256' in r for r in results)
    checkpoint_path = BATCH / 'checkpoint.json'
    checkpoint = read(checkpoint_path)
    checkpoint.update(updatedAt=now, stage='local-final-review' if count == 10 else 'production-and-repair',
        generatedVideos=count, requestedVideos=10, projects=sorted(results, key=lambda r:r['order']),
        remaining=['Actual listening and human final review'] if count == 10 else ['Finish remaining selected productions and QA'],
        humanReview='pending', youtubeActionsPerformed=False, driveActionsPerformed=False)
    write(checkpoint_path, checkpoint)
    print(json.dumps({'generatedVideos':count, 'requestedVideos':10, 'humanReview':'pending'}))

if __name__ == '__main__':
    main()
