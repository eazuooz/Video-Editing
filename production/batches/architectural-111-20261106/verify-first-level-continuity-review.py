"""CPU synthetic signals only; no actual voice analysis or external process."""
import copy
import importlib.util
import json
import math
import tempfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('first_level_continuity_cpu',HERE/'first-level-continuity-review.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]


def signal_fixture(decline=False,stem_drop=False,music_close=False):
    rate=8000;duration=.5;count=18;word_samples=round(rate*duration);size=count*word_samples
    amplitudes=np.geomspace(.16,.035,count) if decline else np.full(count,.1)
    raw=np.concatenate([amp*np.sin(2*np.pi*317*np.arange(word_samples)/rate) for amp in amplitudes]).astype(np.float32)[:,None]
    normal=raw*2;prepared=np.repeat(normal,2,axis=1);voice=prepared*.5
    if stem_drop:voice[len(voice)//2:]*=.2
    bed=(.035 if music_close else .00005)*np.sin(2*np.pi*137*np.arange(size)/rate)
    music=np.repeat(bed.astype(np.float32)[:,None],2,axis=1)
    arrays=dict(normalized=normal,prepared=prepared,voice=voice,music=music,mix=voice+music)
    paragraph=dict(sceneId='s03',destinationSampleRange=[0,size],constantGainDb=20*math.log10(2),peakCapApplied=True,targetErrorDb=-5.)
    recognized=dict(globalWords=[dict(text=f'fixture-token-{i}',timestamp=[i*duration,(i+1)*duration]) for i in range(count)])
    words=m.word_records(paragraph,recognized,arrays,raw,rate,rate)
    return paragraph,words,arrays


def passed(name):checks.append(dict(check=name,result='passed'))
def reject(name,call):
    try:call()
    except (ValueError,RuntimeError):passed(name+' rejected')
    else:raise AssertionError(name+' unexpectedly accepted')


def main():
    m.subprocess.run=lambda *a,**k:(_ for _ in ()).throw(AssertionError('No decode/model/meter in CPU fixtures'))
    a,b=m.sample_window('0.033333333333333333333333','0.066666666666666666666667',24000)
    assert (a,b)==(799,1601)  # outward sub-sample rounding is explicit.
    assert m.scale_window(800,1600,24000,48000)==(1600,3200)
    assert m.scale_window(864001,864801,24000,48000)==(1728002,1729602)
    assert m.scale_window(400,800,24000,48000)==(800,1600)  # exact1/60-second grid.
    passed('exact raw-to-mix sample/frame grids retain odd paragraph offsets')
    reject('missing/negative word time',lambda:m.sample_window(-1,1,24000))
    paragraph,words,_=signal_fixture()
    summaries,flags=m.continuity([(paragraph,words)])
    assert not any(f['kind']=='sustained-word-body-decline' for f in flags)
    assert all(abs(w['normalizedMinusCanonicalBodyDb']-paragraph['constantGainDb'])<1e-4 for w in words)
    passed('stable words and uniform gain do not invent a continuity decline')
    paragraph,words,_=signal_fixture(decline=True)
    summaries,flags=m.continuity([(paragraph,words)])
    assert {f['stage'] for f in flags if f['kind']=='sustained-word-body-decline'}>={'canonical','normalized','voice','mix'}
    assert summaries[0]['stages']['voice']['lateMinusEarlyDb']<-6
    assert all(f['action'] for f in flags if f['kind']=='sustained-word-body-decline')
    passed('long-take local decline persists through constant normalization and cannot be cleared by global gain')
    paragraph,words,_=signal_fixture(stem_drop=True)
    _,flags=m.continuity([(paragraph,words)])
    stages={f['stage'] for f in flags if f['kind']=='sustained-word-body-decline'}
    assert 'voice' in stages and 'canonical' not in stages
    passed('processed-stem decline is distinguished from a stable canonical take')
    paragraph,words,arrays=signal_fixture(music_close=True)
    _,flags=m.continuity([(paragraph,words)])
    assert any(f['kind']=='music-close-to-known-voice-component' for f in flags)
    assert all('not estimated SNR' in f['interpretation'] for f in flags if f['kind']=='music-close-to-known-voice-component')
    passed('known music/voice component ratio is flagged without an SNR claim')
    assert not m.residual_summary(arrays['mix'],arrays['voice']+arrays['music'])['exceedsKnownStemTolerance']
    wrong=arrays['mix'].copy();wrong[150,0]+=.001
    assert m.residual_summary(wrong,arrays['voice']+arrays['music'])['exceedsKnownStemTolerance']
    reject('different known-stem sample shape',lambda:m.residual_summary(arrays['mix'][:-1],arrays['voice']+arrays['music']))
    passed('same known stems reproduce mix; changed sample is a real arithmetic mismatch')
    rng=np.random.default_rng(774);rate=8000
    reference=rng.normal(0,.04,(rate*7,2)).astype(np.float32)
    shifted=np.pad(reference,((173,0),(0,0)))+rng.normal(0,1e-5,(len(reference)+173,2)).astype(np.float32)
    alignment=m.estimate_alignment(reference,shifted,rate)
    assert alignment['supported'] and alignment['decodedMinusReferenceSamples']==173 and alignment['audioModified'] is False
    assert m.scale_window(0,1600,8000,8000,173)==(173,1773)
    passed('codec-style positive delay is found from separated waveform anchors without trimming or padding audio')
    removed=reference[80:];alignment=m.estimate_alignment(reference,removed,rate)
    assert alignment['supported'] and alignment['decodedMinusReferenceSamples']==-80
    assert m.scale_window(0,1600,8000,8000,-80)[0]<0
    passed('missing initial coverage remains negative rather than silently clipped or padded')
    assert not m.estimate_alignment(np.zeros((rate*4,2)),np.zeros((rate*4,2)),rate)['supported']
    tone=np.sin(2*np.pi*200*np.arange(rate*5)/rate)
    assert not m.estimate_alignment(tone,tone,rate)['supported']
    passed('silent or periodic ambiguous alignment is not declared established')
    with tempfile.TemporaryDirectory(prefix='first-level-continuity-cpu-') as folder:
        mix=Path(folder)/'mix.wav';mix.write_bytes(b'synthetic immutable mix identity')
        record=m.pin(mix);m.verify_pin(record,'fixture mix');mix.write_bytes(b'changed mix')
        reject('changed mix artifact pin',lambda:m.verify_pin(record,'fixture mix'))
    identity=dict(mix='a'*64,rawWav='b'*64,rawAsr='c'*64,rawComponent='d'*64,method='fixture')
    old=dict(method=m.METHOD,inputIdentity=copy.deepcopy(identity),fingerprint=m.digest(identity))
    assert m.same_identity(old,identity)
    for key in ('mix','rawWav','rawAsr','rawComponent'):
        changed=dict(identity,**{key:'f'*64});assert not m.same_identity(old,changed)
    passed('cached review is reusable only for the same mix, canonical WAV and blind-ASR pins')
    build=dict(artifacts={'final-mix.wav':dict(sha256='m')},rawVoiceFingerprint='voice-id',rawVoiceSha256='v')
    timeline=dict(voiceFingerprint='voice-id',audio=dict(mix=dict(sha256='m'),voice=dict(sha256='v')))
    m.assert_same_audio(build,timeline)
    stale=copy.deepcopy(timeline);stale['audio']['mix']['sha256']='old'
    reject('encoded movie from an old mix',lambda:m.assert_same_audio(build,stale))
    stale=copy.deepcopy(timeline);stale['audio']['voice']['sha256']='old'
    reject('encoded movie from an old voice aggregate',lambda:m.assert_same_audio(build,stale))
    passed('actual render must carry the same selected voice and final-mix identity')
    report=dict(scope='Synthetic CPU signals only; actual voice/mix/ASR/render not analyzed',checks=checks,count=len(checks),allPassed=True,
        reviewerSHA256=m.sha(HERE/'first-level-continuity-review.py'),testSHA256=m.sha(__file__),
        externalProcessesStarted=0,actualListening=False,actualVideoPlayback=False,productionArtifactsChanged=False)
    path=HERE/'first-level-continuity-cpu-validation.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(checks=len(checks),allPassed=True,report=str(path))))


if __name__=='__main__':main()
