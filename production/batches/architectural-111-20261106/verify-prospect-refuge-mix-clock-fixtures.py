"""Small synthetic PCM/FLOAT lineage faults, no models or media processes."""
import copy,hashlib,importlib.util,json,math,pathlib,sys,tempfile,unittest,wave
from types import SimpleNamespace
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('clock_under_test',HERE/'verify-prospect-refuge-mix-clock.py');clock=importlib.util.module_from_spec(s);s.loader.exec_module(clock)

def stereo(x,rate):return np.repeat(resample_poly(x,2,1).astype(np.float32)[:,None],2,axis=1)
def match(x,rate,profile):return(x*10**(2/20)).astype(np.float32),dict(constantGainDb=2)

class ActualSampleLineage(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.folder=pathlib.Path(self.temp.name);self.raw=self.folder/'raw';self.raw.mkdir();self.audio=SimpleNamespace(base=SimpleNamespace(match_paragraph=match,stereo_voice=stereo),PROFILE={});parts=[];rows=[];self.pcm=[];norm=[];cursor=0
  for i in range(103):
   sid=f'p001-c{i+1:03}';data=np.array([0,400,-900,1600,2500,-1400,700,0,0,-200,160,0],dtype='<i2').tobytes();p=self.raw/(sid+'.wav')
   with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(data)
   n=len(data)//2;q=dict(path=str(p.resolve()),sha256=clock.sha(p),pcmSHA256=hashlib.sha256(data).hexdigest(),frames=n,sampleRate=24000,channels=1,sampleWidthBytes=2);a,b=cursor,cursor+n;text='Synthetic complete speech component.'
   parts.append(dict(sceneId=sid,logicalSceneId='logical'+str(min(i,95)),paragraph=1,canonicalKo=text,startSample=a,endSample=b,rawWav=q));values,measure=match(np.frombuffer(data,dtype='<i2').astype(np.float32)/32768.,24000,{})
   name=sid+'-normalized.wav';sf.write(self.folder/name,values,24000,subtype='FLOAT');norm.append(values);self.pcm.append(data)
   rows.append(dict(sceneId=sid,paragraph=1,text=text,rawTake=q['path'],rawTakeSHA256=q['sha256'],rawPcmSHA256=q['pcmSHA256'],sourceSampleRange=[0,n],destinationSampleRange=[a,b],prepared48kSampleRange=[2*a,2*b],frames=n,rate=24000,startSeconds=a/24000,endSeconds=b/24000,normalization=measure,normalizedTake=name,normalizedTakeSHA256=clock.sha(self.folder/name),normalizedTakeFloat32PcmSHA256=clock.pcm_sha(values)));cursor=b
  aggregate=self.raw/'aggregate.wav'
  with wave.open(str(aggregate),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b''.join(self.pcm))
  rawq=dict(path=str(aggregate.resolve()),sha256=clock.sha(aggregate),pcmSHA256=hashlib.sha256(b''.join(self.pcm)).hexdigest(),frames=cursor,sampleRate=24000,channels=1,sampleWidthBytes=2)
  self.voice=dict(fingerprint='synthetic-current-voice',aggregateWav=rawq,timing=dict(path='synthetic-timing',sha256='a'*64));self.timing=dict(physicalComponents=parts,sentences=[{}for _ in range(96)],audioClock=dict(rawSampleRate=24000,totalRawSamples=cursor,mixedAudioTimingAccepted=False),totalFrames=math.ceil(cursor/400))
  self.lines=dict(componentCount=103,voiceFingerprint=self.voice['fingerprint'],rawCanonical=rawq,rawRate=24000,frames=cursor,components=rows,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,wordBoundariesShifted=False,compressorUsed=False,voiceSideDuck=False,voiceSpeed=1,amplitudeOnlyScalarCopies=True,normalizedCopyOnly=True,originalRawFilesUnchanged=True)
  normalized=np.concatenate(norm);prepared=stereo(normalized,24000);gain=1.5;stem=prepared*10**(gain/20);music=np.zeros_like(stem)+np.float32(.0003);mixed=stem+music
  self.data={'narration-component-normalized.wav':(normalized,24000),'narration-prepared-stem.wav':(prepared,48000),'narration-stem.wav':(stem,48000),'music-stem.wav':(music,48000),'final-mix.wav':(mixed,48000)}
  for name,(values,rate)in self.data.items():sf.write(self.folder/name,values,rate,subtype='FLOAT')
  self.mix=dict(selectedComponentCount=103,rawVoiceFingerprint=self.voice['fingerprint'],rawVoice=rawq,canonicalTiming=self.voice['timing'],voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,wordBoundariesShifted=False,compressorUsed=False,voiceSideDuck=False,uniformMixGainDb=0,normalizedVoiceFrames=cursor,normalizedVoiceRate=24000,mixFrames=cursor*2,mixRate=48000,durationSeconds=cursor/24000,voiceGlobalGain=dict(constantGainDb=gain),pcmLineage=dict(voiceOffsetSamples=0,rawToPreparedSampleRatio=[2,1],voiceSpeed=1),videoFrameTarget=dict(fps=60,totalFrames=math.ceil(cursor/400),noAudioTailPadding=True),artifacts={p.name:dict(file=p.name,sha256=clock.sha(p))for p in self.folder.glob('*.wav')})
  for key,name in [('normalized24kMonoFloat32SHA256','narration-component-normalized.wav'),('prepared48kStereoFloat32SHA256','narration-prepared-stem.wav'),('finalVoice48kStereoFloat32SHA256','narration-stem.wav'),('finalMusic48kStereoFloat32SHA256','music-stem.wav'),('finalMix48kStereoFloat32SHA256','final-mix.wav')]:self.mix['pcmLineage'][key]=clock.pcm_sha(self.data[name][0])
  self.mix['mixWav']=dict(path=str((self.folder/'final-mix.wav').resolve()),sha256=clock.sha(self.folder/'final-mix.wav'),sampleRate=48000,channels=2,frames=cursor*2,subtype='FLOAT')
 def tearDown(self):self.temp.cleanup()
 def run_proof(self):return clock.sample_lineage(self.timing,self.voice,self.mix,self.lines,self.folder,self.audio)
 def corrupt(self,name,values,lineage=None):
  rate=self.data[name][1];sf.write(self.folder/name,values,rate,subtype='FLOAT');self.mix['artifacts'][name]['sha256']=clock.sha(self.folder/name)
  if lineage:self.mix['pcmLineage'][lineage]=clock.pcm_sha(values)
  if name=='final-mix.wav':self.mix['mixWav']['sha256']=clock.sha(self.folder/name)
 def test_exact103_scalar_concat_whole_resample_and_mix_pass(self):
  original=copy.deepcopy(self.timing);r=self.run_proof();self.assertEqual(r['componentCount'],103);self.assertEqual(r['logicalGroupCount'],96);self.assertTrue(r['wholeAggregateResampleOnce']);self.assertEqual(self.timing,original);self.assertFalse(self.timing['audioClock']['mixedAudioTimingAccepted'])
 def test_wrong103_count_rejected(self):
  self.lines['components'].pop()
  with self.assertRaisesRegex(clock.Pending,'103 physical'):self.run_proof()
 def test_same_length_source_range_shift_rejected(self):
  self.lines['components'][20]['destinationSampleRange'][0]+=1
  with self.assertRaisesRegex(clock.Pending,'sample range'):self.run_proof()
 def test_false_two_to_one_component_clock_rejected(self):
  self.lines['components'][20]['prepared48kSampleRange'][0]+=1
  with self.assertRaisesRegex(clock.Pending,'sample range'):self.run_proof()
 def test_changed_normalized_bytes_even_with_new_hash_rejected(self):
  row=self.lines['components'][3];p=self.folder/row['normalizedTake'];x,r=sf.read(p,dtype='float32');x[2]+=.001;sf.write(p,x,r,subtype='FLOAT');q=self.mix['artifacts'][p.name];q['sha256']=row['normalizedTakeSHA256']=clock.sha(p);row['normalizedTakeFloat32PcmSHA256']=clock.pcm_sha(x)
  with self.assertRaisesRegex(clock.Pending,'exact accepted whole-component scalar'):self.run_proof()
 def test_shifted_concat_even_with_rewritten_lineage_rejected(self):
  self.corrupt('narration-component-normalized.wav',np.roll(self.data['narration-component-normalized.wav'][0],1),'normalized24kMonoFloat32SHA256')
  with self.assertRaisesRegex(clock.Pending,'synthetic joins'):self.run_proof()
 def test_same_length_resample_shift_rejected(self):
  self.corrupt('narration-prepared-stem.wav',np.roll(self.data['narration-prepared-stem.wav'][0],1,axis=0),'prepared48kStereoFloat32SHA256')
  with self.assertRaisesRegex(clock.Pending,'zero-offset'):self.run_proof()
 def test_per_take_resample_cannot_replace_whole_joined_resample(self):
  wrong=np.concatenate([stereo(x,24000)for x in np.split(self.data['narration-component-normalized.wav'][0],103)])
  self.assertFalse(np.array_equal(wrong,self.data['narration-prepared-stem.wav'][0]));self.corrupt('narration-prepared-stem.wav',wrong,'prepared48kStereoFloat32SHA256')
  with self.assertRaisesRegex(clock.Pending,'whole-signal resample'):self.run_proof()
 def test_nondeclared_voice_gain_rejected(self):
  self.corrupt('narration-stem.wav',self.data['narration-stem.wav'][0]*np.float32(.95),'finalVoice48kStereoFloat32SHA256')
  with self.assertRaisesRegex(clock.Pending,'declared uniform scalar'):self.run_proof()
 def test_same_grid_mix_hidden_sample_change_rejected(self):
  x=self.data['final-mix.wav'][0].copy();x[120]+=np.float32(.001);self.corrupt('final-mix.wav',x,'finalMix48kStereoFloat32SHA256')
  with self.assertRaisesRegex(clock.Pending,'undeclared sample/time change'):self.run_proof()
 def test_nonzero_uniform_mix_gain_rejected(self):
  self.mix['uniformMixGainDb']=-.1
  with self.assertRaisesRegex(clock.Pending,'zero-offset2x'):self.run_proof()
 def test_no_audio_tail_padding_for_visual_ceil(self):
  self.mix['videoFrameTarget']['noAudioTailPadding']=False
  with self.assertRaisesRegex(clock.Pending,'audio padding'):self.run_proof()
 def test_default_readonly_preflight_does_not_start_process(self):
  import contextlib,io
  from unittest.mock import patch
  with patch.object(sys,'argv',[str(clock.__file__)]),patch('subprocess.Popen')as popen,contextlib.redirect_stdout(io.StringIO())as out:clock.main()
  self.assertFalse(json.loads(out.getvalue())['ready']);popen.assert_not_called()
 def test_proof_for_another_caption_input_rejected_before_derivation(self):
  from unittest.mock import patch
  cp=self.folder/'caption.json';cp.write_text('{}',encoding='utf8');ap=self.folder/'audio.json';ap.write_text('{}',encoding='utf8');pp=self.folder/'proof.json';pp.write_text(json.dumps(dict(schemaVersion=clock.SCHEMA,topicId='06.02',captionTiming=clock.pin(cp),audioBuild=clock.pin(ap))),encoding='utf8')
  with patch.object(clock,'prepare')as derive:
   with self.assertRaisesRegex(clock.Pending,'different timing'):clock.verify_existing(pp,self.folder/'another-caption.json',ap)
   derive.assert_not_called()
 def test_modified_existing_clock_receipt_rejected_even_when_input_pins_match(self):
  from unittest.mock import patch
  cp=self.folder/'caption.json';cp.write_text('{}',encoding='utf8');ap=self.folder/'audio.json';ap.write_text('{}',encoding='utf8');fresh=dict(schemaVersion=clock.SCHEMA,topicId='06.02',captionTiming=clock.pin(cp),audioBuild=clock.pin(ap),actualListening=False,fingerprint='f'*64);pp=self.folder/'raw-mix-clock-proofs-v2'/fresh['fingerprint'][:24]/'clock-proof.json';pp.parent.mkdir(parents=True);old=dict(fresh,actualListening=True);pp.write_text(json.dumps(old),encoding='utf8')
  with patch.object(clock,'MEDIA',self.folder),patch.object(clock,'prepare',return_value=fresh):
   with self.assertRaisesRegex(clock.Pending,'Stale/modified'):clock.verify_existing(pp,cp,ap)

if __name__=='__main__':unittest.main(verbosity=2)
