from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'game-math-part2-full-series'))
from camera_projection import make_scenes
globals().update(make_scenes('game-math-camera-projection',__name__))
