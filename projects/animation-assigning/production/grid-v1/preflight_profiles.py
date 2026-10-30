"""Finite native preflight queue; no rendering or unattended next episode."""
import argparse, subprocess, json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
R=H.parents[3]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ids',required=True);ap.add_argument('--revision',default='speech-v1');a=ap.parse_args()
 profiles=json.loads((R/'unity/VideoEditing/Assets/VideoScenes/animation-series-v1/animation-grid-presentations.json').read_text('utf8'))['presentations']
 lookup={p['id']:p for p in profiles}
 for key in a.ids.split(','):
  if key=='idle-intent':p={'mode':'idle-intent','duration':239/60,'cues':[]};frames=239
  else:p=lookup[key];frames=round(p['duration']*60)
  samples={0,frames-1}
  for cue in p['cues']:
   lo=max(0,round(cue['start']*60));hi=min(frames-1,round(cue['end']*60)-1)
   samples.add(min(hi,lo+12));samples.add((lo+hi)//2)
  if not p['cues']:samples.update([48,120,180])
  cmd=[sys.executable,'-X','utf8',str(H/'capture_grid.py'),'preflight','--cut',p['mode'],'--revision',a.revision+'-'+key,'--frames',str(frames),'--samples',','.join(map(str,sorted(samples)))]
  if key!='idle-intent':cmd+=['--presentation',key]
  print('PREFLIGHT',key,'frames',frames,'samples',len(samples),flush=True)
  subprocess.run(cmd,check=True,cwd=R)

if __name__=='__main__':main()
