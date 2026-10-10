"""Observe only this series' owned worker identities; never change another queue."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, os, psutil
ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / 'projects/game-lighting-history-03/production'
def read(p): return json.loads(p.read_text('utf-8-sig'))
def save(p, d):
    temp = p.with_name(p.name + '.writing-' + str(os.getpid()))
    temp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)
def identity(d):
    if not d: return None
    try:
        p = psutil.Process(d['pid'])
        match = abs(p.create_time() - d['createTime']) < .01
        return dict(d, alive=match, actualCommandLine=p.cmdline() if match else None,
                    actualCreateTime=p.create_time(), pidReused=not match)
    except psutil.NoSuchProcess:
        return dict(d, alive=False, pidReused=False)
parser = argparse.ArgumentParser()
parser.add_argument('kind', choices=['native', 'explanation', 'mix', 'asr', 'pair', 'diagnostic', 'recovery', 'pixels'])
parser.add_argument('--session', type=int, required=True)
a = parser.parse_args()
names = dict(native='native-framing-execution-v16.json',
             explanation='explanation-framing-execution-v15.json', mix='review-mix-execution-v15.json',
             asr='review-mixed-asr-execution-v15.json', pair='review-pair-execution-v15.json',
             diagnostic='caption-frame-property-diagnostic-execution-v15.json',
             recovery='review-pair-recovery-execution-v16.json', pixels='encoded-pixel-review-execution-v15.json')
state_path = PROD / names[a.kind]
d = read(state_path)
record = dict(observedAt=datetime.now(timezone.utc).isoformat(), kind=a.kind,
              sessionId=a.session, state=state_path.relative_to(ROOT).as_posix(),
              status=d['status'], worker=identity(d.get('worker')),
              active=identity(d.get('active')), completed=len(d.get('results', [])),
              total=d.get('total', 112 if a.kind == 'native' else 47 if a.kind == 'explanation' else 2 if a.kind == 'pair' else None),
              cpuThreads=2, gpuJobs=0, exitCode=d.get('exitCode'),
              allFinalPixelsReviewed=False, finalMixedAsrApproved=False,
              collected=False, uploaded=False)
if a.kind == 'diagnostic':
    record['total'] = 1
    record['completed'] = 1 if d['status'] == 'complete' else 0
if a.kind == 'recovery':
    record['total'] = 2
if a.kind == 'pixels':
    record['total'] = 1842
    record['completed'] = len(d.get('images', []))
save(PROD / (a.kind + '-review-media-observation-v15.json'), record)
cp_path = ROOT / 'production/research/game-lighting-history/checkpoint.json'
cp = read(cp_path)
cp['updatedAt'] = record['observedAt']
cp['stage'] = 'episode03-' + a.kind + '-review-media-' + d['status']
cp['episode03' + a.kind.title() + 'ReviewMedia'] = record
cp['ownedJobsRunning'] = [x for x in [record['worker'], record['active']] if x and x['alive']]
cp['next'] = ('Finish and directly compare all54 current mixed-ASR windows, then verify existing '
              'PCM/window provenance without repeating synthesis or recognition. After explicit '
              'current-mix content review, encode one clean/captioned pair and inspect spatial '
              'motion and every caption/cut pixel before output collection, publishing or Git.')
if a.kind in ['pair', 'recovery']:
    cp['next'] = ('Preserve the sole current CPU2 review-pair worker through clean mux, captioned encode, '
                  'both whole decodes, exact93084/90000/1500PTS and identicalAAC checks. Then extract the '
                  '1842 planned final frames once and directly review all307 boards and spatial motion '
                  'before final QA, four-file collection, publishing and selective Git.')
if a.kind == 'diagnostic':
    cp['next'] = ('Preserve clean, failed captioned encode and completed input media. Read decoded '
                  'frame-property transitions and exact input PTS to determine why captioned video '
                  'has88501 instead of93084 frames. Repair only the affected encoding path after '
                  'observing the cause; no TTS, mix, native or explanation reruns. Final QA remains false.')
save(cp_path, cp)
print(json.dumps({k: record[k] for k in ['kind', 'status', 'completed', 'total', 'sessionId']}, ensure_ascii=False))
