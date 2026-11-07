"""06.02 raw103 -> accepted FLOAT mix clock proof; read-only unless --write.

This is sample-lineage acceptance, never mixed-ASR, listening or final review.
No FFmpeg, model, worker, audio modification or media generation is performed.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,sys,wave
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-06-02')
CAPTION_SHA='fec20b03156cff68fa80d5d2be56a0407634fcf3287e516bb70ff3ffa8413769'
AUDIO_SHA='a7692cdc0ca3fdda1916afa553a66c2d8d925878fe25579b9d35821d6990b1da'
AUDIO_VERIFY_SHA='db521babf1848861979a7580cd0a045540575f945909d99d2a7055433344f3b4'
SCHEMA='06-02-raw-mix-clock-proof-v2'
class Pending(RuntimeError):pass
def require(ok,message):
 if not ok:raise Pending(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pcm_sha(x):return hashlib.sha256(np.asarray(x,dtype='<f4').tobytes(order='C')).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def bound(q):
 p=Path(q['path']).resolve();require(p.is_file()and sha(p)==q.get('sha256'),'Changed or missing pinned input: '+str(p));return p
def read_float(path,rate,channels,frames):
 info=sf.info(path)
 require((info.samplerate,info.channels,info.frames,info.subtype)==(rate,channels,frames,'FLOAT'),'FLOAT sample format/clock differs: '+str(path))
 x,sr=sf.read(path,dtype='float32');require(sr==rate and x.shape==((frames,)if channels==1 else(frames,channels))and np.isfinite(x).all(),'Invalid FLOAT sample grid')
 return x
def raw_pcm(q):
 p=bound(q)
 with wave.open(str(p),'rb')as w:
  require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,24000,q['frames']),'Raw PCM16 component/header differs')
  data=w.readframes(w.getnframes())
 require(len(data)==q['frames']*2 and hashlib.sha256(data).hexdigest()==q['pcmSHA256'],'Raw PCM bytes differ')
 return data

def sample_lineage(timing,voice,mix,lines,folder,audio):
 """Verify actual sample contents, not only declared durations or file headers."""
 parts=timing.get('physicalComponents',[]);records=lines.get('components',[]);frames=voice['aggregateWav']['frames'];folder=Path(folder).resolve()
 require(len(parts)==len(records)==103 and len(timing.get('sentences',[]))==96,'Exactly103 physical and96 logical clocks required')
 require(timing.get('audioClock',{}).get('rawSampleRate')==24000 and timing['audioClock'].get('totalRawSamples')==frames,'Caption raw sample clock differs')
 require(lines.get('componentCount')==103 and lines.get('voiceFingerprint')==voice['fingerprint']and lines.get('rawCanonical')==voice['aggregateWav']and lines.get('rawRate')==24000 and lines.get('frames')==frames,'Line ledger raw identity differs')
 require(mix.get('selectedComponentCount')==103 and mix.get('rawVoiceFingerprint')==voice['fingerprint']and mix.get('rawVoice')==voice['aggregateWav']and mix.get('canonicalTiming')==voice['timing'],'Mix belongs to another raw voice clock')
 for obj in(lines,mix):
  require(obj.get('voiceOffsetSeconds')==0 and obj.get('insertedSamples')==0 and obj.get('trimmedSamples')==0 and obj.get('wordBoundariesShifted')is False and obj.get('compressorUsed')is False and obj.get('voiceSideDuck')is False,'Offset, inserted/trimmed samples, time change or voice compressor/duck is forbidden')
 require(lines.get('voiceSpeed')==1 and lines.get('amplitudeOnlyScalarCopies')is True and lines.get('normalizedCopyOnly')is True and lines.get('originalRawFilesUnchanged')is True,'Only scalar copies of preserved raw PCM are allowed')
 require(mix.get('uniformMixGainDb')==0 and mix.get('pcmLineage',{}).get('voiceOffsetSamples')==0 and mix['pcmLineage'].get('rawToPreparedSampleRatio')==[2,1]and mix['pcmLineage'].get('voiceSpeed')==1,'Exact zero-offset2x sample map required')
 require((mix.get('normalizedVoiceFrames'),mix.get('normalizedVoiceRate'),mix.get('mixFrames'),mix.get('mixRate'),mix.get('durationSeconds'))==(frames,24000,frames*2,48000,frames/24000),'Mix whole-grid rate/count/duration differs')
 require(mix.get('videoFrameTarget')==dict(fps=60,totalFrames=math.ceil(frames/400),noAudioTailPadding=True)and timing.get('totalFrames')==math.ceil(frames/400),'Final picture ceil must not add audio padding')
 inputs=[];proof_rows=[];normalized=[];raw_hash=hashlib.sha256();cursor=0
 def artifact(name):
  q=mix.get('artifacts',{}).get(name,{})
  require(q.get('file')==name and Path(name).name==name,'Canonical artifact name required')
  p=(folder/name).resolve();require(p.parent==folder and sha(p)==q.get('sha256'),'Audio artifact changed or escaped its version')
  inputs.append(pin(p));return p
 for part,row in zip(parts,records):
  q=part['rawWav'];a,b=part['startSample'],part['endSample'];n=b-a;sid=part['sceneId']
  require(type(a)is int and type(b)is int and a==cursor and n>0 and q['frames']==n,'Physical raw sample gap/reorder')
  expected=dict(sceneId=sid,paragraph=part['paragraph'],text=part['canonicalKo'],rawTake=q['path'],rawTakeSHA256=q['sha256'],rawPcmSHA256=q['pcmSHA256'],sourceSampleRange=[0,n],destinationSampleRange=[a,b],prepared48kSampleRange=[2*a,2*b],frames=n,rate=24000,startSeconds=a/24000,endSeconds=b/24000)
  require(all(row.get(k)==v for k,v in expected.items()),'Component scalar ledger source/order/sample range differs: '+sid)
  data=raw_pcm(q);raw_hash.update(data);raw=np.frombuffer(data,dtype='<i2').astype(np.float32)/32768.
  matched,measure=audio.base.match_paragraph(raw,24000,audio.PROFILE)
  require(row.get('normalization')==measure,'Accepted component scalar differs from current trusted calculation: '+sid)
  name=sid+'-normalized.wav';require(row.get('normalizedTake')==name,'Normalized source identity differs')
  p=artifact(name);require(row.get('normalizedTakeSHA256')==sha(p),'Normalized component file SHA differs')
  actual=read_float(p,24000,1,n)
  require(np.array_equal(actual,matched)and row.get('normalizedTakeFloat32PcmSHA256')==pcm_sha(actual),'Normalized component is not exact accepted whole-component scalar: '+sid)
  normalized.append(actual);inputs.append(pin(q['path']));proof_rows.append(dict(sceneId=sid,logicalSceneId=part['logicalSceneId'],rawSampleRange=[a,b],prepared48kSampleRange=[2*a,2*b],rawWav=pin(q['path']),rawPcmSHA256=q['pcmSHA256'],normalizedFloat32PcmSHA256=pcm_sha(actual),constantGainDb=measure['constantGainDb'],sampleCountPreserved=True));cursor=b
 require(cursor==frames and raw_hash.hexdigest()==voice['aggregateWav']['pcmSHA256'],'Raw components do not exactly reconstruct selected canonical PCM')
 require(hashlib.sha256(raw_pcm(voice['aggregateWav'])).hexdigest()==raw_hash.hexdigest(),'Actual raw aggregate differs from103 selected chunks')
 aggregate=np.concatenate(normalized);lineage=mix['pcmLineage'];p=artifact('narration-component-normalized.wav');actual=read_float(p,24000,1,frames)
 require(np.array_equal(actual,aggregate)and pcm_sha(actual)==lineage.get('normalized24kMonoFloat32SHA256'),'Normalized aggregate has changed samples/order or synthetic joins')
 # The reviewed producer resamples the WHOLE joined signal once, not each take.
 prepared=audio.base.stereo_voice(aggregate,24000);p=artifact('narration-prepared-stem.wav');actual=read_float(p,48000,2,frames*2)
 require(np.array_equal(actual,prepared)and pcm_sha(actual)==lineage.get('prepared48kStereoFloat32SHA256'),'Actual prepared stem is not the exact zero-offset reviewed2x whole-signal resample')
 gain_db=mix.get('voiceGlobalGain',{}).get('constantGainDb');require(isinstance(gain_db,(int,float))and not isinstance(gain_db,bool)and math.isfinite(gain_db),'Finite common voice scalar required')
 stem=prepared*10**(gain_db/20);p=artifact('narration-stem.wav');actual=read_float(p,48000,2,frames*2)
 require(np.array_equal(actual,stem)and pcm_sha(actual)==lineage.get('finalVoice48kStereoFloat32SHA256'),'Final voice samples are not the unchanged prepared clock plus declared uniform scalar')
 del aggregate,prepared,actual,normalized
 p=artifact('music-stem.wav');music=read_float(p,48000,2,frames*2);require(pcm_sha(music)==lineage.get('finalMusic48kStereoFloat32SHA256'),'Actual music PCM lineage differs')
 combined=stem+music;p=artifact('final-mix.wav');actual=read_float(p,48000,2,frames*2)
 require(Path(mix['mixWav']['path']).resolve()==p and mix['mixWav'].get('sha256')==sha(p)and np.array_equal(actual,combined)and pcm_sha(actual)==lineage.get('finalMix48kStereoFloat32SHA256'),'Final mix has an undeclared sample/time change')
 require((mix['mixWav']['sampleRate'],mix['mixWav']['channels'],mix['mixWav']['frames'],mix['mixWav']['subtype'])==(48000,2,frames*2,'FLOAT'),'Actual selected mix descriptor grid differs')
 return dict(componentCount=103,logicalGroupCount=96,rawSampleRate=24000,rawFrames=frames,mixSampleRate=48000,mixFrames=frames*2,rawToMixSampleRatio=[2,1],voiceOffsetSamples=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1,wholeAggregateResampleOnce=True,perComponentConstantScalarOnly=True,finalCommonVoiceGainDb=gain_db,uniformMixGainDb=0,componentSampleMap=proof_rows,pcmLineage=lineage,actualArtifactPins=inputs)

def prepare(caption_timing,audio_build):
 cp=HERE/'build-prospect-refuge-caption-timing-v3.py';ap=HERE/'verified-prospect-refuge-audio-build-v3.py';producer=HERE/'prepare-prospect-refuge-audio-v2.py'
 require(sha(cp)==CAPTION_SHA and sha(ap)==AUDIO_VERIFY_SHA and sha(producer)==AUDIO_SHA,'Reviewed selected caption/audio verifier or immutable producer changed')
 cap=module('prospect_clock_caption',cp);audio=module('prospect_clock_audio',ap)
 verified=cap.verify_existing(caption_timing);mix=audio.verified_audio_build(audio_build);folder=Path(mix['output']).resolve()
 require(Path(audio_build).resolve()==folder/'audio-build.json','Current immutable audio-build path required')
 lines=read(folder/'line-levels.json');lineage=sample_lineage(verified['timing'],verified['voice'],mix,lines,folder,audio)
 result=dict(schemaVersion=SCHEMA,topicId='06.02',status='verified-raw-to-mix-sample-clock',captionTiming=pin(caption_timing),audioBuild=pin(audio_build),rawVoiceFingerprint=verified['voice']['fingerprint'],rawVoice=verified['voice']['aggregateWav'],canonicalTiming=verified['voice']['timing'],mixWav=mix['mixWav'],lineLevels=pin(folder/'line-levels.json'),sourceHelpers=dict(clockVerifier=pin(__file__),caption=pin(cp),audio=pin(ap),audioProducer=pin(producer)),runtime=dict(numpyVersion=np.__version__,soundfileVersion=sf.__version__,libsndfileVersion=sf.__libsndfile_version__,scipyVersion=scipy.__version__),lineage=lineage,rawCaptionClockModified=False,rawMixClockAccepted=True,mixedAsrAccepted=False,actualListening=False,actualRealtimePlayback=False,automaticSpeechPass=False,humanApproval=False,scope='Exact PCM sample positions and declared scalar/resampling lineage only; raw blind-ASR time axis is unchanged. Final mixed-ASR and listening remain separate.')
 result['fingerprint']=digest(result);return result

def verify_existing(path,caption_timing=None,audio_build=None):
 path=Path(path).resolve();old=read(path)
 require(old.get('schemaVersion')==SCHEMA and old.get('topicId')=='06.02','Current separate raw-to-mix proof required')
 cp=bound(old['captionTiming']);ap=bound(old['audioBuild'])
 require((caption_timing is None or cp==Path(caption_timing).resolve())and(audio_build is None or ap==Path(audio_build).resolve()),'Clock proof belongs to different timing or mix input')
 fresh=prepare(cp,ap)
 require(path==(MEDIA/'raw-mix-clock-proofs-v2'/fresh['fingerprint'][:24]/'clock-proof.json').resolve()and old==fresh,'Stale/modified raw-to-mix proof or immutable identity differs')
 return fresh

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--caption-timing');p.add_argument('--audio-build');p.add_argument('--write',action='store_true');a=p.parse_args()
 try:
  require(a.caption_timing and a.audio_build,'Actual raw103/96 caption timing and accepted FLOAT audio-build are pending; no sample clock proof generated')
  result=prepare(a.caption_timing,a.audio_build);path=MEDIA/'raw-mix-clock-proofs-v2'/result['fingerprint'][:24]/'clock-proof.json'
  if a.write:
   data=json.dumps(result,ensure_ascii=False,indent=2)+'\n';path.parent.mkdir(parents=True,exist_ok=True)
   require(not path.exists()or path.read_text(encoding='utf8')==data,'Preserve earlier immutable clock proof')
   if not path.exists():path.write_text(data,encoding='utf8')
  print(json.dumps(dict(ready=True,path=str(path),fingerprint=result['fingerprint'],written=a.write,mediaStarted=False,mixedAsrAccepted=False,actualListening=False)))
 except(RuntimeError,AssertionError,FileNotFoundError,KeyError,ValueError)as error:
  if a.write:raise
  print(json.dumps(dict(ready=False,pending=str(error),written=False,mediaStarted=False)))
if __name__=='__main__':main()
