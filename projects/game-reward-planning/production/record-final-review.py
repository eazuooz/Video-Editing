"""Record direct readings only after all contact pages and ASR texts were inspected."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent; W=BASE/'final-v1'; EDIT=BASE/'measured-edit-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'));write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');now=datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
pixel=read(W/'pixel-review-v1/index.json');render=read(W/'render-result.json');tech=read(W/'technical-measurements.json');voice=read(BASE/'voice-approval-v3.json');asr=read(W/'mixed-asr-v1/asr.json');adaptive=read(W/'mixed-asr-adaptive-v1/asr.json')
assert len(pixel['pages'])==22 and len(pixel['rows'])==509 and pixel['captionedSha256']==render['captionedSha256']==sha(ROOT/render['captioned'])
assert asr['complete'] and len(asr['results'])==20 and adaptive['complete'] and len(adaptive['results'])==4 and asr['mixSha256']==adaptive['mixSha256']==tech['mixSha256']
assert voice['allCurrentScenesTechnicallyReviewed'] and voice['paragraphCount']==52 and tech['identicalAAC']
findings=[
 'All22 contact pages were directly read:352 caption/cut intersections,154 encoded first/last boundaries and3 composition views,464 unique rendered frames. All268 Korean cues are represented.',
 'All narration boxes stay at960,970; every rendered line fits. Key selection/research/material prompts remain readable. Gameplay fills the screen; no source audio is present.',
 'All seven white2.5D scenes, including the whole-video overview, retain readable comparisons/arrows and a clear subtitle band. The six-second potion-state study is classified as explanation.',
 'The first04 paragraph announces separately edited collection and research examples; collection precedes the research view within that paragraph observation interval. It does not assert that the combat frame is a research interface or prove a continuous paid unlock.',
 'Wolf wind-up views retain the large enemy, attack preparation and main floor markers above the caption. The subtitle covers part of the foreground lamb body; its head and the narrated enemy action remain visible. No interface or narrated target is obscured.',
 'Original12 membership profile/name/badge rows, exact thank-you title, original cat logo and canonical coaching URL are visible at the first, middle and final outro frames. Truncated handles remain pending.'
]
for r in pixel['rows']:r['directlyRead']=True;r['result']='caption-and-narrated-focus-readable'
pixel.update(status='directly-reviewed-current-rendered-pixels',allCaptionPixelsApproved=True,reviewedAt=now);write(W/'pixel-review-v1/index.json',pixel)
critical=read(W/'pixel-review-v1/critical-index.json');critical['directlyRead']=True;critical['reviewedAt']=now;write(W/'pixel-review-v1/critical-index.json',critical)
pixelproof={'reviewedAt':now,'captionedSha256':render['captionedSha256'],'index':(W/'pixel-review-v1/index.json').relative_to(ROOT).as_posix(),'all22PagesDirectlyRead':True,'all268KoreanCuesDirectlyRead':True,'captionIntersections':352,'encodedBoundaryViews':154,'uniqueFrames':464,'criticalEnlargedViews':18,'additionalFullSizeViews':['frame-0408.jpg','frame-0464.jpg'],'fixedCenter':[960,970],'findings':findings,'humanWholeListening':'pending','truncatedMemberHandles':'pending'};write(W/'pixel-review-v1/direct-review.json',pixelproof)
notes={
 '01':'All four overview promises and first-example connection present. 길 is transcribed 기 in full and isolated mixed windows; preserve that spelling uncertainty and pending human pronunciation review.',
 '02':'All four function/action/limitation paragraphs present. Full opening adds ASR 자, while independent current mixed opening has no greeting. 발사 뒤 appears 발사디 in independent mixed ASR; current isolated PCM evidence and meaning are retained, pronunciation pending.',
 '03':'All three catalogue-role paragraphs present; proposal distinct from observed game rules.',
 '04':'All five resource/research/furnace/potion/bounty/limitation paragraphs present, including missing ingredients and separate edited interactions.',
 '05':'All three prerequisite/material/bypass/unconfirmed-condition paragraphs present.',
 '06':'All five water/electric/ice/coop/healing/overlap paragraphs present; pause context resumes 다음 컷 correctly.',
 '07':'All three growth/competition/limit/shared-use paragraphs present; cooperative footage not asserted to be PvP.',
 '08':'All four paragraphs present, including current 의상/가면 correction and no unlock/stat inference. Whole/short/long mixed ASR variably adds 아/스 to 컬트; current isolated PCM title reads 컬트. Preserve conflicting evidence, human title pronunciation pending. Full/clothing-join context reads 복장; short right-join begins inside phrase and yields6장, not a new narration sentence.',
 '09':'All three appearance/function/purpose paragraphs present.',
 '10':'All five placement/effects/production-work/budget-limitation paragraphs present; independent pause resumes correctly.',
 '11':'All three work-scope/reuse/new-assets/our-plan paragraphs present.',
 '12':'All seven terrain/coop/Cult/wind-up/avoidance/test-question paragraphs present. 새 is rendered 세 in ASR, the same spoken syllable; no item count claimed. Pause context uses 일어났습니다 versus full 일어납니다; preserve context difference.',
 '13':'All three complete-row/prerequisite/verify-in-play-and-production concluding paragraphs present; final words intact.'
}
proof={'reviewedAt':now,'status':'all-current-mixed-chapters-directly-compared-with-uncertain-spelling-preserved','mixSha256':asr['mixSha256'],'sourceVoiceApproval':(BASE/'voice-approval-v3.json').relative_to(ROOT).as_posix(),'all13FullChaptersDirectlyCompared':True,'all52ParagraphsCovered':True,'independentContextsDirectlyCompared':11,'fullReport':(W/'mixed-asr-v1/asr.json').relative_to(ROOT).as_posix(),'adaptiveReport':(W/'mixed-asr-adaptive-v1/asr.json').relative_to(ROOT).as_posix(),'chapters':[{'scene':str(i).zfill(2),'notes':notes[str(i).zfill(2)]} for i in range(1,14)],'endingHeuristicUsedAsApproval':False,'missingOrRepeatedNarrativeParagraphsObserved':False,'arbitraryGreetingProved':False,'humanWholeListening':'pending','pronunciationApproval':'pending','uncertainWords':['길/기','발사 뒤/발사디','컬트/아스컬트/스컬트'],'retimingOrResynthesisPerformed':False};write(W/'full-mix-asr-review.json',proof)
tracks=read(EDIT/'caption-tracks-v2.json');ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json')
norm=lambda s:re.sub(r'\s+','',s)
paragraphs=[]
for s in ko['scenes']:
 es=next(x for x in en['scenes'] if x['id']==s['id'])
 for i,(kt,et) in enumerate(zip(s['lines'],es['lines']),1):
  kr=[r for r in tracks['koRows'] if r['scene']==s['id'] and r['paragraph']==i];er=[r for r in tracks['enRows'] if r['scene']==s['id'] and r['paragraph']==i]
  assert kr and er and norm(''.join(r['ko'] for r in kr))==norm(kt) and norm(''.join(r['en'] for r in er))==norm(et)
  assert abs(kr[0]['startSeconds']-er[0]['startSeconds'])<=.001 and abs(kr[-1]['endSeconds']-er[-1]['endSeconds'])<=.001
  paragraphs.append({'scene':s['id'],'paragraph':i,'start':kr[0]['startSeconds'],'end':kr[-1]['endSeconds'],'koCues':[r['index'] for r in kr],'enCues':[r['index'] for r in er]})
assert len(paragraphs)==52
alignment={'schemaVersion':1,'status':'approved-semantic-paragraph-alignment','reviewedAt':now,'approved':True,'paragraphs':paragraphs,'allParagraphTextsRetained':True,'manualSemanticReview':True,'captions':[{'language':lang,'path':(EDIT/f'captions.{lang}.srt').relative_to(ROOT).as_posix(),'sha256':sha(EDIT/f'captions.{lang}.srt'),'cues':len(tracks[lang+'Rows'])} for lang in ['ko','en']],'reason':'Independent English clause groups preserve all52 paragraph meanings and spoken paragraph intervals;268 Korean and109 English cues intentionally differ.'};write(EDIT/'caption-alignment-review.json',alignment)
tracks.update(allFixedCaptionPixelsApproved=True,status='all-rendered-KO-pixels-and-independent-EN-semantic-groups-reviewed');write(EDIT/'caption-tracks-v2.json',tracks)
qa={'schemaVersion':1,'status':'technical-approved-human-listening-and-public-rights-pending','reviewedAt':now,'technicalApproved':True,'frames':26693,'seconds':26693/60,'actualFrames':15584,'explanationFrames':10389,'bodyActualRatioErrorFrames':.5,'actualExistingGameCuts':67,'officialSources':8,'agentCreatedGameCuts':0,'sourceAudioStreams':0,'original52PcmParagraphsPreserved':True,'sevenExplanationWholePcmPreserved':True,'allCurrentVoiceAsrDirectlyCompared':True,'allCurrentFinalMixAsrDirectlyCompared':True,'allRenderedCaptionPixelsReviewed':True,'captionCenter':[960,970],'koCues':268,'enCues':109,'allBilingualParagraphs':52,'wholeVideoOverview':{'afterOriginalBrandingSeconds':2,'measuredSeconds':24.15,'classified':'explanation','promisesPresentInBodyAndConclusion':True},'membershipOutroFrames':600,'memberIdentities':'original12rows-preserved','evidence':{'technical':(W/'technical-measurements.json').relative_to(ROOT).as_posix(),'pixels':(W/'pixel-review-v1/direct-review.json').relative_to(ROOT).as_posix(),'mixedAsr':(W/'full-mix-asr-review.json').relative_to(ROOT).as_posix(),'captionAlignment':(EDIT/'caption-alignment-review.json').relative_to(ROOT).as_posix()},'cleanSha256':render['cleanSha256'],'captionedSha256':render['captionedSha256'],'humanWholeListening':'pending','pronunciationApproval':'pending','uncertainPronunciationWords':proof['uncertainWords'],'finalPublicRights':'pending','originalNimbus':'pending','truncatedMemberHandles':'pending','externalBackup':'pending','privateUpload':'pending','platformAutomaticDubbing':'pending'};write(W/'qa.json',qa)
render.update(status='technical-approved-awaiting-collection-and-private-save',technicalQa=True,allFinalCaptionPixelsApproved=True,qa=(W/'qa.json').relative_to(ROOT).as_posix());write(W/'render-result.json',render)
print(json.dumps({'technicalApproved':True,'fixedKoCues':268,'englishCues':109,'humanListening':'pending'}))
