"""Reclaim only this revision's reproducible, abandoned unreviewed muxes.

Never targets baseline masters, footage, narration, current deliveries, or
another production. Inputs, hashes and picture/error evidence are retained.
"""
from subject_revision import *
import psutil

def main():
 roots=[DEST.parent/'game-math-subjects-20261115',DEST/'game-math-velocity-derivatives.first-grid-attempt',DEST/'game-math-skinning-normal-map.ass-boundary-attempt']
 rows=[]
 for root in roots:
  assert root.resolve().is_relative_to(DEST.parent.resolve()) and root.resolve()!=DEST.resolve()
  for process in psutil.process_iter(['pid','cmdline']):
   prefix=str(root.resolve()).replace('\\','/').lower()+'/'
   assert prefix not in ' '.join(process.info['cmdline'] or []).replace('\\','/').lower(),('Scratch file is still referenced by a live process',process.pid)
  for f in root.rglob('*.mp4') if root.exists() else []:
   assert f.resolve().is_relative_to(root.resolve()) and not f.is_symlink()
   assert f.name not in ('source.mp4','narration.mp4')
   slug=next((slug for slug in [e['slug'] for e in EPISODES.values()] if slug in str(f)),None);assert slug
   e=next(e for e in EPISODES.values() if e['slug']==slug)
   assert latest(e).is_file() and Path(e['baselineOutputs']['clean']).is_file()
   # These draft locations have never been human approved or delivered as the
   # current review; all accepted masters stay in the distinct final root.
   delivered=[r.get('files',{}).get('captioned',{}).get('path') for r in read(HERE/'progress.json')['rows']]
   assert not any(Path(target).resolve().is_relative_to(root.resolve()) for target in delivered if target)
   rows.append(dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f),preservedInput=str(latest(e))))
 report=dict(status='manifest-verified-before-scratch-cleanup',scope='Only reproducible abandoned muxes from this exact local image-replacement revision',files=rows,originalMastersPreserved=True,footageAndNarrationPreserved=True,allQaPicturesAndInputCodePreserved=True,platformChanges=False)
 save(HERE/'abandoned-mux-cleanup.json',report)
 for row in rows:
  f=Path(row['path']);assert f.stat().st_size==row['bytes'];f.unlink()
 report.update(status='own-abandoned-muxes-pruned',reclaimedBytes=sum(r['bytes'] for r in rows));save(HERE/'abandoned-mux-cleanup.json',report)
 print(len(rows),'abandoned scratch MP4s;',round(report['reclaimedBytes']/2**30,2),'GiB reclaimed; all baseline/final masters retained')

if __name__=='__main__':main()
