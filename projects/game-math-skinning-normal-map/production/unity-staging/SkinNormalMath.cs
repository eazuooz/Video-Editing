using System;

namespace Yamyam.SkinNormal {
    // Double-precision teaching values. Columns are basis vectors; p' = M p.
    [Serializable] public struct Vec {
        public double x,y,z;
        public Vec(double x,double y,double z=0){this.x=x;this.y=y;this.z=z;}
        public static Vec operator +(Vec a,Vec b)=>new Vec(a.x+b.x,a.y+b.y,a.z+b.z);
        public static Vec operator -(Vec a,Vec b)=>new Vec(a.x-b.x,a.y-b.y,a.z-b.z);
        public static Vec operator -(Vec a)=>a*-1;
        public static Vec operator *(Vec a,double k)=>new Vec(a.x*k,a.y*k,a.z*k);
        public static Vec operator *(double k,Vec a)=>a*k;
        public static Vec operator /(Vec a,double k)=>a*(1/k);
        public double Length=>Math.Sqrt(Dot(this,this));
        public static double Dot(Vec a,Vec b)=>a.x*b.x+a.y*b.y+a.z*b.z;
        public static Vec Cross(Vec a,Vec b)=>new Vec(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
        public bool TryUnit(out Vec v,double epsilon=1e-12){double l=Length;v=l>epsilon&& !double.IsInfinity(l)?this/l:new Vec();return l>epsilon&&!double.IsNaN(l)&&!double.IsInfinity(l);}
        public Vec Unit(){if(!TryUnit(out Vec v))throw new ArgumentException("Cannot normalize a zero/non-finite vector.");return v;}
        public override string ToString()=>string.Format(System.Globalization.CultureInfo.InvariantCulture,"({0:0.###}, {1:0.###}, {2:0.###})",x,y,z);
    }
    [Serializable] public struct Affine {
        public Vec x,y,z,p;
        public Affine(Vec x,Vec y,Vec z,Vec p){this.x=x;this.y=y;this.z=z;this.p=p;}
        public static Affine Identity=>new Affine(new Vec(1,0,0),new Vec(0,1,0),new Vec(0,0,1),new Vec());
        public static Affine Translation(Vec v){var a=Identity;a.p=v;return a;}
        public static Affine RotateZ(double radians){double c=Math.Cos(radians),s=Math.Sin(radians);return new Affine(new Vec(c,s),new Vec(-s,c),new Vec(0,0,1),new Vec());}
        public static Affine RotateX(double radians){double c=Math.Cos(radians),s=Math.Sin(radians);return new Affine(new Vec(1,0,0),new Vec(0,c,s),new Vec(0,-s,c),new Vec());}
        public Vec Direction(Vec v)=>x*v.x+y*v.y+z*v.z;
        public Vec Point(Vec v)=>Direction(v)+p;
        public double Determinant=>Vec.Dot(x,Vec.Cross(y,z));
        public Affine Inverse(){double d=Determinant;if(Math.Abs(d)<1e-12)throw new ArgumentException("Singular transform.");Vec r0=Vec.Cross(y,z)/d,r1=Vec.Cross(z,x)/d,r2=Vec.Cross(x,y)/d;var a=new Affine(new Vec(r0.x,r1.x,r2.x),new Vec(r0.y,r1.y,r2.y),new Vec(r0.z,r1.z,r2.z),new Vec());a.p=-a.Direction(p);return a;}
        public Vec Normal(Vec v){var inv=Inverse();return new Vec(Vec.Dot(inv.x,v),Vec.Dot(inv.y,v),Vec.Dot(inv.z,v)).Unit();}
        public static Affine operator *(Affine a,Affine b)=>new Affine(a.Direction(b.x),a.Direction(b.y),a.Direction(b.z),a.Point(b.p));
        public static Affine operator *(Affine a,double w)=>new Affine(a.x*w,a.y*w,a.z*w,a.p*w);
        public static Affine operator +(Affine a,Affine b)=>new Affine(a.x+b.x,a.y+b.y,a.z+b.z,a.p+b.p);
    }
    public struct TangentSolution {public bool valid;public double determinant;public Vec tangent,bitangent;public string reason;}
    public struct Frame {public Vec t,b,n;public double handedness;public Vec ToModel(Vec local)=>t*local.x+b*local.y+n*local.z;public Vec ToLocalOrthonormal(Vec world)=>new Vec(Vec.Dot(t,world),Vec.Dot(b,world),Vec.Dot(n,world));}
    public static class SkinNormalMath {
        public static Vec Blend(Vec[] proposals,double[] weights){if(proposals.Length!=weights.Length||weights.Length==0)throw new ArgumentException("Weight layout mismatch.");double sum=0;Vec result=new Vec();for(int i=0;i<weights.Length;i++){if(weights[i]<0||double.IsNaN(weights[i]))throw new ArgumentException("Weights must be nonnegative.");sum+=weights[i];result+=proposals[i]*weights[i];}if(Math.Abs(sum-1)>1e-8)throw new ArgumentException("Weights must sum to 1; do not silently normalize invalid source data.");return result;}
        public static Vec Decode8(int r,int g,int b,bool normalize=true){if(r<0||r>255||g<0||g>255||b<0||b>255)throw new ArgumentOutOfRangeException();Vec v=new Vec(2*r/255.0-1,2*g/255.0-1,2*b/255.0-1);return normalize?v.Unit():v;}
        public static Vec Encode(Vec normal)=>normal.Unit()*.5+new Vec(.5,.5,.5);
        public static Vec ReconstructPositiveZ(double x,double y){double q=x*x+y*y;if(q>1+1e-10)throw new ArgumentException("XY length exceeds 1.");return new Vec(x,y,Math.Sqrt(Math.Max(0,1-q))).Unit();}
        public static TangentSolution Solve(Vec q1,Vec q2,double s1,double t1,double s2,double t2,double epsilon=1e-8){double d=s1*t2-s2*t1;double scale=Math.Max(1,Math.Sqrt((s1*s1+t1*t1)*(s2*s2+t2*t2)));if(Math.Abs(d)<=epsilon*scale)return new TangentSolution{valid=false,determinant=d,reason="Degenerate or ill-conditioned UV triangle: no unique tangent frame."};if(Vec.Cross(q1,q2).Length<1e-10)return new TangentSolution{valid=false,determinant=d,reason="Degenerate geometric triangle."};return new TangentSolution{valid=true,determinant=d,tangent=(q1*t2-q2*t1)/d,bitangent=(q2*s1-q1*s2)/d,reason="signed reciprocal determinant retained"};}
        public static bool Orthonormalize(Vec normal,Vec accumulatedT,Vec accumulatedB,out Frame frame){frame=new Frame();if(!normal.TryUnit(out Vec n))return false;Vec projected=accumulatedT-n*Vec.Dot(n,accumulatedT);if(!projected.TryUnit(out Vec t))return false;Vec cross=Vec.Cross(n,t);double triple=Vec.Dot(cross,accumulatedB);if(Math.Abs(triple)<1e-12)return false;double h=triple<0?-1:1;frame=new Frame{t=t,n=n,b=cross*h,handedness=h};return true;}
        // Analytic metal grooves. It creates our data texture, not a claim of a renderer bake.
        public static double Height(double u,double v)=>.027*Math.Sin(u*6*Math.PI)*Math.Sin(v*6*Math.PI)+.014*Math.Cos(u*2*Math.PI);
        public static Vec HeightNormal(double u,double v){double du=.162*Math.PI*Math.Cos(u*6*Math.PI)*Math.Sin(v*6*Math.PI)-.028*Math.PI*Math.Sin(u*2*Math.PI);double dv=.162*Math.PI*Math.Sin(u*6*Math.PI)*Math.Cos(v*6*Math.PI);return new Vec(-du,-dv,1).Unit();}
        public static double Clamp01(double u)=>Math.Max(0,Math.Min(1,u));
    }
}
