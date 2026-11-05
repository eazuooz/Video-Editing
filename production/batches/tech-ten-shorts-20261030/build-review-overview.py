"""Read-only media verification and local review index for the exact selected ten.

This does not change a project, pipeline state, approval, or platform. It writes
only the batch's delivery directory. A generated player never implies listening.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPECTED_BATCH = 'tech-ten-shorts-20261030'
FILES = ('clean.mp4', 'captioned.mp4', 'captions.ko.srt', 'captions.en.srt')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def escaped(value):
    return html.escape(str(value), quote=True)


def collect():
    batch = read(HERE / 'batch.json')
    if batch['batchId'] != EXPECTED_BATCH or len(batch['projects']) != 10:
        raise RuntimeError('Expected the exact ten selected projects.')
    media = Path(batch['mediaRoot']).resolve()
    cover_index = media / 'delivery/covers/covers.json'
    covers = {entry['slug']: entry for entry in read(cover_index)['covers']} if cover_index.exists() else {}
    rows = []
    for item in batch['projects']:
        project = ROOT / 'projects' / item['slug']
        manifest = read(project / 'project.json')
        metadata = read(project / 'publishing/metadata.json')
        final = (project / manifest['currentFinalDirectory']).resolve()
        if not final.is_relative_to(media / item['slug']):
            raise RuntimeError('Final path escaped selected media root.')
        row = dict(order=item['order'], slug=item['slug'], game=item['game'],
                   title=metadata['title'], description=metadata['description'],
                   revision=manifest['currentRevision'], visualVersion=manifest.get('currentVisualVersion'),
                   finalDirectory=str(final), generated=False, files=[],
                   humanFinalReview='pending', actualCompleteListening=False,
                   realTimePlaybackVerified=False, platformActionsPerformed=False)
        ledger_path = project / 'production/review-ledger.json'
        row['reviewLedger'] = str(ledger_path)
        row['recordedReviewEvidence'] = read(ledger_path) if ledger_path.exists() else {}
        if (final / 'delivery.json').exists():
            delivery = read(final / 'delivery.json')
            if delivery['revision'] == 'feedback-20261105':
                qa = read(final / 'feedback-check.json')
                if not (qa['decodedBoth'] and qa['subtitleBounds'] and qa['matchingAudioPair']
                        and qa['master'] == sha(final / 'captioned.mp4')):
                    raise RuntimeError(f'{item["slug"]}: feedback QA refers to the wrong version.')
            else:
                state = read(project / 'production/local/finite-pipeline-v1/state.json')
                for stage in ('video-pair', 'integrity', 'qa', 'review'):
                    if state.get('stages', {}).get(stage, {}).get('status') != 'pass':
                        raise RuntimeError(f'{item["slug"]}: missing successful {stage}.')
            if delivery['title'] != row['title'] or delivery['description'] != row['description']:
                raise RuntimeError('Delivered metadata differs from current publication draft.')
            if (delivery['width'], delivery['height'], delivery['fps']) != (1080, 1920, 60):
                raise RuntimeError('Unexpected master format.')
            records = {entry['name']: entry for entry in delivery['files']}
            for name in FILES:
                file = final / name
                digest = sha(file)
                if records[name]['sha256'] != digest or records[name]['bytes'] != file.stat().st_size:
                    raise RuntimeError(f'Changed delivery artifact: {file}')
                row['files'].append(dict(name=name, path=str(file), sha256=digest, bytes=file.stat().st_size))
            row.update(generated=True, seconds=delivery['durationSeconds'], frames=delivery['frames'],
                       review=str(final / 'index.html'), masterSha256=records['captioned.mp4']['sha256'])
            cover = covers.get(item['slug'])
            if cover and cover['masterSha256'] == row['masterSha256']:
                image = Path(cover['path']).resolve()
                if not image.is_relative_to(media / 'delivery/covers') or sha(image) != cover['sha256']:
                    raise RuntimeError('Cover changed or escaped the selected delivery directory.')
                row['coverCandidate'] = cover
        rows.append(row)
    return media, dict(batchId=EXPECTED_BATCH, generatedAt=dt.datetime.now(dt.timezone.utc).isoformat(),
                       completeCount=sum(row['generated'] for row in rows), total=10, projects=rows,
                       approvalInferred=False, platformActionsPerformed=False)


def render(record, page_directory):
    def href(path):
        relative = Path(os.path.relpath(path, page_directory)).as_posix()
        return escaped(quote(relative))

    cards = []
    navigation = '<nav aria-label="완성 영상 바로가기"><ul>' + ''.join(
        f'<li><a href="#video-{row["order"]}">{row["order"]}. {escaped(row["title"].split("#", 1)[0].split("|", 1)[0].strip())}</a></li>'
        for row in record['projects'] if row['generated']) + '</ul></nav>'
    for row in record['projects']:
        if row['generated']:
            final = Path(row['finalDirectory'])
            cover = row.get('coverCandidate')
            poster = f' poster="{href(cover["path"])}"' if cover else ''
            player = f'<video controls playsinline preload="none"{poster} src="{href(final / "captioned.mp4")}"></video>'
            links = ' · '.join(f'<a href="{href(final / name)}">{escaped(name)}</a>' for name in FILES)
            detail = f'<p>{row["seconds"]:.2f}초 · 1080×1920 · 60fps · {escaped(row["visualVersion"] or row["revision"])}</p>'
            detail += f'<p class="status">네 출력·해시·기술 검사 확인 / 사용자 검수 대기</p>{player}<p>{links}</p>'
            detail += f'<p><a href="{href(row["review"])}">대본과 영상 함께 보기</a> · <a href="{href(final / "mobile-review.mp4")}">모바일 크기 영상</a></p>'
            if cover:
                detail += f'<p><a href="{href(cover["path"])}">실제 게임 프레임 썸네일 후보</a> · 플랫폼 적용 전</p>'
            detail += f'<details><summary>정확한 버전 SHA256</summary><code>{row["masterSha256"]}</code></details>'
        else:
            detail = '<p class="status">제작 중 · 완성본 없음</p>'
        cards.append(f'<article id="video-{row["order"]}"><h2>{row["order"]}. {escaped(row["title"])}</h2>{detail}'
                     f'<details><summary>제목·설명 초안</summary><pre>{escaped(row["title"])}\n\n{escaped(row["description"])}</pre></details></article>')
    return '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>게임 개발 기술 쇼츠 10편 · 얌얌코딩 검수</title><style>
*{box-sizing:border-box}body{background:#080b0a;color:#f5f5f2;margin:0;font:16px/1.65 "Malgun Gothic",sans-serif}
main{max-width:950px;margin:auto;padding:24px}h1,h2{color:#ffdc62;line-height:1.4}h1{font-size:28px}h2{font-size:23px}
article{border-top:1px solid #36413b;margin-top:36px;padding-top:20px}a{color:#83d8bc}video{display:block;width:min(100%,375px);margin:20px auto;background:black}
p,pre,code{overflow-wrap:anywhere}pre{white-space:pre-wrap;font:inherit}.muted{color:#b4bdb7}.status{color:#a7dbce}details{margin:16px 0}summary{cursor:pointer}
</style><main><h1>게임 개발 기술 쇼츠 10편</h1>''' + f'<p>검수용 출력 {record["completeCount"]}/10편</p>' + '''
<p>각 영상은 실제 게임 장면과 자체 설명 애니메이션으로 구성했습니다. 아래에서 전체 자막 영상을 재생하고 clean·한영 자막도 받을 수 있습니다.</p>
<p class="muted">파일 생성·자동 검사와 실제 청취·실시간 재생 검수는 구별합니다. 표본 화면 검수 결과는 개별 원장에 기록하며, 전체 청취와 사용자 최종검수는 별도로 남아 있습니다. 이 페이지는 게시 승인이 아닙니다.</p>
<p><a href="review-ten.json">정확한 제목·설명·파일 해시와 검수 기록</a></p>''' + navigation + ''.join(cards) + '</main></html>'


def serve_review(media, record, port):
    """Serve only review artifacts. FileResponse handles seeking and HEAD."""
    from aiohttp import web

    app = web.Application()
    overview_url = '/delivery/review-ten.html'
    files = [media / 'delivery/review-ten.html', media / 'delivery/review-ten.json']
    for row in record['projects']:
        if not row['generated']:
            continue
        directory = Path(row['finalDirectory'])
        files.extend(directory / name for name in (
            *FILES, 'index.html', 'mobile-review.mp4', 'metadata.json', 'delivery.json', 'SHA256SUMS.txt'))
        if row.get('coverCandidate'):
            files.append(Path(row['coverCandidate']['path']))

    routes = {'/' + path.resolve().relative_to(media).as_posix(): path.resolve() for path in files}

    async def get_review(request):
        if request.path == '/':
            raise web.HTTPFound(overview_url)
        path = routes.get(request.path)
        if path is None or not path.is_file():
            raise web.HTTPNotFound()
        return web.FileResponse(path, headers={'Cache-Control': 'no-cache'})

    app.router.add_get('/{path:.*}', get_review)
    web.run_app(app, host='127.0.0.1', port=port)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-all', action='store_true')
    parser.add_argument('--serve', action='store_true', help='Open the verified review pages over loopback HTTP.')
    parser.add_argument('--port', type=int, default=9358)
    args = parser.parse_args()
    media, record = collect()
    if args.require_all and record['completeCount'] != 10:
        raise RuntimeError('All ten complete review outputs are required.')
    target = media / 'delivery'
    target.mkdir(exist_ok=True)
    (target / 'review-ten.html').write_text(render(record, target), encoding='utf8')
    if args.serve:
        serve_review(media, record, args.port)
        return
    contents = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    snapshot = target / ('review-ten-' + hashlib.sha256(contents.encode()).hexdigest()[:12] + '.json')
    snapshot.write_text(contents, encoding='utf8')
    (target / 'review-ten.json').write_text(contents, encoding='utf8')
    print(json.dumps(dict(complete=record['completeCount'], index=str(target / 'review-ten.html'), snapshot=str(snapshot)), ensure_ascii=False))


if __name__ == '__main__':
    main()
