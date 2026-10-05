"""Add8 measured guides without altering any original52 paragraph or PCM."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PROJECT=BASE.parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
textsha=lambda t:hashlib.sha256(t.encode('utf-8')).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stamp=datetime.now(timezone.utc).isoformat()
assert not (BASE/'guided-observation-adoption-v3.json').exists(),'Preserve completed adoption.'
request=read(BASE/'guided-observation-tts-request-v3.json');plan=read(BASE/'measured-edit-v3/plan.json');review=read(BASE/'guided-observation-direct-review-v3.json')
assert review['allEightGuidesTechnicallyCompared'] and not plan['finalTimingApproved']
for p in request['protectedInputs']:assert sha(ROOT/p['path'])==p['sha256'],p['path']
audit=[]
for lang in ['ko','en']:
    path=PROJECT/f'script/narration.{lang}.json';original=read(path)
    baseline=PROJECT/f'script/narration.before-guides-v3.{lang}.json';assert not baseline.exists();save(baseline,original)
    for s in original['scenes']:
        measured=next(x for x in plan['scenes'] if x['id']==s['id']);before=list(s['lines']);after=[p[lang] for p in measured['speechEvidence']]
        kept=[p[lang] for p in measured['speechEvidence'] if p['originalParagraph'] is not None]
        assert before==kept
        audit.append({'language':lang,'scene':s['id'],'originalParagraphs':len(before),'currentParagraphs':len(after),'everyOriginalParagraphAndOrderIdentical':True,'baseline':baseline.relative_to(ROOT).as_posix(),'literalHashes':[textsha(x) for x in before]})
        s['lines']=after
    save(path,original)
outline=PROJECT/'planning/outline.md';text=outline.read_text('utf-8-sig').replace('## 현재 완료와 pending','## 최초 계획 당시 완료와 pending — 역사 기록')
text+='\n## 현재13씬60문단 안내해설 추가 — '+stamp+'\n\n'
text+='현재52KOEN문단의 문장·순서와509.624초의 모든PCM, 여섯흰설명222.446초/원래최소219.68초 및 전체안내24.14초를 그대로 보존했습니다. 길게말없던 동작에는 독립8KOEN안내44.96초만 추가하여 현재음성554.584초입니다. 전체8ASR와 불명확한13-g1의두완결문맥을 직접대조했으며 사람청취·발음은pending입니다.\n\n'
text+='02벽옆접근·직접공격,06전투효과뒤별도준비미리보기,13거리·가까운공격·별도먼발사,12미리보기뒤별도높은자리전투를 안내합니다.12의원래결론두문단은 마지막에유지하며 전투를 결론뒤붙이지않습니다. 네 rail/계단·기둥/상부카메라 구간을제외하고 고유관련행동을재배정했습니다. 모든native구간과단어·자막의새경계는 measured-edit-v3/plan.json의검수후보이며 최종승인이아닙니다.\n\n'
text+='도입의질문은03/05/07, 제작재사용과플레이새결정·검증은03/04/05/09/11/12결론, 실제순서는02→04/06/13→08/10/12, 첫사례연결은02첫벽미리보기에그대로있습니다. 새안내는이미보인행동의관찰을돕고 새로운승리·비용·개발의도·보편규칙을약속하지않습니다.독립13MC/원래흰도식을보존하며본편60:40에모두포함합니다.\n\n'
text+='현재593.05초후보 actual20918/white13945프레임의오차0.2프레임은계산값입니다.모든최종큐·컷·흰도식픽셀/새접합ASR/믹스·렌더·QA·수집·비공개는미완료입니다. planning/guided-observation-v3.json와production/guided-observation-adoption-v3.json의문단별출처·삽입·보존을따릅니다.새이미지는local-only입니다.\n'
outline.write_text(text,encoding='utf-8')
chapter=read(PROJECT/'planning/chapter-plan.json');chapter['historicalBeforeGuidesV3']=copy.deepcopy(chapter['chapters'])
chapter['overview']['measuredSeconds']=24.14
for c in chapter['chapters']:
    s=next(x for x in plan['scenes'] if x['id']==c['id']);c.update(measuredNarrationSeconds=s['currentPcmSeconds'],currentParagraphs=len(s['speechEvidence']),sourceActionIds=sorted(set(x['bankCutId'] for x in s['segments'] if x['classification']=='actual-existing-game')),finalTimingApproved=False,candidateStartFrame=s['startFrame'],candidateEndExclusive=s['endFrameExclusive'],candidatePlan='projects/making-game-sequels/production/measured-edit-v3/plan.json')
chapter.update(updatedAt=stamp,paragraphs=60,guidePlanning='projects/making-game-sequels/planning/guided-observation-v3.json',finalTimingApproved=False);save(PROJECT/'planning/chapter-plan.json',chapter)
action=read(PROJECT/'sources/action-map.json');action.update(status='Current13/60 component voice technically reviewed; current85 unique native cut candidate and all final pixels/joins pending',currentMeasuredCandidate='projects/making-game-sequels/production/measured-edit-v3/plan.json',guidedObservationPlanning='projects/making-game-sequels/planning/guided-observation-v3.json',guideBindings=request['guides'],original52ParagraphsPreserved=True,sourceAudioUsed=False,updatedAt=stamp);save(PROJECT/'sources/action-map.json',action)
index={'schemaVersion':1,'createdAt':stamp,'sceneCount':13,'paragraphs':60,'speechSeconds':554.584,'baseCurrentPcmSeconds':509.624,'newGuideSeconds':44.96,'originalSixExplanationMinimumSeconds':219.68,'currentSixExplanationPcmSeconds':222.446,'openingOverviewSeconds':24.14,'technicalApprovalOnly':True,'allCurrentComponentsTechnicallyCompared':True,'finalMixedScenesBuilt':False,'finalMixAsrApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending','baselineIndex':'projects/making-game-sequels/production/narration-expanded13-index.json','newGuideReview':'projects/making-game-sequels/production/guided-observation-direct-review-v3.json','scriptKoSha256':sha(PROJECT/'script/narration.ko.json'),'scriptEnSha256':sha(PROJECT/'script/narration.en.json'),'scenes':[{'id':s['id'],'baseAudio':s['audio'],'baseAudioSha256':s['audioSha256'],'baseSamples':s['baseSamples'],'currentSpeechSamples':s['currentSpeechSamples'],'seconds':s['currentPcmSeconds'],'paragraphs':len(s['speechEvidence']),'newGuides':[{'id':p['guideId'],'audio':p['audio'],'sha256':p['audioSha256'],'samples':p['pcmToSample'],'wholeAsr':p['asrEvidence']} for p in s['speechEvidence'] if p.get('guideId')]} for s in plan['scenes']]}
save(BASE/'narration-guided60-index-v3.json',index)
manifest=read(PROJECT/'project.json');manifest.update(status='current13-guided60-component-voice-reviewed-native-and-caption-v3-candidate-pending');manifest['paths']['timeline']='projects/making-game-sequels/production/measured-edit-v3/plan.json'
edit=manifest['editing'];edit['historicalMeasuredCandidateV2']=edit['measuredCandidate'];edit.update(timingStatus='guided60-candidate-final-pixels-and-new-joins-pending',currentVoiceReview='projects/making-game-sequels/production/narration-guided60-index-v3.json',measuredSpeechSeconds=554.584)
edit['measuredCandidate']={**edit['measuredCandidate'],'candidatePlan':manifest['paths']['timeline'],'paragraphs':60,'speechSeconds':554.584,'nativeCuts':85,'captionTracks':'projects/making-game-sequels/production/measured-edit-v3/caption-tracks-v3.json','captionLayout':'projects/making-game-sequels/production/measured-edit-v3/caption-layout-v3.json','nativeCompile':None,'koCues':308,'enCues':173,'allFinalPixelsReviewed':False,'newJoinAsrApproved':False,'guidedObservationReview':'projects/making-game-sequels/production/guided-observation-direct-review-v3.json'}
save(PROJECT/'project.json',manifest)
sr=read(BASE/'script-source-review.json');save(BASE/'script-source-review-before-guides-v3.json',sr)
sr['historicalBeforeGuidesV3Inputs']=sr['inputs'];sr.update(reviewedAt=stamp,status='current13-guided60-bilingual-source-and-component-voice-reviewed-final-pixels-and-joins-pending',paragraphs=60,voiceReview='projects/making-game-sequels/production/narration-guided60-index-v3.json',voiceAsrReview='Prior current13/52 PCM preserved and technically compared; eight new files and two onset contexts directly compared. Current554.584s is the component sum, not an approved final mix.',method=sr['method']+' Eight independent new KO/EN guide paragraphs directly compared against the observed native actions, complete ASR and two onset contexts. All52 original paragraphs and their order remain identical.')
sr['overviewPromiseReview']['productionAndPlayerOutcome']['fulfilledBy']=['03','04.4','05','09','11','12.5','12.6'];sr['overviewPromiseReview']['applyToOwnConcept']['fulfilledBy']=['11.1','11.2','11.3','12.5','12.6']
old_scenes={s['id']:s for s in sr['scenes']}
sr['scenes']=[]
for s in plan['scenes']:
    prior=old_scenes[s['id']];paras=[]
    for p in s['speechEvidence']:
        if p['originalParagraph'] is not None:r=copy.deepcopy(prior['paragraphs'][p['originalParagraph']-1])
        else:r={'meaningOrderClaimAndLimitsDirectlyCompared':True,'sourceActionIds':next(g['bankCutIds'] for g in request['guides'] if g['id']==p['guideId']),'guideId':p['guideId'],'technicalReview':'projects/making-game-sequels/production/guided-observation-direct-review-v3.json'}
        r.update(paragraph=p['paragraph'],originalParagraph=p['originalParagraph'],koSha256=textsha(p['ko']),enSha256=textsha(p['en']));paras.append(r)
    sr['scenes'].append({**prior,'paragraphs':paras,'measuredNarrationSeconds':s['currentPcmSeconds']})
sr['inputs']=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [PROJECT/'script/narration.ko.json',PROJECT/'script/narration.en.json',outline,PROJECT/'planning/chapter-plan.json',PROJECT/'sources/action-map.json',PROJECT/'sources/game-candidates.json',BASE/'narration-guided60-index-v3.json',BASE/'guided-observation-direct-review-v3.json',BASE/'measured-edit-v3/plan.json']];save(BASE/'script-source-review.json',sr)
d={'schemaVersion':1,'adoptedAt':stamp,'paragraphs':60,'preservedParagraphs':52,'newGuideParagraphs':8,'scenes':13,'speechSeconds':554.584,'basePcmSeconds':509.624,'newGuideSeconds':44.96,'audit':audit,'all52OriginalKoEnParagraphsAndOrderPreserved':True,'allBasePcmHashesPreserved':True,'originalSixExplanationMinimumSeconds':219.68,'currentSixExplanationSeconds':222.446,'overviewSeconds':24.14,'overviewPromisesDirectlyRechecked':True,'candidateOnly':True,'finalMixBuilt':False,'newJoinAsrApproved':False,'allFinalPixelsApproved':False,'privateVideoComplete':False,'newGitImages':0};save(BASE/'guided-observation-adoption-v3.json',d)
q=read(PROOF.parent/'queue.json');i=next(x for x in q['items'] if x['slug']=='making-game-sequels');i.update(stage=manifest['status'],updatedAt=stamp,guidedObservation={'planning':'projects/making-game-sequels/planning/guided-observation-v3.json','adoption':'projects/making-game-sequels/production/guided-observation-adoption-v3.json','currentIndex':'projects/making-game-sequels/production/narration-guided60-index-v3.json','newGuides':8,'allCurrentComponentSeconds':554.584,'technicalReviewComplete':True,'finalMixBuilt':False},nextAction='Compile only changed native v3 boundaries, reuse exact unchanged media; inspect every changed word/caption and native edge with new guides. All final timing, new joins, mix/render/QA/collection/private delivery remain pending.')
i['execution'].update(status='all-new-guide-ASR-and-context-workers-closed',alive=False,activeTasks=[],cpuProductionJobs=0,primaryCpuProductionJobs=0,gpuSynthesisJobs=0,renderJobs=0,uploads=0,observedAt=stamp);q['updatedAt']=stamp;save(PROOF.parent/'queue.json',q)
for path in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    cp=read(path)
    for k in ['stage','updatedAt','execution','guidedObservation','nextAction']:cp[k]=i[k]
    save(path,cp)
print(json.dumps({'adopted':True,'scenes':13,'paragraphs':60,'allOriginal52Preserved':True,'currentComponentSeconds':554.584,'finalVideoComplete':False}))
