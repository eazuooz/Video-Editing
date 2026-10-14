"""Prepare a fresh observer after actual whole17 closure; no process controls."""
from pathlib import Path
import py_compile
B=Path(__file__).resolve().parent
p=B/'observe-motion-current17-cpu-resource-v6.py';assert not p.exists()
p.write_text((B/'observe-motion-current17-cpu-resource-v5.py').read_text('utf-8').replace('current17-cpu-resource-v5.json','current17-cpu-resource-v6.json'),'utf-8')
py_compile.compile(str(p),doraise=True)
print('Prepared new fresh observer V6; no observer or model run in this step.')
