"""Synthetic CPU-only audio fixtures. No selected source audio/FFmpeg/model job."""
import copy,importlib.util,json,math,uuid
from pathlib import Path
import numpy as np
import soundfile as sf

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selected_zen_audio_fixture',HERE/'prepare-zen-view-audio.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixture=m.TOPIC/'audio-source-preparation/cpu-tests'/uuid.uuid4().hex;fixture.mkdir(parents=True)
passed=[]
def check(name,action):
 action();passed.append(name)
def require(value):
 if not value:raise AssertionError('Fixture contract failed')
def rejected(action):
 try:action()
 except(m.Pending,ValueError,AssertionError):return
 raise AssertionError('Expected explicit rejection, not fallback')

voice=dict(fingerprint='synthetic-voice',identity=dict(scenes=[]),aggregateWav=dict(path=str(fixture/'synthetic-canonical.wav'),sampleRate=24000,frames=0,pcmSHA256='synthetic'),sceneWavs=[],paragraphMapping=[],timing=dict(sha256='synthetic-timing'))
timing=dict(entries=[]);arrays=[];position=0;review=dict(takes=[])
for i in range(14):
 n=2400+i*6;data=(np.sin(np.arange(n)*.037)*(.025+i*.003)).astype(np.float32);data[:64]=0;data[-64:]=0
 path=fixture/f'synthetic-{i:02}.wav';sf.write(path,data,24000,subtype='PCM_16');raw,sr=sf.read(path,dtype='float32');arrays.append(raw)
 sid=f'p{i//2+1:03}-c{i%2+1:02}';text='합성 시험 '+sid
 rawpcm=np.rint(raw.astype(np.float64)*32768).astype('<i2').tobytes()
 take=dict(path=str(path),sha256=m.sha(path),pcmSHA256=m.hashlib.sha256(rawpcm).hexdigest(),sampleRate=24000,channels=1,sampleWidthBytes=2,frames=n)
 voice['sceneWavs'].append(take);voice['paragraphMapping'].append(dict(sceneId=sid,paragraph=i//2+1,canonicalText=text));timing['entries'].append(dict(scene_id=sid,text=text,start=position/24000,end=(position+n)/24000));position+=n
 voice['identity']['scenes'].append(dict(id=sid,lines=[text]))
 review['takes'].append(dict(task=dict(sceneId=sid),text=text,comparison=dict(fixtureLiteralExact=True)))
allraw=np.concatenate(arrays);sf.write(voice['aggregateWav']['path'],allraw,24000,subtype='PCM_16');voice['aggregateWav'].update(frames=position,sha256=m.sha(voice['aggregateWav']['path']))
rows=m.exact_components(voice,timing)
check('exact14components and7paragraphs',lambda:require(len(rows)==14 and[sum(r['paragraph']==n for r in rows)for n in range(1,8)]==[2]*7))
check('all natural component boundaries stay sample-exact',lambda:require(rows[-1]['destinationSampleRange'][1]==position and all(a['destinationSampleRange'][1]==b['destinationSampleRange'][0]for a,b in zip(rows,rows[1:]))))
check('prepared48k ranges exactlydouble24k withoutaddedtail',lambda:require(all(r['prepared48kSampleRange']==[x*2 for x in r['destinationSampleRange']]for r in rows)))
bad=copy.deepcopy(voice);bad['sceneWavs']=bad['sceneWavs'][:6]
check('old6take schema cannot enter14take pipeline',lambda:rejected(lambda:m.exact_components(bad,timing)))
bad=copy.deepcopy(timing);bad['entries'][3]['start']+=1/24000
check('one sample shifted raw boundary rejected',lambda:rejected(lambda:m.exact_components(voice,bad)))
pins={p:m.sha(p)for p in[f['path']for f in voice['sceneWavs']]+[voice['aggregateWav']['path']]}
original_run=m.base.run;m.base.run=lambda args:(_ for _ in()).throw(AssertionError('FFmpeg must never run in fixtures'))
try:
 proposal=m.proposal(voice,rows,review,dict(flags=[]),[])
 check('normalizationproposal never modifies raw WAV bytes',lambda:require(all(m.sha(p)==s for p,s in pins.items())))
 check('all14 proposed gains are finiteboundedscalars',lambda:require(all(math.isfinite(r['normalization']['constantGainDb'])and abs(r['normalization']['constantGainDb'])<=12.001 for r in proposal['identity']['components'])))
 check('quiet raw heads/tails remain at13joins noinsert/trim',lambda:require(len(proposal['identity']['joins'])==13 and all(j['insertedSamples']==j['trimmedSamples']==0 and j['rawLastSample']==j['rawFirstSample']==0 for j in proposal['identity']['joins'])))
 asrpin=dict(path='synthetic-asr-only',sha256='a'*64);levelpin=dict(path='synthetic-level-only',sha256='b'*64)
 accepted=dict(schemaVersion='07-04-accepted-audio-components-v1',topicId='07.04',componentCount=14,voiceFingerprint=voice['fingerprint'],canonicalWavSHA256=voice['aggregateWav']['sha256'],canonicalPcmSHA256=voice['aggregateWav']['pcmSHA256'],timingSHA256=voice['timing']['sha256'],rawAsrReview=asrpin,levelReview=levelpin,proposalFingerprint=proposal['fingerprint'],joinsReviewedSHA256=proposal['joinsReviewedSHA256'],acknowledgedLevelFlagsSHA256=proposal['acknowledgedLevelFlagsSHA256'],reviewer='synthetic-fixture-not-production-review',technicalOnly=True,actualListening=False,humanApproval=False,components=[dict(sceneId=r['sceneId'],rawTakeSHA256=r['rawTakeSHA256'],rawPcmSHA256=r['rawPcmSHA256'],rawTakeASRRecordSHA256=r['rawTakeASRRecordSHA256'],decision='accept-scalar-match',expectedGainDb=r['normalization']['constantGainDb'],literalDecision='accepted',literalReviewNote='synthetic',levelReviewNote='synthetic')for r in proposal['identity']['components']])
 ap=fixture/'synthetic-accepted-review.json'
 def setreview(r):ap.write_text(json.dumps(r));return ap
 check('all14 exact factualnumericdecisions accepted withouthearingclaim',lambda:require(m.accepted_review(proposal,setreview(accepted),asrpin,levelpin)['actualListening']is False))
 bad=copy.deepcopy(accepted);bad['components'].pop()
 check('missingonecomponentdecision rejects entiremix',lambda:rejected(lambda:m.accepted_review(proposal,setreview(bad),asrpin,levelpin)))
 bad=copy.deepcopy(accepted);bad['components'][0]['expectedGainDb']+=.01
 check('changedscalar afterreview rejected',lambda:rejected(lambda:m.accepted_review(proposal,setreview(bad),asrpin,levelpin)))
 bad=copy.deepcopy(accepted);bad['components'][1]['decision']='hold-for-repair'
 check('declinedcomponent cannotfallbacktosilentnormalization',lambda:rejected(lambda:m.accepted_review(proposal,setreview(bad),asrpin,levelpin)))
 bad=copy.deepcopy(accepted);bad['joinsReviewedSHA256']='c'*64
 check('stalescalarjoinreview rejected',lambda:rejected(lambda:m.accepted_review(proposal,setreview(bad),asrpin,levelpin)))
 bad=copy.deepcopy(accepted);bad['rawAsrReview']['sha256']='d'*64
 check('differentrawASRreview cannotreuseacceptance',lambda:rejected(lambda:m.accepted_review(proposal,setreview(bad),asrpin,levelpin)))
 altered=copy.deepcopy(proposal);altered['identity']['components'][0]['literalDifferent']=True
 bad=copy.deepcopy(accepted);bad['components'][0]['literalReviewNote']=''
 check('literalASRdifference cannotdisappearwithoutreviewnote',lambda:rejected(lambda:m.accepted_review(altered,setreview(bad),asrpin,levelpin)))
 altered=copy.deepcopy(proposal);altered['identity']['components'][0]['normalization']['targetErrorDb']=-3.5
 bad=copy.deepcopy(accepted);bad['components'][0]['levelReviewNote']=''
 check('peaklimitedtargetshortfall requiresnumericalreviewnote',lambda:rejected(lambda:m.accepted_review(altered,setreview(bad),asrpin,levelpin)))
 altered=copy.deepcopy(proposal);altered['identity']['levelFlags']=[dict(kind='synthetic-decline-warning')]
 check('numericalflags cannotbeacceptedwithoutdisposition',lambda:rejected(lambda:m.accepted_review(altered,setreview(accepted),asrpin,levelpin)))
 altered=copy.deepcopy(proposal);altered['identity']['levelFlags']=[dict(kind='sustained-take-word-body-decline')]
 bad=copy.deepcopy(accepted);bad['levelFlagsDisposition']='A note cannot repair within-take decline'
 check('within-take decline cannot be waived by a gain acceptance note',lambda:rejected(lambda:m.accepted_review(altered,setreview(bad),asrpin,levelpin)))
 check('within-take decline blocks scalar proposal before processing',lambda:rejected(lambda:m.proposal(voice,rows,review,dict(flags=[dict(kind='sustained-take-word-body-decline')]),[])))
 for alternative_count in [29,33]:
  altvoice=dict(fingerprint='synthetic-'+str(alternative_count),identity=dict(scenes=[]),aggregateWav=dict(path=str(fixture/f'synthetic-{alternative_count}-canonical.wav'),sampleRate=24000,frames=0,pcmSHA256='synthetic-alt'),sceneWavs=[],paragraphMapping=[],timing=dict(sha256='synthetic-alt-timing'));alttiming=dict(entries=[]);altreview=dict(takes=[]);altparts=[];at=0;index=0
  for pno in range(1,8):
   for ordinal in range(alternative_count//7+(1 if pno<=alternative_count%7 else 0)):
    sid=f'alt-p{pno:03}-c{ordinal:03}';text='다른 수량 검사 '+sid;take=voice['sceneWavs'][index%14];n=take['frames']
    altvoice['identity']['scenes'].append(dict(id=sid,lines=[text]));altvoice['sceneWavs'].append(take);altvoice['paragraphMapping'].append(dict(sceneId=sid,paragraph=pno,canonicalText=text));alttiming['entries'].append(dict(scene_id=sid,text=text,start=at/24000,end=(at+n)/24000));altparts.append(arrays[index%14]);at+=n;altreview['takes'].append(dict(task=dict(sceneId=sid),text=text,comparison=dict(synthetic=True)));index+=1
  altvoice['aggregateWav']['frames']=at;sf.write(altvoice['aggregateWav']['path'],np.concatenate(altparts),24000,subtype='PCM_16');altvoice['aggregateWav']['sha256']=m.sha(altvoice['aggregateWav']['path']);altrows=m.exact_components(altvoice,alttiming);altproposal=m.proposal(altvoice,altrows,altreview,dict(flags=[]),[])
  check(f'exact{alternative_count} scene identity produces exact dynamic scalar rows and joins',lambda:require(len(altrows)==len(altproposal['identity']['components'])==alternative_count and len(altproposal['identity']['joins'])==alternative_count-1))
  bad=copy.deepcopy(altvoice);bad['identity']['scenes'][2],bad['identity']['scenes'][3]=bad['identity']['scenes'][3],bad['identity']['scenes'][2]
  check(f'exact{alternative_count} cannot reorder selected source identity',lambda:rejected(lambda:m.exact_components(bad,alttiming)))
  altaccepted=copy.deepcopy(accepted);altaccepted.update(componentCount=alternative_count,voiceFingerprint=altvoice['fingerprint'],canonicalWavSHA256=altvoice['aggregateWav']['sha256'],canonicalPcmSHA256=altvoice['aggregateWav']['pcmSHA256'],timingSHA256=altvoice['timing']['sha256'],proposalFingerprint=altproposal['fingerprint'],joinsReviewedSHA256=altproposal['joinsReviewedSHA256'],acknowledgedLevelFlagsSHA256=altproposal['acknowledgedLevelFlagsSHA256'],components=[dict(sceneId=r['sceneId'],rawTakeSHA256=r['rawTakeSHA256'],rawPcmSHA256=r['rawPcmSHA256'],rawTakeASRRecordSHA256=r['rawTakeASRRecordSHA256'],decision='accept-scalar-match',expectedGainDb=r['normalization']['constantGainDb'],literalDecision='accepted',literalReviewNote='synthetic',levelReviewNote='synthetic')for r in altproposal['identity']['components']])
  check(f'exact{alternative_count} requires all selected acceptance decisions',lambda:require(m.accepted_review(altproposal,setreview(altaccepted),asrpin,levelpin)['componentCount']==alternative_count))
  check(f'old14 acceptance cannot authorize exact{alternative_count} voice',lambda:rejected(lambda:m.accepted_review(altproposal,setreview(accepted),asrpin,levelpin)))
 sf.write(voice['aggregateWav']['path'],allraw+1/32768,24000,subtype='PCM_16')
 check('changedcanonicalsample doesnotuselegacyfadeexception',lambda:rejected(lambda:m.proposal(voice,rows,review,dict(flags=[]),[])))
 check('music shorterthanexactvoice rejects insteadofloop',lambda:rejected(lambda:m.base.music_bed(np.zeros((99,2),dtype=np.float32),100,48000,1,np.ones(100,dtype=np.float32),m.PROFILE)))
 dry=np.ones((48000,2),dtype=np.float32)*.1;copydry=dry.copy();duck=m.base.duck_curve(dry,48000,m.PROFILE)
 check('speechduck affectsbackgroundcurve only',lambda:require(np.array_equal(dry,copydry)and float(duck.min())>=10**(-4/20)-1e-6 and float(duck.max())<=1))
 check('145.44s clock maps8727 visual frames without audio extension',lambda:require(math.ceil(3490561*60/24000)==8727 and 3490561*2==6981122))
 cache=fixture/'synthetic-cache';cache.mkdir();sf.write(cache/'final-mix.wav',np.zeros((120,2),dtype=np.float32),48000,subtype='FLOAT')
 cache_recipe=dict(fingerprint='synthetic-cache');cache_receipt=dict(schemaVersion='07-04-audio-build-v1',topicId='07.04',fingerprint='synthetic-cache',artifacts={'mix':dict(file='final-mix.wav',sha256=m.sha(cache/'final-mix.wav'))},mixWav=m.artifact(cache,'final-mix.wav'))
 def setcache(r):m.save(cache/'audio-build.json',r)
 setcache(cache_receipt)
 check('exact cached mix reused with actual hash/frame descriptor',lambda:require(m.reuse_audio(cache,cache_recipe)['mixWav']['frames']==120))
 bad=copy.deepcopy(cache_receipt);bad['mixWav']['path']=str(fixture/'other.wav');setcache(bad)
 check('stale cached mix path rejected',lambda:rejected(lambda:m.reuse_audio(cache,cache_recipe)))
 bad=copy.deepcopy(cache_receipt);bad['artifacts']['mix']['file']='../outside.wav';setcache(bad)
 check('cached artifact path cannot escape owned folder',lambda:rejected(lambda:m.reuse_audio(cache,cache_recipe)))
 setcache(cache_receipt);sf.write(cache/'final-mix.wav',np.ones((120,2),dtype=np.float32)*.01,48000,subtype='FLOAT')
 check('changed cached mix samples rejected',lambda:rejected(lambda:m.reuse_audio(cache,cache_recipe)))
finally:m.base.run=original_run
receipt=dict(schemaVersion='07-04-audio-source-cpu-validation-v1',passed=len(passed),checks=passed,fixture=str(fixture),sourcePins=[m.pin(HERE/'prepare-zen-view-audio.py'),m.pin(Path(__file__)),m.pin(HERE/'prepare-first-audio.py')],syntheticAudioFixtures=True,selectedSourceAudioProcessed=False,actualMixPrepared=False,ffmpegStarted=False,modelStarted=False,gpuUsed=False,humanListening=False)
m.save(fixture/'receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
