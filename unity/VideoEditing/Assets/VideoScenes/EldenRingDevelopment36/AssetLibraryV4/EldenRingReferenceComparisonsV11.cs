using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        Action<float> CausalStreamingReference()
        {
            FrameCamera(V(5,9,-12),V(0,.1f,0),4.1f);
            var cells=new Transform[7];var counters=new Transform[7];var rocks=new Transform[7];
            for(int i=0;i<7;i++) {
                float x=-4.2f+i*1.4f;
                cells[i]=Block("Prepared data region "+i,V(x,.02f,0),V(1.3f,.12f,2.5f),Slate);
                counters[i]=Block("One illustrative resident region "+i,V(-3.9f+i*.34f,.12f,2.0f),V(.24f,.2f,.4f),Aqua);
                rocks[i]=Group("Landscape object from region "+i,V(x,.12f,.8f));
                Attach("rock",rocks[i],V(.48f,.45f,.45f),true);
            }
            var player=Pawn("Same traveler route",V(-3.8f,.15f,-.3f),Gold);
            var bounds=Ring("Prepared neighborhood",V(-3.8f,.17f,0),1.55f,Aqua);
            var warning=Ring("Arrived before the next region was ready",V(0,.20f,-.3f),.35f,Red);
            Route(Paper,V(-4,.14f,-.3f),V(4,.14f,-.3f));
            return t=>{
                bool all=!Second&&t<.32f;bool late=!Second&&t>=.32f&&t<.76f;
                float motion=Second?Range(t,.08f,.72f):late?Range(t,.35f,.70f):Range(t,.78f,.97f);
                float x=Mathf.Lerp(-3.8f,3.8f,motion);player.position=V(x,.15f,-.3f);
                int cell=Mathf.Clamp(Mathf.RoundToInt((x+4.2f)/1.4f),0,6);int loaded=0;
                float local=(x+4.9f)/1.4f;bool lag=late&&(local-Mathf.Floor(local))<.38f;
                warning.gameObject.SetActive(lag);warning.position=V(x,.20f,-.3f);
                bounds.gameObject.SetActive(!all&&!late);bounds.position=V(x,.17f,0);
                for(int i=0;i<7;i++) {
                    bool resident=all||(late?i==Mathf.Max(0,cell-(lag?1:0)):Mathf.Abs(i-cell)<=1);
                    if(resident)loaded++;
                    Tint(cells[i],i==cell?Gold:resident?Aqua:Slate);
                    // The second shot separates the data diagram from the continuously visible landscape.
                    rocks[i].gameObject.SetActive(Second||resident);
                }
                for(int i=0;i<7;i++)counters[i].gameObject.SetActive(i<loaded);
            };
        }

        Action<float> CausalFaceReference()
        {
            var original=FaceLayersV8();
            var oldArrows=new List<GameObject>();
            foreach(Transform child in stage)if(child.name=="Surface normal direction")oldArrows.Add(child.gameObject);
            var left=stage.Find("Color texture only");var right=stage.Find("Same color with normal map");
            var normal=right.Find("Identical face surface").GetComponent<Renderer>().sharedMaterial;
            var light=stage.Find("Key light").GetComponent<Light>();
            var sameLeft=FaceNormalArrowV8(left,false,Aqua,-.012f);
            var sameRight=FaceNormalArrowV8(right,false,Aqua,-.012f);
            var changedRight=FaceNormalArrowV8(right,true,Gold,-.012f);
            string[] names={"Color texture sample","Scar placement mask sample","Tangent-space normal sample"};
            return t=>{
                original(0);foreach(var item in oldArrows)item.SetActive(false);
                float strength=Second?Range(t,.22f,.30f):0;
                normal.SetFloat("_BumpScale",strength);
                float sweep=Second?Range(t,.40f,.92f):Range(t,.72f,.95f);
                light.transform.rotation=Quaternion.LookRotation(V(Mathf.Lerp(-.88f,.88f,sweep),-.38f,.81f));
                sameLeft.SetActive(!Second||t<.40f);sameRight.SetActive(!Second||t<.22f);
                changedRight.SetActive(Second&&t>=.22f&&t<.40f);
                for(int i=0;i<3;i++) {
                    bool show=Second&&t>=.06f+i*.08f;
                    stage.Find(names[i]).gameObject.SetActive(show);stage.Find(names[i]+" frame").gameObject.SetActive(show);
                }
            };
        }

        Action<float> CausalBlessingCurve()
        {
            var prior=ObservedProgressCurve();
            var before=new List<Transform>();var after=new List<Transform>();
            foreach(Transform child in stage) {
                if(child.name=="Schematic earlier balance")before.Add(child);
                if(child.name=="Schematic adjusted balance")after.Add(child);
            }
            return t=>{
                prior(t);FrameCamera(V(.5f,5.1f,-8.5f),V(.0f,.74f,.21f),3.52f);
                for(int i=0;i<after.Count;i++) {
                    float reveal=Range(t,.20f+.076f*i,.32f+.086f*i);
                    float level=(i+1f)/after.Count;
                    // Qualitative only: early boost, slower later increments, and a slightly higher maximum.
                    float height=Mathf.Lerp(.04f,2.25f*Mathf.Sqrt(level),reveal);
                    after[i].localScale=V(.46f,height,.41f);
                    after[i].localPosition=V(-3.44f+i*1.12f,height/2,1.27f);
                    bool early=Second&&t<.77f&&i<3;
                    bool last=Second&&t>=.77f&&i==after.Count-1;
                    Tint(after[i],early||last?Gold:Aqua);Tint(before[i],early||last?Gold:Paper);
                }
            };
        }
    }
}
