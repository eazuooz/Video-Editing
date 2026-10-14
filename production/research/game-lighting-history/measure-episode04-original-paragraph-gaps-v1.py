"""Inspect original PCM around ASR paragraph transitions without rewriting audio."""
from pathlib import Path
import datetime,hashlib,json,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
anchor_path=BASE/'local/original-word-anchors-draft-v1.json'
anchors=json.loads(anchor_path.read_text('utf-8-sig'))
audio=ROOT/anchors['originalAudio']['path']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(audio)!=anchors['originalAudio']['sha256']:raise RuntimeError('Original PCM changed')
with wave.open(str(audio),'rb') as f:
    if (f.getnchannels(),f.getsampwidth(),f.getframerate())!=(1,2,24000):raise RuntimeError('PCM format changed')
    data=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.int32)
sr=24000;hop=240;records=[]
for chapter in anchors['chapters']:
    origin=chapter['currentOriginalSampleRange'][0]
    for left,right in zip(chapter['paragraphs'],chapter['paragraphs'][1:]):
        a=left['sceneRelativeSpokenSeconds'][1];b=right['sceneRelativeSpokenSeconds'][0];target=(a+b)/2
        first=max(origin,origin+round((target-.8)*sr));last=min(chapter['currentOriginalSampleRange'][1],origin+round((target+.8)*sr))
        starts=list(range(first,last-hop+1,hop))
        peaks=[int(np.max(np.abs(data[i:i+hop]))) for i in starts]
        candidates=[];run=None
        for k,peak in enumerate(peaks+[32768]):
            if peak<=66 and run is None:run=k
            if peak>66 and run is not None:
                if k-run>=4:
                    start=starts[run];end=starts[k-1]+hop;middle=(start+end)//2
                    candidates.append(dict(originalSampleRange=[start,end],sceneRelativeSeconds=[(start-origin)/sr,(end-origin)/sr],samples=end-start,peakMax=max(peaks[run:k]),middleSample=middle,middleShiftFromAsrMidpointSeconds=(middle-origin)/sr-target))
                run=None
        candidates.sort(key=lambda x:abs(x['middleShiftFromAsrMidpointSeconds']))
        records.append(dict(leftId=left['id'],rightId=right['id'],scene=chapter['scene'],leftLastWord=left['lastWord'],rightFirstWord=right['firstWord'],asrGapSeconds=[a,b],candidates=candidates,envelope10ms=dict(firstSample=first,peaks=peaks),actualCutApproved=False))
out=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalAudio=anchors['originalAudio'],anchors=dict(path=anchor_path.relative_to(ROOT).as_posix(),sha256=sha(anchor_path)),thresholdPcm16=66,hopSamples=hop,minimumQuietRunSamples=960,records=records,scope='Low-amplitude PCM candidate runs near observed spoken boundaries; direct word/gap review required, no audio edit or ASR approval.',allActualCutsApproved=False)
path=BASE/'local/original-paragraph-gap-measurements-v1.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
for r in records:
    print(json.dumps(dict(left=r['leftId'],right=r['rightId'],asr=r['asrGapSeconds'],lastWord=r['leftLastWord']['text'],firstWord=r['rightFirstWord']['text'],candidates=r['candidates'][:3]),ensure_ascii=False))
