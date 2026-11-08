"""Bounded regression for libsndfile FLOAT WAV timestamp churn.

The synthetic fixture tests unchanged serializable PCM and one changed sample.
The optional A01 check rebuilds only existing prepared audio groups, no TTS/render.
"""
from pathlib import Path
import argparse,time,struct,hashlib,json
import numpy as np
import soundfile as sf
import prepare_final_audio as a

def peak_stamp(p):
    data=Path(p).read_bytes();at=12
    while at+8<=len(data):
        name=data[at:at+4];size=struct.unpack_from('<I',data,at+4)[0]
        if name==b'PEAK':return struct.unpack_from('<II',data,at+8)[1]
        at+=8+size+(size%2)
    return None

def snapshot(p):
    x,_=sf.read(p,dtype='float32',always_2d=True)
    return {'sha256':a.sha(p),'mtimeNs':Path(p).stat().st_mtime_ns,
        'pcmSha256':hashlib.sha256(x.tobytes()).hexdigest(),'peakTimestamp':peak_stamp(p)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--a01',action='store_true');args=ap.parse_args()
    out=a.L/'idempotence-regression';out.mkdir(parents=True,exist_ok=True)
    p=out/'synthetic-float.wav';x=np.zeros((4800,2),dtype=np.float64);x[100:300,0]=np.linspace(-.25,.25,200)
    a.save_mix(p,x);first=snapshot(p);time.sleep(1.2);a.save_mix(p,x);second=snapshot(p)
    assert first==second,'Equal serialized PCM must preserve complete file bytes and mtime'
    changed=x.copy();changed[150,1]=.125;a.save_mix(p,changed);third=snapshot(p)
    check,_=sf.read(p,dtype='float32',always_2d=True)
    assert np.array_equal(check,changed.astype(np.float32))and third['sha256']!=second['sha256']
    real={}
    if args.a01:
        plan=a.read(a.L/'A01/audio-plan.json');files=[a.R/g['source']for g in plan['groups']]
        before={str(p):snapshot(p)for p in files};a.prepare(['A01']);one={str(p):snapshot(p)for p in files}
        time.sleep(1.2);a.prepare(['A01']);two={str(p):snapshot(p)for p in files}
        assert before==one==two,'Rebuilding actual A01 must preserve equal PCM, WAV bytes and mtime'
        a.align_ready();real={'allFourGroups':len(files)==4,'before':before,'afterFirst':one,'afterSecond':two,'exactlyUnchanged':True}
    a.save(out/'receipt.json',{'synthetic':{'before':first,'afterSamePcm':second,'afterOneSampleChange':third,
        'samePcmFileAndMtimePreserved':True,'changedPcmActuallyWritten':True,'timeGapSeconds':1.2},
        'a01':real,'sourceCodeSha256':a.sha(Path(a.__file__)),'humanListening':False,'ttsStarted':False,'videoRendered':False})
    print('PASS: equal PCM preserves WAV bytes/mtime across time; changed PCM is written. A01:',bool(real))

if __name__=='__main__':main()
