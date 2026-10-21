"""Prepare exact approved paragraphs and unchanged Qwen identities; CPU only."""
from pathlib import Path
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_voice_prepare_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def main():
 c.selected();script=c.read(c.SCRIPT);en_file=c.P/'script/revision-v8-orientation-matrix/narration.en.json';en=c.read(en_file)
 assert len(script['scenes'])==len(en['scenes'])==13
 voice=dict(revision='orientation-matrix-v8',approvedDisplayScript=c.rel(c.SCRIPT),approvedDisplayScriptSha256=c.APPROVED,pronunciationAliases=[],scenes=[])
 for ko,eng in zip(script['scenes'],en['scenes']):
  assert ko['id']==eng['id']and len(ko['paragraphs'])==len(eng.get('paragraphs',eng.get('lines',[])))
  voice['scenes'].append(dict(id=ko['id'],title=ko['title'],lines=ko['paragraphs']))
 assert sum(len(x['lines'])for x in voice['scenes'])==76
 target=H/'voice-input.json'
 if target.exists():assert c.read(target)==voice
 else:c.save(target,voice)
 prior=c.read(c.P/'planning/revision-v7-two-part/part-01-audio-plan.json')
 tts=c.read(c.P/'production/revision-v7-part1/voice-tts-manifest.json')['tts']
 tts={k:v for k,v in tts.items()if k not in ['outputDir','renderMode','sceneGapSeconds','edgeFadeSeconds']}
 tts.update(renderMode='paragraph-takes',lineGapSeconds=.28,sceneGapSeconds=0,edgeFadeSeconds=0,outputDir=c.rel(c.O),batchSize=1,
  lineLevelEqualization=dict(targetSpeechFrameMedianDbfs=-22,frameMs=50,gateBelowPeakDb=25,maxGainDb=12,method='One constant gain per complete paragraph; no syllable flattening, trimming or speech fades'))
 manifest=H/'voice-tts-manifest.json';c.save(manifest,dict(revision='orientation-matrix-v8',tts=tts))
 paths=dict(approvedKo=c.SCRIPT,approvedEn=en_file,authorization=H/'authorization.json',voiceInput=target,ttsManifest=manifest,
  reference=c.R/tts['reference'],referenceText=c.R/tts['referenceText'],ttsModelConfig=c.R/tts['model']/'config.json',ttsGenerationConfig=c.R/tts['model']/'generation_config.json')
 immutable={k:dict(file=c.rel(p),sha256=c.sha(p))for k,p in paths.items()}
 identity=hashlib.sha256(json.dumps(dict(tts=tts,inputs={k:immutable[k]for k in ['reference','referenceText','ttsModelConfig','ttsGenerationConfig']}),sort_keys=True).encode()).hexdigest()
 plan=dict(schemaVersion=1,revision='orientation-matrix-v8',approvedScriptSha256=c.APPROVED,sceneCount=13,paragraphCount=76,
  identitySha256=identity,resources=prior['resources'],asrIdentity=prior['asrIdentity'],immutableInputs=immutable,
  generation='Each approved complete paragraph exactly once, same Qwen1.7B/ref/prompt; no fabricated greeting, speedup or observation holds.',
  sourceAsr='All13 actually assembled current scene WAVs once; expected text is not supplied to recognizer. Direct full76paragraph review follows.',
  pcm='Raw paragraph FLOAT PCM preserved; scene FLOAT PCM contains only constant per-paragraph gain and recorded .28s line gaps. No clipping or automatic retakes.',
  downstreamMix='Only a whole-program loudness gain follows these line levels; no further paragraph normalization or voice ducking. Actual peak/headroom must be measured.',
  timelineInterface=dict(sampleRate=24000,scenes='audio/tts-current.json scenes[id,file,sha256,samples,sampleRate,lines]',
   paragraphOrigins='lines[line,takeFile,takeSha256,startSample,endSample,gapBeforeSamples,gainDb]',
   alignment='audio/source-alignment.json scenes[].lines[line,rawStart,rawEnd,characterStarts,characterEnds] at same exact scene sample clock',
   noMandatorySceneGap=True,voiceSpeed=1,addedObservationSilenceSamples=0),humanListening='pending actual files')
 c.save(H/'voice-plan.json',plan);c.O.mkdir(parents=True,exist_ok=True)
 print(json.dumps(dict(scenes=13,paragraphs=76,voiceInputSha256=c.sha(target),planSha256=c.sha(H/'voice-plan.json'),gpuJobStarted=False)))
if __name__=='__main__':main()
