"""Companion calculations. Internal angles are radians; figures label degrees.

Book game convention: +x right, +y up, +z forward; heading turns right,
positive pitch looks downward. This is a declared convention, not every engine.
"""
import math
def finite(*values):
 if not all(math.isfinite(v) for v in values):raise ValueError('Coordinates must be finite')
def wrap_angle(angle):
 finite(angle)
 result=math.remainder(angle,math.tau)
 return math.pi if result==-math.pi else result
def canonical_polar(radius,angle):
 finite(radius,angle)
 if radius==0:return 0.0,0.0
 if radius<0:radius=-radius;angle+=math.pi
 return radius,wrap_angle(angle)
def polar_to_xy(radius,angle):
 finite(radius,angle)
 return radius*math.cos(angle),radius*math.sin(angle)
def xy_to_polar(x,y):
 finite(x,y)
 radius=math.hypot(x,y)
 return (0.0,0.0) if radius==0 else (radius,wrap_angle(math.atan2(y,x)))
def cylindrical_to_xyz(radius,angle,height):
 x,y=polar_to_xy(radius,angle);finite(height)
 return x,y,height
def math_spherical_to_xyz(radius,azimuth,zenith):
 finite(radius,azimuth,zenith)
 horizontal=radius*math.sin(zenith)
 return horizontal*math.cos(azimuth),horizontal*math.sin(azimuth),radius*math.cos(zenith)
def book_spherical_to_xyz(radius,heading,pitch):
 finite(radius,heading,pitch)
 horizontal=radius*math.cos(pitch)
 return horizontal*math.sin(heading),-radius*math.sin(pitch),horizontal*math.cos(heading)

def xyz_to_math_spherical(x,y,z):
 finite(x,y,z);radius=math.hypot(x,y,z);horizontal=math.hypot(x,y)
 if radius==0:return 0.0,0.0,0.0
 azimuth=0.0 if horizontal==0 else wrap_angle(math.atan2(y,x))
 return radius,azimuth,math.atan2(horizontal,z)
def xyz_to_book_spherical(x,y,z):
 finite(x,y,z);radius=math.hypot(x,y,z);horizontal=math.hypot(x,z)
 if radius==0:return 0.0,0.0,0.0
 heading=0.0 if horizontal==0 else wrap_angle(math.atan2(x,z))
 return radius,heading,math.atan2(-y,horizontal)
def camera_position(center,radius,heading,pitch):
 finite(*center)
 return tuple(c+v for c,v in zip(center,book_spherical_to_xyz(radius,heading,pitch)))
def shortest_turn(current,target,max_speed,delta_time):
 finite(current,target,max_speed,delta_time)
 if max_speed<0 or delta_time<0:raise ValueError('Speed and elapsed time must be nonnegative')
 difference=wrap_angle(target-current);step=max_speed*delta_time
 return wrap_angle(current+max(-step,min(step,difference)))
