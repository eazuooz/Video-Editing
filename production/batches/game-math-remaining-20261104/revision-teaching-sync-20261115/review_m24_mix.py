"""Evidence for the specific M24 ASR differences inspected in this revision."""
import json,os,subprocess
from pathlib import Path
import numpy as np
from inventory import ROOT,HERE,read,save
from render_revision import FF,CREATE

folder=ROOT/'projects/game-math-velocity-derivatives/production/local/teaching-sync-v2'
d=read(folder/'mix-evidence.json')
e=next(e for e in read(HERE/'inventory.json')['episodes'] if e['id']=='M24')
assert len(d['paragraphs'])==47 and set(d['changedRecognition'])=={'019','030'}
assert d['levelFlagScenes']==['000']
digest=d['captionedSha256']
pcm=Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingScratch/math-teaching-sync-v2'/e['slug']/digest[:16]/'actual-final-body-mono.wav'
a=np.frombuffer(subprocess.check_output([str(FF),'-v','error','-nostdin','-threads','1',
    '-i',e['baselineOutputs']['clean'],'-ss','2','-t','45','-vn','-ar','48000','-ac','1','-f','f32le','-'],creationflags=CREATE),dtype=np.float32)
b=np.frombuffer(subprocess.check_output([str(FF),'-v','error','-nostdin','-threads','1',
    '-i',str(pcm),'-t','45','-ar','48000','-ac','1','-f','f32le','-'],creationflags=CREATE),dtype=np.float32)
rows=[]
for r in d['paragraphs']:
    for w in r['suspectLevelWindows']:
        j=round((w['time']-2)*48000);x=a[j:j+4800].astype(float);y=b[j:j+4800].astype(float)
        gain=float(20*np.log10(np.sqrt(np.mean(y*y)/np.mean(x*x))))
        correlation=float(np.corrcoef(x,y)[0,1])
        assert abs(gain)<.2 and correlation>.99,(gain,correlation)
        rows.append(dict(time=w['time'],gainAgainstBaselineMixedDb=gain,mixedCorrelation=correlation))
new=next(r for r in d['paragraphs'] if r['scene']=='004')
assert new['coverage']==1 and not new['suspectLevelWindows']
save(folder/'mix-review.json',dict(status='pass',captionedSha256=digest,
    method='Actual whole final mix ASR, all paragraph comparisons and local levels; inherited intro game bed compared against the original mixed audio',
    all47ParagraphsReviewed=True,flaggedIntroMixedAudioComparison=rows,newMarioRange=new['localGainRange'],
    recognitionFindings=['019: minor grammatical recognizer variant; expected coverage 1.0.',
        '030: dx/dt token spacing; derivative notation preserved. Other paragraphs normalize to their prior recognition.'],
    actualHumanListening=False))
print(json.dumps(rows));print('M24 final whole mix evidence reviewed; human listening remains pending')
