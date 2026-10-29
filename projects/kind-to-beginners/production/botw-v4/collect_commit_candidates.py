"""Collect D29-only candidate paths; no Git or shared-file writes."""
from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
LOCAL = PROJECT / 'production/local/botw-v4'
EXCLUDED = {
    'label-assets-draft-semantic-v3.json', 'label-assets-draft-semantic-v4.json',
    'native-compile-attempt-01.json', 'native-compile-request.json',
    'native-readiness.json', 'native-repair-01.json', 'native-repair-03-staged.json',
    'native-representative-v2.json', 'native-representative-v3.json',
    'native-representative-v4-v5.json', 'timing-lock.draft.json',
    'timing-proposal.json', 'caption-text-layout-precheck.json',
    'review-server.json',  # PID/port state is runtime-only, not reusable production source.
}
SHARED = ['shared/publishing/video-production-control.json',
          'shared/publishing/video-worklist.json', 'docs/VIDEO_WORKLIST.md',
          '.gitignore', 'shared/git-essential-images.json']
FINAL_PROJECT = ['project.json', 'rebuild.json', 'production/delivery-output.json',
                 'production/review-ledger.json']
FINAL_REVISION = ['pixel-review.json', 'native-review.json', 'audio-review.json',
                  'review-status.json', 'checkpoint.json', 'essential-label-images.json',
                  'gameplay-delta-pixel-review.json']


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def rel(path):
    return path.relative_to(ROOT).as_posix()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def main():
    native = read(LOCAL / 'git-native-required-paths.json')
    paths = set(native['paths'])
    categories = {'nativeRequired': list(native['paths']), 'productionSourcesAndEvidence': [],
                  'script': [], 'projectFinalMetadata': [], 'sharedScopedOverlayOnly': SHARED}
    excluded, anticipated = [], []
    for path in HERE.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        if path.name in EXCLUDED:
            excluded.append(rel(path))
            continue
        assert path.suffix in {'.py', '.json', '.cjs', '.cs', '.md', '.txt'}, path
        paths.add(rel(path))
        categories['productionSourcesAndEvidence'].append(rel(path))
    for path in (PROJECT / 'script/botw-v4').iterdir():
        if path.is_file():
            paths.add(rel(path))
            categories['script'].append(rel(path))
    for base, names, category in [(PROJECT, FINAL_PROJECT, 'projectFinalMetadata'),
                                   (HERE, FINAL_REVISION, 'productionSourcesAndEvidence')]:
        for name in names:
            path = base / name
            if path.is_file():
                paths.add(rel(path))
                if rel(path) not in categories[category]:
                    categories[category].append(rel(path))
            else:
                anticipated.append(rel(path))
    paths.update(SHARED)
    paths = sorted(paths)
    assert len(native['paths']) == 430 and set(native['paths']).issubset(paths)
    assert all((ROOT / path).is_file() for path in paths)
    assert not any('/production/local/' in path or '/Preflight/' in path or '/ThirdParty/' in path for path in paths)
    pngs = {p for p in paths if Path(p).suffix == '.png'}
    expected = {a['assetPath'] for a in read(HERE / 'label-assets-measured-v2.json')['assets']}
    assert len(pngs) == 89 and pngs == expected
    for path in paths:
        assert (path in SHARED or path.startswith('projects/kind-to-beginners/')
                or path.startswith('unity/VideoEditing/Assets/VideoScenes/')
                or path == 'unity/VideoEditing/Assets/VideoScenes.meta'), path
    candidate = LOCAL / 'git-final-candidate-paths.json'
    anticipated_path = LOCAL / 'git-final-anticipated-paths.json'
    save(candidate, paths)
    save(anticipated_path, sorted(set(anticipated)))
    report = {
        'schemaVersion': 1, 'revision': 'botw-v4', 'status': 'candidate-scope-prepared-not-staged',
        'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'candidatePathList': rel(candidate), 'candidatePathListSha256': sha(candidate),
        'count': len(paths), 'anticipatedPathList': rel(anticipated_path),
        'anticipated': sorted(set(anticipated)), 'categories': categories, 'excluded': excluded,
        'preservedOnDisk': True,
        'necessaryDraftNamedInput': {
            'path': rel(HERE / 'unity-teaching-cues.draft.json'),
            'reason': 'Current build_edit.lock() directly reads this semantic input; the name is historical, but this is a required authored source.',
        },
        'necessaryPreBindingInputs': {
            'paths': [rel(HERE / 'edit-plan.before-native-binding.json'), rel(HERE / 'production-plan.before-native-binding.json')],
            'reason': 'bind_native.py reads these original plans for guarded binding and preservation.',
        },
        'nativeSummary': {'requiredPaths': 430, 'savedFinalScenes': 22, 'finalLabelPng': 89,
                          'labelMetaAndSourceIncluded': True, 'vendorFilesAdded': 0,
                          'preflightScenesAdded': 0, 'unreferencedGeneratedAssetsAdded': 0},
        'commitHelper': {'path': rel(HERE / 'scoped_commit.py'), 'sha256': sha(HERE / 'scoped_commit.py'),
                         'basedOn': 'production/batches/design-25-30-review-actions-20261029/commit_scope.py',
                         'sharedHelperModified': False, 'syntax': 'AST parse passed; commit helper not executed'},
        'diffImpactReview': [
            'The original batch helper overlays six batch rows and four older thumbnails. The copied D29 helper limits rows to D29, maps only final89scene-label PNGs, and has no thumbnail inventory.',
            'Control overlay changes only the selectedD29Revision branch. Other authorizations and unrelated bytes remain intact.',
            'Worklist overlay changes selected D29 production/review fields only; videoId/url/upload fields are excluded. Evidence and authorized prior-master history append to the destination state.',
            'Markdown overlay changes D29 production/review/platform columns only; titles, order and other rows remain intact.',
            'Image registry and ignore overlays include exact final89D29label entries/exceptions only.',
            'Temporary isolated indices, original-index backup, foreign-index checks and source/index/HEAD CAS guards are retained. Push remains explicit.',
            'This is a candidate path list, not an assertion every path is modified. Root must inspect the final dry-run after metadata completion.',
        ],
        'remainingRootSteps': [
            'Complete final metadata and final89label registration, then rerun this light collector to resolve anticipated paths.',
            'Read the D29-only commit dry-run and final exact changed paths before --execute.',
            'Preserve all other index entries and working files; do not bulk add local media or the repository.',
        ],
        'noGitOrSharedMutation': True,
    }
    save(LOCAL / 'git-final-candidate-scope-review.json', report)
    print(json.dumps({'candidates': len(paths), 'native': 430, 'labels': 89,
                      'anticipated': anticipated, 'candidateSha256': sha(candidate)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
