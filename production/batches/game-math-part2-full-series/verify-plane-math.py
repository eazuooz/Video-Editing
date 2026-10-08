"""Independent calculations for the plane/triangle lecture; pixels reviewed later."""
from pathlib import Path
import datetime, hashlib, json, shutil
import numpy as np
from production_control import require_current_authorization

ROOT = Path(__file__).resolve().parents[3]
slug = 'game-math-planes-barycentric'
require_current_authorization(slug, 'independent plane and triangle calculations')
base = ROOT / 'projects' / slug
checks = []

def check(name, values):
    checks.append(dict(name=name, status='passed', values=values))

normal = np.array([0., 2., 0.])
d = 4.
p = np.array([4., 5., -3.])
residual = normal @ p - d
distance = residual / np.linalg.norm(normal)
projection = p - residual / (normal @ normal) * normal
np.testing.assert_allclose([residual, distance], [6, 3])
np.testing.assert_allclose(projection, [4, 2, -3])
np.testing.assert_allclose(normal @ projection, d)
np.testing.assert_allclose(distance, (normal / 2 @ p - d / 2))
assert normal @ np.zeros(3) != d
check('affine-plane-residual-distance-projection', dict(residual=float(residual), signedDistance=float(distance), projection=projection.tolist(), normalizeBothNormalAndD=True, originNotOnPlane=True))

v = np.array([[0., 0., 0.], [6., 0., 0.], [0., 4., 0.]])
cross = np.cross(v[1]-v[0], v[2]-v[0])
np.testing.assert_allclose(cross, [0, 0, 24])
np.testing.assert_allclose(np.cross(v[2]-v[0], v[1]-v[0]), -cross)
np.testing.assert_allclose(cross/np.linalg.norm(cross), [0, 0, 1])
check('right-handed-winding', dict(cross=cross.tolist(), unitNormal=[0, 0, 1], d=0, reversedNormal=[0, 0, -1]))

polygon = np.array([[0., 0., 0.], [4., 0., 0.], [4., 2., 0.], [2., 3., 0.], [0., 2., 0.]])
def newell(vertices):
    result = np.zeros(3)
    for current, following in zip(vertices, np.roll(vertices, -1, axis=0)):
        result += [(current[1]-following[1])*(current[2]+following[2]),
                   (current[2]-following[2])*(current[0]+following[0]),
                   (current[0]-following[0])*(current[1]+following[1])]
    return result
np.testing.assert_allclose(newell(polygon), [0, 0, 20])
np.testing.assert_allclose(newell(polygon[::-1]), [0, 0, -20])
check('ordered-Newell-normal', dict(normal=[0, 0, 20], reversed=[0, 0, -20], scope='Ordered polygon; not arbitrary unordered least squares'))

sides = np.array([3., 4., 5.])
semiperimeter = sides.sum()/2
area = np.sqrt(semiperimeter * np.prod(semiperimeter-sides))
np.testing.assert_allclose([sides.sum(), semiperimeter, area], [12, 6, 6])
np.testing.assert_allclose(np.linalg.norm(np.cross([4, 0, 0], [0, 3, 0]))/2, area)
check('triangle-area-three-methods', dict(perimeter=12, semiperimeter=6, baseHeightArea=6, heronRadicand=36, heronArea=float(area), parallelogramArea=12, crossArea=6))

def signed_twice_area(a, b, c):
    u, w = (b-a)[:2], (c-a)[:2]
    return u[0]*w[1]-u[1]*w[0]
total = signed_twice_area(*v)
for weights, expected_point, inside in [([.2, .3, .5], [1.8, 2., 0.], True), ([-.2, .7, .5], [4.2, 2., 0.], False)]:
    weights = np.array(weights)
    point = weights @ v
    sub = np.array([signed_twice_area(point, v[1], v[2]), signed_twice_area(point, v[2], v[0]), signed_twice_area(point, v[0], v[1])])
    np.testing.assert_allclose(weights.sum(), 1)
    np.testing.assert_allclose(point, expected_point)
    np.testing.assert_allclose(sub / total, weights)
    np.testing.assert_allclose((-sub) / (-total), weights)
    assert bool(np.all(weights >= 0)) == inside
    check('signed-area-barycentrics-' + str(inside), dict(weights=weights.tolist(), point=point.tolist(), signedSubAreas=(sub/2).tolist(), insideAndCoplanar=inside, consistentWindingInvariant=True))

off_plane = np.array([1.8, 2., 7.])
np.testing.assert_allclose(off_plane[:2], [.2, .3, .5] @ v[:, :2])
assert abs(off_plane @ np.array([0., 0., 1.])) == 7
check('projected-weights-do-not-prove-coplanarity', dict(surfacePoint=[1.8, 2, 0], offPlane=off_plane.tolist(), distance=7, sameXY=True, mustRejectOffPlane=True))

color = np.array([.2, .3, .5]) @ np.eye(3)
np.testing.assert_allclose(color, [.2, .3, .5])
check('linear-vertex-RGB-interpolation', dict(weights=[.2, .3, .5], linearResult=color.tolist(), screenPerspectiveWeightsNotAssumedAffine=True, display='sRGB transfer for display only'))

path = base / 'production/math-verification.json'
backup = ROOT / 'shared/output' / slug / 'math-verification-before-current-clarification.json'
if path.exists() and not backup.exists():
    shutil.copy2(path, backup)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = dict(status='passed-independent-current-calculations-awaiting-final-pixels',
              reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), checks=checks,
              koScriptSha256=sha(base / 'script/narration.ko.json'),
              lessonDataSha256=sha(Path(__file__).parent / 'lessons' / (slug + '.json')),
              numericalChecksPassed=True, finalRenderedPixels='pending', passed=False)
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(len(checks), 'independent checks passed; final rendered math pixels still pending')
