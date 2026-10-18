"""CPU-only staging of measured representative and remaining M04 capture jobs.

It only reads the parent's completed timeline/current lesson. It never launches
Unity, ffmpeg, a GPU task, TTS or a compositor. Both jobs share final clip stems
and output directory so the initial approved03/07results are reused unchanged.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[5]
OWN=Path(__file__).resolve().parent
LOCAL=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v2'
DEFAULT_TIMELINE=ROOT/'projects/game-math-euler-axis-angle/production/revision-v2/timeline.json'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--timeline',default=str(DEFAULT_TIMELINE));args=ap.parse_args()
    timeline=Path(args.timeline).resolve()
    if not timeline.exists():raise SystemExit('Measured timeline is not ready; no job or active production input was changed.')
    initial_hash=sha(timeline)
    full=LOCAL/'unity-spatial-job.json';placement=LOCAL/'unity-spatial-placement.json'
    subprocess.run([sys.executable,'-X','utf8',str(OWN/'prepare-capture-job.py'),'--timeline',str(timeline),
        '--job',str(full),'--placement',str(placement),'--output-dir',str(LOCAL/'unity-spatial-clips')],check=True)
    data=read(full);first=[c for c in data['clips'] if c['sceneId'] in {'03','07'}]
    rest=[c for c in data['clips'] if c['sceneId'] not in {'03','07'}]
    if {c['sceneId'] for c in first}!={'03','07'}:raise ValueError('Both representative scenes03and07must be present.')
    if len(first)+len(rest)!=len(data['clips']):raise AssertionError('Split lost clips.')
    stems=[c['fileStem'] for c in data['clips']]
    if len(stems)!=len(set(stems)):raise ValueError('Capture stems must be unique.')
    jobs=[]
    for name,clips in [('unity-spatial-first-03-07-job.json',first),('unity-spatial-remaining-job.json',rest)]:
        job=dict(data);job['clips']=clips;path=LOCAL/name
        path.write_text(json.dumps(job,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        jobs.append(dict(path=str(path),sha256=sha(path),sceneIds=sorted({c['sceneId'] for c in clips}),
            clipCount=len(clips),renderedFrames=sum(c['frames'] for c in clips),
            renderedSeconds=sum(c['frames'] for c in clips)/60))
    if sha(timeline)!=initial_hash:raise RuntimeError('Timeline changed during job staging; do not start these jobs until regenerated.')
    report=dict(schemaVersion=1,timeline=str(timeline),timelineSha256=initial_hash,fullJob=str(full),
        fullJobSha256=sha(full),placement=str(placement),placementSha256=sha(placement),
        outputDirectory=data['outputDirectory'],totalClipCount=len(data['clips']),jobs=jobs,
        gpuOrMediaJobsStarted=False,activeNarrationInputsChanged=False,
        order=['Wait for explicit parent ASR-complete GPU handoff',
            'run-isolated-capture.py --job first03/07job --bake',
            'sync-baked-assets.py; render-spatial.py --scene03 --scene07',
            'Parent verifies current timing/captions atFHDand375px',
            'Only after parent instruction capture remainingjob without03/07',
            'Fullcompositor reuses identical03/07hash-cache outputs'])
    (LOCAL/'unity-spatial-two-stage-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
