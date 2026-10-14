using System;
using System.Collections.Generic;
using UnityEngine;

// Reproducible lesson state. The same transaction code drives the scene and capture data.
[ExecuteAlways]
public class AiCraftLessonScene : MonoBehaviour
{
    public string sceneId = "17";
    public int durationFrames = 1800;
    public int captureFps = 60;
    public GameObject hero, potion;
    public Camera captureCamera;
    public AnimationClip walk, idle, interact, cheer;
    public SpriteRenderer pixelHero;
    public Transform delayedHero;
    public int inputFrame = 180;
    public int delayedInputFrames = 18;
    public AiCraftExtraScene extra;
    [NonSerialized] public State state;

    [Serializable] public class State
    {
        public int frame, gold, items, capacity, acceptedRequests, requestDeliveries;
        public string scene, scenario, result, requestId, clip;
        public float heroX, heroY, potionX, potionY, responseDelaySeconds;
    }
    public sealed class Wallet
    {
        public int gold, items, capacity, accepted, deliveries;
        readonly HashSet<string> processed = new HashSet<string>();
        public Wallet(int money, int inventory = 0, int limit = 3) { gold=money;items=inventory;capacity=limit; }
        public string Buy(string request, int price=30)
        {
            deliveries++;
            if(processed.Contains(request)) return "duplicate-ignored";
            if(gold < price) return "insufficient-gold";
            if(items >= capacity) return "inventory-full";
            gold-=price;items++;accepted++;processed.Add(request);return "purchased";
        }
    }
    public State ApplyFrame(int frame)
    {
        frame=Mathf.Clamp(frame,0,Mathf.Max(1,durationFrames)-1);
        if(extra) return extra.ApplyFrame(frame,this);
        if(sceneId=="20") return ApplyJump(frame);
        int count=sceneId=="17"?3:(sceneId=="18"||sceneId=="09")?2:1;
        int segment=Mathf.Max(1,durationFrames/count), part=Mathf.Min(count-1,frame/segment), local=frame-part*segment;
        if(sceneId=="23")local=480; // Identical pose, camera and scene; only lighting changes.
        bool plainReward=sceneId=="09"&&part==0;
        bool insufficient=sceneId=="17"&&part==1, full=sceneId=="17"&&part==2;
        var wallet=new Wallet(insufficient?20:100,full?3:0);
        string scenario=insufficient?"insufficient-gold":full?"inventory-full":sceneId=="09"?(plainReward?"numeric-feedback":"animated-feedback"):sceneId=="18"?(part==0?"same-request-retried":"two-distinct-purchases"):"normal-purchase";
        int arrive=Mathf.Min(180,segment/5), reach=arrive+Mathf.Min(60,segment/12), eventFrame=reach+60;
        string result="waiting",request="purchase-A";
        if(local>=eventFrame)result=wallet.Buy(request);
        if(sceneId=="18"&&local>=eventFrame+90){request=part==0?"purchase-A":"purchase-B";result=wallet.Buy(request);}
        string clip=local<arrive?"Walking_A":local<reach?"Idle":local<eventFrame+20?"Interact":wallet.accepted>0&&local<eventFrame+180?"Cheer":"Idle";
        if(plainReward&&local>=eventFrame)clip="Idle";
        var animation=clip=="Walking_A"?walk:clip=="Interact"?interact:clip=="Cheer"?cheer:idle;
        if(hero&&animation){float t=(clip=="Interact"?local-reach:local)/(float)captureFps;animation.SampleAnimation(hero,Mathf.Max(0,t)%animation.length);}
        if(hero){hero.transform.position=new Vector3(Mathf.Lerp(-2.7f,-.28f,Mathf.Clamp01(local/(float)arrive)),0,.50f);hero.transform.rotation=Quaternion.Euler(0,90,0);}
        if(potion){
            potion.SetActive(wallet.accepted==0||(!plainReward&&local<eventFrame+105));
            float u=wallet.accepted>0?Mathf.Clamp01((local-eventFrame)/105f):0;
            potion.transform.position=Vector3.Lerp(new Vector3(.56f,1.24f,-.12f),new Vector3(-.23f,1.2f,.8f),u)+Vector3.up*(Mathf.Sin(u*Mathf.PI)*.8f);
            potion.transform.localScale=Vector3.one*.85f*(1-Mathf.Clamp01((u-.7f)/.3f));
        }
        if(sceneId=="23") SetArtDirection(frame>=durationFrames/2);
        var hp=hero?captureCamera.WorldToViewportPoint(hero.transform.position+Vector3.up*1.3f):Vector3.zero;
        var pp=potion?captureCamera.WorldToViewportPoint(potion.transform.position):Vector3.zero;
        state=new State{frame=frame,scene=sceneId,scenario=scenario,result=result,requestId=request,gold=wallet.gold,items=wallet.items,capacity=wallet.capacity,acceptedRequests=wallet.accepted,requestDeliveries=wallet.deliveries,clip=clip,heroX=hp.x*1920,heroY=(1-hp.y)*1080,potionX=pp.x*1920,potionY=(1-pp.y)*1080};
        return state;
    }
    void SetArtDirection(bool cool)
    {
        foreach(var light in gameObject.scene.GetRootGameObjects()){
            var l=light.GetComponent<Light>();if(!l)continue;
            if(light.name=="Key"){l.color=cool?new Color(.62f,.73f,1):new Color(1,.88f,.72f);l.intensity=cool?1.35f:2;}
            if(light.name=="Fill"){l.color=cool?new Color(.95f,.55f,.76f):new Color(.55f,.8f,1);l.intensity=cool?.45f:.8f;}
        }
    }
    State ApplyJump(int f)
    {
        int flight=72;
        float Jump(int trigger){float t=(f-trigger)/(float)flight;return t>=0&&t<=1?4*2.2f*t*(1-t):0;}
        if(pixelHero)pixelHero.transform.position=new Vector3(-2.8f,-1.4f+Jump(inputFrame),0);
        if(delayedHero)delayedHero.position=new Vector3(2.8f,-1.4f+Jump(inputFrame+delayedInputFrames),0);
        state=new State{frame=f,scene=sceneId,scenario="same-distance-different-input-latency",result=f<inputFrame?"waiting":f<inputFrame+delayedInputFrames?"left-responded-right-waiting":"both-responded",responseDelaySeconds=delayedInputFrames/(float)captureFps};
        return state;
    }
}
