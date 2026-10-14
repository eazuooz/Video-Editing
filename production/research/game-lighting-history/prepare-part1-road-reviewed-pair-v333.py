"""Preserve the proven323 producer gates, permitting only reviewed road-source delta."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=Path(__file__).with_name('build-part1-reviewed-pair-v323.py')
dest=Path(__file__).with_name('build-part1-reviewed-pair-v333.py');assert not dest.exists()
code=source.read_text('utf-8-sig').replace('v323','v333').replace('V323','V333')
def replace(old,new):
 global code
 assert code.count(old)==1,old
 code=code.replace(old,new)
replace("P/'part1-final-visual-build-v322.json'","P/'part1-final-visual-build-v332.json'")
replace("assert visualproof['retainedOther90InputsByteIdentical'] and visualproof['newTts']==0 and visualproof['newAudioMix']==0",
 "assert visualproof['retainedOther93InputsByteIdenticalToV322'] and visualproof['newTts']==0 and visualproof['newAudioMix']==0")
replace("assert len(currentCuts)==94",'''assert len(currentCuts)==94
roadReviewPath=P/'part1-road-native-input-direct-review-v331.json';roadReview=m.read(roadReviewPath)
assert roadReview['allOneFullInputIntervalsActuallyPlayed'] and roadReview['allOneSelectedForCurrentPrivateTechnicalPair']
assert visualproof['inputOverrides']['roadReview']['sha256']==m.sha(roadReviewPath)
assert roadReview['execution']['sha256']==m.sha(ROOT/roadReview['execution']['path'])
assert roadReview['proposal']['sha256']==m.sha(ROOT/roadReview['proposal']['path'])
road=roadReview['records'][0];assert road['id']=='geometry-road-mask:native'
assert road['fullSelectedIntervalActuallyPlayed'] and road['playbackRate']==1 and road['normalSpeedInputPixelsApproved'] and road['cue204GreenRegionConfirmed']
for mediaKey in ['native','preview']:assert m.sha(ROOT/road[mediaKey]['path'])==road[mediaKey]['sha256']
assert currentCuts[road['id']]['sha256']==road['native']['sha256'] and currentCuts[road['id']]['sourceCuts']==[{'inFrame':2160,'outFrame':3197}]
assert currentCuts[road['id']]['frames']==road['frames']==1037
previous322path=P/'part1-final-visual-build-v322.json';previous322=m.read(previous322path)
assert visualproof['previousVisual']['sha256']==m.sha(previous322path)
for before in previous322['cuts']:
 now=currentCuts[before['id']]
 assert (now['frames'],now['fromFrame'],now['toFrame'])==(before['frames'],before['fromFrame'],before['toFrame'])
 if before['id']!=road['id']:assert now['sha256']==before['sha256']
assert sum(c['frames'] for c in currentCuts.values())==plan['bodyFrames']''')
replace("if key not in mobileInputs and key not in ['outer-comparison-before:model','texture-dependent-conversion:native','cyber-surface-observation:native']:",
 "if key not in mobileInputs and key not in ['outer-comparison-before:model','texture-dependent-conversion:native','cyber-surface-observation:native','geometry-road-mask:native']:")
replace("for r in oldvisual['repairs']:\n if r['id'] in mobileInputs:",
 "for r in oldvisual['repairs']:\n if r['id']==road['id']:continue\n if r['id'] in mobileInputs:")
replace("if key not in ['texture-dependent-conversion:native','cyber-surface-observation:native']:",
 "if key==road['id']:continue\n if key not in ['texture-dependent-conversion:native','cyber-surface-observation:native']:")
replace("if key in mobileInputs:continue\n if key!='cyber-surface-observation:native':",
 "if key in mobileInputs or key==road['id']:continue\n if key!='cyber-surface-observation:native':")
replace("'mobileInputDirectReviewSha256':m.sha(mobileReviewPath),",
 "'mobileInputDirectReviewSha256':m.sha(mobileReviewPath),'roadInputDirectReviewSha256':m.sha(roadReviewPath),")
replace("Current pair after four directly reviewed mobile repairs: exact current mix and captions; fresh final pixels remain unapproved.",
 "Current pair after one directly reviewed road-source delta. Preserve37-window mixed approval,335/409 captions and all other93 inputs. Final pixels remain unapproved.")
code=code.replace("'build-part1-reviewed-pair-v333.py']","'build-part1-reviewed-pair-v333.py','build-part1-road-preview-v330.py','build-part1-road-repaired-visual-v332.py']")
compile(code,str(dest),'exec')
dest.write_text(code,'utf8');print(m.rel(dest))
