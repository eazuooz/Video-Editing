"""CPU-only immutable voice inputs and finite Part1 execution plan."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_audio_common',H/'audio-common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
def proof(path):return dict(file=c.rel(path),sha256=c.sha(path))
def main():
 c.selected(require_full=False)
 source=c.P/'script/revision-v7-two-part/part-01.ko.json'
 auth=H/'authorization.json';authority=c.read(auth)
 assert authority['selectedPart']==1 and authority['scriptApproved'] and authority['fullProductionAuthorized']
 assert c.sha(source)==authority['approvedScriptSha256']
 script=c.read(source);assert len(script['scenes'])==21 and sum(len(s['lines']) for s in script['scenes'])==135
 c.O.mkdir(parents=True,exist_ok=True)
 voice=copy.deepcopy(script)
 # Approved KO is already speech-safe Korean, including axis names and numerals.
 # No global replacements and no editorial sentence changes.
 c.save(H/'voice-input.json',voice)
 reference=c.R/'shared/voice-reference/reference-15-35s.wav';reftext=reference.with_suffix('.ko.txt')
 assert c.sha(reference)=='f0d59e79530ffc06bf0eb1541d31040042c6f108f2222e4991669748624ee089'
 assert c.sha(reftext)=='a22dbc1cc8a7d5bcaa8a412b5212439b86b51035bcaf692622374db48cffec20'
 model=c.R/'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base'
 manifest=dict(schemaVersion=1,revision='v7-part1',part=1,slug=c.P.name,paths=dict(script=c.rel(H/'voice-input.json')),tts=dict(engine='qwen3-tts',model=c.rel(model),reference=c.rel(reference),referenceText=c.rel(reftext),language='Korean',outputDir=c.rel(c.O),renderMode='scene',sceneGapSeconds=0,edgeFadeSeconds=0,maxRenderAttempts=1,maxNewTokens=4096,nonStreaming=True),executionState='prepared; root serialized TTS/source-ASR slot required')
 c.save(H/'voice-tts-manifest.json',manifest)
 oldscript=c.read(c.P/'production/revision-v6/voice-input.ko.json')
 oldtexts={' '.join(s['lines']):s['id'] for s in oldscript['scenes']}
 mapping=c.P/'production/local/revision-v6/voice/current-pcm.json';oldpcm=c.read(mapping)
 preserved=[dict(file=r['file'],sha256=r['sha256']) for r in oldpcm['scenes']]
 assert len(preserved)==41
 for item in preserved:assert c.sha(c.R/item['file'])==item['sha256']
 sp2=importlib.util.spec_from_file_location('v7_source_asr',H/'voice-review.py');asr=importlib.util.module_from_spec(sp2);sp2.loader.exec_module(asr)
 local=asr.model_path()
 asr_model=dict(model='openai/whisper-large-v3-turbo',resolvedPath=str(local.resolve()),configSha256=c.sha(local/'config.json'),weightsSha256=c.sha(local/'model.safetensors'),weightsBytes=(local/'model.safetensors').stat().st_size,weightsMtimeNs=(local/'model.safetensors').stat().st_mtime_ns,localFilesOnly=True)
 immutable=dict(approvedKo=proof(source),partAuthorization=proof(auth),voiceInput=proof(H/'voice-input.json'),ttsManifest=proof(H/'voice-tts-manifest.json'),reference=proof(reference),referenceText=proof(reftext),ttsModelConfig=proof(model/'config.json'),ttsGenerationConfig=proof(model/'generation_config.json'),priorCurrentPcmMapping=proof(mapping))
 identity=dict(referenceSha256=c.sha(reference),referenceTextSha256=c.sha(reftext),modelConfigSha256=c.sha(model/'config.json'),modelGenerationConfigSha256=c.sha(model/'generation_config.json'),dtype='bfloat16',batchSize=1,language='Korean',nonStreaming=True,maxNewTokens=4096,sampling='Existing model generation configuration; no style/speed invention')
 identity_sha=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
 scenes=[]
 for s in script['scenes']:
  text=' '.join(s['lines'])
  scenes.append(dict(id=s['id'],title=s['title'],paragraphCount=len(s['lines']),speechCharacters=len(text),textSha256=hashlib.sha256(text.encode()).hexdigest(),output=c.rel(c.O/'chunks'/(s['id']+'-scene.wav')),byteEquivalentPriorWholeScene=oldtexts.get(text),newContinuousSceneRequired=text not in oldtexts))
 memory_proof=c.P/'production/local/revision-v6/qa/preparation/whisper-encoder-retention-cpu-review.json'
 plan=dict(schemaVersion=1,part=1,revision='v7-part1',createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='CPU preparation complete; GPU batch not started by preparation',immutableInputs=immutable,identity=identity,identitySha256=identity_sha,resources=dict(tts=dict(allocatorCapMiB=6144,minimumFreeMiB=7168),sourceAsr=dict(allocatorCapMiB=4608,minimumFreeMiB=5120),maximumConcurrentModels=1,preloadStableReads=2,maximumPreloadWaitSeconds=45),asrIdentity=asr_model,asrConfiguration=asr.CONFIG,asrMemoryProof=proof(memory_proof),asrMemoryPolicy='Same eager FP16 computation; process-local encoder output_attentions=False only, decoder cross-attentions retained. Existing CPU equivalence proof reused; actual new-source ASR still required.',pacing=dict(policy='article-faithful-teaching-pace-v1',revision='speech-synchronized-v2',renderUnit='One continuous PCM per script scene;135 paragraphs stay in context.',animationRequiresNarrationSilence=False,insertedObservationSilenceSamples=0,sceneJoin='Natural existing breaths; no automatic fixed scene gap or paragraph padding; exact joins after current PCM/word timing.',sourceSpeed=1,noGlobalSilenceTrim=True,noTimeStretch=True,humanPaceAndBreathing='pending'),audioMix=dict(addedBgm=False,narrationInitialTargetLufs=-16,gameInitialTargetLufs=-23,ducking=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280,makeup=1),amixNormalize=0,nativeSilentSources='Superflight and current MK8 source ranges stay genuinely silent; no synthetic replacement sound.'),qa=dict(sourceAsr='One current new-PCM full recognition batch; expected text never used as a recognition prompt. Preserve raw words/transcripts. Independent complete contexts only for ambiguous content.',sourceLevels='CPU speech-active400ms/100ms local levels and paragraph/scene joins; sustained>6dB and adjacent>3dB are review candidates, not automatic failures or automatic gain flattening.',gain='Preserve raw source samples. One scene gain where sufficient; sustained-decay corrections only on evidence-backed complete paragraph groups/quiet joins. No word compression.',finalMix='New final mix needs one complete encoded-ASR/full-text comparison and aligned source→stem→encoded continuity review; source ASR does not pass final mix.',reuse='Same approved voice identity and generic numerical/memory proof only. No old scene ASR/level/timing reused for rewritten speech; exact successful new chunks/caches never regenerated.',humanWholeListening='pending; measurements/ASR do not count as human listening.'),sceneCount=21,paragraphCount=135,totalSpeechCharacters=sum(s['speechCharacters'] for s in scenes),longestScene=max(scenes,key=lambda x:x['speechCharacters'])['id'],longestSceneCharacters=max(s['speechCharacters'] for s in scenes),exactWholeSceneReuseCount=sum(s['byteEquivalentPriorWholeScene'] is not None for s in scenes),scenes=scenes,preservedV6Pcm=preserved,execution=dict(tts='qwen3-tts/.venv/Scripts/python.exe -u -X utf8 '+c.rel(H/'voice-render.py')+' --gpu-approved',sourceAsr='qwen3-tts/.venv/Scripts/python.exe -u -X utf8 '+c.rel(H/'voice-review.py')+' --gpu-approved'),mediaJobsStartedByPreparation=0)
 c.save(c.P/'planning/revision-v7-two-part/part-01-audio-plan.json',plan)
 c.validate(require_full=False,preserve_pcm=True)
 print('Prepared21continuous scenes/135paragraphs;0exact whole-scene reuse; approved reference exact. No model loaded or audio job run.')
 print('Longest',plan['longestScene'],plan['longestSceneCharacters'],'characters; model max_new_tokens4096 remains the prior tested ceiling.')
if __name__=='__main__':main()

