"""Prepare single-run exact-identity closure and encoded-pixel workers for10b."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
old=(B/'record-orientation-07b-worker-exit-v3.py').read_text('utf-8-sig')
new=old.replace('07b-tracked-','10b-tracked-').replace('tracked07b','tracked10b').replace('-execution-v2.json','-execution-v1.json').replace('exitRecorderVersion=3','exitRecorderVersion=1')
p=B/'record-orientation-10b-worker-exit-v1.py';assert not p.exists();p.write_text(new,'utf-8')
old=(B/'extract-orientation-07b-tracked-pixels-v2.py').read_text('utf-8-sig')
new=old.replace('07b-tracked-','10b-tracked-').replace("'07b-encoded-","'10b-encoded-").replace('-execution-v2.json','-execution-v1.json')
begin=new.index('events=[int(t*60)');end=new.index('\nfor seg in',begin)
new=new[:begin]+"events=[int(t*60) for t in [2.18,6.34,8.1,10.78,14.76,15.5,15.9,16.3,17.4,18.74,19.66,20.68,21.8,24.88,26.24,28.9,29.36,31.64]]"+new[end:]
p=B/'extract-orientation-10b-tracked-pixels-v1.py';assert not p.exists();p.write_text(new,'utf-8')
print('Prepared10b exact-identity closure and encoded-pixel workers; execution0.')
