using System;
namespace Yamyam.OriginalTechTwelve.Temporal {
    [Serializable] public struct TemporalState {public float seconds,cameraX,cubeX;}
    public static class TemporalSceneModel {
        public static readonly string[] Modes={"no-aa","jitter-only","naive-history-overlay","temporal-clipping"};
        public static TemporalState Sample(string mode,float seconds){if(Array.IndexOf(Modes,mode)<0)throw new ArgumentException("Unknown temporal lesson mode");float t=Math.Max(0,Math.Min(12,seconds));return new TemporalState{seconds=t,cameraX=.6f*(float)Math.Sin(t*.6),cubeX=2.2f*(float)Math.Sin(t*.8)};}
        public static float Halton(int index,int radix){float f=1,result=0;while(index>0){f/=radix;result+=f*(index%radix);index/=radix;}return result;}
        public static float Constrain(float history,float low,float high){if(low>high)throw new ArgumentException("Invalid neighborhood");return Math.Max(low,Math.Min(high,history));}
        public static float Blend(float current,float history,float feedback){if(feedback<0||feedback>1)throw new ArgumentException("Invalid feedback");return current*(1-feedback)+history*feedback;}
    }
}
