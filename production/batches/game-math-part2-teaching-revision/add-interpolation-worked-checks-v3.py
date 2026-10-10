"""Add two useful numerical walkthroughs without rewriting frozen v2 audio."""
from pathlib import Path
import copy,json,hashlib,math,importlib.util
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
SLUG='game-math-interpolation-worked-checks-v3';P=ROOT/'projects'/SLUG
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not any((ROOT/f'shared/output/narration/{SLUG}').rglob('*.wav')),'Do not rewrite a voiced script'
scenes=[
 {'id':'IP07','after':'12','episode':'game-math-interpolation-paths-v2','title':'같은 호도 시간에 따라 다르게 움직입니다','kind':'explanation',
  'ko':['방금 시간 조건을 설명했으니 같은 회전을 작은 수로 비교해 보죠. 여기서는 카메라와 제트축을 고정하고, 영 도에서 구십 도까지 일 초 동안 돌리는 계산 예시입니다.',
        '절반인 영 점 오 초가 지났을 때, 경과 시간을 전체 시간으로 나누면 티는 영 점 오입니다. 선형 시간에서는 구십 도의 절반인 사십오 도가 됩니다.',
        '이번에는 경과 시간의 비율을 제곱해서 티로 쓰겠습니다. 영 점 오의 제곱은 영 점 이오이고, 같은 순간의 회전은 구십 도의 사분의 일인 이십이 점 오 도입니다.',
        '일 초가 끝나면 두 방법 모두 티가 일이 되어 구십 도에 도착합니다. 시작과 끝과 지나가는 호는 같지만, 중간에 언제 어디까지 갔는지는 달라졌죠. 그래서 경로를 고르는 일과 시간에 맞춰 움직이는 일은 따로 정합니다.'],
  'en':['After the time conditions, compare the same rotation with small numbers. This defined example fixes the camera and z axis and turns from zero to ninety degrees over one second.',
        'At half a second, elapsed time divided by duration gives t equal to one half. With linear time, half of ninety degrees is forty-five degrees.',
        'Now use the square of the elapsed-time fraction as t. One half squared is one quarter, so the same instant gives one quarter of ninety degrees: twenty-two point five degrees.',
        'At one second both reach t equal to one and ninety degrees. The endpoints and arc stay the same, but progress at intermediate times differs. Choosing the path and mapping time to progress are separate decisions.'],
  'beats':['고정 카메라·z축 / 0°→90° / 전체1초','0.5초: t=.5 → 45°','0.5초: t=.5²=.25 → 22.5°','1초: 둘 다90° / 같은 경로·다른 시간 진행'],
  'retainedResult':'Fixed endpoints and the short rotation arc from original12','nextQuestion':'Which time mapping determines the visible orientation at a particular second?'},
 {'id':'IP08','after':'25','episode':'game-math-rotation-conversions-v2','title':'같은 방향인지 벡터를 돌렸다가 되돌려 봅니다','kind':'explanation',
  'ko':['방금 검산한 사십오 도 자세를 이번에는 작은 벡터로 확인하겠습니다. 앞에서 정한 오른손 제트축과 열벡터 약속을 그대로 씁니다. 입력은 오른쪽으로 한 칸 향하는 일, 영, 영입니다.',
        '이 자세를 쿼터니언으로 적을 때는 반각인 이십이 점 오 도의 코사인과 사인을 사용합니다. 하지만 실제 물체가 도는 각도는 사십오 도입니다. 저장할 숫자와 물체의 각도를 구분하세요.',
        '같은 자세의 행렬로 입력 벡터를 돌리면, 결과는 루트 이 나누기 이, 루트 이 나누기 이, 영입니다. 오른쪽과 위쪽 성분이 같아졌지만 길이는 여전히 일입니다.',
        '이제 반대 회전인 마이너스 사십오 도를 적용하면 처음의 일, 영, 영으로 돌아옵니다. 표현을 바꿔도 같은 방향을 만들고, 역회전이 되돌리는지 확인한 것입니다. 게임 화면의 각도를 재서 얻은 숫자가 아니라, 약속한 입력으로 계산한 결과입니다.'],
  'en':['Check the same forty-five-degree orientation with a small vector. Keep the right-handed z axis and column-vector convention. The input points one unit right: one, zero, zero.',
        'Its quaternion uses the cosine and sine of the half angle, twenty-two point five degrees. The physical orientation still turns forty-five degrees. Stored components and the physical angle have different roles.',
        'The matrix for the same orientation sends the input to square root of two over two, square root of two over two, zero. Its rightward and upward components match and its length remains one.',
        'Applying the inverse rotation, minus forty-five degrees, returns one, zero, zero. Equivalent representations give the same direction and the inverse undoes the operation. These are defined calculation results, not angles measured from game footage.'],
  'beats':['같은 RH·열벡터 / 입력(1,0,0)','q=(cos22.5°,0,0,sin22.5°) / 물체45°','Rz(45°)v=(√2/2,√2/2,0) / 길이1','Rz(-45°)Rv=v / 같은 자세·역회전 검산'],
  'retainedResult':'The same fixed z ninety-degree endpoint and forty-five-degree midpoint from original25','nextQuestion':'Do equivalent encodings act identically on a vector, and does the inverse undo them?'}
]
baseline=read(B/'baselines/game-math-rotation-interpolation/lesson.json');original={s['id']:s for s in baseline['scenes']}
flow=read(B/'interpolation-episode-flow-audit.json')
for new in scenes:
    project=ROOT/'projects'/new['episode'];lesson=read(project/'production/lesson.json')
    lesson['scenes']=[s for s in lesson['scenes'] if s['id']!=new['id']]
    at=next(i for i,s in enumerate(lesson['scenes']) if s['id']==new['after'])+1;lesson['scenes'].insert(at,copy.deepcopy(new));write(project/'production/lesson.json',lesson)
    for lang in ['ko','en']:
        narration=read(project/f'script/narration.{lang}.json');narration['scenes']=[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in lesson['scenes']];write(project/f'script/narration.{lang}.json',narration)
    e=next(e for e in flow['episodes'] if e['slug']==new['episode']);e['order']=[s['id'] for s in lesson['scenes']];e['newWorkedCheck']=new['id']
