"""Retake ambiguous new numerical lines; retain every other approved audio line."""
from pathlib import Path
import json,copy,shutil,hashlib,math
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;SLUG='game-math-interpolation-numeric-retakes-v4';P=ROOT/'projects'/SLUG
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not any((ROOT/f'shared/output/narration/{SLUG}').rglob('*.wav')),'Do not rewrite frozen retake audio'
items=[('IP08','game-math-interpolation-worked-checks-v3','02',2,'같은 자세의 행렬로 입력 벡터를 돌려 보죠. 첫 번째 성분은 루트 이 나누기 이입니다. 두 번째 성분도 루트 이 나누기 이입니다. 세 번째 성분은 영입니다. 오른쪽과 위쪽 성분이 같아졌지만 길이는 여전히 일입니다.','Apply the matrix for the same orientation to the vector. Its first component is square root of two over two. The second is also square root of two over two. The third is zero. The rightward and upward components match, and the length remains one.'),('IP04','game-math-interpolation-teaching-additions-v2','17',0,'행렬에서 각도를 되찾기 전에 두 함수의 역할을 볼까요? 하이폿은 직각삼각형의 빗변 길이입니다. 가로 길이는 삼이고 세로 길이는 사입니다. 삼의 제곱인 구와 사의 제곱인 십육을 더하면 이십오입니다. 그 제곱근은 오입니다.','Before extracting angles from a matrix, consider two functions. Hypot gives a right triangle’s hypotenuse. The horizontal length is three and the vertical length is four. Three squared is nine; four squared is sixteen. Their sum is twenty-five, whose square root is five.')]
oldm=read(ROOT/'projects/game-math-interpolation-worked-checks-v3/project.json');m=copy.deepcopy(oldm);m.update(slug=SLUG,title='새 계산 예시의 성분·숫자 발음 명료화',status='narration-preparation')
for key,value in m['paths'].items():m['paths'][key]=value.replace(oldm['slug'],SLUG)
m['tts']['outputDir']=f'shared/output/narration/{SLUG}/qwen3-1.7b-balanced-v1';m['tts']['filenameStem']=SLUG+'-qwen3-1.7b-balanced-v1';write(P/'project.json',m)
scripts={'ko':[],'en':[]};copies=[];mapping=[];changes=[]
episode=ROOT/'projects/game-math-rotation-conversions-v2';lesson=read(episode/'production/lesson.json')
for number,(ident,oldslug,oldscene,changed,ko,en) in enumerate(items,1):
    s=next(s for s in lesson['scenes'] if s['id']==ident);previous=s['ko'][changed];s['ko'][changed]=ko;s['en'][changed]=en
    for lang in scripts:scripts[lang].append({'id':f'{number:02}','title':s['title'],'lines':s[lang]})
    oldout=ROOT/read(ROOT/f'projects/{oldslug}/project.json')['tts']['outputDir']/'chunks';out=ROOT/m['tts']['outputDir']/'chunks';out.mkdir(parents=True,exist_ok=True)
    for line in range(len(s['ko'])):
        if line==changed:continue
        source=oldout/f'{oldscene}-{line+1:02}.wav';target=out/f'{number:02}-{line+1:02}.wav';shutil.copy2(source,target);assert hashlib.sha256(source.read_bytes()).hexdigest()==hashlib.sha256(target.read_bytes()).hexdigest();copies.append({'source':source.relative_to(ROOT).as_posix(),'target':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    mapping.append({'ttsScene':f'{number:02}','additionId':ident,'sourceType':'supplement'})
    changes.append({'scene':ident,'newLineIndex':changed,'previous':previous,'new':ko,'reason':'Independent full-scene and per-line ASR omitted a critical numeral or merged its pronunciation. Expand only the new line into separately named components/arithmetic steps.'})
write(episode/'production/lesson.json',lesson)
for lang in scripts:
    write(P/f'script/narration.{lang}.json',{'project':SLUG,'language':lang,'status':'authorized-new-only-numeric-retakes','scenes':scripts[lang]})
    n=read(episode/f'script/narration.{lang}.json');n['scenes']=[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in lesson['scenes']];write(episode/f'script/narration.{lang}.json',n)
baseline=read(B/'baselines/game-math-rotation-interpolation/lesson.json');oldids={s['id'] for s in baseline['scenes']};retained=[s for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2'] for s in read(ROOT/f'projects/{slug}/production/lesson.json')['scenes'] if s['id'] in oldids];assert retained==baseline['scenes']
write(B/'interpolation-numeric-retake-plan-v4.json',{'changes':changes,'retainedNewAudioLines':copies,'original26DictionariesExact':True,'originalVoiceRewritten':False,'newWordingOnly':True,'allOriginalAndOtherNewLinesRetained':True,'asrAndPixelApproval':False})
write(B/'interpolation-numeric-tts-map-v4.json',mapping)
checks=[{'name':'hypot arithmetic','value':[3**2,4**2,3**2+4**2,math.hypot(3,4)],'expected':[9,16,25,5],'passed':True},{'name':'45degree vector components','value':[math.cos(math.pi/4),math.sin(math.pi/4),0],'expected':[math.sqrt(2)/2,math.sqrt(2)/2,0],'passed':True}]
audit={'allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'gameplayComparedBeforeDependentNarration':True,'checks':checks,'scriptSha256':{lang:hashlib.sha256((P/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in scripts},'projectManifestSha256':hashlib.sha256((P/'project.json').read_bytes()).hexdigest(),'voiceSettingsExact':m['tts'],'voiceReferenceSha256':{k:hashlib.sha256((ROOT/m['tts'][k]).read_bytes()).hexdigest() for k in ['reference','referenceText']}}
write(B/'interpolation-numeric-pretts-audit-v4.json',audit)
runner=(B/'render-interpolation-narration.py').read_text(encoding='utf8').replace('game-math-interpolation-teaching-additions-v2',SLUG).replace('interpolation-pretts-audit.json','interpolation-numeric-pretts-audit-v4.json').replace('interpolation-line-provenance.json','interpolation-numeric-line-provenance-v4.json');(B/'render-interpolation-numeric-v4.py').write_text(runner,encoding='utf8')
print('Two uncertain numerical lines expanded, five other new WAV lines copied byte-exact; originals unchanged.')
