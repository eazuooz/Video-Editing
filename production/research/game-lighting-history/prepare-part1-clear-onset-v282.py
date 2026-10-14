"""Retain the meaning of a newly authored guide while clarifying its onset."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
R=Path(__file__).resolve().parents[3]; P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
e=read(P/'part1-onset-take-asr-execution-v281.json')
assert e['status']=='complete' and e['exitCode']==0 and len(e['results'])==2
w=e['worker'];assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
records=[]
for r in e['results']:
 p=R/r['path'];assert sha(p)==r['sha256'];j=read(p)
 assert len(j['words'])==(15 if r['label']=='raw-new-guide' else 61)
 records.append({**r,'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
 'contentApproved':False,'observation':'The entire raw guide and all three complete neighbouring paragraphs were read. Raw starts 다수의0.00–0.14; complete context starts 수의5.64–5.84. The first word remains unresolved. Later sentences and endings are complete without invented greetings or repeats. Preserve this take as historical, unselected evidence.'})
proof={'reviewedAt':datetime.now(timezone.utc).isoformat(),'execution':rel(P/'part1-onset-take-asr-execution-v281.json'),'records':records,'allFullTextsAndTimestampsDirectlyCompared':True,'selected':False,'firstSyllableResolved':False,'humanWholeListening':'pending','humanPronunciation':'pending','next':'Clarify only the new guide wording while preserving its reconstruction-versus-display-frequency distinction.'}
dest=P/'part1-onset-take-direct-review-v282.json';assert not dest.exists();dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
base=read(P/'part1-onset-repair-tts-manifest-v280.json')
old=next(p for p in read(P/'part1-final-input-plan-v240.json')['paragraphs'] if p['id']=='outer-comparison-before')
ko='무늬 복원과 화면을 더 자주 표시하는 일은 다릅니다. 아우터 월드에서는 프레임 생성 배수 표시를 읽어 보죠.'
en=old['en']
out='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part1-clear-onset-v282';stem='game-lighting-history-04-part1-clear-onset-v282'
scripts={}
for lang,text in [('ko',ko),('en',en)]:
 p=R/f'projects/game-lighting-history-04/script/physical-part1-clear-onset.{lang}.v282.json';assert not p.exists()
 p.write_text(json.dumps({'title':'Embroidery detail reconstruction versus display frequency','scenes':[{'id':old['id'],'title':old['id'],'lines':[text],'screenRole':'explanation'}]},ensure_ascii=False,indent=2)+'\n','utf-8');scripts[lang]=rel(p)
base['paths'].update(script=scripts['ko'],scriptEn=scripts['en'],narration=f'{out}/{stem}.wav',captionsKo=f'{out}/{stem}.srt',captionsEn=f'{out}/{stem}.en.srt')
base['tts'].update(outputDir=out,filenameStem=stem,maxNewTokens=512,maxNewTokensReason='One new guide only; explicit first-word clarity. Preserve original111 and all other approved additions.')
mp=P/'part1-clear-onset-tts-manifest-v282.json';assert not mp.exists();mp.write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n','utf-8')
request=read(P/'part1-onset-repair-tts-request-v280.json')
request.update(preparedAt=datetime.now(timezone.utc).isoformat(),manifestOverride=rel(mp),reason='New guide onset remains unresolved in raw and full context; replace 자수의 with the clearer equivalent 무늬 while retaining both complete conceptual distinctions and the following demonstration. Original narration untouched.',sameKoreanAndEnglishTexts=False,meaningPreserved=True,previousKorean=old['ko'],revisedKorean=ko,englishMeaningUnchanged=True,retimingApproved=False,selected=False,
 scenes=[{'id':old['id'],'path':f'{out}/chunks/{old["id"]}-scene.wav'}])
request['protectedInputs'] += [{'path':rel(p),'sha256':sha(p)} for p in [dest,mp,R/scripts['ko'],R/scripts['en'],R/e['newTake']['path']]]
rp=P/'part1-clear-onset-tts-request-v282.json';assert not rp.exists();rp.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf-8')
code=(R/'production/research/game-lighting-history/render-part1-onset-repair-v280.py').read_text('utf-8-sig').replace('part1-onset-repair-tts-request-v280','part1-clear-onset-tts-request-v282').replace('part1-onset-repair-tts-execution-v280','part1-clear-onset-tts-execution-v282').replace('episode04Part1OnsetTtsV280','episode04Part1ClearOnsetTtsV282').replace('.tts280.tmp','.tts282.tmp')
p=R/'production/research/game-lighting-history/render-part1-clear-onset-v282.py';assert not p.exists();p.write_text(code,'utf-8')
print(json.dumps({'newGuide':old['id'],'meaningPreserved':True,'originalNarrationRegenerated':0,'selected':False}))
