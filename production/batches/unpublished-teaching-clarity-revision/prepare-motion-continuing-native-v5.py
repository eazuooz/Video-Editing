"""Prepare a separate inspection for fresh continuous dirt removal; reuse no completed extraction."""
from pathlib import Path

batch = Path(__file__).resolve().parent
old = batch / 'inspect-motion-opening-native-v4.py'
new = batch / 'inspect-motion-opening-native-v5.py'
assert not new.exists()
text = old.read_text('utf-8')
text = text.replace('motion-opening-native-v4', 'motion-opening-native-v5')
text = text.replace('motion-opening-native-execution-v4', 'motion-opening-native-execution-v5')
text = text.replace('inspect-motion-opening-native-v4', 'inspect-motion-opening-native-v5')
text = text.replace("'schemaVersion': 4", "'schemaVersion': 5")
old_windows = """windows = [{'id': 'roundabout-tail', 'firstFrame': 13447, 'endExclusiveFrame': 13860},
           {'id': 'tower-unused', 'firstFrame': 16614, 'endExclusiveFrame': 17340}]"""
assert old_windows in text
text = text.replace(old_windows, "windows = [{'id': 'continuing-cleaning', 'firstFrame': 33144, 'endExclusiveFrame': 34800}]")
old_reuse = """        reused_probe = root / 'shared/assets/presenting-game-scores/raw/motion-opening-native-v3/roundabout-tail/native-frames.json'
        reused_frames = []
        if window['id'] == 'roundabout-tail':
            reused_frames = json.loads(reused_probe.read_text('utf-8'))['frames']
            assert len([f for f in reused_frames if first * 256 <= int(f['pts']) < end * 256]) == 412
            probe_cmd[probe_cmd.index('-read_intervals') + 1] = f'{(end - 2) / 60:.9f}%{end / 60 + 0.5:.9f}'
"""
assert old_reuse in text
text = text.replace(old_reuse, "        reused_probe = None\n        reused_frames = []\n")
text = text.replace("'recoveryReason': 'ffprobe stopped before one delayed final frame at the exclusive end; pad decoder read range and reuse 412 already verified selected PTS. No VFR inference.',", "'inspectionReason': 'New552.4–580 interval is absent from every retained baseline cut; compare visible cleaning instead of adopting the approach-dominated276.9–289 window.',")
text = text.replace("'failedHistory': 'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v3.json',", "'priorCompletedInspectionPreserved': 'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v4.json',")
new.write_text(text, encoding='utf-8')
print('Prepared one new native interval; completed v4 probes and45 samples preserved.')
