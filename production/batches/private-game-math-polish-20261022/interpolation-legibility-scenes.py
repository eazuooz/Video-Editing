"""M07 visual-only wrapper: preserve the original strings, math and clock."""
import importlib.util
import inspect
import textwrap
from pathlib import Path

p = Path(__file__).with_name('lesson-scenes.py')
spec = importlib.util.spec_from_file_location('interpolation_recovery', p)
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
assert recovery.slug == 'game-math-interpolation-paths-v2'
original = recovery.main
base_txt = original.txt
base_card = original.card


def readable_text(value, size=28, color=original.INK, font='Malgun Gothic'):
    size = {19:24, 20:25, 22:26, 23:27, 25:29, 27:31}.get(size, size)
    return base_txt(value, size, color, font)


def readable_card(value, width=6, size=29, color=original.BLUE):
    return base_card(value, width, max(size, 28), color)


def code_card(value, width=12, size=26, color=original.BLUE):
    words = original.fit(base_txt(value, max(size, 28), color), width - .4)
    face = original.Rectangle(width=width, height=max(.6, words.height + .14),
                              stroke_color=original.RULE, stroke_width=1,
                              fill_color=original.WHITE, fill_opacity=1)
    shadow = face.copy().set_stroke(width=0).set_fill(original.PALE, opacity=.9).shift(.04*original.RIGHT+.04*original.DOWN)
    return original.VGroup(shadow, face, words)


original.txt = readable_text
original.card = readable_card
original.code_card = code_card
original.timing = lambda _slug, _data: recovery.T
CONSTRUCT_SOURCE = textwrap.dedent(inspect.getsource(original.InterpolationScene.construct))


def replace_once(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after)


CONSTRUCT_SOURCE = replace_once(
    CONSTRUCT_SOURCE,
    "Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1)",
    "Line([-6.5,sub.get_bottom()[1]-.12,0],[6.5,sub.get_bottom()[1]-.12,0],color=RULE,stroke_width=1)",
)
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE, "font_size=20,color=INK,t2c=", "font_size=24,color=INK,t2c=")
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE, "buff=.11);fit(special,11.9);special.move_to([0,-.45,0])", "buff=.07);fit(special,11.9);special.move_to([0,-.3,0])")
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE, "active,card(beat,width=6 if panel else 12", "active,(code_card if mode=='slerp-code' else card)(beat,width=6 if panel else 12")
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE, "[3.1 if panel else 0,1.65,0]", "[3.1 if panel else 0,1.85 if mode=='slerp-code' else 1.65,0]")
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE, "txt('checked_unit: 유한·비영 입력 검증',23,RED).move_to([0,-2.25,0])", "txt('checked_unit: 유한·비영 입력 검증',23,RED).move_to([0,-2.45,0])")
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE, "Indicate(special[j],color=GOLD) for j in groups[i]", "Indicate(special[j],color=GOLD,scale_factor=1.06) for j in groups[i]")
CONSTRUCT_SOURCE = replace_once(CONSTRUCT_SOURCE, "fit(txt(label,20,BLUE if x<-3 else GREEN),3.08)", "fit(txt(label.replace(' / ','\\n'),20,BLUE if x<-3 else GREEN),2.95)")
scope = dict(original.__dict__)
exec(compile(CONSTRUCT_SOURCE, __file__, 'exec'), scope)
original.InterpolationScene.construct = scope['construct']

# Keep the existing supplementary construction and timed events as well.
extra = recovery.extra
extra.txt = readable_text
EXTRA_SOURCE = textwrap.dedent(inspect.getsource(extra.InterpolationAddition.construct))
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, "timing=O/'combined-addition-timing.json'", "timing=Path(os.environ['POLISH_TIMING_MAP'])")
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, "def fixed(content,where,color=INK,size=27):", "def fixed(content,where,color=INK,size=30):")
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, "if group.height>1.10:group.scale(1.10/group.height)", "if group.height>1.25:group.scale(1.25/group.height)")
EXTRA_SOURCE = replace_once(EXTRA_SOURCE, "fixed(content,[3.2,.35,0],color,29)", "fixed(content,[3.2,.35,0],color,32)")
extra_scope = dict(extra.__dict__)
exec(compile(EXTRA_SOURCE, __file__, 'exec'), extra_scope)
extra.InterpolationAddition.construct = extra_scope['construct']

for slot in recovery.T['scenes']:
    if slot['classification'] != 'explanation':
        continue
    sid = slot['id']
    parent = getattr(recovery, 'Polish' + sid)
    globals()['Polish' + sid] = type('Polish' + sid, (parent,), {'__module__': __name__})
