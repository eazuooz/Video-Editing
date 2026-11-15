"""Preserve failed picture/input evidence; resume only this finite correction."""
from subject_revision import *
import psutil

def main():
 previous=read(HERE/'finite-worker.json');assert not psutil.pid_exists(previous['pid'])
 assert not read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['productionAllowedNow']
 e=EPISODES['M28'];p=work(e);d=DEST/e['slug']
 assert read(p/'encoded.json')['finalReviewReady']==False
 rows=[]
 for parent,target in ((WORK,p),(DEST,d)):
  archive=parent/(e['slug']+'.context-formula-attempt')
  assert target.resolve().parent==parent.resolve() and not archive.exists()
  target.rename(archive)
  for f in archive.glob('*.mp4'):
   assert parent==DEST and f.resolve().parent==archive.resolve()
   assert latest(e).is_file() and Path(e['baselineOutputs']['clean']).is_file()
   assert not any(str(f).replace('\\','/').lower() in ' '.join(x.info['cmdline'] or []).replace('\\','/').lower() for x in psutil.process_iter(['cmdline']))
   rows.append(dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size))
 save(HERE/'context-overlap-draft-cleanup.json',dict(status='verified-own-failed-draft-only',files=rows,baselinePreserved=True,pictureAndInputEvidencePreserved=True))
 for row in rows:Path(row['path']).unlink()
 r=read(HERE/'context-overlap-draft-cleanup.json');r.update(status='own-failed-muxes-pruned',reclaimedBytes=sum(x['bytes'] for x in rows));save(HERE/'context-overlap-draft-cleanup.json',r)
 phase=HERE/'local/context-phases/M28-M30-M31-M32-M33.json';v=read(phase);v.update(actuallyInspected=True,review=f'All{len(v["rows"])} early/late authoring pictures viewed on{len(v["boards"])} boards; corrected M28 late Hooke formula viewed at1080p. Photo moved to blank upper-center; all original formula rows visible. M30–M33 contexts avoid formulas and captions.',humanReviewed=False);save(phase,v)
 freeze=read(HERE/'authoring-freeze.json');freeze.setdefault('scopedCorrections',[]).append(dict(episode='M28',previousEncoderSha256=freeze['encoderSha256'],reason='Actual encoded late002 photo overlapped formula; relocate only this context to inspected upper-center. Previously passed masters unchanged.',authoringEvidence=str(phase),encoderSha256=sha(HERE/'subject_revision.py')));freeze['encoderSha256']=sha(HERE/'subject_revision.py');save(HERE/'authoring-freeze.json',freeze)
 save(HERE/'worker-before-context-correction.json',previous)
 cpath=ROOT/'shared/publishing/video-production-control.json';c=read(cpath);v=c['explicitMathRemainingBatch20261104'];v['productionAllowedNow']=True;v['gameSubjectRevision20261115']['contextFormulaHold'].update(status='resolved-at-safe-boundary',resolution='Worker exited without termination; all remaining contexts phase-checked; only M28 requires new encode. M29 already encoded unaffected.');save(cpath,c)
 print('M28 failed muxes pruned; picture/input evidence retained; same finite scope may resume')
if __name__=='__main__':main()
