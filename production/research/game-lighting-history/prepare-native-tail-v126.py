"""Prepare one unchanged-text retake; preserve the four passed takes and all history."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p: json.loads(p.read_text('utf-8-sig'))
def write(p,v):
    if p.exists(): raise RuntimeError('Preserve existing '+str(p))
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def binding(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
request=read(BASE/'native-followup-request-v120.json')
original=ROOT/request['script']['path']
pair=next(x for x in read(original)['scenes'] if x['id']=='focus-layers-entry')
script=ROOT/'projects/game-lighting-history-04/script/native-tail.koen.v126.json'
write(script,dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),unchangedText=True,source=binding(original),scenes=[pair]))
paths={}
for lang in ['ko','en']:
    old=read(ROOT/f'projects/game-lighting-history-04/script/native-followup.{lang}.v120.json')
    old['scenes']=[x for x in old['scenes'] if x['id']==pair['id']]
    target=ROOT/f'projects/game-lighting-history-04/script/native-tail.{lang}.v126.json'
    write(target,old);paths[lang]=target.relative_to(ROOT).as_posix()
manifest=copy.deepcopy(read(BASE/'native-followup-manifest-v120.json'))
manifest['status']='prepared-one-unchanged-text-tail-retake'
manifest['tts']['outputDir']='shared/output/narration/game-lighting-history-04/qwen3-1.7b-native-tail-v126'
manifest['tts']['filenameStem']='game-lighting-history-04-native-tail-v126'
manifest['tts']['maxNewTokensReason']='Only focus-layers-entry unchanged-text retake; preserve all passed takes and thresholds.'
manifest['paths']['script']=paths['ko'];manifest['paths']['scriptEn']=paths['en']
stem=manifest['tts']['outputDir']+'/'+manifest['tts']['filenameStem']
for key,suffix in [('narration','.wav'),('captionsKo','.srt'),('captionsEn','.en.srt')]:manifest['paths'][key]=stem+suffix
mp=BASE/'native-tail-manifest-v126.json';write(mp,manifest)
result=read(BASE/'native-followup-execution-v121.json')
if result.get('status')!='failed-preserve-existing-and-new-takes':raise RuntimeError('Expected preserved partial failure')
if [x['id'] for x in result['results'] if not x['technicalTailGatePassed']]!=['focus-layers-entry']:raise RuntimeError('One-retake scope changed')
history=ROOT/'shared/output/gpu-handoff/6c198aa7-1c8a-4a98-a259-f19af5d9393b.json'
if read(history)['state']!='research_resume_verified':raise RuntimeError('Research restoration not verified')
request['preparedAt']=datetime.now(timezone.utc).isoformat()
request['script']=binding(script);request['manifestOverride']=mp.relative_to(ROOT).as_posix()
request['protectedInputs'] += [binding(mp),binding(ROOT/paths['ko']),binding(ROOT/paths['en']),binding(BASE/'native-followup-execution-v121.json'),binding(history)]
request['existingSelectedTakeFiles'] += [dict(path=x['path'],sha256=x['sha256']) for x in result['results']]
request['scenes']=[dict(id=pair['id'],path=manifest['tts']['outputDir']+'/chunks/focus-layers-entry-scene.wav',kind='same-text-technical-tail-retake')]
request.update(previousPartialExecution=binding(BASE/'native-followup-execution-v121.json'),passedTakeCountPreserved=4,thresholdChanged=False)
write(BASE/'native-tail-request-v126.json',request)
worker=(ROOT/'production/research/game-lighting-history/render-native-followup-v121.py').read_text('utf-8')
worker=worker.replace('native-followup-request-v120.json','native-tail-request-v126.json').replace('native-followup-execution-v121.json','native-tail-execution-v126.json')
worker=worker.replace("expected={'focus-scale-edit','focus-layers-entry','debugger-command-submit','focus-to-frame-inspection','resource-name-limits'}","expected={'focus-layers-entry'}")
worker=worker.replace("len(request['scenes'])!=5","len(request['scenes'])!=1").replace('Five-scene scope changed','One-scene scope changed')
worker=worker.replace('native-followup-five-scenes-running','native-tail-one-scene-running').replace('five-scenes-generated-awaiting-ASR-and-research-restoration','one-scene-generated-awaiting-ASR-and-research-restoration')
target=ROOT/'production/research/game-lighting-history/render-native-tail-v126.py'
if target.exists():raise RuntimeError('Preserve existing worker')
compile(worker,str(target),'exec');target.write_text(worker,'utf-8')
print(json.dumps(dict(prepared=True,scene=pair['id'],passedPreserved=4,previousSelectedPreserved=43,thresholdChanged=False),ensure_ascii=False))
