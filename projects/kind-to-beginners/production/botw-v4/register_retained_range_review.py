"""Record directly inspected, bounded retained-source windows; preserve media."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json

ROOT = Path('D:/Github/VideoEditing')
OWN = ROOT / 'projects/kind-to-beginners/production/botw-v4'
RESEARCH = ROOT / 'projects/kind-to-beginners/production/local/botw-v4/research'
EXPECTED = '7cb6820b1654cfbb1c65aa93d9fbcd747d597488b6c7991297bf3cc97b73d884'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def main():
    path = OWN / 'sources.json'
    before = path.read_bytes()
    assert hashlib.sha256(before).hexdigest() == EXPECTED, 'Source registry changed; re-review before writing'
    sources = json.loads(before)
    original = copy.deepcopy(sources)
    proof_names = [
        'range-extension-20261029/unpacking-launch-contact-1.jpg',
        'range-extension-20261029/unpacking-launch-contact-2.jpg',
        'range-extension-20261029/hike-climbing-contact-1.jpg',
        'range-extension-20261029/hike-walk-contact-1.jpg',
        'range-extension-20261029/hike-glide-contact-1.jpg',
        'range-boundaries-20261029/unpacking-launch-contact-1.jpg',
        'range-boundaries-20261029/unpacking-launch-contact-2.jpg',
        'range-boundaries-20261029/hike-climbing-contact-1.jpg',
        'range-boundaries-20261029/unpacking-launch-063.80.jpg',
    ]
    rows = [
        {
            'cutId': '06-01-a', 'sourceId': 'unpacking-launch',
            'requested': [1.0, 10.7], 'recommended': [1.0, 10.7], 'status': 'usable',
            'observed': 'Opening bedroom unpacking continues: scissors are picked up above the carton at9.5s, carried to the desk drawer, and the drawer is open at10.7s. The added tail is the same native interaction, with no title or album transition.',
            'teachingRole': 'Familiar unpacking and placing objects with a pointer; no claim of a measured button-hold duration.',
        },
        {
            'cutId': '06-01-b', 'sourceId': 'unpacking-launch',
            'requested': [33.0, 38.8], 'recommended': [33.0, 38.8], 'status': 'usable',
            'observed': 'The view pans into the kitchen while a pot is carried to the lower-right cupboard. At37.8s the cursor returns to the carton;38.3s a small red object is carried out;38.8s it reaches the refrigerator. Same kitchen operation, no photo interface.',
            'teachingRole': 'Real object placement supports the first familiar-tidying clause; allow the red-object placement to finish at its native pace.',
        },
        {
            'cutId': '06-03', 'sourceId': 'unpacking-launch',
            'requested': [62.2, 69.133], 'recommended': [63.8, 69.133], 'status': 'trim-start-required',
            'rejected': [62.2, 63.8],
            'observed': '62.2–62.6s shows the album page,62.8–63.0s the dark transition,63.1–63.6s the room fades up. At63.8s the bedroom is fully legible;64–69.133s continues removing the carton and selecting/repositioning clothes on the bed. The earlier start would present album/transition frames as direct object manipulation.',
            'teachingRole': 'Unhurried item relocation; retain useful action rather than stretching the album or fade.',
        },
        {
            'cutId': '07-01', 'sourceId': 'hike-climbing',
            'requested': [8.0, 15.3], 'recommended': [8.0, 15.3], 'status': 'usable-as-path-traversal',
            'observed': 'At8s the character is already on the upper ledge.8–11s runs along the path, around12s descends the next edge briefly airborne,13–15.3s continues along the lower trail. This is not continuous wall climbing.',
            'teachingRole': 'The actual07-01 speech concerns someone directing every next action/path, so traversal is the relevant picture. The editor confirmed this cut is not labeled as wall climbing.',
        },
        {
            'cutId': '08-01-b', 'sourceId': 'hike-walk',
            'requested': [4.15, 11.5], 'recommended': [4.15, 11.5], 'status': 'usable',
            'observed': 'Continuous travel up steps, around the cabin deck, down to the nearby grassy overlook by11–11.5s. Source beyond this target was not adopted as duration padding.',
            'teachingRole': 'Self-directed exploration in the closing example.',
        },
        {
            'cutId': '07-03-c', 'sourceId': 'hike-glide',
            'requested': [6.6, 14.03], 'recommended': [6.6, 14.03], 'status': 'usable-with-takeoff-lead-in',
            'observed': '6.6s is the cliff-edge lead-in; by7.2s the character launches.8–14.03s continues airborne across the ravine with visible wing/flight trails. Do not describe the first6.6s frame as already gliding.',
            'teachingRole': 'Beginning before takeoff preserves before/action/result; editor aligns the voiced glide clause with takeoff.',
        },
        {
            'cutId': '07-03-b', 'sourceId': 'hike-climbing',
            'requested': [3.4, 5.2], 'recommended': [3.4, 5.2], 'status': 'usable-as-wall-climbing',
            'observed': 'Directly inspected2.5,4,5,6,6.2,6.6s states: character ascends the waterfall-adjacent wall at4–5s, reaches the lip around6–6.2s, then walks on top by6.6s.3.4–5.2s lies within the climbing action, separate from07-01 later traversal.',
            'teachingRole': 'Actual wall-climbing picture for the specific wall-climbing clause.',
        },
    ]
    report_rel = rel(OWN / 'retained-source-range-review.json')
    proof = [{'path': rel(RESEARCH / name), 'sha256': sha(RESEARCH / name)} for name in proof_names]
    for source in sources['sources']:
        relevant = [r for r in rows if r['sourceId'] == source['id']]
        if not relevant:
            continue
        assert sha(ROOT / source['file']) == source['sha256'], f"Source bytes changed:{source['id']}"
        source['rangeExtensionReview'] = {
            'record': report_rel,
            'method': 'Direct inspection of bounded decoded still sequences and relevant native-resolution frame; full moving/caption join review remains a final-edit check.',
            'windows': relevant,
        }
    for old, new in zip(original['sources'], sources['sources']):
        stripped = copy.deepcopy(new)
        stripped.pop('rangeExtensionReview', None)
        assert stripped == old, 'Only range evidence may change'
    report = {
        'schemaVersion': 1, 'slug': 'kind-to-beginners', 'revision': 'botw-v4',
        'reviewedAt': datetime.now(timezone.utc).isoformat(),
        'scope': 'Requested retained-source edit-window extensions only; no new footage, narration, TTS, ASR, Unity, final render or platform operation.',
        'method': 'CPU1 one-frame extraction from existing media, direct contact-sheet inspection, native1920x1080 inspection of the uncertain bedroom boundary.',
        'fullMovingPlaybackPerformedInThisAudit': False,
        'actualListeningPerformed': False,
        'humanReviewPerformed': False,
        'rightsAndAudioDecisionsChanged': False,
        'sourceMediaChanged': False,
        'reviewedWindows': rows,
        'proof': proof,
        'frameManifests': [
            {'path': rel(RESEARCH / folder / 'stills.json'), 'sha256': sha(RESEARCH / folder / 'stills.json')}
            for folder in ('range-extension-20261029', 'range-boundaries-20261029')
        ],
        'sourcesBeforeSha256': EXPECTED,
        'remainingCheck': 'Final cut/caption/speech synchronization and normal-speed motion joins must be reviewed after composition. This source-window audit does not substitute for that check.',
    }
    encoded = (json.dumps(sources, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    report['sourcesAfterSha256'] = hashlib.sha256(encoded).hexdigest()
    destination = OWN / 'retained-source-range-review.json'
    assert not destination.exists(), 'Preserve existing audit'
    assert path.read_bytes() == before, 'Concurrent source registry edit detected'
    path.write_bytes(encoded)
    with destination.open('x', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'review': rel(destination), 'reviewSha256': sha(destination), 'sourcesSha256': sha(path)}, indent=2))


if __name__ == '__main__':
    main()
