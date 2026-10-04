from pathlib import Path
import sys,runpy
root=Path(__file__).resolve().parents[3]
file=root/'production/batches/game-math-polar-lecture/align.py'
sys.argv=[str(file),'game-math-polar-2d',*sys.argv[1:]]
runpy.run_path(str(file),run_name='__main__')
