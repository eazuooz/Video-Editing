from pathlib import Path
import json
R=Path('D:/Github/VideoEditing');B=R/'production/batches/private-math-gameplay-20261024/m14-gameplay-abstract-v5';P=R/'projects/game-math-polygon-partition-v2'
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
scenes=[
 {'id':'A','title':'모양을 나눈다는 질문','lines':['타일을 이어 붙이면 땅의 모양이 바뀝니다. 이렇게 만든 땅을 삼각형으로 나눌 때, 무엇을 지켜야 할까요?']},
 {'id':'B','title':'빈 공간도 보존','lines':['호수를 그린 자리도, 땅으로 채우면 안 되겠죠.']},
 {'id':'C','title':'오늘의 핵심','lines':['오늘은 조각의 개수만 세는 데서 한 걸음 더 나아가겠습니다. 원래 땅은 빠짐없이 덮고, 빈 공간은 그대로 남기는 분할을 찾아보겠습니다.']}
]
save(B/'intro.ko.json',{'slug':'game-math-polygon-partition-v2','scenes':scenes})
m=json.loads((P/'project.json').read_text('utf-8-sig'));m['paths']['script']=(B/'intro.ko.json').relative_to(R).as_posix();m['tts'].update(renderMode='scene',outputDir='projects/game-math-polygon-partition-v2/production/local/gameplay-abstract-v5/intro-audio',filenameStem='abstract',sceneGapSeconds=.30,maxNewTokens=1536,gpuMinimumFreeMiB=8192,gpuProfileReason='Existing approved Qwen1.7B batch1 scene profile; new opening only. CPU selected while other GPU activity is present.');m['editing']['narrationPlacement']='continuous-across-example-and-explanation';m['editing']['exampleSeconds']=0
save(B/'intro-manifest.json',m)
p=B/'checkpoint.json';d=json.loads(p.read_text('utf8'));d['introScript']='intro.ko.json';d['ttsChoice']={'device':'cpu','reason':'Other active GPU use observed; short added introduction uses same model/reference without terminating or delaying other work. Body PCM untouched.'};save(p,d)
print('Three abstract beats prepared. Body unchanged.')
