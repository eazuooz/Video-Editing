from common import *
P=R/'projects/game-math-polygon-partition-v2';H=P/'production/concept-fit-v2'
old=read(H/'composition-before-square-cue.json');new=read(H/'composition.json');oldmap={s['id']:s for s in old['scenes']};unchanged=[s['id'] for s in new['scenes'] if s['sha256']==oldmap[s['id']]['sha256']];assert len(unchanged)==23
code=(B/'qa-m14.py').read_text(encoding='utf8').replace("for s in T['scenes']:\n times=","for s in T['scenes']:\n if s['id']!='QG06':continue\n times=")
code=code.replace("for tm in sorted(set(round(x,3) for x in times)):","times += [(c['start']+c['end'])/2 for c in read(H/'captions.json')['cues'] if c['scene']=='QG06']\n times += [s['start']+x for x in [2.2,2.4,2.7,3,3.4,3.75,4,4.8,6,8] if x<s['seconds']]\n for tm in sorted(set(round(x,3) for x in times)):")
code=code.replace("['QG04','14','15','16','QG05','17','QG06','QB13','QG09','19','QG07','21']","['QG06']")
exec(compile(code,str(B/'qa-m14.py'),'exec'))
q=read(H/'qa.json');q['inheritedEvidence']=dict(parentQa=rel(H/'qa-before-square-cue.json'),parentNativePlayback=rel(H/'parent-native-playback.json'),unchangedScenes=unchanged,unchangedSceneCount=23,scope='Only QG06 composite recut, no audio/caption/frame-count change. Parent full playback plus changed scene native replay.');save(H/'qa.json',q)
c=read(H/'caption-pixel-coverage-before-square-cue.json');c.update(masterSha256=read(H/'outputs.json')['outputs'][1]['sha256'],deltaFrames=q['frames'],deltaSheets=q['sheets'],deltaMobile=q['mobile'],deltaDirectReview='pending',parentEvidence=rel(H/'caption-pixel-coverage-before-square-cue.json'),unchangedScenes=unchanged);save(H/'caption-pixel-coverage.json',c)
