using System;
using System.Collections.Generic;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif
namespace Yamyam.AnimationSeries {
public class AttackStudy : AnimationLessonStage {
    public int chapter;
    public Transform arm, forearm, hand, torso, blade, tip;
    public GameObject attacker, receiver;
    public SphereCollider contactTarget;
    public Vector3 origin;
    public float bladeLength = 1.35f;
    public int activeFrom=12, activeUntil=16, endFrame=48, earlyFrame=36;
    public int contactFrame=-1;
    public string visibleState;
    public int simulationFrame, freezeLeft;
    public bool hit, released;
    public Vector3 previousTip;
    public AnimationClip idleClip, runClip;
    public GameObject attackerModel;
    public bool allowEarlyRun=true, queueRun=true;
    protected override string GeneratedAssetRoot => "Assets/VideoScenes/animation-breaking-down-attack-animations";
    const string SwordPath="Assets/ThirdParty/YamyamAssetLibrary/080-free-medieval-weapons-small-low-poly-pack/Generated/Prefabs/Sword_1_A_0b109e96ef50.prefab";
    static readonly int[] keys={0,4,11,14,18,28,36,48};
    static readonly float[] shoulder={-58,62,111,8,-52,-62,-45,-58};
    static readonly float[] elbow={34,86,125,3,-29,-36,3,34};
    static readonly float[] edge={62,116,144,2,-49,-48,27,62};
    [SerializeField] Quaternion middleBase;
    [SerializeField] Quaternion[] baseRotation;
    static Vector3 Direction(float degrees) {
        float a=degrees*Mathf.Deg2Rad;
        return new Vector3(Mathf.Cos(a),Mathf.Sin(a),-.09f).normalized;
    }
    static float Curve(int f,float[] values) {
        int i=1;while(i<keys.Length-1 && keys[i]<f)i++;
        return Mathf.Lerp(values[i-1],values[i],Mathf.SmoothStep(0,1,Mathf.InverseLerp(keys[i-1],keys[i],f)));
    }
    static void Aim(Transform parent,Transform child,Vector3 dir) {
        parent.rotation=Quaternion.FromToRotation((child.position-parent.position).normalized,dir)*parent.rotation;
    }
    public override void Build() {
#if UNITY_EDITOR
        origin=new Vector3(-.92f,0,0);
        camera.orthographicSize=2.20f;camera.transform.position=new Vector3(0,1.58f,-15);camera.transform.LookAt(new Vector3(0,1.58f,0));
        attacker=Actor("검을 든 공격자",origin,false,2.45f,22);
        receiver=Actor("타격 대상",new Vector3(1.00f,0,.06f),true,2.32f,153);
        base.FlushPoses();
        attackerModel=attacker.transform.GetChild(0).gameObject;
        string clips=Library+"011-cartoon-city-massive-pack-characters-unity-godot-fbx/Characters Full/Unity FBX/Animations/";
        idleClip=ReadClip(clips+"Idle_A.fbx");runClip=ReadClip(clips+"Runing_A.fbx");
        foreach(var b in attacker.GetComponentsInChildren<Transform>()) {
            switch(b.name){case "Arm.R":arm=b;break;case "ForeArm.R":forearm=b;break;case "Hand.R":hand=b;break;case "Torso":torso=b;break;}
        }
        if(!arm||!forearm||!hand||!torso)throw new Exception("Required artist rig bones missing");
        middleBase=torso.localRotation;baseRotation=new[]{arm.localRotation,forearm.localRotation,hand.localRotation};
        blade=new GameObject("검 손잡이").transform;blade.SetParent(hand,false);
        var source=AssetDatabase.LoadAssetAtPath<GameObject>(SwordPath);
        var model=(GameObject)PrefabUtility.InstantiatePrefab(source,blade);
        model.transform.localPosition=Vector3.zero;model.transform.localRotation=Quaternion.identity;
        var renderers=model.GetComponentsInChildren<Renderer>();var bb=renderers[0].bounds;
        foreach(var r in renderers)bb.Encapsulate(r.bounds);
        // Normalize the imported mesh in world space so its longest axis runs from grip to tip.
        blade.SetParent(transform,true);blade.rotation=Quaternion.identity;blade.localScale=Vector3.one;
        model.transform.localScale=Vector3.one;model.transform.localRotation=Quaternion.identity;
        bb=renderers[0].bounds;foreach(var r in renderers)bb.Encapsulate(r.bounds);
        Vector3 size=bb.size;
        int axis=size.x>size.y && size.x>size.z?0:size.y>size.z?1:2;
        Vector3 localAxis=axis==0?Vector3.right:axis==1?Vector3.up:Vector3.forward;
        model.transform.rotation=Quaternion.FromToRotation(localAxis,Vector3.up);
        bb=renderers[0].bounds;foreach(var r in renderers)bb.Encapsulate(r.bounds);
        if(bb.size.z>bb.size.x)model.transform.Rotate(Vector3.up,90,Space.World);
        model.transform.localScale=Vector3.one*(bladeLength/Mathf.Max(.001f,size[axis]));
        bb=renderers[0].bounds;foreach(var r in renderers)bb.Encapsulate(r.bounds);
        model.transform.position+=blade.position-new Vector3(bb.center.x,bb.min.y+.12f,bb.center.z);
        blade.SetParent(hand,true);
        tip=new GameObject("검 끝").transform;tip.SetParent(blade,false);
        tip.position=blade.position+Vector3.up*(bladeLength-.12f); Layer(blade.gameObject);
        if(!usedAssetPaths.Contains(SwordPath))usedAssetPaths.Add(SwordPath);
        var hitZone=new GameObject("피격 영역");hitZone.transform.SetParent(receiver.transform,true);
        PoseFrame(14);
        hitZone.transform.position=tip.position;
        contactTarget=hitZone.AddComponent<SphereCollider>();contactTarget.radius=.16f;
        var edgeMark=Line("검날 강조",new[]{Vector3.zero,Vector3.up*(bladeLength-.12f)},Hex("395552"),.025f);
        edgeMark.transform.SetParent(blade,true);edgeMark.transform.position=blade.position;edgeMark.transform.rotation=blade.rotation;
        camera.backgroundColor=Hex("EBEFEB");
        for(int i=-8;i<=8;i++)Line("세로 격자 "+i,new[]{new Vector3(i*.52f,-.02f,.95f),new Vector3(i*.52f,3.7f,.95f)},Hex("BFCAC3"),.012f);
        for(int i=0;i<8;i++)Line("가로 격자 "+i,new[]{new Vector3(-4,i*.52f,.95f),new Vector3(4,i*.52f,.95f)},Hex("BFCAC3"),.012f);
        Apply(0);
#endif
    }
#if UNITY_EDITOR
    static AnimationClip ReadClip(string path){
        foreach(var asset in AssetDatabase.LoadAllAssetsAtPath(path))
            if(asset is AnimationClip clip && !clip.name.StartsWith("__preview__"))return clip;
        throw new Exception("Animation not found: "+path);
    }
#endif
    void Start(){if(Application.isPlaying && camera)camera.enabled=true;}
    void Update(){if(Application.isPlaying && arm)SetSample(Mathf.Max(0,Mathf.FloorToInt(Time.time*60)%108-18),allowEarlyRun,chapter==5 && queueRun,chapter==3);}
    void PoseFrame(int f) {
        attacker.transform.position=origin;
        torso.localRotation=middleBase*Quaternion.AngleAxis(24*Mathf.Sin(Mathf.PI*Mathf.Clamp01(f/28f)),Vector3.up);
        arm.localRotation=baseRotation[0];forearm.localRotation=baseRotation[1];hand.localRotation=baseRotation[2];
        Aim(arm,forearm,Direction(Curve(f,shoulder)));Aim(forearm,hand,Direction(Curve(f,elbow)));
        blade.position=hand.position;blade.rotation=Quaternion.FromToRotation(Vector3.up,Direction(Curve(f,edge)));
    }
    public void SetSample(int output, bool canRun, bool hasInput, bool hitStop) {
        receiver.transform.position=new Vector3(1,0,.06f);receiver.transform.rotation=Quaternion.Euler(0,153,0);
        idleClip.SampleAnimation(attackerModel,0);
        int t=Mathf.Max(0,output);int f=0;int hold=0;int at=-1;
        bool didHit=false;bool transitioned=false;
        PoseFrame(0);Vector3 prev=tip.position;
        for(int tick=0;tick<=Mathf.Min(t,70);tick++){
            if(tick>0 && hold>0){hold--;continue;}
            if(tick>0 && !transitioned)f=Mathf.Min(endFrame,f+1);
            PoseFrame(f);
            if(!didHit && f>=activeFrom && f<activeUntil){
                // Sweep the tip and the current blade against the measured target sphere.
                Vector3 center=contactTarget.transform.position;
                float d=Mathf.Min(DistanceToSegment(center,prev,tip.position),DistanceToSegment(center,hand.position,tip.position));
                if(d<=contactTarget.radius+.07f){didHit=true;at=f;if(hitStop)hold=6;}
            }
            if(hasInput && f>=(canRun?earlyFrame:endFrame))transitioned=true;
            prev=tip.position;
        }
        simulationFrame=f;released=transitioned;hit=didHit;freezeLeft=hold;contactFrame=at;previousTip=tip.position;
        float recoil=didHit?Mathf.Sin(Mathf.PI*Mathf.Clamp01((f-at)/16f)):0;
        receiver.transform.position=new Vector3(1+.15f*recoil,0,.06f);
        receiver.transform.rotation=Quaternion.Euler(0,153,-9*recoil);
        if(transitioned){
            float travel=Mathf.Max(0,t-(canRun?earlyFrame:endFrame))/60f;
            attacker.transform.position=origin+new Vector3(Mathf.Min(1.15f,travel*2),0,-.6f*travel);
            runClip.SampleAnimation(attackerModel,travel%runClip.length);
            blade.position=hand.position;blade.rotation=Quaternion.FromToRotation(Vector3.up,Direction(52));
        }
        visibleState=transitioned?"run":f==0?"standby":f<12?"lead-in":f<18?"attack":f<48?"follow-through":"idle";
    }
    static float DistanceToSegment(Vector3 p,Vector3 a,Vector3 b){
        Vector3 ab=b-a;return Vector3.Distance(p,a+ab*Mathf.Clamp01(Vector3.Dot(p-a,ab)/Mathf.Max(.000001f,ab.sqrMagnitude)));
    }
    public override void Apply(float t){if(arm)SetSample(Mathf.RoundToInt(t*60),chapter==5,chapter==5,chapter==3);}
}
}
