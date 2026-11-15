using System;
using System.Collections.Generic;
namespace Yamyam.OriginalTechTwelve.RemainingSeven {
    [Serializable] public struct V {
        public float x,y,z;public V(float x,float y,float z=0){this.x=x;this.y=y;this.z=z;}
        public static V operator+(V a,V b){return new V(a.x+b.x,a.y+b.y,a.z+b.z);}public static V operator-(V a,V b){return new V(a.x-b.x,a.y-b.y,a.z-b.z);}public static V operator*(V a,float s){return new V(a.x*s,a.y*s,a.z*s);}
        public float Length{get{return(float)Math.Sqrt(x*x+y*y+z*z);}}public V Unit{get{return this*(1/Math.Max(.000001f,Length));}}public static float Dot(V a,V b){return a.x*b.x+a.y*b.y+a.z*b.z;}
    }
    [Serializable] public class Pose {public string id,kind,color;public V p,size,euler;public bool visible=true;}
    [Serializable] public class Link {public string a,b,color;public float width=.065f;}
    [Serializable] public class State {
        public string topic,mode,phase;public int frame,health,ammo,fuel,activeNodes;public float seconds,ropeLength,ropeError,speed,collisionSeconds=-1,impulseStrength,bondStrength;public bool burning,ready,bondsBroken,parented;
        public List<Pose> poses=new List<Pose>();public List<Link> links=new List<Link>();
    }
    public static class RuleModels {
        public static readonly string[] Topics={"spiderman","control","returnal","ratchet","doom","botw","mariokart8"};
        public static readonly string[] Modes={"a","b"};
        static readonly Dictionary<string,V[]> SwingPositions=new Dictionary<string,V[]>();
        static float Sin(float t){return(float)Math.Sin(t);}static float Cos(float t){return(float)Math.Cos(t);}static float Max(float a,float b){return Math.Max(a,b);}
        static void Add(State s,string id,string kind,V p,V size,string color,V euler=default(V),bool visible=true){s.poses.Add(new Pose{id=id,kind=kind,p=p,size=size,color=color,euler=euler,visible=visible});}
        static void Line(State s,string a,string b,string color,float width=.065f){s.links.Add(new Link{a=a,b=b,color=color,width=width});}
        public static State Sample(string topic,string mode,int frame){
            if(Array.IndexOf(Topics,topic)<0||Array.IndexOf(Modes,mode)<0||frame<0||frame>=720)throw new ArgumentException("Exact selected teaching case and frame required");
            var s=new State{topic=topic,mode=mode,frame=frame,seconds=frame/60f};
            switch(topic){case"spiderman":Swing(s);break;case"control":Break(s);break;case"returnal":Tentacle(s);break;case"ratchet":Streaming(s);break;case"doom":Recovery(s);break;case"botw":Chemistry(s);break;case"mariokart8":Kart(s);break;}return s;
        }
        static void Swing(State s){
            V anchor=new V(0,s.mode=="a"?7:10),start=new V(-4,2),velocity=new V(3,0);float length=(start-anchor).Length;
            V[] positions;if(!SwingPositions.TryGetValue(s.mode,out positions)){
                positions=new V[720];positions[0]=start;V p=start,v=velocity;float dt=1/60f;
                for(int i=1;i<positions.Length;i++){v+=new V(0,-9.81f)*dt;p+=v*dt;var radial=(p-anchor).Unit;p=anchor+radial*length;v-=radial*V.Dot(v,radial);positions[i]=p;}
                SwingPositions.Add(s.mode,positions);
            }
            var position=positions[s.frame];s.ropeLength=length;s.ropeError=Math.Abs((position-anchor).Length-length);s.phase="same launch input; selected anchor height changes";
            Add(s,"hero","hero",position-new V(0,.8f),new V(1.5f,1.5f,1.5f),"hero");Add(s,"body-point","sphere",position,new V(.14f,.14f,.14f),"relation");Add(s,"anchor","sphere",anchor,new V(.34f,.34f,.34f),"relation");Line(s,"body-point","anchor","relation",.08f);
            Add(s,"building","cube",new V(0,5,3),new V(5,10,2),"structure");Add(s,"attachment-face","cube",new V(0,anchor.y,1.7f),new V(.5f,.5f,.2f),"changed");Line(s,"anchor","attachment-face","muted");
        }
        static void Break(State s){
            float age=Max(0,s.seconds-3);s.impulseStrength=s.mode=="b"?8:2;s.bondStrength=4;s.bondsBroken=s.impulseStrength>s.bondStrength&&age>0;s.phase=s.bondsBroken?"central bonds released":"prepared connections hold";
            for(int i=0;i<5;i++){float y=2,rz=0;if(i==2&&s.bondsBroken){y=Max(.14f,2-4.905f*age*age);rz=age*55;}Add(s,"board"+i,"cube",new V(i-2,y,0),new V(.98f,.17f,1.7f),"wood",new V(0,0,rz));if(i>0)Line(s,"board"+(i-1),"board"+i,s.bondsBroken&&(i==2||i==3)?"problem":"relation",.06f);}
            for(int x=-1;x<=1;x+=2)for(int z=-1;z<=1;z+=2)Add(s,"leg"+x+z,"cube",new V(x*1.8f,.95f,z*.65f),new V(.18f,1.9f,.18f),"wood");
            Add(s,"impact-input","sphere",new V(0,2.45f,0),new V(.35f,.35f,.35f),"changed",visible:s.seconds>=3&&s.seconds<3.3f);
            for(int i=0;i<18;i++){float a=i*2.39996f;var p=new V(Sin(a)*age*.9f,2+age*.65f-age*age,Cos(a)*age*.8f);Add(s,"dust"+i,"sphere",p,new V(.055f,.055f,.055f),"dust",visible:s.bondsBroken&&age<1.4f&&p.y>.05f);}
        }
        static void Tentacle(State s){
            var root=new V(1.5f*Sin(s.seconds*.8f),.5f,0);float rotation=.65f*Sin(s.seconds*.6f);s.parented=s.mode=="b";s.activeNodes=14;s.phase=s.parented?"local nodes inherit the moving root":"same local curve, without root inheritance";Add(s,"root","sphere",root,new V(.6f,.6f,.6f),"changed");
            for(int i=0;i<14;i++){
                var local=new V(.45f*Sin(s.seconds*2-i*.38f),.4f+i*.28f,.35f*Cos(s.seconds*1.3f-i*.25f));var transformed=new V(local.x*Cos(rotation)+local.z*Sin(rotation),local.y,-local.x*Sin(rotation)+local.z*Cos(rotation));var p=s.parented?root+transformed:new V(0,.5f)+local;
                Add(s,"node"+i,"sphere",p,new V(.13f,.13f,.13f),"relation");Line(s,i==0?"root":"node"+(i-1),"node"+i,"relation",.07f);
                for(int j=0;j<3;j++)Add(s,"particle"+i+"-"+j,"sphere",p+new V(.14f*Sin(j*2.1f+s.seconds),0,.14f*Cos(j*2.1f+s.seconds)),new V(.045f,.045f,.045f),"ink");
            }
        }
        static void Streaming(State s){
            float begin=s.mode=="a"?0:4,readDone=begin+1.4f,readyAt=readDone+1.1f;s.ready=s.seconds>=readyAt;s.phase=s.seconds<begin?"not requested":s.seconds<readDone?"reading":!s.ready?"decompressing":"ready";
            Add(s,"hero","hero",new V(0,0,-4+Math.Min(8,Max(0,s.seconds-2)*1.333333f)),new V(1.4f,1.4f,1.4f),"hero");Add(s,"portal","portal",new V(0,2,0),new V(2,2,2),"relation");
            for(int i=0;i<4;i++){Add(s,"source"+i,"cube",new V((i%2==0?-1:1)*3.6f,1.5f,-2.5f-i/2f),new V(1.6f,3,1.5f),"structure");Add(s,"destination"+i,"cube",new V((i%2==0?-1:1)*3.2f,1.0f+i*.3f,3.2f+i/2f),new V(1.8f,2+i*.6f,1.8f),"changed",visible:s.ready);}
            Add(s,"pending-destination","wire-box",new V(0,2.1f,4),new V(8,4.2f,4),"problem",visible:!s.ready);
        }
        static void Recovery(State s){
            bool advance=s.mode=="b";float distance=advance?Max(.9f,5-s.seconds*1.4f):5+s.seconds*.25f;bool finish=advance&&s.seconds>=3;float next=Math.Max(0,Math.Min(1,(s.seconds-3)/3));V player=finish?new V(2*next,0,-.9f+1.2f*next):new V(0,0,-distance);bool saw=finish&&s.seconds>=7&&(player-new V(2.6f,0,1)).Length<=1.2f;
            s.health=finish?50:20;s.ammo=saw?28:8;s.fuel=saw?1:2;s.phase=saw?"fuel spent, ammunition reward":finish?"close finish, health reward":s.seconds>=1&&s.seconds<4?"stagger opportunity":"no finish yet";
            Add(s,"hero","hero",player,new V(1.6f,1.6f,1.6f),"hero",new V(0,finish?next<1?59:40.6f:0,0));Add(s,"enemy","hero",new V(0,0,0),new V(1.6f,1.6f,1.6f),s.seconds>=1&&s.seconds<4?"changed":"muted",visible:!finish);Add(s,"second-enemy","hero",new V(2.6f,0,1),new V(1.5f,1.5f,1.5f),"muted",visible:!saw);
            Add(s,"health-reward","sphere",new V(0,.5f,-.6f),new V(.3f,.3f,.3f),"result",visible:finish&&s.seconds<4.2f);Add(s,"ammo-reward","cube",new V(2.2f,.5f,.8f),new V(.35f,.25f,.3f),"relation",visible:saw&&s.seconds<8.3f);
        }
        static void Chemistry(State s){
            const float ignition=(-1.2f-.9f-.125f+4)/1.4f;bool rain=s.mode=="b"&&s.seconds>=5;s.burning=s.seconds>=ignition&&!rain;s.phase=rain?"water element extinguishes fire":s.burning?"fire changes wood state":"same dry wood before fire contact";
            Add(s,"wood","cube",new V(-1.2f,.45f,0),new V(1.8f,.9f,1.1f),s.burning?"burning-wood":"wood");Add(s,"other-material","cube",new V(2.3f,.4f,0),new V(.9f,.8f,1),"structure");
            Add(s,"fire-input","sphere",new V(-4+Math.Min(2.8f,s.seconds*1.4f),.9f,0),new V(.25f,.25f,.25f),"changed",visible:s.seconds<ignition);
            for(int i=0;i<18;i++){float age=(s.seconds*1.3f+i*.173f)%1;var p=new V(-1.2f+.35f*Sin(i*2.4f+age*3),.8f+age*1.2f,.25f*Cos(i*2.4f));Add(s,"flame"+i,"sphere",p,new V(.16f*(1-age*.6f),.26f,.16f),i%2==0?"changed":"title",visible:s.burning);}
            for(int i=0;i<24;i++){float age=(s.seconds*1.7f+i*.137f)%1;Add(s,"rain"+i,"sphere",new V(-2.7f+(i%6)*.6f,5-age*5,-.8f+(i/6)*.5f),new V(.035f,.16f,.035f),"water",visible:rain);}
        }
        static void Kart(State s){
            const float initialDistance=6,approachSpeed=2,combinedContactRadius=1.2f;float contact=(initialDistance-combinedContactRadius)/approachSpeed;float age=Max(0,s.seconds-contact);bool anti=s.mode=="b";s.collisionSeconds=contact;s.speed=s.seconds<contact?2:anti&&age<1.2f?2.7f:anti?2:1.3f;
            float z=s.seconds<contact?-6+2*s.seconds:anti?-1.2f+Math.Min(age,1.2f)*2.7f+Max(0,age-1.2f)*2:-1.2f+age*1.3f;float yaw=anti&&age<1.2f?age/1.2f*360:0;s.phase=s.seconds<contact?"same approach":anti?"contact triggers authored spin boost":"contact slows the authored kart";
            float otherZ=age*.5f,neededX=(float)Math.Sqrt(Max(0,combinedContactRadius*combinedContactRadius-(z-otherZ)*(z-otherZ)));float natural=.9f*(1-(float)Math.Exp(-age*3)),separation=Math.Max(natural,neededX);
            Add(s,"hero-kart","kart",new V(separation*.8f,.5f,z),new V(1,1,1),"hero",new V(0,yaw,0));Add(s,"other-kart","kart",new V(-separation*.2f,.5f,otherZ),new V(1,1,1),"muted");
            Add(s,"track","cube",new V(0,-.06f,10),new V(4,.1f,44),"structure");for(int i=-1;i<=1;i+=2)Add(s,"track-edge"+i,"cube",new V(i*2,.03f,10),new V(.07f,.04f,44),"relation");for(int i=-10;i<=30;i+=2)Add(s,"reference-road-mark"+i,"cube",new V(0,.001f,i),new V(.08f,.012f,.7f),"title");
        }
    }
}
