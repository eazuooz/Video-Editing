"""A02 measured-profile sparse native capture and actual-cue still QA.

No full render, TTS, publishing, timing changes or final listening claims.
"""
from pathlib import Path
import json
import math
import hashlib
import argparse
from PIL import Image
import capture_grid as capture
import qa_native_contacts as qa

H = Path(__file__).resolve().parent
R = H.parents[3]
M = H.parent / 'local/grid-v1'
BOOK = H / 'measured-native-profiles.json'
PLAN = H / 'measured-edit-plan.proposal.json'
CAPTIONS = M / 'edit/captions.json'
SELECTED = ('A02-E002B', 'A02-E003', 'A02-E011', 'A02-E014', 'A02-E015',
            'A02-E019', 'A02-E022', 'A02-E024')


def samples(profile):
    count = round(profile['duration'] * 60)
    values = {0, count - 1}
    for cue in profile['phases']:
        start, end = (round(cue[key] * 60) for key in ('start', 'end'))
        onset = round((cue['start'] + cue['motionStart']) * 60)
        values.update((start-1, start, start+1, end-1, end,
                       onset-1, onset, onset+1, (start+end)//2))
        if profile['mode'] in ('normal-and-pause', 'size-amplitude', 'paused-pose-context'):
            values.update(onset + offset for offset in (7, 8, 9, 21, 22, 23))
            if profile['mode'] == 'paused-pose-context' and cue['phase'] == 2:
                values.update(onset + offset for offset in (13, 14, 15))
        if cue['motionDuration'] > 0:
            length = cue['motionDuration'] * 60
            for progress in (.25, .5, .72, 1):
                mark = onset + round(length * progress)
                values.update((mark-1, mark, mark+1))
    if len([value for value in values if 0 <= value < count]) < 12:
        values.update(round((count-1) * index/11) for index in range(12))
    return sorted(value for value in values if 0 <= value < count)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',default='v1',choices=('v1','v2','v3'))
    args = parser.parse_args()
    capture.authorize()
    assert BOOK.read_bytes() == capture.PROFILE.read_bytes(), 'Exact measured book must be copied and compiled first'
    book, plan, captions = (capture.read(path) for path in (BOOK, PLAN, CAPTIONS))
    profiles = {value['id']: value for value in book['presentations']}
    cuts = {value['id']: value for value in plan['cuts']}
    fingerprint = capture.read(H / 'source-fingerprint.json')['fingerprint']
    output = M / ('qa/measured-native-20261104-'+args.revision)
    assert not output.exists(), 'Preserve prior measured QA'
    font = qa.font_at(48)
    records, inputs = [], []
    for identifier in SELECTED:
        profile, cut = profiles[identifier], cuts[identifier]
        assert round(profile['duration']*60) == cut['frames']
        assert hashlib.sha256(CAPTIONS.read_bytes()).hexdigest() == profile['captionSchedule']['sha256']
        chosen = samples(profile)
        revision = 'measured-' + identifier + '-20261104-' + args.revision
        capture.request_capture('preflight', profile['mode'], revision, identifier,
                                cut['frames'], chosen, fingerprint)
        directory = M / 'preflight' / revision / profile['mode']
        reopen = capture.read(directory / 'scene-reopen-evidence.json')
        assert reopen['sourceFingerprint'] == fingerprint and reopen['maxBonePositionError'] <= .001
        inputs.append({'id': identifier, 'mode': profile['mode'], 'directory': str(directory),
                       'sampleFrames': chosen, 'reopenEvidence': reopen})
        for frame in chosen:
            global_time = (cut['startFrame'] + frame)/60
            active = [cue for cue in captions['cues'] if cue['start'] <= global_time < cue['end']]
            assert len(active) <= 1
            cue = active[0] if active else None
            image_path = directory / f'frame-{frame:05d}.png'
            diagnostic = capture.read(directory / f'a02-{frame:05d}.json')
            assert diagnostic['profileId'] == identifier and diagnostic['sourceFingerprint'] == fingerprint
            target = output / identifier
            (target/'caption-layout-fhd').mkdir(parents=True, exist_ok=True)
            (target/'mobile-375').mkdir(parents=True, exist_ok=True)
            fhd = target/'caption-layout-fhd'/image_path.name
            mobile = target/'mobile-375'/image_path.name
            with Image.open(image_path) as source:
                assert source.size == (1920, 1080)
                geometry = qa.caption_geometry(cue['ko'], font) if cue else None
                image = qa.captioned_frame(source, geometry, font) if cue else source.convert('RGB')
                image.save(fhd)
                image.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
            records.append({'id':identifier,'mode':profile['mode'],'frame':frame,
                            'globalSeconds':global_time,'sourceImage':qa.artifact(image_path),
                            'diagnostic':diagnostic,'captionCue':cue['cue'] if cue else None,
                            'captionText':cue['ko'] if cue else '', 'captionTextEnglish':cue['en'] if cue else '',
                            'captionGeometry':geometry,'captionLayoutFhd':qa.artifact(fhd),
                            'mobile375':qa.artifact(mobile)})
    qa.QA_LABEL = 'Measured native frames + actual current caption cue'
    sheets = []
    for identifier in SELECTED:
        selected = [record for record in records if record['id'] == identifier]
        for first in range(0,len(selected),12):
            sheets.append(qa.contact_page(selected[first:first+12],output,
                                          f'{identifier}-contact-{first//12+1:02d}.png'))
    result = {'episode':'A02','kind':'measured-native-sparse-frame-layout-QA',
              'book':qa.artifact(BOOK),'editPlan':qa.artifact(PLAN),'captionSchedule':qa.artifact(CAPTIONS),
              'helper':qa.artifact(Path(__file__)),'sourceFingerprint':fingerprint,
              'inputs':inputs,'frames':records,'contacts':sheets,'humanReview':False,
              'actualAudioListeningPerformed':False,'movingPlaybackReviewed':False,
              'captionRasterizer':'Pillow fixed geometry preview with current exact timed clause; final libass pixels/emphasis unverified',
              'limitations':'Sparse stills verify phase/key poses/layout only; final moving captions, source joins and audio remain for final QA.'}
    capture.write(output/'qa-manifest.json',result)
    page=['<!doctype html><meta charset="utf-8"><title>A02 measured native QA</title>',
          '<style>body{background:#101214;color:white;font-family:sans-serif}img{max-width:100%}a{color:#86cfa3}</style>',
          '<h1>A02 measured native frames + current timed Korean captions</h1>',
          '<p>Sparse still layout QA only. No final playback/listening claim.</p>']
    page += [f'<p><a href="{Path(sheet["path"]).name}"><img src="{Path(sheet["path"]).name}"></a></p>' for sheet in sheets]
    (output/'index.html').write_text('\n'.join(page),encoding='utf-8')
    capture.write(H/'measured-native-preflight-review-20261104.json',
                  {'episode':'A02','sourceFingerprint':fingerprint,'manifest':qa.artifact(output/'qa-manifest.json'),
                   'sampledFrames':len(records),'profileCount':len(inputs),'readyForRootVisualReview':True,
                   'humanReview':False,'fullRenderStarted':False})
    print(json.dumps({'output':str(output),'frames':len(records),'profiles':len(inputs)},ensure_ascii=False))


if __name__ == '__main__':
    main()
