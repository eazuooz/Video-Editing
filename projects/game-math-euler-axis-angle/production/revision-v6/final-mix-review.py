"""Once-only ASR evidence from the actual complete V6 captioned MP4 audio.

The whole encoded audio is decoded once to preserved48k stereo FLOAT WAV.
Scene reads from that WAV cover every body frame, including inserted holds.
Only ASR input is downmixed/resampled to16k; no source PCM ASR is repeated.
No similarity threshold, spelling heuristic or successful ASR approves speech.
"""
from pathlib import Path
import argparse,difflib,hashlib,importlib.util,json,math,os,subprocess,sys,time,uuid
import psutil

H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v6_final_mix_approved_asr',H/'voice-review.py')
approved_asr=importlib.util.module_from_spec(spec);spec.loader.exec_module(approved_asr)
v=approved_asr.v
R,P,LEASE=v.R,v.P,v.LEASE
O=P/'production/local/revision-v6';BASE=O/'qa/final-mix-asr'
ASR_CAP_MIB=approved_asr.ASR_CAP_MIB
ASR_MIN_FREE_MIB=approved_asr.ASR_MIN_FREE_MIB
PYTHON=R/'qwen3-tts/.venv/Scripts/python.exe'
CONFIG={'model':'openai/whisper-large-v3-turbo','modelResolver':'voice-review.py:model_path; existing offline files only','localFilesOnly':True,'dtype':'float16','device':'cuda:0','attention':'eager','chunkLengthSeconds':25,'strideSeconds':3,'batchSize':1,'language':'korean','task':'transcribe','timestamps':'word','prompt':None,'asrSampleRate':16000,'conversion':'exact48k stereo scene range -> arithmetic channel mean -> scipy.resample_poly(1,3); no gain/fade/time stretch'}

