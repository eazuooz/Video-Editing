"""Use the unchanged local Whisper reviewer with a small CPU thread pool."""
from pathlib import Path
import sys,torch
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'qwen3-tts'))
from review_project_narration import main
if __name__=='__main__':
 # Long CPU batches can outlast the shared reviewer's two-hour watch window.
 # Re-enter with the same model/settings and reuse only current-hash caches.
 for attempt in range(4):
  try:
   main()
   break
  except TimeoutError:
   if '--watch' not in sys.argv or attempt==3:raise
   print('Voice production continues; resume current-hash read-back watch.',flush=True)
