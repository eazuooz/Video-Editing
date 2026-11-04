using System;
using System.Globalization;
using Yamyam.SkinNormal;
public static class SkinNormalChecks {
 static int checks;
 static void Assert(bool ok,string message){checks++;if(!ok)throw new Exception(message);}
 static void Near(double a,double b,string label,double e=1e-10)=>Assert(Math.Abs(a-b)<=e,label+": "+a+" != "+b);
 static void Near(Vec a,Vec b,string label,double e=1e-10)=>Near((a-b).Length,0,label,e);
 static void Throws(Action a,string label){bool thrown=false;try{a();}catch(ArgumentException){thrown=true;}Assert(thrown,label);}
 public static void Main(){CultureInfo.CurrentCulture=CultureInfo.InvariantCulture;
  Near(SkinNormalMath.Blend(new[]{new Vec(0,2),new Vec(2,0)},new[]{.6,.4}),new Vec(.8,1.2),"60/40 worked position");
  Near(SkinNormalMath.Blend(new[]{new Vec(0,2),new Vec(2,0)},new[]{.2,.8}),new Vec(1.6,.4),"20/80 worked position");
  Throws(()=>SkinNormalMath.Blend(new[]{new Vec(),new Vec()},new[]{.6,.6}),"Weight sum guard");
  Throws(()=>SkinNormalMath.Blend(new[]{new Vec(),new Vec()},new[]{-1.0,2.0}),"Weight positivity guard");
  var bind=Affine.Translation(new Vec(1,0));var current=Affine.Translation(new Vec(3,0));var p=new Vec(2,0);
  Near((current*bind.Inverse()).Point(p),new Vec(4,0),"Inverse bind example");Near(current.Point(p),new Vec(5,0),"Skip-inverse counterexample");Near((bind*bind.Inverse()).Point(p),p,"Bind pose is identity");
  var rng=new Random(22);for(int i=0;i<1000;i++){
   double a=rng.NextDouble()*6-3,b=rng.NextDouble()*6-3,w=rng.NextDouble();Vec v=new Vec(rng.NextDouble(),rng.NextDouble(),rng.NextDouble());Affine x=Affine.Translation(new Vec(1,3,-2))*Affine.RotateZ(a),y=Affine.Translation(new Vec(-2,1,4))*Affine.RotateX(b);
   Near((x*w+y*(1-w)).Point(v),x.Point(v)*w+y.Point(v)*(1-w),"Matrix blend distributivity");
   Near(x.Inverse().Point(x.Point(v)),v,"Affine round trip");
   Near(x.Normal(v),x.Direction(v).Unit(),"Rigid normal transform");
  }
  Affine scale=Affine.Identity;scale.x=new Vec(2,0,0);Vec normal=new Vec(1,1).Unit(),tangent=new Vec(1,-1).Unit();
  Near(Vec.Dot(scale.Normal(normal),scale.Direction(tangent)),0,"Inverse-transpose preserves perpendicularity");
  Assert(Math.Abs(Vec.Dot(scale.Direction(normal).Unit(),scale.Direction(tangent)))>.5,"Direct normal direction fails under nonuniform scale");
  Vec translated=Affine.Translation(new Vec(100,2,3)).Direction(normal);Near(translated,normal,"Normal has no translation");
  for(int i=0;i<=180;i++){double a=i*Math.PI/180;Affine blend=Affine.Identity*.5+Affine.RotateX(a)*.5;double radius=blend.Direction(new Vec(0,1,0)).Length;Near(radius,Math.Abs(Math.Cos(a/2)),"Twist shrink prediction");}
  var raw=SkinNormalMath.Decode8(37,128,218,false);var decoded=SkinNormalMath.Decode8(37,128,218);Near(raw,new Vec(-181/255.0,1/255.0,181/255.0),"Exact 8-bit decode");Near(decoded.Length,1,"Decoded normalization");Assert(decoded.y>0,"Quantization Y is not zero");
  Near(SkinNormalMath.Encode(new Vec(0,0,1)),new Vec(.5,.5,1),"Flat normal encoding");
  Vec q1=new Vec(2,0),q2=new Vec(0,1);var positive=SkinNormalMath.Solve(q1,q2,1,0,0,1);var mirrored=SkinNormalMath.Solve(q1,q2,-1,0,0,1);
  Assert(positive.valid&&mirrored.valid,"Tangent solutions exist");Near(positive.tangent,new Vec(2,0),"Positive UV T");Near(mirrored.tangent,new Vec(-2,0),"Signed UV determinant");Near(mirrored.bitangent,new Vec(0,1),"Mirrored UV B retained");
  Assert(!SkinNormalMath.Solve(q1,q2,1,0,2,0).valid,"Degenerate UV guard");Assert(!SkinNormalMath.Solve(q1,q2,1,0,0,1e-12).valid,"Near-degenerate UV guard");Assert(!SkinNormalMath.Solve(q1,q1,1,0,0,1).valid,"Geometry degenerate guard");
  for(int i=0;i<1000;i++){double s1=rng.NextDouble()*2-1,t1=rng.NextDouble()*2-1,s2=rng.NextDouble()*2-1,t2=rng.NextDouble()*2-1;var r=SkinNormalMath.Solve(q1,q2,s1,t1,s2,t2);if(!r.valid)continue;Near(r.tangent*s1+r.bitangent*t1,q1,"Tangent equation one",1e-8);Near(r.tangent*s2+r.bitangent*t2,q2,"Tangent equation two",1e-8);}
  Assert(SkinNormalMath.Orthonormalize(new Vec(0,0,1),new Vec(2,0,.7),new Vec(0,1,0),out var f),"Gram-Schmidt valid");Near(Vec.Dot(f.n,f.t),0,"T perpendicular N");Near(f.t.Length,1,"Unit T");Near(f.b,new Vec(0,1,0),"Restored B");Near(f.handedness,1,"Positive handedness");
  Assert(SkinNormalMath.Orthonormalize(new Vec(0,0,1),mirrored.tangent,mirrored.bitangent,out var mirrorFrame),"Mirrored frame valid");Near(mirrorFrame.handedness,-1,"Mirror changes handedness");Near(mirrorFrame.b,new Vec(0,1,0),"Handedness restores mirrored B");
  Near(f.ToLocalOrthonormal(f.ToModel(decoded)),decoded,"TBN round trip");
  Assert(!SkinNormalMath.Orthonormalize(new Vec(0,0,1),positive.tangent+mirrored.tangent,positive.bitangent+mirrored.bitangent,out var invalid),"Opposite seam tangents cannot be averaged");
  Affine oblique=new Affine(new Vec(1,0,0),new Vec(.5,1,0),new Vec(0,0,1),new Vec());Vec world=new Vec(1,1,1),inverse=oblique.Inverse().Direction(world),transpose=new Vec(Vec.Dot(oblique.x,world),Vec.Dot(oblique.y,world),Vec.Dot(oblique.z,world));Assert((inverse-transpose).Length>.5,"Transpose is not inverse for oblique frame");
  const double h=1e-6;for(int i=0;i<80;i++){double u=rng.NextDouble(),v=rng.NextDouble();double du=(SkinNormalMath.Height(u+h,v)-SkinNormalMath.Height(u-h,v))/(2*h),dv=(SkinNormalMath.Height(u,v+h)-SkinNormalMath.Height(u,v-h))/(2*h);Near(SkinNormalMath.HeightNormal(u,v),new Vec(-du,-dv,1).Unit(),"Analytic normal versus finite differences",1e-8);}
  Throws(()=>new Vec().Unit(),"Zero normalize guard");Throws(()=>SkinNormalMath.ReconstructPositiveZ(1,1),"Invalid XY normal guard");
  Console.WriteLine("{\"passed\":true,\"checks\":"+checks+",\"rgbDecoded\":["+raw.x+","+raw.y+","+raw.z+"],\"rgbNormalized\":["+decoded.x+","+decoded.y+","+decoded.z+"],\"mirroredT\":[-2,0,0],\"bindExample\":4,\"shaderAndUnityRuntimeQA\":false}");
 }
}
