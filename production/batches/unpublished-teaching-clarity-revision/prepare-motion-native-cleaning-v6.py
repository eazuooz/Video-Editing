"""Inspect one fresh earlier cleaning interval; preserve completed v4/v5 samples."""
from pathlib import Path

base = Path(__file__).resolve().parent
target = base / 'inspect-motion-opening-native-v6.py'
assert not target.exists()
source = (base / 'inspect-motion-opening-native-v5.py').read_text('utf-8')
source = source.replace('motion-opening-native-v5', 'motion-opening-native-v6')
source = source.replace('motion-opening-native-execution-v5', 'motion-opening-native-execution-v6')
source = source.replace('inspect-motion-opening-native-v5', 'inspect-motion-opening-native-v6')
source = source.replace("'schemaVersion': 5", "'schemaVersion': 6")
old = "windows = [{'id': 'continuing-cleaning', 'firstFrame': 33144, 'endExclusiveFrame': 34800}]"
assert old in source
source = source.replace(old, "windows = [{'id': 'early-cleaning', 'firstFrame': 3480, 'endExclusiveFrame': 4140}]")
source = source.replace('New552.4–580 interval is absent from every retained baseline cut; compare visible cleaning instead of adopting the approach-dominated276.9–289 window.', 'Fresh58–69 interval follows the retained48–57.983333 cut; compare visible dirt removal without adopting follower-alert overlays in552–580.')
source = source.replace("'priorCompletedInspectionPreserved': 'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v4.json'", "'priorCompletedInspectionPreserved': ['production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v4.json', 'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v5.json']")
target.write_text(source, 'utf-8')
print('Prepared new58–69 inspection only;104 prior samples and18 boards retained.')
