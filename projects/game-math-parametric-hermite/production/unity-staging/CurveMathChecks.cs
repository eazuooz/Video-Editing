using System;
using Yamyam.MathCurves;
public static class CurveMathChecks {
    static int checks;
    static void Check(bool ok,string name){checks++;if(!ok)throw new Exception(name);}
    static void Near(double a,double b,string n,double e=1e-8){Check(!double.IsNaN(a)&&Math.Abs(a-b)<=e,n+": "+a+" != "+b);}
    static void Vec(CVec a,CVec b,string n){Near((a-b).Length,0,n);}
    static void Throws(Action a,string n){bool caught=false;try{a();}catch(ArgumentException){caught=true;}Check(caught,n);}
    public static void Main(){
        var b=new[]{new CVec(3,5),new CVec(6,1),new CVec(0,3),new CVec(5,5)};
        Vec(CurveMathModel.Bezier(b,.4),new CVec(3.56,2.696),"M33 worked position");
        Vec(CurveMathModel.BezierSample(b,.4).d1,new CVec(-3,-.48),"M33 worked derivative");
        var c=CurveMathModel.BezierPower(b);var expected=new[]{new CVec(3,5),new CVec(9,-12),new CVec(-27,18),new CVec(20,-6)};
        for(int i=0;i<4;i++){Vec(c[i],expected[i],"Power coefficient"+i);Vec(CurveMathModel.PowerBezier(c)[i],b[i],"Inverse coefficient"+i);}
        var hermite=CurveMathModel.HermitePower(new CVec(0,0),new CVec(0,3),new CVec(0,-3),new CVec(2,0));
        Vec(CurveMathModel.Power(hermite,.5),new CVec(1,.75),"M31 arch midpoint");
        Vec(CurveMathModel.PowerSample(hermite,0).d1,new CVec(0,3),"Hermite departure");
        Vec(CurveMathModel.PowerSample(hermite,1).d1,new CVec(0,-3),"Hermite arrival");
        double[] nodes={0,1.0/3,2.0/3,1};var samples=new[]{new CVec(0,2),new CVec(1,3),new CVec(2,2),new CVec(3,3)};
        for(int k=0;k<4;k++){var w=CurveMathModel.LagrangeWeights(nodes,nodes[k]);for(int j=0;j<4;j++)Near(w[j],j==k?1:0,"Lagrange cardinal"+k+"/"+j);}
        for(int i=0;i<=100;i++){
            double t=i/100.0;var l=CurveMathModel.Lagrange(nodes,samples,t);var a=CurveMathModel.Aitken(nodes,samples,t);
            Vec(l,a[3][0],"Aitken/Lagrange agree");Near(l.y,18*t*t*t-27*t*t+10*t+2,"Worked S polynomial");
            Vec(CurveMathModel.Power(c,t),CurveMathModel.Bezier(b,t),"Power/Bezier same curve");
            var weights=CurveMathModel.Bernstein(3,t);double sum=0;foreach(double x in weights){Check(x>=0,"Bernstein positivity");sum+=x;}Near(sum,1,"Partition unity");
        }
        Check(CurveMathModel.Lagrange(nodes,samples,.25).y>3,"Expected S overshoot, not hidden by clamping");
        var pieces=CurveMathModel.Split(b,.5);Vec(pieces[0][3],new CVec(3.25,2.75),"Split join worked value");
        var extracted=CurveMathModel.Subcurve(b,.2,.5);var eControls=new[]{new CVec(3.88,3.272),new CVec(3.94,2.72),new CVec(3.55,2.6),new CVec(3.25,2.75)};
        for(int i=0;i<4;i++)Vec(extracted[i],eControls[i],"Extracted control"+i);
        var elevated=CurveMathModel.Elevate(b);var eExpected=new[]{b[0],new CVec(5.25,2),new CVec(3,2),new CVec(1.25,3.5),b[3]};
        for(int i=0;i<5;i++)Vec(elevated[i],eExpected[i],"Elevated control"+i);
        for(int i=0;i<=100;i++){
            double u=i/100.0;Vec(CurveMathModel.Bezier(extracted,u),CurveMathModel.Bezier(b,.2+.3*u),"Subcurve geometry");
            Vec(CurveMathModel.BezierSample(extracted,u).d1,CurveMathModel.BezierSample(b,.2+.3*u).d1*.3,"Subcurve derivative scale");
            Vec(CurveMathModel.Bezier(pieces[0],u),CurveMathModel.Bezier(b,.5*u),"Left split");
            Vec(CurveMathModel.Bezier(pieces[1],u),CurveMathModel.Bezier(b,.5+.5*u),"Right split");
            Vec(CurveMathModel.Bezier(elevated,u),CurveMathModel.Bezier(b,u),"Elevation preserves curve");
        }
        Vec(CurveMathModel.Blossom(b,new[]{.2,.5,.2}),CurveMathModel.Blossom(b,new[]{.5,.2,.2}),"Blossom symmetry");
        Near(CurveMathModel.Circle(2,.3).curvature,.5,"Circle curvature");
        var line=CurveMathModel.HermiteBezier(new CVec(),new CVec(2,0),new CVec(2,0),new CVec(2,0));
        Near(CurveMathModel.BezierSample(line,.4).curvature,0,"Line curvature");
        var stopped=CurveMathModel.HermiteBezier(new CVec(),new CVec(),new CVec(),new CVec(2,0));
        Check(!CurveMathModel.BezierSample(stopped,0).regular,"Zero speed has no normalized tangent");
        Check(double.IsNaN(CurveMathModel.BezierSample(stopped,0).curvature),"Zero speed curvature unavailable");
        Near(CurveMathModel.Smoothstep(-1),0,"Smoothstep low clamp");Near(CurveMathModel.Smoothstep(2),1,"Smoothstep high clamp");
        var q=CurveMathModel.Quintic(new CVec(),new CVec(1,2),new CVec(-2,3),new CVec(5,4),new CVec(3,-1),new CVec(2,-4));
        Vec(CurveMathModel.PowerSample(q,0).d2,new CVec(-2,3),"Quintic start acceleration");Vec(CurveMathModel.PowerSample(q,1).p,new CVec(5,4),"Quintic endpoint");Vec(CurveMathModel.PowerSample(q,1).d1,new CVec(3,-1),"Quintic arrival");Vec(CurveMathModel.PowerSample(q,1).d2,new CVec(2,-4),"Quintic end acceleration");
        var previous=new CVec(0,0);var current=new CVec(1,2);var next=new CVec(4,0);
        var baseline=CurveMathModel.TCB(previous,current,next,0,0,0);Vec(baseline[0],new CVec(2,0),"CatmullRom incoming");Vec(baseline[1],new CVec(2,0),"CatmullRom outgoing");
        var tension=CurveMathModel.TCB(previous,current,next,1,0,0);Vec(tension[0],new CVec(),"Tension1 incoming stop");Vec(tension[1],new CVec(),"Tension1 outgoing stop");
        var corner=CurveMathModel.TCB(previous,current,next,0,-1,0);Vec(corner[0],current-previous,"Cminus1 arrives along previous edge");Vec(corner[1],next-current,"Cminus1 departs along next edge");
        Vec(CurveMathModel.UniformTangent(next,next),new CVec(),"Phantom copied next yields zero tangent");
        var ended=CurveMathModel.TCBPieces(new[]{previous,current,next},.3,.4,.7,true);
        Vec(CurveMathModel.BezierSample(ended[0],0).d1,new CVec(),"Explicit start stop with nonzero bias");
        Vec(CurveMathModel.BezierSample(ended[1],1).d1,new CVec(),"Explicit end stop with nonzero continuity");
        Vec(CurveMathModel.QuadraticStart(new CVec(0,0),new CVec(1,1),new CVec(2,4)),new CVec(1,0),"Quadratic t,t2 first derivative");
        var left=CurveMathModel.HermiteBezier(new CVec(0,0),new CVec(2,0),new CVec(2,0),new CVec(2,0));
        var right=CurveMathModel.HermiteBezier(new CVec(2,0),new CVec(1,0),new CVec(1,0),new CVec(3,0));
        Check(!CurveMathModel.Join(left,right).c1,"Unequal local derivative not C1");Check(CurveMathModel.Join(left,right).g1,"Same direction still G1");Check(CurveMathModel.Join(left,right,2,1).c2,"Unequal durations restore physical C2");
        var bendLeft=CurveMathModel.PowerBezier(new[]{new CVec(0,.5),new CVec(1,-1),new CVec(0,.5),new CVec()});
        var bendRight=CurveMathModel.PowerBezier(new[]{new CVec(1,0),new CVec(1,0),new CVec(0,0,.5),new CVec()});
        var jn=CurveMathModel.Join(bendLeft,bendRight);Check(jn.g1&&!jn.g2,"Equal scalar curvature but different bend plane is not G2");
        Near(CurveMathModel.BezierSample(bendLeft,1).curvature,CurveMathModel.BezierSample(bendRight,0).curvature,"Equal scalar curvatures test premise");
        var restLeft=CurveMathModel.HermiteBezier(new CVec(),new CVec(),new CVec(),new CVec(1,0));var restRight=CurveMathModel.HermiteBezier(new CVec(1,0),new CVec(),new CVec(),new CVec(1,1));
        var restJoin=CurveMathModel.Join(restLeft,restRight);Check(restJoin.c1&&!restJoin.regular&&!restJoin.g1,"Stopped corner C1 is not regular G1");
        var address=CurveMathModel.Address(2.3,4);Check(address.index==2,"Zero-based segment");Near(address.local,.3,"Local parameter");address=CurveMathModel.Address(4,4);Check(address.index==3&&address.local==1,"Final boundary stays in last segment");
        Throws(()=>CurveMathModel.Address(4.1,4),"Out-of-range curve traversal rejected");Throws(()=>CurveMathModel.LagrangeWeights(new[]{0.0,0.0},.5),"Duplicate interpolation nodes rejected");Throws(()=>CurveMathModel.Bezier(new CVec[0],.5),"Empty controls rejected");Throws(()=>CurveMathModel.Subcurve(b,.5,.2),"Reversed extract rejected");
        Console.WriteLine("PASS "+checks+" numerical, endpoint, derivative, subdivision, continuity and invalid-input assertions. No Unity runtime or visual QA.");
    }
}
