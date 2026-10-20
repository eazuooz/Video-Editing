using System;
using UnityEngine;

namespace YamyamCoding.GameMath.EulerAxisAngle.V6
{
    /// <summary>
    /// Article contract: LEFT-HANDED +X right/+Y up/+Z forward; positive left-hand
    /// rotations; ROW vectors v_u = v_o R; intrinsic body Y-X-Z (h,p,b).
    /// R_object_to_upright = Rz_row(b) Rx_row(p) Ry_row(h).
    /// Unity stores column transforms, so the engine matrix is R.transpose.
    /// No reflection/conjugation from the older right-handed V5 pipeline is used.
    /// </summary>
    public static class EulerV6Math
    {
        public static Matrix4x4 Rx(float degrees)
        {
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            Matrix4x4 r = Matrix4x4.identity;
            r.m11 = c; r.m12 = s; r.m21 = -s; r.m22 = c; return r;
        }
        public static Matrix4x4 Ry(float degrees)
        {
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            Matrix4x4 r = Matrix4x4.identity;
            r.m00 = c; r.m02 = -s; r.m20 = s; r.m22 = c; return r;
        }
        public static Matrix4x4 Rz(float degrees)
        {
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            Matrix4x4 r = Matrix4x4.identity;
            r.m00 = c; r.m01 = s; r.m10 = -s; r.m11 = c; return r;
        }
        public static Matrix4x4 HPB(Vector3 hpb) => Rz(hpb.z) * Rx(hpb.y) * Ry(hpb.x);
        public static Vector3 RowMultiply(Vector3 v, Matrix4x4 r) => r.transpose.MultiplyVector(v);
        public static Vector3 ToUnity(Vector3 v) => v;
        public static Vector3 ToMath(Vector3 v) => v;
        public static Quaternion UnityRotation(Matrix4x4 row)
        {
            Matrix4x4 column = row.transpose;
            return Quaternion.LookRotation(column.GetColumn(2), column.GetColumn(1));
        }
        public static Matrix4x4 AxisAngle(Vector3 axis, float degrees)
        {
            if (Mathf.Abs(degrees) < 1e-7f) return Matrix4x4.identity;
            if (axis.sqrMagnitude < 1e-12f) throw new ArgumentException("Nonzero rotation needs a nonzero axis.");
            Vector3 n = axis.normalized;
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a), t = 1f - c;
            Matrix4x4 r = Matrix4x4.identity;
            r.m00 = c + n.x*n.x*t; r.m01 = n.x*n.y*t + n.z*s; r.m02 = n.x*n.z*t - n.y*s;
            r.m10 = n.y*n.x*t - n.z*s; r.m11 = c + n.y*n.y*t; r.m12 = n.y*n.z*t + n.x*s;
            r.m20 = n.z*n.x*t + n.y*s; r.m21 = n.z*n.y*t - n.x*s; r.m22 = c + n.z*n.z*t;
            return r;
        }
        public static Matrix4x4 RotationVector(Vector3 radians)
        {
            float theta = radians.magnitude;
            return theta < 1e-7f ? Matrix4x4.identity : AxisAngle(radians/theta, theta*Mathf.Rad2Deg);
        }
        public static float Difference(Matrix4x4 a, Matrix4x4 b)
        {
            float e = 0f;
            for(int i=0;i<3;i++) for(int j=0;j<3;j++) e=Mathf.Max(e,Mathf.Abs(a[i,j]-b[i,j]));
            return e;
        }
        public static void Validate()
        {
            const float eps=3e-5f;
            Check(RowMultiply(Vector3.forward,Ry(90)),Vector3.right,"heading+90",eps);
            Check(RowMultiply(Vector3.forward,Rx(90)),Vector3.down,"pitch+90",eps);
            Check(RowMultiply(Vector3.up,Rz(90)),Vector3.left,"bank+90",eps);
            Check(RowMultiply(Vector3.forward,Rx(90)*Ry(90)),Vector3.down,"fixedXthenY",eps);
            Check(RowMultiply(Vector3.forward,Ry(90)*Rx(90)),Vector3.right,"fixedYthenX",eps);
            Equal(HPB(new Vector3(0,135,0)),HPB(new Vector3(180,45,180)),"alias",eps);
            Equal(HPB(new Vector3(30,90,10)),HPB(new Vector3(20,90,0)),"gimbal+h-b",eps);
            Equal(HPB(new Vector3(45,90,0)),HPB(new Vector3(0,90,-45)),"corrected-source-sign",eps);
            Equal(HPB(new Vector3(30,-90,10)),HPB(new Vector3(40,-90,0)),"gimbal-h+b",eps);
            Equal(AxisAngle(Vector3.up,90),AxisAngle(Vector3.down,270),"norm<2pi-is-not-unique",eps);
            Check(RowMultiply(Vector3.up,AxisAngle(Vector3.up,90)),Vector3.up,"axis-Y-invariant",eps);
            var rng=new System.Random(20261020);
            for(int i=0;i<120;i++)
            {
                Vector3 hp=new Vector3((float)rng.NextDouble()*360-180,(float)rng.NextDouble()*180-90,(float)rng.NextDouble()*360-180);
                Matrix4x4 r=HPB(hp);Quaternion q=UnityRotation(r);
                Check(q*Vector3.forward,RowMultiply(Vector3.forward,r),"Unity-forward-transpose",eps);
                Check(q*Vector3.up,RowMultiply(Vector3.up,r),"Unity-up-transpose",eps);
                Quaternion native=Quaternion.AngleAxis(hp.x,Vector3.up)*Quaternion.AngleAxis(hp.y,Vector3.right)*Quaternion.AngleAxis(hp.z,Vector3.forward);
                Check(native*Vector3.forward,q*Vector3.forward,"native-positive-axes",eps);
            }
        }
        private static void Check(Vector3 a,Vector3 b,string name,float eps)
        {if(Vector3.Distance(a,b)>eps)throw new InvalidOperationException("V6 math check failed: "+name+" "+a+" != "+b);}
        private static void Equal(Matrix4x4 a,Matrix4x4 b,string name,float eps)
        {if(Difference(a,b)>eps)throw new InvalidOperationException("V6 matrix check failed: "+name);}
    }
}
