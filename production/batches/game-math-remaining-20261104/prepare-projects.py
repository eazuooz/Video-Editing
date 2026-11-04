"""Prepare manifests for the exact authorized thirteen; no TTS/render/platform side effects."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
batch=read(BASE/'batch.json')
auth=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
assert auth['productionAllowedNow'] and len(batch['items'])==13
for item in batch['items']:
    slug=item['slug'];project=ROOT/'projects'/slug
    tts={'engine':'qwen3-tts','language':'Korean','reference':'shared/voice-reference/reference-15-35s.wav','referenceText':'shared/voice-reference/reference-15-35s.ko.txt','model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base','outputDir':f'projects/{slug}/production/local/audio-v1','filenameStem':'narration','renderMode':'scene','lineGapSeconds':0.28,'sceneGapSeconds':0.28,'maxNewTokens':2048,'maxRenderAttempts':1,'edgeFadeSeconds':0.006,'tailRatioThreshold':0.07,'tailDecayMsThreshold':70,'gpuMinimumFreeMiB':8192,'gpuProfileReason':'Approved local1.7B BF16 voice, paragraph-as-scene batch1; root must verify game use ended and no active render. Idle inspected editors preserved; require10240MiB free and cap allocator7680MiB. Record actual peak; fail owned job without terminating others.','lineLevelEqualization':{'targetSpeechFrameMedianDbfs':-22,'frameMs':50,'gateBelowPeakDb':25,'maxGainDb':12,'record':'line-levels.json'},'status':'prepared-not-generated','paidApi':False}
    paths={'script':f'projects/{slug}/script/narration.ko.json','scriptEn':f'projects/{slug}/script/narration.en.json'}
    edit={'narrationPlacement':'continuous-across-example-and-explanation','exampleSeconds':0}
    manifest=project/'project.json'
    if not manifest.exists():
        save(manifest,{'schemaVersion':1,'slug':slug,'titles':{'ko':item['title']},'status':'authorized-preproduction','batch':BASE.name,'startGate':{'productionAllowedNow':True,'authorizationKey':'explicitMathRemainingBatch20261104'},'video':{'width':1920,'height':1080,'fps':60},'paths':paths,'editing':edit,'tts':tts,'audio':{'addedBackgroundMusic':False,'gameAudio':'Preserve rights-cleared original game sound with standard narration ducking'},'lecture':{'sections':item['sections'],'fixedRuntime':None,'fixedGameplayShare':None},'publishing':{'allowedNow':False,'localFinalReviewRequired':True}})
    voice=project/'production/tts-manifest.json'
    if not voice.exists():save(voice,{'schemaVersion':1,'slug':slug,'paths':paths,'editing':edit,'tts':tts})
    plan=project/'planning/production-plan.json'
    if not plan.exists():save(plan,{'schemaVersion':1,'episode':item['id'],'batch':'production/batches/'+BASE.name+'/batch.json','sourceNotion':item['sourceNotion'],'sections':item['sections'],'sourceSnapshots':'production/batches/'+BASE.name+'/sources/index.json','sourceAudit':'planning/source-audit.json','footageAudit':'planning/footage-audit.json','unityPlan':'planning/unity-plan.json','stage':'source-acquired-full-audit-pending','sourceFinal':False,'narrationFinal':False,'sceneBindingsFinal':False,'learningSteps':[],'teachingBeats':[],'boundaryLinks':[],'terminology':[]})
    checkpoint=project/'production/checkpoint.json'
    if not checkpoint.exists():save(checkpoint,{'stage':'source-acquired-full-audit-pending','runningCostlyJobs':[],'nextAction':'Read all selected source paragraphs, preserve source learning order and inspect concept-matched footage before final script.'})
    ledger=project/'production/review-ledger.json'
    if not ledger.exists():save(ledger,{'schemaVersion':1,'project':slug,'checks':[],'localReviewReady':False,'humanReview':{'status':'not-requested-no-master'}})
print('13 authorized project manifests and paragraph voice configurations prepared; no model or render launched.')
