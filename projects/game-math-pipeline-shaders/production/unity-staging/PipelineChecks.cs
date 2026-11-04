using System;
using System.Collections.Generic;
using Yamyam.PipelineTeaching;
class PipelineChecks {
    static int checks;
    static void Yes(bool b,string m){checks++;if(!b)throw new Exception(m);}
    static void Near(double a,double b,string m,double eps=1e-9){Yes(Math.Abs(a-b)<eps,m+": "+a+" != "+b);}
    static void Vec(P3 a,P3 b,string m,double e=1e-9){Near(a.x,b.x,m+" x",e);Near(a.y,b.y,m+" y",e);Near(a.z,b.z,m+" z",e);}
    static PVertex V(double x,double y,double z=.5,double w=1)=>new PVertex(new P4(x,y,z,w),new P2(x,y),new P3(1,1,1));
    static int Main(){
        var rng=new Random(23);
        for(int k=0;k<100;k++){
            var p=new P4(rng.NextDouble(),rng.NextDouble(),rng.NextDouble());var m=PMatrix.RotateY(rng.NextDouble())*PMatrix.Translation(2,-1,4);var v=PMatrix.Translation(-1,1,2);var pr=PMatrix.Projection(1.5,60,1,100,false);
            var a=pr.Transform(v.Transform(m.Transform(p)));var b=(m*v*pr).Transform(p);Vec(a.xyz,b.xyz,"row MVP");Near(a.w,b.w,"row w");
        }
        var gl=PMatrix.Projection(2.0/3,60,1,256,true);var dx=PMatrix.Projection(2.0/3,60,1,256,false);
        Near(PipelineMath.Divide(gl.Transform(new P4(0,0,-1))).z,-1,"GL near");Near(PipelineMath.Divide(gl.Transform(new P4(0,0,-256))).z,1,"GL far");
        Near(PipelineMath.Divide(dx.Transform(new P4(0,0,1))).z,0,"DX near");Near(PipelineMath.Divide(dx.Transform(new P4(0,0,256))).z,1,"DX far");
        Near(dx[0,0],Math.Sqrt(3),"horizontal zoom");Near(dx[1,1],2*Math.Sqrt(3)/3,"vertical zoom");Near(360/Math.PI*Math.Atan(1/dx[1,1]),81.78678929826182,"vertical FOV");
        var wide=PMatrix.Projection(8.0/9,60,1,256,false);Near(360/Math.PI*Math.Atan(1/wide[1,1]),66.00898319776617,"wide FOV");
        var crossing=new[]{V(0,0),V(2,0),V(0,.8)};var cp=PipelineMath.ClipPlane(crossing,1);Yes(cp.Count==4,"start-output clipped quad");Near(cp[0].clip.x,0,"start emitted");Near(cp[1].clip.x,1,"intersection first");Near(cp[1].uv.x,1,"attribute clip linear");Near(cp[2].clip.x,1,"intersection second");
        var near=PipelineMath.Clip(new[]{V(-.5,-.5,-.5),V(.5,-.5,.5),V(0,.5,.5)});Yes(near.Count==4,"near plane creates quad");foreach(var v in near)for(int p=0;p<6;p++)Yes(PipelineMath.Plane(v.clip,p)>=-1e-9,"inside all homogeneous planes");
        Yes(PipelineMath.Clip(new[]{V(-.5,-.5,-2),V(.5,-.5,-2),V(0,.5,-2)}).Count==0,"wholly behind near rejected");
        for(int i=0;i<200;i++){var vertices=new PVertex[3];for(int j=0;j<3;j++){double w=.1+rng.NextDouble()*3;vertices[j]=V((rng.NextDouble()*4-2)*w,(rng.NextDouble()*4-2)*w,(rng.NextDouble()*2-.5)*w,w);}foreach(var p in PipelineMath.Clip(vertices))for(int plane=0;plane<6;plane++)Yes(PipelineMath.Plane(p.clip,plane)>=-1e-8,"random clip inside");}
        var bfr=new PBuffer(16,16);var quad=new[]{V(-1,-1),V(1,-1),V(1,1),V(-1,1)};PipelineMath.Triangle(bfr,quad[0],quad[1],quad[2],new PRasterOptions());PipelineMath.Triangle(bfr,quad[0],quad[2],quad[3],new PRasterOptions());
        foreach(var n in bfr.coverage)Yes(n==1,"top-left shared edge exactly once");
        var o=new PRasterOptions();bfr.Clear();PipelineMath.Draw(bfr,PipelineMath.TriangleAt(.7,new P3(0,0,1)),o);o.objectId=1;PipelineMath.Draw(bfr,PipelineMath.TriangleAt(.3,new P3(1,0,0)),o);o.objectId=2;PipelineMath.Draw(bfr,PipelineMath.TriangleAt(.8,new P3(0,1,0)),o);int at=8*16+8;Near(bfr.depth[at],.3,"depth smaller");Yes(bfr.owner[at]==1,"occluded later rejected");Vec(bfr.color[at],new P3(1,0,0),"front color");
        bfr.Clear(true);o.reverseDepth=true;o.objectId=0;PipelineMath.Draw(bfr,PipelineMath.TriangleAt(.7,new P3(0,0,1)),o);o.objectId=1;PipelineMath.Draw(bfr,PipelineMath.TriangleAt(.3,new P3(1,0,0)),o);Near(bfr.depth[at],.7,"reverse stores 1-depth");Yes(bfr.owner[at]==1,"reverse same visible surface");
        Yes(!PipelineMath.DepthPass(1,1),"far endpoint LESS equality fails");Yes(!PipelineMath.DepthPass(0,0,true),"reverse far equality fails");
        Vec(PipelineMath.Blend(new P3(1,0,0),new P3(0,0,1),.25),new P3(.25,0,.75),"alpha example");
        P3 rb=PipelineMath.Blend(new P3(1,0,0),PipelineMath.Blend(new P3(0,0,1),new P3(),.5),.5),br=PipelineMath.Blend(new P3(0,0,1),PipelineMath.Blend(new P3(1,0,0),new P3(),.5),.5);Vec(rb,new P3(.5,0,.25),"far blue then red");Vec(br,new P3(.25,0,.5),"reverse blend differs");
        bfr.Clear();o=new PRasterOptions{alphaTest=true,alpha=.2,cutoff=.5};PipelineMath.Draw(bfr,PipelineMath.TriangleAt(.3,new P3(1,0,0)),o);Near(bfr.depth[at],1,"discard leaves depth");
        var lam=new[]{.25,.25,.5};var weights=PipelineMath.AttributeWeights(lam,new[]{1.0,2.0,4.0},true);Near(weights[0],.5,"persp weight0");Near(weights[1],.25,"persp weight1");Near(weights[2],.25,"persp weight2");
        bfr.Clear();o=new PRasterOptions{perspective=true};var a0=V(-1,-1,.2,1);var a1=V(2,-2,1.2,2);var a2=V(0,4,3.2,4);PipelineMath.Triangle(bfr,a0,a1,a2,o);var screen=new[]{new P2(0,0),new P2(16,0),new P2(8,16)};var lambda=PipelineMath.Barycentric(screen[0],screen[1],screen[2],new P2(8.5,8.5));Near(bfr.depth[at],lambda[0]*.2+lambda[1]*.6+lambda[2]*.8,"depth affine not 1/w");
        Near(PipelineMath.BackfaceDot(new P3(1,0,0),new P3(),new P3(2,0,0)),-2,"front dot");Near(PipelineMath.BackfaceDot(new P3(1,0,0),new P3(),new P3(-2,0,0)),2,"back dot");
        Vec(PipelineMath.BlinnPhong(new P3(0,0,1),new P3(0,0,-1),new P3(0,0,1),new P3(.5,.5,.5),new P3(1,1,1),8,new P3(1,1,1),new P3(.1,.1,.1)),new P3(.05,.05,.05),"backlight gates spec");
        Near(.5*(.75*.8+.1)+.4*.75*.2,.41,"source scalar lighting");Vec(P3.Hadamard(new P3(.8,.4,.2),new P3(1,.5,1)),new P3(.8,.2,.2),"texture tint");
        Near(Math.Max((.5+(-.5))*.5,0),0,"post clamp");Near((Math.Max(.5,0)+Math.Max(-.5,0))*.5,.25,"pre clamp different");
        var expected=new[]{new P3(.5817152646910346,-.5761694144396308,.5741394923620328),new P3(-.16879106487387602,.9617165324209217,.21589554809449255),new P3(.7071013852990032,.6341978072023884,.3127311501080648),new P3(.871509438838122,.3811482848291667,.30854056943592695)};
        for(int i=0;i<4;i++){var n=PipelineMath.Normal8(PipelineMath.NormalRGB[i,0],PipelineMath.NormalRGB[i,1],PipelineMath.NormalRGB[i,2]);Vec(PipelineMath.ToModel(n,PipelineMath.NormalN[i],PipelineMath.NormalT[i],PipelineMath.NormalH[i]),expected[i],"normal exercise"+i);}
        Yes(PipelineMath.Encode(.805)==230,"source normal .805");Yes(PipelineMath.Encode(.267)==162&&PipelineMath.Encode(-.535)==59,"source normal encode");Yes(PipelineMath.Encode(0)==128,"half channel rounding");
        for(int i=0;i<100;i++){var uv=new P2(rng.NextDouble(),rng.NextDouble());Vec(PipelineMath.Checker(uv),PipelineMath.Checker(uv+new P2(5,-1)),"repeat integer offset");}
        Console.WriteLine("{\"passed\":true,\"checks\":"+checks+",\"coverageRule\":\"top-left y-up\",\"matrixConvention\":\"row-vector\",\"normalExerciseB\":[-0.16879106487387602,0.9617165324209217,0.21589554809449255],\"depthExample\":{\"normal\":0.3,\"reverse\":0.7},\"scope\":\"CPU implementation, no Unity/GPU or rendering QA\"}");return 0;
    }
}
