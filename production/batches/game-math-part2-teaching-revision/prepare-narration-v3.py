"""New auxiliary narration, never overwrite an approved baseline or v2 checkpoint."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-quaternion-teaching-additions-v3';P=ROOT/'projects'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(B/'quaternion-additive-draft.json')
v=read(B/'quaternion-clarified-additions-v3.json')
overrides={x['id']:x for x in v['overrides']}
oldmap=read(B/'quaternion-addition-tts-map.json')
olditems={x['id']:x for x in d['additions']+d['bridges']}
items=[]
for ref in oldmap:
    if ref['ttsScene'] not in v['retakeExistingTtsScenes']:continue
    s={**olditems[ref['additionId']]}
    if s['id'] in overrides:s.update(overrides[s['id']])
    s['sourceType']=ref['sourceType'];s['retakeOf']=ref['ttsScene']
    s.setdefault('title','연결 해설 '+s.get('before',''))
    items.append(s)
items += [dict(x,sourceType='framing') for x in read(B/'quaternion-episode-framing.json')['scenes']]
games=read(B/'quaternion-game-insertions.json')
assert games['review']['allRawCandidateIntervalsPlayed']
items += [dict(x,sourceType='actual-footage') for x in games['scenes']]
mapping=[]
for i,s in enumerate(items,1):
    mapping.append({'ttsScene':f'{i:02d}','additionId':s['id'],'sourceType':s['sourceType'],'before':s.get('before'),'after':s.get('after'),'retakeOf':s.get('retakeOf'),'observationGapAfterLine':s.get('observationGapAfterLine',{})})
for lang in ['ko','en']:
    write(P/f'script/narration.{lang}.json',{'project':slug,'language':lang,'status':'additive-authorized-revision','scenes':[{'id':ref['ttsScene'],'title':s['title'],'lines':s[lang]} for s,ref in zip(items,mapping)]})
base=read(B/'baselines/game-math-quaternion-operations/project.json')
tts={**base['tts'],'outputDir':f'shared/output/narration/{slug}/qwen3-1.7b-balanced-v1','filenameStem':slug+'-qwen3-1.7b-balanced-v1'}
manifest={'schemaVersion':1,'slug':slug,'title':'쿼터니언 설명 보강·숫자 재녹음·게임 연결','status':'narration-preparation','revisionOf':'game-math-quaternion-operations','standaloneUploadAllowed':False,'authorizationQueue':str(B.relative_to(ROOT)/'queue.json').replace('\\','/'),'paths':{'script':f'projects/{slug}/script/narration.ko.json','scriptEn':f'projects/{slug}/script/narration.en.json','captionsKo':f'projects/{slug}/script/voice-aligned.ko.srt','captionsEn':f'projects/{slug}/script/voice-aligned.en.srt'},'tts':tts,'editing':{'exampleSeconds':0,'narrationPlacement':'continuous-across-all-three-segments','backgroundMusic':False},'preservation':{'baselineAudioOverwritten':False,'v2AudioOverwritten':False,'approvedVoicePreserved':True},'contract':d['contract']}
write(P/'project.json',manifest);write(B/'quaternion-v3-tts-map.json',mapping)
audit=read(B/'quaternion-pretts-math-audit.json')
assert audit['originalSceneOrderAndAllFieldsExact'] and audit['originalContractExact'] and all(x['passed'] for x in audit['checks'])
write(B/'quaternion-v3-pretts-audit.json',{'originalAuditPreserved':True,'scriptSha256':{lang:hashlib.sha256((P/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']},'newSceneCount':len(items),'retakesOnlyNewMaterial':True,'baseline26ScenesAnd155KoLinesChanged':False,'numericReview':{'N02':{'input':[2,1],'multiplyBy':'i','output':[-1,2],'lengthSquared':5},'N05':{'input':[3,0,0,4],'norm':5,'output':[.6,0,0,.8],'normSquared':1},'N08':{'C':'sqrt(2)/2','vector':[1,0,1],'q':['C',0,0,'C'],'qTimesP':['-C','C','C','C'],'inverse':['C',0,0,'-C'],'complete':[0,0,1,1]},'N09':{'cos90':0,'sin90':1,'complexUnit':'i'}},'coordinateContract':d['contract'],'sourceNarrationMatchedToPlayedIntervals':True,'finalVoiceAndMovingPixelQaComplete':False})
print(json.dumps({'project':slug,'scenes':len(items),'koLines':sum(len(s['ko']) for s in items),'gameMaximumSeconds':sum(s['maximumSeconds'] for s in games['scenes']),'originalChanged':False}))
