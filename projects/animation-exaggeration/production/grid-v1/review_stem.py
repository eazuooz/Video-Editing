"""A02: compare identical speech samples in preserved source and mastered stem."""
import json
import numpy as np
import soundfile as sf
from storage_paths import HERE, LOCAL
import audio_pipeline as ap

def db(a):
    return float(20*np.log10(max(1e-12,np.sqrt(np.mean(a.astype('float64')**2)))))

def main():
    build_path=LOCAL/'edit/audio-build.json'
    build=ap.read(build_path)
    stem_path=LOCAL/'edit/narration-stem.wav'
    stem,rate=sf.read(stem_path,always_2d=True,dtype='float32')
    assert rate==48000
    known={r['path']:r['sha256'] for r in build['outputs']}
    assert known[ap.relative(stem_path)]==ap.sha(stem_path)
    rows=[];flags=[];inputs=[]
    for scene in build['scenes']:
        source=LOCAL/f"voice/chunks/{scene['scene']}-scene.wav"
        a,rs=sf.read(source,dtype='float32')
        assert rs==rate and ap.sha(source)==scene['sourceSha256']
        recognition_path=LOCAL/f"voice/asr/{scene['scene']}.json"
        recognition=ap.read(recognition_path)
        mask=ap.mask_words(len(a),rate,recognition['words'])
        offset=scene['voiceStartSample'];b=stem[offset:offset+len(a),0]
        assert len(a)==len(b)
        gain=scene['fixedGainDb']+build['globalGainDb']
        expected=a*10**(gain/20)
        inputs.append({'scene':scene['scene'],'source':ap.artifact(source),'recognition':ap.artifact(recognition_path),'voiceStartSample':offset,'constantGainDb':gain})
        for start in range(0,len(a),rate//2):
            end=min(len(a),start+rate);active=mask[start:end]
            if active.sum()<rate//4:continue
            x=expected[start:end][active];y=b[start:end][active]
            xd=x.astype('float64');yd=y.astype('float64')
            corr=float(np.sum(xd*yd)/max(1e-18,np.sqrt(np.sum(xd*xd)*np.sum(yd*yd))))
            delta=db(y)-db(x)
            row={'scene':scene['scene'],'sceneLocalStart':start/rate,'timelineStart':(offset+start)/rate,'speechActiveSamples':int(active.sum()),'expectedAfterConstantGainDbfs':db(x),'actualMatchedStemDbfs':db(y),'differenceDb':delta,'correlation':corr,'expectedPeakDbfs':float(20*np.log10(max(1e-12,np.max(np.abs(x))))),'stemPeakDbfs':float(20*np.log10(max(1e-12,np.max(np.abs(y)))))}
            rows.append(row)
            if delta < -3.0 or delta>.2 or corr<.95:flags.append(row)
    diagnostic_review=[]
    for rough in build['diagnosticContinuityFlags']:
        matches=[r for r in rows if r['scene']==rough['scene'] and r['sceneLocalStart']==rough['sceneLocalStart']]
        assert len(matches)==1
        matched=matches[0]
        diagnostic_review.append({'originalWholeWindowDiagnostic':rough,'matchedSpeechWindow':matched,'status':'still-flagged' if matched in flags else 'resolved-by-identical-speech-mask','interpretation':'Original diagnostic compared speech-only source RMS against a whole stem window. With identical speech samples, the measured difference is within the limiter tolerance. This is a signal comparison, not an audition.'})
    record={'status':'needs-contextual-review' if flags else 'passed-source-to-stem','scope':'Every overlapping 1-second window at 0.5-second stride containing at least 0.25 seconds of speech. Identical word masks in source and stem; limiter effects measured, not described as new source defects.','audioBuild':ap.artifact(build_path),'stem':ap.artifact(stem_path),'inputs':inputs,'records':rows,'remainingFlags':flags,'wholeWindowDiagnostics':build['diagnosticContinuityFlags'],'wholeWindowDiagnosticReview':diagnostic_review,'finalEncodedMixContinuity':'Separate qa/audio-v1/continuity.json','actualListeningPerformed':False,'humanListening':'pending','reviewedAt':ap.now()}
    ap.save(HERE/'source-stem-continuity-review.json',record)
    print(json.dumps({'status':record['status'],'speechWindows':len(rows),'flagCount':len(flags),'flags':flags},ensure_ascii=False))

if __name__=='__main__':main()
