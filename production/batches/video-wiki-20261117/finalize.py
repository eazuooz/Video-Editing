"""Reconcile the actually saved wiki pages into the scoped publication ledger."""
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')

def body(page):
    match = re.search(r'<content>\n([\s\S]*?)\n</content>', page['text'])
    assert match, page.get('title')
    return match[1]

def main():
    verified = read(HERE/'evidence/final-readback-corrected.json')
    pub = read(HERE/'publication.json')
    inv = read(HERE/'inventory.json')
    sources = read(HERE/'sources.json')
    inventory = {r['id']: r for r in inv['rows']}
    source_by_id = {r['id']: r for r in sources['rows']}
    records = []
    hubs = pub['hubs']
    for item in verified['articles']:
        key, page = item['id'], item['data']
        content = body(page)
        record = pub['pages'][key]
        series = inventory[key]['series']
        hub = hubs[series].replace('-', '')
        assert hub in page['text'].split('<content>')[0], (key, 'parent')
        assert '## 이어서 읽기' in content, (key, 'navigation')
        assert not re.search(r'\\\*\\\*|[^\n] ## ', content), (key, 'formatting')
        assert len(content) >= 1100, (key, 'short body')
        assert not page.get('truncated') and not page.get('unknown_block_count'), key
        image_count = len(re.findall(r'<image(?:\s|>)', content))
        if key not in {'D13', 'D19'}:
            assert image_count, (key, 'no image')
        else:
            assert 'mermaid' in content, (key, 'missing authored diagram')
        assert key == 'D13' or '<video source=' in content, (key, 'video embed')
        (HERE/'articles'/f'{key}.md').write_text(content+'\n', encoding='utf8')
        write(HERE/'evidence'/f'{key}-notion-read.json', page)
        public_url = 'https://www.yamyamcoding.com/'+record['pageId']
        row = dict(id=key, series=series, title=page['title'], pageId=record['pageId'],
                   notionUrl=record['url'], publicUrl=public_url, images=image_count,
                   bodyChars=len(content), bodySha256=hashlib.sha256(content.encode()).hexdigest(),
                   status='verified-saved-article-images-navigation-and-parent',
                   videoId=inventory[key].get('videoId'), platformStatus=inventory[key].get('platformStatus'))
        records.append(row)
        record.update(title=row['title'], publicUrl=public_url, bodyChars=row['bodyChars'],
                      bodySha256=row['bodySha256'], imageCount=image_count,
                      navigationVerified=True, status=row['status'],
                      verification=f'evidence/{key}-notion-read.json')
        inventory[key].update(status=row['status'], article=record['article'], wikiPageId=record['pageId'],
                              wikiUrl=record['url'], publicWikiUrl=public_url, savedArticleTitle=row['title'])
        if key in source_by_id:
            source = source_by_id[key]
            source['status'] = 'reviewed-and-saved-companion-article'
            source['savedArticleTitle'] = row['title']
            if (HERE/'evidence/legacy-audio'/f'{key}.json').exists():
                source['audioObservationEvidence'] = f'evidence/legacy-audio/{key}.json'
                source['asrUse'] = 'Rough lookup aid, not a verified transcript; article independently edited against observed frames and available original text.'
    assert len(records) == 113
    assert sum(r['images'] for r in records) == 144
    counts = dict(Counter(r['series'] for r in records))
    assert counts == {'game-design': 31, 'game-animation': 18, 'shorts': 64}, counts

    # The full D04 script, rather than its obsolete 83-second preview, is authoritative.
    d04 = source_by_id['D04']
    draft04 = read(HERE/'drafts/D04.json')
    d04['obsoletePreviewTextSource'] = d04.get('obsoletePreviewTextSource', d04.get('textSource'))
    if 'cues' in d04:
        d04['obsoletePreviewCues'] = d04.pop('cues')
    d04['textSource'] = draft04['sources']['sceneSource']
    d04['textSourceSha256'] = draft04['sources']['sceneSourceSha256']
    d04['sourceCorrection'] = draft04['sourceCorrection']
    d04['textSourceKind'] = 'full-nine-scene-narration-json'
    inventory['D10']['status'] = 'excluded-not-produced-no-channel-video'
    source_by_id['D10']['status'] = 'excluded-not-produced-no-channel-video'
    archive = verified['archive']
    archive_id = archive['id']
    archive_body = body(archive)
    assert len(re.findall(r'https://www.youtube.com/watch\?v=', archive_body)) == 15
    (HERE/'articles/shorts-ancillary-archive.md').write_text(archive_body+'\n', encoding='utf8')
    for row in inv['excluded']:
        row['status'] = 'indexed-in-original-video-archive'
        row['archiveWikiUrl'] = archive['url']

    hub_checks = []
    for key, page in verified['hubs'].items():
        content = body(page)
        count = len(re.findall(r'<page url=', content))
        expected = {'designHub': 31, 'animationHub': 18, 'shortsHub': 65}[key]
        assert count == expected, (key, count)
        assert content.index('## 읽기 차례') < content.index('## 원문 페이지 보관함')
        chapters = re.findall(r'^## 읽기 차례 · (\d)부', content, re.M)
        assert chapters == [str(i) for i in range(1, len(chapters)+1)], (key, chapters)
        (HERE/f'{key}.md').write_text(content+'\n', encoding='utf8')
        write(HERE/'evidence'/f'{key}-final-notion-read.json', page)
        hub_checks.append(dict(id=page['id'], title=page['title'], children=count,
                               chapterGroups=len(chapters), saved=True))

    now = datetime.now(timezone.utc).isoformat()
    summary = dict(learningPages=113, newlyCreated=109, existingPreserved=4, imageBlocks=144,
                   authoredDiagramOnlyPages=['D13', 'D19'], series=counts,
                   archivedAncillaryVideos=15, excludedUnproduced=['D10'],
                   videoPlatformMutations=0, humanReview='pending')
    pub.update(status='complete-notion-saved-and-internally-reviewed', completedAt=now,
               summary=summary, articlesIndex='article-index.json', qa='final-qa.json',
               ancillaryPages=[dict(pageId=archive_id, title=archive['title'], url=archive['url'],
                                    publicUrl='https://www.yamyamcoding.com/'+archive_id,
                                    videoCount=15, status='verified-original-links-and-categories')])
    inv.update(status=pub['status'], summary=summary, publicationLedger='publication.json')
    sources['status'] = 'reviewed-for-113-saved-learning-articles-one-unproduced-exclusion'
    sources['subtitleLookupNote'] = 'Several early public subtitle requests were rate-limited (HTTP 429). The no-public-transcript label in transcript-progress.json records lookup failure, not proof that captions do not exist. Retained scripts and actual frames/audio were used instead.'
    qa = dict(checkedAt=now, summary=summary, checks=dict(savedBodies=113, expectedParents=113,
             navigation=113, nonEmptyPages=113, nativeImageBlocks=144, unknownBlocks=0,
             escapedMarkdownResolved=True, childPagesPreserved=True,
             explicitVideoAvailabilityExceptions=['D13 deleted-video archive', 'D19 private video with supplementary reading cases', 'D23/D24/S27/S73 private videos', 'A03-A18/S01-S07 retain scheduled-video notice']),
             hubs=hub_checks, publicWebsite=read(HERE/'public-qa.json') if (HERE/'public-qa.json').exists() else {'status':'pending-final-browser-check'},
             specialCases=[
                 'D04 uses the complete nine-scene script matching the actual 410-second lesson; obsolete preview cues preserved as history.',
                 'D13 retains the article but removes its deleted-video embed; native state table and Mermaid replace an unavailable image.',
                 'D19 labels supplementary reading cases rather than asserting they occur in the private older video; unrelated footage rejected.',
                 'S73 uses an explicitly identified related Bloom frame rather than inventing a missing six-second implementation.'
             ])
    for name, data in [('publication.json', pub), ('inventory.json', inv), ('sources.json', sources),
                       ('article-index.json', records), ('final-qa.json', qa)]:
        write(HERE/name, data)
    links = {s: 'https://www.yamyamcoding.com/'+p for s,p in hubs.items()}
    notes = '\n'.join([
        '# 영상별 얌얌코딩 위키 — 완료 기록', '',
        '2026-11-17 사용자 요청. 영상 플랫폼의 업로드·공개·예약은 변경하지 않았다.', '',
        '| 시리즈 | 학습 글 | 목차 |', '| --- | ---: | --- |',
        *[f'| {s} | {n} | [공개 위키]({links[s]}) |' for s,n in counts.items()], '',
        '학습 글 113장: 신규 109장 + 기존 4장 보존·보강. 이미지 144개. 모든 장의 부모 위치·본문·목차·앞뒤 장 링크를 실제 저장 결과로 확인했다.', '',
        '일상·공연·단순 패러디 쇼츠 15편은 별도 보관 목록에 원래 제목과 영상 링크를 남겼다. 미제작 D10은 완료 강의로 꾸미지 않았다.', '',
        '## 검수와 예외', '',
        '- D13: 영상이 삭제되어 읽기용 글로 표시. D19: 비공개 구버전과 보충 사례를 구별. 두 글은 관계를 직접 보여 주는 표·도식으로 설명한다.',
        '- 비공개·예약 영상은 해당 상태를 안내한다. 글 저장과 실제 영상 공개 재생은 별개로 기록한다.',
        '- 기존 문서 재사용 권리가 불명확한 화면은 배제하고 자체 설명 프레임 등으로 대체했다.',
        '- 초기 자막 조회의 HTTP 429를 자막 부재로 해석하지 않는다. 보존된 대본과 실제 프레임·음성 관찰로 보완했다.',
        '- 공개 웹사이트의 최종 관찰은 [public-qa.json](public-qa.json), 저장 본문·표·도식·이미지 검수는 [final-qa.json](final-qa.json)에 기록했다.', '',
        '## 검수 링크', '',
        '[전체 113장 검수표](index.html) · [페이지/이미지/영상 대응](publication.json) · [상시 제작 규칙](../../../../docs/VIDEO_WIKI_WORKFLOW.md)', '',
        '영상 제작 완료 조건에 위키 상세 글·장면 이미지·목차 연결·저장 검증을 추가했고, 사용자가 지목한 Video Agent1 (영상) 대화에도 전달했다.', '',
        'MP4/WAV·원본·캡처 및 임시 ASR 자료는 evidence/에 두고 Git 저장에서 제외했다. Git에는 글·규칙·매핑·검수 상태만 선택 저장한다.', ''
    ])
    (HERE/'README.md').write_text(notes, encoding='utf8')
    rows = ''.join('<tr><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['series'])+'</td><td><a href="'+r['publicUrl']+'">'+html.escape(r['title'])+'</a><br><a href="'+r['notionUrl']+'">Notion에서 보기</a></td><td>'+str(r['images'])+'</td><td>저장·내부 검수 완료<br>'+html.escape(str(r['platformStatus'] or '별도 영상 상태 확인'))+'</td></tr>' for r in sorted(records,key=lambda x:(['game-design','game-animation','shorts'].index(x['series']), x['id'])))
    (HERE/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>영상별 위키 검수표</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:1200px;margin:40px auto;padding:0 20px;color:#172126;background:#fafbf9}h1{font-size:30px}a{color:#146e66}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;border-bottom:1px solid #d9dfdc;padding:14px;vertical-align:top}th{background:#edf3ed}input{font:inherit;padding:10px;width:90%;margin:12px 0 24px}small{color:#52605a}</style><h1>영상별 얌얌코딩 위키 검수표</h1><p>게임디자인 31장 · 애니메이션 18장 · 교육 쇼츠 64장<br>113장 / 이미지 144개 / 일상·패러디 별도 보관 15편</p><p><a href="README.md">완료 기록과 예외</a> · <a href="final-qa.json">검수 근거</a></p><small>글 저장 상태와 영상 공개 상태는 별개입니다. 사용자 내용 검수는 대기입니다.</small><br><input id="search" placeholder="제목·시리즈·ID 검색" oninput="document.querySelectorAll(\'tbody tr\').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(this.value.toLowerCase()))"><table><thead><tr><th>ID</th><th>시리즈</th><th>학습 페이지</th><th>그림</th><th>상태</th></tr></thead><tbody>'+rows+'</tbody></table></html>', encoding='utf8')
    control_path = ROOT/'shared/publishing/video-production-control.json'
    control = read(control_path)
    control['videoCompanionWikiPolicy20261117']['existingBatch'] = dict(path=HERE.relative_to(ROOT).as_posix(), status=pub['status'], learningPages=113, imageBlocks=144)
    write(control_path, control)
    worklist_path = ROOT/'shared/publishing/video-worklist.json'
    worklist = read(worklist_path)
    worklist['videoCompanionWiki20261117'] = dict(status=pub['status'], summary=summary,
        manifest=HERE.relative_to(ROOT).as_posix()+'/publication.json',
        review=HERE.relative_to(ROOT).as_posix()+'/index.html',
        publicWebsiteQA=HERE.relative_to(ROOT).as_posix()+'/public-qa.json',
        pages=[dict(id=r['id'], videoId=r['videoId'], wikiUrl=r['notionUrl'],
                    status=r['status']) for r in records])
    write(worklist_path, worklist)
    print(json.dumps(summary, ensure_ascii=True))

if __name__ == '__main__':
    main()
