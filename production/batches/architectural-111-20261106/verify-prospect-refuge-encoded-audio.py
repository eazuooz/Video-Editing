"""PureCPU encoded-audio clock/DSP/report fixtures; no FFmpeg or actual media."""
import copy,importlib.util,json,tempfile
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prospect_encoded_cpu_fixtures',HERE/'review-prospect-refuge-encoded-audio.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def require(ok):
 if not ok:raise AssertionError('Encoded QA fixture failed')
def check(name,fn):fn();checks.append(name)
def reject(fn):
 try:fn()
 except(ValueError,RuntimeError,AssertionError):return
 raise AssertionError('Invalid encoded QA input accepted')
def packet_fixture():
 stream=dict(codec_name='aac',sample_rate='48000',channels=2,time_base='1/48000',start_pts=0,start_time='0.000000',duration_ts=4096,duration=str(4096/48000),extradata_hash='SHA256:'+'e'*64)
 packets=[]
 for i in range(5):
  packets.append(dict(pts=(i-1)*1024,dts=(i-1)*1024,duration=1024,size='400',flags='KD'if i==0 else'K_',data_hash='SHA256:'+format(i,'064x'),side_data_list=[dict(side_data_type='Skip Samples',skip_samples=1024,discard_padding=0,skip_reason=0,discard_reason=0)]if i==0 else[]))
 return dict(streams=[stream],packets=packets)
data=packet_fixture();good=m.packet_contract(data,4096)
check('actualexplicitcodecskip respected withzeroeffective start',lambda:require(good['explicitInitialSkipSamples']==1024 and good['manualSkipSamples']==0 and good['effectivePacketEndSample']==4096))
check('sameAAC payload/timestamps/skip metadata accepted',lambda:require(m.same_packets(good,copy.deepcopy(good))['identicalPayloadClockAndSkipMetadata']is True))
for name,mutate in [
 ('missing AAC hash',lambda x:x['packets'][1].pop('data_hash')),
 ('missing stream',lambda x:x.__setitem__('streams',[])),
 ('wrong sample rate',lambda x:x['streams'][0].__setitem__('sample_rate','24000')),
 ('mono substitute',lambda x:x['streams'][0].__setitem__('channels',1)),
 ('wrong timebase',lambda x:x['streams'][0].__setitem__('time_base','1/24000')),
 ('nonzero stream start',lambda x:x['streams'][0].__setitem__('start_pts',1)),
 ('one sample packet gap',lambda x:x['packets'][2].__setitem__('pts',1025)),
 ('one sample skip offset',lambda x:x['packets'][0]['side_data_list'][0].__setitem__('skip_samples',1023)),
 ('interior skip',lambda x:x['packets'][2].__setitem__('side_data_list',[dict(side_data_type='Skip Samples',skip_samples=1,discard_padding=0)])),
 ('interior discard',lambda x:x['packets'][2].__setitem__('side_data_list',[dict(side_data_type='Skip Samples',skip_samples=0,discard_padding=1)])),
 ('bool clock',lambda x:x['packets'][2].__setitem__('duration',True)),
 ('invalid negative size',lambda x:x['packets'][2].__setitem__('size','-1')),
]:
 def case(mutate=mutate):
  x=copy.deepcopy(data);mutate(x);reject(lambda:m.packet_contract(x,4096))
 check(name+' rejected',case)
for name,key,value in [('payload','data_hash','SHA256:'+'f'*64),('PTS','pts',123),('skip','side_data_list',[])]:
 changed=copy.deepcopy(good);changed['packetSignature'][0][key]=value
 check('clean/captioned '+name+' difference rejected',lambda changed=changed:reject(lambda:m.same_packets(good,changed)))
check('packetend beyond1codecframe rejected',lambda:reject(lambda:m.packet_contract(data,1)))
frames=24000*3;raw=dict(frames=frames);mix=dict(sha256=m.MIX_SHA,sampleRate=48000,channels=2,subtype='FLOAT',frames=frames*2)
build=dict(topicId='06.02',selectedComponentCount=103,mixWav=mix,rawVoice=raw,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,uniformMixGainDb=0,wordBoundariesShifted=False,compressorUsed=False,voiceSideDuck=False)
t=dict(audio=dict(voice=raw,mix=mix),format=dict(width=1080,height=1920,fps=60),totalFrames=180)
check('exactraw2xmixand60fpsceil accepted',lambda:require(m.validate_grid(build,t)['mixFrames']==144000))
for name,key,value in [('offset','voiceOffsetSeconds',.001),('trim','trimmedSamples',1),('insert','insertedSamples',1),('commonDSPgain','uniformMixGainDb',-.1),('compressor','compressorUsed',True),('voiceDuck','voiceSideDuck',True)]:
 check(name+' rejected',lambda key=key,value=value:reject(lambda:m.validate_grid(dict(build,**{key:value}),t)))
