"""Native source temporal-change corroboration, not semantic or engine telemetry."""
import numpy as np
from prepare import *
def main():
 sources=read(HERE/'sources.json');plan=read(HERE/'plan.json');rows=[]
 for e in plan['episodes']:
  for s in e['inserts']:
   source=sources[s['source']];duration=min(18,s['sourceOut']-s['sourceIn'])
   data=subprocess.check_output([FF,'-v','error','-nostdin','-threads','1','-ss',str(s['sourceIn']),'-t',str(duration),'-i',source['file'],'-an','-vf','fps=2,scale=160:90','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-'],creationflags=subprocess.CREATE_NO_WINDOW)
   f=np.frombuffer(data,dtype=np.uint8).reshape(-1,90,160,3).astype('int16');diff=np.abs(f[1:]-f[:-1]);changed=(diff.max(axis=3)>5).mean(axis=(1,2));moving=float((changed>.0003).mean());assert len(f)>=20 and moving>.1,(s['key'],len(f),moving)
   rows.append(dict(key=s['key'],sourceSha256=source['sha256'],nativeStart=s['sourceIn'],observedSeconds=duration,temporalSamples=len(f),changedAdjacentSampleFraction=moving,meanChangedPixelFraction=float(changed.mean()),nativeSpeed=1,loop=False,freezePadding=False,interpretation='Corroborates that source images change. Actual conceptual action is separately judged from temporal strips and encoded composites; camera motion is not mislabeled as measured object motion.'))
 save(HERE/'native-motion.json',dict(status='passed-for-all-selected-sources',cases=rows));print('Native temporal evidence:',len(rows),'cases')
if __name__=='__main__':main()
