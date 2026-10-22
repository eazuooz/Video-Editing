"""Original numeric construction stopped after a selected teaching beat."""
import importlib.util
import os
from pathlib import Path

p = Path(__file__).with_name('planes-legibility-scenes.py')
spec = importlib.util.spec_from_file_location('planes_legibility', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
sid = os.environ['GEOMETRY_PREVIEW_SID']
count = int(os.environ['GEOMETRY_PREVIEW_STATE_COUNT'])
if not sid.isdigit():
    class Preview(getattr(m, 'Polish'+sid)):
        pass
else:
    source = m.CONSTRUCT_SOURCE
    needle = "for i,beat in enumerate(s['beats']):"
    assert source.count(needle) == 1
    source = source.replace(needle, f"for i,beat in enumerate(s['beats'][:{count}]):")
    scope = dict(m.original.__dict__)
    exec(compile(source, __file__, 'exec'), scope)


    class Preview(getattr(m, 'Polish' + sid)):
        construct = scope['construct']
