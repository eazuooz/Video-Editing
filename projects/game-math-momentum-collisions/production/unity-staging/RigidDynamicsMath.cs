using System;
using System.Collections.Generic;

namespace Yamyam.RigidTeaching {
    // Right-handed mathematical coordinates, column vectors, SI units.
    // Camera projection may flip z; physical formulas never inherit Unity's display convention.
    [Serializable] public struct D3 {
        public double x,y,z;
        public D3(double x,double y,double z=0){this.x=x;this.y=y;this.z=z;}
        public double Sqr=>x*x+y*y+z*z;
        public double Length=>Math.Sqrt(Sqr);
        public D3 Unit(){double m=Length;if(m<1e-12||!Dynamics.Finite(m))throw new ArgumentException("Nonzero finite direction required");return this/m;}
        public static D3 operator +(D3 a,D3 b)=>new D3(a.x+b.x,a.y+b.y,a.z+b.z);
        public static D3 operator -(D3 a,D3 b)=>new D3(a.x-b.x,a.y-b.y,a.z-b.z);
        public static D3 operator -(D3 a)=>a*-1;
        public static D3 operator *(D3 a,double k)=>new D3(a.x*k,a.y*k,a.z*k);
        public static D3 operator *(double k,D3 a)=>a*k;
        public static D3 operator /(D3 a,double k)=>a*(1/k);
        public static double Dot(D3 a,D3 b)=>a.x*b.x+a.y*b.y+a.z*b.z;
        public static D3 Cross(D3 a,D3 b)=>new D3(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
    }
    [Serializable] public struct DMatrix {
        public D3 c0,c1,c2;
        public DMatrix(D3 a,D3 b,D3 c){c0=a;c1=b;c2=c;}
        public static DMatrix Identity=>Diagonal(1,1,1);
        public static DMatrix Diagonal(double x,double y,double z)=>new DMatrix(new D3(x,0,0),new D3(0,y,0),new D3(0,0,z));
        public DMatrix Transpose()=>new DMatrix(new D3(c0.x,c1.x,c2.x),new D3(c0.y,c1.y,c2.y),new D3(c0.z,c1.z,c2.z));
        public double Determinant=>D3.Dot(c0,D3.Cross(c1,c2));
        public DMatrix Inverse(){double d=Determinant;if(Math.Abs(d)<1e-12||!Dynamics.Finite(d))throw new ArgumentException("Singular inertia is not an invertible body");return new DMatrix(D3.Cross(c1,c2)/d,D3.Cross(c2,c0)/d,D3.Cross(c0,c1)/d).Transpose();}
        public static D3 operator *(DMatrix a,D3 b)=>a.c0*b.x+a.c1*b.y+a.c2*b.z;
        public static DMatrix operator *(DMatrix a,DMatrix b)=>new DMatrix(a*b.c0,a*b.c1,a*b.c2);
        public static DMatrix operator *(DMatrix a,double k)=>new DMatrix(a.c0*k,a.c1*k,a.c2*k);
        public static DMatrix operator +(DMatrix a,DMatrix b)=>new DMatrix(a.c0+b.c0,a.c1+b.c1,a.c2+b.c2);
        public static DMatrix operator -(DMatrix a,DMatrix b)=>new DMatrix(a.c0-b.c0,a.c1-b.c1,a.c2-b.c2);
        public static DMatrix Outer(D3 a,D3 b)=>new DMatrix(a*b.x,a*b.y,a*b.z);
        public static DMatrix CrossMatrix(D3 w)=>new DMatrix(new D3(0,w.z,-w.y),new D3(-w.z,0,w.x),new D3(w.y,-w.x,0));
    }
    [Serializable] public struct DQuaternion {
        public double w,x,y,z;
        public DQuaternion(double w,double x,double y,double z){this.w=w;this.x=x;this.y=y;this.z=z;}
        public D3 Vector=>new D3(x,y,z);
        public double Sqr=>w*w+x*x+y*y+z*z;
        public static DQuaternion Identity=>new DQuaternion(1,0,0,0);
        public DQuaternion Unit(){double n=Math.Sqrt(Sqr);if(n<1e-12||!Dynamics.Finite(n))throw new ArgumentException("Invalid orientation");return this*(1/n);}
        public static DQuaternion operator *(DQuaternion a,DQuaternion b){D3 v=b.Vector*a.w+a.Vector*b.w+D3.Cross(a.Vector,b.Vector);return new DQuaternion(a.w*b.w-D3.Dot(a.Vector,b.Vector),v.x,v.y,v.z);}
        public static DQuaternion operator *(DQuaternion a,double k)=>new DQuaternion(a.w*k,a.x*k,a.y*k,a.z*k);
        public static DQuaternion operator +(DQuaternion a,DQuaternion b)=>new DQuaternion(a.w+b.w,a.x+b.x,a.y+b.y,a.z+b.z);
        public static DQuaternion AxisAngle(D3 axis,double radians){axis=axis.Unit();double s=Math.Sin(radians/2);return new DQuaternion(Math.Cos(radians/2),axis.x*s,axis.y*s,axis.z*s);}
        public D3 Rotate(D3 p){var q=Unit();D3 t=D3.Cross(q.Vector,p)*2;return p+t*q.w+D3.Cross(q.Vector,t);}
        public DMatrix Matrix(){return new DMatrix(Rotate(new D3(1,0,0)),Rotate(new D3(0,1,0)),Rotate(new D3(0,0,1)));}
    }
    [Serializable] public struct MassPoint {public double mass;public D3 position;public MassPoint(double m,D3 p){mass=m;position=p;}}
    [Serializable] public struct Body {
        public D3 position,velocity,omega;
        public double inverseMass;
        public DMatrix inverseInertiaWorld;
        public D3 PointVelocity(D3 r)=>velocity+D3.Cross(omega,r);
    }
    public struct ContactResult {public Body a,b;public double approach,multiplier,denominator;public D3 impulseOnB;public bool applied;}
    public struct KinematicState {public double position,velocity;public KinematicState(double p,double v){position=p;velocity=v;}}
    public enum Integration {ExplicitEuler,SemiImplicitEuler,Midpoint,RungeKutta4}
    public static class Dynamics {
        public static bool Finite(double x)=>!double.IsInfinity(x)&&!double.IsNaN(x);
        static void Positive(double x,string name){if(!Finite(x)||x<=0)throw new ArgumentOutOfRangeException(name);}
        public static D3 Momentum(double mass,D3 velocity){Positive(mass,"mass");return velocity*mass;}
        public static D3 Impulse(D3 force,double duration){if(duration<0||!Finite(duration))throw new ArgumentOutOfRangeException("duration");return force*duration;}
        public static double Energy(double m,D3 v){Positive(m,"mass");return .5*m*v.Sqr;}
        public static D3 Center(IList<MassPoint> points){double m=0;D3 sum=new D3();foreach(var p in points){Positive(p.mass,"mass");m+=p.mass;sum+=p.position*p.mass;}Positive(m,"total mass");return sum/m;}
        public static D3 StickingVelocity(double ma,D3 va,double mb,D3 vb){Positive(ma,"mass A");Positive(mb,"mass B");return (va*ma+vb*mb)/(ma+mb);}
        public static DMatrix PointInertia(double mass,D3 r){Positive(mass,"mass");return (DMatrix.Identity*r.Sqr-DMatrix.Outer(r,r))*mass;}
        public static DMatrix CombinedInertia(IList<MassPoint> points,D3 origin){var sum=new DMatrix();foreach(var p in points)sum+=PointInertia(p.mass,p.position-origin);return sum;}
        public static DMatrix BoxInertia(double m,D3 side){Positive(m,"mass");Positive(side.x,"x");Positive(side.y,"y");Positive(side.z,"z");return DMatrix.Diagonal(m*(side.y*side.y+side.z*side.z)/12,m*(side.x*side.x+side.z*side.z)/12,m*(side.x*side.x+side.y*side.y)/12);}
        public static DMatrix SphereInertia(double m,double radius){Positive(m,"mass");Positive(radius,"radius");double k=.4*m*radius*radius;return DMatrix.Diagonal(k,k,k);}
        public static DMatrix CylinderXInertia(double m,double radius,double length){Positive(m,"mass");Positive(radius,"radius");Positive(length,"length");double transverse=m*(3*radius*radius+length*length)/12;return DMatrix.Diagonal(.5*m*radius*radius,transverse,transverse);}
        public static DMatrix ParallelAxis(DMatrix centerInertia,double m,D3 displacement)=>centerInertia+PointInertia(m,displacement);
        public static DMatrix WorldInertia(DMatrix body,DQuaternion orientation){DMatrix r=orientation.Matrix();return r*body*r.Transpose();}
        public static D3 AngularAcceleration(DMatrix inertiaWorld,D3 omega,D3 torque)=>inertiaWorld.Inverse()*(torque-D3.Cross(omega,inertiaWorld*omega));
        // Normal points A -> B. Positive dot(vA-vB,n) means approaching.
        // Non-unit n is supported; multiplier is not impulse magnitude unless |n|=1.
        public static ContactResult Resolve(Body a,Body b,D3 rA,D3 rB,D3 normal,double restitution){
            if(restitution<0||restitution>1||!Finite(restitution))throw new ArgumentOutOfRangeException("restitution");
            if(normal.Sqr<1e-16||!Finite(normal.Sqr)||a.inverseMass<0||b.inverseMass<0)throw new ArgumentException("Invalid contact");
            var q=new ContactResult{a=a,b=b};q.approach=D3.Dot(a.PointVelocity(rA)-b.PointVelocity(rB),normal);
            D3 ca=D3.Cross(rA,normal),cb=D3.Cross(rB,normal);
            q.denominator=(a.inverseMass+b.inverseMass)*normal.Sqr+D3.Dot(ca,a.inverseInertiaWorld*ca)+D3.Dot(cb,b.inverseInertiaWorld*cb);
            if(q.approach<=0||q.denominator<=1e-15)return q;
            q.multiplier=(1+restitution)*q.approach/q.denominator;q.impulseOnB=normal*q.multiplier;q.applied=true;
            q.a.velocity-=q.impulseOnB*a.inverseMass;q.b.velocity+=q.impulseOnB*b.inverseMass;
            q.a.omega-=a.inverseInertiaWorld*D3.Cross(rA,q.impulseOnB);q.b.omega+=b.inverseInertiaWorld*D3.Cross(rB,q.impulseOnB);return q;
        }
        public static D3 SeparatePosition(D3 normal,double depth,double slop,double invMass,double otherInvMass){
            if(depth<0||slop<0||invMass<0||otherInvMass<0)throw new ArgumentOutOfRangeException();
            double sum=invMass+otherInvMass;return sum>0?normal.Unit()*(Math.Max(0,depth-slop)*invMass/sum):new D3();
        }
        public static DQuaternion OrientationStep(DQuaternion q,D3 omega,double dt,bool world=true,bool exponential=true){
            if(dt<0||!Finite(dt))throw new ArgumentOutOfRangeException("dt");
            if(omega.Length<1e-12)return q.Unit();
            if(exponential){var dq=DQuaternion.AxisAngle(omega,omega.Length*dt);return (world?dq*q:q*dq).Unit();}
            var wq=new DQuaternion(0,omega.x,omega.y,omega.z);return (q+(world?wq*q:q*wq)*(.5*dt)).Unit();
        }
        public static DMatrix MatrixEuler(DMatrix r,D3 omegaWorld,double dt)=>r+(DMatrix.CrossMatrix(omegaWorld)*r)*dt;
        public static DMatrix Orthonormalize(DMatrix r){D3 x=r.c0.Unit(),y=(r.c1-x*D3.Dot(x,r.c1)).Unit();return new DMatrix(x,y,D3.Cross(x,y));}
        public static KinematicState Integrate(KinematicState s,double time,double dt,Func<double,double,double,double> acceleration,Integration method){
            if(dt<0||!Finite(dt))throw new ArgumentOutOfRangeException("dt");double a=acceleration(time,s.position,s.velocity);
            if(method==Integration.ExplicitEuler)return new KinematicState(s.position+s.velocity*dt,s.velocity+a*dt);
            if(method==Integration.SemiImplicitEuler){double v=s.velocity+a*dt;return new KinematicState(s.position+v*dt,v);}
            if(method==Integration.Midpoint){double vm=s.velocity+a*dt/2;double am=acceleration(time+dt/2,s.position+s.velocity*dt/2,vm);return new KinematicState(s.position+vm*dt,s.velocity+am*dt);}
            double k1x=s.velocity,k1v=a,k2x=s.velocity+k1v*dt/2,k2v=acceleration(time+dt/2,s.position+k1x*dt/2,k2x);
            double k3x=s.velocity+k2v*dt/2,k3v=acceleration(time+dt/2,s.position+k2x*dt/2,k3x);
            double k4x=s.velocity+k3v*dt,k4v=acceleration(time+dt,s.position+k3x*dt,k4x);
            return new KinematicState(s.position+dt*(k1x+2*k2x+2*k3x+k4x)/6,s.velocity+dt*(k1v+2*k2v+2*k3v+k4v)/6);
        }
        // Finite rectangle approximation; no attempt to evaluate delta(0).
        public static double ImpulseRectangle(double time,double center,double width,double area){Positive(width,"width");return time>=center-width/2&&time<center+width/2?area/width:0;}
        public static double ImpulseRectangleIntegral(double time,double center,double width,double area){Positive(width,"width");return area*Math.Max(0,Math.Min(1,(time-center+width/2)/width));}
    }
}
