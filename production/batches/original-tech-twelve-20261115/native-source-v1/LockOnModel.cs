using System;

namespace Yamyam.OriginalTechTwelve.LockOn {
    // A deterministic teaching model, independent of Nintendo code, AI or damage.
    [Serializable] public struct Point {
        public float x,z;
        public Point(float x,float z){this.x=x;this.z=z;}
        public float Length { get { return (float)Math.Sqrt(x*x+z*z); } }
        public Point Normalized { get { float n=Length;return n>0.00001f?new Point(x/n,z/n):new Point(0,1); } }
        public static Point operator+(Point a,Point b){return new Point(a.x+b.x,a.z+b.z);}
        public static Point operator-(Point a,Point b){return new Point(a.x-b.x,a.z-b.z);}
        public static Point operator*(Point a,float b){return new Point(a.x*b,a.z*b);}
        public static float Dot(Point a,Point b){return a.x*b.x+a.z*b.z;}
    }
    [Serializable] public class State {
        public float time,sideInput,forwardInput,heroY,radialDistance,facingDot;
        public string mode,phase;
        public Point hero,heroForward,enemyA,enemyB;
        public bool targetRelative,attackA,attackB,hasSecondEnemy;
        public int selectedEnemy,attackParticipants;
    }
    public static class Model {
        public static readonly string[] Modes={"free-movement","target-relative","simultaneous-intents","turn-taking-intents"};
        static float Clamp(float x,float a,float b){return Math.Max(a,Math.Min(b,x));}
        static float Pulse(float t,float start,float duration){
            if(t<start||t>=start+duration)return 0;
            return (float)Math.Sin(Math.PI*(t-start)/duration);
        }
        public static State Sample(string mode,float seconds){
            if(Array.IndexOf(Modes,mode)<0)throw new ArgumentException("Unknown exact demonstration mode");
            float t=Clamp(seconds,0,12);
            var s=new State {time=t,mode=mode,phase="hold",hero=new Point(0,-4),heroForward=new Point(0,1),enemyA=new Point(0,0),enemyB=new Point(1.8f,0),selectedEnemy=0};
            s.hasSecondEnemy=mode.EndsWith("intents",StringComparison.Ordinal);
            s.targetRelative=mode!="free-movement";
            if(s.hasSecondEnemy){
                s.hero=new Point(0,-2.8f);s.enemyA=new Point(-1.8f,.3f);s.enemyB=new Point(1.8f,.3f);
                float cycle=t%6;
                s.attackA=cycle>=1.5f&&cycle<2.9f;
                s.attackB=mode=="simultaneous-intents"?s.attackA:cycle>=3.1f&&cycle<4.5f;
                s.selectedEnemy=cycle>=3.0f?1:0;
                Point aStart=s.enemyA,bStart=s.enemyB;
                s.enemyA=aStart+(s.hero-aStart).Normalized*(.9f*Pulse(cycle,1.5f,1.4f));
                s.enemyB=bStart+(s.hero-bStart).Normalized*(.9f*Pulse(cycle,mode=="simultaneous-intents"?1.5f:3.1f,1.4f));
                s.heroForward=((s.selectedEnemy==0?s.enemyA:s.enemyB)-s.hero).Normalized;
                s.phase="attack-participation-model";
            }else{
                float approach=Clamp(t-1,0,2),side=Clamp(t-3,0,4),leap=Clamp(t-8,0,1.2f);
                float radius=4-.5f*approach;
                float angle=-(float)Math.PI/2+.7f*side/3;
                if(s.targetRelative)s.hero=new Point((float)Math.Cos(angle)*radius,(float)Math.Sin(angle)*radius);
                else s.hero=new Point(.7f*side,-radius);
                s.forwardInput=t>=1&&t<3?1:0;s.sideInput=t>=3&&t<7?1:0;
                if(t>=1&&t<3)s.phase="approach";
                if(t>=3&&t<7)s.phase="side-step";
                if(t>=8&&t<9.2f){
                    s.phase="illustrative-jump-in";float u=leap/1.2f;
                    s.hero=s.targetRelative?s.hero*(1-.4f*u):s.hero+new Point(1.2f*u,0);
                    s.heroY=.75f*(float)Math.Sin(Math.PI*u);
                }else if(t>=9.2f){s.hero=s.targetRelative?s.hero*.6f:s.hero+new Point(1.2f,0);s.phase="hold-after-jump";}
                s.heroForward=s.targetRelative?(s.enemyA-s.hero).Normalized:
                    (t>=3?new Point(1,0):new Point(0,1));
            }
            Point target=s.selectedEnemy==0?s.enemyA:s.enemyB;
            s.radialDistance=(target-s.hero).Length;
            s.facingDot=Point.Dot(s.heroForward,(target-s.hero).Normalized);
            s.attackParticipants=(s.attackA?1:0)+(s.attackB?1:0);
            return s;
        }
    }
}
