"""Synthetic CPU fixtures only; no profile/model/resource/media subprocess."""
import copy, importlib.util, json, math, os, tempfile, types
from pathlib import Path
os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
import numpy as np
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('solution_encoded_synthetic',HERE/'review-solution-path-encoded-audio-v1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def need(value):
 if not value:raise AssertionError('Synthetic encoded QA fixture failed')
def check(name,fn):fn();checks.append(name)
def reject(fn):
 try:fn()
 except (ValueError,RuntimeError,AssertionError,KeyError,TypeError):return
 raise AssertionError('Invalid encoded QA input accepted')

def packet_fixture():
 stream=dict(codec_name='aac',sample_rate='48000',channels=2,time_base='1/48000',start_pts=0,start_time='0',duration_ts=4096,duration=str(4096/48000),extradata_hash='SHA256:'+'a'*64)
 packets=[dict(pts=(i-1)*1024,dts=(i-1)*1024,duration=1024,size='400',flags='KD' if i==0 else 'K_',data_hash='SHA256:'+format(i,'064x'),side_data_list=[dict(side_data_type='Skip Samples',skip_samples=1024,discard_padding=0)] if i==0 else []) for i in range(5)]
 return dict(streams=[stream],packets=packets)
p=packet_fixture();good=m.packet_contract(p,4096)
check('codec-skip-only zero effective start',lambda:need(good['explicitInitialSkipSamples']==1024 and good['manualSkipSamples']==0))
check('exact shared AAC packets accepted',lambda:need(m.same_packets(good,copy.deepcopy(good))['identicalPayloadClockAndSkipMetadata']))
for name,change in [
 ('missing payload hash',lambda x:x['packets'][1].pop('data_hash')),
 ('one sample PTS gap',lambda x:x['packets'][2].__setitem__('pts',1025)),
 ('wrong codec rate',lambda x:x['streams'][0].__setitem__('sample_rate','24000')),
 ('mono AAC',lambda x:x['streams'][0].__setitem__('channels',1)),
 ('nonzero effective skip',lambda x:x['packets'][0]['side_data_list'][0].__setitem__('skip_samples',1023)),
 ('interior discard',lambda x:x['packets'][2].__setitem__('side_data_list',[dict(side_data_type='Skip Samples',discard_padding=1)])),
 ('boolean clock',lambda x:x['packets'][2].__setitem__('duration',True)),
]:
 def case(change=change):
  x=copy.deepcopy(p);change(x);reject(lambda:m.packet_contract(x,4096))
 check(name+' rejected',case)
x=copy.deepcopy(good);x['packetSignature'][1]['data_hash']='SHA256:'+'b'*64
check('clean/captioned payload difference rejected',lambda:reject(lambda:m.same_packets(good,x)))

rawframes=48*2500
rawmeta=dict(frames=rawframes,sampleRate=24000,channels=1,sampleWidthBytes=2)
mixmeta=dict(frames=rawframes*2,sampleRate=48000,channels=2,subtype='FLOAT',path='synthetic-mix.wav',sha256='a'*64)
build=dict(schemaVersion='11.05-audio-build-v5',topicId='11.05',selectedComponentCount=48,rawVoiceFingerprint=m.VOICE_FP,rawVoice=rawmeta,mixWav=mixmeta,
 voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,uniformMixGainDb=0.,wordBoundariesShifted=False,compressorUsed=False,voiceSideDuck=False,originalRawFilesUnchanged=True)
t=dict(picturePlan=dict(fps=60,totalFrames=(rawframes*60+23999)//24000,audio=dict(mix=mixmeta)),encodedAudioMapping=dict(reference='accepted-body-mix',bodyStartSample=0,bodyEndSample=rawframes*2,wholeAudioFrames=rawframes*2,rate=48000,noAudioPadding=True),assemblyProfile=dict(kind='body-only-portrait-with-integrated-brand',introAudioSamples=0,outroAudioSamples=0,rawBodyPcmPreserved=True))
check('actual variable48-body clock and mapping accepted',lambda:need(m.validate_grid(build,t)['mixFrames']==rawframes*2))
for name,key,value in [('voiceoffset','voiceOffsetSeconds',.00001),('trim','trimmedSamples',1),('insert','insertedSamples',1),('speed','voiceSpeed',1.001),('common gain','uniformMixGainDb',-.1),('compressor','compressorUsed',True),('voice duck','voiceSideDuck',True),('old voice','rawVoiceFingerprint','e51-old')]:
 check(name+' rejected',lambda key=key,value=value:reject(lambda:m.validate_grid(dict(build,**{key:value}),t)))
for key,value in [('bodyStartSample',1),('bodyEndSample',rawframes*2-1),('wholeAudioFrames',rawframes*2+1),('noAudioPadding',False),('rate',24000)]:
 def case(key=key,value=value):
  bad=copy.deepcopy(t);bad['encodedAudioMapping'][key]=value;reject(lambda:m.validate_grid(build,bad))
 check('wrong explicit audio mapping '+key,case)
bad=copy.deepcopy(t);bad.pop('encodedAudioMapping')
check('missing final audio mapping rejected',lambda:reject(lambda:m.validate_grid(build,bad)))
bad=copy.deepcopy(t);bad['picturePlan']['totalFrames']+=1
check('one video-frame clock drift rejected',lambda:reject(lambda:m.validate_grid(build,bad)))
bad=copy.deepcopy(t);bad['picturePlan']['audio']['mix']['sha256']='substituted'
check('changed mix source rejected',lambda:reject(lambda:m.validate_grid(build,bad)))
actual_manifest=dict(format=dict(width=1080,height=1920,fps=60,totalFrames=t['picturePlan']['totalFrames']),encodedAudioMapping=copy.deepcopy(t['encodedAudioMapping']),assemblyProfile=copy.deepcopy(t['assemblyProfile']))
check('actual router picturePlan andmanifest shape accepted',lambda:m.manifest_clock(actual_manifest,t))
for name,change in [('width',lambda x:x['format'].__setitem__('width',1920)),('frame',lambda x:x['format'].__setitem__('totalFrames',1)),('mapping',lambda x:x['encodedAudioMapping'].__setitem__('bodyStartSample',1)),('assembly',lambda x:x['assemblyProfile'].__setitem__('introAudioSamples',48000))]:
 def case(change=change):
  bad=copy.deepcopy(actual_manifest);change(bad);reject(lambda:m.manifest_clock(bad,t))
 check('actualmanifest '+name+' drift rejected',case)

rows=[];takes=[]
for i in range(48):
 a,b=i*2500,(i+1)*2500;p=i*14//48+1;sid=f'p{p:03}-c{i+1:02}'
 row=dict(sceneId=sid,paragraph=p,frames=b-a,destinationSampleRange=[a,b],sourceSampleRange=[0,b-a],prepared48kSampleRange=[a*2,b*2],normalization=dict(constantGainDb=-2.))
 rows.append(row);takes.append(dict(task=dict(sceneId=sid,offsetSample=a,endSample=b),aliasesApplied=False,expectedPrompt=None,globalWords=[dict(text='원문차이',timestamp=[(a+100)/24000,(b-100)/24000])]))
paragraphs=[]
for p in range(1,15):
 group=[r for r in rows if r['paragraph']==p];paragraphs.append(dict(paragraph=p,sceneIds=[r['sceneId'] for r in group],startSample=group[0]['destinationSampleRange'][0],endSample=group[-1]['destinationSampleRange'][1]))
review=dict(takes=takes,paragraphs=paragraphs,boundaryWindows=[dict(task=dict(previousScene=a['sceneId'],nextScene=b['sceneId'],boundarySample=a['destinationSampleRange'][1])) for a,b in zip(rows,rows[1:])])
q=m.primitives();windows,unknown=m.window_plan(review,rows,q)
check('48take14paragraph47join clock covers actual body',lambda:(m.component_grid(rows,rawframes),need(sum(w['kind']=='join' for w in windows)==47 and sum(w['kind']=='paragraph' for w in windows)==14)))
check('literal differences unchanged in window plan',lambda:need(all(w['recognizedText']=='원문차이' for w in windows if w['kind']=='word')))
bad=copy.deepcopy(rows);bad[1]['destinationSampleRange'][0]+=1
check('one raw sample gap rejected',lambda:reject(lambda:m.component_grid(bad,rawframes)))
bad=copy.deepcopy(rows);bad[1]['prepared48kSampleRange'][0]+=1
check('one resampled sample drift rejected',lambda:reject(lambda:m.component_grid(bad,rawframes)))
bad=copy.deepcopy(review);bad['takes'][0]['globalWords'][0]['timestamp']=[None,None]
ww,uu=m.window_plan(bad,rows,q)
check('unsupported words explicit while all take clocks retained',lambda:need(len(uu)==1 and sum(w['kind']=='take' for w in ww)==48 and len([w for w in ww if w['kind']=='word'])==47))
bad=copy.deepcopy(review);bad['boundaryWindows'][0]['task']['boundarySample']+=1
check('join sample mismatch rejected',lambda:reject(lambda:m.window_plan(bad,rows,q)))

rng=np.random.default_rng(11105);raw=rng.normal(0,.05,(rawframes,1)).astype('float32')
normalized=(raw*10**(-2/20)).astype('float32');prepared=np.repeat(np.repeat(normalized,2,axis=0),2,axis=1)
voice=prepared*.5;music=np.zeros_like(voice);mix=voice+music
ctx=dict(mathqa=q,rows=rows,build=dict(voiceGlobalGain=dict(constantGainDb=20*math.log10(.5))),windows=windows,unknown=[])
arrays=dict(normalized=normalized,prepared=prepared,voice=voice,music=music,mix=mix)
numeric=m.compare_arrays(ctx,arrays,raw,mix.copy())
check('six actual waveform anchors zerooffset in synthetic identity',lambda:need(numeric['alignment']['supported'] and numeric['alignment']['decodedMinusReferenceSamples']==0 and len(numeric['alignment']['anchors'])==6))
check('same scalar/stem arithmetic residuals zero',lambda:need(all(v['maximumAbsolute']==0 for v in numeric['residuals'].values())))
check('allword take para joins measured with tail',lambda:need(numeric['countByKind']==dict(word=48,take=48,paragraph=14,join=47,tail=1)))
check('all47actualjoin raw/stem/decoder endpoint pairs retained',lambda:need(len([r for r in numeric['windowComparisons'] if r['kind']=='join' and set(r['boundarySamples'])=={'canonical','normalized','prepared','voice','music','mix','decoded'}])==47))
check('tail actual raw/mix/decoder endpoints retained',lambda:need(numeric['decoderTail']['finalRawSample']==raw[-1].tolist() and numeric['decoderTail']['finalBodyMixSample']==mix[-1].tolist() and numeric['decoderTail']['lastDecodedSample']==mix[-1].tolist()))
check('no numerical speech or hearing approval',lambda:need('humanApproval' not in numeric and numeric['decodedGrid']['alignmentAppliedToAudio'] is False))
shifted=np.pad(mix,((37,0),(0,0)));changed=m.compare_arrays(ctx,arrays,raw,shifted)
check('37sample offset measured and retained not repaired',lambda:need(changed['alignment']['decodedMinusReferenceSamples']==37 and any(f['kind']=='encoded-nonzero-comparison-offset' for f in changed['flags'])))
bad=copy.deepcopy(arrays);bad['normalized'][111,0]+=.1
badnum=m.compare_arrays(ctx,bad,raw,mix)
check('unexpected scalar DSP flagged',lambda:need(badnum['residuals']['rawToScalar']['exceedsKnownStemTolerance']))
badmix=mix.copy();badmix[200:4500]*=2
badnum=m.compare_arrays(ctx,arrays,raw,badmix)
check('encoded local word level loss/change retained',lambda:need(any(f['kind']=='encoded-local-level-delta' for f in badnum['flags'])))
check('silence cannot establish alignment',lambda:need(q.estimate_alignment(np.zeros_like(mix),np.zeros_like(mix),48000)['supported'] is False))
check('codec tail metadata never applies padding or trim',lambda:need(not m.decoded_grid(1000,2023,dict(supported=True,decodedMinusReferenceSamples=0))[1] and m.decoded_grid(1000,2023,dict(supported=True,decodedMinusReferenceSamples=0))[0]['manualSkipSamples']==0))
check('shortened decoder output retained as flag',lambda:need(bool(m.decoded_grid(1000,999,dict(supported=True,decodedMinusReferenceSamples=0))[1])))
with tempfile.TemporaryDirectory() as folder:
 p=Path(folder)/'synthetic.bin';p.write_bytes(b'synthetic-only');log=Path(folder)/'loudness.log'
 log.write_text('{"input_i":"-20.9","input_tp":"-2.97","output_i":"-16","output_tp":"-1.5"}')
 check('input LUFS not hypothetical normalized output',lambda:need(m.measured_input(log,p)['inputLufs']==-20.9))
 saved=m.pin(p);p.write_bytes(b'changed');check('source hash change declined',lambda:reject(lambda:m.bound(saved)))
 log.write_text('{"input_i":"NaN","input_tp":"-2.97"}')
 check('nonfinite loudness declined',lambda:reject(lambda:m.measured_input(log,p)))

target=Path(tempfile.gettempdir()).resolve()/'solution-encoded-documentary-fixture'
manifestpin=dict(path=str(target.parent/'render-manifest.json'),sha256='a'*64)
savedctx=dict(identity=dict(inputs=[manifestpin]),manifest=dict(timeline=dict(path='timeline.json',sha256='b'*64),outputs=dict(clean=dict(path='clean.mp4',sha256='c'*64),captioned=dict(path='captioned.mp4',sha256='d'*64))),build=dict(mixWav=mixmeta))
saved=dict(renderManifest=manifestpin,timeline=savedctx['manifest']['timeline'],masters=savedctx['manifest']['outputs'],mixWav=mixmeta,output=str(target),
 decode=dict(source=savedctx['manifest']['outputs']['captioned'],wav=dict(path=str(target/'decoded-encoded-aac.wav'),sha256='e'*64)),packetProof=dict(path=str(target/'audio-packets.json'),sha256='f'*64),numerical=dict(path=str(target/'numerical.json'),sha256='0'*64),
 artifacts=[dict(file='decoded-encoded-aac.wav',sha256='e'*64),dict(file='audio-packets.json',sha256='f'*64),dict(file='numerical.json',sha256='0'*64)])
check('exact saved documentary bindings accepted',lambda:m.saved_bindings(saved,savedctx,target))
for name,change in [('master',lambda x:x['masters']['captioned'].__setitem__('sha256','other')),('timeline',lambda x:x['timeline'].__setitem__('sha256','other')),('mix',lambda x:x['mixWav'].__setitem__('sha256','other')),('decoder outside',lambda x:x['decode']['wav'].__setitem__('path',str(target.parent/'foreign.wav'))),('artifact hash',lambda x:x['numerical'].__setitem__('sha256','other'))]:
 def case(change=change):
  bad=copy.deepcopy(saved);change(bad);reject(lambda:m.saved_bindings(bad,savedctx,target))
 check('saved '+name+' substitution rejected',case)

with tempfile.TemporaryDirectory() as folder:
 original_dest=m.DEST;m.DEST=Path(folder).resolve()
 try:
  fp='a'*64;target=m.DEST/fp[:24];target.mkdir();work=m.DEST/('work-'+fp[:16]+'-'+'b'*10)
  receiptctx=dict(fingerprint=fp,ff=m.DEST/'ffmpeg.exe',probe=m.DEST/'ffprobe.exe',manifest=dict(outputs=dict(clean=dict(path='actual-clean.mp4'),captioned=dict(path='actual-captioned.mp4'))),build=dict(output='accepted-stems',mixWav=dict(path='accepted-mix.wav')))
  commands=m.expected_commands(receiptctx,work);old=dict(workOrigin=str(work),toolReceipts={})
  for i,(role,command) in enumerate(commands.items()):
   key=f'{i:010x}';request=target/(key+'.request.json');request.write_text(json.dumps(dict(command=command,inputIdentitySHA256=fp)))
   out=target/(key+'.stdout.bin');err=target/(key+'.stderr.bin');out.write_bytes(b'{}' if role in ('clean','captioned') else b'');err.write_bytes(b'{"input_i":"-21","input_tp":"-3"}')
   if role in ('clean','captioned'):(target/(role+'-audio-packets.json')).write_bytes(out.read_bytes())
   if role in ('voice','mix','decodedAac'):(target/(role+'-loudness.log')).write_bytes(err.read_bytes())
   result=target/(key+'.result.json');result.write_text(json.dumps(dict(exitCode=0,request=dict(path=str(work/request.name),sha256=m.sha(request)),stdout=dict(path=str(work/out.name),sha256=m.sha(out)),stderr=dict(path=str(work/err.name),sha256=m.sha(err)))))
   old['toolReceipts'][role]=m.pin(result)
  check('all actual-command receipt chains accepted synthetically',lambda:m.verify_tool_receipts(old,receiptctx,target))
  bad=copy.deepcopy(old);bad['toolReceipts'].pop('decode')
  check('missing decode receipt rejected',lambda:reject(lambda:m.verify_tool_receipts(bad,receiptctx,target)))
  log=target/'voice-loudness.log';log.write_bytes(b'substituted')
  check('measurement log must match actual tool stderr',lambda:reject(lambda:m.verify_tool_receipts(old,receiptctx,target)))
  log.write_bytes((target/'0000000003.stderr.bin').read_bytes())
  request=target/'0000000000.request.json';data=json.loads(request.read_text());data['command'].append('-foreign');request.write_text(json.dumps(data))
  result=target/'0000000000.result.json';data=json.loads(result.read_text());data['request']['sha256']=m.sha(request);result.write_text(json.dumps(data));old['toolReceipts']['clean']=m.pin(result)
  check('rebound altered actual-command receipt rejected',lambda:reject(lambda:m.verify_tool_receipts(old,receiptctx,target)))
 finally:m.DEST=original_dest

with tempfile.TemporaryDirectory() as folder:
 class Worker:
  record={}
  def update(self,**value):self.record.update(value)
 worker=Worker();old_active=m.ACTIVE;old_popen=m.subprocess.Popen;m.ACTIVE=worker
 fakeproducer=types.SimpleNamespace(fresh_serial_gate=lambda *args:None,child_identity=lambda *args:(_ for _ in ()).throw(RuntimeError('injected registration failure')))
 ctxgap=dict(ff=Path(folder).resolve()/'ffmpeg.exe',probe=Path(folder).resolve()/'ffprobe.exe',producer=fakeproducer,fingerprint='a'*64)
 try:
  m.subprocess.Popen=lambda *args,**kwargs:types.SimpleNamespace(pid=12345)
  check('launch-registration failure propagates',lambda:reject(lambda:m.run_tool(ctxgap,None,None,[ctxgap['ff'],'synthetic-no-process'],Path(folder))))
  check('launch gap retains exact command and unknown child marker',lambda:need(worker.record['phase']=='launching-owned-audio-tool' and worker.record['child'] is None and worker.record['launchCommand']==[str(ctxgap['ff']),'synthetic-no-process']))
 finally:m.ACTIVE=old_active;m.subprocess.Popen=old_popen

check('missing final manifest stops before profile/resource/media',lambda:reject(lambda:m.prepare('missing-render-manifest.json')))
original_sha=m.sha
try:
 m.sha=lambda path:'0'*64 if Path(path).resolve()==Path(m.__file__).resolve() else original_sha(path)
 check('imported own-source drift rejected beforeidentity canpinnewbytes',lambda:reject(lambda:m.check_sources()))
finally:m.sha=original_sha
check('tool cannot launch without owner',lambda:reject(lambda:m.run_tool({},None,None,[],Path('never-created'))))
print(json.dumps(dict(passed=len(checks),checks=checks,sourceSHA256=m.sha(HERE/'review-solution-path-encoded-audio-v1.py'),actualMediaRead=False,profileCalled=False,resourceCalled=False,ffmpegStarted=False,modelLoaded=False,gpuUsed=False),ensure_ascii=False))
