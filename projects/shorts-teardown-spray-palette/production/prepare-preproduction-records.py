"""Reproducible preproduction records only. No speech, render or platform jobs."""
from pathlib import Path
import hashlib, json, re, subprocess
from datetime import datetime, timezone

R = Path(__file__).resolve().parents[3]
P = R / 'projects/shorts-teardown-spray-palette'
LOCAL = P / 'production/local'
SLUG = 'shorts-teardown-spray-palette'
REV = 'spray-palette-v1'
NOW = datetime.now(timezone.utc).isoformat()
AUTH = 'explicit-cuphead-teardown-splatoon-20261026'
PRIMARY = 'https://blog.voxagon.se/2020/12/03/spraycan.html'

def write(rel, value):
    path = P / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

# Each line is a breath-sized paragraph. IDs are stable for later real-PCM alignment.
rows = [
    [
        ('이 스프레이, 색을 칠하는 순간 번호를 바꿉니다.', '이 스프레이, 색을 칠하는 순간\n번호를 바꿉니다.', 'This spray changes a number to paint.'),
        ('테어다운이 쓴 꼼수죠.', 'Teardown이 쓴 꼼수죠.', 'That is Teardown\'s trick.'),
    ],
    [
        ('작은 입체 칸인 복셀마다,', '작은 입체 칸인 복셀마다,', 'Each voxel is a tiny 3D cell.'),
        ('색 대신 재질 번호 한 바이트를 넣어요.', '색 대신 재질 번호\n1바이트를 넣어요.', 'It stores a one-byte material number.'),
        ('이 번호를 재질 인덱스,', '이 번호를 재질 인덱스,', 'This number is the material index;'),
        ('번호로 찾아보는 재질표를 팔레트라고 합니다.', '번호로 찾아보는 재질표를\n팔레트라고 합니다.', 'the material table is called a palette.'),
    ],
    [
        ('로딩할 때 원래 재질과,', '로딩할 때 원래 재질과,', 'At load time, prepare the original'),
        ('점점 노래지는 재질을 미리 준비합니다.', '점점 노래지는 재질을\n미리 준비합니다.', 'and progressively yellower variants.'),
        ('뿌릴 때는 팔레트 변환표를 보고,', '뿌릴 때는 팔레트 변환표를 보고,', 'Spraying consults a translation table'),
        ('해당 복셀의 번호만 바꿔요.', '해당 복셀의 번호만 바꿔요.', 'and changes the voxel\'s index.'),
    ],
    [
        ('예를 들어 삼 번 벽돌을,', '예를 들어 3번 벽돌을,', 'For example, replace brick index 3'),
        ('구 번 노란 벽돌로 바꾸는 식이죠.', '9번 노란 벽돌로 바꾸는 식이죠.', 'with yellow-brick index 9.'),
        ('모양은 그대로인데 색이 달라집니다.', '모양은 그대로인데\n색이 달라집니다.', 'Its shape stays; its color changes.'),
    ],
    [
        ('문제는 표의 크기입니다.', '문제는 표의 크기입니다.', 'The palette has limited space.'),
        ('최대 이백오십오 칸에,', '최대 255칸에,', 'There are up to 255 material slots.'),
        ('노랑 네 단계와 검정 네 단계까지 넣으면,', '노랑 4단계와\n검정 4단계까지 넣으면,', 'Add four yellow and four black shades:'),
        ('원래 재질 하나에 아홉 칸이 필요해요.', '원래 재질 하나에\n9칸이 필요해요.', 'one original now needs nine slots.'),
    ],
    [
        ('공간이 부족하면 비슷한 색을 합치고,', '공간이 부족하면\n비슷한 색을 합치고,', 'When space runs out, merge similar colors'),
        ('남은 재질에서 가장 가까운 색을 고릅니다.', '남은 재질에서\n가장 가까운 색을 고릅니다.', 'and choose the closest available match.'),
        ('그래서 초기 구현의 복잡한 성에서는,', '그래서 초기 구현의\n복잡한 성에서는,', 'In the early Castle example,'),
        ('노랑 대신 갈색이 되거나 그대로인 곳도 있었죠.', '노랑 대신 갈색이 되거나\n그대로인 곳도 있었죠.', 'some surfaces turned brown or stayed unchanged.'),
    ],
    [
        ('물감 하나에도,', '물감 하나에도,', 'Even a spray can hides a trade-off:'),
        ('적은 메모리와 풍부한 색 사이의 타협이 숨어 있습니다.', '적은 메모리와 풍부한 색 사이의\n타협이 숨어 있습니다.', 'less memory versus more color choices.'),
    ],
]
lines = [' '.join(part[0] for part in row) for row in rows]
clauses = [dict(id=f'p{i+1}-{j+1}', lineIndex=i, spoken=v[0], ko=v[1], en=v[2]) for i,row in enumerate(rows) for j,v in enumerate(row)]
write('script/narration.spoken.ko.json', dict(slug=SLUG, revision=REV, status='draft-footage-pending', scenes=[dict(id='main', lines=lines)]))
write('script/clauses.json', dict(clauses=clauses, pronunciationAliases={}))
(P/'script/narration.ko.txt').write_text('\n\n'.join(lines)+'\n', encoding='utf-8')
(P/'script/narration.en.txt').write_text('\n\n'.join(' '.join(p[2] for p in r) for r in rows)+'\n',encoding='utf-8')

