"""Reconcile only the observed 43 long-form schedule changes; no platform actions."""
import copy
import datetime as dt
import hashlib
import html
import json
from pathlib import Path

ROOT = Path('D:/Github/VideoEditing')
HERE = Path(__file__).resolve().parent
UPLOAD = HERE.parent / 'game-math-upload-20261117'
KEY = 'longformDaily20261117'
START = '<!-- LONGFORM-DAILY-SCHEDULE-20261117-START -->'
END = '<!-- LONGFORM-DAILY-SCHEDULE-20261117-END -->'
USER = '그리고 영상 예약날짜 쇼츠랑 일반영상은 별개로 올라가는거야~ 쇼츠뒤에 한거같은데 별개로 영상 예약걸려있는거 오늘부터 하나씩 올라갈수 있게 예약 날짜 수정해줘'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def block(path, content):
    p = ROOT / path
    before = p.read_text(encoding='utf-8-sig')
    if START in before:
        before = before[:before.index(START)] + content + before[before.index(END) + len(END):]
    else:
        before = before.rstrip() + '\n\n' + content + '\n'
    p.write_text(before, encoding='utf8')


def main():
    plan, progress, final = (read(HERE / name) for name in ('plan.json', 'progress.json', 'final-verification.json'))
    rows = progress['rows']
    assert len(rows) == final['longformCount'] == 43
    assert len({r['videoId'] for r in rows}) == 43
    assert final['allIndividualTimesReopened'] and final['longformTableMatchesPlan'] and final['shortsUnchanged']
    before, after = (read(HERE / f'shorts-{name}.json') for name in ('before', 'after'))
    assert before == after and len(after) == 7
    assert not ({r['videoId'] for r in rows} & {r['videoId'] for r in after})
    first = dt.datetime.fromisoformat('2026-11-17T19:00:00+09:00')
    for i, r in enumerate(rows):
        expected = first + dt.timedelta(days=i)
        assert r['newKst'] == expected.isoformat()
        assert r['status'] == 'saved-and-reopened' and r['metadataPreserved']
        proof = HERE / 'evidence' / f"{i+1:02}-{r['videoId']}.txt"
        text = proof.read_text(encoding='utf8')
        assert f'{expected.year}. {expected.month}. {expected.day}.' in text
        assert '오후 7:00' in text and 'GMT+0900' in text
        r['evidence'] = str(proof)
        r['evidenceSha256'] = hashlib.sha256(proof.read_bytes()).hexdigest()
        a = next(v for v in final['rows'] if v['videoId'] == r['videoId'])
        assert a['date'] == f'{expected.year}. {expected.month}. {expected.day}.'

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
    summary = dict(status='all-43-scheduled-and-reopened', count=43,
        firstKst=rows[0]['newKst'], lastKst=rows[-1]['newKst'], timeZone='Asia/Seoul',
        cadence='one-longform-per-day', previousOrderPreserved=True,
        shortsUnchanged=True, scheduledShortsCount=7,
        report=str(HERE / 'review.html'), verification=str(HERE / 'final-verification.json'),
        userEvidence=USER, verifiedAtKst=now,
        uploadedOrDeleted=False, metadataAndThumbnailsChanged=False,
        rows=copy.deepcopy(rows))
    plan.update(status='completed', completedAtKst=now, summary=str(HERE / 'summary.json'))
    progress.update(status='complete', completedAtKst=now, finalVerification=str(HERE / 'final-verification.json'))
    write(HERE / 'plan.json', plan)
    write(HERE / 'progress.json', progress)
    write(HERE / 'summary.json', summary)

    control = read(ROOT / 'shared/publishing/video-production-control.json')
    auth = control['scopedPublishingAuthorizations'][KEY]
    auth.update(status=summary['status'], userEvidence=USER, verifiedAtKst=now,
                summary=str(HERE / 'summary.json'), report=summary['report'], shortsUnchanged=True)
    policy = control['separateFormatSchedulePolicy20261117']
    policy['userEvidence'] = '영상 예약날짜 쇼츠랑 일반영상은 별개로 올라가는거야'
    write(ROOT / 'shared/publishing/video-production-control.json', control)

    by_id = {r['videoId']: r for r in rows}
    ledger = read(ROOT / 'shared/publishing/video-worklist.json')
    ledger[KEY] = copy.deepcopy(summary)
    for r in ledger['rows']:
        actual = by_id.get(r.get('videoId'))
        if actual:
            r['longformSchedule20261117'] = dict(status='scheduled-verified', scheduledKst=actual['newKst'],
                evidence=actual['evidence'], report=summary['report'])
            if r.get('publishing20261117'):
                r['publishing20261117']['scheduledKst'] = actual['newKst']

    # Current upload metadata follows the new actual dates; old UI evidence remains untouched.
    batch, platform = read(UPLOAD / 'batch.json'), read(UPLOAD / 'platform-progress.json')
    for r in batch['rows']:
        ident, vid = r['id'], r['actualVideoId']
        actual = by_id[vid]
        change = dict(beforeKst=r['scheduledKst'], afterKst=actual['newKst'], evidence=actual['evidence'],
                      reason=USER, status='saved-and-reopened')
        if r.get('reschedule20261117'):
            change = r['reschedule20261117']
        for p in (UPLOAD / ident / 'package.json', UPLOAD / ident / 'youtube-upload.json'):
            doc = read(p)
            doc['reschedule20261117'] = copy.deepcopy(change)
            for k in ('scheduleKst', 'scheduledKst'):
                if k in doc:
                    doc[k] = actual['newKst']
            write(p, doc)
        r.update(reschedule20261117=copy.deepcopy(change), scheduledKst=actual['newKst'], scheduleKst=actual['newKst'])
        platform['rows'][ident].update(scheduledKst=actual['newKst'],
            scheduleVerifiedBy='Saved, reloaded, and date/time/GMT+0900 reopened; ' + actual['evidence'],
            reschedule20261117=copy.deepcopy(change))
    batch.setdefault('originalReservation20261117', {k:batch[k] for k in
        ('actualExistingLastScheduledKst','plannedFirstKst','plannedLastKst','actualFirstKst','actualLastKst')})
    batch.update(actualFirstKst=by_id[batch['rows'][0]['actualVideoId']]['newKst'],
                 actualLastKst=by_id[batch['rows'][-1]['actualVideoId']]['newKst'],
                 currentScheduleSummary=summary['report'])
    platform['reschedule20261117'] = dict(report=summary['report'], verifiedAtKst=now)
    write(UPLOAD / 'batch.json', batch)
    write(UPLOAD / 'platform-progress.json', platform)
    upload_summary = read(UPLOAD / 'summary.json')
    upload_summary.setdefault('originalReservation20261117', {k:upload_summary[k] for k in
        ('firstKst','lastKst','existingAnchorKst')})
    upload_summary.update(firstKst=batch['actualFirstKst'], lastKst=batch['actualLastKst'],
        existingAnchorKst=by_id['9OMsNJmNJOc']['newKst'], currentScheduleSummary=summary['report'])
    write(UPLOAD / 'summary.json', upload_summary)
    ledger['mathPublishing20261117'].update(firstKst=batch['actualFirstKst'], lastKst=batch['actualLastKst'],
        existingAnchorKst=by_id['9OMsNJmNJOc']['newKst'], currentScheduleSummary=summary['report'])
    write(ROOT / 'shared/publishing/video-worklist.json', ledger)
    control['scopedPublishingAuthorizations']['mathPublishing20261117'].update(
        firstKst=batch['actualFirstKst'], lastKst=batch['actualLastKst'],
        existingAnchorKst=by_id['9OMsNJmNJOc']['newKst'], currentScheduleSummary=summary['report'])
    write(ROOT / 'shared/publishing/video-production-control.json', control)

    lines = [START, '### 일반 영상 예약 변경 완료 · 쇼츠 일정 분리 (2026-11-17)', '',
        '예약된 일반 영상 43편의 기존 순서를 유지해 **2026-11-17~12-29 매일 19:00 (Asia/Seoul)**로 변경했다. 쇼츠 예약 7편은 기존 날짜를 그대로 유지했다.', '',
        '- 기존 수학 14편: 11월 17~30일', '- 애니메이션 A03–A18 16편: 12월 1~16일',
        '- 게임수학 M21–M33 13편: 12월 17~29일', '',
        '43편 각각 저장 완료 후 페이지를 다시 열어 날짜·오후 7시·GMT+0900을 확인했다. 최종 일반 영상 43개 ID/날짜가 계획과 일치하고 쇼츠 7개 ID/날짜/제목도 변경 전과 일치한다. 이 날짜가 이전 2027년 1월 예약 기록보다 우선하는 현재 일정이다. 영상 본문·썸네일·자막·재생목록은 변경하지 않았다.', '',
        '[전체 43편 예약표](../production/batches/longform-daily-schedule-20261117/review.html) · [검증 기록](../production/batches/longform-daily-schedule-20261117/summary.json)', END]
    for p in ('docs/VIDEO_WORKLIST.md', 'docs/GAME_MATH_PRIVATE_POLISH.md'):
        block(p, '\n'.join(lines))
    # The workflow points to the independent-format rule, overriding old mixed anchors.
    block('docs/VIDEO_WORKFLOW.md', '\n'.join([START, '### 예약 일정은 형식별 독립 큐', '',
        '2026-11-17 사용자 정정에 따라 일반 영상과 쇼츠의 다음 예약일은 각 형식의 실제 예약 목록만으로 계산한다. 다른 형식의 마지막 예약 날짜를 이어받지 않으며 같은 날 각 한 편이 공개되어도 충돌이 아니다. 기존 예약 변경은 명시된 범위만 수행한다. 현재 승인된 일반 영상 43편은 11월 17일~12월 29일 매일 한국 시간 오후 7시로 저장·재열람 완료했다. 쇼츠 7편은 보존했다. 상세는 [게시 규격](YOUTUBE_PUBLISHING.md)의 형식별 예약 규칙과 [전체 예약표](../production/batches/longform-daily-schedule-20261117/review.html)를 따른다.', END]))
    (HERE / 'README.md').write_text('\n'.join(lines[1:-1]) + '\n\n| 순서 | 영상 | 한국 시간 공개일 | 상태 |\n|---|---|---|---|\n' +
        '\n'.join(f"| {r['order']} | [{r['title'].replace('|','·')}](https://youtu.be/{r['videoId']}) | {r['newKst'][:10]} 19:00 | 저장·재열람 완료 |" for r in rows) + '\n', encoding='utf8')
    trs = ''.join(f"<tr><td>{r['order']}</td><td><a href='https://youtu.be/{r['videoId']}'>{html.escape(r['title'])}</a></td><td>{r['newKst'][:10]} 19:00</td><td>예약·재열람 완료</td></tr>" for r in rows)
    page = """<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>일반 영상 43편 예약표</title><style>body{font:16px/1.7 'Malgun Gothic',sans-serif;margin:32px;color:#19242a}h1{font-size:28px}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #d7dde1;text-align:left}th{background:#fff0a3}a{color:#215673}img{max-width:100%}.notice{background:#f4f5f0;padding:20px}td:nth-child(3){white-space:nowrap}@media(max-width:600px){body{margin:14px}td,th{padding:8px}}</style><h1>일반 영상 43편 · 매일 한 편</h1><p class="notice">2026년 11월 17일~12월 29일 · 매일 오후 7시 · 한국 시간.<br>기존 일반 영상의 순서를 유지했습니다. 쇼츠 예약 7편은 별도 일정 그대로입니다.<br>M21~M33은 12월 17~29일에 공개됩니다. 기존 2027년 1월 예약 기록보다 이 일정이 우선합니다.</p><p>43편 각각 저장 완료 후 날짜·시간·GMT+0900 재열람. 최종 일반 영상 목록과 쇼츠 변경 전후 목록 대조 완료. 영상 내용·제목·설명·썸네일·자막·재생목록 변경 없음.</p><table><thead><tr><th>순서</th><th>영상</th><th>공개 시각 KST</th><th>상태</th></tr></thead><tbody>""" + trs + """</tbody></table><p><a href="summary.json">검증 기록</a> · <a href="shorts-after.json">보존된 쇼츠 7편</a></p><h2>실제 Studio 예약 목록</h2><img src="evidence/longform-final.jpg" alt="YouTube Studio 일반 영상 예약 목록의 11월 17일부터 이어지는 공개 날짜"><h2>별도 유지된 쇼츠 목록</h2><img src="evidence/shorts-after.jpg" alt="날짜를 변경하지 않은 쇼츠 예약 목록"></html>"""
    (HERE / 'review.html').write_text(page, encoding='utf8')
    # Put a current notice ahead of the historical upload/thumbnail review records.
    for p in (UPLOAD / 'review.html', UPLOAD / 'thumbnail-revision-v2/review.html'):
        text = p.read_text(encoding='utf8')
        notice = '<aside style="padding:18px;background:#fff0a3">현재 예약: M21~M33은 2026년 12월 17~29일 매일 오후 7시(KST). <a href="' + ('../' if p.parent == UPLOAD else '../../') + 'longform-daily-schedule-20261117/review.html">일반 영상 43편 현재 예약표</a>. 아래 최초 업로드 예약 화면은 변경 전 이력입니다.</aside>'
        if '현재 예약: M21~M33은 2026년 12월 17~29일' not in text:
            text = text.replace('<h1>', notice + '<h1>', 1)
            p.write_text(text, encoding='utf8')
    print('Verified and reconciled 43 long-form dates; 7 Shorts unchanged.')


if __name__ == '__main__':
    main()
