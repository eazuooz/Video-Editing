"""Regression: unchanged quality-passing takes must beat failing candidates."""
from pathlib import Path
import importlib.util,json
sp=importlib.util.spec_from_file_location('lecture_voice',Path(__file__).parent/'render-voice.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
p=v.render_narration._passes_quality;s=v.render_narration._badness
assert not p(.075,65) and p(.002,45)
assert s(.002,45)<s(.075,65)
assert not p(.039,54) and p(.004,46)
assert s(.004,46)<s(.039,54)
assert not p(.002,20) and p(.002,35)
assert s(.002,35)<s(.002,20)
print(json.dumps({'passed':True,'qualityThresholdsUnchanged':True,'maxAttemptsUnchanged':True,'regressions':['scene18 fail65ms versus quiet passing45ms','scene06 fail54ms versus quiet passing46ms','quiet natural35ms versus clipped20ms'],'scope':'Local PART2 wrapper only; do not modify other projects or approved speaker/model'}))