write('project.json', dict(slug=SLUG, title='색을 칠했는데, 바뀐 건 번호였다? | Teardown 스프레이의 비밀', format=dict(type='youtube-shorts',width=1080,height=1920,fps=60),status='preproduction-blocked-independent-spray-footage',currentRevision=REV,authorization=dict(id=AUTH,productionDateKst='2026-10-26',scope='Explicit finite Cuphead/Teardown/Splatoon production; this agent is restricted to Teardown preproduction.',userEvidence='Parent relayed a new explicit user request for Cuphead, Teardown and Splatoon Shorts on 2026-10-26; later fourth Splatoon ink topic keeps same authorization.',fullProductionAuthorized=True,humanFinalReviewRequired=True,youtubeAuthorized=False,driveAuthorized=False),paths=dict(script=f'projects/{SLUG}/script/narration.spoken.ko.json',checkpoint=f'projects/{SLUG}/production/checkpoint.json',productionPlan=f'projects/{SLUG}/planning/production-plan.json',timeline=f'projects/{SLUG}/production/visual-timing.json'),mediaRoot=f'C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/{SLUG}',currentFinalDirectory='production/local/final-reviewed-v1',publishReady=False))

observations = {
 'teardown-official-steam-trailer-1080p60.mp4': ('https://store.steampowered.com/app/1167630/Teardown/', '50 ordered samples at approximately 2-second spacing; 18–24s four-fps close inspection and native20.5s', 'No actual spray action confirmed. Suspected20–22s was walking and existing scenery, not paint application.'),
 'teardown-official-pr-trailer-2022.mp4': ('https://www.youtube.com/watch?v=56zNrL0lJ5Y','47 ordered one-second samples','New features montage. No spray application confirmed.'),
 'teardown-ttwBelIlLv8.mp4': ('https://www.youtube.com/watch?v=ttwBelIlLv8','100 ordered one-second samples across three contact sheets','Destruction/heist/mods trailer. Yellow route markings are visible, but spray application not established.'),
 'teardown-cVRyoUJyxIE.mp4': ('https://www.youtube.com/watch?v=cVRyoUJyxIE','43 ordered one-second samples','Heist trailer; no actual spray application confirmed.'),
 'teardown-Ov5GxFlHqUQ.mp4': ('https://www.youtube.com/watch?v=Ov5GxFlHqUQ','93 ordered one-second samples;38.5–43s at4fps and native40.5s','Yellow roof route lines are already present. Tool is a gun making a hole; explicitly rejected as spray evidence.'),
 'teardown-0OtAzeu0L5s.mp4': ('https://www.youtube.com/watch?v=0OtAzeu0L5s','79 ordered approximately two-second samples;66–72s at4fps','Official gameplay overview; sampled tool shots show selection/destruction, no verified spray-before/action/result.'),
}
candidates=[]
for name, (url,viewed,note) in observations.items():
    f=LOCAL/'sources'/name
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,codec_name:format=duration,size','-of','json',str(f)],text=True,encoding='utf-8'))
    candidates.append(dict(id=name,sourceUrl=url,path=f'projects/{SLUG}/production/local/sources/{name}',sha256=sha(f),probe=data,sourceKind='official-gameplay-promotional-trailer',adopted=False,reason=note,actuallyViewedSamples=viewed,fullRealtimePlaybackClaimed=False,sourceAudioAdopted=False,rightsStatus='official-source-established-reuse-license-not-assumed'))
