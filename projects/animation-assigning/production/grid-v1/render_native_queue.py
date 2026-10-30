"""Capture the exact measured A01 native cut list, sequentially and without UI focus."""
import json, subprocess, sys
from pathlib import Path
import capture_grid as cg

H=Path(__file__).resolve().parent
R=H.parents[3]
L=H.parent/'local/grid-v1'

def main():
 plan=cg.read(H/'edit-plan.json')
 assert plan['episode']=='A01' and plan['revision']=='grid-v1'
 queue=plan['nativeCaptureQueue']
 for index,item in enumerate(queue,1):
  cg.authorize()
  out=L/'render'/item['revision']/item['mode']
  receipt=out/'render-success.json'
  if receipt.exists():
   record=cg.read(receipt);request=cg.read(out/'request.json')
   assert record['status']=='complete' and record['completed']==item['frames']
   assert request['frames']==item['frames'] and request.get('presentationId','')==item['presentation']
   assert (out/'unity.mp4').is_file()
   print('REUSE',index,len(queue),item['id'],flush=True)
   continue
  assert not out.exists(),'Incomplete output preserved: '+str(out)
  args=[sys.executable,'-X','utf8',str(H/'capture_grid.py'),'render','--cut',item['mode'],
        '--revision',item['revision'],'--frames',str(item['frames'])]
  if item['presentation']:args+=['--presentation',item['presentation']]
  print('CAPTURE',index,len(queue),item['id'],item['frames'],flush=True)
  subprocess.run(args,cwd=R,check=True)
 print('COMPLETE exact A01 native queue; final composite/QA remains pending',flush=True)

if __name__=='__main__':main()
