"""Combine approved large-cat pictures and the unchanged approved BGM AAC mix.

No TTS, frame render, retiming, music guessing or new audio encoding.
"""
from pathlib import Path
import importlib.util
import json
import shutil

spec = importlib.util.spec_from_file_location('base', Path(__file__).with_name('finish-fairness60.py'))
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
R, P, S = f.R, f.P, f.S
L = P / 'production/local/fairness-60s-reactions-bgm-v1'
VISUAL = P / 'production/local/fairness-60s-reactions-v1/visual-review-v3.captioned.mp4'
CLEAN = R / 'shared/output/motion-canvas/shorts-forgiving-hitbox-reactions60-full-v3.mp4'
MIX = P / 'production/local/fairness-60s-bgm/final-mix.m4a'


def packets(path, stream):
    return json.loads(f.run([f.FP, '-v', 'error', '-select_streams', stream,
        '-show_packets', '-show_data_hash', 'sha256', '-show_entries',
        'packet=pts_time,duration_time,data_hash', '-of', 'json', str(path)]).stdout)['packets']


def main():
    control = f.read(R / 'shared/publishing/video-production-control.json')['shortsRecurringAuthorization']
    assert control['selectedShort'] == S
    assert control['latestSelection']['currentUploadAuthorization']['status'] == 'authorized-combination-of-reviewed-components'
    assert f.sha(VISUAL) == 'cc07d64d0644a234121b89ac5b5198485728f2527fd4e837fb23608f38858365'
    assert f.sha(CLEAN) == 'd67e1a419bb9def21458b66e472ae68be71a2de22b513cce9fcf636ac8ac31ea'
    oldqa = f.read(P / 'production/local/fairness-60s-bgm/asr-full-review.json')
    assert oldqa['canonicalFullTextMatch'] and oldqa['fullMixCompared']
    assert f.sha(MIX) == f.read(P / 'production/local/fairness-60s-bgm/audio-build.json')['finalMixSha256']
    L.mkdir(parents=True, exist_ok=True)
    results = {}
    for kind, source in [('clean', CLEAN), ('captioned', VISUAL)]:
        dest = L / f'{S}.{kind}.mp4'
        assert not dest.exists(), 'Preserve completed output; inspect existing receipt instead.'
        f.run([f.FF, '-v', 'error', '-n', '-i', str(source), '-i', str(MIX),
            '-map', '0:v:0', '-map', '1:a:0', '-t', '60', '-c', 'copy',
            '-movflags', '+faststart', str(dest)])
        meta = json.loads(f.run([f.FP, '-v', 'error', '-show_streams', '-of', 'json', str(dest)]).stdout)
        v = next(x for x in meta['streams'] if x['codec_type'] == 'video')
        assert (v['width'], v['height'], v['r_frame_rate'], int(v['nb_frames'])) == (1080, 1920, '60/1', 3600)
        assert float(v['duration']) == 60
        assert packets(dest, 'v:0') == packets(source, 'v:0')
        assert packets(dest, 'a:0') == packets(MIX, 'a:0')
        framehash = L / f'{kind}.framehash'
        f.run([f.FF, '-v', 'error', '-n', '-i', str(dest), '-map', '0:v:0',
            '-f', 'framehash', str(framehash), '-map', '0:a:0', '-f', 'null', '-'])
        rows = [x for x in framehash.read_text().splitlines() if not x.startswith('#')]
        assert len(rows) == 3600 and [int(x.split(',')[2]) for x in rows] == list(range(3600))
        if kind == 'captioned':
            prior = P / 'production/local/fairness-60s-reactions-v1/qa-v3/visual-review.framehash'
            assert rows == [x for x in prior.read_text().splitlines() if not x.startswith('#')]
        results[kind] = dict(path=dest.relative_to(R).as_posix(), sha256=f.sha(dest),
            bytes=dest.stat().st_size, fullDecode=True, uniformPts=True, frames=3600,
            identicalVideoPackets=True, identicalAacPackets=True)
    for lang in ('ko', 'en'):
        shutil.copy2(P / f'production/local/fairness-60s-bgm/captions.{lang}.srt', L / f'captions.{lang}.srt')
    f.save(L / 'technical.json', dict(status='pass', seconds=60, format=[1080, 1920, 60], files=results,
        videoSourceSha256=f.sha(VISUAL), audioSourceSha256=f.sha(MIX),
        audioEvidenceReused=['production/local/fairness-60s-bgm/asr-full-review.json',
            'production/local/fairness-60s-bgm/qa/audio-continuity.json'],
        audioReuseReason='Identical compressed AAC packet data, PTS and duration; no remux audio alteration.',
        visualEvidenceReused='production/revisions/fairness-60s-reactions-large-right-v2.json',
        noNewTts=True, noNewAudioEncode=True, noRetiming=True,
        music='Pixel Peeker Polka - faster / Kevin MacLeod, previous approved licensed mix; not identified as reference song',
        humanWholeListening='not newly asserted'))
    print(json.dumps(results, ensure_ascii=False))


if __name__ == '__main__':
    main()