research=LOCAL/'research/spray-developer-720p-RESEARCH-ONLY.mp4'
researchVideo=dict(id='developer-spray-20201015',url='https://twitter.com/tuxedolabs/status/1316718751421784066/video/1',path=f'projects/{SLUG}/production/local/research/{research.name}',sha256=sha(research),sourceKind='research-reference-only',width=1280,height=720,productionAllowed=False,reason='Highest listed original rendition is720p, below mandatoryFHD. No upscaling exception requested or inferred.',actuallyViewedSamples='20 chronological2s samples; spray paints continuous yellow paths over ground, pallets, barrels and a red car, with spray tool visible.',actualRealtimePlaybackClaimed=False,sourceAudioAdopted=False)
write('sources/selected-footage.json', dict(revision=REV,status='no-qualified-source-selected',independentFootageViewed=False,selected=[],candidates=candidates,researchOnly=[researchVideo],requiredNextSource=dict(phenomenon='Actual spray can applying yellow paint with visible before/action/result on a surface',minimumNative=[1920,1080],speed=1,rights='Original recorder or publisher permission for adopted clip; publisher self-recorded-gameplay policy alone does not establish rights to reuse somebody else\'s recording.',sourceAudio='Excluded unless separately cleared'),noReferenceSourceMayEnterCutList=True))
write('sources/rights-review.json',dict(updatedAt=NOW,status='no-adopted-footage',primary=dict(url=PRIMARY,snapshot=f'projects/{SLUG}/production/local/research/spraycan-primary.html',sha256=sha(LOCAL/'research/spraycan-primary.html'),role='technical-fact-reference',fullArticleRead=True,publicationDate='2020-12-03',scope='Historical implementation, not independently verified current2026 internals'),gameplayPolicy=dict(url='https://store.steampowered.com/eula/1167630_eula_0',snapshot=f'projects/{SLUG}/production/local/research/teardown-eula.html',sha256=sha(LOCAL/'research/teardown-eula.html'),finding='Own play recordings may be posted in good taste with game name and Tuxedo Labs developer credit. No inference that this licenses reuse of third-party recordings.'),pressKit=dict(url='https://teardowngame.com/download/presskit.zip',sha256=sha(LOCAL/'research/teardown-official-presskit.zip'),contents='Key art, logos, screenshots and stickers. No video or permission text in the archive.',use='Research only, no production asset selected.'),officialPR=dict(url='https://www.vicariouspr.com/clients/teardown/',trailer='https://www.youtube.com/watch?v=56zNrL0lJ5Y',assetFolder='https://drive.google.com/drive/u/1/folders/1quu_k6sYFYEu6pJdO4CT-JzkLoWu5YUF',finding='Press-facing trailer and download-assets links; this trailer does not supply the needed action. No blanket CC/monetization grant asserted.'),creditsRequiredWhenGameUsed=['Teardown — Tuxedo Labs','Exact adopted recorder/source URL once selected'],sourceAudioAdopted=False,publishReady=False))

ids=['game','index','variants','lookup','capacity','limits','close']
starts=[0,5,15,25,33,44,55,60]
write('production/section-plan.json',[dict(id=id,paragraph=i,firstCue=f'p{i+1}-1',purpose=id) for i,id in enumerate(ids)])
write('production/visual-timing.json',dict(revision=REV,previewOnly=True,timingStatus='Layout placeholder only; no PCM. Never use as final timing or claim as60s finished duration.',fps=60,frames=3600,durationSeconds=60,sections=[dict(id=id,start=starts[i],end=starts[i+1],startFrame=starts[i]*60,endFrame=starts[i+1]*60,kind='diagram',forceDiagram=True) for i,id in enumerate(ids)],events={},sources={},reactions=[],actualAudioListening='not-generated',fullMovingReview='not-rendered'))
write('production/visual-config.json',dict(slug=SLUG,revision=REV,game='Teardown',headline=['색을 칠했는데','바뀐 건 번호?'],term='팔레트 변환표',english='Palette translation table',historicalScope='2020년 공개 구현',sourceGameMaster=None,sourceSHA256=None,sourceAudioAdopted=False,cuts={},frameRoot=f'/@fs/D:/Github/VideoEditing/projects/{SLUG}/production/local/frames/',footageReady=False,productionRenderReady=False,diagramLabel='원리 설명용 모형 · 번호는 예시',headerSuppliedByFinalizer=True,fixedHeaderHeight=440,captionCenter=[510,1380],captionClearanceY=[1290,1470],model=dict(originalIndex=3,yellowIndices=[9,11,13,15],knownPaletteMaterialLimit=255,stepsPerTint=4,tints=2,slotsPerOriginalWithoutMixedTints=9,oneVariable='available palette slots',notGameMeasurements=True),eventCues={'voxelReveal':['p2-1'],'indexReveal':['p2-2','p2-3'],'paletteReveal':['p2-4'],'variantsReveal':['p3-1','p3-2'],'lookupReveal':['p3-3'],'recolor':['p3-4'],'numberSwap':['p4-1','p4-2'],'sameShape':['p4-3'],'capacityReveal':['p5-1','p5-2'],'variantCount':['p5-3','p5-4'],'slotsFull':['p6-1'],'nearestMatch':['p6-2'],'historicLimit':['p6-3','p6-4'],'conclusion':['p7-1','p7-2']}))

