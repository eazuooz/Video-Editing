using System;
namespace Yamyam.MathMotion {
    public static class MotionMathChecks {
        static int count;
        static void Near(string name,double actual,double expected,double tolerance=1e-8) {count++;if(Math.Abs(actual-expected)>tolerance)throw new Exception(name+": "+actual+" != "+expected);}
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
            Console.WriteLine("PASS "+count+" numerical/model invariants. No Unity runtime or visual QA.");return 0;
        }
    }
}
