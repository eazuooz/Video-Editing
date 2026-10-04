"""Verify the actual numerical examples and singular cases in both lectures."""
from pathlib import Path
import math,random,json
from coordinates import *
def close(a,b):assert all(math.isclose(x,y,abs_tol=1e-9,rel_tol=1e-10) for x,y in zip(a,b)),(a,b)
close(canonical_polar(-2,math.pi/4),(2,-3*math.pi/4))
close(xy_to_polar(-3,4),(5,math.atan2(4,-3)))
close(polar_to_xy(10,math.pi/6),(5*math.sqrt(3),5))
close(camera_position((0,1,0),5,math.pi/3,-math.pi/6),(3.75,3.5,5*math.sqrt(3)/4))
close(xyz_to_book_spherical(0,2,0),(2,0,-math.pi/2))
close(xyz_to_book_spherical(0,0,0),(0,0,0))
close(xyz_to_math_spherical(0,0,2),(2,0,0))
close(xyz_to_math_spherical(0,0,-2),(2,0,math.pi))
close(xyz_to_math_spherical(0,0,0),(0,0,0))
close(math_spherical_to_xyz(2,0,math.pi/2),(2,0,0))
close([shortest_turn(math.radians(179),math.radians(-179),math.pi/2,1/60)],[math.radians(-179.5)])
assert wrap_angle(-math.pi)==math.pi and wrap_angle(math.pi)==math.pi
rng=random.Random(704)
for _ in range(1000):
 r=rng.uniform(-100,100);h=rng.uniform(-20,20);p=rng.uniform(-20,20)
 xyz=book_spherical_to_xyz(r,h,p);r2,h2,p2=xyz_to_book_spherical(*xyz)
 close(book_spherical_to_xyz(r2,h2,p2),xyz)
 close(book_spherical_to_xyz(-r,h+math.pi,-p),xyz)
 close(book_spherical_to_xyz(r,h+math.pi,math.pi-p),xyz)
 x,y=polar_to_xy(r,h);cr,ca=canonical_polar(r,h);close(polar_to_xy(cr,ca),(x,y))
 xyz_math=math_spherical_to_xyz(r,h,p);close(math_spherical_to_xyz(*xyz_to_math_spherical(*xyz_math)),xyz_math)
report={'numericalExamplesPassed':True,'randomRoundTrips':1000,'poleOriginAndPiBoundaryPassed':True,'cameraOffsetVerified':[3.75,3.5,5*math.sqrt(3)/4],'angleUnits':'radians internally; degrees on lecture figures','bookConvention':'+x right,+y up,+z forward,positive pitch downward','hugeAngleCaveat':'Wrapping cannot restore precision already lost in an enormous floating-point input.'}
report['mathematicalSphericalInverseAndZenithPolesPassed']=True
Path(__file__).with_name('math-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
