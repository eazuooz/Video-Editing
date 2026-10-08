"""One owned TTS handoff for current episode overview,closure,and full-line repairs."""
from pathlib import Path
import argparse,subprocess,sys
from production_control import require_current_authorization
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--device',choices=['cpu','cuda:0'],required=True);args=p.parse_args();assert args.project=='game-math-camera-projection';require_current_authorization(args.project,'split-episode narration')
sys.path.insert(0,str(R/'qwen3-tts'));from gpu_handoff_guard import check_gpu_handoff
check_gpu_handoff(args.project,args.device)
subprocess.run([sys.executable,'-X','utf8',str(B/'render-voice.py'),'--project',args.project,'--batch-size','1','--device',args.device,'--scenes','01,24','--force-scenes','01,24'],cwd=R,check=True)
for sid in ['13','15']:
 subprocess.run([sys.executable,'-X','utf8',str(B/'repair-scene-by-lines.py'),args.project,sid,'--device',args.device,'--defer-assembly'],cwd=R,check=True)
print('Current episode overview/closure and full line-by-line numeric repairs checkpointed; raw readback/final timing still required.',flush=True)
