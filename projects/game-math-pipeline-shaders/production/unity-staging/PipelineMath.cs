using System;
using System.Collections.Generic;

namespace Yamyam.PipelineTeaching {
    public struct P2 { public double x,y; public P2(double x,double y){this.x=x;this.y=y;} public static P2 operator +(P2 a,P2 b)=>new P2(a.x+b.x,a.y+b.y);public static P2 operator *(P2 a,double t)=>new P2(a.x*t,a.y*t); }
    public struct P3 {
        public double x,y,z; public P3(double x,double y,double z=0){this.x=x;this.y=y;this.z=z;}
        public double Length=>Math.Sqrt(x*x+y*y+z*z);
        public P3 Unit(){double n=Length;return n>1e-12?this/n:new P3();}
        public static double Dot(P3 a,P3 b)=>a.x*b.x+a.y*b.y+a.z*b.z;
        public static P3 Cross(P3 a,P3 b)=>new P3(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
        public static P3 operator +(P3 a,P3 b)=>new P3(a.x+b.x,a.y+b.y,a.z+b.z);
        public static P3 operator -(P3 a,P3 b)=>new P3(a.x-b.x,a.y-b.y,a.z-b.z);
        public static P3 operator *(P3 a,double s)=>new P3(a.x*s,a.y*s,a.z*s);
        public static P3 operator /(P3 a,double s)=>a*(1/s);
        public static P3 Hadamard(P3 a,P3 b)=>new P3(a.x*b.x,a.y*b.y,a.z*b.z);
    }
    public struct P4 {
        public double x,y,z,w;public P4(double x,double y,double z,double w=1){this.x=x;this.y=y;this.z=z;this.w=w;}
        public P3 xyz=>new P3(x,y,z);
        public static P4 operator +(P4 a,P4 b)=>new P4(a.x+b.x,a.y+b.y,a.z+b.z,a.w+b.w);
        public static P4 operator *(P4 a,double t)=>new P4(a.x*t,a.y*t,a.z*t,a.w*t);
    }
    // Storage is row-major indexing; arithmetic follows the source's row-vector v*M convention.
    public sealed class PMatrix {
        public readonly double[] e=new double[16];
        public double this[int r,int c]{get=>e[4*r+c];set=>e[4*r+c]=value;}
        public static PMatrix Identity(){var m=new PMatrix();for(int i=0;i<4;i++)m[i,i]=1;return m;}
        public static PMatrix Translation(double x,double y,double z){var m=Identity();m[3,0]=x;m[3,1]=y;m[3,2]=z;return m;}
        public static PMatrix Scale(double x,double y,double z){var m=Identity();m[0,0]=x;m[1,1]=y;m[2,2]=z;return m;}
        public static PMatrix RotateY(double a){var m=Identity();m[0,0]=m[2,2]=Math.Cos(a);m[0,2]=-Math.Sin(a);m[2,0]=Math.Sin(a);return m;}
        public P4 Transform(P4 p){var v=new[]{p.x,p.y,p.z,p.w};var o=new double[4];for(int c=0;c<4;c++)for(int r=0;r<4;r++)o[c]+=v[r]*this[r,c];return new P4(o[0],o[1],o[2],o[3]);}
        public static PMatrix operator *(PMatrix a,PMatrix b){var m=new PMatrix();for(int r=0;r<4;r++)for(int c=0;c<4;c++)for(int k=0;k<4;k++)m[r,c]+=a[r,k]*b[k,c];return m;}
        public PMatrix Transposed(){var m=new PMatrix();for(int r=0;r<4;r++)for(int c=0;c<4;c++)m[r,c]=this[c,r];return m;}
        public static PMatrix Projection(double aspect,double horizontalFovDegrees,double near,double far,bool gl){
            if(aspect<=0||near<=0||far<=near||horizontalFovDegrees<=0||horizontalFovDegrees>=180)throw new ArgumentOutOfRangeException();
            var m=new PMatrix();double sx=1/Math.Tan(horizontalFovDegrees*Math.PI/360);m[0,0]=sx;m[1,1]=aspect*sx;
            if(gl){m[2,2]=-(far+near)/(far-near);m[3,2]=-2*far*near/(far-near);m[2,3]=-1;}
            else {m[2,2]=far/(far-near);m[3,2]=-far*near/(far-near);m[2,3]=1;}
            return m;
        }
    }
    public struct PVertex {
        public P4 clip;public P2 uv;public P3 color,normal;public P3 world;
        public PVertex(P4 c,P2 uv,P3 color){clip=c;this.uv=uv;this.color=color;normal=new P3(0,0,1);world=c.xyz;}
        public static PVertex Mix(PVertex a,PVertex b,double t)=>new PVertex(a.clip*(1-t)+b.clip*t,a.uv*(1-t)+b.uv*t,a.color*(1-t)+b.color*t){normal=a.normal*(1-t)+b.normal*t,world=a.world*(1-t)+b.world*t};
    }
    public sealed class PBuffer {
        public readonly int width,height;public readonly P3[] color;public readonly double[] depth;public readonly int[] coverage,owner;
        public PBuffer(int w,int h){if(w<=0||h<=0)throw new ArgumentOutOfRangeException();width=w;height=h;color=new P3[w*h];depth=new double[w*h];coverage=new int[w*h];owner=new int[w*h];Clear();}
        public void Clear(bool reverse=false){for(int i=0;i<depth.Length;i++){color[i]=new P3(.025,.029,.034);depth[i]=reverse?0:1;coverage[i]=0;owner[i]=-1;}}
    }
    public sealed class PRasterOptions {
        public bool perspective=true,depthTest=true,depthWrite=true,reverseDepth=false,alphaTest=false,glDepth=false;
        public bool cullBack=false,frontCCW=true;public double alpha=1,cutoff=.5;
        public int objectId=0,scissorX=0,scissorY=0,scissorWidth=int.MaxValue,scissorHeight=int.MaxValue;
        public Func<P2,P3,P3,P3> shade; // UV, normalized interpolated normal, vertex color -> linear RGB.
    }
    public static class PipelineMath {
        public static double Clamp01(double x)=>Math.Max(0,Math.Min(1,x));
        // D3D homogeneous half-spaces: no division until all six planes have clipped the polygon.
        public static double Plane(P4 p,int plane,bool gl=false){switch(plane){case 0:return p.x+p.w;case 1:return p.w-p.x;case 2:return p.y+p.w;case 3:return p.w-p.y;case 4:return gl?p.z+p.w:p.z;case 5:return p.w-p.z;default:throw new ArgumentOutOfRangeException();}}
        static bool Same(P4 a,P4 b)=>Math.Abs(a.x-b.x)+Math.Abs(a.y-b.y)+Math.Abs(a.z-b.z)+Math.Abs(a.w-b.w)<1e-10;
        static void AddUnique(List<PVertex> o,PVertex v){if(o.Count==0||!Same(o[o.Count-1].clip,v.clip))o.Add(v);}
        public static List<PVertex> ClipPlane(IList<PVertex> input,int plane,bool gl=false){
            var o=new List<PVertex>();if(input.Count<3)return o;
            // This is the source's START-output variant, consistently across all four cases.
            for(int i=0;i<input.Count;i++){PVertex a=input[i],b=input[(i+1)%input.Count];double da=Plane(a.clip,plane,gl),db=Plane(b.clip,plane,gl);bool ai=da>=0,bi=db>=0;
                if(ai)AddUnique(o,a);
                if(ai!=bi){double t=da/(da-db);AddUnique(o,PVertex.Mix(a,b,t));}
            }
            if(o.Count>1&&Same(o[0].clip,o[o.Count-1].clip))o.RemoveAt(o.Count-1);
            return o;
        }
        public static List<PVertex> Clip(IList<PVertex> polygon,bool gl=false){var p=new List<PVertex>(polygon);for(int i=0;i<6&&p.Count>=3;i++)p=ClipPlane(p,i,gl);if(p.Count<3)p.Clear();return p;}
        public static P3 Divide(P4 p){if(p.w<=1e-12)throw new ArgumentException("Non-positive homogeneous w cannot be divided for this perspective view.");return p.xyz/p.w;}
        public static double Edge(P2 a,P2 b,P2 p)=>(b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x);
        // y-up screen coordinates: top horizontal edges point left, left edges point down.
        public static bool TopLeft(P2 a,P2 b)=>b.y<a.y||(b.y==a.y&&b.x<a.x);
        static bool Inside(double e,P2 a,P2 b)=>e>1e-10||(Math.Abs(e)<=1e-10&&TopLeft(a,b));
        public static double[] Barycentric(P2 a,P2 b,P2 c,P2 p){double d=Edge(a,b,c);if(Math.Abs(d)<1e-12)throw new ArgumentException("Degenerate triangle.");return new[]{Edge(b,c,p)/d,Edge(c,a,p)/d,Edge(a,b,p)/d};}
        public static double[] AttributeWeights(double[] lambda,double[] w,bool perspective){var k=new double[3];double sum=0;for(int i=0;i<3;i++){if(w[i]<=1e-12)throw new ArgumentException("Positive w required.");k[i]=perspective?lambda[i]/w[i]:lambda[i];sum+=k[i];}if(Math.Abs(sum)<1e-12)throw new ArgumentException("Undefined attribute denominator.");for(int i=0;i<3;i++)k[i]/=sum;return k;}
        public static bool DepthPass(double incoming,double stored,bool reverse=false)=>reverse?incoming>stored:incoming<stored;
        public static P3 Blend(P3 src,P3 dst,double alpha)=>src*Clamp01(alpha)+dst*(1-Clamp01(alpha));
        public static int Draw(PBuffer target,IList<PVertex> polygon,PRasterOptions options){var p=Clip(polygon,options.glDepth);int writes=0;for(int i=1;i+1<p.Count;i++)writes+=Triangle(target,p[0],p[i],p[i+1],options);return writes;}
        public static int Triangle(PBuffer target,PVertex a,PVertex b,PVertex c,PRasterOptions o){
            if(a.clip.w<=1e-12||b.clip.w<=1e-12||c.clip.w<=1e-12)return 0;
            P3 na=Divide(a.clip),nb=Divide(b.clip),nc=Divide(c.clip);
            P2 sa=new P2((na.x*.5+.5)*target.width,(na.y*.5+.5)*target.height),sb=new P2((nb.x*.5+.5)*target.width,(nb.y*.5+.5)*target.height),sc=new P2((nc.x*.5+.5)*target.width,(nc.y*.5+.5)*target.height);
            double area=Edge(sa,sb,sc);if(Math.Abs(area)<1e-10)return 0;if(o.cullBack&&((area>0)!=o.frontCCW))return 0;
            if(area<0){var tv=b;b=c;c=tv;var ts=sb;sb=sc;sc=ts;var tn=nb;nb=nc;nc=tn;area=-area;}
            int x0=Math.Max(0,(int)Math.Floor(Math.Min(sa.x,Math.Min(sb.x,sc.x)))),x1=Math.Min(target.width-1,(int)Math.Ceiling(Math.Max(sa.x,Math.Max(sb.x,sc.x))));
            int y0=Math.Max(0,(int)Math.Floor(Math.Min(sa.y,Math.Min(sb.y,sc.y)))),y1=Math.Min(target.height-1,(int)Math.Ceiling(Math.Max(sa.y,Math.Max(sb.y,sc.y))));int writes=0;
            for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
                if(x<o.scissorX||y<o.scissorY||(long)x>=(long)o.scissorX+o.scissorWidth||(long)y>=(long)o.scissorY+o.scissorHeight)continue;
                P2 sample=new P2(x+.5,y+.5);double e0=Edge(sb,sc,sample),e1=Edge(sc,sa,sample),e2=Edge(sa,sb,sample);
                if(!Inside(e0,sb,sc)||!Inside(e1,sc,sa)||!Inside(e2,sa,sb))continue;
                int index=y*target.width+x;target.coverage[index]++;
                double[] l={e0/area,e1/area,e2/area};
                // NDC z is affine in screen barycentrics. Do NOT apply the attribute 1/w division again.
                double depth=l[0]*na.z+l[1]*nb.z+l[2]*nc.z;if(o.glDepth)depth=depth*.5+.5;if(o.reverseDepth)depth=1-depth;
                if(depth<0||depth>1)continue;if(o.depthTest&&!DepthPass(depth,target.depth[index],o.reverseDepth))continue;
                double[] k=AttributeWeights(l,new[]{a.clip.w,b.clip.w,c.clip.w},o.perspective);
                P2 uv=a.uv*k[0]+b.uv*k[1]+c.uv*k[2];P3 normal=(a.normal*k[0]+b.normal*k[1]+c.normal*k[2]).Unit();P3 color=a.color*k[0]+b.color*k[1]+c.color*k[2];
                double alpha=Clamp01(o.alpha);if(o.alphaTest&&alpha<o.cutoff)continue;if(o.shade!=null)color=o.shade(uv,normal,color);
                target.color[index]=Blend(color,target.color[index],alpha);if(o.depthWrite)target.depth[index]=depth;target.owner[index]=o.objectId;writes++;
            }
            return writes;
        }
        public static P3 Checker(P2 uv){int a=(int)Math.Floor(uv.x*8),b=(int)Math.Floor(uv.y*8);bool on=((a+b)&1)==0;double u=uv.x-Math.Floor(uv.x),v=uv.y-Math.Floor(uv.y);if(u<.06)return new P3(.8,.22,.18);if(v<.06)return new P3(.2,.7,.5);return on?new P3(.8,.75,.5):new P3(.08,.16,.22);}
        public static P3 BlinnPhong(P3 n,P3 l,P3 v,P3 diffuse,P3 specular,double exponent,P3 light,P3 ambient){
            n=n.Unit();l=l.Unit();v=v.Unit();double ndl=Math.Max(0,P3.Dot(n,l));P3 h=(l+v).Unit();double s=ndl>0&&h.Length>0?Math.Pow(Math.Max(0,P3.Dot(n,h)),Math.Max(exponent,0)):0;
            return P3.Hadamard(diffuse,ambient+light*ndl)+P3.Hadamard(specular,light)*s;
        }
        public static P3 Normal8(int r,int g,int b){if(r<0||r>255||g<0||g>255||b<0||b>255)throw new ArgumentOutOfRangeException();return new P3(2*r/255.0-1,2*g/255.0-1,2*b/255.0-1).Unit();}
        public static int Encode(double n)=>(int)Math.Round(255*Clamp01(n*.5+.5),MidpointRounding.AwayFromZero);
        public static P3 ToModel(P3 tangentNormal,P3 suppliedN,P3 suppliedT,int h){P3 n=suppliedN.Unit(),t=(suppliedT-n*P3.Dot(n,suppliedT)).Unit();if(n.Length<.5||t.Length<.5||Math.Abs(h)!=1)throw new ArgumentException("Invalid tangent basis.");P3 b=P3.Cross(n,t)*h;return(t*tangentNormal.x+b*tangentNormal.y+n*tangentNormal.z).Unit();}
        public static double BackfaceDot(P3 n,P3 point,P3 eye)=>P3.Dot(n,point-eye);
        public static PVertex[] TriangleAt(double z,P3 color)=>new[]{new PVertex(new P4(-.8,-.7,z),new P2(0,0),color),new PVertex(new P4(.8,-.7,z),new P2(1,0),color),new PVertex(new P4(0,.8,z),new P2(.5,1),color)};
        public static P2[][] ExerciseUV=new[]{new[]{new P2(.2,-.3),new P2(1.3,-.3),new P2(1.3,1.2),new P2(.2,1.2)},new[]{new P2(5,-1),new P2(6,-1),new P2(6,0),new P2(5,0)},new[]{new P2(1,0),new P2(-.23,-.77),new P2(0,1),new P2(1.24,1.77)},new[]{new P2(2,0),new P2(1,1),new P2(0,1),new P2(1,0)},new[]{new P2(-.1,1.1),new P2(-.1,.1),new P2(.9,.1),new P2(.9,1.1)},new[]{new P2(0,-1),new P2(3.35,.06),new P2(1,2),new P2(-2.36,.94)}};
        public static readonly int[,] Materials={{210,40,50,0,0,0,1},{65,55,200,150,0,0,16},{65,55,200,230,230,230,2},{50,50,100,210,40,50,4},{65,55,200,210,40,50,2},{65,55,200,0,0,0,64},{0,0,0,210,40,50,1},{210,40,50,100,100,100,64},{210,40,50,230,230,230,2},{210,40,50,65,55,200,2}};
        public static readonly int[,] NormalRGB={{128,255,128},{106,155,250},{128,218,218},{233,58,145}};
        public static readonly P3[] NormalN={new P3(.408,-.408,-.816),new P3(0,1,0),new P3(1,0,0),new P3(.154,-.617,.772)};
        public static readonly P3[] NormalT={new P3(.707,.707,0),new P3(1,0,0),new P3(0,.447,-.894),new P3(.986,.046,-.161)};
        public static readonly int[] NormalH={1,-1,1,-1};
    }
}
