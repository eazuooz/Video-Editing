from common import *
P=R/'projects/game-math-polygon-partition-v2';H=P/'production/concept-fit-v2';authorized('M14')
parent=read(H/'outputs-before-square-cue.json');qa=read(H/'qa-before-square-cue.json');coverage=read(H/'caption-pixel-coverage-before-square-cue.json')
assert parent['outputs'][1]['sha256']==sha(R/parent['outputs'][1]['path'])
save(H/'parent-native-playback.json',dict(masterSha256=parent['outputs'][1]['sha256'],tool='cua_repl tab68',segments=[dict(start=0,end=670.516667,rate=1,ended=True)],checkedAt=now(),actualListening=False,continuousHumanViewing=False))
qa.update(directVisualReview='All91 final frames on8 sheets, all96 additional caption frames on8sheets covering149cues, and12actual375px frames directly inspected. QG06 square/star mismatch corrected by a single native cut recut.',nativePlayback=rel(H/'parent-native-playback.json'));save(H/'qa-before-square-cue.json',qa)
coverage.update(directReview='All8sheets directly inspected; QG06 mismatch addressed separately.',reviewedAt=now());save(H/'caption-pixel-coverage-before-square-cue.json',coverage)
run(['C:/Python/python.exe','-X','utf8',B/'assemble-m14.py'])
run(['C:/Python/python.exe','-X','utf8',B/'qa-m14-square-delta.py'])
