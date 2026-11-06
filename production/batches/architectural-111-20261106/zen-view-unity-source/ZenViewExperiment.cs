using System;
using UnityEngine;

namespace Yamyam.Architectural111.ZenView {
    [Serializable] public sealed class ZenViewConfig {
        public int frames,fps,width,height;
        public float pathStartX,pathEndX,pathZ,eyeHeight,frontZ,backZ,frontCenterX,backCenterX;
        public float wallLeftX,wallRightX,wallHeight,openingBottom,openingTop,narrowWidth,wideWidth;
        public float targetX,targetY,targetZ,verticalFieldOfView,observerX,observerY,observerZ,observerOrthographicSize;
    }
    [Serializable] public sealed class ZenRay {
        public string target;
        public Vector3 origin,desiredEndpoint,actualEndpoint;
        public bool blocked,inFrustum,visible;
    }
    [Serializable] public sealed class ZenFrameRays { public int frame; public ZenRay[] rays; }
    [Serializable] public sealed class ZenAnchor {
        public string name;public Vector3 world,playerViewport,observerViewport;
    }
    [Serializable] public sealed class ZenFrameAnchors { public int frame; public ZenAnchor[] anchors; }

    // Original visibility experiment. No commercial-game renderer/intent claim.
    public sealed class ZenViewExperiment : MonoBehaviour {
        public const int WallLayer=26,LintelLayer=27,ActorLayer=28,GuideLayer=29;
        public ZenViewConfig config;
        public float openingWidth;
        public Camera playerCamera,observerCamera;
        public Transform actor,actorModel;
        public AnimationClip walkingClip;
        public Vector3 modelBasePosition,modelBaseScale;
        public Quaternion modelBaseRotation;
        public LineRenderer[] sightLines;
        public LineRenderer frontOpening,backOpening;
        public ZenRay[] CurrentRays { get; private set; }
        public bool CenterVisible { get; private set; }
        public int VisibleSampleCount { get; private set; }
        public int SampleCount => 5;
        public int Frame { get; private set; }
        float elapsed;
        public Vector3 Eye => playerCamera.transform.position;
        public Vector3 Target => new Vector3(config.targetX,config.targetY,config.targetZ);
        public int WallMask => (1<<WallLayer)|(1<<LintelLayer);

