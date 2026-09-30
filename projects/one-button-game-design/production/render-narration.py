"""Local scene synthesis with bounded CPU threading; preserves valid takes."""
import sys
import json
from pathlib import Path
import torch

ROOT = Path(__file__).resolve().parents[3]
manifest_path=ROOT/'projects/one-button-game-design/project.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
stem=manifest['tts']['outputDir']+'/'+manifest['tts']['filenameStem']
# Voice/subtitle tools operate on the body. prepare creates the final +2s
# subtitle copies, so rerunning the full workflow never adds the intro twice.
manifest['paths']['captionsKo']=stem+'.srt'
manifest['paths']['captionsEn']=stem+'.en.srt'
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
torch.set_num_threads(2)
sys.path.insert(0, str(ROOT / 'qwen3-tts'))
import render_narration

sys.argv = [sys.argv[0], '--project', 'one-button-game-design', '--batch-size', '1', *sys.argv[1:]]
render_narration.main()
