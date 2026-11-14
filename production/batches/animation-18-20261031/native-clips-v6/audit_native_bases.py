"""Verify retained comparisons really use installed animations, not hand-made poses."""
import argparse
import sys
from pathlib import Path

import numpy as np

from prepare import BATCH, HERE, ROOT, WORK, read, save
from finish_episode import sha

sys.path.insert(0, str(BATCH / 'real-clips-v2'))
from motion import Motion, L


def check_rotation(study, side, frame, motion, source_time):
    pose = motion.sample(source_time)
    errors = []
    for index, name in enumerate(motion.names):
        q = np.asarray(study['animations'][side]['tracks'][name]['q'][frame])
        errors.append(1 - abs(float(np.dot(q, pose['q'][index]))))
    assert max(errors) < 2e-6, (study['study'], side, frame, max(errors))
    return max(errors)


def audit(ep):
    catalog = {r['id']: r for r in read(BATCH / 'real-clips-v2/source-motion-catalog.json')}
    results = []
    if ep == 'A09':
        m = Motion('AS_ComboHands')
        d = read(L / 'studies/A09-fist.json')
        for f in range(180):
            t = float(np.interp(f, [0, 12, 54, 80, 130, 179], [0, 0, .45, .77, 1.2, 1.2]))
            for side in (0, 1):
                check_rotation(d, side, f, m, t)
        results.append({'clip': m.data['sourceClip'], 'framesChecked': 360,
                        'retainedChange': 'Only hand scale demonstrates the narrated squash/stretch principle; all joint rotations remain original.'})
    elif ep == 'A16':
        m = Motion('AS_Spear_Attack_04')
        for key in ('range', 'path', 'overhead', 'active'):
            d = read(L / ('studies/A16-' + key + '.json'))
            for f in range(180):
                t = float(np.interp(f, [0, 17, 32, 60, 110, 179], [1.1, 1.55, 1.9, 3.4, 5.1, 5.1]))
                for side in (0, 1):
                    check_rotation(d, side, f, m, t)
            results.append({'clip': m.data['sourceClip'], 'study': key, 'framesChecked': 360,
                            'retainedChange': 'Original weapon animation; only camera, collision radius and active interval differ.'})
    elif ep == 'A03':
        m = Motion('AS_Spear_Attack_02')
        for key in ('attack', 'cancel36', 'cancel48', 'noinput'):
            d = read(L / ('studies/A03-' + key + '.json'))
            errors = []
            for f, trace in enumerate(d['trace']):
                if trace['transitionAccepted']:
                    continue
                t = float(np.interp(min(48, max(0, trace['simulationFrame'])), [0, 5, 12, 18, 48], [1.62, 2.2, 3.25, 3.65, 6.45]))
                p = m.sample(t)
                for i, name in enumerate(m.names):
                    q = np.asarray(d['tracks'][name]['q'][f])
                    errors.append(1 - abs(float(np.dot(q, p['q'][i]))))
            assert max(errors) < 2e-6
            results.append({'clip': m.data['sourceClip'], 'study': key,
                            'retainedChange': 'Native overhead strike, retimed attack clock and genuine run clip on input; no sculpted joint poses.'})
    elif ep == 'A13':
        for key in ('mirror', 'tool', 'direction'):
            d = read(L / ('studies/A13-' + key + '.json'))
            m = Motion(str(d['sourceClip']).split('/')[-1])
            for f in range(180):
                t = float(np.clip((f - 12) / 60, 0, .65)) if key == 'direction' else min(m.seconds, f / 60)
                check_rotation(d, 0, f, m, t)
            results.append({'clip': m.data['sourceClip'], 'study': key, 'framesChecked': 180,
                            'retainedChange': 'Native performance; opposite view uses bind-relative mathematical reflection or camera change, not hand-posed movement.'})
    else:
        raise ValueError('Only the explicitly audited native studies may be retained here.')
    for result in results:
        key = result['clip'].split('/')[-1]
        source = ROOT / 'GameAnimationSample/Content' / (result['clip'].removeprefix('/Game/') + '.uasset')
        assert source.exists()
        result.update(originalAsset=str(source), originalAssetSha256=sha(source))
        assert result['originalAssetSha256'] == catalog[key]['sourceAssetSha256']
    plan = next(r for r in read(HERE / 'plan.json')['episodes'] if r['id'] == ep)
    pictures = {r['kind']: {'path': str(ROOT / r['path']), 'sha256': r['sha256']}
                for r in plan['baseline']['files'] if r['kind'] in ('clean.mp4', 'captioned.mp4')}
    for row in pictures.values():
        assert sha(Path(row['path'])) == row['sha256']
    save(WORK / ep / 'native-source-audit.json', {'episode': ep, 'sourceMotionVerified': True,
        'studies': results, 'pictures': pictures,
        'reviewBoundary': 'Source provenance and exact pose validation; encoded moving-picture sampling remains required.'})
    print(ep, 'native source poses verified', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('episodes', nargs='+')
    for episode in parser.parse_args().episodes:
        audit(episode)
