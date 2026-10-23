"""Full decode of the new pair; re-inspect every cue of the one changed scene."""
from common import *
P=R/'projects/game-math-triangle-addresses-v2';H=P/'production/concept-fit-v2'
old=read(H/'composition-before-crossing-cue.json');new=read(H/'composition.json');oldmap={s['id']:s for s in old['scenes']}
unchanged=[s['id'] for s in new['scenes'] if s['sha256']==oldmap[s['id']]['sha256']]
assert len(unchanged)==21 and 'PG04' not in unchanged
caps=read(H/'captions.json')['cues'];affected=[x for x in caps if x['scene']=='PG04']
code=(B/'qa-m12.py').read_text(encoding='utf8')
code=code.replace("for s in T['scenes']:\n times=", "for s in T['scenes']:\n if s['id']!='PG04':continue\n times=")
code=code.replace("for tm in sorted(set(round(x,3) for x in times)):","times += [(c['start']+c['end'])/2 for c in read(H/'captions.json')['cues'] if c['scene']=='PG04']\n times += [s['start']+x for x in [3,5,6,7,8,10,12,15] if x<s['seconds']]\n for tm in sorted(set(round(x,3) for x in times)):")
code=code.replace("['11','PG04','12','13','14','15','17','18','19','PG07','21','22']","['PG04']")
exec(compile(code,str(B/'qa-m12.py'),'exec'))
q=read(H/'qa.json');q['inheritedEvidence']=dict(parentQa=rel(H/'qa-before-crossing-cue.json'),parentNativePlayback=rel(H/'parent-native-playback.json'),unchangedScenes=unchanged,unchangedSceneCount=21,scope='Only PG04 visual cue advanced; all other composite scene hashes and entire audio/caption timing unchanged. Parent full playback plus changed-scene native replay required.');save(H/'qa.json',q)
coverage=read(H/'caption-pixel-coverage-before-crossing-cue.json');coverage.update(masterSha256=read(H/'outputs.json')['outputs'][1]['sha256'],deltaFrames=q['frames'],deltaSheets=q['sheets'],deltaMobile=q['mobile'],deltaDirectReview='pending',parentEvidence=rel(H/'caption-pixel-coverage-before-crossing-cue.json'),unchangedScenes=unchanged);save(H/'caption-pixel-coverage.json',coverage)
