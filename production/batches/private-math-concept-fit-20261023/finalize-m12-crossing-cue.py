from common import *
P=R/'projects/game-math-triangle-addresses-v2';H=P/'production/concept-fit-v2'
parent=read(H/'outputs-before-crossing-cue.json');qa=read(H/'qa-before-crossing-cue.json');coverage=read(H/'caption-pixel-coverage-before-crossing-cue.json')
assert parent['outputs'][1]['sha256']==sha(R/parent['outputs'][1]['path'])
save(H/'parent-native-playback.json',dict(masterSha256=parent['outputs'][1]['sha256'],tool='cua_repl tab65',segments=[dict(start=0,end=820.533333,rate=1,ended=True)],checkedAt=now(),failedEarlierAttempt=dict(end=794.248,reason='Prior file was overwritten during playback; not a completed review'),actualListening=False,continuousHumanViewing=False))
qa.update(directVisualReview='All58 final frames on5 sheets, all134 extra caption frames on12sheets covering178cues, and12actual375px frames directly inspected. PG04 crossing speech led motion; single-scene repair follows.',nativePlayback=rel(H/'parent-native-playback.json'));save(H/'qa-before-crossing-cue.json',qa)
coverage.update(directReview='All12sheets directly inspected; single PG04 timing discrepancy addressed separately.',reviewedAt=now());save(H/'caption-pixel-coverage-before-crossing-cue.json',coverage)
authorized('M12')
for name in ['compose','assemble']:run(['C:/Python/python.exe','-X','utf8',B/f'{name}-m12.py'])
