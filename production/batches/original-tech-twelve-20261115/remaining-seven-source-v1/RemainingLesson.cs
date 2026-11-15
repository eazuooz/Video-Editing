using System;
using System.Linq;
using UnityEngine;
namespace Yamyam.OriginalTechTwelve.RemainingSeven {
    // These are authored teaching models. The original games' code, controls,
    // collision systems, timings and performance are not reproduced here.
    public sealed class RemainingLesson : MonoBehaviour {
        public string topic,mode;public bool livePlayback;
        public string[] actorIds;public Transform[] actors,animatedChildren;
        public string[] linkA,linkB,linkColors;public LineRenderer[] relationships;
        public Camera overview,detail;public AnimationClip idle,walk;
        public string[] colorNames;public Color[] colors;public State current;float elapsed;
        static Vector3 Vec(V v){return new Vector3(v.x,v.y,v.z);}
        void Update(){if(livePlayback){elapsed=(elapsed+Time.deltaTime)%12;Apply(Mathf.Min(719,(int)(elapsed*60)));}}
        public void Apply(int frame){
            current=RuleModels.Sample(topic,mode,frame);
            for(int i=0;i<actorIds.Length;i++){
                var pose=current.poses.Single(p=>p.id==actorIds[i]);var tr=actors[i];tr.gameObject.SetActive(pose.visible);
                tr.position=Vec(pose.p);tr.rotation=Quaternion.Euler(Vec(pose.euler));tr.localScale=Vec(pose.size);
                int colorIndex=Array.IndexOf(colorNames,pose.color);if(colorIndex>=0){var block=new MaterialPropertyBlock();block.SetColor("_Color",colors[colorIndex]);foreach(var renderer in tr.GetComponentsInChildren<Renderer>(true))renderer.SetPropertyBlock(block);}
                if(animatedChildren[i]&&idle){
                    var child=animatedChildren[i];var scale=child.localScale;
                    bool moving=topic=="spiderman"||topic=="ratchet"&&(frame>=120&&frame<480)||topic=="doom"&&(mode=="a"||frame<360);
                    var clip=moving&&walk?walk:idle;clip.SampleAnimation(child.gameObject,frame/60f%Mathf.Max(.01f,clip.length));
                    child.localPosition=Vector3.zero;child.localRotation=Quaternion.identity;child.localScale=scale;
                }
                if(pose.kind=="kart"){
                    bool anti=mode=="b";foreach(Transform wheel in tr)if(wheel.name.StartsWith("Wheel"))wheel.localRotation=Quaternion.Euler(anti?0:0,0,anti?0:90);
                }
            }
            for(int i=0;i<relationships.Length;i++){
                var link=current.links[i];int a=Array.IndexOf(actorIds,link.a),b=Array.IndexOf(actorIds,link.b);
                // A broken connection is absent, rather than an intact-looking red bond.
                relationships[i].enabled=link.color!="problem"&&actors[a].gameObject.activeSelf&&actors[b].gameObject.activeSelf;
                relationships[i].SetPosition(0,actors[a].position);relationships[i].SetPosition(1,actors[b].position);
            }
            if(topic=="mariokart8"){
                // Identical reference camera motion in both modes. It never follows
                // the faster kart and thereby hides its movement against the track.
                float referenceZ=-6+current.seconds*2;
                detail.transform.position=new Vector3(5,4,referenceZ-7);detail.transform.LookAt(new Vector3(0,.5f,referenceZ+1));
            }
        }
    }
}
