"""Record only this episode's observed local delivery; never imply human review."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from storage_paths import repo_path, relative


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['paths', 'record'])
    args = parser.parse_args()
    if PROJECT.name not in ['limited-color-world', 'computer-controlled-players']:
        raise ValueError('Only the two assigned finite-batch episodes are supported')
    plan = read(HERE / 'edit-plan.json')
    edit = repo_path(plan['outputDir'])
    manifest_path = PROJECT / 'project.json'
    manifest = read(manifest_path)
    prefix = plan['outputDir'] + '/' + plan['outputStem']
    paths = {'videoBurnedCaptions': prefix + '-captioned.mp4',
             'videoClean': prefix + '-clean.mp4',
             'captionsKo': plan['outputDir'] + '/captions.ko.srt',
             'captionsEn': plan['outputDir'] + '/captions.en.srt',
             'captionAlignment': plan['outputDir'] + '/caption-alignment.json'}
    for value in paths.values():
        if not repo_path(value).is_file():
            raise ValueError('Required current local output missing: ' + value)
    manifest['paths'].update(paths)
    manifest['publishReady'] = False
    manifest['membershipOutro'] = {'enabled': True, 'appliedToFinal': True,
                                   'frames': plan['outroFrames'], 'source': plan['membershipFile']}
    if args.stage == 'paths':
        save(manifest_path, manifest)
        print('Current explicit four-output paths recorded; user review remains pending')
        return
    structural_path = edit / 'structural-verification.json'
    structural = read(structural_path)
    visual_path = HERE / 'visual-review.json'
    visual = read(visual_path)
    audio_path = edit / 'qa/audio-continuity.json'
    audio = read(audio_path)
    collection_path = PROJECT / 'production/delivery-output.json'
    collection = read(collection_path)
    if structural['status'] != 'pass' or len(collection['files']) != 4:
        raise ValueError('Both verified masters and exact four-file collection are required')
    for file in collection['files']:
        if sha(repo_path(file['source'])) != file['sha256']:
            raise ValueError('Current delivery source bytes changed')
        if sha(repo_path(collection['directory'] + '/' + file['name'])) != file['sha256']:
            raise ValueError('Collected file bytes changed')
    actual_hash = sha(repo_path(paths['videoBurnedCaptions']))
    if structural['outputs']['captioned']['sha256'] != actual_hash:
        raise ValueError('Structural verification belongs to another master')
    asr_review_path = HERE / 'final-comparison-review.json'
    asr_review = read(asr_review_path) if asr_review_path.exists() else {}
    asr_done = (asr_review.get('fullTextDirectlyCompared') is True
                and asr_review.get('encodedAudioPacketsSha256') == structural['outputs']['captioned']['audioPacketsSha256'])
    state = 'local-review-ready' if asr_done else 'final-audio-asr-pending'
    now = datetime.now(timezone.utc).isoformat()
    status = {'schemaVersion': 1, 'slug': PROJECT.name, 'revision': 'batch-v1',
              'status': state, 'stage': 'local-final-review' if asr_done else 'four-local-outputs-internal-qa',
              'fourOutputsVerified': True, 'durationSeconds': plan['totalFrames'] / 60,
              'captionedSha256': actual_hash, 'localFiles': paths,
              'localOutputDirectory': collection['directory'],
              'localIndex': collection['directory'] + '/index.html',
              'technicalSummary': 'Both complete 1080p60 masters decoded; exact native frame/PTS grid and identical AAC verified; collected four-file hashes match.',
              'audioSummary': {'measurementStatus': audio['status'],
                               'transferFlags': len(audio.get('flaggedVoiceTransferWindows', [])),
                               'sourceCadenceCandidates': len(audio.get('sustainedLocalDropCandidates', [])),
                               'finalEncodedAsr': 'complete root text comparison; exact same AAC verified' if asr_done else 'pending root final comparison',
                               'wholeListening': 'pending'},
              'visualSummary': visual, 'humanReview': 'pending', 'humanListening': 'pending',
              'evidence': {'structural': relative(structural_path), 'visual': relative(visual_path),
                           'audioContinuity': relative(audio_path), 'collection': relative(collection_path)},
              'uploadAuthorized': False, 'schedulingAuthorized': False, 'updatedAt': now}
    save(HERE / 'review-status.json', status)
    manifest.update(status=state, updatedAt=now)
    manifest['currentRevision'].update(status=state, productionComplete=asr_done,
                                       humanFinalReview='pending')
    manifest['approvals'].update(render=True, qa=asr_done, collected=True, uploaded=False)
    manifest['finalRender'] = {'status': state,
                               'captionedSha256': actual_hash, 'durationSeconds': plan['totalFrames'] / 60,
                               'openItems': ([] if asr_done else ['최종 인코딩 음성의 루트 ASR 대조 대기']) + ['실제 사람의 전체 청취·최종 검수 대기']}
    manifest['paths'].update(reviewStatus=relative(HERE / 'review-status.json'),
                             deliveryIndex=status['localIndex'], outputDirectory=collection['directory'])
    save(manifest_path, manifest)
    checkpoint = read(HERE / 'checkpoint.json')
    checkpoint.update(status=state, stage=status['stage'],
                      updatedAt=now, reviewStatus=relative(HERE / 'review-status.json'),
                      nextAction='Local human final review only; no upload authorized.' if asr_done else 'Root final encoded ASR comparison; then local human final review only.',
                      actualHumanListening=False, uploadAuthorized=False, automaticNextVideo=False,
                      captionedSha256=actual_hash, localOutputDirectory=collection['directory'])
    save(HERE / 'checkpoint.json', checkpoint)
    print(json.dumps({'status': status['status'], 'duration': status['durationSeconds'],
                      'captionedSha256': actual_hash, 'index': status['localIndex']}))


if __name__ == '__main__':
    main()
