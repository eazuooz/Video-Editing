using System;
using System.Collections.Generic;

namespace Yamyam.MathCurves {
    [Serializable] public struct CVec {
        public double x,y,z;
        public CVec(double x,double y,double z=0){this.x=x;this.y=y;this.z=z;}
        public static CVec operator +(CVec a,CVec b)=>new CVec(a.x+b.x,a.y+b.y,a.z+b.z);
        public static CVec operator -(CVec a,CVec b)=>new CVec(a.x-b.x,a.y-b.y,a.z-b.z);
        public static CVec operator -(CVec a)=>a*-1;
        public static CVec operator *(CVec a,double s)=>new CVec(a.x*s,a.y*s,a.z*s);
        public static CVec operator *(double s,CVec a)=>a*s;
        public static CVec operator /(CVec a,double s){if(s==0)throw new DivideByZeroException();return a*(1/s);}
        public double Length=>Math.Sqrt(Dot(this,this));
        public static double Dot(CVec a,CVec b)=>a.x*b.x+a.y*b.y+a.z*b.z;
        public static CVec Cross(CVec a,CVec b)=>new CVec(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
        public override string ToString()=>"("+x.ToString("0.###",System.Globalization.CultureInfo.InvariantCulture)+", "+y.ToString("0.###",System.Globalization.CultureInfo.InvariantCulture)+", "+z.ToString("0.###",System.Globalization.CultureInfo.InvariantCulture)+")";
    }
    public struct CurveSample {public CVec p,d1,d2;public bool regular;public CVec tangent;public double curvature;}
    public struct JoinMeasure {public double positionGap,firstDerivativeGap,secondDerivativeGap,tangentDirectionGap,curvatureVectorGap;public bool regular,c0,c1,c2,g1,g2;}
    public struct SegmentAddress {public int index;public double local;}
    public static class CurveMathModel {
        static void Nonempty(CVec[] p){if(p==null||p.Length==0)throw new ArgumentException("At least one coefficient/control is required.");}
        static void Finite(double t){if(double.IsNaN(t)||double.IsInfinity(t))throw new ArgumentOutOfRangeException(nameof(t));}
        public static CVec Lerp(CVec a,CVec b,double t){Finite(t);return a*(1-t)+b*t;}
        public static CVec Power(CVec[] c,double t){Nonempty(c);Finite(t);CVec r=c[c.Length-1];for(int i=c.Length-2;i>=0;i--)r=r*t+c[i];return r;}
        public static CVec[] PowerDerivative(CVec[] c){Nonempty(c);if(c.Length==1)return new[]{new CVec()};var r=new CVec[c.Length-1];for(int i=1;i<c.Length;i++)r[i-1]=c[i]*i;return r;}
        public static CurveSample PowerSample(CVec[] c,double t)=>Sample(Power(c,t),Power(PowerDerivative(c),t),Power(PowerDerivative(PowerDerivative(c)),t));
        public static CurveSample Sample(CVec p,CVec d1,CVec d2){double speed=d1.Length;bool regular=speed>1e-10;return new CurveSample{p=p,d1=d1,d2=d2,regular=regular,tangent=regular?d1/speed:new CVec(),curvature=regular?CVec.Cross(d1,d2).Length/(speed*speed*speed):double.NaN};}
        public static CurveSample Circle(double radius,double t){if(radius<=0)throw new ArgumentOutOfRangeException(nameof(radius));double w=2*Math.PI,a=w*t;return Sample(new CVec(radius*Math.Cos(a),radius*Math.Sin(a)),new CVec(-w*radius*Math.Sin(a),w*radius*Math.Cos(a)),new CVec(-w*w*radius*Math.Cos(a),-w*w*radius*Math.Sin(a)));}
        public static CVec[] HermitePower(CVec p0,CVec v0,CVec v1,CVec p1)=>new[]{p0,v0,3*(p1-p0)-2*v0-v1,2*(p0-p1)+v0+v1};
        // Input order is deliberately the source order p0,v0,v1,p1.
        public static double[] HermiteWeights(double t){double q=t*t,r=q*t;return new[]{2*r-3*q+1,r-2*q+t,r-q,-2*r+3*q};}
        public static CVec[] HermiteBezier(CVec p0,CVec v0,CVec v1,CVec p1)=>new[]{p0,p0+v0/3,p1-v1/3,p1};
        public static double Smoothstep(double t){double u=Math.Max(0,Math.Min(1,t));return u*u*(3-2*u);}
        public static CVec[] Quintic(CVec p0,CVec v0,CVec a0,CVec p1,CVec v1,CVec a1){
            CVec c0=p0,c1=v0,c2=a0/2,d=p1-c0-c1-c2,v=v1-c1-2*c2,a=a1-2*c2;
            return new[]{c0,c1,c2,10*d-4*v+a/2,-15*d+7*v-a,6*d-3*v+a/2};
        }
        public static CVec[][] Casteljau(CVec[] b,double t){Nonempty(b);Finite(t);var rows=new CVec[b.Length][];rows[0]=(CVec[])b.Clone();for(int j=1;j<b.Length;j++){rows[j]=new CVec[b.Length-j];for(int i=0;i<rows[j].Length;i++)rows[j][i]=Lerp(rows[j-1][i],rows[j-1][i+1],t);}return rows;}
        public static CVec Bezier(CVec[] b,double t){var r=Casteljau(b,t);return r[r.Length-1][0];}
        public static CVec[] BezierDerivative(CVec[] b){Nonempty(b);int n=b.Length-1;if(n==0)return new[]{new CVec()};var r=new CVec[n];for(int i=0;i<n;i++)r[i]=n*(b[i+1]-b[i]);return r;}
        public static CurveSample BezierSample(CVec[] b,double t)=>Sample(Bezier(b,t),Bezier(BezierDerivative(b),t),Bezier(BezierDerivative(BezierDerivative(b)),t));
        public static double Binomial(int n,int i){if(n<0||i<0||i>n)throw new ArgumentOutOfRangeException();double v=1;for(int k=1;k<=Math.Min(i,n-i);k++)v=v*(n-k+1)/k;return v;}
        public static double[] Bernstein(int n,double t){if(n<0)throw new ArgumentOutOfRangeException(nameof(n));var r=new double[n+1];for(int i=0;i<=n;i++)r[i]=Binomial(n,i)*Math.Pow(t,i)*Math.Pow(1-t,n-i);return r;}
        public static CVec[] BezierPower(CVec[] b){if(b==null||b.Length!=4)throw new ArgumentException("Cubic conversion requires4 controls.");return new[]{b[0],3*(b[1]-b[0]),3*b[0]-6*b[1]+3*b[2],-b[0]+3*b[1]-3*b[2]+b[3]};}
        public static CVec[] PowerBezier(CVec[] c){if(c==null||c.Length!=4)throw new ArgumentException("Cubic conversion requires4 coefficients.");return new[]{c[0],c[0]+c[1]/3,c[0]+2*c[1]/3+c[2]/3,c[0]+c[1]+c[2]+c[3]};}
        public static CVec[][] Split(CVec[] b,double t){if(t<0||t>1)throw new ArgumentOutOfRangeException(nameof(t));var tri=Casteljau(b,t);int n=b.Length;var left=new CVec[n];var right=new CVec[n];for(int i=0;i<n;i++){left[i]=tri[i][0];right[n-1-i]=tri[i][n-1-i];}return new[]{left,right};}
        public static CVec Blossom(CVec[] b,double[] parameters){Nonempty(b);if(parameters.Length!=b.Length-1)throw new ArgumentException("Degree many blossom parameters required.");var row=(CVec[])b.Clone();int active=row.Length;foreach(double t in parameters){for(int i=0;i<active-1;i++)row[i]=Lerp(row[i],row[i+1],t);active--;}return row[0];}
        public static CVec[] Subcurve(CVec[] b,double a,double z){if(a<0||z>1||a>=z)throw new ArgumentOutOfRangeException("Subinterval must satisfy0<=a<b<=1.");Nonempty(b);int n=b.Length-1;var controls=new CVec[n+1];for(int k=0;k<=n;k++){var u=new double[n];for(int j=0;j<n;j++)u[j]=j<n-k?a:z;controls[k]=Blossom(b,u);}return controls;}
        public static CVec[] Elevate(CVec[] b){Nonempty(b);int n=b.Length-1;var r=new CVec[n+2];r[0]=b[0];r[n+1]=b[n];for(int i=1;i<=n;i++)r[i]=b[i-1]*(i/(double)(n+1))+b[i]*(1-i/(double)(n+1));return r;}
        static void Nodes(double[] t,CVec[] p){Nonempty(p);if(t==null||t.Length!=p.Length)throw new ArgumentException("Every point needs one parameter.");for(int i=0;i<t.Length;i++){Finite(t[i]);for(int j=0;j<i;j++)if(t[i]==t[j])throw new ArgumentException("Interpolation parameters must be distinct.");}}
        public static CVec[][] Aitken(double[] knots,CVec[] points,double t){Nodes(knots,points);Finite(t);var rows=new CVec[points.Length][];rows[0]=(CVec[])points.Clone();for(int k=1;k<points.Length;k++){rows[k]=new CVec[points.Length-k];for(int i=0;i<rows[k].Length;i++)rows[k][i]=((knots[i+k]-t)*rows[k-1][i]+(t-knots[i])*rows[k-1][i+1])/(knots[i+k]-knots[i]);}return rows;}
        public static double[] LagrangeWeights(double[] nodes,double t){if(nodes==null||nodes.Length==0)throw new ArgumentException();Nodes(nodes,new CVec[nodes.Length]);var w=new double[nodes.Length];for(int i=0;i<w.Length;i++){w[i]=1;for(int j=0;j<w.Length;j++)if(i!=j)w[i]*=(t-nodes[j])/(nodes[i]-nodes[j]);}return w;}
        public static CVec Lagrange(double[] nodes,CVec[] points,double t){Nodes(nodes,points);var w=LagrangeWeights(nodes,t);var r=new CVec();for(int i=0;i<w.Length;i++)r+=points[i]*w[i];return r;}
        public static SegmentAddress Address(double s,int segmentCount){if(segmentCount<=0||s<0||s>segmentCount||double.IsNaN(s))throw new ArgumentOutOfRangeException();if(s==segmentCount)return new SegmentAddress{index=segmentCount-1,local=1};return new SegmentAddress{index=(int)Math.Floor(s),local=s-Math.Floor(s)};}
        public static CVec UniformTangent(CVec previous,CVec next)=>(next-previous)/2;
        public static CVec[] TCB(CVec previous,CVec current,CVec next,double tension,double continuity,double bias){
            var a=current-previous;var b=next-current;double k=(1-tension)/2;
            var incoming=k*((1-continuity)*(1+bias)*a+(1+continuity)*(1-bias)*b);
            var outgoing=k*((1+continuity)*(1+bias)*a+(1-continuity)*(1-bias)*b);
            return new[]{incoming,outgoing};
        }
        public static CVec QuadraticStart(CVec p0,CVec p1,CVec p2)=>(-3*p0+4*p1-p2)/2;
        public static CVec[][] TCBPieces(CVec[] points,double tension,double continuity,double bias,bool stopAtEnds){
            if(points==null||points.Length<2)throw new ArgumentException("At least2 knots required.");var tangent=new CVec[points.Length][];
            for(int i=0;i<points.Length;i++){
                CVec previous=i>0?points[i-1]:stopAtEnds?points[1]:2*points[0]-points[1];
                CVec next=i<points.Length-1?points[i+1]:stopAtEnds?points[points.Length-2]:2*points[i]-points[i-1];
                tangent[i]=TCB(previous,points[i],next,tension,continuity,bias);
                // Endpoint stopping is an explicit boundary condition. A mirrored
                // phantom point alone cancels only the unbiased uniform case.
                if(stopAtEnds&&(i==0||i==points.Length-1))tangent[i]=new[]{new CVec(),new CVec()};
            }
            var pieces=new CVec[points.Length-1][];for(int i=0;i<pieces.Length;i++)pieces[i]=HermiteBezier(points[i],tangent[i][1],tangent[i+1][0],points[i+1]);return pieces;
        }
        static CVec CurvatureVector(CurveSample s){double speed=s.d1.Length;var tangent=s.d1/speed;return (s.d2-tangent*CVec.Dot(tangent,s.d2))/(speed*speed);}
        public static JoinMeasure Join(CVec[] left,CVec[] right,double leftDuration=1,double rightDuration=1,double tolerance=1e-8){
            if(leftDuration<=0||rightDuration<=0)throw new ArgumentOutOfRangeException();var a=BezierSample(left,1);var b=BezierSample(right,0);
            var r=new JoinMeasure{positionGap=(a.p-b.p).Length,firstDerivativeGap=(a.d1/leftDuration-b.d1/rightDuration).Length,secondDerivativeGap=(a.d2/(leftDuration*leftDuration)-b.d2/(rightDuration*rightDuration)).Length,regular=a.regular&&b.regular,tangentDirectionGap=double.NaN,curvatureVectorGap=double.NaN};
            r.c0=r.positionGap<=tolerance;r.c1=r.c0&&r.firstDerivativeGap<=tolerance;r.c2=r.c1&&r.secondDerivativeGap<=tolerance;
            if(r.regular){r.tangentDirectionGap=(a.tangent-b.tangent).Length;r.curvatureVectorGap=(CurvatureVector(a)-CurvatureVector(b)).Length;}
            r.g1=r.c0&&r.regular&&r.tangentDirectionGap<=tolerance;r.g2=r.g1&&r.curvatureVectorGap<=tolerance;return r;
        }
    }
}
