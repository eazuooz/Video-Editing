"""Record actual partial review and propose a labelled source comparison; no approval."""
from pathlib import Path
import importlib.util, json
spec = importlib.util.spec_from_file_location('m',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
ex=P/'part1-texture-preview-execution-v343.json';e=m.read(ex)
assert e['status']=='complete-awaiting-direct-review' and e['exitCode']==0
boards=R/'production/research/game-lighting-history/local/part1-texture-preview-cues-v343b'
review=dict(reviewedAt=m.stamp(),execution=dict(path=m.rel(ex),sha256=m.sha(ex)),
    all9BoardsDirectlyRead=True,all50ImagesDirectlyRead=True,
    boards=[dict(path=m.rel(boards/f'board-{i:03}.png'),sha256=m.sha(boards/f'board-{i:03}.png'),directlyRead=True) for i in range(1,10)],
    normalSpeedCompletePreviewsActuallyPlayed=True,playbackRate=1,
    textureTile=dict(input=next(x for x in e['results'] if x['id']=='texture-project-tile-settings:native'),
        approvedInputPixels=True,observations='Tile128, border4, feedback16 and AutoVT4096 are visible when the corresponding instructions occur; settings remain visible through the 24.2833-second preview. Five cues readable at fixed960,970. Presenter excluded.'),
    textureStack=dict(approvedInputPixels=False,reason='Graph and Stats are now readable, but stack1→3 appears around source112.2s, after cue84 at relative3.32–8.84. Retain this preview as rejected timing evidence.'),
    rejectedContinuousCandidate=dict(viewer='production/research/game-lighting-history/local/part1-texture-stack-aligned-source-v343c.html',interval=[105,131.11666666666667],completeActuallyPlayed=True,rate=1,endObserved=131.302,reason='Later part leaves the coordinate graph for a city/statistics demonstration; it does not support the middle coordinate-sharing narration.'),
    frameBoundaryLimitation='v343b selections used raw subtitle plan frames. Actual ASS centisecond boundaries differ by1frame in several cues. Final boundary extraction must use layout.metrics.assFirstFrame/exclusiveEndFrame; these previews do not approve final cue-edge pixels.',
    allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False,newGitImages=0,humanListeningPending=True)
m.save(P/'part1-texture-preview-partial-direct-review-v343c.json',review)
proposal=m.read(P/'part1-texture-source-repair-proposal-v342b.json')
c=proposal['inputs'][0]
c['proposedCuts']=[dict(inFrame=5400,outFrame=5599,condition='좌표 공유 · 연결 전'),dict(inFrame=6534,outFrame=6865,condition='입력 복제 · 연결 변경'),dict(inFrame=5599,outFrame=6534,condition='좌표 공유 · 연결 전 비교'),dict(inFrame=6865,outFrame=6967,condition='연결 변경 결과')]
assert sum(x['outFrame']-x['inFrame'] for x in c['proposedCuts'])==c['frames']
assert sorted((x['inFrame'],x['outFrame']) for x in c['proposedCuts'])==[(5400,5599),(5599,6534),(6534,6865),(6865,6967)]
c['observationBeat']['sourceContinuous']=False
c['sourceReview']=dict(viewer='production/research/game-lighting-history/local/part1-texture-reordered-source-v343c.html',fullCandidateActuallyPlayed=False,rate=1,
    reason='Compare the real before and real changed connection explicitly. All original90–116.1167 source frames occur once at normal speed, reordered to show the observed stack change during cue84. Each cut must be labelled so comparison is not mistaken for one continuous operation.')
c['comparisonLabelsRequired']=True
proposal.update(preparedAt=m.stamp(),allTwoSourceIntervalsActuallyPlayed=False,partialReview=dict(path=m.rel(P/'part1-texture-preview-partial-direct-review-v343c.json'),sha256=m.sha(P/'part1-texture-preview-partial-direct-review-v343c.json')),
    inputPixelsApproved=False,allFinalPixelsReviewed=False,qaApproved=False,uploaded=False)
m.save(P/'part1-texture-source-order-proposal-v343c.json',proposal)
original=R/'production/research/game-lighting-history/local/part1-texture-stack-aligned-source-v343c.html'
html=original.read_text('utf8');start=html.index('const rows=');end=html.index(';const pick=',start)
rows=[dict(id='texture-stack-labelled-comparison-source',path=c['video']['path'],ranges=[[x['inFrame']/60,x['outFrame']/60] for x in c['proposedCuts']],ko='같은 원본의 좌표 공유와 연결 변경을 비교합니다. 원본90–116.1167의 모든 프레임을 한 번씩 정상속도로 재배치한 후보이며, 연속 조작으로 오인하지 않도록 렌더에 연결 전/변경 상태를 표시해야 합니다.')]
html=html[:start]+'const rows='+json.dumps(rows,ensure_ascii=False)+html[end:]
(R/'production/research/game-lighting-history/local/part1-texture-reordered-source-v343c.html').write_text(html,'utf8')
cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp)
j['updatedAt']=m.stamp();j['episode04Part1TexturePartialReviewV343c']=dict(path=m.rel(P/'part1-texture-preview-partial-direct-review-v343c.json'),tileInputPixelsApproved=True,stackInputPixelsApproved=False,all9BoardsDirectlyRead=True)
j['ownedActiveWork']=dict(status='no-active-owned-media-worker',next='Direct labelled normal-speed source comparison, then rebuild only rejected stack input; reuse reviewed tile input')
m.save(cp,j)
print(json.dumps(dict(recorded=9,tileApproved=True,stackApproved=False,allFinalPixelsReviewed=False)))
