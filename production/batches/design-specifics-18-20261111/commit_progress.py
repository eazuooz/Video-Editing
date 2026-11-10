"""Record only the selected Design Specifics batch and its worklist rows."""

import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = HERE.relative_to(ROOT).as_posix()
SCENES = 'motion-canvas/src/projects/design-specifics/'
CONTROL = 'shared/publishing/video-production-control.json'
WORKLIST = 'shared/publishing/video-worklist.json'
TABLE = 'docs/VIDEO_WORKLIST.md'
IDS = {f'DS{i:02}' for i in range(1, 19)}
KEY = 'designSpecifics18Selected20261111'
START = '<!-- DESIGN-SPECIFICS-18-20261111-START -->'
END = '<!-- DESIGN-SPECIFICS-18-20261111-END -->'

helper = ROOT / 'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
import_spec = importlib.util.spec_from_file_location('scoped_design_specifics_commit', helper)
scoped = importlib.util.module_from_spec(import_spec)
import_spec.loader.exec_module(scoped)


def overlay(name, raw, spec):
    if name == CONTROL:
        return scoped.patch(raw, [KEY], spec['control'])
    if name == WORKLIST:
        for row in spec['rows']:
            raw = scoped.upsert(raw, 'rows', 'id', row)
        return raw
    if name == TABLE:
        first = raw.find(START.encode())
        last = raw.find(END.encode())
        assert (first < 0) == (last < 0) and first <= last
        newline = '\r\n' if b'\r\n' in raw else '\n'
        block = spec['worklistMarkdown'].replace('\n', newline).encode()
        if first >= 0:
            return raw[:first] + block + raw[last + len(END):]
        return raw + (newline * 2).encode() + block + newline.encode()
    raise AssertionError(name)


def validate(spec):
    assert spec['scope'] == KEY and {row['id'] for row in spec['rows']} == IDS
    assert not spec['control']['youtubeAuthorized'] and not spec['control']['recurringAutomationAuthorized']
    for name in spec['ownedPaths']:
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts and 'local' not in path.parts
        assert name.startswith((BATCH + '/', SCENES))
        assert path.suffix in {'.json', '.md', '.py', '.tsx', '.ts', '.cjs'}
        assert (ROOT / name).is_file()
    return sorted(spec['ownedPaths']) + sorted(scoped.SHARED)


def prepare():
    data = json.loads((HERE / 'batch.json').read_text(encoding='utf-8'))
    rows = []
    table = [START, '', '## 게임 설계 디테일 18편', '',
             '[편별 검수와 제작 계획](../' + BATCH + '/reference-review.md)', '',
             '| 순서 | 영상 | 제작 상태 | 사용자 검수 | YouTube |', '|---|---|---|---|---|']
    for ep in data['episodes']:
        assert ep['id'] in IDS
        draft = bool(ep.get('draftOutline'))
        state = '한영 대본 초안 · 게임 구간 확인 중' if draft else '참고 영상 검수·구성 정리 · 게임 자료 확인 중'
        ready = bool(ep.get('deliveryManifest'))
        if ready:
            state = '1080p60 로컬 4종 완성'
        status = '최종 검수 대기' if ready else '제작 후 검수'
        row = {'id': ep['id'], 'slug': 'design-specifics-' + str(ep['order']).zfill(2),
               'series': 'DS', 'seriesOrder': ep['order'], 'title': ep['workingTitle'],
               'productionComplete': ready, 'productionStatus': state, 'executionStatus': '제작 선택',
               'reviewStatus': status, 'humanApproval': None, 'platformStatus': '미업로드',
               'localMasterAvailable': ready, 'latestRulesPassed': None, 'notes': '',
               'sourceEvidence': ep['referenceUrl'], 'evidence': [BATCH + '/batch.json']}
        if ready:
            row['localDelivery'] = ep['deliveryManifest']
        rows.append(row)
        table.append(f"| {row['id']} | {row['title'].replace('|', '/')} | {state} | {status} | 미업로드 |")
    table += ['', END]
    sources = [file for directory in (HERE, ROOT / SCENES) for file in directory.rglob('*')
               if file.is_file() and file.suffix in {'.json', '.md', '.py', '.tsx', '.ts', '.cjs'}
               and 'local' not in file.relative_to(ROOT).parts]
    spec = {'scope': KEY, 'control': {
        'status': data['status'], 'selectedAt': data['startedAt'], 'scope': data['userSelection'],
        'batch': BATCH + '/batch.json', 'referencePlaylist': data['referencePlaylistUrl'],
        'episodes': [row['id'] for row in rows], 'productionTarget': 'local-final-review-four-files',
        'automaticAdvanceWithinSelectedPlaylist': True, 'recurringAutomationAuthorized': False,
        'humanFinalReviewRequired': True, 'youtubeAuthorized': False, 'driveAuthorized': False,
    }, 'rows': rows, 'worklistMarkdown': '\n'.join(table),
        'ownedPaths': sorted(file.relative_to(ROOT).as_posix() for file in sources)}
    path = Path(data['mediaRoot']) / 'scoped-commit-spec.json'
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(path)


if __name__ == '__main__':
    if sys.argv[1:] == ['--prepare']:
        prepare()
    else:
        scoped.SHARED = {CONTROL, WORKLIST, TABLE}
        scoped.overlay = overlay
        scoped.validate = validate
        scoped.main()
