using System.Collections;
using UnityEngine;

namespace Yamyam.LofiRoom
{
    // Native clips supply all body poses. IK only fits existing seated arms
    // and feet to the furniture; actions are queued until safe boundaries.
    public sealed class LofiActivities:MonoBehaviour
    {
        public LofiRoomSample room;
        public Animator actor;
        public Transform leftKey,rightKey,book,leftPage,rightPage;
        public GameObject closedBook;
        public Vector3 seatRoot=new(1f,.0974f,.95f);
        public float sitDuration=1.15f,standDuration=1.15f;
        public string phase="쉬는 중";
        public bool seated;
        public float handWeight;
        public float readingWeight;
        public float seatWeight;
        public string requested="idle";
        public bool busy;
        Coroutine runner;
        string current="idle";
        public float maxHandError;
        Quaternion leftFootRotation,rightFootRotation;
        bool capturedFeet;
        public void Request(string mode)
        {
            if(!busy && mode==current)return;
            requested=mode;
            if(runner==null)runner=StartCoroutine(Run());
        }
        IEnumerator Run()
        {
            busy=true;
            while(requested!=current)
            {
                string next=requested;
                var living=room.GetComponent<LofiLivingRoom>();
                if(living && living.reclined)
                {yield return living.LeaveLounge();current="idle";continue;}
                if(living && next=="read" && !seated)
                {yield return living.EnterLounge();current="read";continue;}
                if(seated && (next=="idle" || (living && next=="read")))
                {
                    phase="책을 내려놓고 일어나기";
                    yield return FadeHands(0,0,.45f);
                    actor.CrossFadeInFixedTime("StandUp",.18f);
                    for(float t=0;t<standDuration;t+=Time.deltaTime){seatWeight=1-Mathf.SmoothStep(0,1,Mathf.Clamp01(t/(standDuration*.65f)));yield return null;}seatWeight=0;
                    seated=false;room.HoldNativeMotion();actor.speed=.74f;
                    phase="의자에서 한 걸음 비켜나기";actor.CrossFadeInFixedTime("Walk",.22f);room.moving=true;
                    foreach(var exit in new[]{new Vector3(1.62f,room.groundY,.95f),new Vector3(1.62f,room.groundY,-.45f)})
                    {
                        room.SetMotionTarget(exit);
                        while(Vector3.Distance(actor.transform.position,exit)>.075f)
                        {var d=exit-actor.transform.position;d.y=0;if(d.sqrMagnitude>.0001f)actor.transform.rotation=Quaternion.RotateTowards(actor.transform.rotation,Quaternion.LookRotation(d),150*Time.deltaTime);yield return null;}
                    }
                    room.moving=false;actor.speed=1;
                    actor.CrossFadeInFixedTime("Idle",.28f);
                    yield return new WaitForSeconds(.28f);
                    current="idle";phase="쉬는 중";
                    continue;
                }
                if(!seated && next!="idle")
                {
                    phase="의자로 걸어가는 중";
                    room.HoldNativeMotion();actor.speed=.74f;room.moving=true;
                    actor.CrossFadeInFixedTime("Walk",.3f);
                    // Approach from the open side, avoiding the chair back.
                    var path=new[]{new Vector3(1.62f,room.groundY,-.45f),new Vector3(1.62f,room.groundY,.95f),new Vector3(1,room.groundY,.95f)};
                    foreach(var target in path)
                    {
                        room.SetMotionTarget(target);
                        while(Vector3.Distance(actor.transform.position,target)>.045f)
                        {
                            Vector3 direction=target-actor.transform.position;direction.y=0;
                            actor.transform.rotation=Quaternion.RotateTowards(actor.transform.rotation,Quaternion.LookRotation(direction),170*Time.deltaTime);
                            yield return null;
                        }
                    }
                    room.moving=false;phase="의자 앞 정렬";
                    actor.CrossFadeInFixedTime("Idle",.2f);actor.speed=1;
                    Vector3 from=actor.transform.position;Quaternion rot=actor.transform.rotation;
                    var targetRoot=new Vector3(seatRoot.x,room.groundY,seatRoot.z);
                    for(float t=0;t<.50f;t+=Time.deltaTime)
                    {
                        float u=Mathf.SmoothStep(0,1,t/.50f);
                        actor.transform.position=Vector3.Lerp(from,targetRoot,u);
                        actor.transform.rotation=Quaternion.Slerp(rot,Quaternion.identity,u);yield return null;
                    }
                    actor.transform.SetPositionAndRotation(targetRoot,Quaternion.identity);
                    yield return new WaitForSeconds(.18f);
                    phase="천천히 의자에 앉기";actor.CrossFadeInFixedTime("SitDown",.40f);
                    for(float t=0;t<sitDuration;t+=Time.deltaTime)
                    {float u=Mathf.InverseLerp(sitDuration*.35f,sitDuration,t);seatWeight=u*u*u*(u*(u*6-15)+10);yield return null;}seatWeight=1;
                    seated=true;
                    actor.CrossFadeInFixedTime("Desk",.52f);yield return new WaitForSeconds(.62f);
                }
                if(next=="read")
                {
                    phase="책을 펼치는 중";
                    actor.CrossFadeInFixedTime("Read",.5f);
                    if(book)book.gameObject.SetActive(true);
                    yield return FadeHands(1,1,.9f);
                    phase="책 읽는 중";
                }
                else if(next=="computer")
                {
                    phase="키보드로 손 옮기기";
                    actor.CrossFadeInFixedTime("Desk",.5f);
                    yield return FadeHands(1,0,.7f);
                    phase="아이맥 작업 중";
                }
                current=next;
            }
            busy=false;runner=null;
        }
        IEnumerator FadeHands(float target,float reading,float seconds)
        {
            float from=handWeight,read=readingWeight;
            for(float t=0;t<seconds;t+=Time.deltaTime)
            {float u=Mathf.SmoothStep(0,1,t/seconds);handWeight=Mathf.Lerp(from,target,u);readingWeight=Mathf.Lerp(read,reading,u);yield return null;}
            handWeight=target;readingWeight=reading;
        }
        public void FitHands()
        {
            var living=room.GetComponent<LofiLivingRoom>();
            if(living && living.reclined){living.FitLounge();return;}
            if(book){book.position=Vector3.Lerp(new Vector3(1.47f,.85f,1.25f),new Vector3(1,.99f,1.12f),readingWeight);book.rotation=Quaternion.Slerp(Quaternion.identity,Quaternion.Euler(-18,0,0),readingWeight);book.gameObject.SetActive(readingWeight>.04f);}
            if(closedBook)closedBook.SetActive(readingWeight<=.04f);
            if(!actor)return;
            if(seatWeight>.001f)
            {
                var hips=actor.GetBoneTransform(HumanBodyBones.Hips);
                actor.bodyPosition+=(new Vector3(1,.60f,.84f)-hips.position)*seatWeight;
            }
            if(seated && actor.GetCurrentAnimatorStateInfo(0).IsName("Desk") && !actor.IsInTransition(0))
            {leftFootRotation=actor.GetIKRotation(AvatarIKGoal.LeftFoot);rightFootRotation=actor.GetIKRotation(AvatarIKGoal.RightFoot);capturedFeet=true;}
            if(seated && readingWeight>.01f && capturedFeet)
            {
                actor.SetIKPositionWeight(AvatarIKGoal.LeftFoot,readingWeight);actor.SetIKPositionWeight(AvatarIKGoal.RightFoot,readingWeight);
                actor.SetIKPosition(AvatarIKGoal.LeftFoot,new Vector3(.82f,.105f,1.25f));actor.SetIKPosition(AvatarIKGoal.RightFoot,new Vector3(1.18f,.105f,1.25f));
                actor.SetIKRotationWeight(AvatarIKGoal.LeftFoot,readingWeight);actor.SetIKRotationWeight(AvatarIKGoal.RightFoot,readingWeight);
                actor.SetIKRotation(AvatarIKGoal.LeftFoot,leftFootRotation);actor.SetIKRotation(AvatarIKGoal.RightFoot,rightFootRotation);
            }
            if(handWeight<.001f)return;
            Fit(AvatarIKGoal.LeftHand,leftKey,leftPage);Fit(AvatarIKGoal.RightHand,rightKey,rightPage);
            actor.SetLookAtWeight(.35f,.16f,.5f,.35f,.5f);
            actor.SetLookAtPosition(readingWeight>.5f?book.position: new Vector3(1,1.23f,1.65f));
        }
        void Fit(AvatarIKGoal goal,Transform keyboard,Transform page)
        {
            if(!keyboard || !page)return;
            actor.SetIKPositionWeight(goal,handWeight);actor.SetIKRotationWeight(goal,0);
            actor.SetIKPosition(goal,Vector3.Lerp(keyboard.position,page.position,readingWeight));actor.SetIKRotation(goal,Quaternion.Slerp(keyboard.rotation,page.rotation,readingWeight));
        }
    }
}
