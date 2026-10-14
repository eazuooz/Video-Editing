from pathlib import Path
import py_compile
B=Path(__file__).resolve().parent
p=B/'observe-orientation-guide-cpu-resource-v1.py';q=B/'observe-orientation-current34-cpu-resource-v1.py'
assert not q.exists()
t=p.read_text('utf-8-sig').replace("'build-motion-current17',","'build-motion-current17','build-orientation-current34','assemble-orientation-current34',")
assert t!=p.read_text('utf-8-sig')
q.write_text(t,'utf-8')
for x in [q,B/'build-orientation-current34-mix-v1.py']:py_compile.compile(str(x),doraise=True)
print('Prepared CPU resource observer and current34 mixer; no heavy worker started.')
