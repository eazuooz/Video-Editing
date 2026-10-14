"""Find short unplanned grey diagnostics across every native frame; no visual approval."""
import importlib.util,json,subprocess,sys
from pathlib import Path
import numpy as np
p=Path(__file__).with_name('review-media-common-v15.py')
s=importlib.util.spec_from_file_location('review_media',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
suffix=sys.argv[1];pp=m.PROD/f'native-repair-{suffix}-plan-v18.json';plan=m.read(pp)
dest=m.PROD/f'native-repair-{suffix}-grey-audit-v18.json';assert not dest.exists(),'Preserve prior evidence'
resource=m.resources();rows=[]
for c in plan['cuts']:
 source=m.ROOT/c['output'];proof=m.read(source.with_suffix('.verification.json'));assert m.sha(source)==proof['outputSha256']
 command=[str(m.FF),'-v','error','-threads','1','-filter_threads','1','-i',str(source),'-an','-vf','crop=1760:850:80:80,scale=128:72','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
 result=subprocess.run(command,capture_output=True,check=True);pixels=np.frombuffer(result.stdout,dtype=np.uint8).reshape(-1,72,128,3);assert len(pixels)==c['frames']
 delta=pixels.max(axis=3).astype(np.int16)-pixels.min(axis=3).astype(np.int16)
 near_grey=((delta<12)&(pixels.mean(axis=3)>55)).mean(axis=(1,2));suspects=np.flatnonzero(near_grey>.65)
 rows.append(dict(id=c['id'],frames=len(pixels),sha256=proof['outputSha256'],commandLine=command,exitCode=result.returncode,minGreyFraction=float(near_grey.min()),maxGreyFraction=float(near_grey.max()),suspectFrames=[dict(localFrame=int(f),timelineFrame=c['fromFrame']+int(f),sourceSeconds=c['sourceFromSeconds']+int(f)/60,nearGreyFraction=float(near_grey[f]))for f in suspects]))
m.save(dest,dict(recordedAt=m.stamp(),plan=dict(path=m.rel(pp),sha256=m.sha(pp)),worker=m.worker(),resourceObservation=resource,results=rows,method='Every decoded frame, interior crop excluding captions; fraction of bright pixels with RGB channel range below12. Threshold0.65 identifies candidates for direct visual review, not engine modes or final approval.',suspectCount=sum(len(r['suspectFrames'])for r in rows),allFinalPixelsReviewed=False,qaApproved=False,newImages=0,newGitImages=0))
print(json.dumps(dict(path=m.rel(dest),suspects=[dict(id=r['id'],frames=r['suspectFrames'])for r in rows],finalApproval=False)),flush=True)
