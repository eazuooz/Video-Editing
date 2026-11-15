using System;
using System.Collections.Generic;
namespace Yamyam.OriginalTechTwelve.Placement {
    [Serializable] public class Candidate {
        public int id;public float x,z,sample,density,y,yaw,scale,normalX,normalY,normalZ;
        public bool accepted,road,water;public string reason,asset;
    }
    [Serializable] public class PlacementState {
        public string mode;public int candidates,accepted,rejectedDensity,rejectedRoad,rejectedWater;
        public bool terrainAligned,secondLayer;
        public List<Candidate> points=new List<Candidate>();
    }
    public static class PlacementModel {
        public static readonly string[] Modes={"all-candidates","density-map","road-water-exclusion","terrain-aligned","two-placement-layers"};
        public static float Height(float x,float z){return .45f*(float)Math.Sin(x*.35)+.35f*(float)Math.Cos(z*.4);}
        public static PlacementState Build(string mode){
            int stage=Array.IndexOf(Modes,mode);if(stage<0)throw new ArgumentException("Unknown teaching stage");
            var result=new PlacementState{mode=mode,terrainAligned=stage>=3,secondLayer=stage>=4};var rng=new Random(20261115);
            for(int z=0;z<10;z++)for(int x=0;x<10;x++){
                var p=new Candidate{id=z*10+x,x=(x-4.5f)*1.8f+(float)(rng.NextDouble()-.5)*.5f,z=(z-4.5f)*1.8f+(float)(rng.NextDouble()-.5)*.5f,sample=(float)rng.NextDouble(),yaw=(float)rng.NextDouble()*360,scale=.85f+(float)rng.NextDouble()*.3f,asset="tree"};
                p.density=p.x<0?.72f:.32f;p.road=Math.Abs(p.x)<1.95;p.water=p.x>3&&p.z>3;
                p.accepted=true;p.reason="accepted";
                if(stage>=1&&p.sample>=p.density){p.accepted=false;p.reason="density";result.rejectedDensity++;}
                else if(stage>=2&&p.road){p.accepted=false;p.reason="road";result.rejectedRoad++;}
                else if(stage>=2&&p.water){p.accepted=false;p.reason="water";result.rejectedWater++;}
                p.y=stage>=3?Height(p.x,p.z):0;
                float nx=-.1575f*(float)Math.Cos(p.x*.35),nz=.14f*(float)Math.Sin(p.z*.4),length=(float)Math.Sqrt(nx*nx+1+nz*nz);p.normalX=nx/length;p.normalY=1/length;p.normalZ=nz/length;
                result.points.Add(p);result.candidates++;if(p.accepted)result.accepted++;
            }
            return result;
        }
        public static bool GrassAllowed(float x,float z){return Math.Abs(x)>1.85f&&!(x>3&&z>3)&&((int)Math.Floor((x+10)*2)+(int)Math.Floor((z+10)*2))%3!=0;}
    }
}
