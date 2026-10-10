"""Freeze only new teaching/audio after compared footage, preserving22 originals."""
from pathlib import Path
import json,copy,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;BASE='game-math-lines-bounds';AUX='game-math-lines-bounds-teaching-additions-v2'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not any((ROOT/f'shared/output/narration/{AUX}').rglob('*.wav')),'Freeze after voice exists'
flow=read(B/'lines-bounds-flow-draft.json');source=read(B/'lines-game-insertions.json')
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
 m['video']['durationSeconds']=0;m['finalRender']={'status':'not-rendered','currentPixelApproval':False};m['publishing']={'defaults':'shared/publishing/youtube-defaults.json','privateUploadComplete':False,'fullPublishingSettingsComplete':False,'baselineVideoId':'avLKKfQBV_U','baselinePreserved':True,'scheduleStatus':'plan only; save reviewed actual episode after private/Git completion','coachingEndingLinkRequired':True,'pinnedCoachingCommentRequired':True}
 m['approvals']={'script':'all22 original dictionaries/order preserved; new prerequisites/math pre-TTS checked; final voice/flow pending','voice':'same approved reference; whole listening pending','rights':'recording permissions/Valve video policy retained; game-IP/human review pending','pixels':'pending'}
 m['editing'].update(timingStatus='awaiting current-hash new audio and exact frame planning',backgroundMusic=False)
 for key in ['actualGameplaySeconds','actualExplanationSeconds','actualGameplayShare','actualCommercialGameplaySeconds','actualDevelopmentFootageSeconds','actualPrototypeExplanationSeconds']:m['editing'][key]=None
 m['editing']['causalFlow']={'required':True,'chain':'previous visible/calculated result → unresolved question → why next operation → resulting state','plan':(B/'lines-episode-flow-audit.json').relative_to(ROOT).as_posix(),'continuousReview':'pending'}
 m['editing']['openingOverview']={'required':True,'scene':'LF01' if number==1 else 'LF03','reviewedBeforeTts':True,'question':e['question'],'languages':['ko','en'],'classification':'explanation'}
 m['editing']['exampleInterleaving']['reviewStatus']='native/dense candidate comparisons complete; tracked final moving footage pending'
 m['tts']['renderMode']='preserved-baseline-plus-new-only-additions';m['audio']['mixStatus']='not-rendered';m['membershipOutro']['appliedToFinal']=False
 m['paths']['productionData']=f'projects/{slug}/production/lesson.json';m['paths']['manimProject']='manim/projects/game-math-part2-teaching-revision/lines_additions.py';m['paths']['productionBuilder']='production/batches/game-math-part2-teaching-revision/build-lines-episodes.py'
 m['preservation']={'baseline':BASE,'originalIds':[i for i in order if i in original],'originalAudioMethod':'exact baseline PCM samples and unchanged encoded explanation clips','baselineMediaChanged':False,'introAndMemberOutro':'reuse original2-second intro and10-second member profiles/name/badges','palette':'preserved existing research-paper-white-v1; already-started exception'}
 m['lecture'].update(episode=number,viewerQuestion=e['question']);write(P/'project.json',m)
 retained=[s for s in scenes if s['id'] in original];assert all(s==original[s['id']] for s in retained)
 audits.append({'slug':slug,'episode':number,'order':order,'originalIds':[s['id'] for s in retained],'originalScenesExact':True,'originalKoLines':sum(len(s['ko']) for s in retained),'newActualCapacitySeconds':sum(s.get('maximumSeconds',0) for s in scenes),'mediaQaComplete':False})
 items.extend(s for s in scenes if s['id'] in extra)
assert [i for e in audits for i in e['originalIds']]==list(original)
assert len({s['id'] for s in items})==len(items)
write(B/'lines-episode-flow-audit.json',{'episodes':audits,'allOriginalSceneDictionariesExact':True,'originalScenes':22,'originalKoLines':sum(len(s['ko']) for s in old['scenes']),'originalEnLines':sum(len(s['en']) for s in old['scenes']),'originalOrderAndContractExact':True,'completeBoundary':flow['completeBoundary'],'omittedUnrecordedRepetition':flow['omitUnrecorded'],'omitReason':flow['omitReason'],'finalContinuousReview':False})
mapping=[{'ttsScene':f'{i:02d}','additionId':s['id'],'sourceType':'actual-footage' if s['kind']=='actual' else 'framing' if s['id'].startswith('LF') else 'bridge' if s['id'].startswith('LC') else 'supplement'} for i,s in enumerate(items,1)]
oldm=read(base/'project.json');tts={**oldm['tts'],'outputDir':f'shared/output/narration/{AUX}/qwen3-1.7b-balanced-v1','filenameStem':AUX+'-qwen3-1.7b-balanced-v1','renderMode':'line'}
manifest={'schemaVersion':1,'slug':AUX,'title':'직선과 경계: 새 기초 설명과 유기적 연결','status':'narration-preparation','revisionOf':BASE,'standaloneUploadAllowed':False,'authorizationQueue':(B/'queue.json').relative_to(ROOT).as_posix(),'paths':{'script':f'projects/{AUX}/script/narration.ko.json','scriptEn':f'projects/{AUX}/script/narration.en.json','captionsKo':f'projects/{AUX}/script/voice-aligned.ko.srt','captionsEn':f'projects/{AUX}/script/voice-aligned.en.srt'},'tts':tts,'editing':{'exampleSeconds':0,'narrationPlacement':'continuous-across-all-three-segments','backgroundMusic':False},'preservation':{'baselineAudioOverwritten':False,'originalScenes':22,'existingVoiceReferencePreserved':True},'contract':old['contract']};write(ROOT/'projects'/AUX/'project.json',manifest)
for lang in ['ko','en']:write(ROOT/'projects'/AUX/f'script/narration.{lang}.json',{'project':AUX,'language':lang,'status':'authorized-new-only-additive-narration','scenes':[{'id':r['ttsScene'],'title':s['title'],'lines':s[lang]} for r,s in zip(mapping,items)]})
write(B/'lines-addition-tts-map.json',mapping)
checks=[]
def check(name,value,expected,tol=1e-9):
 a=np.asarray(value);b=np.asarray(expected);assert np.allclose(a,b,atol=tol,rtol=0),name;checks.append({'name':name,'computed':a.tolist(),'expected':b.tolist(),'passed':True})