def norm(s):
 import re
 return re.sub('[^a-z0-9가-힣]','',s.lower())
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def proof(p):return {'file':rel(p),'sha256':v.sha(p)}
def obj_sha(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()
def selected():
 c=v.read(R/'shared/publishing/video-production-control.json')
 assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def run(args,log):
 cp=subprocess.run(args,cwd=R,capture_output=True)
 log.parent.mkdir(parents=True,exist_ok=True);log.write_bytes(cp.stderr)
 assert cp.returncode==0,cp.stderr.decode(errors='replace')[-2500:]
 return cp
def model_identity():
 local=approved_asr.model_path();assert PYTHON.exists()
 names=['model.safetensors','config.json','generation_config.json','preprocessor_config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','added_tokens.json','merges.txt','normalizer.json','vocab.json']
 required=['model.safetensors','config.json','preprocessor_config.json','tokenizer_config.json']
 assert all((local/name).exists() for name in required),'The same approved offline model/processor files must exist'
 files=[local/name for name in names if (local/name).exists()]
 return {'configuration':CONFIG,'resolvedModelPath':str(local.resolve()),'resolver':proof(H/'voice-review.py'),'configSha256':v.sha(local/'config.json'),'files':[{'name':f.name,'file':str(f.resolve()),'sha256':v.sha(f),'bytes':f.stat().st_size} for f in files]}

def inference_identity(identity):
 # Allocation limits, resolver code hashes and cache paths do not change
 # the model/inference result. Keep successful recognition reusable when
 # only memory safety or provenance changes.
 return {'configuration':identity['configuration'],'configSha256':identity['configSha256'],'modelFiles':[{'name':x.get('name',Path(x['file']).name),'sha256':x['sha256']} for x in identity['files']]}

def check_model_only():
 local=approved_asr.model_path()
 identity={'resolvedModelPath':str(local.resolve()),'configSha256':v.sha(local/'config.json'),'weightBytes':(local/'model.safetensors').stat().st_size,'modelAndProcessorFilesExist':all((local/name).exists() for name in ['model.safetensors','config.json','preprocessor_config.json','tokenizer_config.json','tokenizer.json']),'resolverReusedDirectly':'voice-review.py:model_path','localFilesOnly':True,'modelLoaded':False,'asrExecuted':False,'gpuQueriedOrOpened':False}
 source_execution=v.O/'source-asr-execution.json'
 if source_execution.exists():
  source=v.read(source_execution)
  if 'offlineModelPath' in source:
   assert Path(source['offlineModelPath']).resolve()==local.resolve()
   assert source['offlineModelConfigSha256']==identity['configSha256']
   identity['samePathAndConfigAsSourceAsrExecution']=True
 assert identity['modelAndProcessorFilesExist']
 print(json.dumps(identity,ensure_ascii=False,indent=2))

def scene_ranges(timeline):
 assert timeline['revision']=='article-flow-v6' and timeline['slug']==P.name
 assert timeline['fps']==60 and timeline['introFrames']==120 and timeline['outroFrames']==600
 assert timeline['sceneCount']==len(timeline['scenes'])==41 and timeline['lineCount']==250
 rows=[];cursor=timeline['introFrames']
 for s in timeline['scenes']:
  assert s['startFrame']==cursor and s['endFrame']==s['startFrame']+s['frames']
  rate=s['sampleRate'];assert rate==24000
  segments=[]
  for part in s['voiceSegments']:
   a,b,d=[part[k] for k in ['sourceSampleStart','sourceSampleEnd','destinationSampleStart']]
   segments.append({'sourceStartSample':a,'sourceEndSample':b,'sourceSampleRate':rate,'sceneDestinationStartSample24k':d,'globalStartSample48k':s['startFrame']*800+d*2,'globalEndSample48k':s['startFrame']*800+(d+b-a)*2,'globalStartSeconds':s['startFrame']/60+d/rate,'globalEndSeconds':s['startFrame']/60+(d+b-a)/rate})
  rows.append({'id':s['id'],'startFrame':s['startFrame'],'endFrame':s['endFrame'],'startSample':s['startFrame']*800,'endSample':s['endFrame']*800,'sampleRate':48000,'startSeconds':s['startFrame']/60,'endSeconds':s['endFrame']/60,'sourceVoiceFile':s['rawVoiceFile'],'sourceVoiceSha256':s['rawVoiceSha256'],'sourceVoiceSampleRate':rate,'sourceToGlobalSegments':segments,'lineOffsets':[{'line':x['line'],'sourceRawStart':x['rawStart'],'sourceRawEnd':x['rawEnd'],'sceneStartSeconds':x['start'],'sceneEndSeconds':x['end'],'globalStartSeconds':s['startFrame']/60+x['start'],'globalEndSeconds':s['startFrame']/60+x['end']} for x in s['lines']]})
  cursor=s['endFrame']
 assert cursor==timeline['temporalContract']['outroStartFrame']
 assert sum(x['endSample']-x['startSample'] for x in rows)==(cursor-120)*800
 return rows

def decode_once(master,master_sha,timeline,folder):
 import numpy as np
 import soundfile as sf
 receipt=folder/'extraction.json';decoded=folder/'decoded-final-48k-stereo.wav'
 inputs={'captionedMasterFile':rel(master),'captionedMasterSha256':master_sha,'timelineSha256':v.sha(H/'timeline.json'),'audioStream':0,'decode':'native48k stereo FLOAT, no gain/filter/trim/padding'}
 if receipt.exists():
  old=v.read(receipt)
  assert old['inputs']==inputs and (R/old['decodedFile']).exists() and v.sha(R/old['decodedFile'])==old['decodedSha256'],'Different encoded extraction exists; preserve it, do not silently overwrite'
  return old
 assert not decoded.exists(),'Unreceipted decoded WAV preserved; inspect before retrying extraction'
 folder.mkdir(parents=True,exist_ok=True)
 probe=subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(master)],text=True)
 streams=json.loads(probe)['streams'];video=next(x for x in streams if x['codec_type']=='video');audio=next(x for x in streams if x['codec_type']=='audio')
 assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(1920,1080,'60/1',timeline['totalFrames']),'Final master is incomplete/stale'
 assert int(audio['sample_rate'])==48000 and int(audio['channels'])==2,'Do not silently resample the preserved level-review reference'
 assert abs(float(audio.get('start_time','0')))<=1/48000,'Nonzero encoded-audio start offset requires explicit timeline mapping; do not silently shift it to zero'
 run(['ffmpeg','-nostdin','-hide_banner','-loglevel','warning','-threads','2','-i',str(master),'-map','0:a:0','-vn','-sn','-dn','-c:a','pcm_f32le','-ar','48000','-ac','2','-rf64','auto',str(decoded)],folder/'decode.log')
 pcm=hashlib.sha256()
 with sf.SoundFile(decoded) as f:
  assert f.samplerate==48000 and f.channels==2 and f.subtype=='FLOAT'
  samples=f.frames
  for block in f.blocks(blocksize=480000,dtype='float32',always_2d=True):pcm.update(np.asarray(block,dtype='<f4').tobytes())
 expected=timeline['totalFrames']*800
 assert expected<=samples<=expected+2048,'Decoded audio must cover the video exactly apart from explicitly recorded AAC tail padding; never invent missing samples'
 data={**inputs,'schemaVersion':1,'inputs':inputs,'decodedFile':rel(decoded),'decodedSha256':v.sha(decoded),'decodedPcmSha256':pcm.hexdigest(),'sampleRate':48000,'channels':2,'decodedSamples':samples,'videoRangeSamples':expected,'bodyStartSample':120*800,'bodyEndSample':timeline['temporalContract']['outroStartFrame']*800,'encoderTailSamples':samples-expected,'tailPolicy':'Full actual decoded WAV retained. Samples beyond the video range are recorded, never hidden or used as invented speech.','sourceMasterDecodePasses':1,'decodeGainDb':0,'audioStreamMetadata':audio,'sceneRanges':scene_ranges(timeline),'levelReview':'Shared unchanged48k stereo FLOAT reference for source→stem→encoded continuity; actual listening and level comparison pending','humanListening':'pending'}
 v.save(receipt,data);return data

