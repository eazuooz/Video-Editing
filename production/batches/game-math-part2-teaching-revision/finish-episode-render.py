"""Sequential technical assembly; does not upload or grant review approval."""
from pathlib import Path
import sys,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug=sys.argv[1]
for stage in ['mix','burn','qa']:
 subprocess.run([sys.executable,'-X','utf8',str(B/'build-episodes.py'),slug,stage],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
subprocess.run([sys.executable,'-X','utf8',str(B/'prepare-editor.py'),slug],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
subprocess.run([sys.executable,'-X','utf8',str(B/'make-final-review-page.py'),slug],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
print('Technical render complete; direct moving/caption/listening/publishing review remains separate',flush=True)
