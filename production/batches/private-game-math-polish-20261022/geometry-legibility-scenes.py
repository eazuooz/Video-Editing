"""M09/M10 isolated typography and guide clarity; original math and clock."""
import importlib.util
import inspect
import textwrap
from pathlib import Path

p=Path(__file__).with_name('lesson-scenes.py')
spec=importlib.util.spec_from_file_location('geometry_recovery',p)
recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)
assert recovery.slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']
original=recovery.main
base_txt,base_card=original.txt,original.card

def readable_text(value,size=28,color=original.INK,font='Malgun Gothic'):
    size={18:23,19:24,20:25,21:25,22:26,23:27,26:30,27:31}.get(size,size)
    return base_txt(value,size,color,font)

def readable_card(value,width=6,size=29,color=original.BLUE):
    return base_card(value,width,max(size,28),color)

def replace_once(source,before,after):
    assert source.count(before)==1,before
    return source.replace(before,after)

original.txt,original.card=readable_text,readable_card
original.timing=lambda _slug,_data:recovery.T
CONSTRUCT_SOURCE=textwrap.dedent(inspect.getsource(original.GeometryScene.construct))
CONSTRUCT_SOURCE=replace_once(CONSTRUCT_SOURCE,
    'Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1)',
    'Line([-6.5,sub.get_bottom()[1]-.12,0],[6.5,sub.get_bottom()[1]-.12,0],color=RULE,stroke_width=1)')
# The min/max code retains its existing syntax roles and separate execution box.
CONSTRUCT_SOURCE=replace_once(CONSTRUCT_SOURCE,'font_size=21,color=INK,t2c=','font_size=24,color=INK,t2c=')
CONSTRUCT_SOURCE=replace_once(CONSTRUCT_SOURCE,'buff=.21).move_to([-1.55,-.1,0])','buff=.15).move_to([-1.55,-.40,0])')
CONSTRUCT_SOURCE=replace_once(CONSTRUCT_SOURCE,
    "txt('입력점 (x,y,z)',18,MUTED).move_to([-1.55,1.08,0])",
    "txt('입력점 (x,y,z)',18,MUTED).move_to([-1.55,.90,0])")
# Keep the legend outside the full expanded blue AABB and above fixed captions.
CONSTRUCT_SOURCE=replace_once(CONSTRUCT_SOURCE,
    "fit(txt('초록: 변환한 5점 / 파랑: 변환한 8꼭짓점 AABB',18,MUTED),6).move_to([-3.35,2.28,0])",
    "fit(txt('초록: 변환한 5점\\n파랑: 변환한 8꼭짓점 AABB',23,MUTED),6).move_to([3.15,-1.27,0])")
scope=dict(original.__dict__);exec(compile(CONSTRUCT_SOURCE,__file__,'exec'),scope)
original.GeometryScene.construct=scope['construct']

extra=recovery.extra;extra.txt=readable_text
EXTRA_SOURCE=textwrap.dedent(inspect.getsource(extra.LinesAddition.construct))
EXTRA_SOURCE=replace_once(EXTRA_SOURCE,"O/'combined-addition-timing.json'","Path(os.environ['POLISH_TIMING_MAP'])")
EXTRA_SOURCE=replace_once(EXTRA_SOURCE,'def fixed(text,where,color=INK,size=27):','def fixed(text,where,color=INK,size=30):')
EXTRA_SOURCE=replace_once(EXTRA_SOURCE,'if group.height>1.15:group.scale(1.15/group.height)','if group.height>1.25:group.scale(1.25/group.height)')
EXTRA_SOURCE=replace_once(EXTRA_SOURCE,'fixed(text,[3.2,.35,0],color,29)','fixed(text,[3.2,.35,0],color,32)')
extra_scope=dict(extra.__dict__);exec(compile(EXTRA_SOURCE,__file__,'exec'),extra_scope)
extra.LinesAddition.construct=extra_scope['construct']

for slot in recovery.T['scenes']:
    if slot['classification']=='explanation':
        sid=slot['id'];globals()['Polish'+sid]=type('Polish'+sid,(getattr(recovery,'Polish'+sid),),{'__module__':__name__})
