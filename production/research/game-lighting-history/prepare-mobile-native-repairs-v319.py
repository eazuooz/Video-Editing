"""Prepare four evidenced visual repairs; do not approve source or final pixels."""
from pathlib import Path
import importlib.util,copy,json
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
old=m.read(P/'part1-input-overrides-v289.json');baseline=m.read(P/'part1-final-visual-build-v316.json')
assert baseline['wholeDecodeExitCode']==0 and baseline['frames']==89148
dest=P/'part1-mobile-native-repair-proposal-v319.json';assert not dest.exists()
flat=[396,262,1128,818];conference=[836,486,788,572]
changes={
 'mobile-device-policy:native':dict(reason='Replace blank loading with actual loaded profile list, then crop only the editor across the original conference-layout transition.',baseFrame=2160,pieces=[dict(inFrame=2160,outFrame=3203,cropRect=flat),dict(inFrame=3203,outFrame=3533,cropRect=conference)],identity='Fortnite · 모바일 Device Profile 편집기',qualifier='실제 설정 목록 · 기기별 정책 관찰'),
 'mobile-lod-settings:native':dict(reason='Crop the actual LOD editor on both sides of the source layout switch; exclude the presenter without changing settings action.',baseFrame=3960,pieces=[dict(inFrame=3960,outFrame=4004,cropRect=conference),dict(inFrame=4004,outFrame=5362,cropRect=flat)],identity='Fortnite · 모바일 Texture LOD 설정',qualifier='그룹별 최대 크기·LOD Bias · 실제 편집기'),
 'fortnite-mobile-test:native':dict(reason='Move unique normal-speed HQ/LQ rock intervals under cue295 rather than the GBufferNormals wall. Keep the diagnostic graph and all source conditions.',baseFrame=14370,pieces=[dict(inFrame=a,outFrame=b,cropRect=[82,174,1838,906]) for a,b in [(14840,14992),(14530,14680),(14370,14530),(15240,15415),(14992,15240),(14680,14840),(15445,15540)]],identity='Fortnite · 모바일 실제 테스트 맵',qualifier='HQ / LQ Noise bump map · 원본 진단값은 장면별 조건'),
 'fortnite-normal-material:native':dict(reason='Expand the actual phone gameplay viewport, including graph, controls and labels; exclude the conference presenter and slide ground.',baseFrame=15780,pieces=[dict(inFrame=15780,outFrame=16664,cropRect=[620,360,1280,640])],identity='Fortnite · 모바일 재질 테스트',qualifier='법선·재질의 표시 조건 관찰 · 원본 게임 통계 보존')}
for c in old['effectiveCuts']:
 if c['id'] not in changes:continue
 change=changes[c['id']];change['input']=copy.deepcopy(c)
 assert sum(p['outFrame']-p['inFrame'] for p in change['pieces'])==c['frames']
 spans=sorted((p['inFrame'],p['outFrame']) for p in change['pieces'])
 assert all(a[1]<=b[0] for a,b in zip(spans,spans[1:])), 'No repeated source frames'
 for ref in [c['video'],c['pcm']]:assert m.sha(R/ref['path'])==ref['sha256']
 sourceSpans=[(q['inFrame'],q['outFrame']) for other in old['effectiveCuts'] if other['id']!=c['id'] and other.get('video',{}).get('path')==c['video']['path'] for q in other.get('proposedCuts',[])]
 assert all(b<=u or a>=v for a,b in spans for u,v in sourceSpans),'Do not borrow another used native interval'
proof=dict(preparedAt=m.stamp(),baselineBuild=dict(path=m.rel(P/'part1-final-visual-build-v316.json'),sha256=m.sha(P/'part1-final-visual-build-v316.json')),changes=changes,
 observedIssues=dict(path=m.rel(P/'part1-final-board-direct-progress-v297.json'),sha256=m.sha(P/'part1-final-board-direct-progress-v297.json')),
 sourceInspection=dict(path='production/research/game-lighting-history/local/mobile-source-inspect-v318',exactNormalized60FpsBoundaries=dict(device=3203,lod=4004),allDisplayedInspectionBoardsDirectlyRead=True),
 preserved=dict(finalFrames=89148,actualFrames=53057,explanationFrames=35371,paragraphs=77,koCues=335,enCues=409,narrationPcm=True,audioMix=True,chapterTimes=True,other90CutInputs=True),
 noSourceAudio=True,noLoops=True,noSlowdown=True,newTts=0,newGitImages=0,allSelectedSourcesNormalSpeedApproved=False,allRepairPixelsApproved=False,allFinalPixelsReviewed=False,qaApproved=False,uploaded=False)
m.save(dest,proof);print(json.dumps(dict(prepared=m.rel(dest),repairs=4,allApproved=False,newTts=0)))
