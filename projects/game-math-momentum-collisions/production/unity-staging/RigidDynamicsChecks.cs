using System;
using Yamyam.RigidTeaching;
class RigidDynamicsChecks {
    static int count;
    static void Near(double a,double b,double eps=1e-9){count++;if(Math.Abs(a-b)>eps||!Dynamics.Finite(a))throw new Exception("Mismatch "+a+" != "+b);}
    static void Near(D3 a,D3 b,double eps=1e-9){Near(a.x,b.x,eps);Near(a.y,b.y,eps);Near(a.z,b.z,eps);}
    static void Near(DMatrix a,DMatrix b,double eps=1e-9){Near(a.c0,b.c0,eps);Near(a.c1,b.c1,eps);Near(a.c2,b.c2,eps);}
    static Body Particle(double m,D3 v)=>new Body{inverseMass=1/m,velocity=v};
    static void Main(){
        Near(Dynamics.StickingVelocity(.01,new D3(350,0),2,new D3()).x,3.5/2.01);
        Near(Dynamics.Center(new[]{new MassPoint(1,new D3()),new MassPoint(3,new D3(4,0))}),new D3(3,0));
        Near(Dynamics.Impulse(new D3(10,0),.3),new D3(3,0));
        var floor=new Body();var ball=Particle(.05,new D3(-4,-4));
        var c=Dynamics.Resolve(floor,ball,new D3(),new D3(),new D3(1,3),.9);
        Near(c.multiplier,.152);Near(c.b.velocity,new D3(-.96,5.12));
        c=Dynamics.Resolve(floor,ball,new D3(),new D3(),new D3(1,3),.01);Near(c.multiplier,.0808);Near(c.b.velocity,new D3(-2.384,.848));
        for(int i=1;i<=100;i++){
            double ma=.1+i*.03,mb=.7+i*.05,e=(i%11)/10.0;D3 n=new D3(1,.7,-.2).Unit();
            var a=Particle(ma,new D3(4,.2,.5));var b=Particle(mb,new D3(-1,.3,.1));
            c=Dynamics.Resolve(a,b,new D3(),new D3(),n,e);if(!c.applied)throw new Exception("approach");
            Near(c.a.velocity*ma+c.b.velocity*mb,a.velocity*ma+b.velocity*mb);
            Near(D3.Dot(c.a.velocity-c.b.velocity,n),-e*D3.Dot(a.velocity-b.velocity,n));
            Near(D3.Cross(c.a.velocity-c.b.velocity,n),D3.Cross(a.velocity-b.velocity,n));
            var same=Dynamics.Resolve(a,b,new D3(),new D3(),n*3,e);Near(same.a.velocity,c.a.velocity);Near(same.b.velocity,c.b.velocity);
            var swap=Dynamics.Resolve(b,a,new D3(),new D3(),-n,e);Near(swap.a.velocity,c.b.velocity);Near(swap.b.velocity,c.a.velocity);
            double before=Dynamics.Energy(ma,a.velocity)+Dynamics.Energy(mb,b.velocity),after=Dynamics.Energy(ma,c.a.velocity)+Dynamics.Energy(mb,c.b.velocity);
            Near(before-after,.5*(1-e*e)/(1/ma+1/mb)*Math.Pow(D3.Dot(a.velocity-b.velocity,n),2),1e-8);
            var separating=Dynamics.Resolve(c.a,c.b,new D3(),new D3(),n,e);Near(separating.multiplier,0);
        }
        var kinematic=new Body{velocity=new D3(0,2)};c=Dynamics.Resolve(kinematic,Particle(1,new D3(0,-3)),new D3(),new D3(),new D3(0,1),1);Near(c.b.velocity,new D3(0,7));Near(c.a.velocity,kinematic.velocity);
        Near(Dynamics.BoxInertia(2,new D3(1,2,3)),DMatrix.Diagonal(26.0/12,20.0/12,10.0/12));
        Near(Dynamics.CylinderXInertia(50,.35,.2),DMatrix.Diagonal(3.0625,1.6979166666666667,1.6979166666666667));
        Near(Dynamics.ParallelAxis(DMatrix.Diagonal(.2,.2,.2),2,new D3(1,0)),DMatrix.Diagonal(.2,2.2,2.2));
        var bodyI=DMatrix.Diagonal(2,3,5);DQuaternion q=DQuaternion.AxisAngle(new D3(1,2,3),.7);var r=q.Matrix();Near(r*r.Transpose(),DMatrix.Identity);Near(r.Determinant,1);
        var worldI=Dynamics.WorldInertia(bodyI,q);Near(worldI*worldI.Inverse(),DMatrix.Identity);
        D3 w=new D3(1,2,3),torque=new D3(.3,1,-.5);D3 alpha=Dynamics.AngularAcceleration(worldI,w,torque);Near(worldI*alpha+D3.Cross(w,worldI*w),torque);
        var sphereI=Dynamics.SphereInertia(3,.4);Near(Dynamics.AngularAcceleration(sphereI,w,new D3()),new D3());
        D3 ra=new D3(0,1,0),rb=new D3(0,-.5,0),normal=new D3(1,0,0);
        var A=new Body{inverseMass=.5,velocity=new D3(2,0,0),omega=new D3(0,0,.2),inverseInertiaWorld=bodyI.Inverse()};
        var B=new Body{inverseMass=.25,velocity=new D3(-1,0,0),omega=new D3(0,0,-.3),inverseInertiaWorld=DMatrix.Diagonal(4,6,10).Inverse()};
        c=Dynamics.Resolve(A,B,ra,rb,normal,.6);Near(D3.Dot(c.a.PointVelocity(ra)-c.b.PointVelocity(rb),normal),-.6*c.approach);Near(c.a.velocity*2+c.b.velocity*4,A.velocity*2+B.velocity*4);
        // Total angular momentum about the shared contact: r points COM -> contact.
        Near(bodyI*c.a.omega+DMatrix.Diagonal(4,6,10)*c.b.omega+D3.Cross(-ra,c.a.velocity*2)+D3.Cross(-rb,c.b.velocity*4),bodyI*A.omega+DMatrix.Diagonal(4,6,10)*B.omega+D3.Cross(-ra,A.velocity*2)+D3.Cross(-rb,B.velocity*4));
        var q90=Dynamics.OrientationStep(DQuaternion.Identity,new D3(0,0,Math.PI/2),1);Near(q90.Rotate(new D3(1,0,0)),new D3(0,1,0));
        var qWorld=Dynamics.OrientationStep(q,new D3(.2,.3,-.1),.1,true);var qBody=Dynamics.OrientationStep(q,q.Matrix().Transpose()*new D3(.2,.3,-.1),.1,false);Near(qWorld.Matrix(),qBody.Matrix());
        var raw=Dynamics.MatrixEuler(DMatrix.Identity,new D3(0,0,1),.1);Near(raw.c0.Length,Math.Sqrt(1.01));Near(Dynamics.Orthonormalize(raw)*Dynamics.Orthonormalize(raw).Transpose(),DMatrix.Identity);
        foreach(var method in new[]{Integration.ExplicitEuler,Integration.SemiImplicitEuler,Integration.Midpoint,Integration.RungeKutta4}){
            var s=Dynamics.Integrate(new KinematicState(0,0),0,.1,(t,x,v)=>2,method);Near(s.velocity,.2);Near(s.position,method==Integration.ExplicitEuler?0:method==Integration.SemiImplicitEuler?.02:.01);
        }
        var oscillator=new KinematicState(1,0);for(int i=0;i<100;i++)oscillator=Dynamics.Integrate(oscillator,i*.01,.01,(t,x,v)=>-x,Integration.RungeKutta4);Near(oscillator.position,Math.Cos(1),1e-9);Near(oscillator.velocity,-Math.Sin(1),1e-9);
        foreach(double width in new[]{1.0,.1,.01}){Near(Dynamics.ImpulseRectangle(2,2,width,260)*width,260);Near(Dynamics.ImpulseRectangleIntegral(3,2,width,260)-Dynamics.ImpulseRectangleIntegral(1,2,width,260),260);}
        // Source truck table, SI units. No guessed commercial-game measurements.
        double[] masses={1000,600,400,50,50,50,50};D3[] centers={new D3(0,1,2.25),new D3(0,1.25,.75),new D3(0,1,-1.2),new D3(-1,.35,2.3),new D3(1,.35,2.3),new D3(-1,.35,-1.5),new D3(1,.35,-1.5)};
        var parts=new MassPoint[7];for(int i=0;i<7;i++)parts[i]=new MassPoint(masses[i],centers[i]);D3 com=Dynamics.Center(parts);Near(com,new D3(0,1.009090909090909,1.0454545454545454));
        var ii=new[]{DMatrix.Diagonal(240.83333333333334,520.8333333333334,386.66666666666674),DMatrix.Diagonal(197,312.5,284.5),DMatrix.Diagonal(213.33333333333334,325.3333333333333,154.66666666666669)};
        var truck=new DMatrix();for(int i=0;i<7;i++)truck+=Dynamics.ParallelAxis(i<3?ii[i]:Dynamics.CylinderXInertia(50,.35,.2),masses[i],centers[i]-com);
        Near(truck.c0.x,5110.689393939394);Near(truck.c1.y,5690.912878787878);Near(truck.c2.z,1154.4431818181822);Near(truck.c1.z,-39.59090909090912);Near(truck,truck.Transpose());
        Console.WriteLine(count+" independent dynamics invariants passed; no Unity/runtime/media approval");
    }
}
