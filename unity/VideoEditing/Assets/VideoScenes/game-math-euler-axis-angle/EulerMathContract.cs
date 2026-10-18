using System;
using UnityEngine;

namespace YamyamCoding.GameMath.EulerAxisAngle
{
    /// <summary>
    /// The lesson uses RIGHT-HANDED, COLUMN-VECTOR, LOCAL-TO-WORLD matrices.
    /// x cross y = z, y is up, and aircraft nose is +z. Do not use Unity Euler
    /// angles as the lesson matrix. C = diag(1,1,-1) maps math to Unity space.
    /// Points: pU=C pM. Rotations: RU=C RM C. Both identities are testable.
    /// </summary>
    public static class EulerMathContract
    {
        public static Vector3 ToUnity(Vector3 math) => new Vector3(math.x, math.y, -math.z);
        public static Vector3 ToMath(Vector3 unity) => ToUnity(unity);

        public static Matrix4x4 Rx(float degrees)
        {
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            Matrix4x4 r = Matrix4x4.identity;
            r.m11 = c; r.m12 = -s; r.m21 = s; r.m22 = c;
            return r;
        }
        public static Matrix4x4 Ry(float degrees)
        {
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            Matrix4x4 r = Matrix4x4.identity;
            r.m00 = c; r.m02 = s; r.m20 = -s; r.m22 = c;
            return r;
        }
        public static Matrix4x4 Rz(float degrees)
        {
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            Matrix4x4 r = Matrix4x4.identity;
            r.m00 = c; r.m01 = -s; r.m10 = s; r.m11 = c;
            return r;
        }
        public static Matrix4x4 EulerYXZ(float heading, float pitch, float bank)
            => Ry(heading) * Rx(pitch) * Rz(bank);

        public static Matrix4x4 AxisAngle(Vector3 axisMath, float degrees)
        {
            if (Mathf.Abs(degrees) < 1e-7f) return Matrix4x4.identity;
            if (axisMath.sqrMagnitude < 1e-12f)
                throw new ArgumentException("A nonzero angle needs a nonzero axis.");
            Vector3 n = axisMath.normalized;
            float a = degrees * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a), t = 1f - c;
            Matrix4x4 r = Matrix4x4.identity;
            r.m00 = c + n.x * n.x * t;
            r.m01 = n.x * n.y * t - n.z * s;
            r.m02 = n.x * n.z * t + n.y * s;
            r.m10 = n.y * n.x * t + n.z * s;
            r.m11 = c + n.y * n.y * t;
            r.m12 = n.y * n.z * t - n.x * s;
            r.m20 = n.z * n.x * t - n.y * s;
            r.m21 = n.z * n.y * t + n.x * s;
            r.m22 = c + n.z * n.z * t;
            return r;
        }
        public static Matrix4x4 RotationVector(Vector3 radians)
        {
            float theta = radians.magnitude;
            return theta < 1e-7f ? Matrix4x4.identity : AxisAngle(radians / theta, theta * Mathf.Rad2Deg);
        }
        public static Matrix4x4 UnityMatrix(Matrix4x4 math)
        {
            Matrix4x4 c = Matrix4x4.identity;
            c.m22 = -1f;
            return c * math * c;
        }
        public static Quaternion UnityRotation(Matrix4x4 math)
        {
            Matrix4x4 u = UnityMatrix(math);
            return Quaternion.LookRotation(u.GetColumn(2), u.GetColumn(1));
        }
        public static Matrix4x4 MathMatrix(Quaternion unity)
            => UnityMatrix(Matrix4x4.Rotate(unity));
        public static float WrapPi(float radians)
        {
            if (float.IsNaN(radians) || float.IsInfinity(radians))
                throw new ArgumentException("wrapPi requires finite radians.");
            // Use the same representable pi for both remainder and endpoint
            // comparison; mixing double Math.PI with float Mathf.PI can turn
            // an exactly supplied +Mathf.PI into an almost-negative endpoint.
            float pi = Mathf.PI;
            float r = (float)Math.IEEERemainder(radians, 2.0 * pi);
            if (r <= -pi) r += 2f * pi;
            return r;
        }
        public static float MaxDifference(Matrix4x4 a, Matrix4x4 b)
        {
            float e = 0f;
            for (int r = 0; r < 3; r++) for (int c = 0; c < 3; c++)
                e = Mathf.Max(e, Mathf.Abs(a[r, c] - b[r, c]));
            return e;
        }
    }
}
