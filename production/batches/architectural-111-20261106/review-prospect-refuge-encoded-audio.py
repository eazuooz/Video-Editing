"""06.02 encoded AAC numerical QA; default readiness performs no media process.

Only --execute probes/decodes actual completed masters and measures input levels.
No encoder/model/GPU/lease, speech repair, trimming, offset application or hearing.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,re,shutil,subprocess,sys,uuid
from fractions import Fraction
from pathlib import Path
os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
import numpy as np
import soundfile as sf
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106');TOPIC=MEDIA/'shorts-leveldesign-06-02'
DEST=TOPIC/'encoded-audio-review-v1';SCHEMA='06-02-encoded-audio-numerical-review-v1'
PINS={'review-zen-view-audio-levels.py':'240c9bfe5e3baf5133fbcd39ec7e45e4739737a63ba594f220265c4b795a2388','first-level-continuity-review.py':'545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544','render-prospect-refuge-film-v2.py':'3ba569d8b8340e338f5ab58e2be1c0944af58e6466bca8b1b69f8d75b421abe9','verified-prospect-refuge-audio-build-v3.py':'db521babf1848861979a7580cd0a045540575f945909d99d2a7055433344f3b4'}
NUMERIC_PEER=ROOT/'projects/shorts-leveldesign-06-02/audio-actual-numerical-peer-v3.json'
NUMERIC_PEER_SHA='f50b92af52d4294cba642d5f2b32154be6515ca96fa956be247c122ed0b0d86b'
MIX_SHA='16823497fd0241b8c48b5fa1f607b076ebffc10dd600f5d388e26757d2bbcc17'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)
ACTIVE=None
class Pending(RuntimeError):pass

def require(ok,message):
 if not ok:raise Pending(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def bound(q):
 p=Path(q['path']).resolve();require(p.is_file()and sha(p)==q['sha256'],'Changed pinned file: '+str(p));return p
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,path)
for name,expected in PINS.items():require(sha(HERE/name)==expected,'Reviewed source changed: '+name)
legacy=module('prospect_encoded_private_07_numerics',HERE/'review-zen-view-audio-levels.py');mathqa=legacy.mathqa
runtime=legacy.runtime;runtime.PROTOCOL='architectural111-06-02-encoded-audio-review-v1';runtime.OWNER='architectural-111-06-02-encoded-audio-review'
WORKER=MEDIA/'06-02-encoded-audio-review-worker.json'
POLICY=copy.deepcopy(mathqa.POLICY)

def validate_grid(build,t):
 mix=build['mixWav'];raw=build['rawVoice']
 require(build.get('topicId')=='06.02'and build.get('selectedComponentCount')==103,'Current selected103 component mix required')
 require(mix.get('sha256')==MIX_SHA and(mix['sampleRate'],mix['channels'],mix['subtype'],mix['frames'])==(48000,2,'FLOAT',raw['frames']*2),'Exact current stereoFLOAT mix clock required')
 require(t.get('audio',{}).get('voice')==raw and t['audio'].get('mix')==mix,'Film uses another speech/mix source')
 require(t.get('format')==dict(width=1080,height=1920,fps=60)and t.get('totalFrames')==math.ceil(mix['frames']/800),'Encoded visual ceil/sample clock differs')
 for key,value in dict(voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,uniformMixGainDb=0,wordBoundariesShifted=False,compressorUsed=False,voiceSideDuck=False).items():require(build.get(key)==value,'Forbidden speech DSP/time change: '+key)
 return dict(rawFrames=raw['frames'],rawRate=24000,mixFrames=mix['frames'],mixRate=48000,videoFrames=t['totalFrames'],fps=60)

def prepare(render_manifest):
 path=Path(render_manifest).resolve();require(path.name=='render-manifest.json'and path.is_relative_to((TOPIC/'render-attempts-v2').resolve()),'Actual selected render manifest required')
 manifest=read(path);require(manifest.get('schemaVersion')=='06-02-render-manifest-v2'and manifest.get('topicId')=='06.02'and manifest.get('complete')is True,'Complete actual06.02 render is pending')
 t=read(bound(manifest['timeline']));renderer=module('prospect_encoded_current_renderer',HERE/'render-prospect-refuge-film-v2.py');renderer.verify_inputs(t)
 require(manifest['format']==t['format']and manifest['totalFrames']==t['totalFrames']and manifest['inputs']==t['inputs'],'Render clock/input snapshot differs from current verified timeline')
 for key in('clean','captioned','ko','en'):
  q=manifest['outputs'][key];p=bound(q);require(p.parent==path.parent and p.name=='shorts-leveldesign-06-02.'+({'clean':'clean.mp4','captioned':'captioned.mp4','ko':'ko.srt','en':'en.srt'}[key]),'Final output escaped selected immutable attempt')
 ap=bound(t['audio']['build']);audio=module('prospect_encoded_current_audio',HERE/'verified-prospect-refuge-audio-build-v3.py');build=audio.verified_audio_build(ap);grid=validate_grid(build,t)
 require(sha(NUMERIC_PEER)==NUMERIC_PEER_SHA,'Reviewed actual numeric word/stem evidence changed');peer=read(NUMERIC_PEER)
 require(peer['inputs']['audioBuild']==pin(ap)and peer['mixWav']==build['mixWav'],'Word-level peer belongs to a different mix')
 words_path=bound(peer['actualWordLevelReport']);wordproof=read(words_path)
 for q in wordproof['inputs'].values():bound(q)
 require(wordproof['mixWav']==build['mixWav']and len(wordproof['words'])==1041 and wordproof['independentlyReadWordWindowResiduals']==dict(rawToScalarMaximumAbsolute=0.,preparedToVoiceMaximumAbsolute=0.,knownMixStemMaximumAbsolute=0.),'Actual current same-time word/stem proof differs')
 clock=read(bound(t['rawMixClockProof']));require(clock['audioBuild']==pin(ap)and clock['mixWav']==build['mixWav']and clock['rawMixClockAccepted']is True,'Actual raw-to-mix clock proof differs')
 words=[]
 lines=read(ap.parent/'line-levels.json');texts={r['sceneId']:r['text']for r in lines['components']}
 for row in wordproof['words']:
  a,b=row['rawSampleRange'];require(row['mixedSampleRange']==[a*2,b*2]and 0<=a<b<=build['rawVoice']['frames'],'Word sample mapping differs')
  words.append(dict(row,mixSampleRange=row['mixedSampleRange'],recognizedContext=texts[row['sceneId']]))
 ff=Path(mathqa.ffmpeg_path()).resolve();probe=ff.with_name('ffprobe.exe');require(ff.is_file()and probe.is_file(),'Installed bounded CPU audio tools missing')
 sources=[pin(__file__)]+[pin(HERE/name)for name in PINS]
 inputs=[pin(path),manifest['timeline'],pin(ap),pin(NUMERIC_PEER),pin(words_path),t['rawMixClockProof']]+[manifest['outputs'][k]for k in('clean','captioned','ko','en')]+[pin(ff),pin(probe)]
 identity=dict(schemaVersion=SCHEMA,sourcePins=sources,inputs=inputs,grid=grid,mix=build['mixWav'],policy=POLICY,manualSkipSamples=0,alignmentUse='comparison windows only; never audio edits')
 return dict(identity=identity,fingerprint=digest(identity),manifest=manifest,timeline=t,build=build,peer=peer,wordProof=wordproof,words=words,ff=ff,probe=probe)

def packet_contract(data,frames):
 streams=data.get('streams',[]);packets=data.get('packets',[])
 require(len(streams)==1 and packets,'Exactly one actual AAC stream and nonempty packets required')
 s=streams[0];require(s.get('codec_name')=='aac'and int(s.get('sample_rate',0))==48000 and s.get('channels')==2 and Fraction(s.get('time_base','0'))==Fraction(1,48000),'AAC codec/sample grid differs')
 signature=[];previous_end=None;initial_skip=0;final_discard=0
 for i,p in enumerate(packets):
  pts=p.get('pts');dts=p.get('dts');duration=p.get('duration');size=p.get('size')
  require(type(pts)is int and type(dts)is int and type(duration)is int and duration>0 and pts==dts and int(size)>0,'AAC packet clock/size missing or invalid')
  require(previous_end is None or pts==previous_end,'AAC packet gap/overlap or reordered PTS');previous_end=pts+duration
  require(re.fullmatch('SHA256:[0-9a-fA-F]{64}',p.get('data_hash',''))is not None,'Actual AAC payload hash missing')
  side=p.get('side_data_list',[]);require(type(side)is list,'Packet side-data must be explicit list')
  for q in side:
   if q.get('side_data_type')=='Skip Samples':
    skip=q.get('skip_samples',0);discard=q.get('discard_padding',0)
    require(type(skip)is int and type(discard)is int and 0<=skip<=duration and 0<=discard<=duration,'Invalid explicit AAC skip/discard samples')
    require(not skip or i==0,'Unexplained interior AAC skip');require(not discard or i==len(packets)-1,'Unexplained interior AAC discard')
    initial_skip+=skip;final_discard+=discard
  signature.append(dict(pts=pts,dts=dts,duration=duration,size=int(size),flags=p.get('flags'),data_hash=p['data_hash'],side_data_list=side))
 require(packets[0]['pts']+initial_skip==0 and int(s.get('start_pts',0))==0,'Actual AAC effective start is nonzero; no guessed trim')
 end=packets[-1]['pts']+packets[-1]['duration']-final_discard
 require(abs(end-frames)<=1024,'AAC packet end differs beyond one codec frame')
 return dict(stream={k:s.get(k)for k in('codec_name','sample_rate','channels','time_base','start_pts','start_time','duration_ts','duration','extradata_hash')},packetSignature=signature,packetCount=len(signature),explicitInitialSkipSamples=initial_skip,explicitFinalDiscardSamples=final_discard,effectivePacketEndSample=end,referenceFrames=frames,packetEndMinusReferenceSamples=end-frames,manualSkipSamples=0)

def same_packets(first,second):
 require(first['stream']==second['stream']and first['packetSignature']==second['packetSignature'],'Clean/captioned AAC payload, side-data or timestamps differ')
 return dict(identicalPayloadClockAndSkipMetadata=True,packetCount=first['packetCount'],packetSequenceSHA256=digest(first['packetSignature']))

def decoded_grid(reference_frames,decoded_frames,alignment):
 flags=[]
 if decoded_frames<reference_frames or decoded_frames-reference_frames>1023:flags.append(dict(kind='encoded-decoded-duration-outside-one-frame-tail',referenceFrames=reference_frames,decodedFrames=decoded_frames))
 if not alignment.get('supported'):flags.append(dict(kind='encoded-alignment-not-established',alignment=alignment))
 elif alignment.get('decodedMinusReferenceSamples')!=0:flags.append(dict(kind='encoded-nonzero-comparison-offset',alignment=alignment,audioModified=False))
 return dict(referenceFrames=reference_frames,decodedFrames=decoded_frames,decodedMinusReferenceFrames=decoded_frames-reference_frames,normalDecoderSkipHandling=True,manualSkipSamples=0,alignmentAppliedToAudio=False),flags

def tool(command,log):
 require(ACTIVE is not None,'Owned bounded CPU worker required');command=[str(x)for x in command];binary=Path(command[0]).resolve()
 ff=Path(mathqa.ffmpeg_path()).resolve();require(binary in(ff,ff.with_name('ffprobe.exe')),'Only installed CPU audio probe/decode/measurement tools allowed')
 ACTIVE.update(phase='launching-owned-cpu-measurement',launchCommand=command,child=None)
 child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE);ACTIVE.update(child=runtime.identity(child.pid),phase='owned-cpu-measurement')
 try:out,err=child.communicate(timeout=1800)
 except subprocess.TimeoutExpired:
  child.terminate();out,err=child.communicate(timeout=30);Path(log).write_bytes(err);raise Pending('Owned CPU audio process exceeded finite1800-second limit')
 ACTIVE.update(child=None,phase='numerical-analysis');Path(log).write_bytes(err)
 require(child.returncode==0,'Owned CPU audio tool failed; preserved exact logs');return subprocess.CompletedProcess(command,child.returncode,out,err)

def probe_packets(ctx,key,work):
 q=ctx['manifest']['outputs'][key];bound(q)
 command=[ctx['probe'],'-v','error','-threads','2','-select_streams','a:0','-show_streams','-show_packets','-show_data_hash','sha256','-of','json',q['path']]
 data=json.loads(tool(command,work/(key+'-packet-probe.log')).stdout);save(work/(key+'-audio-packets.json'),data)
 return packet_contract(data,ctx['build']['mixWav']['frames'])

def compute_comparison(ctx,decoded_path):
 mix,rate=sf.read(ctx['build']['mixWav']['path'],dtype='float32',always_2d=True);decoded,sr=sf.read(decoded_path,dtype='float32',always_2d=True)
 require(rate==sr==48000 and mix.shape[1]==decoded.shape[1]==2 and np.isfinite(mix).all()and np.isfinite(decoded).all(),'Decoded AAC finite stereo grid differs')
 encoded,flags=legacy.encoded_comparison(mix,decoded,ctx['words']);grid,extra=decoded_grid(len(mix),len(decoded),encoded['alignment']);flags+=extra
 return dict(encoded=encoded,decodedGrid=grid,flags=flags)

def remaining_review(ctx):
 return dict(existingNumericPeer=pin(NUMERIC_PEER),actualWordLevelReport=ctx['peer']['actualWordLevelReport'],retainedExistingCounts=ctx['peer']['retainedExistingReviewCounts'],knownMusicRatioWatchTargets=ctx['wordProof']['knownMusicRatioWatchTargets'],medianTargetShortfalls=ctx['wordProof']['medianTargetShortfalls'],technicalAcceptance=ctx['build']['acceptedComponentsReview'],existingTargetsCleared=False,interpretation='Known component ratios/short phrase trends/peak caps are numerical listening targets, not perceptual masking or naturalness verdicts')

def measured_input(log,source):
 blocks=re.findall(r'\{\s*"input_i"[\s\S]*?\}',Path(log).read_text(encoding='utf-8',errors='replace'));require(blocks,'Actual loudness input measurement missing');value=json.loads(blocks[-1]);i=float(value['input_i']);tp=float(value['input_tp'])
 require(math.isfinite(i)and math.isfinite(tp),'Actual input loudness/truepeak notfinite')
 return dict(inputLufs=i,inputTruePeakDbtp=tp,source=pin(source),audioChanged=False,qualityPass=False,method='Input measurement only; FFmpeg transformed output discarded')

def peak_flags(full):
 return [dict(kind='whole-input-true-peak-above-approved-limit',stage=name,inputTruePeakDbtp=full[name]['inputTruePeakDbtp'],maximumDbtp=-1.5,audioChanged=False)for name in('mix','decodedAac')if full[name]['inputTruePeakDbtp']> -1.5]

def analyze(render_manifest):
 global ACTIVE
 worker=runtime.SingleWorker(WORKER,is_alive=legacy.owned_alive).acquire();ACTIVE=worker;legacy.ACTIVE=worker;legacy.run_tool=tool;work=None
 try:
  ctx=prepare(render_manifest);renderer=module('prospect_encoded_authority',HERE/'render-prospect-refuge-film-v2.py');renderer.fresh_authorization()
  target=DEST/ctx['fingerprint'][:24]
  if(target/'review.json').exists():return verify_existing(target/'review.json',render_manifest)
  require(not target.exists(),'Preserve incomplete prior encoded QA output')
  require(shutil.disk_usage(TOPIC).free>ctx['build']['mixWav']['frames']*8+1024**3,'Insufficient proportional CPU decode reserve')
  require(runtime.psutil.virtual_memory().available>ctx['build']['mixWav']['frames']*80+1024**3,'Insufficient bounded audio comparison memory')
  os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2');runtime.psutil.Process().nice(runtime.psutil.BELOW_NORMAL_PRIORITY_CLASS)
  work=DEST/('work-'+ctx['fingerprint'][:16]+'-'+uuid.uuid4().hex[:8]);work.mkdir(parents=True,exist_ok=False);save(work/'input-identity.json',ctx['identity'])
  packet_records={k:probe_packets(ctx,k,work)for k in('clean','captioned')};packet_match=same_packets(packet_records['clean'],packet_records['captioned']);save(work/'audio-packets.json',dict(**packet_records,comparison=packet_match))
  wav=work/'decoded-encoded-aac.wav';command=[ctx['ff'],'-hide_banner','-nostdin','-n','-xerror','-err_detect','explode','-threads','2','-filter_threads','2','-hwaccel','none','-i',ctx['manifest']['outputs']['captioned']['path'],'-map','0:a:0','-vn','-ar','48000','-ac','2','-c:a','pcm_f32le',wav];tool(command,work/'aac-decode.log')
  numerical=compute_comparison(ctx,wav);full={}
  for name,path in [('voice',Path(ctx['build']['output'])/'narration-stem.wav'),('mix',ctx['build']['mixWav']['path']),('decodedAac',wav)]:full[name]=legacy.loudness(path,work,name)
  numerical['flags']+=peak_flags(full)
  save(work/'numerical.json',numerical)
  fresh=prepare(render_manifest);require(fresh['identity']==ctx['identity'],'Selected inputs changed during encoded QA');renderer.fresh_authorization()
  artifacts=[dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in sorted(work.iterdir())if p.is_file()]
  remaining=remaining_review(ctx)
  result=dict(schemaVersion=SCHEMA,topicId='06.02',status='encoded-numerical-complete-listening-pending',fingerprint=ctx['fingerprint'],inputIdentity=ctx['identity'],renderManifest=pin(render_manifest),timeline=ctx['manifest']['timeline'],masters={k:ctx['manifest']['outputs'][k]for k in('clean','captioned')},mixWav=ctx['build']['mixWav'],packetProof=pin(work/'audio-packets.json'),packetMatch=packet_match,decode=dict(source=ctx['manifest']['outputs']['captioned'],wav=pin(wav),command=[str(x)for x in command],manualSkipSamples=0,audioModified=False),numerical=pin(work/'numerical.json'),encoded=numerical['encoded'],decodedGrid=numerical['decodedGrid'],encodedFlags=numerical['flags'],fullFileLoudness=full,remainingReview=remaining,artifacts=artifacts,output=str(target),actualPcmDecoded=True,videoFramesDecoded=False,mixedAsrPerformed=False,modelLoaded=False,gpuUsed=False,originalPcmUnchanged=True,voiceDspChanged=False,comparisonOffsetAppliedToAudio=False,automaticSpeechPass=False,actualListening=False,fullRealtimePlayback=False,naturalnessApproved=False,humanApproval=False)
  result=legacy.rebased_proof(result,work,target);save(work/'review.json',result);require(not target.exists(),'Version appeared concurrently');work.rename(target);return result
 except BaseException as error:
  if work and work.exists()and not(work/'failed.json').exists():save(work/'failed.json',dict(complete=False,error=str(error),originalPcmUnchanged=True,actualListening=False))
  raise
 finally:
  ACTIVE=None;legacy.ACTIVE=None;worker.close(remove=not runtime.alive(worker.record.get('child'))and not legacy.unregistered(worker.record))

def saved_bindings(old,ctx,target):
 """Documentary report fields must refer to these exact verified inputs/artifacts."""
 require(old.get('renderManifest')==ctx['identity']['inputs'][0]and old.get('timeline')==ctx['manifest']['timeline'],'Saved report substituted manifest/timeline pin')
 require(old.get('masters')=={k:ctx['manifest']['outputs'][k]for k in('clean','captioned')}and old.get('mixWav')==ctx['build']['mixWav'],'Saved report substituted master/mix pin')
 require(old.get('decode',{}).get('source')==ctx['manifest']['outputs']['captioned']and Path(old.get('output','')).resolve()==target.resolve(),'Saved report substituted decoder source/output scope')
 rows=old.get('artifacts',[]);names=[r.get('file')for r in rows];require(len(names)==len(set(names)),'Duplicate saved encoded artifact name')
 hashes={r['file']:r['sha256']for r in rows}
 for q,name in((old.get('decode',{}).get('wav',{}),'decoded-encoded-aac.wav'),(old.get('packetProof',{}),'audio-packets.json'),(old.get('numerical',{}),'numerical.json')):
  require(Path(q.get('path','')).resolve()==(target/name).resolve()and q.get('sha256')==hashes.get(name),'Saved encoded artifact pin/path escaped exact owned result: '+name)

def verify_existing(path,render_manifest=None):
 path=Path(path).resolve();old=read(path);require(old.get('schemaVersion')==SCHEMA and old.get('topicId')=='06.02','Selected encoded numerical review required')
 manifest=bound(old['renderManifest']);require(render_manifest is None or manifest==Path(render_manifest).resolve(),'Encoded review belongs to a different render')
 ctx=prepare(manifest);target=DEST/ctx['fingerprint'][:24];require(path==target/'review.json'and old.get('inputIdentity')==ctx['identity']and old.get('fingerprint')==ctx['fingerprint'],'Stale encoded review/source identity')
 saved_bindings(old,ctx,target)
 for row in old['artifacts']:
  require(Path(row['file']).name==row['file'],'Encoded QA artifact escaped version');bound(dict(path=str(target/row['file']),sha256=row['sha256']))
 packets=read(bound(old['packetProof']));new_packets={k:packet_contract(read(target/(k+'-audio-packets.json')),ctx['build']['mixWav']['frames'])for k in('clean','captioned')};require(packets==dict(**new_packets,comparison=same_packets(new_packets['clean'],new_packets['captioned']))and old['packetMatch']==packets['comparison'],'Encoded packet proof changed')
 numerical=read(bound(old['numerical']));recomputed=compute_comparison(ctx,bound(old['decode']['wav']))
 for key in('encoded','decodedGrid'):require(old[key]==numerical[key]==recomputed[key],'Decoded aligned word measurement changed')
 full={name:measured_input(target/(name+'-loudness.log'),source)for name,source in [('voice',Path(ctx['build']['output'])/'narration-stem.wav'),('mix',ctx['build']['mixWav']['path']),('decodedAac',old['decode']['wav']['path'])]}
 stored_full=copy.deepcopy(old['fullFileLoudness'])
 for value in stored_full.values():value['source'].pop('producedAtPath',None) # Atomic-move provenance is documentary, actual path/SHA stay checked.
 require(stored_full==full,'Whole-file actual input measurement changed')
 require(old['encodedFlags']==numerical['flags']==recomputed['flags']+peak_flags(full),'Encoded flags were hidden/changed')
 for key in('actualListening','fullRealtimePlayback','naturalnessApproved','humanApproval','automaticSpeechPass'):require(old.get(key)is False,'Numerical QA cannot grant '+key)
 require(old['remainingReview']==remaining_review(ctx),'Original listening targets changed or cleared')
 return old

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--render-manifest');p.add_argument('--execute',action='store_true');p.add_argument('--verify-report');a=p.parse_args()
 if a.verify_report:result=verify_existing(a.verify_report,a.render_manifest)
 elif a.execute:
  require(a.render_manifest,'Actual final manifest required');result=analyze(a.render_manifest)
 elif not a.render_manifest:result=dict(ready=False,pending='Actual complete06.02 clean/captioned render required',mediaStarted=False,modelLoaded=False)
 else:
  try:ctx=prepare(a.render_manifest);result=dict(ready=True,fingerprint=ctx['fingerprint'],wordWindows=len(ctx['words']),mediaStarted=False,modelLoaded=False)
  except(Pending,ValueError,KeyError,FileNotFoundError)as e:result=dict(ready=False,pending=str(e),mediaStarted=False,modelLoaded=False)
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