o=np.array([2.,1.]);delta=np.array([6.,3.]);check('endpoint',o+delta,[8,4]);check('midpoint fraction',o+.5*delta,[5,2.5]);check('unit direction norm',np.linalg.norm(delta/np.linalg.norm(delta)),1);check('midpoint distance',o+math.sqrt(45)/2*delta/np.linalg.norm(delta),[5,2.5])
check('circle expanded constant',2**2+3**2-1**2,12)
check('equal distances at bisector x1',[np.linalg.norm(np.array([1,4]))**2,np.linalg.norm(np.array([-1,4]))**2],[17,17])
check('sphere boundary squared',np.array([2,0,0])@np.array([2,0,0]),4);check('sphere outside squared',np.array([3,0,0])@np.array([3,0,0]),9)
check('1D minmax center/half',[min([2,4,7]),max([2,4,7]),(2+7)/2,(7-2)/2],[2,7,4.5,2.5]);check('interval overlap',[max(1,3),min(4,6)],[3,4]);assert max(1,3)>min(2,5)
points=np.array(original['15']['points'],dtype=float);minimum=points.min(0);maximum=points.max(0);center=(minimum+maximum)/2;extent=(maximum-minimum)/2
check('five point minima',minimum,[-5,-7,-5]);check('five point maxima',maximum,[7,11,8]);check('five point center',center,[1,2,1.5]);check('five point half',extent,[6,9,6.5])
R=np.array([[1,-1,0],[1,1,0],[0,0,math.sqrt(2)]])/math.sqrt(2)
rp=points@R.T;check('rotated point minima',rp.min(0),[-6/math.sqrt(2),-12/math.sqrt(2),-5]);check('rotated point maxima',rp.max(0),[3/math.sqrt(2),18/math.sqrt(2),8])
corners=np.array([[x,y,z] for x in [minimum[0],maximum[0]] for y in [minimum[1],maximum[1]] for z in [minimum[2],maximum[2]]]);rc=corners@R.T
check('affine box min matches corners',R@center-np.abs(R)@extent,rc.min(0));check('affine box max matches corners',R@center+np.abs(R)@extent,rc.max(0));assert np.all(rc.min(0)<=rp.min(0)+1e-9) and np.all(rc.max(0)>=rp.max(0)-1e-9)
check('negative interval transformed',[min(-2*np.array([3,7])+1),max(-2*np.array([3,7])+1),-2*5+1,abs(-2)*2],[-13,-5,-9,4]);check('new endpoint',[5-7,3+5],[-2,8]);check('slope and intercept',[-5/7,3-(-5/7)*5],[-5/7,46/7]);check('rotated example half',np.abs(R)@np.array([2,1,.5]),[3/math.sqrt(2),3/math.sqrt(2),.5])
voice={k:v for k,v in tts.items() if k in ['engine','language','reference','referenceText','model','tailRatioThreshold','tailDecayMsThreshold','maxRenderAttempts','maxNewTokens','edgeFadeSeconds']}
audit={'status':'pre-TTS preservation and numeric audit; measured audio/pixels pending','allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'gameplayComparedBeforeDependentNarration':True,'newOnlyScenes':len(items),'newKoLines':sum(len(s['ko']) for s in items),'checks':checks,'scriptSha256':{lang:sha(ROOT/'projects'/AUX/f'script/narration.{lang}.json') for lang in ['ko','en']},'voiceSettingsExact':voice,'voiceReferenceSha256':{key:sha(ROOT/tts[key]) for key in ['reference','referenceText']},'projectManifestSha256':sha(ROOT/'projects'/AUX/'project.json'),'coordinateContract':old['contract'],'engineInternalsAsserted':False,'humanListening':'pending'};write(B/'lines-pretts-audit.json',audit)
q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']==BASE);item['status']='additive-preparation';item['revision'].update(episodeSlugs=[e['slug'] for e in flow['episodes']],originalPreservationAuditPassed=True,footageComparisonPassed=True,episodePlanReviewed=True,flowReviewPassed=False,narrationComplete=False,renderComplete=False);q['execution']['stage']='Interpolation first finishing upload; lines/bounds additive scripts/math ready, current training boundary required before TTS';write(B/'queue.json',q)
print(json.dumps({'originalScenes':22,'newTtsScenes':len(items),'newKoLines':audit['newKoLines'],'mathChecks':len(checks),'actualCapacities':[a['newActualCapacitySeconds'] for a in audits],'mediaComplete':False},ensure_ascii=False))
