"""Actual finished V8 AAC and exact source/global/ceiling/final-stem continuity.

Run only after root's final-master handoff and one whole-final ASR. No audio
modification or ASR; window measurements are not subjective listening.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,subprocess
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_final_levels_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64))))if len(x)else 0.
def group_windows(rows,threshold,key,minimum=.5):
 groups=[]
 for w in rows:
  if w[key]>threshold:continue
  if groups and w['globalStart']<=groups[-1]['end']+.001:
   groups[-1]['end']=w['globalStart']+.4;groups[-1]['minimumDb']=min(groups[-1]['minimumDb'],w[key])
  else:groups.append(dict(start=w['globalStart'],end=w['globalStart']+.4,minimumDb=w[key]))
 return [dict(g,duration=g['end']-g['start'])for g in groups if g['end']-g['start']>=minimum]
def audio_identity(file):
 result=subprocess.run(['ffmpeg','-v','error','-nostdin','-threads','2','-i',str(file),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],capture_output=True);assert result.returncode==0
 payload=result.stdout.decode().strip().removeprefix('SHA256=')
 result=subprocess.run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_streams','-show_data_hash','sha256','-show_entries',
  'packet=pts,dts,duration,size,side_data_list:stream=codec_name,sample_rate,channels,extradata_hash,extradata_size,time_base','-of','json',str(file)],capture_output=True);assert result.returncode==0
 clock=json.loads(result.stdout);return dict(payloadSha256=payload,clockSha256=hashlib.sha256(json.dumps(clock,sort_keys=True).encode()).hexdigest(),
  packetCount=len(clock['packets']),codec=clock['streams'],firstPacket=clock['packets'][0],lastPacket=clock['packets'][-1])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--mix-before-master',action='store_true');args=parser.parse_args();c.validate();inp=H/'audio-final-input.json'
 if args.mix_before_master:
  timeline=H/'timeline.json';mixfile=c.O.parent/'mix/mix-report.json';mix=c.read(mixfile);t=c.read(timeline);encoded=c.R/mix['encodedAudio']
  assert any(r['file']==c.rel(encoded)and r['sha256']==c.sha(encoded)for r in mix['outputs']);identity=audio_identity(encoded)
  provenance=dict(aacPacketPayloadSha256=identity['payloadSha256']);selected=dict(master='not yet handed off;measured encoded mix only',masterSha256=None)
  asr_sha=None
 else:
  selected=c.read(inp);master=c.R/selected['master'];assert c.sha(master)==selected['masterSha256'];assert selected['approvedScriptSha256']==c.APPROVED
  timeline=c.R/selected['timeline'];assert c.sha(timeline)==selected['timelineSha256'];t=c.read(timeline)
  mixfile=c.R/selected['mixReport'];assert c.sha(mixfile)==selected['mixReportSha256'];mix=c.read(mixfile)
  provenance=c.read(c.O/'final-aac-provenance.json');asr=c.read(c.O/'final-aac-asr.json');assert provenance['masterSha256']==asr['masterSha256']==selected['masterSha256']
  assert asr['inputSha256']==provenance['inputSha256']==c.sha(inp);assert asr['aacPacketPayloadSha256']==provenance['aacPacketPayloadSha256']
  encoded=c.R/provenance['actualMasterAac'];assert c.sha(encoded)==provenance['actualMasterAacSha256'];identity=audio_identity(encoded);asr_sha=c.sha(c.O/'final-aac-asr.json')
  master_identity=audio_identity(master)
  assert identity==master_identity,'Actual master AAC clocks/priming/config must match the extracted AAC;inspect before claiming final binding'
  earlier=c.O/'measured-mix-level-review.json'
  if earlier.exists():
   previous=c.read(earlier)
   if previous['audioIdentity']==identity and previous['inputs']['mixReportSha256']==c.sha(mixfile)and previous['inputs']['timelineSha256']==c.sha(timeline)and previous['inputs']['sourceReceiptSha256']==c.sha(c.O/'tts-current.json')and previous['inputs']['sourceAlignmentSha256']==c.sha(c.O/'source-alignment.json'):
    assert c.sha(c.R/previous['decodedFile'])==previous['decodedSha256']
    previous['measurementOrigin']='Exact measured AAC;actual current-master payload,packet boundaries,PTS/DTS,duration,decoder priming and codec configuration identical. Deterministic decoded PCM and all400ms levels reused without repeated analysis.'
    previous['master']=selected['master'];previous['masterSha256']=selected['masterSha256'];previous['actualFinalAac']=c.rel(encoded)
    previous['inputs'].update(masterSha256=selected['masterSha256'],actualFinalAacSha256=c.sha(encoded),wholeFinalAsrSha256=asr_sha)
    previous['actualFinalMasterBindingComplete']=True;previous['actualMasterAudioIdentity']=master_identity
    previous['reusedExactMeasuredAacLevels']=dict(file=c.rel(earlier),sha256=c.sha(earlier),actualMasterCodecAndPacketClockIdentity=True)
    c.save(c.O/'final-aac-level-review.json',previous);print('Bound exact measured AAC levels to current final master;no repeated decoding or ASR');return
 source=c.read(c.O/'tts-current.json');assert mix['inputs']['ttsCurrentSha256']==c.sha(c.O/'tts-current.json')
 alignment=c.read(c.O/'source-alignment.json');byal={s['id']:s for s in alignment['scenes']};source_levels=c.read(c.O/'source-level-review.json');bysource={s['scene']:s for s in source_levels['scenes']}
 files={Path(row['file']).name:row for row in mix['outputs']};stems={row['role']:row for row in mix['stems']}
 raw=c.R/files['narration-placed-48k.wav']['file'];prevoice=c.R/files['narration-global-gain.wav']['file'];ceiling=c.R/files['narration-normalized.wav']['file']
 reference=c.R/mix['audioMix'];voice=c.R/stems['narration']['file'];game=c.R/stems['game']['file'];brand=c.R/stems['branding']['file']
 for file in [raw,prevoice,ceiling,reference]:assert c.sha(file)==files[file.name]['sha256']
 for row in stems.values():assert c.sha(c.R/row['file'])==row['sha256']
 signatures=dict(masterSha256=selected['masterSha256'],finalAacSha256=c.sha(encoded),mixReportSha256=c.sha(mixfile),timelineSha256=c.sha(timeline),
  sourceReceiptSha256=c.sha(c.O/'tts-current.json'),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json'),sourceLevelsSha256=c.sha(c.O/'source-level-review.json'),
  wholeFinalAsrSha256=asr_sha,implementationSha256=c.sha(Path(__file__)))
 report=c.O/('measured-mix-level-review.json'if args.mix_before_master else'final-aac-level-review.json');decoded=c.O/('measured-mix-decoded-48k.wav'if args.mix_before_master else'final-aac-decoded-48k.wav')
 if report.exists():
  old=c.read(report);assert old['inputs']==signatures and c.sha(decoded)==old['decodedSha256'];print('Exact current finished AAC level evidence reused');return
 assert not decoded.exists(),'Preserve an unreceipted final decode and inspect before reuse'
 result=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-n','-threads','2','-filter_threads','2','-i',str(encoded),'-map','0:a:0','-c:a','pcm_f32le','-ar','48000','-ac','2',str(decoded)],capture_output=True)
 (c.O/'final-aac-decode.log').write_bytes(result.stderr);assert result.returncode==0
 total=t['totalFrames']*800
 with sf.SoundFile(decoded)as dec:assert dec.samplerate==48000 and dec.channels==2 and total<=len(dec)<total+1024;decoded_samples=len(dec)
 body=t['scenes'][0]['startFrame']*800
 with sf.SoundFile(decoded)as dec,sf.SoundFile(reference)as ref:
  dec.seek(body);xx=dec.read(48000,dtype='float32',always_2d=True).mean(axis=1);ref.seek(body);yy=ref.read(48000,dtype='float32',always_2d=True).mean(axis=1)
  # Explicit sum avoids the local BLAS delay-load issue observed in V7.
  lag=max(range(-128,129),key=lambda k:float(np.sum(xx[max(0,k):len(xx)+min(0,k)]*yy[max(0,-k):len(yy)-max(0,k)],dtype=np.float64)))
 assert lag==0,'Encoded sample shift must be investigated, never silently compensated'
 scene_rows=[];all_windows=[];clip_samples=0
 paths=[decoded,reference,raw,prevoice,ceiling,voice,game,brand];handles=[sf.SoundFile(p)for p in paths]
 names=['actualEncodedMixDbfs','knownFinalMixDbfs','sourcePlacedDbfs','globalTargetVoiceDbfs','postCeilingVoiceDbfs','finalVoiceStemDbfs','knownGameStemDbfs','knownBrandStemDbfs']
 try:
  for scene in t['scenes']:
   sid=scene['id'];begin=scene['startFrame']*800;length=scene['rawVoiceSamples']*2;buffers=[]
   for handle in handles:handle.seek(begin);buffers.append(handle.read(length,dtype='float32',always_2d=True))
   assert all(len(x)==length for x in buffers);mask=np.zeros(length,bool);asrrow=c.read(c.R/byal[sid]['asrFile']);assert asrrow['audio_sha256']==scene['rawVoiceSha256']
   for w in asrrow['words']:
    a,b=w['timestamp']
    if a is not None and b is not None and b>a:mask[max(0,round(a*48000)):min(length,round(b*48000))]=True
   def values(a,b):
    active=mask[a:b];assert active.any();data={name:db(rms(x[a:b][active]))for name,x in zip(names,buffers)}
    data.update(encodedMixTransferDb=data['actualEncodedMixDbfs']-data['knownFinalMixDbfs'],
     measuredGlobalVoiceTransferDb=data['globalTargetVoiceDbfs']-data['sourcePlacedDbfs'],ceilingEnergyTransferDb=data['postCeilingVoiceDbfs']-data['globalTargetVoiceDbfs'],
     measuredFinalProgramVoiceGainDb=data['finalVoiceStemDbfs']-data['postCeilingVoiceDbfs'],knownVoiceToGameDb=data['finalVoiceStemDbfs']-data['knownGameStemDbfs'],
     codecResidualDbfs=db(rms(buffers[0][a:b][active]-buffers[1][a:b][active])))
    return data
   windows=[]
   for a in range(0,length-19200+1,4800):
    b=a+19200
    if mask[a:b].sum()<7200:continue
    windows.append(dict(rawStart=a/48000,rawEnd=b/48000,globalStart=(begin+a)/48000,**values(a,b)))
   paragraphs=[]
   for line in byal[sid]['lines']:
    a=max(0,round(line['rawStart']*48000));b=min(length,round(line['rawEnd']*48000));base=next(r for r in bysource[sid]['paragraphs']if r['line']==line['line'])
    paragraphs.append(dict(line=line['line'],rawStart=a/48000,rawEnd=b/48000,globalStart=(begin+a)/48000,globalEnd=(begin+b)/48000,
     sourceRawTakeSpeechDbfs=base['sourceSpeechDbfs'],sourceCompleteParagraphGainDb=base['documentedGainDb'],sourceConstantGainSampleExact=base['constantGainPcmExact'],**values(a,b)))
   encoded_flags=[w for w in windows if abs(w['encodedMixTransferDb'])>1]
   clips=int(np.sum(abs(buffers[0])>=1));clip_samples+=clips
   scene_rows.append(dict(scene=sid,currentSourceSha256=scene['rawVoiceSha256'],asrSha256=byal[sid]['asrSha256'],paragraphs=paragraphs,windows=windows,
    encodedTransferCandidateWindows=encoded_flags,encodedRelativeDropGroups=group_windows(windows,-6,'encodedMixTransferDb'),
    ceilingEnergyReductionGroups=group_windows(windows,-6,'ceilingEnergyTransferDb'),decodedSamplesAtOrAboveFullScale=clips,
    codecResidualRmsDbfs=db(rms(buffers[0]-buffers[1])),humanListening='pending'))
   all_windows.extend(windows);print('Reviewed actual final AAC levels',sid,flush=True)
 finally:
  for handle in handles:handle.close()
 joins=[]
 for left,right in zip(scene_rows,scene_rows[1:]):
  a,b=left['paragraphs'][-1],right['paragraphs'][0];joins.append(dict(previous=left['scene'],next=right['scene'],previousCompleteParagraph=a,nextCompleteParagraph=b,
   actualEncodedParagraphDeltaDb=b['actualEncodedMixDbfs']-a['actualEncodedMixDbfs'],knownVoiceParagraphDeltaDb=b['finalVoiceStemDbfs']-a['finalVoiceStemDbfs'],
   wordTimestampQuietSpan=b['globalStart']-a['globalEnd'],humanListening='pending'))
 result=dict(revision='orientation-matrix-v8',inputs=signatures,master=selected['master'],masterSha256=selected['masterSha256'],
  actualFinalAac=c.rel(encoded),aacPacketPayloadSha256=provenance['aacPacketPayloadSha256'],audioIdentity=identity,decodedFile=c.rel(decoded),decodedSha256=c.sha(decoded),
  measuredVoicedSampleShift=lag,sampleRate=48000,channels=2,programSamples=total,decodedSamples=decoded_samples,trailingEncoderPaddingSamples=decoded_samples-total,
  sourceToGlobalGainDb=mix['voiceGlobalGainDb'],peakSafety=mix['peakSafety'],finalProgramGainDb=mix['programGlobalGainDb'],encodedMeasurement=mix['encodedMeasurement'],
  measurementInterpretation='Only loudnorm input_i/input_tp measure existing audio. output_* are discarded analysis-filter output.',
  scenes=scene_rows,joins=joins,encodedTransferCandidateWindows=sum(len(s['encodedTransferCandidateWindows'])for s in scene_rows),
  decodedSamplesAtOrAboveFullScale=clip_samples,addedBgm=False,sourceSpeed=1,voiceFades=False,voiceDucking=False,
  method='Compare preserved source→one global gain→4xoversampled ceiling→actual final voice stem→known mix→current master decoded AAC at exact sample positions.400ms/100mswindows require150ms source-ASR timestamp-active samples. No encoded source-separation claim; changes between mix and decoded AAC include codec error.',
  measuredBeforeFinalMasterHandoff=args.mix_before_master,humanWholeListening='pending',actualVoiceVisualPace='pending',finalFullTextReview='separate exact current AAC transcript comparison required')
 c.save(report,result);print(json.dumps(dict(sceneCount=len(scene_rows),paragraphCount=sum(len(s['paragraphs'])for s in scene_rows),encodedCandidateWindows=result['encodedTransferCandidateWindows'],masterSha256=selected['masterSha256'])))
if __name__=='__main__':main()
