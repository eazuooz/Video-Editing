"""Current selected project context; importing starts no jobs."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'production/batches/tech-ten-shorts-20261030'))
from scoped_context import make_context
globals().update(make_context('shorts-starcraft-worker-mineral-walk'))
