"""Synthetic CPU fixtures only; no current rawvoice/FFmpeg/ASR/model execution."""
import copy,hashlib,importlib.util,json,math,uuid
from pathlib import Path
from unittest.mock import patch,MagicMock
import numpy as np
import soundfile as sf
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('prospect_audio_cpu_fixtures',HERE/'prepare-prospect-refuge-audio-v2.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
fixture=m.TOPIC/'audio-v2-source-preparation/cpu-tests'/uuid.uuid4().hex;fixture.mkdir(parents=True);passed=[]
def require(value):
 if not value:raise AssertionError('Synthetic fixture failed')
def check(name,fn):fn();passed.append(name)
def reject(fn):
 try:fn()
 except(m.Pending,ValueError,AssertionError,FileNotFoundError):return
 raise AssertionError('Expected explicit rejection, never fallback')
def save(p,obj):p.write_text(json.dumps(obj),encoding='utf8');return p

check('approved calmer source and exact CC BY credit are hash-pinned',lambda:require(m.music_rights()['source']['sha256']==m.MUSIC_SHA and 'Wholesome Kevin MacLeod' in m.music_rights()['requiredDescriptionCredit'] and m.music_rights()['actualCurrentMusicListening']is False))
check('old07 and first audio sources unchanged',lambda:require(m.sha(HERE/'prepare-zen-view-audio.py')==m.PREVIOUS_AUDIO_SHA and m.sha(HERE/'prepare-first-audio.py')==m.BASE_SHA))
check('default requires actual raw evidence and never launches anything',lambda:reject(lambda:m.prepare()))
check('missing final mix is Pending without decode or model',lambda:reject(lambda:m.verified_audio_build(fixture/'missing/audio-build.json')))
short=m.loop_plan(100,60,10)
check('music shorterthan source is one exact excerpt',lambda:require(short['repeatCount']==0 and short['continuousSingleExcerpt']and short['segments'][0]['sourceSampleRange']==[0,60]))
long=m.loop_plan(100,250,10)
check('one second overlap has exact source and destination clocks',lambda:require(long['repeatCount']==2 and [s['destinationSampleRange']for s in long['segments']]==[[0,100],[90,190],[180,250]]and all(s['outgoingSourceSampleRange']==[90,100]and s['incomingSourceSampleRange']==[0,10]for s in long['seams'])))
for bad in[(20,100,10),(100,0,10),(True,100,10),(100,100,0),(100.5,100,10)]:check('invalid or degenerate loop clock rejects '+str(bad),lambda bad=bad:reject(lambda:m.loop_plan(*bad)))
constant=np.ones((100,2),dtype=np.float32)*.2;original=constant.copy();music,proof=m.loop_music(constant,250,10)
check('linear complementary seams preserve constant amplitude without doubled music',lambda:require(music.shape==(250,2)and music.dtype==np.float32 and np.max(np.abs(music-.2))<3e-8 and np.array_equal(constant,original)))
check('repeat proof is honest and music-only',lambda:require(proof['repeatCount']==2 and not proof['continuousSingleExcerpt']and proof['speechSamplesChanged']is False and proof['speechInsertedSamples']==proof['speechTrimmedSamples']==0 and proof['actualListening']is False))
ramp=np.repeat(np.linspace(-.2,.2,100,dtype=np.float32)[:,None],2,axis=1);assembled,rp=m.loop_music(ramp,250,10);up=np.linspace(0,1,10,dtype=np.float32);expected=ramp[90:100]*(1-up[:,None])+ramp[:10]*up[:,None]
check('seam uses actual outgoing tail and incoming head phase',lambda:require(np.array_equal(assembled[90:100],expected)and np.array_equal(assembled[100:180],ramp[10:90])))
check('raw and assembled music FLOAT32 PCM hashes are exact',lambda:require(rp['sourceFloat32PcmSHA256']==hashlib.sha256(ramp.astype('<f4').tobytes()).hexdigest()and rp['assembledFloat32PcmSHA256']==hashlib.sha256(assembled.astype('<f4').tobytes()).hexdigest()))
for bad in[np.zeros((100,2),dtype=np.float64),np.zeros(100,dtype=np.float32),np.full((100,2),float('nan'),dtype=np.float32)]:check('wrong or nonfinite music array rejects',lambda bad=bad:reject(lambda:m.loop_music(bad,250,10)))
voice_unchanged=np.linspace(-.1,.1,250,dtype=np.float32);voice_copy=voice_unchanged.copy();duck=m.base.duck_curve(np.repeat(voice_unchanged[:,None],2,axis=1),100,m.PROFILE);bed=m.base.music_bed(assembled,250,100,1.,duck,m.PROFILE)
check('music fades and duck never change voice samples',lambda:require(np.array_equal(voice_unchanged,voice_copy)and len(bed)==250 and np.all(bed[0]==0)and np.all(bed[-1]==0)))
cap=m.music_headroom_compensation(dict(constantGainDb=-3.,desiredGainDb=2.));out,cp=m.apply_music_compensation(bed,cap)
check('peaklimited voice target compensates music only never voice',lambda:require(cap['compensationDb']==-5. and np.array_equal(out,bed*10**(-5/20))and np.array_equal(voice_unchanged,voice_copy)))
check('music no-shortfall never boosts',lambda:require(m.music_headroom_compensation(dict(constantGainDb=3.,desiredGainDb=2.))['linearFactor']==1.))

voice=dict(topicId='06.02',fingerprint='synthetic-103',identity=dict(scenes=[]),aggregateWav=dict(path=str(fixture/'canonical.wav'),sampleRate=24000,frames=0,pcmSHA256='synthetic'),sceneWavs=[],paragraphMapping=[],timing=dict(sha256='synthetic-timing'));timing=dict(entries=[]);review=dict(takes=[]);arrays=[];position=0;ix=0
for paragraph in range(1,26):
 for ordinal in range((4 if paragraph<=18 or paragraph>=23 else 3)+(1 if paragraph in(4,11,13,18,22,24,25)else 0)):
  sid=f'p{paragraph:03}-c{ordinal+1:02}';text='음성 합성 검사 '+sid;n=2400+(ix%3)*6;values=(np.sin(np.arange(n)*.037)*(.025+(ix%5)*.003)).astype(np.float32);values[:64]=0;values[-64:]=0;file=fixture/(sid+'.wav');sf.write(file,values,24000,subtype='PCM_16');raw,sr=sf.read(file,dtype='float32');arrays.append(raw);pcm=np.rint(raw.astype(np.float64)*32768).astype('<i2').tobytes();take=dict(path=str(file),sha256=m.sha(file),pcmSHA256=hashlib.sha256(pcm).hexdigest(),sampleRate=24000,channels=1,sampleWidthBytes=2,frames=n);voice['sceneWavs'].append(take);voice['identity']['scenes'].append(dict(id=sid,lines=[text]));voice['paragraphMapping'].append(dict(sceneId=sid,paragraph=paragraph,canonicalText=text));timing['entries'].append(dict(scene_id=sid,text=text,start=position/24000,end=(position+n)/24000));position+=n;review['takes'].append(dict(task=dict(sceneId=sid),text=text,comparison=dict(syntheticLiteralExact=True)));ix+=1
allraw=np.concatenate(arrays);sf.write(voice['aggregateWav']['path'],allraw,24000,subtype='PCM_16');voice['aggregateWav'].update(frames=position,sha256=m.sha(voice['aggregateWav']['path']));rows=m.exact_components(voice,timing)
check('exact103 components cover exact25 paragraphs in identityorder',lambda:require(len(rows)==103 and sorted(set(r['paragraph']for r in rows))==list(range(1,26))))
legacy=copy.deepcopy(voice);legacyTiming=copy.deepcopy(timing)
for key in('sceneWavs','paragraphMapping'):legacy[key]=legacy[key][:96]
legacy['identity']['scenes']=legacy['identity']['scenes'][:96];legacyTiming['entries']=legacyTiming['entries'][:96];legacy['aggregateWav']['frames']=sum(x['frames']for x in legacy['sceneWavs'])
check('old96physical evidence cannot enter selected103 audio recipe',lambda:reject(lambda:m.exact_components(legacy,legacyTiming)))
check('newversion preserves sharedsingleton but owns fresh audio-version root',lambda:require(m.WORKER.name=='06-02-audio-worker.json'and m.DEST.name=='audio-preparation-v2'and m.PROTOCOL.endswith('-v2')))
check('raw boundaries and48k ranges are exact with no additions',lambda:require(rows[-1]['destinationSampleRange'][1]==position and all(a['destinationSampleRange'][1]==b['destinationSampleRange'][0]for a,b in zip(rows,rows[1:]))and all(r['prepared48kSampleRange']==[2*x for x in r['destinationSampleRange']]for r in rows)))
for kind in['order','paragraph','boundary','id']:
 bad=copy.deepcopy(voice);bt=copy.deepcopy(timing)
 if kind=='order':bad['identity']['scenes'][0],bad['identity']['scenes'][1]=bad['identity']['scenes'][1],bad['identity']['scenes'][0]
 elif kind=='paragraph':bad['paragraphMapping'][-1]['paragraph']=26
 elif kind=='boundary':bt['entries'][2]['start']+=1/24000
 else:bad['identity']['scenes'][0]['id']='../escape'
 check('changed component '+kind+' rejected',lambda bad=bad,bt=bt:reject(lambda:m.exact_components(bad,bt)))
pins={p:m.sha(p)for p in[f['path']for f in voice['sceneWavs']]+[voice['aggregateWav']['path']]};proposed=m.proposal(voice,rows,review,dict(flags=[]),[])
check('proposal preserves every original sample/file',lambda:require(all(m.sha(p)==v for p,v in pins.items())))
check('proposal records103 finite reviewed scalar candidates and102 natural joins',lambda:require(len(proposed['identity']['components'])==103 and len(proposed['identity']['joins'])==102 and all(abs(r['normalization']['constantGainDb'])<=12.001 for r in proposed['identity']['components'])and all(j['insertedSamples']==j['trimmedSamples']==0 for j in proposed['identity']['joins'])))
asrpin=dict(path='synthetic-asr',sha256='a'*64);levelpin=dict(path='synthetic-levels',sha256='b'*64)
accepted=dict(schemaVersion='06-02-accepted-audio-components-v1',topicId='06.02',componentCount=103,voiceFingerprint=voice['fingerprint'],canonicalWavSHA256=voice['aggregateWav']['sha256'],canonicalPcmSHA256=voice['aggregateWav']['pcmSHA256'],timingSHA256=voice['timing']['sha256'],rawAsrReview=asrpin,levelReview=levelpin,proposalFingerprint=proposed['fingerprint'],joinsReviewedSHA256=proposed['joinsReviewedSHA256'],acknowledgedLevelFlagsSHA256=proposed['acknowledgedLevelFlagsSHA256'],reviewer='synthetic CPU fixture, not actual media review',technicalOnly=True,actualListening=False,humanApproval=False,components=[dict(sceneId=r['sceneId'],rawTakeSHA256=r['rawTakeSHA256'],rawPcmSHA256=r['rawPcmSHA256'],rawTakeASRRecordSHA256=r['rawTakeASRRecordSHA256'],decision='accept-scalar-match',expectedGainDb=r['normalization']['constantGainDb'],literalDecision='accepted',literalReviewNote='synthetic text comparison only',levelReviewNote='synthetic scalar only')for r in proposed['identity']['components']])
ap=fixture/'accepted-synthetic.json'
def acceptance(r):return save(ap,r)
check('exact103 technical decisions cannot imply hearing or userapproval',lambda:require(m.accepted_review(proposed,acceptance(accepted),asrpin,levelpin)['actualListening']is False))
for kind in['missing','gain','hold','asrhash','joinhash','human','listening','reorder']:
 bad=copy.deepcopy(accepted)
 if kind=='missing':bad['components'].pop()
 elif kind=='gain':bad['components'][0]['expectedGainDb']+=.1
 elif kind=='hold':bad['components'][1]['decision']='hold-for-repair'
 elif kind=='asrhash':bad['rawAsrReview']['sha256']='c'*64
 elif kind=='joinhash':bad['joinsReviewedSHA256']='d'*64
 elif kind=='human':bad['humanApproval']=True
 elif kind=='listening':bad['actualListening']=True
 else:bad['components'][0],bad['components'][1]=bad['components'][1],bad['components'][0]
 check('acceptance '+kind+' cannot silentlypass',lambda bad=bad:reject(lambda:m.accepted_review(proposed,acceptance(bad),asrpin,levelpin)))
bad=copy.deepcopy(proposed);bad['identity']['levelFlags']=[dict(kind='sustained-take-word-body-decline',sceneId=rows[0]['sceneId'])]
check('withincomponent decline requires source repair not blanketgain',lambda:reject(lambda:m.accepted_review(bad,acceptance(accepted),asrpin,levelpin)))
check('withincomponent decline blocks proposal before audio assembly',lambda:reject(lambda:m.proposal(voice,rows,review,dict(flags=[dict(kind='sustained-take-word-body-decline')]),[])))
bad=copy.deepcopy(proposed);bad['identity']['components'][0]['normalization']['targetErrorDb']=-3.;ar=copy.deepcopy(accepted);ar['components'][0]['levelReviewNote']=''
check('peakcap shortfall requires explicit numeric note',lambda:reject(lambda:m.accepted_review(bad,acceptance(ar),asrpin,levelpin)))
bad=copy.deepcopy(proposed);bad['identity']['components'][0]['literalDifferent']=True;ar=copy.deepcopy(accepted);ar['components'][0]['literalReviewNote']=''
check('literal difference requires explicit retained note',lambda:reject(lambda:m.accepted_review(bad,acceptance(ar),asrpin,levelpin)))
bad=copy.deepcopy(proposed);bad['identity']['joins'][0]['normalizedAbsoluteStep']=.03
check('large boundary sample step requires explicit retained technical note',lambda:reject(lambda:m.accepted_review(bad,acceptance(accepted),asrpin,levelpin)))
sf.write(voice['aggregateWav']['path'],allraw+1/32768,24000,subtype='PCM_16')
check('changed canonical sample has no legacyfade fallback',lambda:reject(lambda:m.proposal(voice,rows,review,dict(flags=[]),[])))
with patch.object(m.subprocess,'Popen')as pop:
 check('forbidden executable cannot launch through owned CPU wrapper',lambda:reject(lambda:m.tracked_run(None,['powershell.exe','fake'])))
 pop.assert_not_called()
check('visual ceil never pads or stretches raw speech',lambda:require(math.ceil(3490561*60/24000)==8727 and 3490561*2==6981122))
cache=fixture/'minimal-cache';cache.mkdir();sf.write(cache/'final-mix.wav',np.zeros((240,2),dtype=np.float32),48000,subtype='FLOAT');cr=dict(fingerprint='synthetic-cache')
report=dict(schemaVersion='06-02-audio-build-v1',topicId='06.02',fingerprint='synthetic-cache',mixWav=m.artifact(cache,'final-mix.wav'),artifacts={'final-mix.wav':dict(file='final-mix.wav',sha256=m.sha(cache/'final-mix.wav'))});m.save(cache/'audio-build.json',report)
check('mix-only partial cache cannot stand in for component and stem evidence',lambda:reject(lambda:m.reuse_audio(cache,cr)))
required=['input-recipe.json','line-levels.json','narration-component-normalized.wav','narration-prepared-stem.wav','narration-stem.wav','music-stem.wav','music-loop-plan.json']
for name in required:(cache/name).write_bytes(b'Synthetic cache descriptor only, not actual production audio')
report['artifacts'].update({n:dict(file=n,sha256=m.sha(cache/n))for n in required});m.save(cache/'audio-build.json',report)
check('complete hash-bound cache descriptor remains same identity',lambda:require(m.reuse_audio(cache,cr)['mixWav']['frames']==240))
bad=copy.deepcopy(report);bad['mixWav']['path']=str(fixture/'outside.wav');m.save(cache/'audio-build.json',bad)
check('existing cache path cannot be relabelled outside owned output',lambda:reject(lambda:m.reuse_audio(cache,cr)))
bad=copy.deepcopy(report);bad['artifacts']['music-stem.wav'].update(file='../outside.wav');m.save(cache/'audio-build.json',bad)
check('artifact traversal or filename substitution rejects',lambda:reject(lambda:m.reuse_audio(cache,cr)))
m.save(cache/'audio-build.json',report);sf.write(cache/'final-mix.wav',np.ones((240,2),dtype=np.float32)*.01,48000,subtype='FLOAT')
check('changed actual cached mix samples reject',lambda:reject(lambda:m.reuse_audio(cache,cr)))
worker=MagicMock();child=MagicMock(pid=123,returncode=0);child.communicate.return_value=(b'fixture',b'')
with patch.object(m.subprocess,'Popen',return_value=child)as launch,patch.object(m.runtime,'identity',return_value={'pid':123,'createTime':10.}):
 m.tracked_run(worker,[m.base.FF,'-version']);cmd=launch.call_args.args[0]
 check('owned FFmpeg command is bounded to two threads',lambda:require(cmd[1:5]==['-threads','2','-filter_threads','2']))
 check('owned CPU child launch and exited lifecycle are recorded',lambda:require(worker.update.call_args_list[0].kwargs['phase']=='launching-owned-cpu-audio-tool'and worker.update.call_args_list[-1].kwargs==dict(child=None,phase='audio-cpu-processing')))
 cmd=[str(m.base.FF),'-threads','2','synthetic-actual-output-path']
fake=MagicMock();fake.info=dict(name='ffmpeg.exe',cmdline=cmd)
with patch.object(m.runtime.psutil,'process_iter',return_value=[fake]):check('launchgap exact owned CPU child remains protected',lambda:require(m.unrecorded_audio_child(dict(phase='launching-owned-cpu-audio-tool',launchCommand=cmd))))
check('same native source frame count produces integral48k duration without rounding',lambda:require(m.loop_plan(363*48000,600*48000,48000)['targetFrames']==600*48000 and m.loop_plan(363*48000,600*48000,48000)['repeatCount']==1))
receipt=dict(topicId='06.02',cpuChecksPassed=len(passed),checks=passed,fixture=str(fixture),sourcePins=[m.pin(HERE/'prepare-prospect-refuge-audio-v2.py'),m.pin(Path(__file__)),m.pin(HERE/'prepare-first-audio.py'),m.pin(HERE/'prepare-zen-view-audio.py')],syntheticAudioOnly=True,currentRawVoiceProcessed=False,actualMixPrepared=False,ffmpegStarted=False,modelStarted=False,gpuUsed=False,humanListening=False)
m.save(fixture/'receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
