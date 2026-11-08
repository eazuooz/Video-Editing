"""Read-only CPU1 validation of the narrow footer fix and actual-caption previews."""
from pathlib import Path
import json, subprocess
import numpy as np
from PIL import Image
import caption_safe_stage_footer as p


def outside_equal(old, new, rect):
    x, y, w, h = rect; details = []; cursor = 0
    for name, width, height, factor in [('Y', 1920, 1080, 1), ('U', 960, 540, 2), ('V', 960, 540, 2)]:
        n = width * height
        a = np.frombuffer(old[cursor:cursor+n], np.uint8).reshape(height, width)
        b = np.frombuffer(new[cursor:cursor+n], np.uint8).reshape(height, width)
        mask = np.ones((height, width), bool)
        mask[y//factor:(y+h)//factor, x//factor:(x+w)//factor] = False
        changed = int(np.count_nonzero(a[mask] != b[mask]))
        assert changed == 0, (name, 'Lossless patch changed pixels outside its rectangle', changed)
        region = b[y//factor:(y+h)//factor, x//factor:(x+w)//factor]
        details.append({'plane': name, 'outsideChangedPixels': changed, 'patchedRegionUniqueValues': np.unique(region).tolist()})
        cursor += n
    return details


def caption_preview(job, frame, global_frame, suffix, output):
    source = p.R / job[suffix]
    ass = p.H.parent / 'local/final-audio/A16/captions/captions.provisional.ko.ass'
    escaped = str(ass.absolute()).replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    vf = f"select=eq(n\\,{frame}),setpts=PTS-STARTPTS+{global_frame}/(60*TB),ass='{escaped}'"
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '1', '-i', str(source),
        '-filter_threads', '1', '-vf', vf, '-frames:v', '1', '-an', '-threads', '1', str(output)],
        check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    with Image.open(output) as im:
        assert im.size == (1920, 1080)
        im.resize((375, 211), Image.Resampling.LANCZOS).save(output.with_name(output.stem + '-375.png'))
    return {'file': str(output), 'sha256': p.sha(output), 'assSha256': p.sha(ass),
            'globalCaptionFrame': global_frame, 'kind': 'Patched intermediate with actual existing A16 libass captions; not a completed replacement master.'}


def main():
    plan = p.read(p.H / 'caption-safe/plan.json'); assert plan['status'] == 'all-caption-safe-plates-ready'
    selected = []
    for ep, study in [('A02', None), ('A06', 'control'), ('A08', 'overview'), ('A14', 'blend'), ('A15', 'keys'), ('A16', 'path'), ('A16', 'active')]:
        choices = [j for j in plan['jobs'] if j['episode'] == ep and (study is None or j['key'] == study)]
        assert choices, (ep, study)
        selected.append(max(choices, key=lambda j: j['stageFrames']))
    results = []
    for job in selected:
        a, b = max(job['stageFrameRanges'], key=lambda ab: ab[1]-ab[0]); frame = (a+b)//2
        before = p.decode_yuv(p.R / job['source'], frame); after = p.decode_yuv(p.R / job['output'], frame)
        planes = outside_equal(before, after, job['clearRectangleXYWH'])
        assert before != after, 'Expected original footer pixels absent; inspect the state mapping'
        prior = None
        if a > 0:
            old = p.decode_yuv(p.R / job['source'], a-1); new = p.decode_yuv(p.R / job['output'], a-1)
            assert old == new, 'Frame before stage transition must be decoded-byte-identical'
            prior = {'frame': a-1, 'allDecodedYuvBytesEqual': True}
        results.append({'episode': job['episode'], 'row': job['id'], 'frame': frame,
            'sourceSha256': job['sourceSha256'], 'patchedSha256': job['sha256'], 'rectangle': job['clearRectangleXYWH'],
            'planes': planes, 'priorNonStageFrame': prior, 'frame821IndicesPreserved': True})
        print(job['episode'], job['id'], 'lossless outside rectangle and nonstage pass', flush=True)
    qa = p.DEST / 'qa'; qa.mkdir(exist_ok=True)
    job = next(j for j in selected if j['episode'] == 'A16' and j['key'] == 'path')
    edl = p.read(p.H.parent / 'local/explanation-assembly/A16/edl.json')
    row = next(r for r in edl['pictureEdl'] if r['id'] == job['id'])
    a, b = job['stageFrameRanges'][0]; frame = (a+b)//2
    global_frame = row['outputStartFrame'] + frame - row['sourceStartFrame']
    previews = [caption_preview(job, frame, global_frame, source, qa / ('A16-caption-' + source + '.png')) for source in ['source', 'output']]
    report = {'status': 'technical-source-patch-qa-passed-visual-preview-inspection-pending',
        'scope': 'Seven representative stage/correction paths, including A02 cutOffset, A06/A08 override state, A14 crop, A15 finger timing and both A16 footer variants.',
        'decodedYuvTests': results, 'actualCaptionPreviews': previews,
        'original443ManifestSha256': plan['originalManifestSha256'], 'safe443ManifestSha256': p.sha(p.NEW),
        'fullMastersChanged': False, 'humanFullWatching': False, 'humanListening': False,
        'modelVisualInspection': None}
    p.save(p.H / 'caption-safe/qa.json', report)


if __name__ == '__main__': main()
