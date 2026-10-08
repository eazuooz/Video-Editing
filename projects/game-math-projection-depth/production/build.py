from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[3]/'production/batches/game-math-part2-full-series/build.py'),run_name='__main__')
