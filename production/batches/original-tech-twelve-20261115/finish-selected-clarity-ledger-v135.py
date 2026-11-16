"""Record the nine completed revisions after the exact twelve review collector."""
from pathlib import Path
import copy, datetime, hashlib, importlib.util, json, sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
M = Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
KEY = 'explicitOriginalTechTwelve20261115'
SELECTED = [2, 3, 5, 6, 7, 8, 10, 11, 12]

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
    p = Path(p)
    return dict(path=str(p.resolve()), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p, d):
    assert not p.exists(), p
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def canonical(d):
    return hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.videos = []; self.files = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'video': self.videos.append(d['src'])
        if tag == 'a' and d.get('href', '').startswith('file:'): self.files.append(d['href'])

def main():
    complete = H / 'selected-clarity-completion-v135.json'
    assert not complete.exists()
    page = H / 'local-final-review-v4.html'
    manifestpath = H / 'local-final-review-manifest-v4.json'
    manifest = read(manifestpath)
    oldmanifest = read(H / 'local-final-review-manifest-v2.json')
    assert manifest['completedSelectedRevisions'] == 9 and manifest['pendingSelectedRevisions'] == 0
    assert manifest['exactProjectCount'] == 12 and manifest['allArtifactHashesVerified']
    assert all(manifest['projects'][n-1] == oldmanifest['projects'][n-1] for n in [1, 4, 9])
    parser = Links(); parser.feed(page.read_text(encoding='utf8'))
    assert len(parser.videos) == 12
    for uri in parser.videos + parser.files:
        assert Path(unquote(urlparse(uri).path).lstrip('/')).is_file(), uri
    queue = M / 'clarity-revision-v83/clean-queue-v132/completion.json'
    q = read(queue)
    assert q['finiteQueueEnded'] and len(q['projects']) == 4
    assert all(len(x['stages']) == 4 and all(s['exitCode'] == 0 for s in x['stages']) for x in q['projects'])
    selected = []
    sources = {H / 'collect-clarity-final-review-v128.py', Path(__file__), page, manifestpath}
    for row in manifest['projects']:
        if row['order'] not in SELECTED: continue
        bp = Path(row['bundle']['path']); bundle = read(bp)
        assert bundle['localFinalBundleComplete'] and not bundle['humanApproval']
        assert pin(bp)['sha256'] == row['bundle']['sha256']
        item = dict(order=row['order'], slug=row['slug'], version=row['version'], durationSeconds=row['actualMixSeconds'],
                    revisionBundle=pin(bp), revisionVideoComplete=True, pilotVisualReview=row['checks']['technicalVisual']['approvedPilotReview'],
                    humanApproval=False, actualFullListening=False, actualRealtimePlayback=False)
        if row['order'] != 2:
            p = ROOT / 'projects' / row['slug']; selection = p / 'production/accepted-voice-selection-v95.json'
            s = read(selection); item['acceptedVoice'] = pin(selection)
            item['mixedContentReview'] = pin(bp.parent.parent / 'audio-mix-v95/mixed-content-review.json')
            sources.add(selection)
            for field in ['captionTiming', 'narration', 'clauses']:
                f = Path(s[field]['path']); assert pin(f)['sha256'] == s[field]['sha256']; sources.add(f)
            version = 130 if row['order'] == 8 else 95
            inputs = p / f'production/film-inputs-v{version}.json'; sources.add(inputs)
            for field in ['voiceSelection', 'captionTiming', 'filmPlan']:
                rec = read(inputs)[field]; f = Path(rec['path']); assert pin(f)['sha256'] == rec['sha256']; sources.add(f)
            sources.update([p/'production/captions-v95.ko.srt', p/'production/captions-v95.en.srt'])
            pilot = read(bp.parent.parent/f'film-v{version}/pilot-proof.json')
            for rec in pilot['identity']['inputs']:
                f = Path(rec['path'])
                if f.is_relative_to(H) or f.is_relative_to(p/'planning') or f.is_relative_to(p/'production'):
                    assert f.suffix in ['.py', '.json', '.srt']
                    assert pin(f)['sha256'] == rec['sha256'], f
                    sources.add(f)
        selected.append(item)
    evidence = dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), selectedOrders=SELECTED,
                    preservedOrders=[1,4,9], selectedRevisionsComplete=9, pendingSelectedRevisions=0,
                    localFinalVideos=12, artifacts=72, reviewPage=pin(page), manifest=pin(manifestpath),
                    sourceRequest=pin(H/'selected-clarity-request-v83.json'), selectedRevisions=selected,
                    finiteCleanQueue=pin(queue), allFiniteStagesExitedZero=True,
                    actualFullListening=False, actualRealtimePlayback=False, humanApproval=False,
                    deliveryPostedInChat=False, platformActions=[], otherBatchesAndAutomationsUnchanged=True)
    save(complete, evidence); sources.add(complete)
    sp = module('selected_clarity_scope_splice_v135', H/'finalize-cpu-preparation-v1.py')
    rowsp = module('selected_clarity_row_splice_v135', H/'finish-lockon-revision-ledger-v80.py')
    scopes = []
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    relativepage = str(page.relative_to(ROOT)).replace('\\', '/')
    for name in ['video-production-control.json', 'video-worklist.json']:
        path = ROOT/'shared/publishing'/name; before = path.read_bytes(); raw = before.decode('utf-8-sig'); data = json.loads(raw)
        own = copy.deepcopy(data[KEY])
        own.update(status='selected-clarity-revisions-local-review-ready', updatedAtKst=now,
                   automaticAdvanceWithinExactList=False, currentSelectedProject=None,
                   activeRevisionScope=[], completedRevisionScope=[x['slug'] for x in selected],
                   reviewPage=relativepage, progressPage=relativepage, selectedRevisionReviewReady=True,
                   localFinalReviewReady=True, finalDeliveryPrepared=True, deliveryPostedInChat=False,
                   localFinalVideos=12, resourceStatus='All nine selected revisions and all twelve local review bundles are complete. Finite production has ended; human viewing and listening approval remains pending.')
        own['latestSelectedRevision'] = dict(request=pin(H/'selected-clarity-request-v83.json'), completion=pin(complete),
                                            manifest=pin(manifestpath), page=relativepage, selectedOrders=SELECTED,
                                            preservedOrders=[1,4,9], localRevisionPreviewComplete=True, humanApproval=False)
        own['activeRevisionProgress'].update(selectedRevisionCompleted=9, selectedRevisionPending=0,
                     acceptedExpandedVoices=8, mixedContentAndLevelsAccepted=8, sourceStages=selected,
                     currentStageEvidence=pin(complete), progressPage=relativepage, humanApproval=False)
        new = sp.replace_value(raw, KEY, own)
        if name == 'video-worklist.json':
            for item in selected:
                row = copy.deepcopy(next(x for x in data['rows'] if x.get('id') == f"OT12-{item['order']:02d}"))
                row.update(reviewPage=relativepage, reviewStatus='수정본 로컬 QA 완료 / 사람 검수 대기',
                           status='exact12-selected-revision-review-ready',
                           selectedClarityRevision=dict(request=pin(H/'selected-clarity-request-v83.json'),
                               revisionVideoComplete=True, bundle=item['revisionBundle'], version=item['version'],
                               durationSeconds=item['durationSeconds'], currentStageEvidence=pin(complete),
                               pilotVisualReview=item['pilotVisualReview'], humanApproval=False))
                new = rowsp.replace_one_row(new, row)
        after = json.loads(new)
        foreign_before = copy.deepcopy(data); foreign_after = copy.deepcopy(after)
        for d in [foreign_before, foreign_after]:
            d.pop(KEY)
            if 'rows' in d: d['rows'] = [x for x in d['rows'] if x.get('id') not in [f'OT12-{n:02d}' for n in SELECTED]]
        assert foreign_before == foreign_after
        path.write_bytes((b'\xef\xbb\xbf' if before.startswith(b'\xef\xbb\xbf') else b'') + new.encode('utf8'))
        scopes.append(dict(path=str(path), ownKeySha256=canonical(after[KEY]),
                           rowSha256=canonical([x for x in after['rows'] if x.get('id','').startswith('OT12-')]) if 'rows' in after else None))
    doc = ROOT/'docs/VIDEO_WORKFLOW.md'; before = doc.read_bytes(); raw = before.decode('utf-8-sig')
    start='<!-- ORIGINAL-TECH-TWELVE-20261115 -->'; end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
    a,z=raw.index(start),raw.index(end)+len(end); marker=raw[a:z]
    old='2026-11-16 최신 사용자 선택은 2번 제목 및 3·5·6·7·8·10·11·12번 설명·실제 예시 보강이다. 기존 원문 학습 순서와 승인 PCM을 보존하고 추가 문장만 제작한다. 2번은 잘못된 최초 도입 표현을 피한 제목 수정본을 완성했고, 나머지 8편은 새 음성·연결 검수 및 예시 합성 중이다. [수정 진행표](../production/batches/original-tech-twelve-20261115/local-revision-progress-v3.html)는 기존본과 새 수정본 상태를 구분한다. 다른 편·111·자동화·플랫폼은 변경하지 않는다.'
    replacement='2026-11-16 최신 사용자 선택인 2번 제목 및 3·5·6·7·8·10·11·12번 설명·실제 예시 보강을 모두 완료했다. 기존 원문 학습 순서와 승인 PCM을 보존하고 추가 문장만 제작했으며, 실제 게임 예시와 설명 모형을 구분했다. 2번 제목은 사실과 다른 최초 도입 표현을 피했다. [수정 검수표 v4](../production/batches/original-tech-twelve-20261115/local-final-review-v4.html)에 정확12편과 자막·클린·KO/EN 자막·제목 설명·버전·해시를 연결했다. 자동 검사와 실제 자막별375px 화면 검수는 완료했으며, 연속 실시간 재생·전체 청취·사람 승인은 별개다. 1·4·9번, 기존111·다른 자동화·플랫폼은 보존했다.'
    assert marker.count(old)==1
    updated=marker.replace(old,replacement); new=raw[:a]+updated+raw[z:]
    assert new[:a]==raw[:a] and new[a+len(updated):]==raw[z:]
    doc.write_bytes((b'\xef\xbb\xbf' if before.startswith(b'\xef\xbb\xbf') else b'')+new.encode('utf8'))
    docscopes=[dict(path=str(doc),ownMarkerSha256=hashlib.sha256(updated.encode('utf8')).hexdigest())]
    doc=ROOT/'docs/VIDEO_WORKLIST.md'; before=doc.read_bytes(); raw=before.decode('utf-8-sig')
    a,z=raw.index(start),raw.index(end)+len(end); marker=raw[a:z]
    note='2026-11-16 후속 선택 수정9/9 완료. 쉬운 설명·실제 예시를 보강한 최신 검수본은 아래와 같다. 1·4·9번은 이전 버전을 보존했다. 사람 검수와 게시 승인은 대기 상태다.'
    assert note not in marker
    table=['| 번호 | 제목 | 실제 길이 | 버전 상태 | 사람 검수 |','|---|---|---:|---|---|']
    for row in manifest['projects']:
        title=Path(row['artifacts']['metadataKo']['path']).read_text('utf8').splitlines()[0]
        table.append(f"| {row['order']} | {title.replace('|','/')} | {row['actualMixSeconds']:.2f}초 | {'수정본 준비' if row['order'] in SELECTED else '기존본 유지'} | 대기 |")
    updated=marker.replace('local-final-review-v1.html','local-final-review-v4.html').replace('local-final-review-manifest-v1.json','local-final-review-manifest-v4.json')
    updated=updated[:-len(end)].rstrip()+'\n\n'+note+'\n\n'+'\n'.join(table)+'\n'+end
    new=raw[:a]+updated+raw[z:]
    assert new[:a]==raw[:a] and new[a+len(updated):]==raw[z:]
    doc.write_bytes((b'\xef\xbb\xbf' if before.startswith(b'\xef\xbb\xbf') else b'')+new.encode('utf8'))
    docscopes.append(dict(path=str(doc),ownMarkerSha256=hashlib.sha256(updated.encode('utf8')).hexdigest()))
    validation=dict(sourceInputs=[pin(p) for p in sorted(sources)], scopedSharedInputs=scopes,
                    scopedDocInputs=docscopes,
                    runtimeEvidence=[pin(queue)]+[x['revisionBundle'] for x in selected],
                    progress=dict(finalVideos=12,selectedRevisions=9,pendingSelectedRevisions=0,
                                  actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[]))
    save(H/'selected-clarity-final-validation-v135.json',validation)
    print(json.dumps(dict(completion=pin(complete),page=pin(page),manifest=pin(manifestpath),
                          selectedRevisions=9,videos=12,foreignContentPreserved=True,humanApproval=False)))

if __name__=='__main__': main()
