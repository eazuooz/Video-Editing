using System;
namespace Yamyam.MathMechanics {
    [Serializable] public struct MVec {
        public double x,y,z;
        public MVec(double x,double y=0,double z=0){this.x=x;this.y=y;this.z=z;}
        public double Length=>Math.Sqrt(x*x+y*y+z*z);
        public static MVec operator +(MVec a,MVec b)=>new MVec(a.x+b.x,a.y+b.y,a.z+b.z);
        public static MVec operator -(MVec a,MVec b)=>new MVec(a.x-b.x,a.y-b.y,a.z-b.z);
        public static MVec operator -(MVec a)=>a*(-1);
        public static MVec operator *(MVec a,double s)=>new MVec(a.x*s,a.y*s,a.z*s);
        public static MVec operator /(MVec a,double s){if(s==0)throw new DivideByZeroException();return a*(1/s);}
        public static double Dot(MVec a,MVec b)=>a.x*b.x+a.y*b.y+a.z*b.z;
        public static MVec Cross(MVec a,MVec b)=>new MVec(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
        public MVec Unit(){double n=Length;if(n<1e-15)throw new ArgumentException("A zero vector has no direction");return this/n;}
    }
    public struct ScalarState {public double x,v,a;public ScalarState(double x,double v,double a){this.x=x;this.v=v;this.a=a;}}
    public struct FrictionState {public MVec friction,net;public bool sticking;public double normal,maximumStatic;}
    public static class MechanicsMathModel {
        public const double G=6.67430e-11;
        static void Positive(double x,string name){if(!(x>0)||double.IsInfinity(x))throw new ArgumentOutOfRangeException(name);}
        static void Nonnegative(double x,string name){if(!(x>=0)||double.IsInfinity(x))throw new ArgumentOutOfRangeException(name);}
        public static MVec Acceleration(MVec netForce,double mass){Positive(mass,nameof(mass));return netForce/mass;}
        public static MVec PairGravity(double massA,double massB,MVec fromAToB) {
            Positive(massA,nameof(massA));Positive(massB,nameof(massB));Positive(fromAToB.Length,"distance");
            return fromAToB.Unit()*(G*massA*massB/MVec.Dot(fromAToB,fromAToB));
        }
        // Contact normal points out of the support surface. Only external forces
        // on this selected body enter the sum; action/reaction partners do not.
        public static FrictionState SupportedFriction(MVec external,MVec outwardUnitNormal,MVec relativeVelocity,double muStatic,double muKinetic) {
            Nonnegative(muStatic,nameof(muStatic));Nonnegative(muKinetic,nameof(muKinetic));
            if(Math.Abs(outwardUnitNormal.Length-1)>1e-8)throw new ArgumentException("Contact normal must have unit length");
            double inward=MVec.Dot(external,outwardUnitNormal),n=Math.Max(0,-inward);
            MVec tangent=external-outwardUnitNormal*inward,slip=relativeVelocity-outwardUnitNormal*MVec.Dot(relativeVelocity,outwardUnitNormal);
            bool stationary=slip.Length<1e-9,stick=stationary&&tangent.Length<=muStatic*n;
            MVec friction;
            if(stick)friction=-tangent;
            else if(slip.Length>=1e-9)friction=slip.Unit()*(-muKinetic*n);
            else friction=tangent.Length>0?tangent.Unit()*(-muKinetic*n):new MVec();
            return new FrictionState{friction=friction,net=external+outwardUnitNormal*n+friction,normal=n,maximumStatic=muStatic*n,sticking=stick};
        }
        // Exact 1-D free slide with kinetic friction. Stop at v=0, never reverse
        // solely because a finite time step overshot the end of the slide.
        public static ScalarState FreeSlide(double initialVelocity,double deceleration,double t) {
            Nonnegative(deceleration,nameof(deceleration));Nonnegative(t,nameof(t));
            if(deceleration==0)return new ScalarState(initialVelocity*t,initialVelocity,0);
            double stop=Math.Abs(initialVelocity)/deceleration,used=Math.Min(t,stop),sign=Math.Sign(initialVelocity);
            return new ScalarState(initialVelocity*used-.5*sign*deceleration*used*used,t>=stop?0:initialVelocity-sign*deceleration*t,t>=stop?0:-sign*deceleration);
        }
        public static ScalarState DesignedJump(double height,double apexSeconds,double t) {
            Positive(height,nameof(height));Positive(apexSeconds,nameof(apexSeconds));Nonnegative(t,nameof(t));
            double v0=2*height/apexSeconds,a=-2*height/(apexSeconds*apexSeconds);
            return new ScalarState(v0*t+.5*a*t*t,v0+a*t,a);
        }
        public static MVec InAcceleratingFrame(MVec worldAcceleration,MVec frameAcceleration)=>worldAcceleration-frameAcceleration;
        public static double SpringForce(double displacement,double k){Positive(k,nameof(k));return -k*displacement;}
        public static double DampingForce(double velocity,double c){Nonnegative(c,nameof(c));return -c*velocity;}
        public static double NaturalFrequency(double mass,double k){Positive(mass,nameof(mass));Positive(k,nameof(k));return Math.Sqrt(k/mass);}
        public static double DampingRatio(double mass,double k,double c){Nonnegative(c,nameof(c));return c/(2*mass*NaturalFrequency(mass,k));}
        // Exact constant-coefficient homogeneous spring solution, fixed target.
        // A moving target must be split into explicit, documented held intervals.
        public static ScalarState Spring(double mass,double k,double c,double x0,double v0,double t) {
            double w=NaturalFrequency(mass,k),z=DampingRatio(mass,k,c);Nonnegative(t,nameof(t));double x,v;
            if(z<1-1e-9) {
                double decay=z*w,wd=w*Math.Sqrt(1-z*z),a=x0,b=(v0+decay*x0)/wd,cs=Math.Cos(wd*t),sn=Math.Sin(wd*t),e=Math.Exp(-decay*t);
                x=e*(a*cs+b*sn);v=e*((-decay*a+wd*b)*cs+(-decay*b-wd*a)*sn);
            } else if(z>1+1e-9) {
                double root=Math.Sqrt(z*z-1),r1=-w/(z+root),r2=-w*(z+root);
                double a=(v0-r2*x0)/(r1-r2),b=x0-a,e1=Math.Exp(r1*t),e2=Math.Exp(r2*t);
                x=a*e1+b*e2;v=r1*a*e1+r2*b*e2;
            } else {
                double b=v0+w*x0,e=Math.Exp(-w*t);x=(x0+b*t)*e;v=(b-w*(x0+b*t))*e;
            }
            return new ScalarState(x,v,(-k*x-c*v)/mass);
        }
        public static ScalarState SemiImplicitSpring(ScalarState previous,double target,double normalizedK,double normalizedC,double dt) {
            Positive(normalizedK,nameof(normalizedK));Nonnegative(normalizedC,nameof(normalizedC));Positive(dt,nameof(dt));
            double a=-normalizedK*(previous.x-target)-normalizedC*previous.v,v=previous.v+a*dt;
            return new ScalarState(previous.x+v*dt,v,a);
        }
        public static double FirstOrderLag(double value,double target,double lambda,double dt) {
            Positive(lambda,nameof(lambda));Nonnegative(dt,nameof(dt));return target+(value-target)*Math.Exp(-lambda*dt);
        }
        public static double SpringEnergy(double mass,double k,ScalarState s){Positive(mass,nameof(mass));Positive(k,nameof(k));return .5*mass*s.v*s.v+.5*k*s.x*s.x;}
        public static double Amplitude(double x0,double v0,double omega){Positive(omega,nameof(omega));return Math.Sqrt(x0*x0+v0*v0/(omega*omega));}
        public static double InitialPhase(double x0,double v0,double omega){Positive(omega,nameof(omega));if(x0==0&&v0==0)throw new ArgumentException("Equilibrium has no meaningful phase");return Math.Atan2(-v0/omega,x0);}
    }
}
