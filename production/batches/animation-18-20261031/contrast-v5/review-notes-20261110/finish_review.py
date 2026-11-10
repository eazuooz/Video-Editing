"""Deliver the feedback revisions on the existing final clock."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys

import numpy as np
from scipy.signal import resample_poly
import soundfile as sf

from plan_observations import BATCH, HERE, OUTPUT, ROOT, TIMECODE, WORK, load, read, save, seconds


MEDIA = Path('C:/Users/1/Videos/YamyamProduction/animation-review-notes-20261110')
RATE = 48000
FPS = 60
SAMPLES_PER_FRAME = RATE // FPS
VENC = ['-threads', '4', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709']
SEGMENT_ENC = VENC + ['-bf', '0', '-g', '120', '-sc_threshold', '0', '-r', '60', '-video_track_timescale', '60000']
VISUAL_REVISIONS = {'A06', 'A08', 'A11'}
NOTES = {
    'A06': '데이지와 마리사 실제 플레이를 본문 다섯 곳에 추가하고, 후속 동작은 손목 궤적 한 줄로 표시했습니다.',
    'A08': '링 피트 전사 자세 I를 참고해 양손이 몸 앞에서 머리 위로 올라가고, 앞뒤로 놓인 발 위에서 몸통이 기울도록 수정했습니다.',
    'A11': '같은 회전 발차기에서 준비와 다리를 뻗는 데 쓰는 시간만 바꿔 비교합니다.',
}
sys.path.insert(0, str(ROOT / 'projects/animation-breaking-down-attack-animations/production/grid-v1'))
import caption_pipeline as captions


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def invoke(args, log):
    with Path(log).open('ab') as stream:
        subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-y', *map(str, args)],
                       check=True, stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)


def check_video(path, frames, audio):
    import json
    result = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                                 '-of', 'json', str(path)]))
    video = next(row for row in result['streams'] if row['codec_type'] == 'video')
    assert (video['width'], video['height'], video['avg_frame_rate'], int(video['nb_frames'])) == (1920, 1080, '60/1', frames), (path, video)
    if audio:
        audio = next(row for row in result['streams'] if row['codec_type'] == 'audio')
        assert (audio['codec_name'], audio['channels'], audio['sample_rate']) == ('aac', 2, '48000')


def audio_payload(path):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0',
                                    '-c:a', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], text=True).strip()


def load_take(path):
    voice, rate = sf.read(path, dtype='float32')
    assert voice.ndim == 1 and np.isfinite(voice).all()
    # Preserve the spoken line. Remove only leading and trailing near-silence.
    activity = np.flatnonzero(np.abs(voice) >= np.max(np.abs(voice)) * .018)
    assert len(activity)
    a = max(0, activity[0] - round(rate * .04))
    b = min(len(voice), activity[-1] + round(rate * .09))
    voice = resample_poly(voice[a:b], RATE, rate).astype('float32')
    return voice, (int(a), int(b)), rate


def voice_window(row, samples):
    a, b = row['available']
    if samples > (b - a) * SAMPLES_PER_FRAME:
        # The planner reserved 14 and 11 frames on the two sides. A close fit
        # can use part of that margin while keeping at least six clear frames.
        a, b = a - 8, b + 5
    return a * SAMPLES_PER_FRAME, b * SAMPLES_PER_FRAME


def mix(record, plan, folder):
    baseline = record['technicalQa']['audioInput']
    assert sha(baseline['source']) == baseline['sha256']
    data, rate = sf.read(baseline['source'], dtype='float32', always_2d=True)
    assert rate == RATE and data.shape[1] == 2
    before = data.copy()
    evidence = []
    for row in plan:
        path = WORK / 'voice/chunks' / (row['id'] + '-scene.wav')
        if not path.exists():
            candidates = list((WORK / 'voice').rglob(row['id'] + '-scene.wav'))
            assert len(candidates) == 1, ('voice missing', row['id'])
            path = candidates[0]
        proof = load(WORK / 'readback' / f'{row["id"]}.json')
        assert proof['sha256'] == sha(path) and proof['expected'] == row['ko']
        voice, source_samples, source_rate = load_take(path)
        a, b = voice_window(row, len(voice))
        assert len(voice) <= b - a, ('line too long', row['id'], len(voice) / RATE, (b - a) / RATE)
        # Leave an initial beat to see the clip, then speak during the repeat.
        begin = round((a + .43 * (b - a - len(voice))) / SAMPLES_PER_FRAME) * SAMPLES_PER_FRAME
        stop = begin + len(voice)
        assert a <= begin < stop <= b and (not evidence or evidence[-1]['endSample'] < begin)
        edge = round(.018 * RATE)
        fade = np.linspace(0, 1, edge, dtype=np.float32)
        voice[:edge] *= fade
        voice[-edge:] *= fade[::-1]
        rms = float(np.sqrt(np.mean(voice ** 2)))
        gain = min(.116 / rms, .83 / float(np.max(np.abs(voice))))
        tail = round(.09 * RATE)
        duck = np.ones(len(voice), dtype='float32') * .49
        duck[:tail] = np.linspace(1, .49, tail)
        duck[-tail:] = np.linspace(.49, 1, tail)
        bed = data[begin:stop] * duck[:, None]
        headroom = .985 - float(np.max(np.abs(bed)))
        if headroom > 0:
            gain = min(gain, headroom / float(np.max(np.abs(voice))))
        data[begin:stop] = bed + voice[:, None] * gain
        assert float(np.max(np.abs(data[begin:stop]))) < .99
        evidence.append(dict(row, startSample=begin, endSample=stop, voice=str(path), sha256=proof['sha256'],
                             sourceSamples=list(source_samples), sourceRate=source_rate, voiceGain=gain,
                             readback=proof['recognized'], semanticMatch=proof['semanticMatch']))
    cursor = 0
    for row in evidence:
        assert np.array_equal(data[cursor:row['startSample']], before[cursor:row['startSample']])
        cursor = row['endSample']
    assert np.array_equal(data[cursor:], before[cursor:])
    output = folder / 'narration-mix.wav'
    sf.write(output, data, RATE, subtype='FLOAT')
    saved, _ = sf.read(output, dtype='float32', always_2d=True)
    assert np.array_equal(saved, data)
    save(folder / 'mix.json', {'baseline': baseline, 'originalSamplesOutsideCueRangesUnchanged': True,
                               'ranges': evidence, 'sha256': sha(output), 'sampleRate': RATE})
    return output, evidence


def srt_cues(file):
    pattern = re.compile(r'^\d+\s*\n(' + TIMECODE + r') --> (' + TIMECODE + r')\s*\n(.*?)(?=\n\n\d+\s*\n|\Z)', re.M | re.S)
    return [(seconds(a), seconds(b), text.strip()) for a, b, text in pattern.findall(read(file).strip())]


def write_captions(record, evidence, folder):
    output = {}
    styles = BATCH / 'local/final-audio' / record['id'] / 'captions'
    font = captions.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'), 500)
    prior_ass = styles / 'captions.provisional.ko.ass'
    signature = load(BATCH / 'local/final-encode' / record['id'] / 'signature.json')
    assert sha(prior_ass) == signature['assSha256']
    ass = read(prior_ass)
    additions = []
    for lang in ('ko', 'en'):
        path = next(f['path'] for f in record['files'] if f['kind'] == f'{lang}.srt')
        original = srt_cues(path)
        assert original
        new = []
        for row in evidence:
            start, end = row['startSample'] / RATE, row['endSample'] / RATE
            wrapped = captions.wrap(row[lang], font)
            assert wrapped, (record['id'], lang, row[lang])
            text = '\n'.join(wrapped)
            new.append((start, end, text))
            if lang == 'ko':
                additions.append(captions.ass_events({'start': start, 'end': end, 'ko': text,
                                                       'emphasis': {'ko': None}},
                                                      captions.geometry(text, font, None, None), 'ko'))
        for start, end, _ in new:
            assert not any(a < end and b > start for a, b, _ in original)
        combined = sorted(original + new)
        output[lang] = folder / f'{lang}.srt'
        output[lang].write_text(''.join(f'{i}\n{captions.srt_stamp(a)} --> {captions.srt_stamp(b)}\n{text}\n\n'
                                        for i, (a, b, text) in enumerate(combined, 1)), encoding='utf8')
    path = folder / 'captions.ko.ass'
    path.write_text(ass.rstrip() + '\n' + ''.join(additions), encoding='utf8')
    return path, output


def make_picture(record, clean, folder, log):
    ep = record['id']
    if ep not in VISUAL_REVISIONS:
        return Path(clean)
    manifest = load(MEDIA / ep / 'new-pictures/manifest.json')
    assert manifest['priorFrameCount'] == record['frames']
    segments = []
    cursor = 0

    def preserve(end):
        if cursor == end:
            return
        output = folder / f'keep-{cursor:06d}-{end:06d}.mp4'
        if not output.exists():
            invoke(['-ss', f'{cursor / FPS:.9f}', '-threads', 2, '-i', clean, '-map', '0:v:0',
                    '-frames:v', end - cursor, '-an', *SEGMENT_ENC, output], log)
        check_video(output, end - cursor, False)
        segments.append((output, end - cursor))

    for row in manifest['spans']:
        assert sha(row['file']) == row['sha256'] and cursor <= row['start'] < row['end']
        preserve(row['start'])
        segments.append((Path(row['file']), row['end'] - row['start']))
        cursor = row['end']
    preserve(record['frames'])
    assert sum(count for _, count in segments) == record['frames']
    playlist = folder / 'spans.ffconcat'
    playlist.write_text('ffconcat version 1.0\n' + ''.join(
        f"file '{path.as_posix()}'\nduration {count / FPS:.9f}\n" for path, count in segments), encoding='utf8')
    picture = folder / 'picture.mp4'
    invoke(['-f', 'concat', '-safe', 0, '-i', playlist, '-map', '0:v:0', '-c:v', 'copy',
            '-bsf:v', 'setts=pts=N*1000:dts=N*1000:duration=1000:time_base=1/60000',
            '-video_track_timescale', 60000, '-movflags', '+faststart', picture], log)
    check_video(picture, record['frames'], False)
    return picture


def finish(ep):
    previous = load(BATCH / 'review-manifest.json')
    record = next(row for row in previous['records'] if row['id'] == ep)
    plan = load(HERE / 'observation-plan.json')['episodes'][ep]
    for f in record['files']:
        assert sha(f['path']) == f['sha256'], (ep, 'previous delivery changed')
    folder = MEDIA / ep / 'finish'
    folder.mkdir(parents=True, exist_ok=True)
    log = folder / 'finish.log'
    out = OUTPUT / ep
    out.mkdir(parents=True, exist_ok=True)
    wav, evidence = mix(record, plan, folder)
    ass, subtitles = write_captions(record, evidence, folder)
    original_clean = next(f['path'] for f in record['files'] if f['kind'] == 'clean.mp4')
    picture = make_picture(record, original_clean, folder, log)
    audio = folder / 'audio.m4a'
    invoke(['-i', wav, '-c:a', 'aac', '-b:a', '192k', '-ar', RATE, '-ac', 2, audio], log)
    name = record['slug']
    clean = out / f'{name}.clean.mp4'
    captioned = out / f'{name}.captioned.mp4'
    invoke(['-i', picture, '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
            '-movflags', '+faststart', clean], log)
    ass_filter = ass.as_posix().replace(':', '\\:')
    invoke(['-threads', 4, '-filter_threads', 1, '-i', picture, '-i', audio, '-map', '0:v:0', '-map', '1:a:0',
            '-vf', f"ass='{ass_filter}'", '-frames:v', record['frames'], '-c:a', 'copy',
            *VENC, '-movflags', '+faststart', captioned], log)
    assert audio_payload(clean) == audio_payload(captioned) == audio_payload(audio)
    files = []
    for kind, file in [('captioned.mp4', captioned), ('clean.mp4', clean), *[(f'{k}.srt', p) for k, p in subtitles.items()]]:
        if kind.endswith('mp4'):
            check_video(file, record['frames'], True)
            invoke(['-threads', 4, '-i', file, '-f', 'null', '-'], log)
        else:
            target = out / f'{name}.{kind}'
            shutil.copyfile(file, target)
            file = target
        files.append({'kind': kind, 'path': str(file), 'bytes': file.stat().st_size, 'sha256': sha(file)})
    description = NOTES.get(ep, '') + ' 반복 관찰에 동작을 짚는 안내 음성을 추가했습니다.'
    proof = {k: record[k] for k in ('id', 'slug', 'title', 'durationSeconds', 'frames', 'gameExamples')}
    proof.update(revision='review-notes-20261110', files=files, description=description.strip(),
                 localFinalFilesReady=True, humanReviewed=False, humanListened=False, platformChanged=False,
                 baselineFiles=record['files'], cues=evidence, fullDecode=True, pictureEdited=ep in VISUAL_REVISIONS,
                 reviewPoints=[{'label': '관찰 안내', 'seconds': r['startSample'] / RATE} for r in evidence])
    if ep == 'A06':
        old = record['pictureMetrics']
        inserts = load(HERE / 'A06-game-beats.json')['inserts']
        frames_added = sum(q['end'] - q['start'] for q in inserts)
        proof['addedNativeGameplaySeconds'] = frames_added / FPS
        proof['nativeGameplaySharePct'] = round(old['gameMotionSharePct'] + 100 * frames_added / old['bodyFrames'], 3)
        proof['reviewPoints'] += [{'label': row['label'], 'seconds': row['start'] / FPS} for row in inserts]
    save(out / 'delivery.json', proof)
    print(ep, 'four verified local outputs', len(evidence), 'observation cues', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('episode')
    finish(parser.parse_args().episode)
