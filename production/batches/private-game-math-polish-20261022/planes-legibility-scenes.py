"""M11/M12 existing plane/triangle lesson typography; values and clock retained."""
import importlib.util
import inspect
import textwrap
from pathlib import Path

p = Path(__file__).with_name('lesson-scenes.py')
spec = importlib.util.spec_from_file_location('planes_recovery', p)
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
assert recovery.slug in ['game-math-plane-distances-v2', 'game-math-triangle-addresses-v2']
original = recovery.main
base_txt, base_card = original.txt, original.card


def readable_text(value, size=28, color=original.INK, font='Malgun Gothic'):
    size = {18:23, 19:24, 20:25, 21:25, 22:26, 23:27, 26:30, 27:31}.get(size, size)
    return base_txt(value, size, color, font)


def readable_card(value, width=6, size=29, color=original.BLUE):
    return base_card(value, width, max(size, 28), color)


def replace_once(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after)


original.txt, original.card = readable_text, readable_card
original.timing = lambda _slug, _data: recovery.T
CONSTRUCT_SOURCE = textwrap.dedent(inspect.getsource(original.PlaneTriangleScene.construct))
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE,
    'Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1)',
    'Line([-6.5,sub.get_bottom()[1]-.12,0],[6.5,sub.get_bottom()[1]-.12,0],color=RULE,stroke_width=1)')
scope = dict(original.__dict__)
exec(compile(CONSTRUCT_SOURCE, __file__, 'exec'), scope)
original.PlaneTriangleScene.construct = scope['construct']

extra = recovery.extra
extra.txt = readable_text
EXTRA_SOURCE = textwrap.dedent(inspect.getsource(extra.PlaneAddition.construct))
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, "O/'combined-addition-timing.json'", "Path(os.environ['POLISH_TIMING_MAP'])")
# Four formula rows need enough height; the separate caption retains its .65 cap.
EXTRA_SOURCE = replace_once(EXTRA_SOURCE,
    'def fixed(text,where,color=INK,size=27,width=6.05,height=1.3):',
    'def fixed(text,where,color=INK,size=30,width=6.05,height=1.65):')
EXTRA_SOURCE = replace_once(EXTRA_SOURCE,
    'fixed(text,[3.2,.35,0],color,29)', 'fixed(text,[3.2,.35,0],color,32)')
extra_scope = dict(extra.__dict__)
exec(compile(EXTRA_SOURCE, __file__, 'exec'), extra_scope)
extra.PlaneAddition.construct = extra_scope['construct']

for slot in recovery.T['scenes']:
    if slot['classification'] == 'explanation':
        sid = slot['id']
        globals()['Polish'+sid] = type('Polish'+sid, (getattr(recovery, 'Polish'+sid),), {'__module__':__name__})
