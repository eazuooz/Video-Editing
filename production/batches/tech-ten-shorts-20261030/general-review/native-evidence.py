"""Seal the measured demonstrations and keep the editable Unity scene with its material GUIDs."""
import csv
import shutil
from render import WORK,MEDIA,HERE,editor

native=WORK/'native-final'
prefabs=MEDIA/'unity-capture/Assets/VideoScenes/GeneralReview'
def rows(path):
    with path.open(encoding='utf8') as stream:return list(csv.DictReader(stream))
base=rows(native/'seed-42/ticks.csv')
alt=rows(native/'seed-7/ticks.csv')
baseline=(MEDIA/'feedback-nov05/unity-rts-layout2/record/state.csv').read_text().splitlines()
assert [r['hp'] for r in base[::2]]==[line.split(',')[1] for line in baseline]
def gaps(trace):
    return [int(r['nextShot'])-i for i,r in enumerate(trace) if i and r['nextShot']!=trace[i-1]['nextShot']]
def file_records(folder,mask):
    return {p.name:editor.sha(p) for p in sorted(folder.glob(mask))}
direct=rows(native/'direct/poses.csv');wrapped=rows(native/'wrapped/poses.csv')
assert all((a['anchorX'],a['anchorY'],a['endX'],a['endY'])==(b['anchorX'],b['anchorY'],b['endX'],b['endY']) for a,b in zip(direct,wrapped))
assert direct[-1]['hit']=='1' and direct[-1]['wrapped']=='0' and wrapped[-1]['wrapped']=='1'
assert [len(list((native/s).glob('*.jpg'))) for s in ['side','direct','wrapped','seed-42','seed-7']]==[91,91,91,195,195]
snapshot=HERE/'unity-scene'
snapshot.mkdir(exist_ok=True)
for pattern in ('*.mat','*.meta','*.unity'):
    for p in prefabs.glob(pattern):shutil.copyfile(p,snapshot/p.name)
proof=dict(renderer=(native/'complete.txt').read_text(),scene=str(prefabs/'RopeAroundPost.unity'),
           captureResolution=[1080,548],renderRate=30,simulationTicksPerSecond=60,
           rope=dict(restLengthSideMeters=3.15,matchedEndpointPairs=len(direct),
                     traceSHA256={m:editor.sha(native/m/'poses.csv') for m in ('side','direct','wrapped')}),
           replay=dict(speed=2.85,seed42Intervals=gaps(base),seed7Intervals=gaps(alt),
                       firstHpDifferenceTick=next(i for i,(a,b) in enumerate(zip(base,alt)) if a['hp']!=b['hp']),
                       hpAtTick389={42:int(base[-1]['hp']),7:int(alt[-1]['hp'])},
                       traceSHA256={s:editor.sha(native/f'seed-{s}/ticks.csv') for s in (42,7)}),
           assetsSourceRecord='../feedback-nov05/unity-source.json', editableFiles=file_records(snapshot,'*'))
editor.save(HERE/'native-evidence.json',proof)