        void Start(){elapsed=0;SetFrame(0);}
        void Update(){
            if(!Application.isPlaying||config==null)return;
            elapsed=Mathf.Min(elapsed+Time.deltaTime,(config.frames-1f)/config.fps);
            SetFrame(Mathf.FloorToInt(elapsed*config.fps));
        }
        public Vector3 OpeningPoint(bool back,bool right) {
            return new Vector3((back?config.backCenterX:config.frontCenterX)+(right?1:-1)*openingWidth*.5f,
                config.eyeHeight,back?config.backZ:config.frontZ);
        }
        bool InCamera(Vector3 point) {
            Vector3 p=playerCamera.WorldToViewportPoint(point);
            return p.z>0&&p.x>=0&&p.x<=1&&p.y>=0&&p.y<=1;
        }
        public ZenRay Cast(string name,Vector3 endpoint) {
            Vector3 delta=endpoint-Eye;RaycastHit hit;
            bool blocked=Physics.Raycast(Eye,delta.normalized,out hit,delta.magnitude-.0001f,WallMask,QueryTriggerInteraction.Ignore);
            bool inside=InCamera(endpoint);
            return new ZenRay{target=name,origin=Eye,desiredEndpoint=endpoint,actualEndpoint=blocked?hit.point:endpoint,
                blocked=blocked,inFrustum=inside,visible=inside&&!blocked};
        }
        Vector3 ExtendToVista(Vector3 direction) {
            float length=direction.z>.00001f?(config.targetZ-Eye.z)/direction.z:20f;
            return Eye+direction*length;
        }
        void OpeningFrame(LineRenderer line,bool back) {
            float x=back?config.backCenterX:config.frontCenterX,z=back?config.backZ:config.frontZ,h=openingWidth*.5f;
            line.positionCount=5;
            line.SetPositions(new[]{new Vector3(x-h,config.openingBottom,z),new Vector3(x+h,config.openingBottom,z),
                new Vector3(x+h,config.openingTop,z),new Vector3(x-h,config.openingTop,z),new Vector3(x-h,config.openingBottom,z)});
        }
        public void SetFrame(int frame) {
            if(config==null)throw new InvalidOperationException("Missing immutable capture config");
            Frame=Mathf.Clamp(frame,0,config.frames-1);float t=Frame/(float)(config.frames-1);
            float x=Mathf.Lerp(config.pathStartX,config.pathEndX,t);
            actor.position=new Vector3(x,0,config.pathZ);
            playerCamera.transform.position=new Vector3(x,config.eyeHeight,config.pathZ);
            playerCamera.transform.rotation=Quaternion.LookRotation(new Vector3(
                (config.backCenterX-config.frontCenterX)/(config.backZ-config.frontZ),0,1));
            if(walkingClip)walkingClip.SampleAnimation(actorModel.gameObject,Mathf.Repeat(Frame/(float)config.fps,walkingClip.length));
            actorModel.localPosition=modelBasePosition;actorModel.localRotation=modelBaseRotation;actorModel.localScale=modelBaseScale;
            Physics.SyncTransforms();
            Vector3[] samples={Target,Target+new Vector3(-1.25f,-1.4f,0),Target+new Vector3(1.25f,-1.4f,0),
                Target+new Vector3(0,.7f,0),Target+new Vector3(0,-.7f,0)};
            VisibleSampleCount=0;
            for(int i=0;i<samples.Length;i++)if(Cast("sample-"+i,samples[i]).visible)VisibleSampleCount++;
            CurrentRays=new ZenRay[7];CurrentRays[0]=Cast("fixed-landmark-center",Target);CenterVisible=CurrentRays[0].visible;
            for(int i=0;i<4;i++) {
                bool back=i>=2,right=(i%2)==1;Vector3 corner=OpeningPoint(back,right);
                CurrentRays[i+1]=Cast((back?"back":"front")+(right?"-right":"-left"),ExtendToVista(corner-Eye));
            }
            for(int i=0;i<2;i++) {
                Vector3 direction=playerCamera.ViewportPointToRay(new Vector3(i,.5f,0)).direction;
                CurrentRays[5+i]=Cast(i==0?"camera-left-FOV":"camera-right-FOV",ExtendToVista(direction));
            }
            for(int i=0;i<sightLines.Length;i++) {
                var ray=CurrentRays[i];var line=sightLines[i];line.positionCount=2;line.SetPositions(new[]{ray.origin,ray.actualEndpoint});
                Color c=i==0?(ray.visible?new Color(.25f,.95f,.69f):new Color(1,.25f,.20f)):
                    i<3?new Color(.25f,.75f,1):i<5?new Color(1,.82f,.32f):new Color(.6f,.65f,.65f);
                line.startColor=line.endColor=c;
            }
            OpeningFrame(frontOpening,false);OpeningFrame(backOpening,true);
        }
        public ZenFrameAnchors ProjectedAnchors() {
            var points=new System.Collections.Generic.List<ZenAnchor>();
            Action<string,Vector3> add=(name,p)=>points.Add(new ZenAnchor{name=name,world=p,
                playerViewport=playerCamera.WorldToViewportPoint(p),observerViewport=observerCamera.WorldToViewportPoint(p)});
            add("eye",Eye);add("landmark-center",Target);add("actor-ground",actor.position);
            for(int i=0;i<4;i++)add((i>=2?"back":"front")+(i%2==1?"-right":"-left"),OpeningPoint(i>=2,i%2==1));
            for(int i=0;i<CurrentRays.Length;i++)add(CurrentRays[i].target+"-actual-end",CurrentRays[i].actualEndpoint);
            return new ZenFrameAnchors{frame=Frame,anchors=points.ToArray()};
        }
    }
}
