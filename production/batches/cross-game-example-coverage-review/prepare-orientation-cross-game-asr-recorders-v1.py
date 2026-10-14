"""Prepare session/exit recorders with current five-item paths; no model job."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
src=(B/'register-orientation-additive-asr-v1.py').read_text('utf-8')
src=src.replace('additions-', 'cross-game-').replace('review-orientation-additive-voice-v2.py','review-orientation-cross-game-voice-v1.py').replace('existing6PCM-', 'cross-game5PCM-')
p=B/'register-orientation-cross-game-asr-v1.py';assert not p.exists();p.write_text(src,'utf-8');compile(src,str(p),'exec')
src=(B/'record-orientation-additive-asr-exit-v1.py').read_text('utf-8')
src=src.replace('additions-', 'cross-game-').replace('narration-tts-execution-v2.json','narration-cross-game-repair-execution-v1.json').replace('existing6PCM-','cross-game5PCM-')
p=B/'record-orientation-cross-game-asr-exit-v1.py';assert not p.exists();p.write_text(src,'utf-8');compile(src,str(p),'exec')
print('Prepared current five-item ASR session/exit recorders; no execution/model.')
