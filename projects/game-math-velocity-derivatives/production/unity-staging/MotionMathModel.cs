using System;

namespace Yamyam.MathMotion {
    // Analytic teaching models, not measurements or physics claims about any game.
    [Serializable] public struct DVec {
        public double x,y,z;
        public DVec(double x,double y,double z=0) { this.x=x;this.y=y;this.z=z; }
        public double Length => Math.Sqrt(Dot(this,this));
        public static DVec operator +(DVec a,DVec b)=>new DVec(a.x+b.x,a.y+b.y,a.z+b.z);
        public static DVec operator -(DVec a,DVec b)=>new DVec(a.x-b.x,a.y-b.y,a.z-b.z);
        public static DVec operator *(DVec a,double s)=>new DVec(a.x*s,a.y*s,a.z*s);
        public static DVec operator /(DVec a,double s)=>a*(1/s);
        public static double Dot(DVec a,DVec b)=>a.x*b.x+a.y*b.y+a.z*b.z;
        public static DVec Cross(DVec a,DVec b)=>new DVec(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
        public static DVec Normalize(DVec v) { if(v.Length<1e-12)throw new ArgumentException("A zero vector has no unit direction.");return v/v.Length; }
    }
    public enum MotionKind { Polynomial, ConstantVelocity, ConstantAcceleration, DesignedJump, Circle, PiecewiseExercise, ChainSlope }
    [Serializable] public class MotionParameters {
        public MotionKind kind=MotionKind.Polynomial;
        public DVec origin=new DVec(0,0),velocity=new DVec(3,0),acceleration=new DVec(0,-4);
        public double quadratic=-1,linear=6,constant=-1;
        public double radius=2,omega=1,theta0=0;
        public DVec axis=new DVec(0,0,1),radiusDirection=new DVec(1,0,0);
        public double jumpHeight=2,timeToApex=1,horizontalSpeed=3;
        public double chainSlope=.25,pathSpeed=4;
    }
    public struct MotionState {
        public double time;
        public DVec position,velocity,acceleration;
        public bool velocityDefined,accelerationDefined;
        public MotionState(double t,DVec p,DVec v,DVec a,bool valid=true) {
            time=t;position=p;velocity=v;acceleration=a;velocityDefined=accelerationDefined=valid;
        }
    }
    public static class MotionMathModel {
        public static void Validate(MotionParameters p) {
            if(p==null)throw new ArgumentNullException(nameof(p));
            if(p.kind==MotionKind.Circle && (p.radius<=0 || p.axis.Length<1e-12 || DVec.Cross(p.axis,p.radiusDirection).Length<1e-12))
                throw new ArgumentException("Circle requires positive radius and an axis with a nonparallel radius direction.");
            if(p.kind==MotionKind.DesignedJump && (p.jumpHeight<=0 || p.timeToApex<=0))throw new ArgumentException("Jump H and apex T must be positive.");
            if(p.kind==MotionKind.ChainSlope && Math.Abs(p.chainSlope)>1)throw new ArgumentException("dy/ds for arc length cannot exceed one in magnitude.");
        }
        public static MotionState Sample(MotionParameters p,double t) {
            Validate(p);
            if(double.IsNaN(t)||double.IsInfinity(t))throw new ArgumentOutOfRangeException(nameof(t));
            switch(p.kind) {
                case MotionKind.Polynomial:
                    return new MotionState(t,p.origin+new DVec(p.quadratic*t*t+p.linear*t+p.constant,0),new DVec(2*p.quadratic*t+p.linear,0),new DVec(2*p.quadratic,0));
                case MotionKind.ConstantVelocity:
                    return new MotionState(t,p.origin+p.velocity*t,p.velocity,new DVec());
                case MotionKind.ConstantAcceleration:
                    return new MotionState(t,p.origin+p.velocity*t+p.acceleration*(.5*t*t),p.velocity+p.acceleration*t,p.acceleration);
                case MotionKind.DesignedJump:
                    double g=2*p.jumpHeight/(p.timeToApex*p.timeToApex),vy=2*p.jumpHeight/p.timeToApex;
                    return new MotionState(t,p.origin+new DVec(p.horizontalSpeed*t,vy*t-.5*g*t*t),new DVec(p.horizontalSpeed,vy-g*t),new DVec(0,-g));
                case MotionKind.Circle:
                    DVec n=DVec.Normalize(p.axis);
                    DVec e1=DVec.Normalize(p.radiusDirection-n*DVec.Dot(n,p.radiusDirection));
                    DVec e2=DVec.Cross(n,e1);
                    double angle=p.theta0+p.omega*t;
                    DVec r=(e1*Math.Cos(angle)+e2*Math.Sin(angle))*p.radius;
                    return new MotionState(t,p.origin+r,DVec.Cross(n*p.omega,r),r*(-p.omega*p.omega));
                case MotionKind.PiecewiseExercise:
                    if(t<0)throw new ArgumentOutOfRangeException(nameof(t),"Exercise time domain begins at zero.");
                    bool interior=Math.Abs(t-2)>1e-10&&Math.Abs(t-4)>1e-10&&Math.Abs(t-7)>1e-10;
                    double x,v,a;
                    if(t<2) { x=2*t-t*t;v=2-2*t;a=-2; }
                    else if(t<4) { x=v=a=0; }
                    else if(t<7) { x=Math.Sin(Math.PI*t);v=Math.PI*Math.Cos(Math.PI*t);a=-Math.PI*Math.PI*Math.Sin(Math.PI*t); }
                    else { x=7-t;v=-1;a=0; }
                    var state=new MotionState(t,p.origin+new DVec(x,0),new DVec(v,0),new DVec(a,0),interior);
                    // t=0 has a right derivative only; do not advertise a two-sided derivative.
                    if(t==0)state.velocityDefined=state.accelerationDefined=false;
                    return state;
                case MotionKind.ChainSlope:
                    double slope=p.chainSlope;
                    DVec tangent=new DVec(Math.Sqrt(Math.Max(0,1-slope*slope)),slope);
                    return new MotionState(t,p.origin+tangent*(p.pathSpeed*t),tangent*p.pathSpeed,new DVec());
                default:throw new ArgumentOutOfRangeException();
            }
        }
        public static DVec SecantVelocity(MotionParameters p,double t,double h) {
            if(h==0)throw new ArgumentException("Secant interval must be nonzero; h=0 is not an evaluation of the derivative.");
            return (Sample(p,t+h).position-Sample(p,t).position)/h;
        }
        public static double LeftRiemannLinear(double v0,double a,double duration,int count) {
            if(count<=0||duration<0)throw new ArgumentOutOfRangeException();
            double dt=duration/count,total=0;
            for(int k=0;k<count;k++)total+=(v0+a*k*dt)*dt;
            return total;
        }
        public static double[] ProjectedArrivalTimes(DVec displacement,DVec velocity,DVec acceleration) {
            double A=DVec.Dot(acceleration,acceleration),B=DVec.Dot(velocity,acceleration),D=DVec.Dot(displacement,acceleration);
            if(A<1e-20)throw new ArgumentException("Zero acceleration needs the constant-velocity case, not division by A.");
            double disc=B*B+2*A*D;
            if(disc<0)return Array.Empty<double>();
            if(disc==0)return new[]{-B/A};
            return new[]{(-B-Math.Sqrt(disc))/A,(-B+Math.Sqrt(disc))/A};
        }
        public static bool ReachesTarget(DVec delta,DVec v,DVec a,double t,double tolerance=1e-8)=>t>=0&&(v*t+a*(.5*t*t)-delta).Length<=tolerance;
        public static DVec RecoverPerpendicularAngularVelocity(DVec r,DVec v) {
            double rr=DVec.Dot(r,r);if(rr<1e-20)throw new ArgumentException("Angular velocity at zero radius is undefined.");
            return DVec.Cross(r,v)/rr;
        }
    }
}
