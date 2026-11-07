using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.Architectural111.ProspectRefugeSupplement.Corrections {
    [Serializable] public sealed class CorrectionScene {
        public string mode, sourceSceneFile, sceneFile, correction, purpose;
        public int[] paragraphs;
    }
    [Serializable] public sealed class CorrectionConfig {
        public int frames, fps, width, height, courtyardTurnStartFrame, courtyardTurnEndFrame;
        public string sourceKind, sceneFolder, sourceSceneFolder, frameConvention;
        public Vector3 scaleCameraPosition, scaleCameraTarget, atriumPlayerPosition, atriumLookAt, courtyardReobserveTarget;
        public float scaleVerticalFieldOfView;
        public float interiorCeilingUndersideY, interiorCeilingThickness, interiorCeilingWidth, interiorCeilingMinZ, interiorCeilingMaxZ;
        public CorrectionScene[] scenes;
    }
    [Serializable] public sealed class CorrectedState {
        public int frame, sourceClockFrame, appliedCommandFrame, routePointCount;
        public float timeSeconds;
        public string mode, sourceKind, correction, phase, motionKind;
        public Vector3 playerPosition, requestedPlayerPosition, actualMoveDelta, playerEuler;
        public Vector3 enemyPosition, secondEnemyPosition, playerCameraEye, playerCameraEuler, observerCameraEye, observerCameraEuler;
        public bool commercialImplementationMeasured, safetyMeasured, wholeMeshVisibilityMeasured;
        public RayEvidence[] rays;
    }
    [Serializable] public sealed class CameraProof {
        public Vector3 position, forward;
        public float fieldOfView, aspect, nearClip, farClip;
        public float[] viewProjectionRowMajor;
    }
    [Serializable] public sealed class CameraRayProof {
        public Vector3 origin, desiredEndpoint, actualEndpoint;
        public bool blocked;
        public string hitCollider;
    }
    [Serializable] public sealed class CorrectedAnchor {
        public string id, role;
        public Vector3 world, playerViewport, observerViewport;
        public bool active, playerInFrustum, observerInFrustum;
        public CameraRayProof playerCameraRay, observerCameraRay;
    }
    [Serializable] public sealed class CorrectedAnchorFrame {
        public int frame;
        public CameraProof playerCamera, observerCamera;
        public CorrectedAnchor[] anchors;
    }
    [Serializable] public sealed class CorrectedRoute {
        public string mode, sourceKind="our-authored-corrected-illustration";
        public Vector3[] points;
        public bool physicallySolved=false;
    }

    // Original scene geometry and NPC clock remain in Experiment. This component
    // owns the changed pose/camera and publishes fresh evidence AFTER each step.
    [DefaultExecutionOrder(100)]
    public sealed class CorrectionDriver : MonoBehaviour {
        public Experiment originalRig;
        public CorrectionConfig config;
        public bool previewInPlayMode=true;
        public CorrectedState CurrentState { get; private set; }
        public RayEvidence[] CurrentRays { get; private set; }
        public int Frame { get { return originalRig.Frame; } }
        readonly List<Vector3> route=new List<Vector3>();
        float previewAccumulator;
        Vector3 previousCorrectedPosition;
        bool hasPrevious;

        void Start(){if(Application.isPlaying)ResetCorrection();}
        void Update(){
            if(!Application.isPlaying||!previewInPlayMode||!originalRig||config==null)return;
            previewAccumulator+=Time.deltaTime;
            while(previewAccumulator>=1f/config.fps&&Frame<config.frames-1){AdvanceOneFrame();previewAccumulator-=1f/config.fps;}
        }
        public CorrectionScene Scene(){
            if(config==null||config.scenes==null||!originalRig)throw new InvalidOperationException("Correction scene is incomplete");
            foreach(var scene in config.scenes)if(scene.mode==originalRig.mode)return scene;
            throw new InvalidOperationException("Only the four selected corrective modes are allowed");
        }
        public void ResetCorrection(){
            var scene=Scene();
            if(config.frames!=720||config.fps!=60||config.width!=1920||config.height!=1080||originalRig.IsEncounter)
                throw new InvalidOperationException("Correction contract is not a selected 720-frame illustration");
            originalRig.previewInPlayMode=false;
            originalRig.playerCamera.aspect=originalRig.observerCamera.aspect=config.width/(float)config.height;
            originalRig.ResetExperiment();
            route.Clear();hasPrevious=false;previewAccumulator=0;
            ApplyCorrection();
        }
        public void AdvanceOneFrame(){
            if(Frame>=config.frames-1)throw new InvalidOperationException("Finite correction ended");
            originalRig.AdvanceOneFrame();
            ApplyCorrection();
        }
        static void FaceHorizontal(Transform subject,Vector3 toward){
            var delta=toward-subject.position;delta.y=0;
            if(delta.sqrMagnitude>1e-8f)subject.rotation=Quaternion.LookRotation(delta);
        }
        void SampleActualIdle(){
            var rest=originalRig.playerModel;var clip=originalRig.idleClip;
            if(rest==null||!rest.model||!clip)throw new InvalidOperationException("Original articulated Idle model/clip is required");
            clip.SampleAnimation(rest.model.gameObject,Mathf.Repeat(Frame/(float)config.fps,clip.length));
            rest.model.localPosition=rest.position;rest.model.localRotation=rest.rotation;rest.model.localScale=rest.scale;
        }
        void ApplyCorrection(){
            var rig=originalRig;string mode=rig.mode;
            rig.playerCamera.aspect=rig.observerCamera.aspect=config.width/(float)config.height;
            if(mode=="scale"){
                rig.playerCamera.transform.position=config.scaleCameraPosition;
                rig.playerCamera.transform.rotation=Quaternion.LookRotation(config.scaleCameraTarget-config.scaleCameraPosition);
                rig.playerCamera.fieldOfView=config.scaleVerticalFieldOfView;
            }else if(mode=="atrium"){
                rig.player.transform.position=config.atriumPlayerPosition;
                FaceHorizontal(rig.player.transform,config.atriumLookAt);SampleActualIdle();
                rig.playerCamera.transform.position=rig.player.transform.position+Vector3.up*rig.config.playerEyeHeight;
                rig.playerCamera.transform.rotation=Quaternion.LookRotation(config.atriumLookAt-rig.playerCamera.transform.position);
            }else if(mode=="refuge"){
                // Original body/cameras/outlook remain. The saved additive
                // sectional interior ceiling is real shared scene geometry.
            }else if(mode=="courtyard"){
                if(Frame>=config.courtyardTurnStartFrame){
                    float t=Mathf.Clamp01((Frame-config.courtyardTurnStartFrame)/(float)(config.courtyardTurnEndFrame-config.courtyardTurnStartFrame));
                    Quaternion source=rig.playerCamera.transform.rotation;
                    Quaternion target=Quaternion.LookRotation(config.courtyardReobserveTarget-rig.playerCamera.transform.position);
                    rig.playerCamera.transform.rotation=Quaternion.Slerp(source,target,t);
                    Quaternion bodySource=Quaternion.identity;
                    Vector3 d=config.courtyardReobserveTarget-rig.player.transform.position;d.y=0;
                    rig.player.transform.rotation=Quaternion.Slerp(bodySource,Quaternion.LookRotation(d),t);
                    SampleActualIdle();
                }
            }else throw new InvalidOperationException("Unsupported correction mode");
            Physics.SyncTransforms();
            var corrected=rig.player.transform.position;
            Vector3 delta=hasPrevious?corrected-previousCorrectedPosition:Vector3.zero;
            previousCorrectedPosition=corrected;hasPrevious=true;
            var routePoint=corrected+Vector3.up*.035f;
            if(route.Count==0||(route[route.Count-1]-routePoint).sqrMagnitude>1e-12f)route.Add(routePoint);
            rig.travelledLine.positionCount=route.Count;rig.travelledLine.SetPositions(route.ToArray());
            EvaluateFreshRays();
            string phase=mode=="scale"?(Frame<240?"narrow-to-intimate-boundary":"intimate-to-open-boundary"):
                mode=="atrium"?"stationary-private-room-observes-public-circulation":
                mode=="refuge"?"sectional-interior-ceiling-and-original-outward-view":
                Frame<120?"scripted-observe":Frame<config.courtyardTurnStartFrame?"scripted-cross":
                Frame<config.courtyardTurnEndFrame?"turn-toward-courtyard":"new-outward-observation";
            // Every changed spatial field is sampled from the corrected scene,
            // never from Experiment.CurrentState (which was evaluated earlier).
            CurrentState=new CorrectedState{frame=Frame,sourceClockFrame=rig.Frame,appliedCommandFrame=Frame-1,timeSeconds=Frame/(float)config.fps,
                mode=mode,sourceKind=config.sourceKind,correction=Scene().correction,phase=phase,
                motionKind=mode=="atrium"?"stationary actor; original NPC clock":"declared scripted geometric illustration; corrected camera",
                playerPosition=corrected,requestedPlayerPosition=corrected,actualMoveDelta=delta,playerEuler=rig.player.transform.eulerAngles,
                enemyPosition=rig.enemy?rig.enemy.position:Vector3.zero,secondEnemyPosition=rig.secondEnemy?rig.secondEnemy.position:Vector3.zero,
                playerCameraEye=rig.playerCamera.transform.position,playerCameraEuler=rig.playerCamera.transform.eulerAngles,
                observerCameraEye=rig.observerCamera.transform.position,observerCameraEuler=rig.observerCamera.transform.eulerAngles,
                routePointCount=route.Count,rays=CurrentRays};
        }
        void EvaluateFreshRays(){
            var rig=originalRig;var rays=new List<RayEvidence>();
            if(rig.rayDefinitions!=null)for(int i=0;i<rig.rayDefinitions.Length;i++){
                var spec=rig.rayDefinitions[i];Vector3 origin=spec.from.TransformPoint(spec.fromLocal),end=spec.to.TransformPoint(spec.toLocal),d=end-origin;
                RaycastHit hit=new RaycastHit();bool blocked=d.sqrMagnitude>1e-12f&&Physics.Raycast(origin,d.normalized,out hit,d.magnitude,1<<Experiment.EnvironmentLayer,QueryTriggerInteraction.Ignore);
                var row=new RayEvidence{id=spec.id,meaning=spec.meaning,origin=origin,desiredEndpoint=end,actualEndpoint=blocked?hit.point:end,
                    blocked=blocked,hitCollider=blocked?hit.collider.name:null,distance=d.magnitude};
                rays.Add(row);rig.rayLines[i].positionCount=2;rig.rayLines[i].SetPositions(new[]{origin,row.actualEndpoint});
                rig.rayLines[i].startColor=rig.rayLines[i].endColor=blocked?new Color(.2f,.9f,.65f):new Color(1,.72f,.2f);
            }
            CurrentRays=rays.ToArray();
        }
        static bool InFrustum(Vector3 p,Camera camera){return camera.nearClipPlane<p.z&&p.z<camera.farClipPlane&&0<=p.x&&p.x<=1&&0<=p.y&&p.y<=1;}
        static CameraProof CameraEvidence(Camera camera){
            Matrix4x4 m=camera.projectionMatrix*camera.worldToCameraMatrix;var values=new float[16];
            for(int r=0;r<4;r++)for(int c=0;c<4;c++)values[r*4+c]=m[r,c];
            return new CameraProof{position=camera.transform.position,forward=camera.transform.forward,fieldOfView=camera.fieldOfView,
                aspect=camera.aspect,nearClip=camera.nearClipPlane,farClip=camera.farClipPlane,viewProjectionRowMajor=values};
        }
        static CameraRayProof CameraRay(Camera camera,Vector3 target){
            Vector3 origin=camera.transform.position,d=target-origin;RaycastHit hit=new RaycastHit();
            bool blocked=d.sqrMagnitude>1e-12f&&Physics.Raycast(origin,d.normalized,out hit,d.magnitude,1<<Experiment.EnvironmentLayer,QueryTriggerInteraction.Ignore);
            return new CameraRayProof{origin=origin,desiredEndpoint=target,actualEndpoint=blocked?hit.point:target,blocked=blocked,hitCollider=blocked?hit.collider.name:null};
        }
        public CorrectedAnchorFrame ProjectedAnchors(){
            var rig=originalRig;var anchors=new List<CorrectedAnchor>();
            foreach(var spec in rig.anchorDefinitions){
                Vector3 world=spec.target.TransformPoint(spec.localPoint),player=rig.playerCamera.WorldToViewportPoint(world),observer=rig.observerCamera.WorldToViewportPoint(world);
                anchors.Add(new CorrectedAnchor{id=spec.id,role=spec.role,world=world,playerViewport=player,observerViewport=observer,
                    active=spec.target.gameObject.activeInHierarchy,playerInFrustum=InFrustum(player,rig.playerCamera),observerInFrustum=InFrustum(observer,rig.observerCamera),
                    playerCameraRay=CameraRay(rig.playerCamera,world),observerCameraRay=CameraRay(rig.observerCamera,world)});
            }
            return new CorrectedAnchorFrame{frame=Frame,playerCamera=CameraEvidence(rig.playerCamera),observerCamera=CameraEvidence(rig.observerCamera),anchors=anchors.ToArray()};
        }
        public CorrectedRoute RouteEvidence(){return new CorrectedRoute{mode=originalRig.mode,points=route.ToArray()};}
    }
}
