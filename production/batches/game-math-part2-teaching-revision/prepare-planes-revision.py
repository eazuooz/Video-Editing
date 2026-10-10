"""Freeze only new teaching/audio after compared footage, preserving22 originals."""
from pathlib import Path
import json,copy,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;BASE='game-math-planes-barycentric';AUX='game-math-planes-teaching-additions-v2'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not any((ROOT/f'shared/output/narration/{AUX}').rglob('*.wav')),'Freeze after voice exists'
flow=read(B/'planes-flow-draft.json');flow['omitUnrecorded']=[];flow['omitReason']='No original or selected addition omitted';source=read(B/'planes-game-insertions.json')
assert source['review']['allSelectedNativePlaybackCompared'] and source['review']['denseActionPixelsCompared']
assert not any(r['existingLesson']==BASE for r in source['review']['overlaps']),'Never repeat the retained chapter footage as new quota'
base=B/'baselines'/BASE;old=read(base/'lesson.json');original={s['id']:s for s in old['scenes']}
extra={s['id']:copy.deepcopy(s) for s in flow['additions'] if s['id'] not in flow['omitUnrecorded']};extra.update({s['id']:copy.deepcopy(s) for s in source['scenes']})
audits=[];items=[]
for number,(e,order) in enumerate(zip(flow['episodes'],flow['orders']),1):
 slug=e['slug'];P=ROOT/'projects'/slug;scenes=[copy.deepcopy(original[i] if i in original else extra[i]) for i in order]
 lesson={**copy.deepcopy(old),'slug':slug,'title':e['titleKo'],'scenes':scenes,'revisionOf':BASE,'episode':number,'causalSpine':flow['causalSpine'],'viewerQuestion':e['question'],'baselineOriginalScenesUnchanged':True,'baselineSource':base.relative_to(ROOT).as_posix()};write(P/'production/lesson.json',lesson)
 titles={'ko':e['titleKo'],'en':e['titleEn']}
 for lang in ['ko','en']:write(P/f'script/narration.{lang}.json',{'title':titles[lang],'scenes':[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in scenes]})
 m=json.loads(json.dumps(read(base/'project.json'),ensure_ascii=False).replace(BASE,slug));m.update(slug=slug,titles=titles,status='additive-revision-preparing',publishReady=False,revisionOf=BASE)
 m['video']['durationSeconds']=0;m['finalRender']={'status':'not-rendered','currentPixelApproval':False};m['publishing']={'defaults':'shared/publishing/youtube-defaults.json','privateUploadComplete':False,'fullPublishingSettingsComplete':False,'baselineVideoId':'wsxSYEEj8aQ','baselinePreserved':True,'scheduleStatus':'plan only; save reviewed actual episode after private/Git completion','coachingEndingLinkRequired':True,'pinnedCoachingCommentRequired':True}
 m['approvals']={'script':'all22 original dictionaries/order preserved; new prerequisites/math pre-TTS checked; final voice/flow pending','voice':'same approved reference; whole listening pending','rights':'recording permissions/Valve video policy retained; game-IP/human review pending','pixels':'pending'}
 m['editing'].update(timingStatus='awaiting current-hash new audio and exact frame planning',backgroundMusic=False)
 for key in ['actualGameplaySeconds','actualExplanationSeconds','actualGameplayShare','actualCommercialGameplaySeconds','actualDevelopmentFootageSeconds','actualPrototypeExplanationSeconds']:m['editing'][key]=None
 m['editing']['causalFlow']={'required':True,'chain':'previous visible/calculated result → unresolved question → why next operation → resulting state','plan':(B/'planes-episode-flow-audit.json').relative_to(ROOT).as_posix(),'continuousReview':'pending'}
 m['editing']['openingOverview']={'required':True,'scene':'PF01' if number==1 else 'PF03','reviewedBeforeTts':True,'question':e['question'],'languages':['ko','en'],'classification':'explanation'}
 m['editing']['exampleInterleaving']['reviewStatus']='native/dense candidate comparisons complete; tracked final moving footage pending'
 m['tts']['renderMode']='preserved-baseline-plus-new-only-additions';m['audio']['mixStatus']='not-rendered';m['membershipOutro']['appliedToFinal']=False
 m['paths']['productionData']=f'projects/{slug}/production/lesson.json';m['paths']['manimProject']='manim/projects/game-math-part2-teaching-revision/planes_additions.py';m['paths']['productionBuilder']='production/batches/game-math-part2-teaching-revision/build-planes-episodes.py'
 m['preservation']={'baseline':BASE,'originalIds':[i for i in order if i in original],'originalAudioMethod':'exact baseline PCM samples and unchanged encoded explanation clips','baselineMediaChanged':False,'introAndMemberOutro':'reuse original2-second intro and10-second member profiles/name/badges','palette':'preserved existing research-paper-white-v1; already-started exception'}
 m['lecture'].update(episode=number,viewerQuestion=e['question']);write(P/'project.json',m)
 retained=[s for s in scenes if s['id'] in original];assert all(s==original[s['id']] for s in retained)
 audits.append({'slug':slug,'episode':number,'order':order,'originalIds':[s['id'] for s in retained],'originalScenesExact':True,'originalKoLines':sum(len(s['ko']) for s in retained),'newActualCapacitySeconds':sum(s.get('maximumSeconds',0) for s in scenes),'mediaQaComplete':False})
 items.extend(s for s in scenes if s['id'] in extra)
