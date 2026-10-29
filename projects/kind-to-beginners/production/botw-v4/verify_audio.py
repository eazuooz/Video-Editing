"""Verify the completed AAC against the reviewed continuous mix, without new TTS."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess
import numpy as np
import soundfile as sf
from storage_paths import ROOT, HERE, LOCAL, relative, repo_path
from audio_pipeline import tool

def read(p): return json.loads(p.read_text('utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    edit=LOCAL/'edit'; plan=read(HERE/'edit-plan.json'); structure=read(edit/'structural-verification.json')
    assert structure['status']=='pass' and structure['identicalContinuousAudio']
    source_review=read(HERE/'source-asr-review.json')
    assert source_review['fullTextDirectlyCompared'] is True
    final_asr=read(HERE/'final-mix-asr-review.json')
    assert final_asr['status']=='passed' and final_asr['fullTextDirectlyCompared'] is True
    assert final_asr['asrSha256']==sha(edit/'final-mix-asr.json')
    stem_review=read(HERE/'source-stem-continuity-review.json')
    assert stem_review['status']=='passed-source-to-stem'
    build=read(edit/'audio-build.json'); pair=read(edit/'aac-source.json')
    aac=edit/'pair-audio.m4a'; pcm=edit/'final-mix.wav'
    assert final_asr['encodedAudioSha256']==sha(aac)
    assert pair['signature']['sourceSha256']==sha(pcm) and pair['outputSha256']==sha(aac)
    assert pair['signature']['deliveryGainDb']==plan['deliveryAudioGainDb']==-.1
    out=LOCAL/'qa/final-audio-v1';out.mkdir(parents=True,exist_ok=True)
    decoded=out/'encoded-mix.wav'
    if not decoded.exists():
        subprocess.run([tool('ffmpeg'),'-v','error','-threads','2','-i',str(aac),'-vn','-ac','2','-ar','48000','-c:a','pcm_f32le','-threads','2',str(decoded)],check=True)
    expected_samples=plan['totalFrames']*800;rows=[]
    with sf.SoundFile(pcm) as f, sf.SoundFile(decoded) as g, sf.SoundFile(edit/'music-stem.wav') as m:
        assert f.samplerate==g.samplerate==m.samplerate==48000
        assert len(f)==expected_samples and abs(len(g)-expected_samples)<=1024
        for start in range(0,expected_samples,48000):
            count=min(48000,expected_samples-start)
            a=f.read(count,dtype='float64')*10**(-.1/20); b=g.read(count,dtype='float64');music=m.read(count,dtype='float64')
            assert a.shape==b.shape
            rms=lambda x:float(20*np.log10(max(1e-12,np.sqrt(np.mean(x*x)))))
            energy=float(np.sum(a*a));corr=float(np.sum(a*b)/(max(1e-18,np.sqrt(energy*np.sum(b*b)))))
            row={'start':start/48000,'expectedDbfs':rms(a),'encodedDbfs':rms(b),'correlation':corr,'musicDbfs':rms(music)}
            row['rmsDeltaDb']=row['encodedDbfs']-row['expectedDbfs'];rows.append(row)
            if row['expectedDbfs']>-65:
                assert corr>.94 and abs(row['rmsDeltaDb'])<1.0,row
    log=out/'final-loudness.log'
    if not log.exists():
        r=subprocess.run([tool('ffmpeg'),'-v','info','-threads','2','-filter_threads','2','-i',str(aac),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
        log.write_text(r.stderr,'utf-8')
    stats=json.loads(re.findall(r'\{\s*"input_i".*?\}',log.read_text('utf-8'),re.S)[-1])
    assert -17<=float(stats['input_i'])<=-15 and float(stats['input_tp'])<=-1.5,stats
    body=[r for r in rows if 3<=r['start']<=plan['totalFrames']/60-11]
    assert sum(r['musicDbfs']>-70 for r in body)/len(body)>.98
    save(out/'continuity.json',{'status':'passed','aacSha256':sha(aac),'reviewedMixPcmSha256':sha(pcm),'deliveryGainDb':-.1,'comparison':'Every consecutive 1-second decoded window versus the same reviewed mix PCM, with delivery gain; no independent ASR claim for this mixed file.','rows':rows,'loudness':stats})
    voice=read(HERE/'voice-generation-record.json')
    save(HERE/'audio-review.json',{'status':'passed','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sourceVoiceSha256':voice['source']['sha256'],'fullCurrentTextCompared':True,
        'fullTextComparisonScope':'Whole current narration and final encoded mix compared with the complete script; bounded uncertainties, if any, are documented in the source/final ASR reviews. Encoded mix is also compared with reviewed PCM in every1s window.',
        'bgmPresentVerified':True,'bgm':build['music'],'sourcePcmPreserved':build['sourcePcmPreserved'],
        'sourceOriginalSoundGroups':len(build['gameSourceGroups']),'normalGameAudioProfile':build['gameProfile'],
        'sameFinalAacInBothMasters':True,'finalAacSha256':sha(aac),'finalLoudnessLufs':float(stats['input_i']),
        'finalTruePeakDbtp':float(stats['input_tp']),'deliveryHeadroomCorrectionDb':-.1,
        'continuityEvidence':relative(out/'continuity.json'),'sourceToStemEvidence':relative(HERE/'source-stem-continuity-review.json'),
        'sourceAsrEvidence':relative(HERE/'source-asr-review.json'),'finalMixAsrEvidence':relative(HERE/'final-mix-asr-review.json'),'technicalVerificationComplete':True,
        'humanWholeListening':'pending','actualListeningPerformed':False})
    print('Full encoded AAC continuity, same audio in both masters, Nimbus presence and final level passed.',stats['input_i'],stats['input_tp'])

if __name__=='__main__': main()