def asr_array(stream,row):
 import numpy as np
 from scipy.signal import resample_poly
 stream.seek(row['startSample']);data=stream.read(row['endSample']-row['startSample'],dtype='float32',always_2d=True)
 assert len(data)==row['endSample']-row['startSample'] and data.shape[1]==2
 source_sha=hashlib.sha256(np.asarray(data,dtype='<f4').tobytes()).hexdigest()
 mono=data.mean(axis=1,dtype=np.float32);raw=np.asarray(resample_poly(mono,1,3),dtype=np.float32)
 assert len(raw)==math.ceil(len(data)/3) and np.isfinite(raw).all()
 return raw,source_sha,hashlib.sha256(np.asarray(raw,dtype='<f4').tobytes()).hexdigest()

def prepare(master):
 import soundfile as sf
 selected();v.validate();timeline=v.read(H/'timeline.json')
 assert timeline['inputs']['koSha256']==v.sha(P/'script/revision-v6-article-flow/narration.ko.json')
 stat={'bytes':master.stat().st_size,'mtimeNs':master.stat().st_mtime_ns};master_sha=v.sha(master)
 folder=BASE/'masters'/master_sha;extraction=decode_once(master,master_sha,timeline,folder)
 assert stat=={'bytes':master.stat().st_size,'mtimeNs':master.stat().st_mtime_ns},'Master changed during preparation'
 identity=model_identity();model_hash=obj_sha(inference_identity(identity));spoken=v.read(H/'voice-input.ko.json');canonical=v.read(P/'script/revision-v6-article-flow/narration.ko.json')
 source={x['id']:x for x in spoken['scenes']};display={x['id']:x for x in canonical['scenes']}
 mix=v.read(O/'audio-build.json');assert mix['inputs']['timelineSha256']==v.sha(H/'timeline.json')
 assert mix['separatelyAddedBgm'] is False and mix['sampleRate']==48000 and mix['channels']==2 and mix['totalFrames']==timeline['totalFrames']
 scene_rows=[]
 with sf.SoundFile(R/extraction['decodedFile']) as stream:
  for row in extraction['sceneRanges']:
   raw,pcm_hash,asr_hash=asr_array(stream,row);key=obj_sha({'scenePcm48kSha256':pcm_hash,'asrMono16kSha256':asr_hash,'modelConfigurationSha256':model_hash})
   cache=BASE/'asr-cache'/f'{key}.json'
   scene_rows.append({**row,'encodedScenePcm48kSha256':pcm_hash,'asrMono16kSha256':asr_hash,'asrSamples':len(raw),'asrSampleRate':16000,'asrDurationSeconds':len(raw)/16000,'cacheFile':rel(cache),'cacheKey':key,'expectedSpoken':' '.join(source[row['id']]['lines']),'expectedCanonicalNarration':' '.join(display[row['id']]['lines']),'expectedSpokenParagraphs':source[row['id']]['lines'],'expectedCanonicalParagraphs':display[row['id']]['lines']})
 inputs={'master':{**proof(master),**stat},'timeline':proof(H/'timeline.json'),'extraction':proof(folder/'extraction.json'),'spokenInput':proof(H/'voice-input.ko.json'),'canonicalNarration':proof(P/'script/revision-v6-article-flow/narration.ko.json'),'finalMixReceipt':proof(O/'audio-build.json'),'voiceRuntime':proof(H/'voice-render.py'),'approvedSourceAsrRuntime':proof(H/'voice-review.py'),'implementation':proof(Path(__file__))}
 data={'schemaVersion':1,'revision':'article-flow-v6','inputs':inputs,'modelIdentity':identity,'modelConfigurationSha256':model_hash,'recognitionCacheIdentity':inference_identity(identity),'memorySafety':{'allocatorCapMiB':ASR_CAP_MIB,'minimumFreeBeforeLoadMiB':ASR_MIN_FREE_MIB,'clearOnlyOwnUnusedCudaCacheAfterNewSuccessfulScene':True,'cachedSceneLoadsModelOrClearsCache':False,'partOfRecognitionCacheKey':False},'extractionFile':rel(folder/'extraction.json'),'decodedFile':extraction['decodedFile'],'decodedSha256':extraction['decodedSha256'],'decodedPcmSha256':extraction['decodedPcmSha256'],'sceneCount':41,'scenes':scene_rows,'expectedParagraphCount':sum(len(x['expectedSpokenParagraphs']) for x in scene_rows),'bodyCoverage':'Every main-body sample from original2s branding end through the exact membership outro start, scene ranges contiguous and nonoverlapping','levelReference':{'narrationStem':mix['narrationStem'],'gameStem':mix['gameStem'],'losslessMix':mix['audioMix'],'encodedAac':mix['encodedAudio'],'constantProgramGainDb':mix['constantProgramGainDb'],'referenceReceiptSha256':v.sha(O/'audio-build.json'),'actualGameFrames':sum(c['frames'] for c in timeline['cuts']),'separatelyAddedBgm':False,'actualEncodedVsReferenceLevelComparison':'pending inventory CPU review using this same decoded48k WAV'},'sourcePcmAsrRepeated':False,'humanWholeListening':'pending','directFullTextReview':'pending','automaticSpeechPass':False}
 assert data['expectedParagraphCount']==250 and data['levelReference']['actualGameFrames']==1074
 path=folder/'preparation.json';v.save(path,data);return path,data

