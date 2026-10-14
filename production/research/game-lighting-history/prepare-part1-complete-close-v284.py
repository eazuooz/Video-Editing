"""Repair the evidenced terminal decay without changing the teaching distinction."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,psutil
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(R).as_posix()
e=read(P/'part1-clear-onset-take-asr-execution-v283.json');assert e['status']=='complete' and e['exitCode']==0 and len(e['results'])==2
w=e['worker'];assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
records=[]
for r in e['results']:
 j=read(R/r['path']);assert sha(R/r['path'])==r['sha256']
 records.append({**r,'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,'onsetResolvedInCompleteContext':r['label']=='complete-neighbour-context',
 'observation':'Full raw text/14 word intervals through6.82s and complete three-paragraph context/62 intervals through28.66s directly read. Raw 무늬보건과 is resolved by complete context 무늬5.64–6.00 and 복원과6.00–6.44. Both complete target sentences and neighbour paragraphs remain, no invented ending/repeat. The actual52.17ms terminal decay still fails the established70ms/quiet-close gate; keep unselected and repair only this guide.'})
proof={'reviewedAt':datetime.now(timezone.utc).isoformat(),'records':records,'allFullTextsAndTimestampsDirectlyCompared':True,'firstWordResolvedByCompleteContext':True,'originalTailGatePassed':False,'selected':False,'humanWholeListening':'pending','humanPronunciation':'pending'}
dp=P/'part1-clear-onset-take-direct-review-v284.json';assert not dp.exists();dp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
ko='복원 품질과 표시 빈도는 다릅니다. 아우터 월드에서는 프레임 생성 배수 표시를 확인합니다.'
en='Reconstruction quality and display frequency are different. In The Outer Worlds, we inspect the frame-generation multiplier.'
out='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part1-complete-close-v284';stem='game-lighting-history-04-part1-complete-close-v284';scripts={}
for lang,text in [('ko',ko),('en',en)]:
 p=R/f'projects/game-lighting-history-04/script/physical-part1-complete-close.{lang}.v284.json';assert not p.exists();p.write_text(json.dumps({'title':'Reconstruction quality versus display frequency','scenes':[{'id':'outer-comparison-before','title':'outer-comparison-before','lines':[text],'screenRole':'explanation'}]},ensure_ascii=False,indent=2)+'\n','utf-8');scripts[lang]=rel(p)
base=read(P/'part1-clear-onset-tts-manifest-v282.json');base['paths'].update(script=scripts['ko'],scriptEn=scripts['en'],narration=f'{out}/{stem}.wav',captionsKo=f'{out}/{stem}.srt',captionsEn=f'{out}/{stem}.en.srt');base['tts'].update(outputDir=out,filenameStem=stem,maxNewTokensReason='One terminal-decay repair, retaining reconstruction/display-frequency teaching and multiplier UI. No original111 regeneration.')
mp=P/'part1-complete-close-tts-manifest-v284.json';assert not mp.exists();mp.write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n','utf-8')
request=read(P/'part1-clear-onset-tts-request-v282.json');request.update(preparedAt=datetime.now(timezone.utc).isoformat(),manifestOverride=rel(mp),reason='Full-context first word resolved but actual terminal decay failed. Use a clear declarative ending and retain the exact conceptual distinction/source multiplier. Previous guides stay immutable and unselected.',revisedKorean=ko,revisedEnglish=en,englishMeaningUnchanged=False,meaningPreserved=True,scenes=[{'id':'outer-comparison-before','path':f'{out}/chunks/outer-comparison-before-scene.wav'}])
request['protectedInputs'] += [{'path':rel(p),'sha256':sha(p)} for p in [dp,mp,R/scripts['ko'],R/scripts['en'],R/e['newTake']['path']]]
rp=P/'part1-complete-close-tts-request-v284.json';assert not rp.exists();rp.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf-8')
code=(R/'production/research/game-lighting-history/render-part1-clear-onset-v282.py').read_text('utf-8-sig').replace('part1-clear-onset-tts-request-v282','part1-complete-close-tts-request-v284').replace('part1-clear-onset-tts-execution-v282','part1-complete-close-tts-execution-v284').replace('episode04Part1ClearOnsetTtsV282','episode04Part1CompleteCloseTtsV284').replace('.tts282.tmp','.tts284.tmp')
p=R/'production/research/game-lighting-history/render-part1-complete-close-v284.py';assert not p.exists();p.write_text(code,'utf-8')
print(json.dumps({'prepared':True,'previousTakeSelected':False,'tailGateUnchanged':True,'originalNarrationRegenerated':0}))
