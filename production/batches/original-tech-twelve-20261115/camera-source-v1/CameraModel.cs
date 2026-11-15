using System;
namespace Yamyam.OriginalTechTwelve.Camera {
    [Serializable] public struct CameraState {
        public float seconds,heroX,heroZ,cameraX,cameraY,cameraZ,lookX,lookY,lookZ;
        public float requestedYaw,actualYaw,distance,fieldOfView;
        public bool limitReached;
    }
    public static class CameraModel {
        public static readonly string[] Modes={"follow","look-around","orbit","pull-back","orbit-limit"};
        static float Smooth(float t){t=Math.Max(0,Math.Min(1,t));return t*t*(3-2*t);}
        public static CameraState Sample(string mode,float seconds){
            if(Array.IndexOf(Modes,mode)<0)throw new ArgumentException("Unknown teaching mode");
            float t=Math.Max(0,Math.Min(12,seconds));
            var s=new CameraState{seconds=t,heroZ=0,cameraY=2.6f,lookY=.85f,distance=6,fieldOfView=55};
            float u=Smooth((t-2)/7);
            if(mode=="follow")s.heroX=-2+4*u;
            if(mode=="look-around"){
                s.distance=2.8f;s.cameraY=1.7f;
                s.lookX=s.heroX+3*(float)Math.Sin(u*Math.PI*1.4-.6);
                s.lookY=.9f+3*Smooth((t-6)/3);s.lookZ=3;
            } else {s.lookX=s.heroX;s.lookZ=s.heroZ;}
            if(mode=="orbit")s.actualYaw=s.requestedYaw=-55+110*u;
            if(mode=="pull-back")s.distance=4+6*u;
            if(mode=="orbit-limit"){
                s.requestedYaw=100*u;s.actualYaw=Math.Min(60,s.requestedYaw);s.limitReached=s.requestedYaw>60;
            }
            double radians=s.actualYaw*Math.PI/180;
            s.cameraX=s.heroX+s.distance*(float)Math.Sin(radians);
            s.cameraZ=s.heroZ-s.distance*(float)Math.Cos(radians);
            return s;
        }
    }
}
