"""Current master AAC→decoded mix/stems continuity; no new ASR or level edits."""
from pathlib import Path
import importlib.util,json,subprocess
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_encoded_levels_prepare',H/'audio-prepare.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
def main():
 c.validate(preserve_pcm=True);selected=c.read(H/'final-asr-input.json');binding_file=c.O/'final-master-binding.json';binding=c.read(binding_file);master=c.R/binding['master'];assert c.sha(master)==binding['masterSha256']
 provenance=c.read(c.O/'final-master-audio-provenance.json');asr=c.read(c.O/'final-master-asr.json')
 assert provenance['masterSha256']==asr['masterSha256']==selected['masterSha256']
 assert binding['asrOriginMasterSha256']==asr['masterSha256']and binding['wholeAsrSha256']==c.sha(c.O/'final-master-asr.json')
 assert binding['frozenAsrInputSha256']==c.sha(H/'final-asr-input.json')and binding['allAacPacketPayloadsAndPtsDtsDurationsIdentical']
 assert binding['audioIdentity']['packetPayloadSha256']==provenance['packetPayloadSha256']==asr['aacPacketPayloadSha256']
 encoded=c.R/provenance['extractedAudio'];assert c.sha(encoded)==provenance['extractedSha256']
 build_file=c.O/'audio-build.json';build=c.read(build_file);assert c.sha(build_file)==selected['audioBuildSha256']
 t=c.read(H/'timeline.json');al={x['id']:x for x in c.read(c.O/'source-alignment.json')['scenes']}
 total=t['totalFrames']*800;decoded=c.O/'final-master-decoded-48k.wav';report_file=c.O/'final-master-level-review.json'
 continuity_file=c.O/'narration-continuity-review.json';continuity=c.read(continuity_file);source_rows={r['scene']:r for r in continuity['scenes']}
 assert continuity['currentNarrationSha256']==c.sha(c.R/build['inputs']['narrationFile'])
 inputs=dict(masterSha256=binding['masterSha256'],asrOriginMasterSha256=selected['masterSha256'],currentMasterBindingSha256=c.sha(binding_file),aacPayloadSha256=provenance['packetPayloadSha256'],audioBuildSha256=c.sha(build_file),timelineSha256=c.sha(H/'timeline.json'),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json'),narrationContinuitySha256=c.sha(continuity_file),implementationSha256=c.sha(Path(__file__)))
 if report_file.exists():
  old=c.read(report_file);assert old['inputs']==inputs and c.sha(decoded)==old['decodedSha256'],'Preserve a different master review'
  print('Exact successful current-master level review reused');return
 reused_decode=decoded.exists()
 if reused_decode:
  recovery=c.read(c.O/'final-master-decode-recovery.json')
  assert recovery['decodedSha256']==c.sha(decoded)and recovery['encodedSha256']==c.sha(encoded)and recovery['masterSha256']==binding['masterSha256'],'Only the explicitly inspected complete decode may be resumed'
 else:a.run(['-threads','2','-filter_threads','2','-i',encoded,'-map','0:a:0','-c:a','pcm_f32le','-ar','48000','-ac','2',decoded],'final-master-decode')
 with sf.SoundFile(decoded)as f:
  assert f.samplerate==48000 and f.channels==2 and total<=f.frames<total+1024
  decoded_samples=f.frames
 known=c.R/build['audioMix'];voice=c.R/build['narrationStem'];game=c.R/build['gameStem'];brand=c.R/build['brandingStem']
 for file in [known,voice,game,brand]:assert any(x['file']==c.rel(file)and c.sha(file)==x['sha256']for x in build['outputs'])
 # Verify AAC skip/priming behavior against a voiced sample without shifting it.
 body=t['scenes'][0]['startFrame']*800
 with sf.SoundFile(decoded)as dec,sf.SoundFile(known)as ref:
  dec.seek(body);x=dec.read(48000,dtype='float32',always_2d=True).mean(axis=1)
  ref.seek(body);y=ref.read(48000,dtype='float32',always_2d=True).mean(axis=1)
  # Elementwise correlation avoids a broken local BLAS DLL delay-load path.
  # This is the same dot product, with explicit double-precision accumulation.
  best=max(range(-128,129),key=lambda lag:float(np.sum(x[max(0,lag):len(x)+min(0,lag)]*y[max(0,-lag):len(y)-max(0,lag)],dtype=np.float64)))
 assert best==0,'Unexpected encoded sample shift; do not silently alter clocks'
 rows=[];clips=[]
 with sf.SoundFile(decoded)as dec,sf.SoundFile(known)as ref,sf.SoundFile(voice)as vs,sf.SoundFile(game)as gs,sf.SoundFile(brand)as bs:
  for scene in t['scenes']:
   sid=scene['id'];begin=scene['startFrame']*800;length=scene['rawVoiceSamples']*2;buffers=[]
   for f in [dec,ref,vs,gs,bs]:f.seek(begin);buffers.append(f.read(length,dtype='float32',always_2d=True))
   actual,expected,voiced,gamed,branded=buffers;assert all(len(x)==length for x in buffers)
   cached=c.read(c.R/al[sid]['asrFile']);assert c.sha(c.R/al[sid]['asrFile'])==al[sid]['asrSha256']and cached['audio_sha256']==scene['rawVoiceSha256']
   mask=np.repeat(a.speech_mask(scene['rawVoiceSamples'],24000,cached['words']),2);windows=[]
   for lo in range(0,length-19200+1,4800):
    hi=lo+19200;active=mask[lo:hi]
    if active.sum()<7200:continue
    lev=[a.db(a.rms(x[lo:hi][active]))for x in buffers];error=actual[lo:hi][active]-expected[lo:hi][active]
    # Subtraction is a codec-error diagnostic, not real source separation.
    estimate=actual[lo:hi][active]-gamed[lo:hi][active]-branded[lo:hi][active]
    windows.append(dict(rawStart=lo/48000,rawEnd=hi/48000,globalStart=begin/48000+lo/48000,
     actualEncodedMixDbfs=lev[0],expectedMixerWaveformDbfs=lev[1],knownVoiceStemDbfs=lev[2],knownGameStemDbfs=lev[3],
     encodedMixTransferDb=lev[0]-lev[1],codecResidualDbfs=a.db(a.rms(error)),knownVoiceToGameDb=lev[2]-lev[3],
     approximateDecodedVoiceResidualDbfs=a.db(a.rms(estimate)),approximateVoiceTransferDb=a.db(a.rms(estimate))-lev[2]))
   flags=[x for x in windows if abs(x['encodedMixTransferDb'])>1 or x['approximateVoiceTransferDb']<-3]
   def range_level(row):
    lo=max(0,round(row['rawStart']*48000));hi=min(length,round(row['rawEnd']*48000));active=mask[lo:hi];assert active.sum()>0
    values=[a.db(a.rms(x[lo:hi][active]))for x in buffers]
    return dict(line=row['line'],sentence=row.get('sentence'),rawStart=lo/48000,rawEnd=hi/48000,globalStart=(begin+lo)/48000,globalEnd=(begin+hi)/48000,
     timestampActiveFrames=int(active.sum()),actualEncodedMixDbfs=values[0],expectedMixerWaveformDbfs=values[1],knownVoiceStemDbfs=values[2],knownGameStemDbfs=values[3],
     encodedMixTransferDb=values[0]-values[1],sourceSpeechDbfs=row['sourceSpeechDbfs'],processedNarrationSpeechDbfs=row['processedSpeechDbfs'])
   paragraphs=[range_level(row)for row in source_rows[sid]['paragraphs']];sentences=[range_level(row)for row in source_rows[sid]['sentences']]
   rows.append(dict(scene=sid,sourcePcmSha256=scene['rawVoiceSha256'],wordSha256=al[sid]['asrSha256'],windows=windows,paragraphs=paragraphs,sentences=sentences,encodedTransferCandidates=flags,humanListening='pending'))
   clips.append(dict(scene=sid,decodedHardClipSamples=int(np.sum(abs(actual)>=32766/32768)),codecErrorRmsDbfs=a.db(a.rms(actual-expected)),expectedRmsDbfs=a.db(a.rms(expected))))
 byscene={r['scene']:r for r in rows};joins=[]
 for l,r in zip(t['scenes'],t['scenes'][1:]):
  left=byscene[l['id']];right=byscene[r['id']];last=left['sentences'][-1];first=right['sentences'][0];lp=left['paragraphs'][-1];rp=right['paragraphs'][0]
  joins.append(dict(previous=l['id'],next=r['id'],boundary=r['startFrame']/60,range=[r['startFrame']/60-3,r['startFrame']/60+3],
   previousCompleteSentence=last,nextCompleteSentence=first,previousCompleteParagraph=lp,nextCompleteParagraph=rp,
   actualEncodedSentenceDeltaDb=first['actualEncodedMixDbfs']-last['actualEncodedMixDbfs'],expectedMixerSentenceDeltaDb=first['expectedMixerWaveformDbfs']-last['expectedMixerWaveformDbfs'],
   knownVoiceSentenceDeltaDb=first['knownVoiceStemDbfs']-last['knownVoiceStemDbfs'],actualEncodedParagraphDeltaDb=rp['actualEncodedMixDbfs']-lp['actualEncodedMixDbfs'],
   actualWordQuietSpan=first['globalStart']-last['globalEnd'],addedObservationSilence=0,humanListening='pending'))
 result=dict(schemaVersion=1,part=1,inputs=inputs,master=c.rel(master),masterSha256=binding['masterSha256'],asrOriginMasterSha256=selected['masterSha256'],
  decodedFile=c.rel(decoded),decodedSha256=c.sha(decoded),reusedInspectedDecode=reused_decode,sampleRate=48000,channels=2,decodedSamples=decoded_samples,programSamples=total,
  trailingEncoderPaddingSamples=decoded_samples-total,measuredVoicedSampleShift=best,voiceStem=c.rel(voice),voiceStemSha256=c.sha(voice),
  gameStem=c.rel(game),gameStemSha256=c.sha(game),currentAacMeasurement=build['encodedMeasurement'],aacMeasurementInterpretation='Only loudnorm input_i/input_tp describe the existing encoded AAC. output_* values describe a discarded analysis-filter result.',scenes=rows,sourceCodecMetrics=clips,joins=joins,
  encodedTransferCandidateWindows=sum(len(x['encodedTransferCandidates'])for x in rows),
  sourceToProcessedProof=c.rel(c.O/'narration-build.json'),sourceToProcessedProofSha256=c.sha(c.O/'narration-build.json'),
  actualMixStemProof=c.rel(build_file),actualMixStemProofSha256=c.sha(build_file),
  method='Current master actual AAC payload decoded once.400ms/100ms current source-word-active windows; exact known mixer waveform/stems compared. Timestamp-active mix levels are not isolated encoded voice levels. Subtracting known game/brand from lossy AAC is only a residual diagnostic, not measured source separation. Complete-sentence/paragraph join deltas are measurements, not subjective smoothness approval.',
  voiceSpeed=1,extraVoiceFadesOrDucking=False,sourcePcmUnchanged=True,addedBgm=False,wholeMasterAsrFile=c.rel(c.O/'final-master-asr.json'),
  wholeMasterAsrSha256=c.sha(c.O/'final-master-asr.json'),completeRawTextReview='pending separate direct transcript report',humanWholeListening='pending',voiceVisualPace='pending')
 c.save(report_file,result)
 print(json.dumps(dict(sceneCount=len(rows),encodedCandidateWindows=result['encodedTransferCandidateWindows'],sampleShift=best,trailingEncoderPadding=decoded_samples-total,masterSha256=binding['masterSha256'])))
if __name__=='__main__':main()
