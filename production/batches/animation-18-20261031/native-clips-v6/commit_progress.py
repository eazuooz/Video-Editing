"""Commit only the selected native-animation revision and its ledger fields."""
import importlib.util
from pathlib import PurePosixPath
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from prepare import HERE, ROOT, WORK, OUTPUT, read, save

CONTROL = 'shared/publishing/video-production-control.json'
WORKLIST = 'shared/publishing/video-worklist.json'
TABLE = 'docs/VIDEO_WORKLIST.md'
KEY = 'animationNativeClipsRevision20261114'
START = '<!-- ANIMATION-NATIVE-CLIPS-V6-20261114 -->'
END = '<!-- ANIMATION-NATIVE-CLIPS-V6-20261114-END -->'
PREFIX = HERE.relative_to(ROOT).as_posix() + '/'
SPEC = WORK / 'scoped-progress-commit.json'
helper = ROOT / 'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
module = importlib.util.spec_from_file_location('native_clip_scoped_commit', helper)
scoped = importlib.util.module_from_spec(module)
module.loader.exec_module(scoped)


def overlay(name, raw, spec):
    if name == CONTROL:
        return scoped.patch(raw, [KEY], spec['control'])
    if name == WORKLIST:
        for row in spec['rows']:
            matches = [i for i, q in enumerate(scoped.load(raw)['rows']) if q['id'] == row['id']]
            assert len(matches) == 1
            raw = scoped.patch(raw, ['rows', matches[0], 'nativeClipRevision'], row['revision'])
        return raw
    if name == TABLE:
        first, last = raw.find(START.encode()), raw.find(END.encode())
        assert (first < 0) == (last < 0)
        nl = '\r\n' if b'\r\n' in raw else '\n'
        block = spec['markdown'].replace('\n', nl).encode()
        if first >= 0:
            return raw[:first] + block + raw[last + len(END):]
        return raw + (nl * 2).encode() + block + nl.encode()
    raise AssertionError(name)


def validate(spec):
    assert spec['scope'] == KEY
    assert [r['id'] for r in spec['rows']] == [f'A{i:02}' for i in range(3, 19)]
    assert spec['control']['excludedUploaded'] == ['A01', 'A02']
    assert not spec['control']['youtubeAuthorized'] and not spec['control']['driveAuthorized']
    for name in spec['ownedPaths']:
        path = PurePosixPath(name)
        assets={r['path']:r['sha256'] for r in read(HERE/'editable-assets.json')['files']} if (HERE/'editable-assets.json').exists() else {}
        if name in assets:
            from finish_episode import sha
            assert name.startswith('GameAnimationSample/Content/YamyamNativeClipsV6/')
            assert path.suffix in {'.uasset','.umap'} and sha(ROOT/name)==assets[name]
            continue
        assert name.startswith(PREFIX) and '..' not in path.parts and 'local' not in path.parts
        assert path.suffix in {'.py', '.cjs', '.json', '.txt', '.md'}
        assert (ROOT / name).is_file()
    return sorted(spec['ownedPaths']) + sorted(scoped.SHARED)


def prepare():
    plan = read(HERE / 'plan.json')
    stamp = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
    rows, completed = [], []
    table = [START, '', '## 애니메이션 기존 클립 비교·10초 요약 수정', '',
             '[통합 검수표](http://127.0.0.1:9300/)', '',
             '공개된 A01·A02는 제외. A06 시연은 보존. 새 업로드·예약·삭제 없음.', '',
             '| 편 | 주제 | 이번 수정 상태 | 사용자 검수 |', '|---|---|---|---|']
    for row in plan['episodes']:
        ep = row['id']
        delivery = OUTPUT / ep / 'delivery.json'
        ready = delivery.is_file() and not read(delivery).get('visualReviewPending', True)
        source_checked = (WORK / ep / 'native-source-audit.json').is_file()
        status = '로컬 수정본 검수 가능' if ready else '기존 클립 검증 완료 · 요약 합성 중' if source_checked else '원본 동작 대조·시연 수정 중'
        revision = {'revision': 'native-clips-v6', 'status': status, 'updatedAt': stamp,
                    'humanReviewed': False, 'platformChanged': False, 'summaryFrames': 600,
                    'reviewUrl': 'http://127.0.0.1:9300/' + ep + '/' if ready else None}
        if ready:
            completed.append(ep)
            revision['delivery'] = str(delivery)
            revision['captionedMasterSha256'] = next(f['sha256'] for f in read(delivery)['files'] if f['kind'] == 'captioned.mp4')
        rows.append({'id': ep, 'revision': revision})
        table.append(f'| {ep} | {row["title"].split("|")[0]} | {status} | {"대기" if ready else "제작 후 검수"} |')
    table += ['', END]
    control = read(ROOT / CONTROL)[KEY]
    control.update(status='native-motion-capture-and-summary-assembly', updatedAt=stamp,
                   completedLocalReviews=completed, reviewUrl='http://127.0.0.1:9300/',
                   humanReviewed=False, platformChanged=False)
    checkpoint = read(HERE / 'checkpoint.json')
    checkpoint.update(updatedAt=stamp, completed=completed,
                      remaining=[r['id'] for r in rows if r['id'] not in completed],
                      recapComponentsReady=[r['id'] for r in rows if (WORK / r['id'] / 'assembly/summary-components.json').exists()])
    save(HERE / 'checkpoint.json', checkpoint)
    markdown = '\n'.join(table)
    (HERE / 'review-table.md').write_text(markdown + '\n', encoding='utf-8')
    sources = sorted(p.relative_to(ROOT).as_posix() for p in HERE.iterdir()
                     if p.is_file() and p.suffix in {'.py', '.cjs', '.json', '.txt', '.md'})
    if (HERE/'editable-assets.json').exists():sources+=sorted(r['path'] for r in read(HERE/'editable-assets.json')['files'])
    save(SPEC, {'scope': KEY, 'control': control, 'rows': rows, 'markdown': markdown, 'ownedPaths': sources})
    print(SPEC)


if __name__ == '__main__':
    if sys.argv[1:] == ['--prepare']:
        prepare()
    else:
        scoped.SHARED = {CONTROL, WORKLIST, TABLE}
        scoped.overlay, scoped.validate = overlay, validate
        scoped.main()
