"""Create an auxiliary TTS project; preserve all baseline audio and scripts."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-quaternion-teaching-additions-v2';P=ROOT/'projects'/slug
d=json.loads((B/'quaternion-additive-draft.json').read_text(encoding='utf8'))
m=json.loads((B/'baselines/game-math-quaternion-operations/project.json').read_text(encoding='utf8'))
def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
items=[dict(x,sourceType='supplement') for x in d['additions']]+[dict(x,title='연결 해설 '+x['before'],sourceType='bridge') for x in d['bridges']]
mapping=[]
for i,s in enumerate(items,1):mapping.append({'ttsScene':f'{i:02d}','additionId':s['id'],'sourceType':s['sourceType'],'before':s.get('before'),'after':s.get('after')})
for language in ['ko','en']:
 write(P/f'script/narration.{language}.json',{'project':slug,'language':language,'status':'additive-narration-for-authorized-revision','scenes':[{'id':r['ttsScene'],'title':s['title'],'lines':s[language]} for s,r in zip(items,mapping)]})
tts={**m['tts'],'outputDir':f'shared/output/narration/{slug}/qwen3-1.7b-balanced-v1','filenameStem':slug+'-qwen3-1.7b-balanced-v1'}
manifest={'schemaVersion':1,'slug':slug,'title':'쿼터니언 수정용 기초 설명과 연결 내레이션','status':'narration-preparation','revisionOf':'game-math-quaternion-operations','standaloneUploadAllowed':False,'authorizationQueue':'production/batches/game-math-part2-teaching-revision/queue.json','paths':{'script':f'projects/{slug}/script/narration.ko.json','scriptEn':f'projects/{slug}/script/narration.en.json'},'tts':tts,'editing':{'exampleSeconds':0,'narrationPlacement':'continuous-across-all-three-segments','backgroundMusic':False},'preservation':{'baselineAudioOverwritten':False,'originalScenes':len(d['scenes']),'existingVoiceReferencePreserved':True},'contract':d['contract']}
write(P/'project.json',manifest);write(B/'quaternion-addition-tts-map.json',mapping)
print(json.dumps({'project':slug,'newTtsScenes':len(items),'newKoLines':sum(len(s['ko']) for s in items),'existingNarrationChanged':False}))
