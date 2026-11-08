"""Record direct sampled encoded review separately from pending human listening."""
from pathlib import Path
import json, datetime
P=Path(__file__).resolve().parents[1]
L=P/'production/local'
def read(p): return json.loads(p.read_text('utf-8'))
def save(p, obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=read(P/'production/technical-qa.json')
tm=read(L/'timeline.json')
asr=read(P/'production/asr-review.json')
assert asr['status']=='reviewed-complete-current-text' and asr['pairedCues']==249
master=next(v for v in qa['videos'] if v['kind']=='captioned')
review={
 'reviewedAt':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
 'masterSha256':master['sha256'],
 'duration':tm['duration'],
 'encodedVisualReview':{
  'status':'sampled-pass',
  'method':'Direct visual inspection of final encoded MP4 samples, not only renderer source images; this is sampled agent QA, not uninterrupted human playback.',
  'sceneSamples':30,
  'sceneContactSheets':[f'production/local/qa/encoded-contact-{n}.jpg' for n in range(4)],
  'targetedCueSamples':16,
  'targetedCueEvidence':'production/encoded-cue-samples.json',
  'mobileWidth':375,
  'directlyInspectedMobileScenes':['04','08','13','22','28'],
  'mobileObservations':'Main subjects, motion comparison, titles and fixed captions remain visible. Small subordinate workflow labels are secondary; the spoken explanation and large stage names carry the mobile reading.',
  'brandingAndMembership':'Encoded branding and membership frames directly inspected; no caption intrusion.',
  'changedSceneFindings':{
   '15':'Central reference precedes outward reveal; background expansion at the corresponding word, then character removal at the background-layer sentence.',
   '27':'Bilinear changes to Point at its spoken word; PPU increase decreases world size; Pivot remains at the feet and becomes the active labeled step.',
   '28':'Native motion precedes exact sequential frame inspection at 2 frames/second. Encoded samples show 1→2→3 and 24→1 with the foot baseline and editorial red box.'
  },
  'captionLayout':'249 sentence-aligned KO/EN cue pairs; actual Malgun Gothic Bold 48px width scan passed, maximum box 1402.6875px within1760px; inspected fixed960,970 clearance.',
  'noReferenceLessonFootage':True,
  'executedTools':['ComfyUI','PixelOE','pixelfx','Pixelbolt'],
  'illustrationBoundary':'Unexecuted animation tool flows, character LoRA training, outpainting and Unity import principles are labeled explanatory models rather than recorded tool execution.'
 },
 'asrTextReview':asr,
 'audioReview':{
  'allCurrentNarrationAndMixAsrRead':True,
  'paragraph15OpeningRepaired':True,
  'other29OriginalTakesPreserved':True,
  'encodedLufs':-16.65,
  'encodedTruePeakDbtp':-1.87,
  'adjacentParagraphJumpsAbove3Db':0,
  'shortQuietContextFlags':30,
  'quietFlagInterpretation':'Short windows can include breathing, sentence tails or pauses. Flags are retained for contextual human listening; no automatic defect claim or destructive compression.',
  'diagnostics':'Scene04 duplicated phrase in segment ASR was absent in word ASR and context-crop ASR. End-credit ASR hallucination occurred in measured digital silence. Neither was inserted in captions.',
  'wholeHumanListening':'pending',
  'speechNaturalnessAndPronunciation':'pending human review'
 },
 'humanReview':{'status':'pending','linkDeliveryIsNotViewing':True},
 'platform':{'youtubeUploadAuthorized':False,'driveUploadAuthorized':False,'mutationsPerformed':False}
}
save(P/'production/final-review.json',review)
qa['encodedVisualReview']={'status':'sampled-pass','evidence':'production/final-review.json','masterSha256':master['sha256']}
save(P/'production/technical-qa.json',qa)
plan=read(P/'planning/production-plan.json')
plan['finalVerification']={
 'evidence':'production/final-review.json',
 'captionEvidence':'production/caption-width-qa.json',
 'visualTimingEvidence':'production/encoded-cue-samples.json',
 'scene15Opening':'이제 완성한 캐릭터 옆에 배경을 놓아 보겠습니다.',
 'scene28Playback':'Native atlas timing followed by sequential individual frames at2Hz, including last→first wrap.',
 'humanListening':'pending'
}
plan['footageClassification'].update(bodySeconds=tm['duration']-12,actualCommercialGameplaySeconds=0,actualToolUiRecordingSeconds=0,explanationAndActualExportCompositionSeconds=tm['duration']-12,quotaApplied=False)
save(P/'planning/production-plan.json',plan)
m=read(P/'project.json')
m['editing'].update(actualGameplaySeconds=0,actualCommercialGameplaySeconds=0,actualDevelopmentFootageSeconds=0,actualExplanationSeconds=tm['duration']-12,actualGameplayShare=0,timingStatus='final-encoded-verified')
m['editing']['exampleInterleaving']['reviewStatus']='Actual exported outputs and explanatory diagrams inspected across30encoded scenes; no gameplay quota for this practical-tool scope.'
m['editing']['explanationStyle']='research-black-v1; actual pixel exports, diagrams and speech-aligned overlays'
m['editing']['exampleExpansion']['planningFormula']='not-applicable: approved tool-workflow exception'
m['editing']['gameExampleSourcePolicy']['actualExistingGameFootageRequired']=False
m['editing']['gameExampleSourcePolicy']['scope']='not-applicable-to-approved-tool-workflow-exception; no commercial gameplay used'
m['audio']['lectureDefaults']['comparisonSampleStatus']='No original gameplay or added BGM; current narration-only mix technically verified, final human listening pending.'
m['paths']['narration']='projects/ai-2d-game-assets/production/local/narration-aligned.wav'
save(P/'project.json',m)
print(master['sha256'])
