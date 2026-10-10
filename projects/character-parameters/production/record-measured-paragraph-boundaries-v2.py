"""Record manually compared original paragraph clocks without changing PCM.

08/09 use exact retained prefixes; their new final paragraph clocks must still
be confirmed in the fresh candidate ASR. These clocks do not approve an edit.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
times=[[0,3.89,10.19],[0,8.19,17.90],[0,9.95,19.39],
       [0,8.80,17.14],[0,9.00,18.20],[0,8.83,17.98,28.73],
       [0,8.56,19.59],[0,9.57],[0,9.97],
       [0,7.72,19.32],[0,9.65,22.18],[0,9.67,20.70]]
tts=read(BASE/'narration-tts-execution-v2.json')
rows=[]
for index,row in enumerate(tts['results']):
    p=ROOT/row['path'];assert sha(p)==row['sha256']
    with wave.open(str(p),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
    boundaries=[]
    for t in times[index][1:]:
        n=round(t*24000);block=pcm[n-120:n+120].astype(float)
        rms=float(np.sqrt(np.mean(block*block)));peak=int(abs(block).max())
        assert rms<350 and peak<1600
        boundaries.append(dict(seconds=t,sample=n,pcm10msRms=rms,pcm10msPeak=peak))
    asr=BASE/'current-whole-asr-v1'/f"{row['id']}.json"
    rows.append(dict(id=row['id'],sourcePath=row['path'],sourceSha256=row['sha256'],
                     paragraphStarts=times[index],quietBoundaries=boundaries,
                     wholeAsr=rel(asr),wholeAsrSha256=sha(asr),
                     completeExpectedActualAndWordClocksDirectlyCompared=True,
                     finalParagraphPendingCurrentClarityReview=index in [7,8]))
output=BASE/'measured-paragraph-boundary-direct-review-v2.json'
assert not output.exists()
output.write_text(json.dumps(dict(schemaVersion=2,reviewedAt=datetime.now(timezone.utc).isoformat(),
    rows=rows,scope='Original complete scene/independent contexts and selected low-amplitude PCM boundaries; no PCM phone is removed, no measured timeline adopted.',
    scene06Paragraph4Evidence='Independent complete context resolved the whole-ASR overlap: original offset8.83 minus zero padding.25 plus context quiet20.15 =28.73s.',
    freshScene08And09Pending=True,currentFinalTimingApproved=False,mixedAsrApproved=False,
    humanListening='pending',humanPronunciation='pending',audioModified=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print('Recorded original paragraph clocks and exact quiet PCM bins; current08/09 and final measured edit remain pending.')
