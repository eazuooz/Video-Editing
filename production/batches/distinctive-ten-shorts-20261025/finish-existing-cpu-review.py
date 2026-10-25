"""Inspect/copy already encoded local masters with software-only QA.

This command cannot create speech, capture scenes, run ASR, or encode masters.
It uses the same serial lock, authorization, input hashes, and output checks.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sys

BATCH = Path(__file__).resolve().parent
sys.path.insert(0, str(BATCH))
spec = importlib.util.spec_from_file_location('finalizer', BATCH / 'finish-ready-videos.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slug', required=True)
    args = parser.parse_args()
    f.authorization(args.slug)
    with f.SerialJobLock(slug=args.slug, stage='existing-media-cpu-review', wait_seconds=0) as lock:
        job = f.ProjectRun(args.slug, lock, retry=True)
        required = ['voice-asr', 'strict-caption-timing', 'visual-render', 'audio-mix',
                    'audio-report', 'mix-asr', 'video-pair']
        required.append('unity-capture' if args.slug in f.UNITY else 'actual-visual-preparation')
        for name in required:
            previous = job.state['stages'].get(name, {})
            if previous.get('status') != 'pass':
                raise RuntimeError('Existing production stage is not complete: ' + name)
            f.verify_artifacts(previous['artifacts'])
        final = Path(job.state['stages']['video-pair']['result']['directory'])
        masters = {str(final / name): f.sha(final / name) for name in ('clean.mp4', 'captioned.mp4')}
        routes = dict(f.commands(args.slug))
        source = (job.project / 'production/finish-video.py').read_text(encoding='utf8').lower()
        if any(word in source for word in ('nvenc', 'cuda', 'hwaccel', 'videotoolbox', 'qsv')):
            raise RuntimeError('This review script has not been verified as software-only.')

        def stage(name, function):
            job.current = name
            f.authorization(job.slug)
            f.require_readiness(job.slug)
            previous = job.state['stages'].get(name)
            if previous and previous.get('status') == 'pass':
                f.verify_artifacts(previous['artifacts'])
                return previous['result']
            lock.set_stage('existing-media-cpu-review:' + name)
            job.state.update(status='running', currentStage=name)
            job.state['stages'][name] = dict(status='running', startedAt=f.now(),
                resources={'cpuOnlyExistingMediaReview':True, 'gpuUsed':False,
                           'newMasterOrVoiceProduced':False, 'userGameNotModified':True})
            job.save()
            result, outputs = function()
            job.state['stages'][name].update(status='pass', endedAt=f.now(), result=result,
                                           artifacts=[f.artifact(path) for path in outputs])
            job.save()
            return result

        stage('video-integrity', lambda: job.simple('video-integrity', routes['video-integrity'], [final / 'integrity.json']))
        def qa():
            job.run('qa-artifact-generation', routes['qa-artifact-generation'])
            index = final / ('qa-sequential-' + f.sha(final / 'captioned.mp4')[:12]) / 'index.json'
            return dict(generatedOnly=True, humanViewed=False), [index, final / 'mobile-review.mp4']
        stage('qa-artifact-generation', qa)
        if any(f.sha(Path(path)) != digest for path, digest in masters.items()):
            raise RuntimeError('An encoded master changed during read-only inspection.')
        delivery = stage('local-delivery', lambda: job.deliver(final))
        job.state.update(status=delivery['status'], currentStage='local-delivery', delivery=delivery,
            generatedForReview=True, internalVisualReview='see-hash-bound-review-ledger',
            internalListeningReview='pending', actualHumanReview='pending',
            humanReview='pending', completeListening='pending', fullMovingReview='pending',
            platformActionsPerformed=False, softwareOnlyReviewCompleted=True)
        job.save()
        print(json.dumps({'slug':args.slug, 'captioned':delivery['captioned'],
                          'masterSha256':delivery['masterSha256'], 'gpuUsed':False}))

if __name__ == '__main__':
    main()
