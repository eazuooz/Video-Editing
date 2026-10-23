from common import *
P=R/'projects/game-math-camera-frustum';H=P/'production/concept-fit-v2'
old=read(H/'composition-before-pane-repair.json');new=read(H/'composition.json');oldmap={s['id']:s for s in old['scenes']};unchanged=[s['id'] for s in new['scenes'] if s['sha256']==oldmap[s['id']]['sha256']];assert len(unchanged)==21
code=(B/'qa-m16.py').read_text(encoding='utf8').replace("Q=O/'qa'","Q=O/'qa-pane-delta'")
code=code.replace("for s in T['scenes']:\n times=","for s in T['scenes']:\n if s['id'] not in ['16']:continue\n times=")
code=code.replace("for tm in sorted(set(round(x,3) for x in times)):","times += [(c['start']+c['end'])/2 for c in read(H/'captions.json')['cues'] if c['scene']==s['id']]\n for tm in sorted(set(round(x,3) for x in times)):")
code=code.replace("['02','05','08','11','13','16','19','21','09','14','18','22']","['16']")
exec(compile(code,str(B/'qa-m16.py'),'exec'))
q=read(H/'qa.json');q['inheritedEvidence']=dict(parentQa=rel(H/'qa-before-pane-repair.json'),parentPixelReview=rel(H/'parent-pixel-review.json'),parentNativePlayback=rel(H/'parent-native-playback.json'),unchangedScenes=unchanged,unchangedSceneCount=21,scope='Only scene16 model pane placement changed; all audio unchanged; all narration and caption timing/model frames retained.');save(H/'qa.json',q)
c=read(H/'caption-pixel-coverage-before-pane-repair.json');c.update(masterSha256=read(H/'outputs.json')['outputs'][1]['sha256'],deltaFrames=q['frames'],deltaSheets=q['sheets'],deltaMobile=q['mobile'],deltaDirectReview='pending',parentEvidence=rel(H/'caption-pixel-coverage-before-pane-repair.json'),unchangedScenes=unchanged);save(H/'caption-pixel-coverage.json',c)
