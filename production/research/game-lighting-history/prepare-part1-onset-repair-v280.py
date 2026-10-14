"""Prepare one identical-text guide repair, preserving all generated media."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
R=Path(__file__).resolve().parents[3]
P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
proof=P/'part1-independent-recognition-direct-review-v279.json'
review=read(proof)
assert review['unresolvedLabels']==['artifact-context-outer-comparison-before'] and review['approvedContexts']==2
planPath=P/'part1-final-input-plan-v240.json';plan=read(planPath)
row=next(p for p in plan['paragraphs'] if p['id']=='outer-comparison-before')
assert row['kind']=='new-guided' and sha(R/row['pcm']['path'])==row['pcm']['sha256']
base=read(P/'part1-scoped-repair-tts-manifest-v176.json')
ko=R/'projects/game-lighting-history-04/script/physical-part1-onset-repair.ko.v280.json'
en=R/'projects/game-lighting-history-04/script/physical-part1-onset-repair.en.v280.json'
out='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part1-onset-repair-v280'
stem='game-lighting-history-04-part1-onset-repair-v280'
for path,text in [(ko,row['ko']),(en,row['en'])]:
 assert not path.exists()
 path.write_text(json.dumps({'title':'Existing guide onset clarity repair','scenes':[{'id':row['id'],'title':row['id'],'lines':[text],'screenRole':'explanation'}]},ensure_ascii=False,indent=2)+'\n','utf-8')
base['paths'].update(script=rel(ko),scriptEn=rel(en),narration=f'{out}/{stem}.wav',captionsKo=f'{out}/{stem}.srt',captionsEn=f'{out}/{stem}.en.srt')
base['tts'].update(outputDir=out,filenameStem=stem,maxNewTokens=512,maxNewTokensReason='Only the unresolved existing6.88s guide; original111 and all other additions remain immutable.')
mp=P/'part1-onset-repair-tts-manifest-v280.json';assert not mp.exists()
mp.write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n','utf-8')
protected=[planPath,proof,ko,en,mp,P/'part1-final-mix-settings-v242.json',P/'part1-final-visual-build-v250.json',P/'part1-caption-layout-v243.json',R/base['tts']['reference'],R/base['tts']['referenceText']]
protected.extend(R/p['pcm']['path'] for p in plan['paragraphs'] if p.get('pcm'))
settings=read(P/'part1-final-mix-settings-v242.json');protected.extend([R/settings['wav'],R/settings['aac']])
original=read(P/'part1-scoped-repair-tts-request-v176.json')
protected.extend(R/x['path'] for x in original['protectedInputs'] if (R/x['path']).exists())
protected=list(dict.fromkeys(protected))
request={'preparedAt':datetime.now(timezone.utc).isoformat(),'slug':'game-lighting-history-04','manifestOverride':rel(mp),
 'repairIds':[row['id']],'reason':'Both Turbo and independent full model leave the first 자 syllable unresolved; identical-text replacement is prepared only for this new guide. No original source narration regenerated.',
 'protectedInputs':[{'path':rel(p),'sha256':sha(p)} for p in protected],
 'previousPcm':row['pcm'],'existingSlotFrames':row['endFrame']-row['startFrame'],
 'sameKoreanAndEnglishTexts':True,'retimingApproved':False,'selected':False,
 'scenes':[{'id':row['id'],'path':f'{out}/chunks/{row["id"]}-scene.wav'}],
 'cpuThreads':2,'gpuJobs':1,'batchSize':1,'researchRestoreRequired':True,'allAsrApproved':False}
rp=P/'part1-onset-repair-tts-request-v280.json';assert not rp.exists()
rp.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf-8')
code=(R/'production/research/game-lighting-history/render-part1-scoped-repair-v176.py').read_text('utf-8-sig')
code=code.replace('part1-scoped-repair-tts-request-v176','part1-onset-repair-tts-request-v280').replace('part1-scoped-repair-tts-execution-v176','part1-onset-repair-tts-execution-v280').replace('1<=len(request[\'scenes\'])<=37','len(request[\'scenes\'])==1').replace('episode04Part1ScopedTtsV176','episode04Part1OnsetTtsV280').replace('.tts176.tmp','.tts280.tmp')
dest=R/'production/research/game-lighting-history/render-part1-onset-repair-v280.py';assert not dest.exists()
dest.write_text(code,'utf-8')
print(json.dumps({'preparedGuide':row['id'],'protectedFiles':len(protected),'identicalText':True,'newTts':0}))