write('planning/production-plan.json',dict(slug=SLUG,revision=REV,updatedAt=NOW,status='preproduction-blocked-independent-spray-footage',scriptFinalized=False,independentFootageViewed=False,technicalResearchComplete=True,sourceRightsReady=False,narrationScope='2020 spray-palette method and its capacity trade-off; the current game is not claimed to retain every historical implementation detail.',targetDurationSeconds=[45,60],durationEvidence='Writing target only; natural Qwen duration and pacing not yet measured. Keep understanding; do not speed voice toforce60s.',primarySource=dict(url=PRIMARY,fullScopeRead=True),claims=[dict(id='material-index',sourceParagraphs=[1],cueIds=['p2-1','p2-2','p2-3','p2-4'],claim='Per voxel one-byte material index referencing object palette; material includes appearance and physical properties, not just RGB.',visual='Same cells point to an explicit material list; byte means per voxel, not total game memory.'),dict(id='precompute',sourceParagraphs=[3,4],cueIds=['p3-1','p3-2'],claim='At load, precompute yellow/black material variations in available palette slots.',visual='Original material plus four increasingly yellow slots; source knows foursteps, not continuous shades.'),dict(id='translate',sourceParagraphs=[6,7,8,9,10,11],cueIds=['p3-3','p3-4','p4-1','p4-2','p4-3'],claim='Table lookup maps current material index to tint variant.',visual='Illustrative3→9→11; same occupied voxel cells retained. Allindices explicitly toyvalues.'),dict(id='capacity',sourceParagraphs=[4,5,12],cueIds=['p5-1','p5-2','p5-3','p5-4'],claim='255 material entries; two tints times foursteps plus original costs9slots before mixed yellow/black variants.',visual='1+4+4=9; show mixed tints need additional entries in small note, no exhaustiveCartesiancount claim.'),dict(id='limits',sourceParagraphs=[6,13,14,15,16,17],cueIds=['p6-1','p6-2','p6-3','p6-4','p7-1','p7-2'],claim='Merge visually similar colors, stopadding whenfull; construct lookup from all available materials. Early Castle singlepalette sometimesbrownorunchanged.',visual='Only palette capacity changes; same desiredyellow and same target. Caption2020Castle; no present-dayallwallsclaim.' )],sourceOrder=['representation','precompute-variants','table-lookup','capacity','best-match-limits'],omissions=[dict(item='GPU palette texture packing and fragment palette inheritance',reason='Background storage layout not needed for selected spray-index mechanism; not contradicted.'),dict(item='DOOM comparison',reason='Historical analogy not needed; avoids another game or invented source clips.'),dict(item='Exact C declaration and transparency priority',reason='Specialist implementation details beyond this selected short; preserve key constraints in internal notes.'),dict(item='Future optimization wish',reason='Nonimplemented future plan, not evidence ofcurrentalgorithm.')],glossary=[dict(ko='복셀',en='Voxel',meaning='작은 입체 칸'),dict(ko='재질 인덱스',en='Material index',meaning='재질표의 한 항목을 가리키는 번호'),dict(ko='팔레트',en='Palette',meaning='색과 표면·물리 속성을 담은 재질표'),dict(ko='팔레트 변환표',en='Palette translation table',meaning='원래 번호에 대응하는 색칠된 재질 번호를 찾아 주는 표')],rendererChoice=dict(renderer='Motion Canvas',reason='This explains a data lookup and resource-capacity relation, not a self-authored playablegame or3Dscene. One persistent2D cell grid and palette makeindex changes visible without building a duplicate engine.',paths=[f'motion-canvas/src/projects/{SLUG}/project.ts',f'motion-canvas/src/projects/{SLUG}/scene.tsx',f'motion-canvas/src/projects/{SLUG}/model.ts']),continuity=[dict(boundary='game→index',link='Painted patch becomes same labelled cell grid'),dict(boundary='index→variants',link='Keep materialtable andadd precomputed slots'),dict(boundary='variants→lookup',link='Keep originalindex andtargetslot;showarrow'),dict(boundary='lookup→capacity',link='Keep table, count occupiedslots'),dict(boundary='capacity→limits',link='Same target, removeavailablevariants only'),dict(boundary='limits→close',link='Keep memoryandcolortradeoff alongside finalpaintresult')],teachingBeats=[dict(section=id,paragraph=i,speech=f'p{i+1}-*',hold=0,visual='Existing stage carries across scene; current sentence reveals the relevant object/action/result.') for i,id in enumerate(ids)],layout=dict(canvas=[1080,1920],staticHeader=[0,0,1080,440],diagramY=[460,1250],fixedCaptionCenter=[510,1380],captionReservedY=[1290,1470],cat=dict(region=[760,1480,280,420],beats=['lookup-reveal','closing'],occlusion='Never coverlookupdestination orsubtitles'),credits='description only'),sourceBlocker='No nativeFHD independently cleared spray-before/action/result clip has been selected. Exact developer demonstration is720p researchonly. No unrelateddestruction substitution.',gpuBlocker='Parent observedOverwatch.exe82620. Do notrunTTS/GPU/render/devserver whilegameactive.',reviewState=dict(voice='not-generated',visualRender='not-generated',fullMoving='not-reviewed',human='not-reviewed'),sourceAudioAdopted=False))

