"""Bind37 reviewed silent inputs without changing the measured timeline or PCM."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess
ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
rel = lambda p: p.resolve().relative_to(ROOT).as_posix()
out = O / 'current34-assembly-inputs-v1.json'
assert not out.exists()
planp = O / 'current34-measured-timing-plan-v1.json'; plan = read(planp)
review = read(O / 'current34-mixed-complete-direct-review-v1.json')
assert review['all180ContextsDirectlyCompared'] and review['all34WholeTextsDirectlyCompared']
assert read(O / 'current34-caption-alignment-v1.json')['allNewCueTimingDirectlyReviewed']
overview = read(O / 'current34-overview-render-execution-v4.json')
ovreview = read(O / 'current34-overview-direct-review-v4.json')
assert overview['actualOuterExitCode'] == 0 and ovreview['all110SamplesDirectlyRead']
assert ovreview['normalPlaybackReviewed'] and ovreview['captionReservedAreaClear']
guides = read(O / 'current34-baseline-guides-render-execution-v1.json')
greview = read(O / 'current34-baseline-guides-direct-review-v1.json')
assert guides['actualOuterExitCode'] == 0 and greview['allPlannedEncodedSamplesDirectlyRead']
assert greview['normalPlaybackReviewed'] and greview['currentNarrationTimingReviewed']
proof = read(O / 'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs'] + proof['results']:
    assert sha(ROOT / x['path']) == x['sha256']
oldconcat = ROOT / 'shared/output/game-math-orientation-matrices/concat.txt'
oldtext = oldconcat.read_text('utf-8-sig')
ov = {x['id']: x for x in overview['scenes']}
gs = {x['id']: x for x in guides['results']}
pieces = []
def add(sid, path, frames, actual, explanation, *, baseline=False, source_sha=None, note=''):
    p = ROOT / path; digest = sha(p)
    if source_sha: assert digest == source_sha
    streams = json.loads(subprocess.check_output([FP, '-v', 'error', '-show_streams', '-of', 'json', str(p)]))['streams']
    assert len(streams) == 1 and streams[0]['codec_type'] == 'video', (sid, 'Silent input required')
    v = streams[0]; n = int(v['nb_frames'])
    assert (v['width'], v['height'], v['r_frame_rate'], v['codec_name']) == (1920, 1080, '60/1', 'h264')
    assert 0 <= frames-n <= 1 and actual+explanation == frames, (sid, n, frames)
    if baseline:
        assert f"file '{p.as_posix()}'" in oldtext and n == frames and v['time_base'] == '1/90000'
    pieces.append(dict(id=sid, path=rel(p), sha256=digest, frames=frames, encodedFrames=n,
        actualFrames=actual, explanationFrames=explanation,
        reencodeRequired=v['time_base'] != '1/90000' or n != frames,
        explanationTailPadFrames=frames-n, retainedOriginalSilentBytes=baseline,
        sourceTimeBase=v['time_base'], classificationNote=note, finalCaptionPixelsReviewed=False))
basefolder = 'shared/output/game-math-orientation-matrices/clips/'
add('intro', basefolder+'intro.mp4', 120, 0, 120, baseline=True, note='Excluded original branding.')
for s in plan['scenes']:
    sid = s['id']; n = s['frames']
    if sid in ov:
        x = ov[sid]; add(sid, x['output'], n, 0, n, source_sha=x['outputSha256'])
    elif sid in gs:
        x = gs[sid]; add(sid, x['output'], n, n, 0, source_sha=x['outputSha256'], note='Unique reviewed normal-speed native gameplay; screen guides only.')
    elif sid == '02a':
        for name, f, a, e in [('02a', 1033, 1032, 1), ('02aext', 486, 486, 0)]:
            x = read(O / (name+'-tracked-render-execution-v1.json'))
            assert x['actualOuterExitCode'] == 0
            add(name, x['output'], f, a, e, source_sha=x['outputSha256'],
                note='One existing last-frame hold counts as explanation.' if name == '02a' else 'Unique contiguous source extension, normal speed.')
    elif s['visual']:
        add(sid, s['visual'], n, s['actualFrames'], s['explanationFrames'], source_sha=s['visualSha256'])
    else:
        assert s['baseline'] and s['actualFrames'] == 0
        add(sid, basefolder+sid+'.mp4', n, 0, n, baseline=True, note='Original useful explanation retained without reencoding.')
add('outro', basefolder+'outro.mp4', 600, 0, 600, baseline=True, note='Excluded original membership ending.')
assert len(pieces) == 37 and sum(x['frames'] for x in pieces) == plan['totalFrames']
body = pieces[1:-1]; actual = sum(x['actualFrames'] for x in body); explanation = sum(x['explanationFrames'] for x in body)
assert actual == 26078 and explanation == 39119 and actual+explanation == plan['bodyFrames']
error = actual-plan['bodyFrames']*.4; assert abs(error) <= 1
data = dict(preparedAt=datetime.now(timezone.utc).isoformat(), plan=rel(planp), planSha256=sha(planp),
    pieces=pieces, totalFrames=plan['totalFrames'], bodyFrames=plan['bodyFrames'], actualFrames=actual,
    explanationFrames=explanation, ratioErrorFrames=error, ratioContract='legacylecture40actual60explanation/noBGM',
    classificationAdjustment=dict(scene='02a', actualToExplanationFrames=1,
        reason='Existing1033-frame tracked piece has1032 unique native frames and one final-frame hold. Timing/audio unchanged.'),
    baselineConcat=rel(oldconcat), baselineConcatSha256=sha(oldconcat), retainedByteIdenticalPieces=14,
    inputClassificationApprovedForAssembly=True, finalRatioApproved=False, allFinalPixelsApproved=False,
    newTts=0, sourceAudio=False, newGitMedia=0)
assert sum(x['retainedOriginalSilentBytes'] for x in pieces) == 14
out.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(inputs=37, retained=14, actual=actual, explanation=explanation, errorFrames=error, finalPixels=False)))
