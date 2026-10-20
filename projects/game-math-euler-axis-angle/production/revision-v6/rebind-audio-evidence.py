"""Bind unchanged encoded audio evidence to a visual-only replacement master.

Checks AAC ADTS stream-copy SHA, codec/extradata, and every packet's normalized
PTS/DTS/duration/size/skip-sample side data against both masters and final AAC.
Never decodes audio, encodes media, starts ASR, loads a model or uses the GPU.
Original reports, decoded WAV and successful recognition caches stay unchanged.
"""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import argparse,copy,hashlib,importlib.util,json,os,subprocess,sys

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).resolve().parent
O=P/'production/local/revision-v6';BASE=O/'qa/final-mix-asr'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def proof(p):return {'file':rel(p),'sha256':sha(p)}
def require(ok,message):
 if not ok:raise ValueError(message)
def inside(p):
 p=Path(p);p=(p if p.is_absolute() else R/p).resolve()
 require(p.is_relative_to(R) and p!=R and p.is_file(),'Missing/unsafe workspace input: '+str(p));return p
def obj_sha(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save_new_or_equal(p,d):
 content=json.dumps(d,ensure_ascii=False,indent=2)+'\n';p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():require(p.read_text(encoding='utf-8-sig')==content,'Existing different wrapper preserved: '+rel(p));return
 with p.open('x',encoding='utf-8') as f:f.write(content)
def replace_json(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.rebind-'+str(os.getpid())+'.tmp')
 tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
def selected():
 c=read(R/'shared/publishing/video-production-control.json')
 require(c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized'],'Current M04 full production selection changed')


def packet_signature(rows,time_base):
 tb=Fraction(time_base);h=hashlib.sha256();first=None;last=None
 for row in rows:
  require(all(k in row for k in ['pts','dts','duration','size']),'Incomplete AAC packet timing')
  value=[str(int(row['pts'])*tb),str(int(row['dts'])*tb),str(int(row['duration'])*tb),int(row['size']),row.get('side_data_list',[])]
  require(int(row['duration'])>0 and int(row['size'])>0,'Invalid AAC packet size/duration')
  h.update(json.dumps(value,sort_keys=True,separators=(',',':')).encode()+b'\n')
  if first is None:first=value
  last=value
 return {'packets':len(rows),'normalizedPacketTimingAndTrimSha256':h.hexdigest(),'first':first,'last':last,
         'includes':'Ordered PTS,DTS,duration,size and all skip/discard/side-data fields, with exact rational seconds'}


def stream_copy_aac_sha(p):
 # Stream copy only. ADTS framing is deterministic from the identical AAC
 # codec config; this is the same compressed-stream hash definition as QA.
 cmd=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-i',str(p),'-map','0:a:0','-vn','-c:a','copy','-f','adts','pipe:1']
 proc=subprocess.Popen(cmd,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 h=hashlib.sha256()
 for block in iter(lambda:proc.stdout.read(4*1024*1024),b''):h.update(block)
 error=proc.stderr.read();code=proc.wait();require(code==0 and not error,error.decode(errors='replace')[-3000:])
 return h.hexdigest()


def inspect_audio(p,video_frames=None):
 flags={'cwd':R,'text':True,'encoding':'utf-8','creationflags':getattr(subprocess,'CREATE_NO_WINDOW',0)}
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_data_hash','sha256','-of','json',str(p)],**flags))
 audio=[x for x in data['streams'] if x['codec_type']=='audio'];require(len(audio)==1,'Exactly one encoded audio stream is required')
 a=audio[0];require((a['codec_name'],int(a['sample_rate']),a['channels'])==('aac',48000,2),'Expected original48k stereo AAC')
 require(a.get('extradata_hash'),'Actual codec extradata hash is required for decode-equivalence reasoning')
 if video_frames is not None:
  videos=[x for x in data['streams'] if x['codec_type']=='video'];require(len(videos)==1,'Exactly one current video stream is required')
  vv=videos[0];require((vv['width'],vv['height'],Fraction(vv['avg_frame_rate']),int(vv['nb_frames']))==(1920,1080,Fraction(60),video_frames),'Current master is partial or has changed timing/format')
 rows=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration,size,side_data_list','-of','json',str(p)],**flags))['packets']
 profile={k:a.get(k) for k in ['codec_name','profile','sample_fmt','sample_rate','channels','channel_layout','extradata_hash']}
 profile['startSeconds']=str(Fraction(str(a.get('start_time','0'))))
 return {'file':rel(p),'fileSha256':sha(p),'aacAdtsSha256':stream_copy_aac_sha(p),'codec':profile,
         'packetTiming':packet_signature(rows,a['time_base']),'audioStreamMetadata':a,
         'decodePerformed':False,'encoderPerformed':False,'method':'ffprobe metadata/packets and FFmpeg -c:a copy ADTS only'}


def run(args):
 selected();old_master=inside(args.previous_master);master=inside(args.master);previous_preparation=inside(args.previous_preparation)
 old=read(previous_preparation);timeline_file=H/'timeline.json';timeline=read(timeline_file);mix_file=O/'audio-build.json';mix=read(mix_file)
 previous_extraction=inside(old['extractionFile']);extraction=read(previous_extraction);old_sha=sha(old_master);new_sha=sha(master)
 require(old_sha==old['inputs']['master']['sha256']==extraction['captionedMasterSha256'],'Archived previous master does not match original audio evidence')
 require(old_sha!=new_sha,'Same master needs no audio-evidence rebinding')
 require(old['inputs']['timeline']['sha256']==sha(timeline_file)==extraction['inputs']['timelineSha256'],'Visual-only replacement must keep exact current timing')
 require(old['inputs']['finalMixReceipt']['sha256']==sha(mix_file),'Original final-mix preparation changed')
 require(old['inputs']['extraction']['sha256']==sha(previous_extraction),'Original decoded-audio receipt changed')
 decoded=inside(extraction['decodedFile']);require(sha(decoded)==old['decodedSha256']==extraction['decodedSha256'],'Original shared decoded WAV changed')
 require(extraction['decodedPcmSha256']==old['decodedPcmSha256'],'Original decoded PCM identity mismatch')
 source_selection=inside(old['inputs']['currentSourceSelection']['selectionReceipt']['file'])
 require(sha(source_selection)==old['inputs']['currentSourceSelection']['selectionReceipt']['sha256']==timeline['inputs']['currentPcmMappingSha256'],'Current selected source PCM mapping changed')
 audio=inside(mix['encodedAudio']);require(any(x['file']==rel(audio) and x['sha256']==sha(audio) for x in mix['outputs']),'Final encoded mix is not the hash-bound original')
 continuity_file=inside(args.continuity_report);continuity=read(continuity_file)
 require(continuity['captionedMasterSha256']==old_sha and continuity['inputs']['decodedSha256']==sha(decoded),'Continuity report belongs to another original master/audio')
 require(continuity['inputs']['extractionSha256']==sha(previous_extraction) and continuity['inputs']['audioBuildSha256']==sha(mix_file),'Original continuity report binding changed')
 folder=O/'qa/audio-reuse'/(old_sha+'--'+new_sha);equivalence_file=folder/'audio-equivalence.json'
 inputs={'previousMaster':proof(old_master),'currentMaster':proof(master),'encodedAudio':proof(audio),'timeline':proof(timeline_file),
         'originalPreparation':proof(previous_preparation),'originalExtraction':proof(previous_extraction),'originalContinuity':proof(continuity_file),
         'sharedDecoded':proof(decoded),'audioMixReceipt':proof(mix_file),'implementation':proof(Path(__file__))}
 if equivalence_file.exists():
  equivalence=read(equivalence_file);require(equivalence['inputs']==inputs,'Existing different audio equivalence is preserved; inspect before rerunning')
  print('Reused identical AAC/presentation proof; no repeated packet/stream-copy inspection.',flush=True)
 else:
  inspected=[inspect_audio(old_master,timeline['totalFrames']),inspect_audio(master,timeline['totalFrames']),inspect_audio(audio)]
  baseline=inspected[0]
  for row in inspected[1:]:
   require(row['aacAdtsSha256']==baseline['aacAdtsSha256'],'Compressed AAC payload differs; previous ASR/continuity cannot be rebound')
   require(row['packetTiming']==baseline['packetTiming'],'AAC packet presentation/trim timing differs; no decode-equivalence claim allowed')
   require(row['codec']==baseline['codec'],'AAC codec/extradata/start differs; no decode-equivalence claim allowed')
  equivalence={'schemaVersion':1,'revision':'article-flow-v6','inputs':inputs,'streams':inspected,'exactAACStreamEqual':True,
   'aacSha256':baseline['aacAdtsSha256'],'packetTimingExactlyEqual':True,'codecAndExtradataExactlyEqual':True,
   'deterministicDecodedAudioEquivalenceEstablished':True,'newMasterAudioDecoded':False,'newAsrRun':False,
   'proofScope':'Same compressed AAC bytes, same decoder configuration, ordered packet presentation/decoding/durations/sizes and skip/discard trim imply the same decoded samples. The new master was not independently decoded; the original actual48k FLOAT WAV remains the sample/level evidence.',
   'sourceDecodedPcmSha256':extraction['decodedPcmSha256'],'sourceDecodedWavSha256':sha(decoded),
   'humanWholeListening':'pending','userReview':'pending'}
 if not args.run:
  print(json.dumps({'status':'checked-only-no-wrapper-written','inputs':inputs,'exactAACStreamEqual':True,'newMasterAudioDecoded':False},indent=2));return
 save_new_or_equal(equivalence_file,equivalence)
 new_folder=BASE/'masters'/new_sha;new_extraction_file=new_folder/'extraction.json'
 new_extraction=copy.deepcopy(extraction)
 new_extraction['inputs'].update(captionedMasterFile=rel(master),captionedMasterSha256=new_sha)
 new_extraction.update(captionedMasterFile=rel(master),captionedMasterSha256=new_sha,sourceMasterDecodePasses=0,
  originalSourceMasterDecodePasses=extraction.get('sourceMasterDecodePasses'),audioEvidenceReuse=proof(equivalence_file),
  originalExtraction=proof(previous_extraction),reuseMethod='Exact compressed payload/codec/packet/trim equivalence; original decoded file reused without another decode')
 save_new_or_equal(new_extraction_file,new_extraction)
 spec=importlib.util.spec_from_file_location('v6_audio_rebind_asr_contract',H/'final-mix-review.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 require(module.CONFIG==old['modelIdentity']['configuration'],'Recognition configuration changed; do not reuse cached recognition')
 require(module.obj_sha(module.inference_identity(old['modelIdentity']))==old['modelConfigurationSha256'],'Recognition identity mismatch')
 preparation=copy.deepcopy(old)
 preparation['inputs'].update(master={**proof(master),'bytes':master.stat().st_size,'mtimeNs':master.stat().st_mtime_ns},
  extraction=proof(new_extraction_file),implementation=proof(H/'final-mix-review.py'))
 preparation['extractionFile']=rel(new_extraction_file)
 preparation['memorySafety']=module.memory_configuration();preparation['memoryExecutionConfigurationSha256']=module.obj_sha(preparation['memorySafety'])
 preparation['audioEvidenceReuse']=proof(equivalence_file)
 preparation['originalPreparation']=proof(previous_preparation)
 preparation['sceneInputReuse']='Same original WAV bytes, sample ranges, arithmetic stereo mean and resample1/3 configuration. Existing48k/16k hashes/cache keys retained; no resampling or recognition repeated.'
 new_preparation_file=new_folder/'preparation.json';save_new_or_equal(new_preparation_file,preparation)
 new_continuity=copy.deepcopy(continuity)
 new_continuity['inputs']['extractionSha256']=sha(new_extraction_file)
 new_continuity.update(captionedMasterFile=rel(master),captionedMasterSha256=new_sha,sharedExtractionFile=rel(new_extraction_file),
  originalNumericReport=proof(continuity_file),audioEvidenceReuse=proof(equivalence_file),numericAnalysisRepeated=False,
  newMasterAudioDecoded=False,newCodecOrModelExecuted=False)
 new_continuity_file=folder/'audio-level-continuity.json';save_new_or_equal(new_continuity_file,new_continuity)
 missing,asr_file=module.aggregate(new_preparation_file)
 output={'schemaVersion':1,'revision':'article-flow-v6','captionedMasterSha256':new_sha,'previousMasterSha256':old_sha,
  'equivalence':proof(equivalence_file),'extraction':proof(new_extraction_file),'preparation':proof(new_preparation_file),
  'audioContinuity':proof(new_continuity_file),'asrReview':proof(asr_file),'recognizedScenes':41-len(missing),'missingScenes':missing,
  'asrAggregationOnly':True,'asrInferenceRun':False,'audioDecodeRun':False,'audioEncodeRun':False,
  'refresh':'Re-run this helper with the same inputs after the original approved ASR batch finishes. It reuses the AAC proof and only aggregates successful per-scene caches.',
  'humanWholeListening':'pending','humanPaceListening':'pending','humanPronunciationReview':'pending','userReview':'pending'}
 replace_json(folder/'outputs.json',output)
 print(json.dumps({'status':'visual-only-audio-evidence-rebound','output':proof(folder/'outputs.json'),'recognizedScenes':output['recognizedScenes'],'missingScenes':missing,'noNewDecodeOrAsr':True},indent=2))


def self_test():
 rows=[{'pts':-1024,'dts':-1024,'duration':1024,'size':100,'side_data_list':[{'side_data_type':'Skip Samples','skip_samples':1024}]},
       {'pts':0,'dts':0,'duration':1024,'size':101}]
 base=packet_signature(rows,'1/48000')
 scaled=[{**r,'pts':r['pts']*2,'dts':r['dts']*2,'duration':r['duration']*2} for r in rows]
 require(packet_signature(scaled,'1/96000')==base,'Exact rational timing normalization failed')
 failures=0
 for key in ['pts','dts','duration','size']:
  altered=copy.deepcopy(rows);altered[1][key]+=1
  failures+=packet_signature(altered,'1/48000')!=base
 altered=copy.deepcopy(rows);altered[0]['side_data_list'][0]['skip_samples']=0
 failures+=packet_signature(altered,'1/48000')!=base
 require(failures==5,'Changed packet/trim contracts were not rejected')
 print('Pure CPU audio-proof tests passed: exact rational timing accepted; five changed timing/size/trim signatures differ. Media/GPU/model/files changed:0.')


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--previous-master',type=Path);parser.add_argument('--master',type=Path,default=O/'euler-captioned.mp4')
 parser.add_argument('--previous-preparation',type=Path);parser.add_argument('--continuity-report',type=Path,default=O/'qa/audio-level-continuity.json')
 parser.add_argument('--run',action='store_true');parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 if args.self_test:return self_test()
 require(args.previous_master is not None and args.previous_preparation is not None,'Explicit archived previous master and immutable preparation are required')
 run(args)


if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 try:main()
 except (ValueError,KeyError,FileNotFoundError) as error:
  print('Audio evidence rebinding stopped: '+str(error),file=sys.stderr);raise SystemExit(2)
