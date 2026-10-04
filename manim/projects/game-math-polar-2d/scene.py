from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'game-math-polar-lecture'))
from lesson import make_scenes
globals().update(make_scenes('game-math-polar-2d',__name__))
