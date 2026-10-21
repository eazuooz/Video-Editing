"""M08-only visual wrapper, retaining original conversions and event clock."""
import importlib.util
import inspect
import textwrap
from pathlib import Path

p = Path(__file__).with_name('lesson-scenes.py')
spec = importlib.util.spec_from_file_location('conversions_recovery', p)
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
assert recovery.slug == 'game-math-rotation-conversions-v2'
original = recovery.main
base_txt, base_card = original.txt, original.card


def readable_text(value, size=28, color=original.INK, font='Malgun Gothic'):
    size = {19:24, 20:25, 22:26, 23:27, 25:29, 26:30, 27:31}.get(size, size)
    return base_txt(value, size, color, font)


def readable_card(value, width=6, size=29, color=original.BLUE):
    return base_card(value, width, max(size, 28), color)


def replace_once(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after)


original.txt, original.card = readable_text, readable_card
original.timing = lambda _slug, _data: recovery.T
CONSTRUCT_SOURCE = textwrap.dedent(inspect.getsource(original.InterpolationScene.construct))
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE,
    'Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1)',
    'Line([-6.5,sub.get_bottom()[1]-.12,0],[6.5,sub.get_bottom()[1]-.12,0],color=RULE,stroke_width=1)')
scope = dict(original.__dict__)
exec(compile(CONSTRUCT_SOURCE, __file__, 'exec'), scope)
original.InterpolationScene.construct = scope['construct']

extra = recovery.extra
extra.txt = readable_text
EXTRA_SOURCE = textwrap.dedent(inspect.getsource(extra.InterpolationAddition.construct))
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, "timing=O/'combined-addition-timing.json'", "timing=Path(os.environ['POLISH_TIMING_MAP'])")
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, 'def fixed(content,where,color=INK,size=27):', 'def fixed(content,where,color=INK,size=30):')
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, 'if group.height>1.10:group.scale(1.10/group.height)', 'if group.height>1.25:group.scale(1.25/group.height)')
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, 'fixed(content,[3.2,.35,0],color,29)', 'fixed(content,[3.2,.35,0],color,32)')
extra_scope = dict(extra.__dict__)
exec(compile(EXTRA_SOURCE, __file__, 'exec'), extra_scope)
extra.InterpolationAddition.construct = extra_scope['construct']

for slot in recovery.T['scenes']:
    if slot['classification'] == 'explanation':
        sid = slot['id']
        globals()['Polish'+sid] = type('Polish'+sid, (getattr(recovery, 'Polish'+sid),), {'__module__':__name__})
