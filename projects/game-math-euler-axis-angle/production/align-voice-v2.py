"""Use reviewed math speech normalization only for timing; never alter raw ASR."""
from pathlib import Path
import sys,runpy
R=Path(__file__).resolve().parents[3];slug='game-math-euler-axis-angle'
sys.path.insert(0,str(R/'qwen3-tts'));sys.argv=[sys.argv[0],slug]
# Importing under a non-main name installs the established spoken-number
# normalization and stable bilingual partitioning without running legacy batch jobs.
helpers=runpy.run_path(str(R/'production/batches/game-math-part2-full-series/align.py'),run_name='math_alignment_helpers')
sys.argv=[sys.argv[0],'--project',slug,'--manifest',f'projects/{slug}/production/revision-v2/tts-manifest.json']
helpers['a'].main()
