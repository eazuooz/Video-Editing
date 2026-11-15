using System;
namespace Yamyam.OriginalTechTwelve.Sand {
    [Serializable] public struct SandState {
        public float seconds,cameraX,cameraY,cameraZ,grain,glitter,viewGlitter,grazingMask,broad;
        public bool preserveMipDistribution;
    }
    public static class SandModel {
        public static readonly string[] Modes={"smooth-surface","averaged-grain-mips","preserved-grain-mips","half-vector-glints","view-related-glints","masked-view-glints","masked-glints-broad-light"};
        public static SandState Sample(string mode,float seconds){
            int n=Array.IndexOf(Modes,mode);if(n<0)throw new ArgumentException("Unknown sand teaching mode");
            float t=Math.Max(0,Math.Min(12,seconds));return new SandState{seconds=t,cameraX=-5+10*t/12,cameraY=3.4f,cameraZ=-9,grain=n>0?1:0,glitter=n>2?1:0,viewGlitter=n>3?1:0,grazingMask=n>4?1:0,broad=n>5?1:0,preserveMipDistribution=n>1};
        }
        public static float Height(float x,float z){return .7f*(float)Math.Sin(x*.4)+.35f*(float)Math.Sin(z*.6+x*.2);}
        public static float[] Grain(Random random){
            double y=.12+.88*random.NextDouble(),angle=random.NextDouble()*Math.PI*2,r=Math.Sqrt(1-y*y);
            return new[]{(float)(r*Math.Cos(angle)),(float)y,(float)(r*Math.Sin(angle))};
        }
    }
}
