"""Assemble the reviewed native picture and summary, preserving the prior body clock."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from prepare import HERE, ROOT, WORK, OUTPUT, read, save
from finish_episode import ff, sha, timestamp, VENC
from insert_recap_picture import insert as insert_recap


def seconds(text):
    h, m, s = text.replace(',', '.').split(':')
    return 3600 * int(h) + 60 * int(m) + float(s)


def srt(path):
    pattern = r'^\d+\s*\n(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)\s*\n(.*?)(?=\n\n\d+\s*\n|\Z)'
    return [(seconds(a), seconds(b), text.strip())
            for a, b, text in re.findall(pattern, path.read_text(encoding='utf-8-sig').strip(), re.M | re.S)]


def assemble(ep):
    import numpy as np
    import soundfile as sf
    selected = next(row for row in read(HERE / 'plan.json')['episodes'] if row['id'] == ep)
    base = selected['baseline']
    assert ep in read(ROOT / 'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']['episodes']
    folder = WORK / ep / 'assembly'
    summary = read(folder / 'summary-components.json')
    assert summary['frames'] == 600
    captions = WORK / ep / 'summary-captions'
    assert (captions / 'caption-alignment.json').is_file()
    prior = {f['kind']: ROOT / f['path'] for f in base['files']}
    pictures = dict(prior)
    reviewed = None
    if ep != 'A06':
        reviewed = read(WORK / ep / 'native-picture-review.json')
        assert reviewed['visualReviewPassed']
        for kind in ('clean.mp4', 'captioned.mp4'):
            pictures[kind] = Path(reviewed['pictures'][kind]['path'])
            assert sha(pictures[kind]) == reviewed['pictures'][kind]['sha256']
    insert = (base['frames'] - 600) / 60
    pcm = Path(reviewed['audioPcm']) if reviewed and reviewed.get('audioPcm') else Path('C:/Users/1/Videos/YamyamProduction/animation-review-notes-20261110') / ep / 'finish/narration-mix.wav'
    if not pcm.is_file():
        pcm = folder / 'previous-decoded.wav'
        ff('-i', prior['clean.mp4'], '-vn', '-ar', 48000, '-ac', 2, '-c:a', 'pcm_f32le', pcm)
    voice, rate = sf.read(pcm, dtype='float32', always_2d=True)
    assert rate == 48000 and voice.shape[1] == 2
    target_samples = round(base['frames'] / 60 * rate)
    assert abs(len(voice) - target_samples) < 1600
    voice = voice[:target_samples]
    if len(voice) < target_samples:
        voice = np.pad(voice, ((0, target_samples - len(voice)), (0, 0)))
    recap_pcm = folder / 'summary-decoded.wav'
    ff('-i', summary['audio'], '-ar', 48000, '-ac', 2, '-c:a', 'pcm_f32le', recap_pcm)
    recap, recap_rate = sf.read(recap_pcm, dtype='float32', always_2d=True)
    assert recap_rate == rate and len(recap) == 480000
    at = round(insert * rate)
    joined = np.concatenate([voice[:at], recap, voice[at:]])
    assert np.array_equal(joined[:at], voice[:at])
    assert np.array_equal(joined[at + 480000:], voice[at:])
    mix = folder / 'final-mix.wav'
    sf.write(mix, joined, rate, subtype='FLOAT')
    audio = folder / 'final-audio.m4a'
    ff('-i', mix, '-c:a', 'aac', '-b:a', '192k', audio)
    summary_captioned = folder / 'summary-captioned.mp4'
    ass = str(captions / 'captions.ko.ass').replace('\\', '/').replace(':', '\\:')
    ff('-i', summary['cleanPicture'], '-vf', "setpts=PTS+2/TB,ass='" + ass + "',setpts=PTS-2/TB",
       '-frames:v', 600, '-an', *VENC, summary_captioned)
    out = OUTPUT / ep
    out.mkdir(parents=True, exist_ok=True)
    outputs = []
    for kind, recap_picture in [('clean.mp4', Path(summary['cleanPicture'])), ('captioned.mp4', summary_captioned)]:
        picture, splice = insert_recap(pictures[kind],recap_picture,base['frames'],folder,kind)
        final = out / (base['slug'] + '.' + kind)
        ff('-i', picture, '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', final)
        ff('-i', final, '-f', 'null', 'NUL')
        info = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(final)]))['streams'][0]
        assert (info['width'], info['height'], info['avg_frame_rate'], int(info['nb_frames'])) == (1920, 1080, '60/1', base['frames'] + 600)
        outputs.append({'kind': kind, 'path': str(final), 'sha256': sha(final), 'fullDecode': 'passed', 'pictureSplice':splice})
    for language in ('ko', 'en'):
        caption_source = Path(reviewed['captions'][language]) if reviewed and reviewed.get('captions') else prior[language+'.srt']
        cues = srt(caption_source)
        assert not any(a < insert < b for a, b, _ in cues)
        cues = [(a + (10 if a >= insert else 0), b + (10 if a >= insert else 0), t) for a, b, t in cues]
        cues += [(a - 2 + insert, b - 2 + insert, t) for a, b, t in srt(captions / ('captions.' + language + '.srt'))]
        cues.sort()
        final = out / (base['slug'] + '.' + language + '.srt')
        final.write_text(''.join(f'{i}\n{timestamp(a)} --> {timestamp(b)}\n{t}\n\n'
                                 for i, (a, b, t) in enumerate(cues, 1)), encoding='utf-8')
        outputs.append({'kind': language + '.srt', 'path': str(final), 'sha256': sha(final)})
    save(out / 'delivery.json', {'id': ep, 'title': base['title'], 'frames': base['frames'] + 600,
         'revisionDescription': ('기존 시연을 보존하고, 마지막에 핵심을 짚는 10초 정리를 추가했습니다.' if ep=='A06' else
             '준비된 애니메이션과 실제 게임 동작을 바탕으로 비교하고, 마지막에 핵심을 짚는 10초 정리를 추가했습니다.'),
         'durationSeconds': (base['frames'] + 600) / 60, 'files': outputs,
         'summaryAt': insert, 'summaryFrames': 600, 'sourcePcm': str(pcm),
         'sourcePcmSha256': sha(pcm),
         'bodyPictures': {kind:{'path':str(pictures[kind]),'sha256':sha(pictures[kind])} for kind in ('clean.mp4','captioned.mp4')},
         'bodyReviewSignature': reviewed.get('configurationSignature') if reviewed else None,
         'summaryPictureSha256': sha(Path(summary['cleanPicture'])), 'summaryAudioSha256': sha(Path(summary['audio'])),
         'sourcePcmOutsideSummaryUnchanged': True, 'humanReviewed': False,
         'visualReviewPending': True, 'platformChanged': False})
    print(ep, 'four outputs ready for final visual review', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('episode')
    assemble(parser.parse_args().episode)