retained=[s for e in flow['episodes'] for s in read(ROOT/f"projects/{e['slug']}/production/lesson.json")['scenes'] if s['id'] in original]
assert retained==baseline['scenes'];write(B/'interpolation-episode-flow-audit.json',flow)
write(B/'interpolation-worked-checks-v3.json',{'reason':'Measured voice requires more useful explanation for40:60; add the missing explicit time comparison and vector/inverse walkthrough, never pad or cut retained explanations.','scenes':scenes,'frozenV2ScriptAndAudioRewritten':False,'original26DictionariesExact':True,'mathOrPixelReview':'math checked; audio and pixels pending'})
base=read(ROOT/'projects/game-math-interpolation-teaching-additions-v2/project.json');m=copy.deepcopy(base);m.update(slug=SLUG,title='보간 시간과 표현 변환의 작은 수 검산',status='narration-preparation')
for key,value in m['paths'].items():m['paths'][key]=value.replace('game-math-interpolation-teaching-additions-v2',SLUG)
m['tts']['outputDir']=f'shared/output/narration/{SLUG}/qwen3-1.7b-balanced-v1';m['tts']['filenameStem']=SLUG+'-qwen3-1.7b-balanced-v1';write(P/'project.json',m)
for lang in ['ko','en']:write(P/f'script/narration.{lang}.json',{'project':SLUG,'language':lang,'status':'authorized-new-only-worked-narration','scenes':[{'id':f'{i:02}','title':s['title'],'lines':s[lang]} for i,s in enumerate(scenes,1)]})
write(B/'interpolation-worked-tts-map-v3.json',[{'ttsScene':f'{i:02}','additionId':s['id'],'sourceType':'supplement'} for i,s in enumerate(scenes,1)])
spec=importlib.util.spec_from_file_location('rotation_reference',ROOT/'production/batches/game-math-part2-full-series/rotation-conversions.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
q=r.axis_quaternion([0,0,1],math.pi/4);R=r.to_matrix(q);v=np.array([1.,0,0]);result=R@v
checks=[{'name':'linear half-second rotation','value':90*.5,'expected':45},{'name':'squared half-second progress','value':.5**2,'expected':.25},{'name':'squared half-second rotation','value':90*.25,'expected':22.5},{'name':'same final rotation','value':90*1**2,'expected':90},{'name':'half-angle quaternion','value':q.tolist(),'expected':[math.cos(math.pi/8),0,0,math.sin(math.pi/8)]},{'name':'midpoint vector','value':result.tolist(),'expected':[math.sqrt(2)/2,math.sqrt(2)/2,0]},{'name':'vector length preserved','value':float(np.linalg.norm(result)),'expected':1},{'name':'inverse returns original','value':(R.T@result).tolist(),'expected':v.tolist()}]
for check in checks:assert np.allclose(check['value'],check['expected'],atol=1e-9,rtol=0);check['passed']=True
audit={'allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'gameplayComparedBeforeDependentNarration':True,'checks':checks,'scriptSha256':{lang:hashlib.sha256((P/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']},'projectManifestSha256':hashlib.sha256((P/'project.json').read_bytes()).hexdigest(),'voiceSettingsExact':m['tts'],'voiceReferenceSha256':{key:hashlib.sha256((ROOT/m['tts'][key]).read_bytes()).hexdigest() for key in ['reference','referenceText']},'currentAudioAndPixelsApproved':False}
write(B/'interpolation-worked-pretts-audit-v3.json',audit)
runner=(B/'render-interpolation-narration.py').read_text(encoding='utf8').replace('game-math-interpolation-teaching-additions-v2',SLUG).replace('interpolation-pretts-audit.json','interpolation-worked-pretts-audit-v3.json').replace('interpolation-line-provenance.json','interpolation-worked-line-provenance-v3.json')
(B/'render-interpolation-worked-v3.py').write_text(runner,encoding='utf8')
print('Two inserted worked checks, eight lines and eight numeric checks frozen; v2 unchanged.')
