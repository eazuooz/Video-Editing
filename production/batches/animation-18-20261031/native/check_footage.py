"""Reject black transitions in scoped edits while retaining approved action windows."""
from pathlib import Path
import subprocess,json
import numpy as np
def black_seconds(file,start,seconds):
    result=subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(start),'-i',str(file),'-t',f'{seconds:.4f}',
                           '-vf','fps=4,scale=80:44,format=gray','-an','-f','rawvideo','-pix_fmt','gray','pipe:1'],capture_output=True,check=True)
    if not result.stdout:return seconds
    frames=np.frombuffer(result.stdout,np.uint8).reshape(-1,80*44)
    blank=(np.mean(frames,axis=1)<6)&(np.quantile(frames,.975,axis=1)<19)
    run=peak=0
    for value in blank:
        run=run+1 if value else 0;peak=max(peak,run)
    return peak/4
def inspect(rows,catalog,root):
    changes=[]
    for row in rows:
        key=row['key']
        if key not in catalog:continue
        entry=catalog[key];file=root/entry['file'];span=row['frames']/60;at=row['sourcePoint']
        black=black_seconds(file,at,span)
        if black<.5:continue
        # Only try neighboring points in the same inspected action window. Keep the original choice legible in the edit record.
        starts=[]
        for a,b in entry['observedWindows']:
            if a-1<=at<=b+1:
                for delta in (-1,1,-2,2,-3,3,-4,4,-5,5,-6,6):
                    candidate=at+delta
                    if a<=candidate and candidate+span<=b:starts.append(candidate)
        fixed=next((x for x in starts if black_seconds(file,x,span)<.5),None)
        if fixed is None:raise ValueError(f"Review source fade: cue {row['cue']} {key} @{at}s for {span:.2f}s; {black:.2f}s blank")
        row['sourcePoint']=fixed
        changes.append(dict(cue=row['cue'],source=key,original=at,reviewedNeighbor=fixed,originalBlankSeconds=black))
    return changes
