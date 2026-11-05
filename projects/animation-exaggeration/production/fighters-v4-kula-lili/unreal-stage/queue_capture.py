"""Wait for the explicitly ordered voice session before allocating the renderer."""
from pathlib import Path
import sys, time, subprocess, json
H=Path(__file__).resolve().parent
L=H.parents[1]/'local/fighters-v4-kula-lili'
clock=L/'voice/qwen/additional-qwen.timing.json'
while not clock.is_file():
    time.sleep(5)
print('Three voice takes assembled. Queuing native image captures.',flush=True)
subprocess.run([sys.executable,'-u','-X','utf8',str(H/'capture.py')],check=True)