def cached(row,model_hash):
 file=R/row['cacheFile']
 if not file.exists():return None
 old=v.read(file)
 assert old['cacheKey']==row['cacheKey'] and old['audioPcm48kSha256']==row['encodedScenePcm48kSha256'] and old['asrMono16kSha256']==row['asrMono16kSha256'] and old['modelConfigurationSha256']==model_hash and old['status']=='recognized-evidence-only','Invalid ASR cache; do not overwrite/repeat it'
 return old

def text_review(row,recognized):
 a,b=norm(row['expectedSpoken']),norm(recognized['text']);match=difflib.SequenceMatcher(None,a,b,autojunk=False)
 words=[]
 for item in recognized['words']:
  original=item['timestamp'];start,end=original
  words.append({'text':item['text'],'sceneTimestamp':original,'globalTimestamp':[None if t is None else row['startSeconds']+t for t in original],'globalSample48kApproximate':[None if t is None else row['startSample']+round(t*48000) for t in original],'timestampInterpretation':'ASR-estimated word boundaries, not measured phoneme/sample truth','timestampFlag':None if start is not None and end is not None and 0<=start<end<=row['asrDurationSeconds']+.1 else 'missing/zero/out-of-range timestamp; inspect context'})
 return {**row,'recognized':recognized['text'],'words':words,'asrCacheSha256':v.sha(R/row['cacheFile']),'similarityAdvisoryOnly':match.ratio(),'normalizedDifferences':[{'kind':tag,'expected':a[i:j],'recognized':b[k:l],'expectedOffsets':[i,j],'recognizedOffsets':[k,l]} for tag,i,j,k,l in match.get_opcodes() if tag!='equal'],'rawTextDiff':list(difflib.ndiff([row['expectedSpoken']],[recognized['text']])),'directFullTextReview':'pending','humanContextListening':'pending','automaticSpeechPass':False}

