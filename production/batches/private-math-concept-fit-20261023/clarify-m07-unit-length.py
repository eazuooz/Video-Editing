from common import *
import shutil
P=R/'projects/game-math-interpolation-paths-v2';H=P/'production/concept-fit-v2'
assert not (P/'production/local/concept-fit-v2/audio/paragraph-takes.json').exists(),'Never change generated speech inputs'
path=B/'m07-narration-edits.json';d=read(path)
changes={1:['빨간 선은 문에 붙은 방향입니다. 문은 돌아가도 크기는 그대로입니다.','The red line is attached to the door. The door turns without changing its size.'],2:['모형의 크기와 쿼터니언의 단위 길이는 다른 이야기입니다. 쿼터니언에서는 네 성분 제곱의 합이 일인지 검사하죠.','The model’s size and a quaternion’s unit length are different concepts. For a quaternion, we check that the squares of its four components sum to one.']}
for n,pair in changes.items():d['edits']['IG10'][str(n)]=pair
save(path,d)
plan=read(H/'voice-plan.json');save(H/'voice-plan.before-unit-length-clarification.json',plan)
for lang,index in [('ko',0),('en',1)]:
 p=P/f'script/concept-fit-v2/narration.{lang}.json';d=read(p);scene=next(s for s in d['scenes'] if s['id']=='IG10')
 for n,pair in changes.items():scene['lines'][n-1]=pair[index]
 save(p,d)
for job in plan['jobs']:
 if job['scene']=='IG10' and job['line'] in changes:
  job['text']=changes[job['line']][0];job['textSha256']=hashlib.sha256(job['text'].encode()).hexdigest()
for v in plan['inputs'].values():v['sha256']=sha(R/v['file'])
plan['identitySha256']=hashlib.sha256(json.dumps(dict(inputs=plan['inputs'],jobs=plan['jobs'],tts=plan['tts']),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
plan['preparedAt']=now();save(H/'voice-plan.json',plan)
save(H/'unit-length-clarification.json',dict(reason='Do not equate the visible3D arrow or physical door size with quaternion4D unit norm.',generatedTakesChanged=False,actualListening=False))
print(plan['identitySha256'])
