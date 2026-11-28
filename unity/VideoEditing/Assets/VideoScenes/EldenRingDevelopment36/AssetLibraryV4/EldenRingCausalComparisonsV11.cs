using System;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        // Each demonstration controls a cause; the compositor supplies source-grounded Korean labels.
        Action<float> CausalPrototype()
        {
            Floor("Same test route",0,0,10,6,0,Slate);
            var walls=new[]{Block("Left reusable wall",V(-1,1,0),V(2,2,.55f),Paper),
                Block("Right reusable wall",V(1,1,0),V(2,2,.55f),Paper)};
            var walker=Pawn("Character tests the opening",V(0,.02f,-2.2f),Gold);
            var width=Bar("Opening width",V(-.2f,.1f,0),V(.2f,.1f,0),.09f,Red);
            var detail=Group("Add art only after passage works",Vector3.zero);
            for(int side=-1;side<=1;side+=2)
                Attach("rock",ChildCausal(detail,"Detailed same-width wall",V(side*2.2f,0,0)),V(1.8f,2,.6f),true);
            FrameCamera(V(4.5f,5,-8),V(0,.6f,0),3.6f);
            return t=>{
                float edit=Second?Range(t,.35f,.52f):0;
                float half=Mathf.Lerp(.2f,1.2f,edit);
                walls[0].position=V(-half-1,1,0);walls[1].position=V(half+1,1,0);
                Segment(width,V(-half,.08f,0),V(half,.08f,0),.09f);Tint(width,edit>.8f?Aqua:Red);
                float walk=Second&&t>.52f?Range(t,.55f,.90f):Range(t,.04f,.28f);
                walker.position=V(0,.02f,Mathf.Lerp(-2.2f,Second&&t>.52f?2.2f:-.55f,walk));
                detail.gameObject.SetActive(Second&&t>.91f);
            };
        }

        Transform ChildCausal(Transform parent,string name,Vector3 p)
        {
            var child=Group(name,p);child.SetParent(parent,false);return child;
        }

        Action<float> CausalAtmosphere()
        {
            Floor("Same field in both tests",0,1,10,10,0,new Color(.29f,.38f,.25f));
            Attach("rock",Group("Fixed rock",V(0,0,0)),V(2.2f,1.8f,2),true);
            Attach("tower",Group("Distant structure",V(2,0,5)),V(1.7f,3.2f,1.7f),true);
            var actor=Pawn("Scale reference",V(-2,.02f,-.5f),Gold);
            var light=stage.Find("Key light").GetComponent<Light>();
            var ambient=RenderSettings.ambientLight;
            FrameCamera(V(4,3.7f,-8),V(0,1.1f,1),3.4f);
            return t=>{
                float dusk=Range(t,.24f,.8f);
                view.backgroundColor=Color.Lerp(new Color(.45f,.62f,.78f),new Color(.24f,.14f,.23f),dusk);
                light.color=Second?Color.Lerp(Color.white,new Color(1,.57f,.35f),dusk):Color.white;
                light.intensity=Second?Mathf.Lerp(1.18f,.4f,dusk):1.18f;
                RenderSettings.ambientLight=Second?Color.Lerp(ambient,new Color(.17f,.12f,.23f),dusk):ambient;
                RenderSettings.fog=Second;RenderSettings.fogMode=FogMode.Exponential;
                RenderSettings.fogDensity=Second?Mathf.Lerp(.005f,.035f,dusk):0;
                RenderSettings.fogColor=Color.Lerp(new Color(.55f,.64f,.72f),new Color(.32f,.23f,.3f),dusk);
                actor.position=V(-2+.2f*Mathf.Sin(t*2),.02f,-.5f);
            };
        }

        Action<float> CausalFlowers()
        {
            Floor("Meadow",0,1,10,9,0,new Color(.20f,.31f,.24f));
            Floor("Path remains fixed",0,1,1.3f,9,.01f,Slate);
            var flowers=new Transform[18];
            for(int i=0;i<18;i++){
                var g=Group("Move selected near flower",V((i%3-1)*.4f,0,-1.8f+(i/3)*.7f));flowers[i]=g;
                Block("Stem",V(0,.3f,0),V(.05f,.6f,.05f),Aqua,g);
                for(int k=0;k<5;k++){float a=k*Mathf.PI*2/5;Orb("Petal",V(Mathf.Cos(a)*.13f,.6f,Mathf.Sin(a)*.13f),.19f,Blue,g);}
            }
            for(int i=0;i<24;i++)Block("Distant colored flower patch",V(-4+(i%8)*1.05f,.03f,4+(i/8)*.45f),V(.6f,.04f,.4f),Blue);
            var walker=Pawn("Traveler needs a readable path",V(0,.02f,-3.2f),Gold);
            FrameCamera(V(3.4f,4.2f,-7.4f),V(0,.4f,1),3.6f);
            return t=>{
                float edit=Range(t,.22f,.58f);
                for(int i=0;i<flowers.Length;i++){
                    float x=(i%3-1)*.4f;float target=(i%2==0?-1:1)*(1.1f+(i%3)*.28f);
                    flowers[i].position=V(Mathf.Lerp(x,target,edit),0,-1.8f+(i/3)*.7f);
                }
                walker.position=V(0,.02f,Mathf.Lerp(-3.2f,3.6f,Range(t,.60f,.95f)));
            };
        }

        Action<float> CausalLandmark()
        {
            var old=ObservedLandmark16();
            // Same traverse is repeated after the pillar edit, rather than changing the camera and pillar together.
            return t=>{
                float u=Second?(t<.45f?t/.45f:(t-.55f)/.45f):t;
                old(Mathf.Clamp01(u));
                var pillar=stage.Find("Near pillar masking distant outline");
                if(pillar) pillar.position=V(Second&&t>=.5f?-1.6f:.12f,1,1.28f);
            };
        }

        Action<float> CausalHistory()
        {
            Floor("Three teaching stages",0,0,10,6,0,Slate);
            var past=Pawn("Past relationship A",V(-3,.02f,.5f),Gold);
            var related=Pawn("Past relationship B",V(-2,.02f,1.6f),Blue);
            var relation=Bar("Relationship becomes a design input",V(-2.6f,1,.5f),V(-2.2f,1,1.6f),.08f,Paper);
            var present=Pawn("Current encounter derived from background",V(.2f,.02f,.5f),Red);
            Attach("tower",Group("Trace in a present place",V(2.8f,0,1.4f)),V(1.2f,2.3f,1.2f),true);
            var viewer=Pawn("Player discovers the trace",V(4,.02f,-1.5f),Aqua);
            var links=new[]{Bar("Past to present",V(-1.5f,.3f,.5f),V(-.3f,.3f,.5f),.09f,Slate),
                Bar("Present to trace",V(.8f,.3f,.5f),V(2.1f,.3f,.5f),.09f,Slate)};
            FrameCamera(V(4,6,-10),V(0,.7f,.5f),3.9f);
            return t=>{
                present.gameObject.SetActive(t>.30f);Tint(links[0],t>.25f?Aqua:Slate);Tint(links[1],t>.55f?Aqua:Slate);
                viewer.position=Vector3.Lerp(V(4,.02f,-1.5f),V(2.8f,.02f,.3f),Range(t,.6f,.94f));
            };
        }

        Action<float> CausalHandoff(bool experience)
        {
            var walk=CausalPrototype();
            var checks=new Transform[4];
            for(int i=0;i<4;i++)checks[i]=Block("Interdependent review item "+i,V(-3.6f+i*2.4f,.12f,-2.9f),V(1.6f,.14f,.4f),Slate);
            var enemy=Pawn("Route must be checked after wall revision",V(2.5f,.02f,2),Red);
            var path=Bar("Revised traversal link",V(0,.12f,-1),V(0,.12f,1),.09f,Aqua);
            return t=>{
                walk(Second?t:Mathf.Min(t,.45f));
                for(int i=0;i<4;i++)Tint(checks[i],t>.13f+i*.21f?Aqua:Slate);
                enemy.position=V(Mathf.Lerp(2.5f,0,Range(t,.50f,.72f)),.02f,Mathf.Lerp(2,-1,Range(t,.73f,.95f)));
                path.gameObject.SetActive(t>.50f);
                if(experience)for(int i=0;i<4;i++)checks[i].localScale=V(1.6f,.14f+(Second?.14f:0),.4f);
            };
        }

        Action<float> CausalDetour()
        {
            Floor("Same encounter and surrounding field",0,0,10,6,0,Slate);
            var foe=Pawn("Encounter remains unchanged",V(2,.02f,0),Red);foe.localScale=Vector3.one*1.5f;
            var hero=Pawn("Return with new preparation",V(-4,.02f,0),Gold);
            var item=Orb("Preparation on alternate route",V(-.5f,.6f,2),.35f,Aqua);
            Route(Aqua,V(-2,.06f,0),V(-2,.06f,2),V(.5f,.06f,2),V(.5f,.06f,0));
            FrameCamera(V(4,6,-9),V(0,.6f,0),3.8f);
            return t=>{
                Vector3 p;
                if(t<.25f)p=Vector3.Lerp(V(-4,.02f,0),V(-2,.02f,0),Range(t,.02f,.25f));
                else if(t<.5f)p=Vector3.Lerp(V(-2,.02f,0),V(-.5f,.02f,2),Range(t,.27f,.5f));
                else p=Vector3.Lerp(V(-.5f,.02f,2),V(.5f,.02f,0),Range(t,.60f,.93f));
                hero.position=p;item.gameObject.SetActive(t<.54f);
                if(t>.54f)Tint(foe,Red); // Opponent deliberately does not become weaker.
            };
        }

        Action<float> CausalExperience()
        {
            Floor("Planning testing revision",0,0,10,6,0,Slate);
            var worker=Pawn("Developer checks the next prototype",V(-3.3f,.02f,-1.2f),Gold);
            var pads=new Transform[3];var records=new Transform[3];
            for(int i=0;i<3;i++){
                pads[i]=Block("Work stage "+i,V(-3+i*3,.10f,.3f),V(2.2f,.18f,1.8f),Paper);
                records[i]=Block("Experience recorded from stage "+i,V(-3+i*3,.25f,2),V(1.7f,.2f,.65f),Slate);
            }
            Block("Prototype wall left",V(-.65f,.65f,.3f),V(.5f,1.1f,.4f),Paper);
            var right=Block("Revised prototype wall",V(.65f,.65f,.3f),V(.5f,1.1f,.4f),Paper);
            var priority=Ring("Previously learned item selected before testing",V(0,.23f,.3f),.8f,Gold);
            Route(Aqua,V(-3,.21f,-.5f),V(0,.21f,-.5f),V(3,.21f,-.5f));
            FrameCamera(V(3.5f,6,-10),V(0,.6f,.3f),3.5f);
            return t=>{
                for(int i=0;i<3;i++){
                    bool known=Second || t>.22f+i*.26f;
                    Tint(records[i],known?Aqua:Slate);
                    records[i].localScale=V(1.7f,known?.28f:.06f,.65f);
                    Tint(pads[i],Mathf.Abs(t-(.16f+i*.3f))<.2f?Gold:Paper);
                }
                priority.gameObject.SetActive(Second && t<.45f);
                // The next project consults the record before testing; no invented measured time saving.
                float route=Second?Range(t,.24f,.85f):Range(t,.06f,.9f);
                worker.position=V(-3.3f+route*6.3f,.02f,-1.2f);
                right.position=V(.65f+Range(t,.55f,.76f)*.65f,.65f,.3f);
            };
        }

        Action<float> CausalWeight()
        {
            Floor("Same weapons and equal comparison lanes",0,0,10,6,0,Slate);
            var rigs=new WalkthroughActor[2];var roots=new Transform[2];
            for(int i=0;i<2;i++){
                roots[i]=Pawn("Same sword motion comparison "+i,V(i==0?-1.35f:1.35f,.02f,0),i==0?Aqua:Gold);
                rigs[i]=walkthroughActors[walkthroughActors.Count-1];rigs[i].FixedFacing=true;
                var tool=Group("Identical shared sword",Vector3.zero);Attach("sword",tool,V(.3f,1.3f,.3f),true);
                var rig=rigs[i];rig.AfterPose=()=>{tool.position=rig.Arms[1].End.position;tool.rotation=rig.Root.rotation*Quaternion.Euler(20+rig.Cast*55,0,0);};
            }
            FrameCamera(V(0,2.2f,-7),V(0,.9f,0),2.05f);
            return t=>{
                for(int i=0;i<2;i++){
                    float prepare=Range(t,.12f,.40f),swing=Range(t,.45f,.64f),recover=Range(t,.69f,.93f);
                    rigs[i].Cast=Mathf.Clamp01(prepare-.55f*swing-.45f*recover);
                    float turn=i==0?0:-42*prepare+88*swing-46*recover;
                    roots[i].rotation=Quaternion.Euler(0,160+turn,0);
                    roots[i].position=V((i==0?-1.35f:1.35f)+(i==0?0:.28f*swing-.28f*recover),.02f,0);
                }
            };
        }

        Action<float> CausalChoir()
        {
            var old=ObservedChoir28();
            // Source of the sound and its location are explanatory; never synthesize an alleged original recording.
            return t=>old(t);
        }

        Action<float> CausalProjection()
        {
            var old=ObservedProjection();
            var sticker=Footprint(V(-1,.06f,-.65f));
            Vector3 screen=Vector3.zero;bool initial=true;
            return t=>{
                old(t);
                if(initial){screen=view.WorldToViewportPoint(V(-1,.06f,-.65f));initial=false;}
                // Intentionally wrong screen-fixed comparator, distinct from the retained reconstructed surface point.
                sticker.position=view.ViewportToWorldPoint(screen);sticker.gameObject.SetActive(!Second&&t<.5f);
            };
        }

        Action<float> CausalCooperation()
        {
            Floor("Summoning before shared battle",0,0,10,6,0,Slate);
            var host=Pawn("Host chooses a player summon sign",V(-3,.02f,-1),Gold);
            var sign=Ring("Player summon sign",V(-1,.04f,-1),.5f,Aqua);
            var guest=Pawn("Other player joins after selection",V(-1,.02f,-1),Aqua);
            var foe=Pawn("Same opponent for both players",V(3,.02f,1),Red);foe.localScale=Vector3.one*1.4f;
            var hostRig=walkthroughActors[walkthroughActors.Count-3];var guestRig=walkthroughActors[walkthroughActors.Count-2];
            FrameCamera(V(4,5,-9),V(0,.8f,0),3.7f);
            return t=>{
                host.position=Vector3.Lerp(V(-3,.02f,-1),V(-1.8f,.02f,-1),Range(t,.04f,.24f));
                bool joined=t>=.43f;guest.gameObject.SetActive(joined);sign.gameObject.SetActive(t<.55f);
                if(joined){
                    float move=Range(t,.55f,.82f);
                    host.position=Vector3.Lerp(V(-1.8f,.02f,-1),V(1.5f,.02f,.3f),move);
                    guest.position=Vector3.Lerp(V(-1,.02f,-1),V(2.5f,.02f,-.5f),move);
                }
                hostRig.Cast=Range(t,.83f,.93f);guestRig.Cast=Range(t,.87f,.98f);
            };
        }
    }
}
