"""One scoped correction after the previous worker's natural completion."""
from subject_revision import *
import psutil,progress,run_remaining

def main():
 old=read(HERE/'finite-worker.json');pid=old['pid'];started=psutil.Process(pid).create_time() if psutil.pid_exists(pid) else None
 journal=HERE/'label-layer-correction-worker.json';save(journal,dict(pid=os.getpid(),episode='M33',status='waiting-for-prior-worker-natural-completion',forceTerminated=False))
 while started is not None and psutil.pid_exists(pid):
  try:
   if psutil.Process(pid).create_time()!=started:break
  except psutil.NoSuchProcess:break
  time.sleep(2)
 assert not any('collect_final_frames.py' in ' '.join(x.info['cmdline'] or []) for x in psutil.process_iter(['cmdline']))
 old=read(HERE/'finite-worker.json');assert old['status']=='encodes-ended-actual-picture-review-pending' and not old['failed']
 save(HERE/'worker-before-label-correction.json',old)
 e=EPISODES['M33'];p=work(e);enc=read(p/'encoded.json');assert not enc['finalReviewReady'] and not (p/'qa.json').exists()
 archives=[]
 for parent,target in ((WORK,p),(DEST,DEST/e['slug'])):
  archive=parent/(e['slug']+'.label-backing-attempt')
  assert target.resolve().parent==parent.resolve() and not archive.exists()
  target.rename(archive);archives.append(str(archive))
 save(journal,dict(pid=os.getpid(),episode='M33',status='prior-attempt-preserved-fresh-encode-pending',archives=archives,priorCaptionedSha256=enc['files']['captioned']['sha256'],reason='Actual encoded apex head and landing feet were hidden by label backings. Draw original-label masks before the character, retain replacement labels above it.',forceTerminated=False,humanReviewed=False))
 freeze=read(HERE/'authoring-freeze.json');freeze.setdefault('scopedCorrections',[]).append(dict(episode='M33',reason='Verified actor occlusion at exact final029 apex/landing. Only two label backings moved before photo layer; original mathematics, speech and timing unchanged.',previousEncoderSha256=freeze['encoderSha256'],encoderSha256=sha(HERE/'subject_revision.py'),authoringFrames=[dict(path=str(HERE/'local/tests-v13'/name),sha256=sha(HERE/'local/tests-v13'/name),actuallyInspected=True) for name in ('M33-029-657.62.png','M33-029-687.95.png')]))
 freeze['encoderSha256']=sha(HERE/'subject_revision.py');save(HERE/'authoring-freeze.json',freeze)
 progress.update();run_remaining.main(['M33'])
 result=read(journal);result['status']='corrected-encode-ended-actual-picture-review-pending';save(journal,result)
if __name__=='__main__':main()