assert [i for e in audits for i in e['originalIds']]==list(original)
assert len({s['id'] for s in items})==len(items)
write(B/'planes-episode-flow-audit.json',{'episodes':audits,'allOriginalSceneDictionariesExact':True,'originalScenes':22,'originalKoLines':sum(len(s['ko']) for s in old['scenes']),'originalEnLines':sum(len(s['en']) for s in old['scenes']),'originalOrderAndContractExact':True,'completeBoundary':flow['completeBoundary'],'omittedUnrecordedRepetition':flow['omitUnrecorded'],'omitReason':flow['omitReason'],'finalContinuousReview':False})
mapping=[{'ttsScene':f'{i:02d}','additionId':s['id'],'sourceType':'actual-footage' if s['kind']=='actual' else 'framing' if s['id'].startswith('PF') else 'bridge' if s['id'].startswith('LC') else 'supplement'} for i,s in enumerate(items,1)]
oldm=read(base/'project.json');tts={**oldm['tts'],'outputDir':f'shared/output/narration/{AUX}/qwen3-1.7b-balanced-v1','filenameStem':AUX+'-qwen3-1.7b-balanced-v1','renderMode':'line'}
manifest={'schemaVersion':1,'slug':AUX,'title':'평면과 삼각형: 새 기초 설명과 유기적 연결','status':'narration-preparation','revisionOf':BASE,'standaloneUploadAllowed':False,'authorizationQueue':(B/'queue.json').relative_to(ROOT).as_posix(),'paths':{'script':f'projects/{AUX}/script/narration.ko.json','scriptEn':f'projects/{AUX}/script/narration.en.json','captionsKo':f'projects/{AUX}/script/voice-aligned.ko.srt','captionsEn':f'projects/{AUX}/script/voice-aligned.en.srt'},'tts':tts,'editing':{'exampleSeconds':0,'narrationPlacement':'continuous-across-all-three-segments','backgroundMusic':False},'preservation':{'baselineAudioOverwritten':False,'originalScenes':22,'existingVoiceReferencePreserved':True},'contract':old['contract']};write(ROOT/'projects'/AUX/'project.json',manifest)
for lang in ['ko','en']:write(ROOT/'projects'/AUX/f'script/narration.{lang}.json',{'project':AUX,'language':lang,'status':'authorized-new-only-additive-narration','scenes':[{'id':r['ttsScene'],'title':s['title'],'lines':s[lang]} for r,s in zip(mapping,items)]})
write(B/'planes-addition-tts-map.json',mapping)
import runpy
runpy.run_path(str(B/'audit-planes-worked-examples.py'))
math_record=read(B/'planes-worked-example-review.json');checks=math_record['checks'];assert len(checks)==21 and all(c['passed'] for c in checks)
voice={k:v for k,v in tts.items() if k in ['engine','language','reference','referenceText','model','tailRatioThreshold','tailDecayMsThreshold','maxRenderAttempts','maxNewTokens','edgeFadeSeconds']}
audit={'status':'pre-TTS preservation and numeric audit; measured audio/pixels pending','allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'gameplayComparedBeforeDependentNarration':True,'newOnlyScenes':len(items),'newKoLines':sum(len(s['ko']) for s in items),'checks':checks,'scriptSha256':{lang:sha(ROOT/'projects'/AUX/f'script/narration.{lang}.json') for lang in ['ko','en']},'voiceSettingsExact':voice,'voiceReferenceSha256':{key:sha(ROOT/tts[key]) for key in ['reference','referenceText']},'projectManifestSha256':sha(ROOT/'projects'/AUX/'project.json'),'coordinateContract':old['contract'],'engineInternalsAsserted':False,'humanListening':'pending'};write(B/'planes-pretts-audit.json',audit)
q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']==BASE);item['status']='additive-preparation';item['revision'].update(episodeSlugs=[e['slug'] for e in flow['episodes']],originalPreservationAuditPassed=True,footageComparisonPassed=True,episodePlanReviewed=True,flowReviewPassed=False,narrationComplete=False,renderComplete=False);q['execution']['currentSlug']=BASE;q['execution']['stage']='Lines/bounds second private upload active; plane/triangle compared gameplay and preserved scripts/math ready, current research boundary required before new TTS';write(B/'queue.json',q)
print(json.dumps({'originalScenes':22,'newTtsScenes':len(items),'newKoLines':audit['newKoLines'],'mathChecks':len(checks),'actualCapacities':[a['newActualCapacitySeconds'] for a in audits],'mediaComplete':False},ensure_ascii=False))
