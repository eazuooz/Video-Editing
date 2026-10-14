"""Seal only the directly observed corrected input, retaining failed final history."""
from pathlib import Path
import importlib.util, copy
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
ep=P/'part1-road-preview-execution-v330.json';e=m.read(ep)
rp=P/'part1-road-native-repair-proposal-v329.json';proposal=m.read(rp)
assert e['status']=='complete-awaiting-direct-review' and e['exitCode']==0 and len(e['results'])==1
assert e['proposalSha256']==m.sha(rp)
r=copy.deepcopy(e['results'][0])
for k in ['native','preview']:assert m.sha(R/r[k]['path'])==r[k]['sha256']
assert r['technical']['wholeDecode']['exitCode']==0 and r['technical']['allPresentationPtsContinuous']
r.update(fullSelectedIntervalActuallyPlayed=True,playbackRate=1,normalSpeedInputPixelsApproved=True,selectedForCurrentPrivateTechnicalPair=True,
 actualObservation='Complete17.283s normal-speed input played through observed17.283 PAUSED endpoint. At3.116 ordinary road/spline plus diagnostic-mode menu;7.388 green Mask visualization and the exact green-region caption agree. Independent cue-start6.717 and cue-end9.890 show the green region;at9.890 the caption is visible.16.165 and endpoint return to ordinary shaded road with the narrated contrast caption. Presenter excluded by unchanged exact crop;original mode/road label and source UI remain readable;bottom boxed captions retain960,970. No simulation, source audio, loop or slowdown.',
 cue204GreenRegionConfirmed=True,fixedBottomCaptionPixelsReviewed=True,sourceAndInputNormalSpeedObserved=True,
 allFinalPixelsReviewed=False,humanWholeListening='pending',humanPronunciation='pending')
out=P/'part1-road-native-input-direct-review-v331.json';assert not out.exists()
proof={'reviewedAt':m.stamp(),'execution':{'path':m.rel(ep),'sha256':m.sha(ep)},'proposal':{'path':m.rel(rp),'sha256':m.sha(rp)},
 'records':[r],'allOneFullInputIntervalsActuallyPlayed':True,'allOneSelectedForCurrentPrivateTechnicalPair':True,
 'resolvedIssue':'Source interval shifted24–41.283 to36–53.283;green diagnostic view now appears during spoken green-region sentence. The failed323 final review is preserved.',
 'framesAndNarrationTimingUnchanged':True,'mixAndKoEnBytesUnchanged':True,'newTts':0,'newAudioMix':0,'newGitImages':0,
 'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending'}
m.save(out,proof);print(m.rel(out))