bad=copy.deepcopy(t);bad['totalFrames']+=1
check('onevisualframe clockchange rejected',lambda:reject(lambda:m.validate_grid(build,bad)))
bad=copy.deepcopy(build);bad['mixWav']['sha256']='other'
check('changedactualmixedsource rejected',lambda:reject(lambda:m.validate_grid(bad,t)))
check('decodedshortening retained asflag',lambda:require(bool(m.decoded_grid(1000,999,dict(supported=True,decodedMinusReferenceSamples=0))[1])))
check('onecodecframe tail retained withoutaudio trim',lambda:require(not m.decoded_grid(1000,2023,dict(supported=True,decodedMinusReferenceSamples=0))[1]and m.decoded_grid(1000,2023,dict(supported=True,decodedMinusReferenceSamples=0))[0]['manualSkipSamples']==0))
check('excessive decoded padding flagged',lambda:require(bool(m.decoded_grid(1000,2024,dict(supported=True,decodedMinusReferenceSamples=0))[1])))
check('nonzero comparisonoffset isnever appliedtoaudio',lambda:require(bool(m.decoded_grid(1000,1000,dict(supported=True,decodedMinusReferenceSamples=1))[1])))
check('unsupported alignment remains flagged',lambda:require(bool(m.decoded_grid(1000,1000,dict(supported=False))[1])))
rng=np.random.default_rng(190);reference=rng.normal(0,.08,(144000,2)).astype('float32');shifted=np.pad(reference,((37,0),(0,0)))
a=m.mathqa.estimate_alignment(reference,reference,48000);c=m.mathqa.estimate_alignment(reference,shifted,48000)
check('independentwaveform anchors findzerooffset',lambda:require(a['supported']and a['decodedMinusReferenceSamples']==0 and len(a['anchors'])==6))
check('37sample codec offset ismeasured notguessed1024',lambda:require(c['supported']and c['decodedMinusReferenceSamples']==37))
check('silencecannotprove codec alignment',lambda:require(m.mathqa.estimate_alignment(np.zeros((144000,2)),np.zeros((144000,2)),48000)['supported']is False))
with tempfile.TemporaryDirectory()as d:
 p=Path(d)/'source.bin';p.write_bytes(b'synthetic-only');log=Path(d)/'measurement.log';log.write_text('{"input_i":"-20.90","input_tp":"-2.97","output_i":"-16.00","output_tp":"-1.50"}')
 measured=m.measured_input(log,p)
 check('LUFS/TP usesactualinputnot hypotheticaloutput',lambda:require(measured['inputLufs']==-20.90 and measured['inputTruePeakDbtp']==-2.97 and measured['qualityPass']is False))
 q=m.pin(p);p.write_bytes(b'changed');check('changedactualsourcepin rejected',lambda:reject(lambda:m.bound(q)))
 log.write_text('{"input_i":"NaN","input_tp":"-2.97"}');check('nonfinite actualmeasurement rejected',lambda:reject(lambda:m.measured_input(log,p)))
check('launchgap withoutknowncommand preservesowner',lambda:require(m.legacy.unregistered(dict(phase='launching-owned-cpu-measurement',launchCommand=None))is True))
check('toolcannotrunwithoutCPUowner',lambda:reject(lambda:m.tool(['not-a-tool'],'never-written')))
check('noactualhearing/naturalness iscreatedbygridmethods',lambda:require(m.decoded_grid(1000,1000,dict(supported=True,decodedMinusReferenceSamples=0))[0]['alignmentAppliedToAudio']is False))
target=Path(tempfile.gettempdir())/'encoded-saved-provenance-fixture';manifest_pin=dict(path=str(target.parent/'render-manifest.json'),sha256='a'*64)
ctx=dict(identity=dict(inputs=[manifest_pin]),manifest=dict(timeline=dict(path='timeline.json',sha256='b'*64),outputs=dict(clean=dict(path='clean.mp4',sha256='c'*64),captioned=dict(path='captioned.mp4',sha256='d'*64))),build=dict(mixWav=mix))
old=dict(renderManifest=manifest_pin,timeline=ctx['manifest']['timeline'],masters=ctx['manifest']['outputs'],mixWav=mix,decode=dict(source=ctx['manifest']['outputs']['captioned'],wav=dict(path=str(target/'decoded-encoded-aac.wav'),sha256='e'*64)),packetProof=dict(path=str(target/'audio-packets.json'),sha256='f'*64),numerical=dict(path=str(target/'numerical.json'),sha256='0'*64),output=str(target),artifacts=[dict(file='decoded-encoded-aac.wav',sha256='e'*64),dict(file='audio-packets.json',sha256='f'*64),dict(file='numerical.json',sha256='0'*64)])
check('exactsaved report bindings accepted',lambda:m.saved_bindings(old,ctx,target))
for name,mutate in [
 ('masterpin',lambda x:x['masters']['captioned'].__setitem__('sha256','other')),
 ('timelinepin',lambda x:x['timeline'].__setitem__('sha256','other')),
 ('mixpin',lambda x:x['mixWav'].__setitem__('sha256','other')),
 ('decoder source',lambda x:x['decode']['source'].__setitem__('path','other.mp4')),
 ('outputscope',lambda x:x.__setitem__('output',str(target.parent/'foreign'))),
 ('decodedoutside',lambda x:x['decode']['wav'].__setitem__('path',str(target.parent/'foreign.wav'))),
 ('packetoutside',lambda x:x['packetProof'].__setitem__('path',str(target.parent/'foreign.json'))),
 ('numericaloutside',lambda x:x['numerical'].__setitem__('path',str(target.parent/'foreign.json'))),
 ('decodedSHA',lambda x:x['decode']['wav'].__setitem__('sha256','other')),
]:
 def case(mutate=mutate):
  changed=copy.deepcopy(old);mutate(changed);reject(lambda:m.saved_bindings(changed,ctx,target))
 check('saved '+name+' drift rejected',case)
print(json.dumps(dict(passed=len(checks),checks=checks,sourceSHA256=m.sha(HERE/'review-prospect-refuge-encoded-audio.py'),actualMediaDecoded=False,ffmpegStarted=False,modelLoaded=False,gpuUsed=False),ensure_ascii=False))
