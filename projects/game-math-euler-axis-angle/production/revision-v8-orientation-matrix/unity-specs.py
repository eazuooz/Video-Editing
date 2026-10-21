"""V8 spatial demonstrations. Pure CPU data; no Unity or renderer is started."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / 'projects/game-math-euler-axis-angle'
H = Path(__file__).parent
O = P / 'production/local/revision-v8-orientation-matrix/unity'
ISO = P / 'production/local/revision-v6/unity-capture'
ASSET = Path('Assets/VideoScenes/game-math-orientation-matrix')
SCRIPT = P / 'script/revision-v8-orientation-matrix/narration.ko.json'
WIDTH, HEIGHT, FPS = 1000, 700, 60

def shot(id, scene, mode, frames=181, **kw):
    return dict(dict(id=id, sceneId=scene, mode=mode, frames=frames,
                angleFrom=0, angleTo=90, axes=True, upright=True,
                point=False, plane=True, pointObject=dict(x=1,y=0,z=2),originFrom=dict(x=0,y=0,z=0),originTo=dict(x=0,y=0,z=0)), **kw)

# A matrix is captured from actual transformed basis vectors. Angles are
# pedagogical commands, not inferred commercial-game values or Euler triples.
SHOTS = [
 shot('direction', 'm01', 'direction', 121, angleTo=45, axes=False, upright=False, plane=False),
 shot('bank', 'm01', 'bank', 181, angleTo=45, axes=False, upright=False),
 shot('intro-translate', 'm01', 'intro-translate', 121, axes=False, upright=False, originTo=dict(x=.8,y=.4,z=0)),
 shot('intro-orientation', 'm01', 'intro-orientation', 121, angleTo=45, axes=False, upright=False, originFrom=dict(x=.8,y=.4,z=0),originTo=dict(x=.8,y=.4,z=0)),
 shot('home-y90', 'm02', 'yaw', 181, axes=False),
 shot('camera-roll', 'm02', 'camera', 181, angleTo=35, axes=False, upright=False),
 shot('basis-y90', 'm03', 'yaw', 181),
 shot('origin-follow', 'm03', 'translate', 121, angleFrom=90, angleTo=90),
 shot('point-place', 'm04', 'point', 121, angleFrom=90, angleTo=90, point=True),
 shot('point-sum', 'm04', 'point-path', 181, angleFrom=90, angleTo=90, point=True),
 shot('point-fixed', 'm05', 'fixed', 2, angleFrom=90, angleTo=90, point=True),
 shot('scale-x', 'm05', 'scale', 181, point=True, pointObject=dict(x=1,y=0,z=0)),
 shot('forward-move', 'm06', 'forward', 181, angleFrom=90, angleTo=90),
 shot('target-right', 'm06', 'target-right', 2, angleFrom=90, angleTo=90),
 shot('target-left', 'm06', 'target-left', 2, angleFrom=90, angleTo=90),
 shot('command-x30', 'm06', 'pitch', 121, angleTo=30),
 shot('projection', 'm07', 'projection', 361, angleTo=180),
 shot('projection-turn90', 'm07', 'projection', 91, angleTo=90),
 shot('projection-to60', 'm07', 'projection', 61, angleFrom=90, angleTo=60),
 shot('basis-rows', 'm08', 'fixed', 2, angleFrom=90, angleTo=90),
 shot('right-unit-y90', 'm09', 'yaw', 181, point=True, plane=False, pointObject=dict(x=1,y=0,z=0)),
 shot('point-y90-again', 'm09', 'yaw', 181, angleFrom=90, angleTo=180, point=True, plane=False, pointObject=dict(x=1,y=0,z=0)),
 shot('arm-hand-sword', 'm09', 'arm', 181, plane=False, axes=False),
 shot('reverse-y90', 'm09', 'yaw', 181, angleFrom=180, angleTo=90, point=True, plane=False, pointObject=dict(x=1,y=0,z=0)),
 shot('pose-context', 'm10', 'humanoid', 2, plane=False, axes=False, upright=False),
 shot('complex-pose', 'm11', 'complex', 2),
 shot('reflection', 'm11', 'reflection', 2),
 shot('stretch-x', 'm12', 'scale', 181, point=True, pointObject=dict(x=1,y=0,z=0)),
 shot('shear', 'm12', 'shear', 181),
 shot('creep-exaggerated', 'm12', 'creep', 181),
 shot('normalize-only', 'm12', 'normalize', 121),
 shot('orthonormalize', 'm12', 'orthonormalize', 121),
 shot('recap-bank', 'm13', 'bank', 121, angleTo=45),
]

# Resolve action phrases against actual voice ASR. Native frames are finite
# and consumed once; definitions/reading continue over an exact state PNG.
def use(asset, state='last', cue=None, **kw):
    d=dict(asset=asset, state=state)
    if cue: d['cue']=cue
    return dict(d, **kw)

PARAGRAPHS = {
 'm01': [
  use('bank','last', role='overview hero; retain forward arrow and changed up'),
  use('intro-translate','motion','잡아서 옮기고', secondary=[use('intro-orientation','motion','어떤 기울기로')], role='actual TOTK left; controlled translation then orientation at identical held posttranslation origin; no game angle measurement'),
  use('direction','motion','축을 따라 빙글 돌려도', result='direction vector itself remains unchanged'),
  use('bank','motion','옆으로 기울면', result='forward unchanged; wing/up rotate'),
  use('bank','last', role='three independent changes are conceptual; no Euler sequence')],
 'm02': [
  use('bank','last'), use('home-y90','motion','동쪽을 보고 있다면'),
  use('home-y90','motion','와이축을 중심으로 사분의 일 바퀴', reuse='purposeful first explicit signed-axis proof; reset to home is named'),
  use('home-y90','last'), use('home-y90','last'),
  use('camera-roll','motion','화면만 옆으로 기울여', result='camera position and target fixed; view-up changes')],
 'm03': [
  use('basis-y90','first', role='three named unit arrows revealed by root'),
  use('basis-y90','motion','비행기가 어느 쪽으로 돌아도', result='object own coordinates remain unit triples'),
  use('basis-y90','last', role='same center dashed upright and solid object'),
  use('origin-follow','motion','얼마나 이동했는지는 빼고', result='object and upright origins move together; basis difference unchanged'),
  use('basis-y90','last', role='actual row basis supplies matrix construction')],
 'm04': [
  use('basis-y90','motion','동쪽으로 돌려', resetReason='narration explicitly recalls north/home'),
  use('basis-y90','last', role='rowX=[0,0,-1], rowY=[0,1,0], rowZ=[1,0,0]'),
  use('point-place','motion','점을 찍습니다', result='point revealed at actual [2,0,-1]U'),
  use('point-sum','motion','오른쪽 축을 한 번 따라가고', result='progressive 1 rowX then2 rowZ; point never moves'),
  use('point-fixed','last', role='same physical point, dual coordinate labels'),
  use('point-fixed','last')],
 'm05': [
  use('point-fixed','last'), use('point-fixed','last'), use('point-fixed','last'),
  use('scale-x','motion','두 배 늘리는', result='counterexample: inverse1/2 differs from unchanged transpose2'),
  use('point-fixed','last', role='explicit return to fixed rotation example; no unknown data')],
 'm06': [
  use('point-fixed','last', role='generic matrix capabilities are root diagram, not a claim of a perspective implementation'),
  use('target-right','last'),
  use('forward-move','motion','실제로 어디로 움직일지', secondary=[use('target-right','last','양수면 오른쪽'),use('target-left','last','음수면 왼쪽')]),
  use('command-x30','motion','엑스축으로 삼십 도 돌리라는'),
  use('target-right','last'), use('target-right','last'),
  use('target-right','last', role='same point/space roots; root semantic code carries bidirectional interface'),
  use('basis-rows','last')],
 'm07': [
  use('projection','first', exactExamples={'same':0,'perpendicular':180,'opposite':360}),
  use('projection-turn90','motion','화살표가 옆으로 누울수록', finishBeforeCue='직각에서는', secondary=[use('projection-to60','motion','육십 도를 벌리면')], result='first0->90 arrives at component0 before 직각에서는; then90->60 arrives at component0.5'),
  use('projection','last', sourceFrame=120, role='unit vectors and component dot product'),
  use('projection','motion','직각의 코사인은 영', sourceWindow=[120,360], exactStages={'90degrees':180,'180degrees':360}),
  use('basis-rows','last', role='restore Y90: center cell1, first cell0')],
 'm08': [use('basis-rows','last', role=r) for r in [
  'one row at a time; input versus output labels', 'p q r and primed axes are names; dot sign separate',
  'both compared arrows in ONE common frame', 'read OUTPUT axes in INPUT coordinates as COLUMNS',
  'read INPUT axes in OUTPUT coordinates as ROWS', 'limits: opposite reading assumes orthonormal bases',
  'row/column vector convention differs from memory layout']],
 'm09': [
  use('point-fixed','last'), use('point-fixed','last', role='root graphics flow, no mandatory matrix-only API claim'),
  use('point-fixed','last'),
  use('arm-hand-sword','first', role='detailed generic articulated arm/hand/recognizable sword as tool, actual relative frames'),
  use('arm-hand-sword','motion','그 순서대로 두 행렬을 곱합니다', role='A=tool input, B=hand intermediate, C=body output at fixed shoulder origin; source orientation matrices are exported'),
  use('right-unit-y90','motion','사분의 일 회전을 적용하면', secondary=[use('point-y90-again','motion','한 번 더 적용하면')], result='Hand-coordinate RIGHTunit[1,0,0] becomes[0,0,-1] then[-1,0,0]; neutral basis diagram, distinct from m04 point'),
  use('reverse-y90','motion','마지막에 한 동작부터', result='undo last turn first; root space chain verifies order')],
 'm10': [use('pose-context','last', role='self-authored neutral articulated mannequin; actual15 parent-relative orientation references; model assumption not universal humanoid standard; root arithmetic over retained model') for _ in range(5)],
 'm11': [
  use('complex-pose','last'), use('basis-rows','last'), use('basis-rows','last'),
  use('basis-rows','last', role='root3length+3pairdot constraint reveals'),
  use('basis-rows','last'),
  use('reflection','last','첫째 축만 반대로 뒤집어도', role='exact before/after; asymmetric F mark mirrors; det-1, no singular interpolation')],
 'm12': [
  use('stretch-x','motion','일에서 이로 바꿔', result='actual aircraft and basis X stretch; tracked1unit point to2'),
  use('shear','motion','비스듬히 찌그러질', result='nonperpendicular axes and actual mesh shear'),
  use('basis-rows','last', role='external-data/convention distinction; no invented sensor measurement'),
  use('creep-exaggerated','first', role='root error accumulation concept; exaggerated values are illustration'),
  use('creep-exaggerated','motion','확대해서', result='explicit pedagogical amplification, not measured FP32 drift'),
  use('normalize-only','motion','각 축을 따로 길이 일로', secondary=[use('orthonormalize','motion','축 사이의 관계까지 함께 고쳐야')], result='normalization leaves nonzero pair dots; orthonormalization restores unit orthogonal same-handed basis')],
 'm13': [
  use('recap-bank','motion','위쪽이 달라지면'), use('basis-rows','last'),
  use('point-fixed','last'), use('complex-pose','last'), use('basis-rows','last')],
}
