"""Preserve the failed end-boundary probe and recover only its missing final PTS."""
from pathlib import Path

batch = Path(__file__).resolve().parent
old = batch / 'inspect-motion-opening-native-v3.py'
new = batch / 'inspect-motion-opening-native-v4.py'
assert not new.exists()
text = old.read_text('utf-8')
text = text.replace('motion-opening-native-v3', 'motion-opening-native-v4')
text = text.replace('motion-opening-native-execution-v3', 'motion-opening-native-execution-v4')
text = text.replace('inspect-motion-opening-native-v3', 'inspect-motion-opening-native-v4')
text = text.replace("'schemaVersion': 3", "'schemaVersion': 4")
text = text.replace("f'{first / 60:.9f}%{end / 60:.9f}'", "f'{first / 60:.9f}%{end / 60 + 0.5:.9f}'")
old_probe = """        probe = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8')
        (folder / 'probe-command.json').write_text(json.dumps(probe_cmd), encoding='utf-8')
        (folder / 'native-frames.json').write_text(probe.stdout, encoding='utf-8')
        (folder / 'probe.stderr.log').write_text(probe.stderr, encoding='utf-8')
        assert probe.returncode == 0 and not probe.stderr.strip(), 'Native frame probe failed'
        observed = [f for f in json.loads(probe.stdout)['frames'] if first * 256 <= int(f['pts']) < end * 256]
"""
new_probe = """        reused_probe = root / 'shared/assets/presenting-game-scores/raw/motion-opening-native-v3/roundabout-tail/native-frames.json'
        reused_frames = []
        if window['id'] == 'roundabout-tail':
            reused_frames = json.loads(reused_probe.read_text('utf-8'))['frames']
            assert len([f for f in reused_frames if first * 256 <= int(f['pts']) < end * 256]) == 412
            probe_cmd[probe_cmd.index('-read_intervals') + 1] = f'{(end - 2) / 60:.9f}%{end / 60 + 0.5:.9f}'
        probe = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8')
        (folder / 'probe-command.json').write_text(json.dumps(probe_cmd), encoding='utf-8')
        (folder / 'supplemental-native-frames.json').write_text(probe.stdout, encoding='utf-8')
        (folder / 'probe.stderr.log').write_text(probe.stderr, encoding='utf-8')
        assert probe.returncode == 0 and not probe.stderr.strip(), 'Native frame probe failed'
        combined = {int(f['pts']): f for f in reused_frames + json.loads(probe.stdout)['frames']}
        observed = [combined[pts] for pts in sorted(combined) if first * 256 <= pts < end * 256]
        (folder / 'native-frames.json').write_text(json.dumps({'frames': observed, 'reusedV3Frames': len(reused_frames),
            'reusedProbe': str(reused_probe.relative_to(root)) if reused_frames else None}), encoding='utf-8')
"""
assert old_probe in text
text = text.replace(old_probe, new_probe)
text = text.replace("'allFinalPixelsApproved': False, 'researchManipulations': 0,", "'allFinalPixelsApproved': False, 'researchManipulations': 0,\n         'recoveryReason': 'ffprobe stopped before one delayed final frame at the exclusive end; pad decoder read range and reuse 412 already verified selected PTS. No VFR inference.',\n         'failedHistory': 'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v3.json',")
new.write_text(text, encoding='utf-8')
print('Prepared v4; v3 probe and failed execution preserved, 412 selected native PTS reused.')
