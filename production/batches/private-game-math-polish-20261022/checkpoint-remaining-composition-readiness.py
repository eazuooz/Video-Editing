"""Verify preserved partial compositions and inventory exact remaining source gaps."""
import datetime
from polish_common import *

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
rows = {}
for ident in ['M09','M10','M11','M12','M17']:
    e = Episode(ident); e.authorized()
    composition = read(e.H/'composition-polish.json')
    assert composition['planSha256'] == sha(R/composition['plan'])
    assert composition['globalAssSha256'] == sha(R/composition['globalAss'])
    evidence = composition['explanationEvidence']
    assert evidence['sha256'] == sha(R/evidence['path'])
    review = read(R/evidence['path'])
    assert review['status'] == 'passed-source-visual-review'
    partial = composition['partialPreflightEvidence']
    for kind in ['still','moving']:
        assert partial[kind+'ReviewSha256'] == sha(R/partial[kind+'Review'])
    counts = {'actual':0, 'explanation':0}
    for sid, item in composition['inputs'].items():
        scene = next(s for s in e.T['scenes'] if s['id']==sid)
        assert sha(R/item['path']) == item['sha256']
        e.verify(R/item['path'], scene['frames'])
        counts['explanation' if scene['classification']=='explanation' else 'actual'] += 1
    assert counts['explanation'] == sum(s['classification']=='explanation' for s in e.T['scenes'])
    missing = [{'scene':s['id'], 'frames':s['frames'], 'sourceId':s['cut']['sourceId'],
                'preservedNarration':[c['text'] for c in s['cues']]}
               for s in e.T['scenes'] if s['id'] not in composition['inputs']]
    assert all(next(s['classification'] for s in e.T['scenes'] if s['id']==m['scene']) != 'explanation' for m in missing)
    rows[ident] = {'composition':rel(e.H/'composition-polish.json'),
        'compositionSha256':sha(e.H/'composition-polish.json'), 'registeredInputs':counts,
        'missingActualInputs':missing, 'timelineSha256':sha(e.P/'production/timeline.json'),
        'fullMasterReady':False, 'newRender':False, 'newTts':False,
        'reviewScope':'Current file hashes, native1920x1080/60fps and exact frame counts verified. Prior unchanged source/partial visual reviews reused. No new full encoded master or human approval.'}
report = {'checkedAt':now, 'status':'all-reviewed-explanation-inputs-registered-remaining-game-sources-blocked',
    'episodes':rows, 'missingActualSceneCount':sum(len(r['missingActualInputs']) for r in rows.values()),
    'wholeMastersAdded':0}
save(B/'composition-readiness.json', report)

archive = read(B/'portal-archive-mirror-review.json')
moddb_url = 'https://www.moddb.com/games/portal-2/videos/e3-2010-thermal-discouragement-beam'
youtube_url = 'https://www.youtube.com/watch?v=wUQaS4KhCtc'
archive['items'] = [r for r in archive['items'] if r['url'] not in [moddb_url,youtube_url]]
archive['items'].append({'url':moddb_url, 'filename':'Portal_E3_Pt4.wmv',
    'observation':'Archive detail page directly lists1280x720 and01:54. No new media downloaded; this mirror does not establish native FHD.',
    'listedDimensions':[1280,720], 'adopted':False})
metadata = R/'shared/output/private-game-math-polish-20261022/fhd-candidates/wUQaS4KhCtc.research.info.json'
thumbnail = metadata.with_name('wUQaS4KhCtc.research.jpg')
j = read(metadata)
archive['items'].append({'url':youtube_url, 'title':j['title'], 'uploader':j['uploader'],
    'metadata':rel(metadata), 'metadataSha256':sha(metadata),
    'thumbnail':rel(thumbnail), 'thumbnailSha256':sha(thumbnail),
    'availableFormats':[[f.get('format_id'), f.get('width'), f.get('height'), f.get('fps')] for f in j['formats'] if (f.get('height') or 0)>=1080],
    'observation':'Directly viewed thumbnail shows a physical monitor, surrounding bezel and perspective distortion. Uploader credits a friend for filming the event.1080p25 stream exists, but that is not verification of a native FHD game capture or compatible shot/rights.',
    'decision':'Do not adopt off-screen event recording as native gameplay replacement; existing rules also exclude stage demonstration footage. No video downloaded, decoded or selected.',
    'adopted':False})
archive.update(checkedAt=now, scope='Archive page/metadata/thumbnail evidence; no new gameplay source adopted. Do not repeat unchanged rejected mirrors, off-screen recordings or inaccessible archive attempts.')
save(B/'portal-archive-mirror-review.json', archive)

p = read(B/'checkpoint.json')
p.update(updatedAt=now, active=[], currentJobs=[],
    nextAction='All polished explanation clips and24 available FHD game slots are registered and hash/frame verified in five partial compositions. Ten Portal2 actual slots remain source-blocked; consult composition-readiness.json for exact preserved narration/actions and portal-archive-mirror-review.json plus existing format reports before further research. Do not repeat unchanged low-resolution/off-screen/inaccessible candidates, reinterpret third-party retail footage as an official demo, upscale, rewrite narration or re-render unchanged explanations. Resume affected source/cut/guide work only on a materially new matching native-FHD source; then assemble and perform complete encoded-master QA. Preserve11 ready masters.')
p['compositionInputReadiness'] = {'report':rel(B/'composition-readiness.json'),
    'sha256':sha(B/'composition-readiness.json'), 'allExplanationInputsRegistered':True,
    'registeredExplanationClips':sum(r['registeredInputs']['explanation'] for r in rows.values()),
    'registeredGameClips':24, 'missingActualSceneCount':10, 'fullMasterCountAdded':0}
p['sourceIssues']['portalArchiveMirrors'].update(sha256=sha(B/'portal-archive-mirror-review.json'),
    result='Additional ModDB mirror explicitly lists720p. A newly located1080p25 Gamescom upload is a filmed monitor/event, not verified native gameplay; rejected from production. No source adopted.')
p['sourceReplacementDecision']['summaryKo']='11편 검수대기 유지. 나머지5편은 설명66장면과 확보한 FHD 게임24장면을 편집 구성에 연결하고 파일·프레임 검사를 완료. M09 5/6, M10 8/9, M11 3/6, M12 5/8, M17 3/5 게임 장면 확보. 남은 Portal2 10장면의 적합한 FHD 원본과 전체 완성본 검수는 미완료.'
p['completedJobs'].append('Registered38 already reviewed M11/M12/M17 explanation clips without rerender; verified all90 available inputs across five partial compositions. Ten Portal2 game slots remain blocked. ModDB720p and Gamescom filmed-screen candidates rejected; no new complete master.')
p['latestStatusReport'].update(at=now, activeMediaWorkerObserved=False)
save(B/'checkpoint.json', p)
blockers = read(B/'source-blockers.json')
for ident in rows:
    blockers[ident].update(updatedAt=now, compositionReadiness=rel(B/'composition-readiness.json'),
        missingActualScenes=[m['scene'] for m in rows[ident]['missingActualInputs']])
save(B/'source-blockers.json', blockers)
w = read(R/'shared/publishing/video-worklist.json')
for key in ['sourceReplacementDecision','compositionInputReadiness']:
    w['privateMathPolish'][key] = p[key]
w['privateMathPolish']['updatedAt'] = now
save(R/'shared/publishing/video-worklist.json', w)
print('Five partial compositions verified:66 explanation +24 game inputs,10 game slots missing;11 full masters ready, no new render.')
