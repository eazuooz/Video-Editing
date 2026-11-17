using System.Collections;
using UnityEngine;
namespace Yamyam.LofiRoom
{
    // Existing licensed reclining body and reading-arm clips are combined by
    // an Avatar Mask. IK fits the book after that native motion is evaluated.
    public sealed class LofiSofaReading:MonoBehaviour
    {
        LofiLivingRoom living;LofiRoomSample room;Transform sofa;int armLayer;bool hasWoodTable;
        Vector3 bodyShift;float feetProgress;
        public void Initialize(LofiLivingRoom owner,GameObject prefab)
        {
            living=owner;room=owner.room;sofa=Instantiate(prefab).transform;sofa.name="Supported reading sofa";sofa.position=new Vector3(-.52f,.085f,-.75f);sofa.rotation=Quaternion.Euler(0,150,0);living.lounge=sofa;
            armLayer=room.actor.GetLayerIndex("Sofa reading arms");hasWoodTable=owner.readingTablePrefab;
            var fabric=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.71f,.65f,.50f)};fabric.SetFloat("_Smoothness",.08f);
            if(hasWoodTable)
            {
                var table=Instantiate(owner.readingTablePrefab,sofa);table.name="Oak and woven coffee table - feet on top";table.transform.localPosition=new Vector3(-.28f,0,.94f);table.transform.localRotation=Quaternion.identity;
            }
            else
            {
                Cushion("large supporting back cushion",new Vector3(-.35f,.77f,-.20f),new Vector3(.62f,.63f,.17f),fabric,new Vector3(-18,0,0));
                Cushion("reading footrest",new Vector3(-.35f,.31f,.92f),new Vector3(.87f,.37f,.58f),fabric,Vector3.zero);
            }
        }
        void Cushion(string name,Vector3 p,Vector3 scale,Material mat,Vector3 euler)
        {
            var o=GameObject.CreatePrimitive(PrimitiveType.Cube);o.name=name;o.transform.SetParent(sofa,false);o.transform.localPosition=p;o.transform.localScale=scale;o.transform.localEulerAngles=euler;o.GetComponent<Renderer>().sharedMaterial=mat;Destroy(o.GetComponent<Collider>());
            var mesh=new Mesh{name="Rounded upholstered cushion"};var vertices=new System.Collections.Generic.List<Vector3>();var normals=new System.Collections.Generic.List<Vector3>();var uv=new System.Collections.Generic.List<Vector2>();var triangles=new System.Collections.Generic.List<int>();const int steps=10;
            foreach(var normal in new[]{Vector3.right,Vector3.left,Vector3.up,Vector3.down,Vector3.forward,Vector3.back})
            {
                var axisU=Mathf.Abs(normal.x)>.5f?Vector3.forward:Vector3.right;var axisV=Vector3.Cross(normal,axisU);int first=vertices.Count;
                for(int y=0;y<=steps;y++)for(int x=0;x<=steps;x++){var point=normal*.5f+axisU*(x/(float)steps-.5f)+axisV*(y/(float)steps-.5f);var inside=new Vector3(Mathf.Clamp(point.x,-.38f,.38f),Mathf.Clamp(point.y,-.38f,.38f),Mathf.Clamp(point.z,-.38f,.38f));var n=(point-inside).normalized;vertices.Add(inside+n*.12f);normals.Add(n);uv.Add(new Vector2(x/(float)steps,y/(float)steps));}
                for(int y=0;y<steps;y++)for(int x=0;x<steps;x++){int i=first+y*(steps+1)+x;triangles.AddRange(new[]{i,i+1,i+steps+1,i+1,i+steps+2,i+steps+1});}
            }
            mesh.SetVertices(vertices);mesh.SetNormals(normals);mesh.SetUVs(0,uv);mesh.SetTriangles(triangles,0);mesh.RecalculateBounds();o.GetComponent<MeshFilter>().sharedMesh=mesh;

        }
        Vector3 Point(float z,float x=-.35f){var p=sofa.TransformPoint(new Vector3(x,0,z));p.y=room.groundY;return p;}
        IEnumerator WalkTo(Vector3 p){room.SetMotionTarget(p);while(Vector3.Distance(room.actor.transform.position,p)>.055f){var d=p-room.actor.transform.position;d.y=0;if(d.sqrMagnitude>.001f)room.actor.transform.rotation=Quaternion.RotateTowards(room.actor.transform.rotation,Quaternion.LookRotation(d),145*Time.deltaTime);yield return null;}}
        public IEnumerator Enter()
        {
            var a=room.activities;var actor=room.actor;room.HoldNativeMotion();a.phase="소파로 걸어가는 중";actor.speed=.74f;room.moving=true;actor.CrossFadeInFixedTime("Walk",.3f);
            // Approach through the open side, never through the footrest.
            yield return WalkTo(Point(1.45f,.65f));yield return WalkTo(Point(.45f,.65f));var seat=Point(.45f);yield return WalkTo(seat);
            room.moving=false;actor.speed=1;actor.CrossFadeInFixedTime("Idle",.25f);var rot=actor.transform.rotation;
            for(float t=0;t<.7f;t+=Time.deltaTime){actor.transform.rotation=Quaternion.Slerp(rot,sofa.rotation,Mathf.SmoothStep(0,1,t/.7f));yield return null;}
            actor.transform.SetPositionAndRotation(seat,sofa.rotation);living.reclined=true;a.seated=true;living.cushionWeight=0;living.bookWeight=0;feetProgress=0;a.phase="소파에 천천히 앉기";actor.CrossFadeInFixedTime("SofaDown",.42f);
            float duration=a.sitDuration;
            for(float t=0;t<duration;t+=Time.deltaTime){living.cushionWeight=Mathf.SmoothStep(0,1,t/duration);yield return null;}
            living.cushionWeight=1;actor.CrossFadeInFixedTime("SofaRead",.8f);
            if(hasWoodTable){a.phase="등을 기대고 테이블에 발 올리기";for(float t=0;t<1.8f;t+=Time.deltaTime){feetProgress=t/1.8f;yield return null;}feetProgress=1;}
            else{a.phase="쿠션에 등을 기대기";yield return new WaitForSeconds(.85f);}
            a.phase="책을 펼쳐 들기";
            for(float t=0;t<1.2f;t+=Time.deltaTime){living.bookWeight=Mathf.SmoothStep(0,1,t/1.2f);yield return null;}
            living.bookWeight=1;a.phase="소파에 기대어 책 읽는 중";
        }
        public IEnumerator Leave()
        {
            var a=room.activities;var actor=room.actor;a.phase="책을 정리하고 소파에서 일어나기";
            for(float t=0;t<.8f;t+=Time.deltaTime){living.bookWeight=1-Mathf.SmoothStep(0,1,t/.8f);yield return null;}living.bookWeight=0;
            if(hasWoodTable){actor.CrossFadeInFixedTime("SofaIdle",.6f);a.phase="테이블에서 발 내리고 자세 정리";for(float t=0;t<1.8f;t+=Time.deltaTime){feetProgress=1-t/1.8f;yield return null;}feetProgress=0;}
            actor.CrossFadeInFixedTime("SofaUp",.6f);float seconds=a.standDuration;
            for(float t=0;t<seconds;t+=Time.deltaTime){living.cushionWeight=1-Mathf.SmoothStep(0,1,t/seconds);yield return null;}
            living.cushionWeight=0;living.reclined=false;a.seated=false;if(armLayer>=0)actor.SetLayerWeight(armLayer,0);actor.CrossFadeInFixedTime("Idle",.35f);a.phase="소파 앞에서 자세 정리";yield return new WaitForSeconds(.35f);
            room.moving=true;actor.speed=.74f;actor.CrossFadeInFixedTime("Walk",.25f);yield return WalkTo(Point(.45f,.65f));yield return WalkTo(Point(1.45f,.65f));room.moving=false;actor.speed=1;actor.CrossFadeInFixedTime("Idle",.3f);a.phase="쉬는 중";
        }
        public void Fit()
        {
            var actor=room.actor;var a=room.activities;float w=living.cushionWeight,b=living.bookWeight;
            if(armLayer>=0)actor.SetLayerWeight(armLayer,w);
            var hips=actor.GetBoneTransform(HumanBodyBones.Hips);bodyShift=(sofa.TransformPoint(new Vector3(-.35f,hasWoodTable?.57f:.65f,-.035f))-hips.position)*w;actor.bodyPosition+=bodyShift;
            if(hasWoodTable)
            {
                // Lift the native legs clear of the tabletop before extending,
                // then lower the heels. Reverse that path before standing.
                Foot(AvatarIKGoal.LeftFoot,-1,w);Foot(AvatarIKGoal.RightFoot,1,w);
            }
            if(!a.book)return;
            var chest=actor.GetBoneTransform(HumanBodyBones.Chest);var head=actor.GetBoneTransform(HumanBodyBones.Head);
            var centre=chest.position+bodyShift+sofa.forward*.34f+Vector3.up*.07f;var across=sofa.right;var normal=Vector3.ProjectOnPlane(head.position+bodyShift-centre,across).normalized;
            a.book.position=centre;a.book.rotation=Quaternion.LookRotation(Vector3.Cross(across,normal),normal);a.book.localScale=Vector3.one*.88f;a.book.gameObject.SetActive(b>.035f);if(a.closedBook)a.closedBook.SetActive(b<=.035f);
            Hand(AvatarIKGoal.LeftHand,AvatarIKHint.LeftElbow,HumanBodyBones.LeftHand,HumanBodyBones.LeftUpperArm,-1,b);Hand(AvatarIKGoal.RightHand,AvatarIKHint.RightElbow,HumanBodyBones.RightHand,HumanBodyBones.RightUpperArm,1,b);
            actor.SetLookAtWeight(b*.55f,0,.75f,.35f,.7f);actor.SetLookAtPosition(centre);
        }
        void Foot(AvatarIKGoal goal,float side,float weight)
        {
            var floor=sofa.TransformPoint(new Vector3(-.35f+side*.13f,0,.34f));floor.y=room.groundY+.075f;
            var target=sofa.TransformPoint(new Vector3(-.35f+side*.13f,0,.73f));target.y=sofa.position.y+.44f+.075f;
            var lifted=floor;lifted.y=target.y+.16f;float u=Mathf.Clamp01(feetProgress);
            var position=u<.5f?Vector3.Lerp(floor,lifted,Mathf.SmoothStep(0,1,u*2)):Vector3.Lerp(lifted,target,Mathf.SmoothStep(0,1,(u-.5f)*2));
            room.actor.SetIKPositionWeight(goal,weight);room.actor.SetIKPosition(goal,position);
        }
        void Hand(AvatarIKGoal goal,AvatarIKHint hint,HumanBodyBones handBone,HumanBodyBones shoulderBone,float side,float w)
        {
            var actor=room.actor;var book=room.activities.book;var hand=actor.GetBoneTransform(handBone);string prefix=side<0?"mixamorig:LeftHand":"mixamorig:RightHand";Transform middle=null,index=null,little=null;
            foreach(var t in actor.GetComponentsInChildren<Transform>()){if(t.name==prefix+"Middle1")middle=t;if(t.name==prefix+"Index1")index=t;if(t.name==prefix+"Pinky1")little=t;}
            actor.SetIKPositionWeight(goal,w);actor.SetIKPosition(goal,book.TransformPoint(new Vector3(side*.20f,-.025f,-.09f)));
            if(middle&&index&&little){var forward=(middle.position-hand.position).normalized;var palm=Vector3.Cross(forward,index.position-little.position).normalized*(side<0?1:-1);var frame=Quaternion.LookRotation(forward,palm);var target=Quaternion.LookRotation(book.forward,side*book.right);actor.SetIKRotationWeight(goal,w);actor.SetIKRotation(goal,target*Quaternion.Inverse(frame)*actor.GetIKRotation(goal));}
            actor.SetIKHintPositionWeight(hint,w);actor.SetIKHintPosition(hint,actor.GetBoneTransform(shoulderBone).position+bodyShift+sofa.right*(side*.33f)-Vector3.up*.18f+sofa.forward*.14f);
        }
    }
}
