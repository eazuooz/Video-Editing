"""Five new reframing/caption previews from already-extracted native frames."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess
from PIL import Image
from orientation_07b_caption_clearance_v1 import reframe, INTERVALS

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
L = ROOT / 'shared/output/unpublished-teaching-clarity-revision/orientation/07b-caption-clearance-static-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
rd = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
ap = argparse.ArgumentParser(); ap.add_argument('--resource', required=True); args = ap.parse_args()
r = rd(ROOT / args.resource)
assert r['ownHeavyJobs'] == 0 and r['guardPassed']
assert (datetime.now(timezone.utc) - datetime.fromisoformat(r['observedAt'])).total_seconds() < 240
assert not L.exists(); L.mkdir(parents=True)
ass = O / 'current34.captions.ko.ass'
prior = rd(O / 'current34-mixed-detailed-render-execution-v2.json')
source = next(x for x in prior['results'] if x['id'] == '07b')
rows = []
for frame in (391, 582, 1622, 1623, 1788):
    sample = next(x for x in source['samples'] if x['frame'] == frame)
    assert sha(ROOT / sample['path']) == sample['sha256']
    with Image.open(ROOT / sample['path']) as im:
        result = reframe(im.convert('RGB'))
    clean = L / f'frame-{frame}-reframed.png'; result.save(clean)
    captioned = L / f'frame-{frame}-captioned.png'
    absolute_frame = 19149 + frame
    cmd = [FF, '-hide_banner', '-nostdin', '-v', 'error', '-threads', '2',
        '-filter_threads', '1', '-i', str(clean), '-vf',
        f'setpts=PTS+{absolute_frame}/60/TB,ass={rel(ass)}',
        '-frames:v', '1', '-update', '1', '-threads', '2', str(captioned)]
    run = subprocess.run(cmd, cwd=ROOT, capture_output=True)
    assert run.returncode == 0, run.stderr.decode('utf-8', errors='replace')
    rows.append(dict(frame=frame, absoluteFrame=absolute_frame,
        retainedSource=sample['path'], retainedSourceSha256=sample['sha256'],
        clean=rel(clean), cleanSha256=sha(clean), captioned=rel(captioned),
        captionedSha256=sha(captioned), actualFfmpegExitCode=run.returncode))
p = O / '07b-caption-clearance-static-preparation-v1.json'; assert not p.exists()
p.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(),
    resource=args.resource, resourceSha256=sha(ROOT / args.resource),
    code='production/batches/cross-game-example-coverage-review/orientation_07b_caption_clearance_v1.py',
    codeSha256=sha(Path(__file__).with_name('orientation_07b_caption_clearance_v1.py')),
    sourceVideo=source['output'], sourceVideoSha256=source['outputSha256'],
    actualCaptionAss=rel(ass), actualCaptionAssSha256=sha(ass),
    intervals=INTERVALS, changedFrames=360, unchangedFrames=1720,
    aspectRatioPreserved=True, allSourceUiRetained=True, sameFrameBackground=True,
    fixedCaptionCenter=[960,970], rows=rows, staticPixelsApproved=False,
    movingPixelsApproved=False, renderExecuted=False, durationAndRatioPreserved=True,
    sourceExtractionRepeated=0, newTts=0, newAsr=0, newMix=0, newImageGit=0),
    ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(newStaticSamples=len(rows), sourceExtractionRepeated=0,
    renderExecuted=False, preparation=rel(p))))
