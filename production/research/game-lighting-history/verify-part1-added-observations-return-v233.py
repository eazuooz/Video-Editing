"""Verify exact own idle lease return; never restart completed research."""
from pathlib import Path
s=Path(__file__).with_name('verify-part1-onset-gpu-return-v207.py').read_text('utf-8')
s=s.replace('part1-onset-repairs-tts-execution-v199','part1-added-observations-tts-execution-v232').replace('part1-onset-gpu-return-v207','part1-added-observations-gpu-return-v233').replace("['runtime-texture-size','geometry-car-material']","['cyber-surface-observation','rivalry-surface-observation']").replace('session=13934','session=45370')
exec(compile(s,str(__file__),'exec'))
