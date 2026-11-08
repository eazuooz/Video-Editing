"""Correct an unsupported DLC title in nine A16 editorial headers only."""
from pathlib import Path
import copy, json, os, subprocess
import caption_safe_stage_footer as p


def main():
    ctrl = p.read(p.R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert 'A16' in ctrl['episodes'] and ctrl['renderAuthorized']
    manifestfile = p.H.parent / 'game-plates-caption-safe.json'
    before = p.H / 'caption-safe/game-plates-own-only.json'
    if not before.exists(): before.write_bytes(manifestfile.read_bytes())
    manifest = p.read(before); jobs = []
    font = 'C\\:/Windows/Fonts/malgunbd.ttf'
    vf = f"drawbox=x=0:y=0:w=1400:h=80:color=0x080d0a:t=fill,drawtext=fontfile='{font}':text='Elden Ring':x=52:y=17:fontsize=42:fontcolor=0xf2d787"
    for ep in manifest['episodes']:
        for row in ep['pictureEdits']:
            if not any(s.get('sourceKey') == 'elden-jump' for s in row.get('mediaSegments', [])): continue
            assert ep['id'] == 'A16' and row['sourceClassification'] in ('game', 'analysis')
            src = p.R / row['picture']; assert p.sha(src) == row['pictureSha256']
            dest = p.DEST / 'canonical-header/A16' / (row['id'] + '.mp4'); dest.parent.mkdir(parents=True, exist_ok=True)
            signature = {'sourceSha256': row['pictureSha256'], 'filter': vf, 'frames': row['newFrames'], 'encoder': p.ENC}
            receiptfile = dest.with_suffix('.json'); old = p.read(receiptfile) if receiptfile.exists() else {}
            if not (dest.exists() and old.get('canonicalHeaderSignature') == signature and old.get('sha256') == p.sha(dest)):
                temp = dest.with_suffix('.pending.mp4')
                with dest.with_suffix('.log').open('wb') as log:
                    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '4', '-i', str(src),
                        '-filter_threads', '1', '-vf', vf, '-frames:v', str(row['newFrames']), '-an', *p.ENC, str(temp)],
                        stdout=log, stderr=log, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                streams = p.probe(temp); assert len(streams) == 1
                s = streams[0]; assert (s['width'], s['height'], s['avg_frame_rate'], int(s['nb_frames'])) == (1920, 1080, '60/1', row['newFrames'])
                os.replace(temp, dest)
                old = copy.deepcopy(p.read(p.R / row['receipt']))
                old.update(picture=str(dest), sha256=p.sha(dest), canonicalHeaderSignature=signature,
                    canonicalGameLabelPatch={'oldLabel': 'Elden Ring: Shadow of the Erdtree', 'newLabel': 'Elden Ring',
                        'reason': 'Recorder metadata supports Elden Ring jump-build gameplay, not an identified DLC edition.',
                        'sourceKey': 'elden-jump', 'sourceVideoId': '8kNea5T5YS4',
                        'originalPlate': row['picture'], 'originalPlateSha256': row['pictureSha256'],
                        'rectangleXYWH': [0, 0, 1400, 80], 'actualGamePixelsBelowY80Untouched': True,
                        'narrationAndAudioChanged': False, 'timingChanged': False})
                p.save(receiptfile, old)
            row.update(picture=str(dest), pictureSha256=old['sha256'], receipt=str(receiptfile),
                       canonicalGameLabelPatch=old['canonicalGameLabelPatch'])
            jobs.append({'id': row['id'], 'frames': row['newFrames'], 'output': str(dest), 'sha256': old['sha256'],
                         'receipt': str(receiptfile), 'source': str(src), 'sourceSha256': signature['sourceSha256']})
            print(row['id'], 'Elden Ring header only', flush=True)
    assert len(jobs) == 9
    manifest['canonicalGameHeaderRevision'] = {'sourceKey': 'elden-jump', 'episode': 'A16', 'changedPlateHeaders': 9,
        'sourceVideoPixelsChanged': False, 'audioOrTimingChanged': False, 'newLabel': 'Elden Ring',
        'receipt': p.rel(p.H / 'caption-safe/elden-header.json')}
    p.save(p.H / 'caption-safe/elden-header.json', {'status': 'nine-canonical-game-headers-ready', 'jobs': jobs,
        'renderScriptSha256': p.sha(__file__), 'gameplayAndAnalysisFrameCountsUnchanged': True, 'humanReview': False})
    p.save(manifestfile, manifest)
    print(json.dumps({'sha256': p.sha(manifestfile), 'headers': 9}), flush=True)


if __name__ == '__main__': main()
