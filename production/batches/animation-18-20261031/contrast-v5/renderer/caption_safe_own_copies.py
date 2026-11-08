"""Propagate the caption-safe source revision into retimed own-scene copies.

Only explanation sources are copied, with the original exact timing recipe.
Commercial gameplay and its source provenance remain entirely unchanged.
"""
from pathlib import Path
import copy, json, os, subprocess
import caption_safe_stage_footer as patch

H, R = patch.H, patch.R
B = H.parent
BASE = H / 'caption-safe/game-plates-before.json'
NEW = B / 'game-plates-caption-safe.json'


def main():
    ctrl = patch.read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert ctrl['renderAuthorized'] and ctrl['fullLocalProductionAuthorized']
    source_manifest = B / 'game-plates-manifest.json'
    if BASE.exists():
        assert BASE.read_bytes() == source_manifest.read_bytes(), 'Original game manifest changed; recheck parent inputs'
    else:
        BASE.parent.mkdir(exist_ok=True); BASE.write_bytes(source_manifest.read_bytes())
    originals = patch.read(BASE); result = copy.deepcopy(originals)
    plan = patch.read(H / 'caption-safe/plan.json')
    assert plan['status'] == 'all-caption-safe-plates-ready'
    bysource = {os.path.normcase(str((R / j['source']).absolute())): j for j in plan['jobs']}
    jobs = []
    for episode in result['episodes']:
        assert episode['id'] in ctrl['episodes'] and episode['id'] != 'A03'
        for row in episode['pictureEdits']:
            if row.get('sourceClassification') != 'own': continue
            oldreceipt = patch.read(R / row['receipt']); details = oldreceipt['details']
            oldsource = details.get('sourcePlate')
            job = bysource.get(os.path.normcase(str((R / oldsource).absolute()))) if oldsource else None
            if not job: continue
            assert details['sourcePlateSha256'] == job['sourceSha256']
            source = R / job['output']; assert patch.sha(source) == job['sha256']
            assert patch.sha(R / row['picture']) == row['pictureSha256'] == oldreceipt['sha256']
            frames = row['newFrames']; sourceframes = details['sourcePlateFrames']
            assert sourceframes == job['frames']
            ratio = frames / sourceframes
            assert abs(ratio - details['authoredAnalysisDurationRatio']) < 1e-12
            output = patch.DEST / 'own-copies' / episode['id'] / (row['id'] + '.mp4')
            output.parent.mkdir(parents=True, exist_ok=True)
            vf = f'setpts={ratio:.12f}*(PTS-STARTPTS),fps=60,tpad=stop_mode=clone:stop_duration=1'
            signature = {'sourceSha256': job['sha256'], 'frames': frames, 'filter': vf, 'encoder': patch.ENC}
            receiptfile = output.with_suffix('.json')
            old = patch.read(receiptfile) if receiptfile.exists() else {}
            if not (output.exists() and old.get('captionSafeSignature') == signature and old.get('sha256') == patch.sha(output)):
                temporary = output.with_suffix('.pending.mp4')
                with output.with_suffix('.log').open('wb') as log:
                    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '4', '-i', str(source),
                        '-vf', vf, '-frames:v', str(frames), '-an', '-filter_threads', '1', *patch.ENC, str(temporary)],
                        stdout=log, stderr=log, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                streams = patch.probe(temporary); assert len(streams) == 1
                s = streams[0]
                assert (s['width'], s['height'], s['avg_frame_rate'], int(s['nb_frames'])) == (1920, 1080, '60/1', frames)
                os.replace(temporary, output)
                old = copy.deepcopy(oldreceipt)
                old.update(picture=str(output), sha256=patch.sha(output), captionSafeSignature=signature,
                    captionSafePatch={'sourcePlate': str(source), 'sourcePlateSha256': job['sha256'],
                        'originalPlate': oldsource, 'originalPlateSha256': job['sourceSha256'],
                        'originalOwnCopy': row['picture'], 'originalOwnCopySha256': row['pictureSha256'],
                        'sourceStageFrameRanges': job['stageFrameRanges'], 'sourceClearRectangleXYWH': job['clearRectangleXYWH'],
                        'timingRecipePreserved': True, 'losslessIntermediate': True,
                        'mediaSegmentsMeaning': 'Original motion ancestry/time retained exactly; new picture path/hash records the caption-only intermediate revision.'})
                patch.save(receiptfile, old)
            # The top-level receipt describes the new picture and its actual
            # input; immutable original-motion ancestry remains in the explicit
            # patch record and unchanged mediaSegments.
            desired_details = {**old['details'], 'sourcePlate': str(source), 'sourcePlateSha256': job['sha256']}
            if old['details'] != desired_details:
                old['details'] = desired_details
                patch.save(receiptfile, old)
            provenance = old['captionSafePatch']
            row.update(picture=str(output), pictureSha256=old['sha256'], receipt=str(receiptfile), captionSafePatch=provenance)
            jobs.append({'episode': episode['id'], 'id': row['id'], 'frames': frames, 'sourceFrames': sourceframes,
                'ratio': ratio, 'output': str(output), 'sha256': old['sha256'], 'receipt': str(receiptfile),
                'captionSafeSourceRow': job['id'], 'sourceStageFrameRanges': job['stageFrameRanges']})
            print(f'{len(jobs)} own copy: {episode["id"]} {row["id"]} {frames} frames', flush=True)
    for before, after in zip(originals['episodes'], result['episodes']):
        assert len(before['pictureEdits']) == len(after['pictureEdits'])
        for a, b in zip(before['pictureEdits'], after['pictureEdits']):
            if a['picture'] == b['picture']: assert a == b
            else:
                assert a['sourceClassification'] == b['sourceClassification'] == 'own'
                for k in ('id', 'startFrame', 'endFrame', 'newFrames', 'mediaSegments', 'sourceStartFrame', 'nativeFrames', 'analysisFrames'):
                    assert a[k] == b[k]
    result['captionSafeRevision'] = {'baselineManifestSha256': patch.sha(BASE),
        'changedOwnRows': len(jobs), 'changedCommercialGameRows': 0, 'timingAndAudioChanged': False,
        'originalGameManifestPreserved': True, 'originalAllMediaPreserved': True,
        'patchManifest': patch.rel(H / 'caption-safe/own-copies.json')}
    patch.save(H / 'caption-safe/own-copies.json', {'status': 'all-caption-safe-own-copies-ready', 'jobs': jobs,
        'sourceGameManifestSha256': patch.sha(BASE), 'newGameManifest': patch.rel(NEW),
        'renderScriptSha256': patch.sha(__file__), 'commercialFootageChanged': False, 'humanReview': False})
    patch.save(NEW, result)
    print(json.dumps({'changedOwnRows': len(jobs), 'frames': sum(j['frames'] for j in jobs),
        'manifest': patch.rel(NEW), 'sha256': patch.sha(NEW)}), flush=True)


if __name__ == '__main__': main()
