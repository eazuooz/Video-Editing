using System;
namespace Yamyam.MathMotion {
    public static class MotionMathChecks {
        static int count;
        static void Near(string name,double actual,double expected,double tolerance=1e-8) {count++;if(double.IsNaN(actual)||double.IsInfinity(actual)||Math.Abs(actual-expected)>tolerance)throw new Exception(name+": "+actual+" != "+expected);}
        static void True(string name,bool result){count++;if(!result)throw new Exception(name);}
        public static int Main() {
            var p=new MotionParameters();var state=MotionMathModel.Sample(p,2.5);Near("x2.5",state.position.x,7.75);Near("v2.5",state.velocity.x,1);Near("secant",MotionMathModel.SecantVelocity(p,2.5,.001).x,.999);
            foreach(int n in new[]{6,12,24})Near("Riemann"+n,MotionMathModel.LeftRiemannLinear(0,32,2.4,n),92.16*(1-1.0/n));
            p.kind=MotionKind.DesignedJump;p.jumpHeight=2;p.timeToApex=1;p.horizontalSpeed=3;state=MotionMathModel.Sample(p,1);Near("jump apex",state.position.y,2);Near("jump apex v",state.velocity.y,0);Near("jump range",MotionMathModel.Sample(p,2).position.x,6);Near("jump same height",MotionMathModel.Sample(p,2).position.y,0);
            p.kind=MotionKind.Circle;p.radius=2;p.omega=3;p.axis=new DVec(0,0,1);p.radiusDirection=new DVec(1,0,0);
            for(int i=0;i<16;i++) {state=MotionMathModel.Sample(p,i*.13);Near("circle speed",state.velocity.Length,6);Near("circle acceleration",state.acceleration.Length,18);Near("circle tangent",DVec.Dot(state.position-p.origin,state.velocity),0);Near("inverse omega",MotionMathModel.RecoverPerpendicularAngularVelocity(state.position-p.origin,state.velocity).z,3);}
            p.kind=MotionKind.PiecewiseExercise;True("join undefined",!MotionMathModel.Sample(p,4).velocityDefined);Near("exercisev",MotionMathModel.Sample(p,4.1).velocity.x,2.98783216474156);Near("exercisea",MotionMathModel.Sample(p,6.5).acceleration.x,-Math.PI*Math.PI);
            p.kind=MotionKind.ChainSlope;p.chainSlope=.25;p.pathSpeed=4;state=MotionMathModel.Sample(p,1);Near("chain vertical",state.velocity.y,1);Near("chain arclength",state.velocity.Length,4);
            var a=new DVec(0,-4);var v=new DVec(3,4);var target=new DVec(6,0);var roots=MotionMathModel.ProjectedArrivalTimes(target,v,a);True("root0 fails full target",!MotionMathModel.ReachesTarget(target,v,a,roots[0]));True("root2 reaches",MotionMathModel.ReachesTarget(target,v,a,roots[1]));
            var r=new DVec(1,0,0);var omega=new DVec(9,0,3);var recovered=MotionMathModel.RecoverPerpendicularAngularVelocity(r,DVec.Cross(omega,r));Near("parallel unobservable",recovered.x,0);Near("perp retained",recovered.z,3);
            foreach(var kind in new[]{MotionKind.Sine,MotionKind.Cosine,MotionKind.Exponential,MotionKind.Power,MotionKind.SineSquared,MotionKind.ExpCosLinear,MotionKind.ExpSineSum,MotionKind.LogAbsolute}){
                p=new MotionParameters{kind=kind,amplitude=1.3,frequency=3,power=3,rate=.4};
                foreach(double t in new[]{.1,.4,.7,1.0}){
                    const double h=1e-5;var left=MotionMathModel.Sample(p,t-h);var mid=MotionMathModel.Sample(p,t);var right=MotionMathModel.Sample(p,t+h);
                    Near(kind+" first derivative",mid.velocity.x,(right.position.x-left.position.x)/(2*h),2e-6);
                    Near(kind+" second derivative",mid.acceleration.x,(right.velocity.x-left.velocity.x)/(2*h),2e-5);
                }
            }
            p=new MotionParameters{kind=MotionKind.RoundTrip};Near("roundtrip start",MotionMathModel.Sample(p,0).position.x,0);Near("roundtrip end",MotionMathModel.Sample(p,4).position.x,0);Near("roundtrip turn",MotionMathModel.Sample(p,2).position.x,6);True("turn derivative undefined",!MotionMathModel.Sample(p,2).velocityDefined);
            p=new MotionParameters{kind=MotionKind.PowerSum,powers=new[]{1.0,3,5,7},coefficients=new[]{1.0,-1.0/6,1.0/120,-1.0/5040}};Near("four sine terms",MotionMathModel.Sample(p,.5).position.x,.479425533234127,1e-12);Near("series derivative at zero",MotionMathModel.Sample(p,0).velocity.x,1);
            p=new MotionParameters{kind=MotionKind.RacePath};Near("race shared start",MotionMathModel.Sample(p,0).position.x,0);Near("race shared end",MotionMathModel.Sample(p,6).position.x,12);Near("race rests",MotionMathModel.Sample(p,3).velocity.x,0);Near("race goes back",MotionMathModel.Sample(p,1.5).velocity.x,-2);
            p=new MotionParameters{kind=MotionKind.AccelerationStep};True("step continuous velocity",MotionMathModel.Sample(p,1).velocityDefined);True("step acceleration undefined",!MotionMathModel.Sample(p,1).accelerationDefined);Near("step left slope",MotionMathModel.Sample(p,1-1e-8).velocity.x,2);Near("step right slope",MotionMathModel.Sample(p,1+1e-8).velocity.x,2,3e-8);
            p=new MotionParameters{kind=MotionKind.ConstantAcceleration,acceleration=new DVec(0,32),velocity=new DVec()};Near("general left rectangles",MotionMathModel.RiemannDisplacement(p,0,2.4,6,0,true),76.8);Near("general midpoint rectangles",MotionMathModel.RiemannDisplacement(p,0,2.4,6,.5,true),92.16);Near("general right rectangles",MotionMathModel.RiemannDisplacement(p,0,2.4,6,1,true),107.52);
            foreach(int n in new[]{6,12,24})Near("rectangles same analytic fall "+n,MotionMathModel.RiemannDisplacement(p,0,2.4,n,0,true),92.16*(1-1.0/n));
            double arrival=Math.Sqrt(2*1353.0/32);Near("1353ft arrival",MotionMathModel.Sample(p,arrival).position.y,1353);Near("1353ft speed",MotionMathModel.Sample(p,arrival).velocity.y,294.265186524,1e-8);
            p.velocity=new DVec(0,-79.25);Near("designed 12s arrival",MotionMathModel.Sample(p,12).position.y,1353);Near("apex derivative",MotionMathModel.Sample(p,79.25/32).velocity.y,0);Near("return height",MotionMathModel.Sample(p,79.25/16).position.y,0);
            p=new MotionParameters{kind=MotionKind.PowerSum,powers=new[]{2.0,0},coefficients=new[]{1.0,30}};Near("FTC displacement",MotionMathModel.Sample(p,3).position.x-MotionMathModel.Sample(p,1).position.x,8);
            p=new MotionParameters{kind=MotionKind.DesignedJump,jumpHeight=2,timeToApex=1,horizontalSpeed=3};Near("same height first time",MotionMathModel.Sample(p,.5).position.y,1.5);Near("same height second time",MotionMathModel.Sample(p,1.5).position.y,1.5);True("height is not target point",!MotionMathModel.ReachesTarget(new DVec(4,1.5),new DVec(3,4),new DVec(0,-4),1.5));
            Console.WriteLine("PASS "+count+" numerical/model invariants. No Unity runtime or visual QA.");return 0;
        }
    }
}
