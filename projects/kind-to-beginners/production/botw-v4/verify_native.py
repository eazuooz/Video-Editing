"""Verify only completed D29 BOTW native clips and their captured scene receipts."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
from native_scene_evidence import verify as verify_scene
from audio_pipeline import tool

H = Path(__file__).resolve().parent
R = H.parents[3]
M = R / 'projects/kind-to-beginners/production/local/botw-v4'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    root = (M / 'render' / args.revision).resolve()
    assert root.parent == (M / 'render').resolve()
    jobs = read(H / 'capture-jobs.json')
    assert jobs['timingLocked'] is True
    expected = read(H / 'botw-code-fingerprint.json')['fingerprints']['D29BotwStage']
    rows = []
    for job in jobs['jobs']:
        d = root / job['cutId']
        scene = verify_scene(d / 'request.json', d / 'render-success.json')
        assert scene['compiledFingerprint'] == expected
        movie = d / 'unity.mp4'
        probe = json.loads(subprocess.check_output([
            tool('ffprobe'), '-v', 'error',
            '-show_streams', '-of', 'json', str(movie)], text=True))
        assert len(probe['streams']) == 1
        video = probe['streams'][0]
        assert video['codec_type'] == 'video'
        assert (video['width'], video['height']) == (1920, 1080)
        assert video['r_frame_rate'] == video['avg_frame_rate'] == '60/1'
        assert int(video['nb_frames']) == job['frames']
        assert abs(float(video['duration']) - job['frames'] / 60) < .001
        rows.append({'cutId': job['cutId'], 'frames': job['frames'],
                     'movie': movie.relative_to(R).as_posix(), 'movieSha256': sha(movie),
                     'width': 1920, 'height': 1080, 'fps': '60/1',
                     'containerFrames': int(video['nb_frames']),
                     'sceneEvidence': (d / 'scene-evidence.json').relative_to(R).as_posix(),
                     'scene': scene['scene'], 'sceneSha256': scene['sceneSha256'],
                     'sceneMetaSha256': scene['sceneMetaSha256'],
                     'receiptSha256': scene['successSha256']})
        print('VERIFIED ' + job['cutId'], flush=True)
    out = H / ('native-render-receipt-' + args.revision + '.json')
    assert not out.exists(), 'Preserve existing verification; do not overwrite.'
    result = {'status': 'passed-native-structural-and-saved-scene-verification',
              'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'revision': 'botw-v4', 'renderRevision': args.revision,
              'compiledFingerprint': expected, 'count': len(rows),
              'totalFrames': sum(x['frames'] for x in rows),
              'jobsSha256': sha(H / 'capture-jobs.json'),
              'cuesSha256': sha(H / 'unity-cues.json'),
              'clips': rows,
              'notYetVerified': 'Full final-master decoding, final compositor captions, full narration synchronization and whole-video human review.'}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(out, flush=True)

if __name__ == '__main__':
    main()
