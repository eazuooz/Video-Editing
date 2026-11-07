using System;
using UnityEngine;

namespace Yamyam.Architectural111.SolutionPathV3 {
    [Serializable] public sealed class Mode { public string id,sceneFile,changedVariable;public int sideVariant,templateVariant,enemyVariant;public bool construction,content,broken; }
    [Serializable] public sealed class Config {public int seed,frames,fps,width,height,traversalStartFrame,themeStartFrame,themeBlendFrames;public float cellSize,walkSpeed,gravity;public Mode[] modes;public int[] animationDiagnosticFrames;public Color themeFloorTarget,themeStoneTarget,themeWoodTarget;}
    [Serializable] public sealed class ModelPose { public Transform model;public Vector3 position,scale;public Quaternion rotation;[NonSerialized]public AnimationClip lastSampledClip;[NonSerialized]public float lastSampledTime; }
    [Serializable] public sealed class Anchor {public string id,meaning;public Transform target;public Vector3 localPoint;}
    [Serializable] public sealed class Projection {public string id,meaning;public Vector3 world,playerViewport,observerViewport;public bool active;public RayEvidence playerRay,observerRay;}
    [Serializable] public sealed class RayEvidence {public Vector3 origin,target,hitPoint;public string hitCollider;public bool hit,hitBeforeTarget;public float targetDistance,hitDistance;}
    [Serializable] public sealed class AnchorFrame {public int frame;public Projection[] anchors;}
    [Serializable] public sealed class State {
        public int frame,appliedCommandFrame,visibleConnectorCount,collisionFlags;public string mode,phase,sourceKind="our-own-implementation";
        public bool modelExitConnected,visiblePortExitConnected,exitReached;public float themeBlend;public Vector3 plannedPlayerPosition,playerPosition,requestedDelta,actualDelta,enemyPosition,enemyReferenceCenter,enemyOffsetDirection;
        public string[] contactColliderIds,contactColliderNames;public Vector3 playerCameraPosition,observerCameraPosition;public float[] playerVP,observerVP;
        public bool safePlayTested=false;public string connectivityDomain="room-graph/reciprocal modeled door ports; not platformer or safety proof";
    }
    public sealed class Experiment:MonoBehaviour {
        public const int WorldLayer=26,ContentLayer=27,PlayerLayer=28,GuideLayer=29;
        public Config config;public Mode mode;public Graph graph;public CharacterController player;public Transform enemy;public ModelPose playerModel,enemyModel;
        public AnimationClip idleClip,walkingClip;public Camera playerCamera,observerCamera;public GameObject[] connectorClosers,routeArrows,templateRoots;public int[] closerA,closerB;
        public GameObject contentRoot,exitVisualRoot;public Anchor[] anchorDefinitions;public Renderer[] themeRenderers;public Color[] themeBaseColors,themeTargetColors;public string[] themeRoles;public bool previewInPlayMode=true,manualStepMode;
        [NonSerialized]public Action<ModelPose,AnimationClip,float,string> animationDiagnosticObserver;
        public int Frame{get;private set;}public State CurrentState{get;private set;}
        float accumulator,vertical;Vector3 lastDelta,requested;int collisions,applied=-1;
        public Vector3 Center(int room){return new Vector3((room%4-1.5f)*config.cellSize,0,(1.5f-room/4)*config.cellSize);}
        public Vector3 PlannedPosition(int frame){
            float length=Mathf.Max(0,(frame-config.traversalStartFrame)/(float)config.fps)*config.walkSpeed;int segment=Mathf.FloorToInt(length/config.cellSize);
            if(segment>=graph.mandatoryRoute.Length-1)return Center(graph.exit);return Vector3.Lerp(Center(graph.mandatoryRoute[segment]),Center(graph.mandatoryRoute[segment+1]),length/config.cellSize-segment);
        }
        public void EnemyBasis(out Vector3 center,out Vector3 perpendicular){
            int best=-1;int middle=graph.mandatoryRoute.Length/2;
            for(int i=1;i<graph.mandatoryRoute.Length-1;i++){
                Vector3 incoming=Center(graph.mandatoryRoute[i])-Center(graph.mandatoryRoute[i-1]);Vector3 outgoing=Center(graph.mandatoryRoute[i+1])-Center(graph.mandatoryRoute[i]);
                if((incoming-outgoing).sqrMagnitude<1e-8f&&(best<0||Math.Abs(i-middle)<Math.Abs(best-middle)))best=i;
            }
            if(best<0)throw new InvalidOperationException("Selected threat illustration needs a straight route focus; do not substitute a world-axis offset");
            center=Center(graph.mandatoryRoute[best]);Vector3 tangent=(Center(graph.mandatoryRoute[best+1])-center).normalized;perpendicular=Vector3.Cross(Vector3.up,tangent).normalized;
        }
        int VisibleEdges(){if(!mode.construction)return graph.edges.Length;int main=graph.mandatoryRoute.Length-1;if(Frame<60)return 0;if(Frame<240)return Mathf.FloorToInt((Frame-60)/180f*main);if(Frame<360)return main+Mathf.FloorToInt((Frame-240)/120f*(graph.edges.Length-main));return graph.edges.Length;}
        public string Phase(){if(!mode.construction)return mode.broken?"single-port-negative":mode.content?"content-and-walk":"rooms-and-walk";return Frame<60?"empty-room-grid":Frame<240?"mandatory-path":Frame<360?"optional-and-sealed-rooms":Frame<450?"hand-authored-template-variants":"illustrative-content-pass";}
        void Start(){if(config==null)return;ResetExperiment();if(Application.isPlaying){playerCamera.enabled=true;observerCamera.enabled=false;}}
        void Update(){if(!Application.isPlaying||!previewInPlayMode||config==null)return;if(Input.GetKeyDown(KeyCode.R)){ResetExperiment();return;}if(manualStepMode){if(Input.GetKeyDown(KeyCode.Space)&&Frame<config.frames-1)AdvanceOneFrame();return;}accumulator+=Time.deltaTime;while(accumulator>=1f/config.fps&&Frame<config.frames-1){AdvanceOneFrame();accumulator-=1f/config.fps;}}
        public void ResetExperiment(){
            if(config==null||graph==null||!player)throw new InvalidOperationException("Missing own generator scene inputs");graph.Validate();Frame=0;applied=-1;vertical=0;accumulator=0;lastDelta=requested=Vector3.zero;collisions=0;
            player.enabled=false;player.transform.position=Center(graph.entrance);player.transform.rotation=Quaternion.identity;player.enabled=true;ApplyLayers();Pose();Physics.SyncTransforms();Evaluate();
        }
        public void AdvanceOneFrame(){
            if(Frame>=config.frames-1)throw new InvalidOperationException("Finite own demonstration ended");applied=Frame;Vector3 before=player.transform.position;
            // The exact reference delta tape is shared by every comparison; never chase the collided actor back to its intended route.
            Vector3 a=PlannedPosition(Frame),b=PlannedPosition(Frame+1);requested=b-a;float dt=1f/config.fps;if(player.isGrounded&&vertical<0)vertical=-.25f;vertical-=config.gravity*dt;
            collisions=(int)player.Move(requested+Vector3.up*vertical*dt);lastDelta=player.transform.position-before;if(requested.sqrMagnitude>1e-8f)player.transform.rotation=Quaternion.LookRotation(requested);
            Frame++;ApplyLayers();Pose();Physics.SyncTransforms();Evaluate();
        }
        void ApplyLayers(){
            int n=VisibleEdges();for(int i=0;i<connectorClosers.Length;i++){bool open=false;for(int k=0;k<n;k++){var e=graph.edges[k];if(e.a==closerA[i]&&e.b==closerB[i]){open=true;break;}}connectorClosers[i].SetActive(!open);}
            for(int i=0;i<routeArrows.Length;i++)routeArrows[i].SetActive(!mode.construction||i<n);
            foreach(var t in templateRoots)t.SetActive(!mode.construction||Frame>=360);contentRoot.SetActive(mode.content&&(!mode.construction||Frame>=450));
            exitVisualRoot.SetActive(!mode.construction||Frame>=240);
            // A short final palette-only reveal on the same stationary geometry;
            // no additional theme capture mode and no game-mechanics claim.
            float theme=mode.construction?Mathf.Clamp01((Frame-config.themeStartFrame)/(float)config.themeBlendFrames):0;var block=new MaterialPropertyBlock();
            if(themeRenderers.Length!=themeBaseColors.Length||themeRenderers.Length!=themeTargetColors.Length||themeRenderers.Length!=themeRoles.Length)throw new InvalidOperationException("Per-material theme roles must remain aligned");
            for(int i=0;i<themeRenderers.Length;i++){Color c=Color.Lerp(themeBaseColors[i],themeTargetColors[i],theme);block.SetColor("_Color",c);block.SetColor("_BaseColor",c);themeRenderers[i].SetPropertyBlock(block);}
        }
        void Sample(ModelPose p,AnimationClip clip){
            if(p==null||!p.model||!clip)return;
            p.model.localPosition=p.position;p.model.localRotation=p.rotation;p.model.localScale=p.scale;
            float time=(Frame/(float)config.fps)%clip.length;p.lastSampledClip=clip;p.lastSampledTime=time;
            animationDiagnosticObserver?.Invoke(p,clip,time,"pre-sample");
            clip.SampleAnimation(p.model.gameObject,time);
            animationDiagnosticObserver?.Invoke(p,clip,time,"post-sample");
            p.model.localPosition=p.position;p.model.localRotation=p.rotation;p.model.localScale=p.scale;
            animationDiagnosticObserver?.Invoke(p,clip,time,"post-root-restore");
        }
        void Pose(){
            Vector3 focus,perpendicular;EnemyBasis(out focus,out perpendicular);enemy.position=focus+perpendicular*((mode.enemyVariant==0?1.8f:0f)+Mathf.Sin(Frame/(float)config.fps)*.15f);
            Sample(playerModel,lastDelta.sqrMagnitude>1e-7f?walkingClip:idleClip);Sample(enemyModel,idleClip);
            playerCamera.transform.position=player.transform.position+new Vector3(0,5.1f,-5.8f);playerCamera.transform.rotation=Quaternion.LookRotation(player.transform.position+Vector3.up*.65f-playerCamera.transform.position);
        }
        static float[] Matrix(Matrix4x4 m){var x=new float[16];for(int r=0;r<4;r++)for(int c=0;c<4;c++)x[r*4+c]=m[r,c];return x;}
        void Evaluate(){
            var contacts=Physics.OverlapCapsule(player.transform.position+Vector3.up*.35f,player.transform.position+Vector3.up*1.35f,.25f,1<<ContentLayer,QueryTriggerInteraction.Collide);var ids=new string[contacts.Length];var names=new string[contacts.Length];for(int i=0;i<contacts.Length;i++){ids[i]=contacts[i].GetEntityId().ToString();names[i]=contacts[i].name;}
            Vector3 focus,perpendicular;EnemyBasis(out focus,out perpendicular);
            CurrentState=new State{frame=Frame,appliedCommandFrame=applied,mode=mode.id,phase=Phase(),themeBlend=mode.construction?Mathf.Clamp01((Frame-config.themeStartFrame)/(float)config.themeBlendFrames):0,visibleConnectorCount=VisibleEdges(),modelExitConnected=graph.Reachable(graph.entrance)[graph.exit],visiblePortExitConnected=graph.Reachable(graph.entrance,VisibleEdges())[graph.exit],plannedPlayerPosition=PlannedPosition(Frame),playerPosition=player.transform.position,requestedDelta=requested,actualDelta=lastDelta,enemyPosition=enemy.position,enemyReferenceCenter=focus,enemyOffsetDirection=perpendicular,collisionFlags=collisions,exitReached=Vector3.Distance(player.transform.position,Center(graph.exit))<.4f,contactColliderIds=ids,contactColliderNames=names,playerCameraPosition=playerCamera.transform.position,observerCameraPosition=observerCamera.transform.position,playerVP=Matrix(playerCamera.projectionMatrix*playerCamera.worldToCameraMatrix),observerVP=Matrix(observerCamera.projectionMatrix*observerCamera.worldToCameraMatrix)};
        }
        RayEvidence Ray(Camera c,Vector3 p){Vector3 v=p-c.transform.position;RaycastHit h;bool hit=Physics.Raycast(c.transform.position,v.normalized,out h,v.magnitude+.02f,(1<<WorldLayer)|(1<<ContentLayer),QueryTriggerInteraction.Collide);return new RayEvidence{origin=c.transform.position,target=p,hit=hit,hitPoint=hit?h.point:p,hitCollider=hit?h.collider.name:null,targetDistance=v.magnitude,hitDistance=hit?h.distance:v.magnitude,hitBeforeTarget=hit&&h.distance<v.magnitude-.08f};}
        public AnchorFrame ProjectedAnchors(){var values=new Projection[anchorDefinitions.Length];for(int i=0;i<values.Length;i++){var a=anchorDefinitions[i];Vector3 p=a.target.TransformPoint(a.localPoint);values[i]=new Projection{id=a.id,meaning=a.meaning,world=p,active=a.target.gameObject.activeInHierarchy,playerViewport=playerCamera.WorldToViewportPoint(p),observerViewport=observerCamera.WorldToViewportPoint(p),playerRay=Ray(playerCamera,p),observerRay=Ray(observerCamera,p)};}return new AnchorFrame{frame=Frame,anchors=values};}
    }
}
