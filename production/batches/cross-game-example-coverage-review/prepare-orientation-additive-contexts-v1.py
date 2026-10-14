"""Prepare complete sentence contexts from current whole words and exact PCM."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave, numpy as np
ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = O / 'additions-independent-context-proposal-v1.json'
assert not out.exists(), 'Preserve the prepared plan.'
whole_path = O / 'additions-whole-asr-execution-v1.json'
whole = read(whole_path)
assert whole['actualExitObserved'] and whole['actualOuterExitCode'] == 0
# Directly read current whole word ends/next starts. Do not split within a word.
gaps = {'02a': [(3.18,3.18),(5.44,5.44),(11.5,11.72)],
    '06a': [(3.46,3.68),(7.4,7.8)],
    '09a': [(3.38,3.62),(8.22,8.42),(10.34,10.54)],
    '13a': [(3.12,3.28),(6.64,6.86),(11.5,11.66)],
    '16a': [(5.84,6.1),(8.3,8.7),(10.98,11.18)],
    '21a': [(4.9,5.3),(10.94,11.24)]}
contexts = []
for row in whole['results']:
    source = ROOT / row['sourcePath']
    assert sha(source) == row['sourceSha256']
    with wave.open(str(source), 'rb') as wav:
        assert (wav.getframerate(),wav.getnchannels(),wav.getsampwidth()) == (24000,1,2)
        frames = wav.getnframes()
        pcm = wav.readframes(frames)
    signal = np.frombuffer(pcm, dtype='<i2')
    bounds = [0]
    evidence = []
    for a,b in gaps[row['id']]:
        lo,hi = round(a*24000),round(b*24000)
        # A zero-width timestamp gap uses that boundary only; surrounding energy is disclosed.
        mid = (lo+hi)//2
        if hi-lo >= 960:
            candidates = range(lo+240,hi-239,120)
            mid = min(candidates,key=lambda x:np.mean(signal[x-240:x+240].astype(float)**2))
        energy = signal[max(0,mid-240):min(frames,mid+240)].astype(float)
        evidence.append(dict(wordGapSeconds=[a,b], boundarySample=mid,
            boundarySeconds=mid/24000, windowSamples=480,
            rmsInt16=float(np.sqrt(np.mean(energy**2))),
            peakInt16=int(np.max(np.abs(energy))),
            zeroWidthWordGap=a==b, acousticOrHumanListeningApproval=False))
        bounds.append(mid)
    bounds.append(frames)
    assert len(bounds) == len(row['expectedKo'])+1
    for i,line in enumerate(row['expectedKo']):
        a,b = bounds[i:i+2]
        assert 0 <= a < b <= frames
        contexts.append(dict(id=f'{row["id"]}-p{i+1:02}',sceneId=row['id'],paragraphIndex=i,
            expectedKo=line,sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],
            startSample=a,endSample=b,sourceSampleRate=24000,
            startSeconds=a/24000,endSeconds=b/24000,zeroPaddingSamplesEachSide=7200,
            exactContextPcmSha256=hashlib.sha256(pcm[a*2:b*2]).hexdigest(),
            expectedWasRecognizerPrompt=False,boundaryEvidence=evidence))
assert len(contexts) == 22
data = dict(createdAt=datetime.now(timezone.utc).isoformat(),
    wholeExecution=whole_path.relative_to(ROOT).as_posix(),wholeExecutionSha256=sha(whole_path),
    contexts=contexts,boundariesDirectlyComparedWithCurrentWordsAndPCM=False,
    modelExecuted=False,finalMixedAsrApproved=False,humanListeningApproved=False)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(proposal=out.relative_to(ROOT).as_posix(),contexts=22,
    boundaries={r['id']:contexts[sum(len(z['expectedKo']) for z in whole['results'][:j])]['boundaryEvidence'] for j,r in enumerate(whole['results'])}),ensure_ascii=False))