write('production/checkpoint.json',dict(schemaVersion=1,slug=SLUG,revision=REV,productionDateKst='2026-10-26',updatedAt=NOW,status='preproduction-blocked-independent-spray-footage',authorization=AUTH,completed=['Full primary technical article read','Six official nativeFHD candidates downloaded toC and relevant chronologicalsamples directlyviewed','Exact developer spraydemo found andviewed;720pmaximum recorded andexcludedfromproduction','KOdraft+ENclauses withsameparagraphscope','Source/provenance/rights/claim/sceneplans','Editabledata-modelMCscene sourceprepared'],notCompleted=['IndependentFHDsprayclipselectionandrights','Finalnarrationlock','TTS/PCM/ASR/captiontiming','Encodedvisual/audio/mobileQA','Fourdeliverables','Humanfinalreview'],blockers=[dict(kind='independent-spray-footage-missing',detail='720pdeveloperreferencecannotqualify;examinedFHDpromotionalclipsdonotconfirmrequiredaction'),dict(kind='user-game-active',name='Overwatch.exe',observedPid=82620,observationBy='parent at delegation',policy='NoGPU/TTS/render/devserverjobs')],costlyJobsStarted=0,lightCpuResearchJobs='Source download, limited source frame extraction, probes, pure-model/syntax validation only',foreignProcessesStopped=False,nextActions=['Find a native1080-or-higher recording that actually shows spray application and establish recorder/publisher reuse basis. Do not substitute destruction shots or upscale720p.','Inspectbefore/action/result source interval atnative size; thenfinalize script andcutplan.','Aftergameexit andparentcoordination, useapprovedvoice withactualPCM/cues beforeanytimingrender.','RenderscopedC fouroutputs, complete actual audio/moving/mobileQA andhumanreview. NoYouTubeorDrive scope here.']))
write('production/review-ledger.json',dict(revision=REV,updatedAt=NOW,status='preproduction-only',sourceInspection=dict(candidateCount=6,qualifiedAdoptedCount=0,referenceOnly720pActuallyViewed=True,fullRealtimePlaybackClaimed=False),checks=dict(primaryFullRead='pass',candidateNativeFhdProbe='pass-all-six',independentFootageSelection='blocked',rights='noadoptedfootage',scriptClauses='exactparagraphreconstructionchecked',voice='not-generated',audioListening='not-performed',sceneSyntax='pending',pureModel='pending',render='not-performed',mobilePlayback='not-performed'),actualUserReview=False,approvedMasterSha256=None,pending=['nativeFHDspraybefore/action/result','recordingreusebasis','actualPCMtimming','sourcecallouttracking','encodedspatialandmobilecheck','fulllistening','humanreview']))
(P/'publishing/title.ko.txt').write_text('색을 칠했는데, 바뀐 건 번호였다? | Teardown 스프레이의 비밀 #게임개발 #shorts\n',encoding='utf-8')
(P/'publishing/title.en.txt').write_text('Teardown Paints by Changing a Number | Palette Translation #gamedev #shorts\n',encoding='utf-8')

for i,line in enumerate(lines):
    assert ' '.join(c['spoken'] for c in clauses if c['lineIndex']==i)==line
report=dict(revision=REV,clauseCount=len(clauses),paragraphCount=len(lines),koreanSyllableCount=len(re.findall('[가-힣]',''.join(lines))),paragraphReconstruction=True,scriptFinalized=False,mediaRoot=str(LOCAL.resolve()))
write('production/preproduction-validation.json',report)
print(json.dumps(report,ensure_ascii=False))
