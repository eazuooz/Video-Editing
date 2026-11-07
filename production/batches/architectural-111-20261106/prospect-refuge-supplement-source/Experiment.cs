using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.Architectural111.ProspectRefugeSupplement {
    [Serializable] public sealed class SupplementCommand {
        public string id; public int startFrame, endFrameExclusive; public float velocityX;
    }
    [Serializable] public sealed class SupplementScene {
        public string mode, sceneFile, purpose; public int[] paragraphs;
    }
    [Serializable] public sealed class SupplementConfig {
        public int frames, fps, width, height;
        public string sourceKind, sceneFolder, frameConvention;
        public float playerHeight, playerRadius, playerEyeHeight, gravity, jumpSpeed, walkSpeed, shotSpeed, enemyShotSpeed;
        public Vector3 observerPosition, observerLookAt;
        public SupplementScene[] scenes; public SupplementCommand[] encounterCommands;
        public int[] jumpFrames, fireFrames;
    }
    [Serializable] public sealed class AnchorDefinition {
        public string id, role; public Transform target; public Vector3 localPoint;
    }
    [Serializable] public sealed class RayDefinition {
        public string id, meaning; public Transform from, to; public Vector3 fromLocal, toLocal;
    }
    [Serializable] public sealed class RayEvidence {
        public string id, meaning, hitCollider; public Vector3 origin, desiredEndpoint, actualEndpoint;
        public bool blocked; public float distance;
    }
    [Serializable] public sealed class ProjectedAnchor {
        public string id, role; public Vector3 world, playerViewport, observerViewport;
        public bool active, playerInFrustum, observerInFrustum;
    }
    [Serializable] public sealed class AnchorFrame { public int frame; public ProjectedAnchor[] anchors; }
    [Serializable] public sealed class RayFrame { public int frame; public RayEvidence[] rays; }
    [Serializable] public sealed class ProjectileEvidence {
        public string id, team, hitCollider; public Vector3 previous, position, velocity, actualHitPoint;
        public bool alive, hit; public int createdAtAppliedFrame, hitAtFrame=-1;
    }
    [Serializable] public sealed class SupplementState {
        public int frame, appliedCommandFrame, collisionFlags;
        public float timeSeconds; public string mode, sourceKind, phase, appliedCommandId, motionKind;
        public Vector3 playerPosition, requestedPlayerPosition, actualMoveDelta, enemyPosition, secondEnemyPosition;
        public Vector3 playerCameraEye, playerCameraEuler, observerCameraEye, observerCameraEuler;
        public bool appliedJump, appliedFire; public RayEvidence[] rays; public ProjectileEvidence[] projectiles;
    }
    [Serializable] public sealed class ModelRest {
        public Transform model; public Vector3 position, scale; public Quaternion rotation;
    }

    // All modes are our own generic illustrations. No commercial AI, whole-mesh
    // visibility, structural stress or psychological measurement is reconstructed.
    public sealed class Experiment : MonoBehaviour {
        public const int EnvironmentLayer=26, ProjectileLayer=27, PlayerLayer=28, GuideLayer=29, EnemyLayer=30;
        public SupplementConfig config; public string mode;
        public CharacterController player;
        public Transform enemy, secondEnemy, outwardTarget, chestLid, enemyShield, movableBoard;
        public Camera playerCamera, observerCamera;
        public AnimationClip idleClip, walkingClip;
        public ModelRest playerModel, enemyModel, secondEnemyModel;
        public Transform[] boundaries, columns, facadePanels, partitions;
        public Vector3[] facadeRest, partitionRest;
        public AnchorDefinition[] anchorDefinitions;
        public RayDefinition[] rayDefinitions;
        public LineRenderer[] rayLines;
        public LineRenderer travelledLine;
        public Material playerShotMaterial, enemyShotMaterial;
        public bool previewInPlayMode;
        public int Frame { get; private set; }
        public SupplementState CurrentState { get; private set; }
        public RayEvidence[] CurrentRays { get; private set; }
        readonly List<Vector3> travelled=new List<Vector3>();
        readonly List<ProjectileEvidence> projectiles=new List<ProjectileEvidence>();
        readonly List<Transform> projectileVisuals=new List<Transform>();
        float verticalSpeed, previewAccumulator;
        int appliedFrame=-1, collisionFlags;
        string commandId="initial-state";
        Vector3 requested, delta;
        bool appliedJump, appliedFire;

        public bool IsEncounter { get {return mode=="flying"||mode=="shield"||mode=="boss";} }
        void Start(){if(config!=null)ResetExperiment();}
        void Update(){
            if(!Application.isPlaying||!previewInPlayMode||config==null)return;
            previewAccumulator+=Time.deltaTime;
            while(previewAccumulator>=1f/config.fps&&Frame<config.frames-1){AdvanceOneFrame();previewAccumulator-=1f/config.fps;}
        }
        static bool Includes(int[] values,int value){if(values!=null)foreach(int x in values)if(x==value)return true;return false;}
        static float Progress(int f,int first,int last){return Mathf.Clamp01((f-first)/(float)(last-first));}
        public SupplementCommand CommandAt(int frame){
            foreach(var x in config.encounterCommands)if(frame>=x.startFrame&&frame<x.endFrameExclusive)return x;
            throw new InvalidOperationException("Finite command tape does not cover frame");
        }
        public void ResetExperiment(){
            if(config==null||!player||!playerCamera||!observerCamera)throw new InvalidOperationException("Incomplete supplementary illustration");
            foreach(var t in projectileVisuals)if(t)DestroyImmediate(t.gameObject);
            projectileVisuals.Clear();projectiles.Clear();travelled.Clear();
            Frame=0;appliedFrame=-1;commandId="initial-state";delta=Vector3.zero;
            verticalSpeed=0;collisionFlags=0;appliedFire=appliedJump=false;previewAccumulator=0;
            player.enabled=false;player.transform.position=IsEncounter?new Vector3(-5,0,0):ScriptedPosition(0);player.transform.rotation=Quaternion.identity;player.enabled=IsEncounter;
            requested=player.transform.position;
            ApplyGeometry(0);PoseOtherActors(0);PoseCameras(0);SampleModels(0,false);
            Physics.SyncTransforms();travelled.Add(player.transform.position+Vector3.up*.035f);Evaluate();
        }
        // Capture0 is the initial state. Applying command f produces capture f+1.
        public void AdvanceOneFrame(){
            if(Frame>=config.frames-1)throw new InvalidOperationException("Finite supplementary mode ended");
            float dt=1f/config.fps;Vector3 before=player.transform.position;
            appliedFrame=Frame;appliedJump=appliedFire=false;
            if(IsEncounter){
                var cmd=CommandAt(Frame);commandId=cmd.id;
                appliedJump=Includes(config.jumpFrames,Frame);appliedFire=Includes(config.fireFrames,Frame);
                if(player.isGrounded&&verticalSpeed<0)verticalSpeed=-.25f;
                if(appliedJump&&player.isGrounded)verticalSpeed=config.jumpSpeed;
                verticalSpeed-=config.gravity*dt;
                Vector3 movement=new Vector3(cmd.velocityX,verticalSpeed,0)*dt;requested=before+movement;
                collisionFlags=(int)player.Move(movement);
                if(Mathf.Abs(cmd.velocityX)>.01f)player.transform.rotation=Quaternion.Euler(0,cmd.velocityX>0?90:270,0);
                if(appliedFire)Spawn("player",player.transform.position+new Vector3(.5f,1.0f,0),Vector3.right*config.shotSpeed,Frame);
                if(Frame>=150&&Frame<600&&(Frame%120==30||Frame%120==42||Frame%120==54)){
                    Vector3 origin=enemy.position+Vector3.up*(mode=="boss"?2.0f:1.1f)+Vector3.left*.6f;
                    Vector3 aim=(player.transform.position+Vector3.up*.95f-origin).normalized;
                    Spawn("enemy",origin,aim*config.enemyShotSpeed,Frame);
                }
            }else{
                commandId="scripted-geometric-illustration-route";
                requested=ScriptedPosition(Frame+1);player.transform.position=requested;
                Vector3 travel=requested-before;if(new Vector2(travel.x,travel.z).sqrMagnitude>1e-8f)player.transform.rotation=Quaternion.LookRotation(new Vector3(travel.x,0,travel.z));
            }
            delta=player.transform.position-before;Frame++;
            ApplyGeometry(Frame);PoseOtherActors(Frame);Physics.SyncTransforms();AdvanceProjectiles(dt);
            PoseCameras(Frame);SampleModels(Frame/(float)config.fps,new Vector2(delta.x,delta.z).sqrMagnitude>1e-8f);
            travelled.Add(player.transform.position+Vector3.up*.035f);Physics.SyncTransforms();Evaluate();
        }
        Vector3 ScriptedPosition(int f){
            if(mode=="atrium")return new Vector3(Mathf.Lerp(-2.4f,2.4f,Progress(f,120,600)),3,-3.4f);
            if(mode=="courtyard"){
                float z=Mathf.Lerp(-5.5f,4.7f,Progress(f,120,600));
                float y=Mathf.Lerp(-.7f,0,Mathf.InverseLerp(-4.1f,-2.6f,z));return new Vector3(0,y,z);
            }
            if(mode=="alcove"){
                if(f<300)return Vector3.Lerp(new Vector3(0,0,-4),new Vector3(3,0,-4),Progress(f,120,300));
                return Vector3.Lerp(new Vector3(3,0,-4),new Vector3(3,0,1.2f),Progress(f,300,600));
            }
            if(mode=="openings"){
                float z=Mathf.Lerp(-4.5f,3.5f,Progress(f,240,660));
                float y=Mathf.Lerp(0,3,Mathf.InverseLerp(-3.5f,2.5f,z));return new Vector3(3.6f,y,z);
            }
            if(mode=="plaza")return new Vector3(Mathf.Lerp(-4,4,Progress(f,120,600)),1.6f,-2.8f);
            if(mode=="footings")return f<570?new Vector3(Mathf.Lerp(-4,0,Progress(f,390,570)),.4f,0):new Vector3(Mathf.Lerp(0,4,Progress(f,570,690)),.4f,0);
            if(mode=="refuge")return new Vector3(0,-.65f,-2);
            if(mode=="protected")return new Vector3(0,0,-2);
            return new Vector3(0,0,0);
        }
        void ApplyGeometry(int f){
            if(mode=="scale"&&boundaries!=null&&boundaries.Length==2){
                float width=f<240?Mathf.Lerp(1.1f,3.8f,Progress(f,90,210)):Mathf.Lerp(3.8f,8,Progress(f,330,540));
                boundaries[0].position=new Vector3(-width*.5f,1.5f,0);boundaries[1].position=new Vector3(width*.5f,1.5f,0);
            }
            if(mode=="structure"){
                float a=Progress(f,90,240);if(columns!=null)foreach(var t in columns){t.gameObject.SetActive(a>.001f);t.localScale=new Vector3(.24f,Mathf.Max(.01f,1.5f*a),.24f);t.position=new Vector3(t.position.x,1.5f*a,t.position.z);}
                float open=Progress(f,300,510);if(facadePanels!=null)for(int i=0;i<facadePanels.Length;i++)facadePanels[i].position=facadeRest[i]+new Vector3((i%2==0?-1:1)*3*open,0,0);
            }
            if(mode=="openings"){
                float open=Progress(f,90,240);if(facadePanels!=null)for(int i=0;i<facadePanels.Length;i++)facadePanels[i].position=facadeRest[i]+Vector3.down*2.7f*open;
                float free=Progress(f,270,420);if(partitions!=null)for(int i=0;i<partitions.Length;i++)partitions[i].position=partitionRest[i]+Vector3.down*3*free;
            }
            if(mode=="alcove"&&chestLid)chestLid.localRotation=Quaternion.Euler(Mathf.Lerp(0,-65,Progress(f,600,690)),0,0);
            if(mode=="footings"&&movableBoard){
                Vector3 a=new Vector3(-4,.475f,2.2f),raised=new Vector3(-4,1.6f,2.2f),overGap=new Vector3(-2,1.6f,0),placed=new Vector3(-2,.325f,0);
                movableBoard.position=f<180?Vector3.Lerp(a,raised,Progress(f,90,180)):f<300?Vector3.Lerp(raised,overGap,Progress(f,180,300)):Vector3.Lerp(overGap,placed,Progress(f,300,360));
            }
        }
        void PoseOtherActors(int f){
            float t=f/(float)config.fps;
            if(mode=="courtyard"){
                float a=t*1.35f+1,b=t*1.1f+3;
                enemy.position=new Vector3(Mathf.PingPong(a,8)-4,0,0.5f);enemy.rotation=Quaternion.Euler(0,Mathf.Repeat(a,16)<8?90:270,0);
                secondEnemy.position=new Vector3(4-Mathf.PingPong(b,8),0,2.2f);secondEnemy.rotation=Quaternion.Euler(0,Mathf.Repeat(b,16)<8?270:90,0);
            }else if(mode=="flying")enemy.position=new Vector3(4.8f+Mathf.Sin(t)*.7f,2.5f+Mathf.Sin(t*1.6f)*.7f,0);
            else if(mode=="shield"||mode=="boss"){
                enemy.position=new Vector3(4.8f,0,0);
                if(mode=="shield"&&enemyShield){int cycle=f%120;float open=cycle>=60&&cycle<110?1:0;enemyShield.localPosition=new Vector3(0,1.1f-1.9f*open,.52f);}
            }
            else if(mode=="atrium"){
                enemy.position=new Vector3(Mathf.Sin(t*.7f)*3,0,1.2f);secondEnemy.position=new Vector3(-Mathf.Sin(t*.7f)*3,0,2.6f);
                enemy.rotation=Quaternion.Euler(0,Mathf.Cos(t*.7f)>=0?90:270,0);secondEnemy.rotation=Quaternion.Euler(0,Mathf.Cos(t*.7f)>=0?270:90,0);
            }
        }
        void PoseCameras(int f){
            Vector3 eye,target;
            if(IsEncounter){eye=new Vector3(0,3.8f,-12.5f);target=new Vector3(0,1.2f,0);}
            else if(mode=="scale"){eye=new Vector3(6,4,-8);target=new Vector3(0,1.2f,0);}
            else if(mode=="structure"){eye=Vector3.Lerp(new Vector3(8,5,-10),new Vector3(7,4,-8),Progress(f,120,660));target=new Vector3(0,1.7f,0);}
            else if(mode=="openings"){eye=player.transform.position+Vector3.up*config.playerEyeHeight;target=new Vector3(0,2,1.8f);}
            else if(mode=="atrium"){eye=player.transform.position+Vector3.up*config.playerEyeHeight;target=new Vector3(0,.8f,1.8f);}
            else if(mode=="courtyard"){eye=player.transform.position+Vector3.up*config.playerEyeHeight;target=new Vector3(0,1.3f,5.8f);}
            else if(mode=="alcove"){eye=player.transform.position+Vector3.up*config.playerEyeHeight;target=outwardTarget.position;}
            else if(mode=="plaza"){eye=player.transform.position+Vector3.up*config.playerEyeHeight;target=new Vector3(1,1.2f,2);}
            else if(mode=="footings"){eye=new Vector3(7,5,-10);target=new Vector3(0,.5f,0);}
            else{eye=player.transform.position+Vector3.up*config.playerEyeHeight;target=outwardTarget.position;}
            playerCamera.transform.position=eye;playerCamera.transform.rotation=Quaternion.LookRotation(target-eye);
            observerCamera.transform.position=config.observerPosition;observerCamera.transform.rotation=Quaternion.LookRotation(config.observerLookAt-config.observerPosition);
        }
        void SampleModels(float time,bool moving){
            Sample(playerModel,moving?walkingClip:idleClip,time);Sample(enemyModel,(mode=="courtyard"||mode=="atrium")?walkingClip:idleClip,time);
            Sample(secondEnemyModel,walkingClip,time);
        }
        static void Sample(ModelRest rest,AnimationClip clip,float time){
            if(rest==null||!rest.model)return;if(!clip)throw new InvalidOperationException("Actual authored-model animation clip missing");
            clip.SampleAnimation(rest.model.gameObject,Mathf.Repeat(time,clip.length));
            rest.model.localPosition=rest.position;rest.model.localRotation=rest.rotation;rest.model.localScale=rest.scale;
        }
        void Spawn(string team,Vector3 origin,Vector3 velocity,int frame){
            var go=GameObject.CreatePrimitive(PrimitiveType.Sphere);go.name="Own projectile "+projectiles.Count;go.layer=ProjectileLayer;
            DestroyImmediate(go.GetComponent<Collider>());go.transform.localScale=Vector3.one*.13f;go.transform.position=origin;
            go.GetComponent<Renderer>().sharedMaterial=team=="player"?playerShotMaterial:enemyShotMaterial;
            projectiles.Add(new ProjectileEvidence{id=go.name,team=team,previous=origin,position=origin,velocity=velocity,alive=true,createdAtAppliedFrame=frame});projectileVisuals.Add(go.transform);
        }
        void AdvanceProjectiles(float dt){
            for(int i=0;i<projectiles.Count;i++){
                var p=projectiles[i];if(!p.alive){projectileVisuals[i].gameObject.SetActive(p.hit&&Frame-p.hitAtFrame<12);continue;}p.previous=p.position;
                Vector3 movement=p.velocity*dt;RaycastHit hit;int mask=(1<<EnvironmentLayer)|(1<<(p.team=="player"?EnemyLayer:PlayerLayer));
                if(Physics.Raycast(p.position,movement.normalized,out hit,movement.magnitude,mask,QueryTriggerInteraction.Ignore)){
                    p.position=hit.point;p.actualHitPoint=hit.point;p.hitCollider=hit.collider.name;p.hit=true;p.alive=false;p.hitAtFrame=Frame;projectileVisuals[i].localScale=Vector3.one*.28f;
                }else p.position+=movement;
                if((p.position-p.previous).sqrMagnitude>0&&Mathf.Abs(p.position.x)>11)p.alive=false;
                projectileVisuals[i].position=p.position;projectileVisuals[i].gameObject.SetActive(p.alive||p.hit);
            }
        }
        string Phase(){
            if(mode=="scale")return Frame<240?"narrow-to-intimate-boundary":"intimate-to-open-boundary";
            if(mode=="structure")return Frame<240?"columns-reveal-illustrated-support":"wall-panels-withdraw-not-stress-simulation";
            if(mode=="openings")return Frame<240?"ribbon-window-opening":Frame<420?"interior-partitions-withdraw":"ramp-to-usable-roof";
            if(mode=="courtyard")return Frame<120?"scripted-observe":Frame<600?"scripted-cross":"scripted-new-observation";
            if(mode=="alcove")return Frame<300?"projecting-wall-conceals-target":Frame<600?"walk-around-projection":"target-revealed";
            if(mode=="footings")return Frame<180?"own-tool-illustration-lifts-board":Frame<360?"place-board-across-open-ground":Frame<690?"scripted-cross-supports-not-hazard-simulation":"new-support-position";
            return IsEncounter?CommandAt(Frame).id:"purposeful-outlook-and-section";
        }
        void Evaluate(){
            var output=new List<RayEvidence>();
            if(rayDefinitions!=null)for(int i=0;i<rayDefinitions.Length;i++){
                var spec=rayDefinitions[i];Vector3 a=spec.from.TransformPoint(spec.fromLocal),b=spec.to.TransformPoint(spec.toLocal),d=b-a;RaycastHit hit;
                bool blocked=Physics.Raycast(a,d.normalized,out hit,d.magnitude,1<<EnvironmentLayer,QueryTriggerInteraction.Ignore);
                var row=new RayEvidence{id=spec.id,meaning=spec.meaning,origin=a,desiredEndpoint=b,actualEndpoint=blocked?hit.point:b,blocked=blocked,hitCollider=blocked?hit.collider.name:null,distance=d.magnitude};output.Add(row);
                rayLines[i].positionCount=2;rayLines[i].SetPositions(new[]{a,row.actualEndpoint});rayLines[i].startColor=rayLines[i].endColor=blocked?new Color(.2f,.9f,.65f):new Color(1,.72f,.2f);
            }
            CurrentRays=output.ToArray();travelledLine.positionCount=travelled.Count;travelledLine.SetPositions(travelled.ToArray());
            CurrentState=new SupplementState{frame=Frame,timeSeconds=Frame/(float)config.fps,mode=mode,sourceKind="our-authored-illustration",phase=Phase(),appliedCommandFrame=appliedFrame,
                appliedCommandId=commandId,motionKind=IsEncounter?"CharacterController.Move with exact shared run/jump/fire tape":"declared scripted geometric illustration route",
                playerPosition=player.transform.position,requestedPlayerPosition=requested,actualMoveDelta=delta,collisionFlags=collisionFlags,enemyPosition=enemy?enemy.position:Vector3.zero,secondEnemyPosition=secondEnemy?secondEnemy.position:Vector3.zero,
                playerCameraEye=playerCamera.transform.position,playerCameraEuler=playerCamera.transform.eulerAngles,observerCameraEye=observerCamera.transform.position,observerCameraEuler=observerCamera.transform.eulerAngles,
                appliedJump=appliedJump,appliedFire=appliedFire,rays=CurrentRays,projectiles=projectiles.ToArray()};
        }
        static bool InFrustum(Vector3 p){return p.z>0&&p.x>=0&&p.x<=1&&p.y>=0&&p.y<=1;}
        public AnchorFrame ProjectedAnchors(){
            var result=new List<ProjectedAnchor>();
            foreach(var a in anchorDefinitions){Vector3 p=a.target.TransformPoint(a.localPoint),pv=playerCamera.WorldToViewportPoint(p),ov=observerCamera.WorldToViewportPoint(p);
                result.Add(new ProjectedAnchor{id=a.id,role=a.role,world=p,playerViewport=pv,observerViewport=ov,active=a.target.gameObject.activeInHierarchy,playerInFrustum=InFrustum(pv),observerInFrustum=InFrustum(ov)});}
            return new AnchorFrame{frame=Frame,anchors=result.ToArray()};
        }
    }
}
