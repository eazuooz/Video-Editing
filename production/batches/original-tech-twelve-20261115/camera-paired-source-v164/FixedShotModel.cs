using System;
namespace Yamyam.OriginalTechTwelve.Camera {
    [Serializable] public struct FixedShotState {
        public int zone;
        public float cameraX,cameraY,cameraZ,lookX,lookY,lookZ,fieldOfView;
    }
    // Authored teaching cameras. These poses and zones are not RE2 game data.
    public static class FixedShotModel {
        public static FixedShotState Sample(float heroX,float heroZ) {
            if(float.IsNaN(heroX)||float.IsInfinity(heroX)||float.IsNaN(heroZ)||float.IsInfinity(heroZ))throw new ArgumentException("Finite actor position required");
            bool second=heroX>=0;
            return new FixedShotState{zone=second?1:0,cameraX=second?6:-5,cameraY=second?3.8f:4.2f,cameraZ=second?-5:-6,lookX=0,lookY=1,lookZ=2,fieldOfView=55};
        }
    }
}
