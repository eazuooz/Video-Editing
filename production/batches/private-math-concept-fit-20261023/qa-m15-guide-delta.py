from common import *
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2'
old=read(H/'composition-before-guide-repair.json');new=read(H/'composition.json');oldmap={s['id']:s for s in old['scenes']};unchanged=[s['id'] for s in new['scenes'] if s['sha256']==oldmap[s['id']]['sha256']];assert len(unchanged)==19
code=(B/'qa-m15.py').read_text(encoding='utf8').replace("Q=O/'qa'","Q=O/'qa-guide-delta'")
code=code.replace("for s in T['scenes']:\n times=","for s in T['scenes']:\n if s['id'] not in ['02','05','08']:continue\n times=")
code=code.replace("for tm in sorted(set(round(x,3) for x in times)):","times += [(c['start']+c['end'])/2 for c in read(H/'captions.json')['cues'] if c['scene']==s['id']]\n for tm in sorted(set(round(x,3) for x in times)):")
code=code.replace("['02','05','08','11','14','17','19','21','09','13','18','22']","['02','05','08']")
exec(compile(code,str(B/'qa-m15.py'),'exec'))
q=read(H/'qa.json');q['inheritedEvidence']=dict(parentQa=rel(H/'qa-before-guide-repair.json'),parentPixelReview=rel(H/'parent-pixel-review.json'),parentNativePlayback=rel(H/'parent-native-playback.json'),unchangedScenes=unchanged,unchangedSceneCount=19,scope='Only3 gameplay composites and their source audio changed; all narration and caption timing/model frames retained.');save(H/'qa.json',q)
c=read(H/'caption-pixel-coverage-before-guide-repair.json');c.update(masterSha256=read(H/'outputs.json')['outputs'][1]['sha256'],deltaFrames=q['frames'],deltaSheets=q['sheets'],deltaMobile=q['mobile'],deltaDirectReview='pending',parentEvidence=rel(H/'caption-pixel-coverage-before-guide-repair.json'),unchangedScenes=unchanged);save(H/'caption-pixel-coverage.json',c)
