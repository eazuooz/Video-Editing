"""Scoped shared-pipeline wrapper; no work at import."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'production/batches/tech-ten-shorts-20261030'))
from scoped_pipeline import dispatch

def main():
    return dispatch('shorts-batman-origins-snow-below-camera', 'render-voice')

if __name__ == '__main__':
    main()
