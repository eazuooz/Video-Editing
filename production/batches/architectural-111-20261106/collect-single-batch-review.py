"""Verify the exact series and collect one local review page when all 111 are ready."""
import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
QUEUE = HERE / 'single-production-queue-v1.json'
ARTIFACTS = {'clean': 'clean.mp4', 'captioned': 'captioned.mp4', 'ko': 'ko.srt', 'en': 'en.srt'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def media_pin(value):
    expected = value.get('sha256') if isinstance(value, dict) else None
    path = Path(value['path'] if isinstance(value, dict) else value)
    if not path.is_absolute() or not path.is_file() or not path.stat().st_size:
        raise ValueError(f'Missing local review file: {path}')
    digest = sha(path)
    if expected and expected != digest:
        raise ValueError(f'Local review file changed: {path}')
    return {'path': path.as_posix(), 'sha256': digest}


def delivery(row):
    review = row['localFinalReview']
    folder = Path(review['outputFolder'])
    if not folder.is_absolute() or not folder.is_dir() or not review['version']:
        raise ValueError('Missing version or local output folder')
    files = {}
    for key, suffix in ARTIFACTS.items():
        value = review.get('files', {}).get(key, str(folder / f"{row['slug']}.{suffix}"))
        files[key] = media_pin(value)
        if Path(files[key]['path']).resolve().parent != folder.resolve():
            raise ValueError('Output file does not belong to the recorded local folder')
    master = review.get('masterSHA256') or review.get('sha256')
    if master != files['captioned']['sha256'] or Path(review['captioned']).resolve() != Path(files['captioned']['path']).resolve():
        raise ValueError('Captioned master does not match the review record')
    return {'version': review['version'], 'outputFolder': folder.as_posix(), 'files': files,
            'metadata': media_pin(review['metadata']), 'episodeIndex': media_pin(review['index']),
            'technicalReview': row['status'], 'humanApproval': row['humanApproval']}


def verify_series():
    queue, batch, worklist = (read(path) for path in (QUEUE, HERE / 'batch.json', HERE / 'worklist.json'))
    rows = worklist['rows']
    key = lambda row: (row['topicId'], row['project'])
    if (queue['deliveryMode'] != 'one-local-review-after-all-111' or
            len(rows) != 111 or len({row['topicId'] for row in rows}) != 111 or
            [key(row) for row in rows] != [key(row) for row in queue['episodes']] or
            {key(row) for row in rows} != {key(row) for row in batch['projects']} or
            [row['order'] for row in rows] != list(range(1, 112))):
        raise ValueError('The worklist no longer matches the exact ordered series')
    complete, pending, invalid = [], [], []
    masters = set()
    for row in rows:
        topic = {'order': row['order'], 'topicId': row['topicId'], 'title': row['title']}
        if row['productionComplete'] is not True:
            pending.append(dict(topic, stage=row['status']))
            continue
        try:
            final = delivery(row)
            master = final['files']['captioned']['sha256']
            if master in masters:
                raise ValueError('Captioned master duplicates another episode')
            masters.add(master)
            complete.append(dict(topic, **final))
        except (OSError, KeyError, TypeError, ValueError) as exc:
            invalid.append(dict(topic, reason=str(exc)))
    return complete, pending, invalid


def href(path, label):
    return f'<a href="{escape(Path(path).as_uri(), quote=True)}">{escape(label)}</a>'


def render(complete):
    table = []
    for row in complete:
        links = [href(row['files'][k]['path'], label) for k, label in
                 [('captioned', '자막 영상'), ('clean', '클린 영상'), ('ko', '한국어 SRT'), ('en', '영어 SRT')]]
        links.extend((href(row['metadata']['path'], '제목·설명'), href(row['episodeIndex']['path'], '검수 기록'),
                      href(row['outputFolder'], '출력 폴더')))
        table.append(f'<tr><td>{row["order"]}</td><td>{escape(row["topicId"])}</td><td>{escape(row["title"])}</td>'
                     f'<td>{escape(row["version"])}</td><td>{" · ".join(links)}</td></tr>')
    return ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" '
            'content="width=device-width,initial-scale=1"><title>레벨디자인 111편 로컬 검수</title>'
            '<style>body{font:16px/1.6 system-ui,sans-serif;margin:24px;color:#161b18;background:#fafbf9}'
            'main{max-width:1200px;margin:auto}.table{overflow:auto}table{width:100%;border-collapse:collapse}'
            'th,td{padding:.65rem;text-align:left;border-bottom:1px solid #d9ded9}th{background:#e9eee9}'
            'a{color:#135540}</style><main><h1>레벨디자인 111편 로컬 검수</h1>'
            '<p>제작 순서대로 정리했습니다. 각 편의 자막 영상을 열어 검수할 수 있습니다.</p>'
            '<div class="table"><table><thead><tr><th>순서</th><th>편</th><th>제목</th><th>버전</th>'
            '<th>파일</th></tr></thead><tbody>' + ''.join(table) + '</tbody></table></div></main></html>\n')


def immutable(path, data):
    if not path.exists():
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        try:
            os.link(temporary, path)
        except FileExistsError:
            pass
        finally:
            temporary.unlink()
    if path.read_bytes() != data:
        raise ValueError(f'An existing delivery file has different content: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deliver', action='store_true')
    args = parser.parse_args()
    complete, pending, invalid = verify_series()
    status = {'total': 111, 'verifiedLocalReviews': len(complete), 'pending': len(pending),
              'invalidCompletedRows': invalid, 'nextPending': pending[:3], 'readyToDeliver': len(complete) == 111}
    if args.deliver and status['readyToDeliver']:
        data = (json.dumps({'series': 'architectural-111-20261106', 'episodes': complete},
                           ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        folder = MEDIA / 'delivery' / 'series-111' / hashlib.sha256(data).hexdigest()[:24]
        folder.mkdir(parents=True, exist_ok=True)
        immutable(folder / 'manifest.json', data)
        immutable(folder / 'index.html', render(complete).encode('utf-8'))
        status.update(index=(folder / 'index.html').as_posix(), manifest=(folder / 'manifest.json').as_posix())
    print(json.dumps(status, ensure_ascii=False))
    return 2 if invalid or (args.deliver and not status['readyToDeliver']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
