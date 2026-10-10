"""Freeze concise played-footage narration and two new-material tail retakes."""
from pathlib import Path
import json,copy,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-quaternion-teaching-additions-v4';P=ROOT/'projects'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
base=read(ROOT/'projects/game-math-quaternion-teaching-additions-v3/project.json')
assert not (ROOT/f'shared/output/narration/{slug}').exists(),'Frozen audio exists; create a separate retake instead'
old_scripts={lang:read(ROOT/f'projects/game-math-quaternion-teaching-additions-v3/script/narration.{lang}.json')['scenes'] for lang in ['ko','en']}
old_map={s['additionId']:s for s in read(B/'quaternion-v3-tts-map.json')}
items=[]
for ident in ['B08','B23']:
 ref=old_map[ident];at=int(ref['ttsScene'])-1
 items.append({'id':ident,'title':old_scripts['ko'][at]['title'],'ko':old_scripts['ko'][at]['lines'],'en':old_scripts['en'][at]['lines'],'sourceType':'bridge','retakeOf':{'project':'game-math-quaternion-teaching-additions-v3','scene':ref['ttsScene']}})
game=read(B/'quaternion-game-insertions.json');overrides={s['id']:s for s in read(B/'quaternion-game-clarifications-v4.json')['scenes']}
pace=[]
for s in game['scenes']:
 s={**s,**overrides[s['id']],'sourceType':'actual-footage'}
 chars=sum(map(len,s['ko']));estimate=chars/5.4+.6
 assert estimate<=s['maximumSeconds']+.5,(s['id'],estimate,s['maximumSeconds'])
 assert len(s['ko'])==len(s['en'])
 pace.append({'id':s['id'],'characters':chars,'conservativeEstimateSeconds':estimate,'playedMaximumSeconds':s['maximumSeconds'],'finalMeasuredGateRequired':True})
 items.append(s)
mapping=[{'ttsScene':f'{i:02}','additionId':s['id'],'sourceType':s['sourceType'],'retakeOf':s.get('retakeOf'),'after':s.get('after'),'before':s.get('before')} for i,s in enumerate(items,1)]
for lang in ['ko','en']:write(P/f'script/narration.{lang}.json',{'project':slug,'language':lang,'status':'additions-only-authorized','scenes':[{'id':ref['ttsScene'],'title':s['title'],'lines':s[lang]} for s,ref in zip(items,mapping)]})
m=copy.deepcopy(base);m.update(slug=slug,title='쿼터니언 실제 동작에 맞춘 간결한 연결 해설',status='narration-preparation')
for key,path in m['paths'].items():m['paths'][key]=path.replace('game-math-quaternion-teaching-additions-v3',slug)
m['tts'].update(outputDir=f'shared/output/narration/{slug}/qwen3-1.7b-balanced-v1',filenameStem=slug+'-qwen3-1.7b-balanced-v1')
m['preservation'].update(v3AudioOverwritten=False,v3ScriptOverwritten=False)
write(P/'project.json',m);write(B/'quaternion-v4-tts-map.json',mapping)
audit=read(B/'quaternion-pretts-math-audit.json');assert audit['originalSceneOrderAndAllFieldsExact'] and audit['originalContractExact']
write(B/'quaternion-v4-pretts-audit.json',{'original26ScenesAnd155KoLinesExact':True,'newGameplayOnlyTightened':True,'scriptSha256':{lang:hashlib.sha256((P/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']},'jobs':len(items),'pacePreflight':pace,'sourceGroups':{'GA02':[0,1,3],'GA08':[0,1],'GB03':[0,3]},'finalMeasuredTimingAndPixelsPassed':False})
print(json.dumps({'jobs':len(items),'koLines':sum(len(s['ko']) for s in items),'originalNarrationChanged':False}))
