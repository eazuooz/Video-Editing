using System;
namespace Yamyam.MathMechanics {
    public static class MechanicsMathChecks {
        static int count;
        static void Near(string name,double actual,double expected,double tolerance=1e-8){count++;if(double.IsNaN(actual)||Math.Abs(actual-expected)>tolerance)throw new Exception(name+": "+actual+" expected "+expected);}
        static void True(string name,bool value){count++;if(!value)throw new Exception(name);}
        public static int Main() {
            Near("F=6-2, m=2",MechanicsMathModel.Acceleration(new MVec(6)-new MVec(2),2).x,2);
            var f=MechanicsMathModel.SupportedFriction(new MVec(2,-10),new MVec(0,1),new MVec(),.5,.3);
            Near("static friction follows demand",f.friction.x,-2);Near("zero net",f.net.Length,0);Near("limit is not actual force",f.maximumStatic,5);True("sticks",f.sticking);
            f=MechanicsMathModel.SupportedFriction(new MVec(6,-10),new MVec(0,1),new MVec(),.5,.3);
            Near("breakaway uses kinetic",f.friction.x,-3);Near("breakaway net",f.net.x,3);True("slides",!f.sticking);
            double theta=Math.Atan(.5),mass=2,g=9.8;var normal=new MVec(-Math.Sin(theta),Math.Cos(theta));
            f=MechanicsMathModel.SupportedFriction(new MVec(0,-mass*g),normal,new MVec(),.5000001,.3);True("threshold sticks",f.sticking);Near("incline support",f.normal,mass*g*Math.Cos(theta));Near("incline net",f.net.Length,0);
            var slide=MechanicsMathModel.FreeSlide(4,2,3);Near("slide stops at 4m",slide.x,4);Near("no reverse",slide.v,0);
            var j=MechanicsMathModel.DesignedJump(2,.4,.4);Near("designed height",j.x,2);Near("apex zero speed",j.v,0);Near("designed acceleration",j.a,-25);
            var ga=MechanicsMathModel.PairGravity(3,5,new MVec(2));var gb=MechanicsMathModel.PairGravity(3,5,new MVec(4));Near("inverse square",ga.Length/gb.Length,4);
            Near("freefall relative",MechanicsMathModel.InAcceleratingFrame(new MVec(0,-g),new MVec(0,-g)).Length,0);
            Near("Hooke example",MechanicsMathModel.SpringForce(.1,20),-2);Near("natural omega",MechanicsMathModel.NaturalFrequency(1,16),4);Near("zeta",MechanicsMathModel.DampingRatio(1,16,4),.5);
            Near("signed initial phase",MechanicsMathModel.InitialPhase(0,2,2),-Math.PI/2);Near("phase amplitude",MechanicsMathModel.Amplitude(0,2,2),1);
            var code=MechanicsMathModel.SemiImplicitSpring(new ScalarState(0,0,0),1,16,4,.1);Near("code acceleration",code.a,16);Near("new velocity",code.v,1.6);Near("new position",code.x,.16);
            Near("first order example",MechanicsMathModel.FirstOrderLag(0,1,2,.5),1-Math.Exp(-1));
            // Differential-equation residuals and initial states across all regimes.
            foreach(double z in new[]{0.0,.1,.5,.999,1.0,1.001,1.5,4.0}) {
                double c=2*z*4;var initial=MechanicsMathModel.Spring(1,16,c,.8,-1.3,0);Near("initial x",initial.x,.8);Near("initial v",initial.v,-1.3);
                double previousEnergy=MechanicsMathModel.SpringEnergy(1,16,initial);
                for(int i=1;i<=150;i++) {
                    double t=i*.02,h=1e-5;var a=MechanicsMathModel.Spring(1,16,c,.8,-1.3,t-h);var s=MechanicsMathModel.Spring(1,16,c,.8,-1.3,t);var b=MechanicsMathModel.Spring(1,16,c,.8,-1.3,t+h);
                    Near("x derivative",(b.x-a.x)/(2*h),s.v,2e-7);Near("v derivative",(b.v-a.v)/(2*h),s.a,3e-6);
                    double energy=MechanicsMathModel.SpringEnergy(1,16,s);True("non-increasing energy",energy<=previousEnergy+1e-9);previousEnergy=energy;
                    if(z==0)Near("conserved undamped energy",energy,.5*1.3*1.3+.5*16*.8*.8);
                }
            }
            var critical=MechanicsMathModel.Spring(1,16,8,1,-10,1.0/6);Near("critical one crossing",critical.x,0);True("critical can overshoot once",MechanicsMathModel.Spring(1,16,8,1,-10,.2).x<0);
            Console.WriteLine("PASS "+count+" numeric checks; no Unity runtime/visual approval.");return 0;
        }
    }
}
