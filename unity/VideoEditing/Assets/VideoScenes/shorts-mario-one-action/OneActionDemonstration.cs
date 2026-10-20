using UnityEngine;

namespace YamyamCoding.Shorts.OneAction {
    /// <summary>Our executable analogy, not a claim about Mario's internal code.</summary>
    public class OneActionDemonstration : MonoBehaviour {
        public enum TargetKind { Reward, CapturableCharacter }
        public TargetKind targetKind;
        public Transform caster, target, projectile;
        public Collider targetCollider;
        public Renderer[] targetRenderers;
        public AnimationClip idleClip,throwClip,walkClip;
        public float launchAt=.85f, speed=3.5f, radius=.20f;
        public Vector3 origin=new Vector3(-1.55f,1.05f,0), direction=Vector3.right;
        public int rewards;
        public bool inputPressed, contact, captured, targetIsControlled;
        public float contactTime=-1;
        public float inputTime=-1,moveInput;
        public string controlledObject;
        public Vector3 contactPoint;
        public bool inspectorPlayback=true;
        float elapsed; Vector3 targetStart,casterStart,casterScale,targetScale;
        public void ResetDemonstration() {
            rewards=0;inputPressed=contact=captured=targetIsControlled=false;contactTime=inputTime=-1;moveInput=0;controlledObject="caster";
            targetStart=target.position;casterStart=caster.position;casterScale=caster.localScale;targetScale=target.localScale;projectile.gameObject.SetActive(false);elapsed=0;
        }
        void Start(){ResetDemonstration();}
        void Update(){if(inspectorPlayback){ReadLiveInput(out var press,out var horizontal);Step(Time.deltaTime,press,horizontal);Animate();}}
        static void ReadLiveInput(out bool press,out float horizontal){
            press=false;horizontal=0;
            #if ENABLE_INPUT_SYSTEM
            var keyboard=UnityEngine.InputSystem.Keyboard.current;
            if(keyboard!=null){press=keyboard.spaceKey.wasPressedThisFrame;horizontal=(keyboard.rightArrowKey.isPressed||keyboard.dKey.isPressed?1:0)-(keyboard.leftArrowKey.isPressed||keyboard.aKey.isPressed?1:0);}
            #elif ENABLE_LEGACY_INPUT_MANAGER
            press=Input.GetKeyDown(KeyCode.Space);horizontal=Input.GetAxisRaw("Horizontal");
            #endif
        }
        void Animate(){
            if(idleClip){var p=caster.position;float u=inputTime>=0?elapsed-inputTime:-1;var clip=throwClip&&u>=0&&u<throwClip.length?throwClip:(!captured&&Mathf.Abs(moveInput)>.01f&&walkClip?walkClip:idleClip);clip.SampleAnimation(caster.gameObject,clip==throwClip?u:elapsed%clip.length);caster.position=p;caster.localScale=casterScale;caster.rotation=Quaternion.Euler(0,90,0);}
            if(targetKind==TargetKind.CapturableCharacter&&idleClip){var p=target.position;var clip=captured&&Mathf.Abs(moveInput)>.01f&&walkClip?walkClip:idleClip;clip.SampleAnimation(target.gameObject,elapsed%clip.length);target.position=p;target.localScale=targetScale;target.rotation=Quaternion.Euler(0,captured&&Mathf.Abs(moveInput)>.01f?90:0,0);}
        }
        public Transform ActiveControlledTransform=>targetIsControlled?target:caster;
        public void Step(float delta,bool press=false,float horizontalInput=0) {
            elapsed+=delta;
            moveInput=Mathf.Clamp(horizontalInput,-1,1);controlledObject=targetIsControlled?"target":"caster";
            ActiveControlledTransform.position+=Vector3.right*(moveInput*.4f*delta);
            if(!inputPressed && press){inputPressed=true;inputTime=elapsed;projectile.gameObject.SetActive(true);projectile.position=origin;}
            if(contact)return;
            if(!inputPressed)return;
            var a=projectile.position;var travel=speed*delta;
            Physics.SyncTransforms();
            var hits=Physics.SphereCastAll(a,radius,direction,travel,~0,QueryTriggerInteraction.Collide);
            System.Array.Sort(hits,(x,y)=>x.distance.CompareTo(y.distance));
            foreach(var hit in hits) {
                if(hit.collider!=targetCollider)continue;
                contact=true;contactTime=elapsed;contactPoint=hit.point;
                projectile.position=a+direction*hit.distance;projectile.gameObject.SetActive(false);
                if(targetKind==TargetKind.Reward){rewards++;target.gameObject.SetActive(false);}
                else{captured=true;targetIsControlled=true;controlledObject="target";if(targetRenderers!=null)foreach(var renderer in targetRenderers)renderer.material.color=new Color(.573f,.875f,.612f);}
                return;
            }
            projectile.position=a+direction*travel;
        }
        public float Elapsed=>elapsed;
    }
}