def aggregate(preparation):
 p=v.read(preparation);rows=[];missing=[]
 for row in p['scenes']:
  result=cached(row,p['modelConfigurationSha256'])
  if result is None:missing.append(row['id'])
  else:rows.append(text_review(row,result))
 report={'schemaVersion':1,'revision':'article-flow-v6','kind':'Whole current encoded-final-mix ASR evidence, never automatic speech/listening approval','preparation':proof(preparation),'inputs':p['inputs'],'extractionFile':p['extractionFile'],'decodedFile':p['decodedFile'],'decodedSha256':p['decodedSha256'],'decodedPcmSha256':p['decodedPcmSha256'],'modelIdentity':p['modelIdentity'],'completeAsrEvidence':not missing,'sceneCount':len(rows),'expectedScenes':41,'missingScenes':missing,'scenes':rows,'levelReference':p['levelReference'],'fullMainBodyCovered':not missing,'sourcePcmAsrRepeated':False,'allExpectedAndRecognizedTextRetained':True,'directFullTextReview':'pending','humanWholeListening':'pending','automaticSpeechPass':False}
 output=preparation.parent/'final-mix-asr-review.json';v.save(output,report);return missing,output

def worker(token,preparation,retry_failed=False):
 import soundfile as sf
 selected();v.validate();lease=v.read(LEASE);me=psutil.Process();owner=lease['coordinator']
 assert lease['token']==token and lease['project']==P.name and lease['purpose']=='one current encoded-final-mix ASR evidence batch'
 assert any(x.pid==owner['pid'] and abs(x.create_time()-owner['createTime'])<.02 for x in [me,*me.parents()])
 p=v.read(preparation);assert p['inputs']['implementation']['sha256']==v.sha(Path(__file__))
 assert p['inputs']['timeline']['sha256']==v.sha(H/'timeline.json')
 decoded=R/p['decodedFile'];assert v.sha(decoded)==p['decodedSha256']
 transcriber=None
 with sf.SoundFile(decoded) as stream:
  for row in p['scenes']:
   selected();existing=cached(row,p['modelConfigurationSha256'])
   if existing is not None:print('Reused identical encoded-scene ASR cache',row['id'],flush=True);continue
   raw,pcm_hash,asr_hash=asr_array(stream,row)
   assert pcm_hash==row['encodedScenePcm48kSha256'] and asr_hash==row['asrMono16kSha256']
   file=R/row['cacheFile'];file.parent.mkdir(parents=True,exist_ok=True);attempt=file.with_suffix('.attempt.json')
   if attempt.exists():assert retry_failed and v.read(attempt)['status']=='failed','Prior incomplete recognition is preserved. Inspect the failure before an explicit --retry-failed; successful cache is never rerun.'
   if transcriber is None:
    # Recheck current free memory immediately before the first model load.
    # Do not demand the unloaded-model threshold again after our model is
    # resident; that would misclassify our own allocation as foreign use.
    free,total,util=v.gpu();assert free>=ASR_MIN_FREE_MIB
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(ASR_CAP_MIB*1048576/torch.cuda.get_device_properties(0).total_memory)
    local_model=approved_asr.model_path()
    assert local_model.resolve()==Path(p['modelIdentity']['resolvedModelPath']).resolve()
    assert v.sha(local_model/'config.json')==p['modelIdentity']['configSha256']
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local_model),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cuda:0')
    processor=AutoProcessor.from_pretrained(str(local_model),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
   state={'status':'running','cacheKey':row['cacheKey'],'scene':row['id'],'pid':me.pid,'startedAt':time.time(),'preparationSha256':v.sha(preparation)};v.save(attempt,state)
   try:
    print('Recognizing actual encoded final-mix scene once',row['id'],flush=True)
    result=transcriber({'raw':raw,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    v.save(file,{'status':'recognized-evidence-only','cacheKey':row['cacheKey'],'audioPcm48kSha256':pcm_hash,'asrMono16kSha256':asr_hash,'modelConfigurationSha256':p['modelConfigurationSha256'],'configuration':CONFIG,'text':result['text'],'words':result['chunks'],'firstMasterSha256':p['inputs']['master']['sha256'],'firstScene':row['id'],'recognizedAt':time.time(),'automaticSpeechPass':False})
    state.update(status='complete',endedAt=time.time(),cacheSha256=v.sha(file));v.save(attempt,state)
    del result,raw
    # Only this finished scene's unused allocator cache is released. Keep
    # model, dtype, chunk/stride, batch and prompt unchanged; touch no
    # foreign process or successful recognition cache.
    torch.cuda.empty_cache()
   except BaseException as error:
    state.update(status='failed',endedAt=time.time(),error=repr(error));v.save(attempt,state);raise
   aggregate(preparation)
 missing,output=aggregate(preparation);assert not missing
 print('All41 actual encoded scenes recognized; full text/context/listening pending.',rel(output),flush=True)

def acquire(preparation,data,retry_failed=False):
 missing,output=aggregate(preparation)
 if not missing:print('Reused all exact encoded-scene ASR caches; no GPU/model loaded.',rel(output));return
 assert not LEASE.exists(),'Existing GPU lease is preserved; wait for TTS/other owner to finish'
 free,total,util=v.gpu();assert free>=ASR_MIN_FREE_MIB
 family={x.pid for x in [psutil.Process(),*psutil.Process().parents()]}
 clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 assert not any('python' in line.lower() and int(line.split(',')[0]) not in family for line in clients.splitlines()),'Foreign GPU Python compute remains untouched'
 me=psutil.Process();token=str(uuid.uuid4());state={'token':token,'project':P.name,'state':'final_mix_asr_running','purpose':'one current encoded-final-mix ASR evidence batch','coordinator':{'pid':me.pid,'createTime':me.create_time()},'foreignProcessesPaused':[],'gpuBefore':{'freeMiB':free,'totalMiB':total,'utilization':util},'allocatorCapMiB':ASR_CAP_MIB,'minimumFreeMiB':ASR_MIN_FREE_MIB,'preparationSha256':v.sha(preparation),'startedAt':time.time()}
 with LEASE.open('x',encoding='utf-8') as f:json.dump(state,f)
 code=1
 try:
  cmd=[str(PYTHON),'-u','-X','utf8',str(Path(__file__).resolve()),'--worker',token,'--preparation',str(preparation)]
  if retry_failed:cmd.append('--retry-failed')
  with (preparation.parent/'asr-worker.log').open('ab') as log:
   process=subprocess.Popen(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state.update(workerPid=process.pid,status='running');v.save(preparation.parent/'asr-execution.json',state);code=process.wait()
 finally:
  state.update(status='recognized-evidence-ready-for-full-text-review' if code==0 else 'failed',returnCode=code,endedAt=time.time(),foreignProcessesRestored=[]);v.save(preparation.parent/'asr-execution.json',state)
  if LEASE.exists() and v.read(LEASE).get('token')==token:LEASE.unlink()
 assert code==0,f'Final-mix ASR worker failed{code}; preserve successful caches and inspect its log'

def self_test():
 example={'id':'v6-01','cacheFile':'not-read','expectedSpoken':'칠백이십 도에서 사십오 도','startSeconds':2,'startSample':96000,'asrDurationSeconds':4}
 assert norm('X 축, 720도!')=='x축720도'
 a,b=norm(example['expectedSpoken']),norm('칠백이십 도에서 사십오 도');assert difflib.SequenceMatcher(None,a,b).ratio()==1
 assert obj_sha({'audio':'same','model':'same'})==obj_sha({'model':'same','audio':'same'})
 assert obj_sha({'audio':'changed','model':'same'})!=obj_sha({'audio':'same','model':'same'})
 assert ASR_CAP_MIB==6656 and ASR_MIN_FREE_MIB==7168
 identity={'configuration':CONFIG,'configSha256':'c','resolver':{'sha256':'old-safety-code'},'resolvedModelPath':'old-path','files':[{'name':'model.safetensors','file':'old-path/model.safetensors','sha256':'same-weights'}]}
 before=obj_sha(inference_identity(identity));identity['resolver']['sha256']='new-memory-safety-code';identity['resolvedModelPath']='other-cache-path'
 assert before==obj_sha(inference_identity(identity)),'Memory/provenance changes must preserve successful ASR cache'
 schema={'captionedMasterSha256':'pending','decodedFile':'pending','decodedSha256':'pending','sampleRate':48000,'channels':2,'decodedSamples':None,'bodyStartSample':96000,'bodyEndSample':None,'humanListening':'pending','automaticSpeechPass':False}
 assert not schema['automaticSpeechPass'] and schema['bodyStartSample']==120*800
 scenes=[]
 for i in range(41):
  start=120+i*6000
  scenes.append({'id':f'v6-{i+1:02}','startFrame':start,'endFrame':start+6000,'frames':6000,'sampleRate':24000,'rawVoiceFile':'no-file-opened','rawVoiceSha256':'0'*64,'voiceSegments':[{'sourceSampleStart':0,'sourceSampleEnd':24000,'destinationSampleStart':1200}],'lines':[{'line':1,'rawStart':0,'rawEnd':1,'start':.05,'end':1.05}]})
 synthetic={'revision':'article-flow-v6','slug':P.name,'fps':60,'introFrames':120,'outroFrames':600,'sceneCount':41,'lineCount':250,'scenes':scenes,'temporalContract':{'outroStartFrame':246120}}
 rows=scene_ranges(synthetic);assert len(rows)==41 and rows[0]['startSample']==96000 and rows[-1]['endSample']==246120*800
 assert rows[0]['sourceToGlobalSegments'][0]['globalStartSample48k']==98400
 scenes[2]['startFrame']+=1
 try:scene_ranges(synthetic)
 except AssertionError:pass
 else:raise AssertionError('A gap in full-body sample coverage must fail')
 print('CPU schema/cache/difference tests passed; no master, media, ASR, model or GPU job opened.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--master',type=Path,default=O/'euler-captioned.mp4');ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--gpu-approved',action='store_true');ap.add_argument('--worker');ap.add_argument('--preparation',type=Path);ap.add_argument('--retry-failed',action='store_true');ap.add_argument('--self-test',action='store_true');ap.add_argument('--check-model',action='store_true');args=ap.parse_args()
 if args.self_test:return self_test()
 if args.check_model:return check_model_only()
 if args.worker:
  assert args.preparation;return worker(args.worker,args.preparation,args.retry_failed)
 assert args.prepare_only or args.gpu_approved,'Choose CPU --prepare-only after master ready, or root-allocated --gpu-approved. This tool never starts automatically.'
 preparation,data=prepare(args.master)
 if args.prepare_only:print('Shared encoded48k reference ready; ASR not started.',rel(preparation));return
 acquire(preparation,data,args.retry_failed)

if __name__=='__main__':main()
