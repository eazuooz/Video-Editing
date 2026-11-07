using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.Architectural111.ProspectRefuge {
    [Serializable] public sealed class MoveCommand {
        public string id;
        public int startFrame, endFrameExclusive;
        public Vector3 velocity;
    }
    [Serializable] public sealed class ProspectRefugeConfig {
        public int frames, fps, width, height;
        public float baselineSecondCoverOffsetX, shiftedSecondCoverOffsetX;
        public Vector3 playerStart, firstCoverCenter, firstCoverSize, secondCoverCenter, secondCoverSize;
        public float capsuleHeight, capsuleRadius, capsuleCenterY, skinWidth, stepOffset, groundStickSpeed;
        public float cameraEyeHeight, cameraPitchDegrees, cameraYawDegrees, verticalFieldOfView;
        public float headSampleHeight, torsoSampleHeight, hipsSampleHeight;
        public float enemyStartX, enemyZ, enemyEyeHeight, enemyTargetHeight, enemyWalkSpeed;
        public float enemyTurnStartSeconds, enemyTurnEndSeconds, enemyPauseStartSeconds;
        public float enemyHorizontalHalfFovDegrees, enemyRange;
        public Vector3 observerPosition;
        public float observerOrthographicSize;
        public MoveCommand[] commands;
    }
    [Serializable] public sealed class VisibilityRay {
        public string id, hitCollider, hitColliderEntityId;
        public Vector3 origin, desiredEndpoint, actualEndpoint;
        public float distance, horizontalAngleDegrees;
        public bool blocked, inRange, inFieldOfView, cameraInFrustum, seen;
    }
    [Serializable] public sealed class FrameRays {
        public int frame;
        public VisibilityRay[] enemyToBody;
        public VisibilityRay playerCameraToEnemy;
    }
    [Serializable] public sealed class ProjectedAnchor {
        public string id;
        public Vector3 world, playerViewport, observerViewport;
    }
    [Serializable] public sealed class FrameAnchors { public int frame; public ProjectedAnchor[] anchors; }
    [Serializable] public sealed class FrameState {
        public int frame, appliedCommandFrame, collisionFlags, seenBodySamples, blockedBodySamples;
        public float timeSeconds, secondCoverOffsetX, enemyYawDegrees;
        public string appliedCommandId, nextCommandId, enemyPhase;
        public Vector3 appliedVelocity, nextVelocity, playerPosition, requestedPlayerPosition, actualMoveDelta;
        public Vector3 enemyPosition, enemyEye, playerCameraEye, cameraRotationEuler, observerCameraPosition, observerCameraRotationEuler;
        public bool enemySeesAnyDeclaredBodySample, playerCameraCanObserveEnemyTorso;
        public VisibilityRay[] bodyRays;
    }

    // Original, deliberately small physical/visibility implementation. Its
    // declared point samples are NOT whole-mesh visibility or commercial AI.
    public sealed class ProspectRefugeExperiment : MonoBehaviour {
        public const int EnvironmentLayer=26, PlayerLayer=28, GuideLayer=29, EnemyLayer=30;
        public ProspectRefugeConfig config;
        public string mode;
        public float secondCoverOffsetX;
        public CharacterController player;
        public Transform playerModel, enemy, enemyModel, enemyEyeMarker;
        public Transform[] bodyMarkers;
        public Transform secondCover;
        public AnimationClip walkingClip, idleClip;
        public Vector3 playerModelBasePosition, playerModelBaseScale, enemyModelBasePosition, enemyModelBaseScale;
        public Quaternion playerModelBaseRotation, enemyModelBaseRotation;
        public Camera playerCamera, observerCamera;
        public LineRenderer[] sightLines;
        public LineRenderer actualTravelPath, playerFootprint, enemyFovBoundary;
        public bool previewInPlayMode=true;
        public int Frame { get; private set; }
        public FrameState CurrentState { get; private set; }
        public VisibilityRay[] BodyRays { get; private set; }
        public VisibilityRay PlayerObservationRay { get; private set; }
        readonly List<Vector3> travelled=new List<Vector3>();
        int appliedCommandFrame=-1;
        CollisionFlags lastCollision;
        Vector3 lastRequested, lastDelta, lastVelocity;
        string lastCommandId="initial-state";
        float playAccumulator;

        void Start() { if(config!=null)ResetExperiment(); }
        void Update() {
            if(!Application.isPlaying||!previewInPlayMode||config==null)return;
            playAccumulator+=Time.deltaTime;
            while(playAccumulator>=1f/config.fps&&Frame<config.frames-1) {
                AdvanceOneFrame();playAccumulator-=1f/config.fps;
            }
        }
        public MoveCommand CommandAt(int frame) {
            foreach(var command in config.commands)
                if(frame>=command.startFrame&&frame<command.endFrameExclusive)return command;
            throw new InvalidOperationException("Command tape must cover every capture interval exactly once");
        }
        public void ResetExperiment() {
            if(config==null||!player||!enemy||!secondCover)throw new InvalidOperationException("Incomplete physical experiment");
            secondCover.position=config.secondCoverCenter+Vector3.right*secondCoverOffsetX;
            player.enabled=false;player.transform.position=config.playerStart;player.transform.rotation=Quaternion.identity;player.enabled=true;
            Frame=0;appliedCommandFrame=-1;lastVelocity=Vector3.zero;lastDelta=Vector3.zero;
            lastRequested=config.playerStart;lastCollision=CollisionFlags.None;lastCommandId="initial-state";playAccumulator=0;
            travelled.Clear();travelled.Add(config.playerStart+Vector3.up*.025f);
            SetEnemyPose(0);SampleActors(0,false);UpdateCamera();Physics.SyncTransforms();EvaluateState();
        }
        // Capture frame0 BEFORE this method. An advance to frame f+1 applies
        // command f for exactly1/fps seconds. No teleport/pathfinding/adaptive wait.
        public void AdvanceOneFrame() {
            if(Frame>=config.frames-1)throw new InvalidOperationException("Finite capture has ended");
            var command=CommandAt(Frame);float dt=1f/config.fps;Vector3 before=player.transform.position;
            appliedCommandFrame=Frame;lastCommandId=command.id;lastVelocity=command.velocity;
            lastRequested=before+(command.velocity+Vector3.down*config.groundStickSpeed)*dt;
            lastCollision=player.Move((command.velocity+Vector3.down*config.groundStickSpeed)*dt);
            lastDelta=player.transform.position-before;Frame++;
            bool moving=new Vector2(lastDelta.x,lastDelta.z).sqrMagnitude>1e-9f;
            if(moving)player.transform.rotation=Quaternion.LookRotation(new Vector3(lastDelta.x,0,lastDelta.z));
            travelled.Add(player.transform.position+Vector3.up*.025f);
            SetEnemyPose(Frame/(float)config.fps);SampleActors(Frame/(float)config.fps,moving);
            UpdateCamera();Physics.SyncTransforms();EvaluateState();
        }
        void SetEnemyPose(float time) {
            float x,yaw;string phase;
            if(time<config.enemyTurnStartSeconds) {
                x=config.enemyStartX+config.enemyWalkSpeed*time;yaw=90;phase="patrol-outbound";
            } else if(time<config.enemyTurnEndSeconds) {
                x=config.enemyStartX+config.enemyWalkSpeed*config.enemyTurnStartSeconds;
                yaw=Mathf.Lerp(90,270,(time-config.enemyTurnStartSeconds)/(config.enemyTurnEndSeconds-config.enemyTurnStartSeconds));phase="scripted-waypoint-turn";
            } else {
                float walkUntil=Mathf.Min(time,config.enemyPauseStartSeconds);
                x=config.enemyStartX+config.enemyWalkSpeed*config.enemyTurnStartSeconds-config.enemyWalkSpeed*(walkUntil-config.enemyTurnEndSeconds);
                yaw=270;phase=time<config.enemyPauseStartSeconds?"patrol-return":"scripted-waypoint-pause";
            }
            enemy.position=new Vector3(x,0,config.enemyZ);enemy.rotation=Quaternion.Euler(0,yaw,0);
            if(CurrentState==null)CurrentState=new FrameState();CurrentState.enemyPhase=phase;
        }
        void SampleActors(float time,bool playerMoving) {
            Sample(playerModel,playerMoving?walkingClip:idleClip,time,playerModelBasePosition,playerModelBaseRotation,playerModelBaseScale);
            bool enemyMoving=CurrentState.enemyPhase=="patrol-outbound"||CurrentState.enemyPhase=="patrol-return";
            Sample(enemyModel,enemyMoving?walkingClip:idleClip,time,enemyModelBasePosition,enemyModelBaseRotation,enemyModelBaseScale);
        }
        static void Sample(Transform model,AnimationClip clip,float time,Vector3 position,Quaternion rotation,Vector3 scale) {
            if(!model||!clip)throw new InvalidOperationException("Articulated model and original animation clips required");
            clip.SampleAnimation(model.gameObject,Mathf.Repeat(time,clip.length));
            // Skeleton motion retained; imported root motion cannot move the physical actor.
            model.localPosition=position;model.localRotation=rotation;model.localScale=scale;
        }
        void UpdateCamera() {
            playerCamera.transform.position=player.transform.position+Vector3.up*config.cameraEyeHeight;
            playerCamera.transform.rotation=Quaternion.Euler(config.cameraPitchDegrees,config.cameraYawDegrees,0);
        }
        VisibilityRay Cast(string id,Vector3 origin,Vector3 target,Vector3 forward,float halfFov,float range,bool cameraRay=false) {
            Vector3 delta=target-origin,flat=new Vector3(delta.x,0,delta.z),flatForward=new Vector3(forward.x,0,forward.z);
            float distance=delta.magnitude;RaycastHit hit=new RaycastHit();
            bool blocked=distance>1e-6f&&Physics.Raycast(origin,delta.normalized,out hit,distance,1<<EnvironmentLayer,QueryTriggerInteraction.Ignore);
            // Definite assignment for C# and stable missing-hit provenance.
            if(!blocked)hit=new RaycastHit();
            float angle=flat.sqrMagnitude<1e-9f?0:Vector3.Angle(flatForward,flat);
            Vector3 viewport=playerCamera.WorldToViewportPoint(target);
            bool inFrustum=viewport.z>playerCamera.nearClipPlane&&viewport.z<playerCamera.farClipPlane&&viewport.x>=0&&viewport.x<=1&&viewport.y>=0&&viewport.y<=1;
            bool inRange=distance<=range,inFov=angle<=halfFov;
            return new VisibilityRay{id=id,origin=origin,desiredEndpoint=target,actualEndpoint=blocked?hit.point:target,
                hitCollider=blocked?hit.collider.name:null,hitColliderEntityId=blocked?hit.collider.GetEntityId().ToString():string.Empty,distance=distance,horizontalAngleDegrees=angle,
                blocked=blocked,inRange=inRange,inFieldOfView=inFov,cameraInFrustum=cameraRay&&inFrustum,
                seen=!blocked&&inRange&&(cameraRay?inFrustum:inFov)};
        }
        void EvaluateState() {
            Vector3 enemyEye=enemy.position+Vector3.up*config.enemyEyeHeight;
            float[] heights={config.headSampleHeight,config.torsoSampleHeight,config.hipsSampleHeight};string[] names={"head","torso","hips"};
            BodyRays=new VisibilityRay[3];int seen=0,blocked=0;
            for(int i=0;i<3;i++) {
                BodyRays[i]=Cast(names[i],enemyEye,player.transform.position+Vector3.up*heights[i],enemy.forward,config.enemyHorizontalHalfFovDegrees,config.enemyRange);
                if(BodyRays[i].seen)seen++;if(BodyRays[i].blocked)blocked++;
                var line=sightLines[i];line.positionCount=2;line.SetPositions(new[]{enemyEye,BodyRays[i].actualEndpoint});
                Color color=BodyRays[i].blocked?new Color(.25f,.95f,.69f):BodyRays[i].seen?new Color(1,.25f,.20f):new Color(1,.82f,.32f);
                line.startColor=line.endColor=color;bodyMarkers[i].position=BodyRays[i].desiredEndpoint;
            }
            PlayerObservationRay=Cast("player-camera-to-enemy-torso",playerCamera.transform.position,enemy.position+Vector3.up*config.enemyTargetHeight,playerCamera.transform.forward,180,config.enemyRange,true);
            enemyEyeMarker.position=enemyEye;
            actualTravelPath.positionCount=travelled.Count;actualTravelPath.SetPositions(travelled.ToArray());
            playerFootprint.positionCount=49;
            for(int i=0;i<49;i++){float a=i*Mathf.PI/24;playerFootprint.SetPosition(i,player.transform.position+new Vector3(Mathf.Cos(a)*config.capsuleRadius,.04f,Mathf.Sin(a)*config.capsuleRadius));}
            float yaw=enemy.eulerAngles.y;enemyFovBoundary.positionCount=3;
            // Boundary is an own horizontal FOV definition on the ground, not an occlusion result.
            Vector3 groundEye=new Vector3(enemyEye.x,.035f,enemyEye.z);
            enemyFovBoundary.SetPositions(new[]{groundEye+Quaternion.Euler(0,yaw-config.enemyHorizontalHalfFovDegrees,0)*Vector3.forward*config.enemyRange,groundEye,groundEye+Quaternion.Euler(0,yaw+config.enemyHorizontalHalfFovDegrees,0)*Vector3.forward*config.enemyRange});
            var next=CommandAt(Frame);
            CurrentState=new FrameState{frame=Frame,timeSeconds=Frame/(float)config.fps,appliedCommandFrame=appliedCommandFrame,appliedCommandId=lastCommandId,
                appliedVelocity=lastVelocity,nextCommandId=next.id,nextVelocity=next.velocity,collisionFlags=(int)lastCollision,
                playerPosition=player.transform.position,requestedPlayerPosition=lastRequested,actualMoveDelta=lastDelta,
                enemyPosition=enemy.position,enemyEye=enemyEye,enemyYawDegrees=yaw,enemyPhase=CurrentState.enemyPhase,secondCoverOffsetX=secondCoverOffsetX,
                seenBodySamples=seen,blockedBodySamples=blocked,enemySeesAnyDeclaredBodySample=seen>0,
                playerCameraCanObserveEnemyTorso=PlayerObservationRay.seen,playerCameraEye=playerCamera.transform.position,cameraRotationEuler=playerCamera.transform.eulerAngles,
                observerCameraPosition=observerCamera.transform.position,observerCameraRotationEuler=observerCamera.transform.eulerAngles,bodyRays=BodyRays};
        }
        public FrameAnchors ProjectedAnchors() {
            var points=new List<ProjectedAnchor>();
            Action<string,Vector3> add=(name,p)=>points.Add(new ProjectedAnchor{id=name,world=p,playerViewport=playerCamera.WorldToViewportPoint(p),observerViewport=observerCamera.WorldToViewportPoint(p)});
            add("player-ground",player.transform.position);add("player-camera-eye",playerCamera.transform.position);add("enemy-eye",CurrentState.enemyEye);
            add("enemy-torso-observation-target",PlayerObservationRay.desiredEndpoint);add("second-cover-center",secondCover.position);
            foreach(var ray in BodyRays){add("body-"+ray.id,ray.desiredEndpoint);add("ray-"+ray.id+"-actual-hit-end",ray.actualEndpoint);}
            add("camera-observation-actual-hit-end",PlayerObservationRay.actualEndpoint);
            return new FrameAnchors{frame=Frame,anchors=points.ToArray()};
        }
    }
}
