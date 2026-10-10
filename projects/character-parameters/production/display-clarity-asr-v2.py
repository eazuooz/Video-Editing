"""Print entire expected/recognized texts, all word clocks and join PCM bins."""
from pathlib import Path
import argparse, hashlib, json, wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3];FOLDER=Path(__file__).resolve().parent/'voice-clarity-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--first',type=int,default=1);ap.add_argument('--last',type=int,default=4);args=ap.parse_args()
state=read(FOLDER/'asr-execution.json')
assert state['exitCode']==0 and state['actualExitObserved'] and len(state['results'])==4
for n,r in enumerate(state['results'],1):
    if not args.first<=n<=args.last: continue
    assert sha(ROOT/r['path'])==r['sha256']
    print('\nITEM',n,r['id'],r['kind'],'seconds',r['seconds'],'SHA',r['sha256'])
    print('EXPECTED:', '\n'.join(r['expectedKo']))
    print('ACTUAL:', r['text'])
    print('ALL_WORDS:',json.dumps(r['words'],ensure_ascii=False))
    if r['kind']=='whole-scene':
        scene=next(x for x in state['candidateScenes'] if r['id']==x['id']+'-whole-candidate')
        with wave.open(str(ROOT/r['path']),'rb') as w: data=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
        join=scene['replacementStartSample'];old_end=scene['retainedOriginalPrefixSamples']
        print('JOIN_EXACT_SAMPLE_BYTES:',json.dumps({k:scene[k] for k in ['retainedOriginalPrefixSamples','zeroGapSamples','replacementStartSample','exactPrefixAndWholeReplacementBytesMatched','prefixBoundaryRms','prefixBoundaryPeak']}))
        for label,center in [('prefix-end',old_end),('new-paragraph-start',join),('whole-ending',len(data)-240)]:
            rows=[]
            for start in range(max(0,center-1200),min(len(data)-239,center+1201),240):
                sample=data[start:start+240].astype(float)
                rows.append(dict(startSample=start,seconds=start/24000,rms=round(float(np.sqrt(np.mean(sample**2))),2),peak=int(np.max(np.abs(sample)))))
            print(label,json.dumps(rows))
    print('Scope: text/clock/sample comparison; human auditory pronunciation remains pending.')
