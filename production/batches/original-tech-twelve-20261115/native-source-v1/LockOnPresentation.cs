using UnityEngine;

namespace Yamyam.OriginalTechTwelve.LockOn {
    public class LockOnPresentation:MonoBehaviour {
        public string mode="target-relative";
        public Transform hero,enemyA,enemyB;
        public LineRenderer link,facing,ring;
        public Camera playerView,observerView;
        public AnimationClip idle,walk;
        public Material enemyAMaterial,enemyBMaterial;
        public bool livePlayback=true;
        public float elapsed;
        public State current;
        Vector3 heroScale,aScale,bScale;
        public void Initialize(){heroScale=hero.localScale;aScale=enemyA.localScale;bScale=enemyB.localScale;Apply(0);}
        void Start(){Initialize();}
        void Update(){if(livePlayback){elapsed=(elapsed+Time.deltaTime)%12;Apply(elapsed);}}
        static Vector3 At(Point p,float y=0){return new Vector3(p.x,y,p.z);}
        void Pose(Transform target,Point position,Point direction,float y,bool moving,Vector3 scale,float t){
            var animation=moving?walk:idle;
            if(animation)animation.SampleAnimation(target.gameObject,t%animation.length);
            target.position=At(position,y);target.localScale=scale;
            target.rotation=Quaternion.LookRotation(At(direction),Vector3.up);
        }
        public void Apply(float t){
            current=Model.Sample(mode,t);
            Pose(hero,current.hero,current.heroForward,current.heroY,current.sideInput!=0||current.forwardInput!=0,heroScale,t);
            Pose(enemyA,current.enemyA,(current.hero-current.enemyA).Normalized,0,current.attackA,aScale,t);
            Pose(enemyB,current.enemyB,(current.hero-current.enemyB).Normalized,0,current.attackB,bScale,t);
            enemyB.gameObject.SetActive(current.hasSecondEnemy);
            var target=At(current.selectedEnemy==0?current.enemyA:current.enemyB,.12f);
            link.enabled=current.targetRelative;link.SetPosition(0,At(current.hero,.12f));link.SetPosition(1,target);
            facing.SetPosition(0,At(current.hero,1.4f+current.heroY));facing.SetPosition(1,At(current.hero+current.heroForward*1.15f,1.4f+current.heroY));
            ring.enabled=current.targetRelative;
            for(int i=0;i<65;i++){float a=i*Mathf.PI*2/64;ring.SetPosition(i,target+new Vector3(Mathf.Cos(a),0,Mathf.Sin(a))*.65f);}
            enemyAMaterial.color=current.attackA?new Color(1,.46f,.12f):new Color(.78f,.84f,.9f);
            enemyBMaterial.color=current.attackB?new Color(1,.46f,.12f):new Color(.78f,.84f,.9f);
            // The camera response is an explicitly authored visualization of
            // the selected relationship, not an emulation of Zelda's camera.
            var heroAt=At(current.hero,.9f+current.heroY);
            playerView.transform.position=At(current.hero)+new Vector3(0,2.5f,-6.4f);
            playerView.transform.LookAt(current.targetRelative?(heroAt+target+Vector3.up*.9f)*.5f:heroAt);
        }
    }
}
