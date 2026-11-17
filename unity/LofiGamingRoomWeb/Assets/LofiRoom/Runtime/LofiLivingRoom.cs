using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.LofiRoom
{
    // The native KayKit lie-down/idle/get-up clips provide the body motion.
    // Contacts fit the cushion/book; they do not synthesize a body animation.
    public sealed class LofiLivingRoom:MonoBehaviour
    {
        public LofiRoomSample room;
        public float lieDuration=3,getUpDuration=3;
        public bool reclined,raining;
        public float cushionWeight,bookWeight;
        public Transform lounge;
        public Material rainTemplate;
        public GameObject readingSofaPrefab,sleepingCatPrefab;
        LofiSofaReading sofaReading;
        Transform catBody,earL,earR,tail;
        Mesh tailMesh;
        Material rainMaterial;
        Texture2D screen;
        float nextScreen;
        int screenFrame;
        static readonly Color Cream=new(.91f,.85f,.72f),Orange=new(.69f,.30f,.10f),Black=new(.105f,.09f,.08f);
        void Awake()
        {
            if(!room)room=GetComponent<LofiRoomSample>();
            if(readingSofaPrefab){sofaReading=gameObject.AddComponent<LofiSofaReading>();sofaReading.Initialize(this,readingSofaPrefab);}else MakeBeanbag();
            if(sleepingCatPrefab)MakeGeneratedCat();else MakeCat();
            MakeRain();MakeScreen();EnhanceRecord();
        }
        void MakeGeneratedCat()
        {
            var root=new GameObject("Tripo sleeping calico - generated from real CC0 photo").transform;root.position=new Vector3(2.15f,.095f,-.50f);root.rotation=Quaternion.Euler(0,-28,0);
            Form("separate oval cat rug",root,new Vector3(0,-.005f,0),new Vector3(1.15f,.036f,.84f),Mat("cat rug warm oat",new Color(.66f,.52f,.38f)));
            var model=Instantiate(sleepingCatPrefab,root.transform);model.name="Tripo calico sleeping model";model.transform.localPosition=Vector3.zero;model.AddComponent<LofiSleepingCatBreath>();
        }
        Material Mat(string name,Color c)
        {
            var m=new Material(Shader.Find("Universal Render Pipeline/Lit")){name=name,color=c};
            m.SetFloat("_Smoothness",.18f);return m;
        }
        Transform Form(string name,Transform parent,Vector3 pos,Vector3 scale,Material mat,PrimitiveType type=PrimitiveType.Sphere)
        {
            var o=GameObject.CreatePrimitive(type);o.name=name;o.transform.SetParent(parent,false);o.transform.localPosition=pos;o.transform.localScale=scale;
            o.GetComponent<Renderer>().sharedMaterial=mat;Destroy(o.GetComponent<Collider>());return o.transform;
        }
        void MakeBeanbag()
        {
            lounge=new GameObject("Central reading beanbag").transform;lounge.position=new Vector3(-.65f,.085f,-.65f);lounge.rotation=Quaternion.Euler(0,150,0);
            var cloth=Mat("woven sage beanbag",new Color(.33f,.43f,.34f));
            var mesh=new Mesh{name="Soft pear beanbag with depressed seat"};var v=new List<Vector3>();var uv=new List<Vector2>();var tris=new List<int>();const int lat=24,lon=56;
            for(int y=0;y<=lat;y++)for(int x=0;x<=lon;x++)
            {
                float p=y*Mathf.PI/lat,a=x*Mathf.PI*2/lon,sp=Mathf.Sin(p),z=sp*Mathf.Sin(a)*.86f,xx=sp*Mathf.Cos(a)*.69f;
                float yy=.29f+Mathf.Cos(p)*.29f;
                if(yy>.28f){float top=Mathf.InverseLerp(.28f,.58f,yy);yy+=top*(Mathf.Clamp01(-z/.7f)*.18f-.14f*Mathf.Exp(-(xx*xx/.25f+(z-.18f)*(z-.18f)/.32f)));}
                float fold=.012f*Mathf.Sin(a*13+sp*5)*sp;v.Add(new Vector3(xx*(1+fold),yy,z*(1+fold)));uv.Add(new Vector2(x/(float)lon,y/(float)lat));
            }
            for(int y=0;y<lat;y++)for(int x=0;x<lon;x++){int i=y*(lon+1)+x;tris.AddRange(new[]{i,i+1,i+lon+1,i+1,i+lon+2,i+lon+1});}
            mesh.SetVertices(v);mesh.SetUVs(0,uv);mesh.SetTriangles(tris,0);mesh.RecalculateNormals();mesh.RecalculateBounds();
            var body=new GameObject("beanbag soft fabric",typeof(MeshFilter),typeof(MeshRenderer));body.transform.SetParent(lounge,false);body.GetComponent<MeshFilter>().sharedMesh=mesh;body.GetComponent<Renderer>().sharedMaterial=cloth;
            Form("reading head cushion",lounge,new Vector3(-.50f,.55f,-.14f),new Vector3(.43f,.22f,.48f),Mat("linen cushion",Cream));
            var stitch=Mat("cream seam",Cream*.8f);
            var points=new List<Vector3>();for(int i=0;i<=80;i++){float a=i*Mathf.PI*2/80;points.Add(new Vector3(Mathf.Cos(a)*.67f,.19f,Mathf.Sin(a)*.83f));}Line("beanbag sewn piping",lounge,points,.006f,stitch);
        }
        void MakeCat()
        {
            var root=new GameObject("Sleeping calico cat").transform;root.position=new Vector3(2.15f,.095f,-.50f);root.rotation=Quaternion.Euler(0,-28,0);
            var rug=Mat("cat rug warm oat",new Color(.66f,.52f,.38f));Form("separate oval cat rug",root,new Vector3(0,-.005f,0),new Vector3(1.15f,.036f,.84f),rug);
            var white=Mat("calico ivory",Cream);var orange=Mat("calico amber",Orange);var black=Mat("calico dark fur",Black);var pink=Mat("ear and nose pink",new Color(.62f,.31f,.29f));
            catBody=new GameObject("sleep breathing body").transform;catBody.SetParent(root,false);catBody.localPosition=new Vector3(.09f,.17f,.02f);
            var fur=Form("curled calico torso",catBody,Vector3.zero,new Vector3(.68f,.35f,.44f),white);Calico(fur,white,false);
            var head=Form("sleeping calico head",catBody,new Vector3(-.30f,.015f,-.13f),new Vector3(.32f,.29f,.29f),white);Calico(head,white,true);
            Form("white muzzle",catBody,new Vector3(-.32f,-.035f,-.25f),new Vector3(.22f,.13f,.085f),white);
            Form("tiny pink nose",catBody,new Vector3(-.32f,-.016f,-.298f),new Vector3(.041f,.026f,.022f),pink);
            for(int i=0;i<2;i++)
            {
                float x=-.38f+i*.14f;var pts=new List<Vector3>();for(int k=0;k<9;k++){float u=k/8f;pts.Add(new Vector3(x+(u-.5f)*.07f, .060f-Mathf.Sin(u*Mathf.PI)*.012f,-.271f));}Line("closed sleeping eyelid",catBody,pts,.009f,black);
                var ear=new GameObject("twitching ear").transform;ear.SetParent(catBody,false);ear.localPosition=new Vector3(-.405f+i*.19f,.11f,-.09f);ear.localRotation=Quaternion.Euler(0,0,i==0?12:-12);
                Ear(ear,i==0?orange:white);var inner=Ear(ear,pink);inner.localScale=new Vector3(.57f,.66f,.57f);inner.localPosition=new Vector3(0,.018f,-.026f);if(i==0)earL=ear;else earR=ear;
                Form("tucked white paw",catBody,new Vector3(-.27f+i*.13f,-.105f,-.25f),new Vector3(.12f,.08f,.15f),white);
                for(int w=0;w<3;w++){float side=i==0?-1:1;Line("sleeping cat whisker",catBody,new List<Vector3>{new Vector3(-.32f+side*.065f,-.03f+w*.015f,-.284f),new Vector3(-.32f+side*.18f,-.04f+w*.026f,-.31f)},.0025f,white);}
            }
            tail=new GameObject("curled breathing tail").transform;tail.SetParent(root,false);tail.localPosition=new Vector3(.29f,.105f,.05f);
            MakeTail(white);
        }
        void MakeTail(Material basis)
        {
            var o=new GameObject("continuous soft curled tail",typeof(MeshFilter),typeof(MeshRenderer));o.transform.SetParent(tail,false);tailMesh=new Mesh{name="Continuous tapered cat tail"};
            const int rings=48,sides=16;var tris=new List<int>();var uv=new List<Vector2>();
            for(int i=0;i<=rings;i++)for(int j=0;j<=sides;j++){uv.Add(new Vector2(j/(float)sides,i/(float)rings));if(i<rings&&j<sides){int k=i*(sides+1)+j;tris.AddRange(new[]{k,k+1,k+sides+1,k+1,k+sides+2,k+sides+1});}}
            tailMesh.vertices=new Vector3[(rings+1)*(sides+1)];tailMesh.SetUVs(0,uv);tailMesh.SetTriangles(tris,0);o.GetComponent<MeshFilter>().sharedMesh=tailMesh;
            var tex=new Texture2D(16,128,TextureFormat.RGB24,true);for(int y=0;y<128;y++)for(int x=0;x<16;x++)tex.SetPixel(x,y,Color.Lerp(new Color(.60f,.32f,.15f),Black,Mathf.SmoothStep(0,1,Mathf.InverseLerp(.72f,.96f,y/127f))));tex.Apply();var m=new Material(basis){color=Color.white,mainTexture=tex};m.SetFloat("_Smoothness",.04f);o.GetComponent<Renderer>().sharedMaterial=m;UpdateTail(0);
        }
        void UpdateTail(float time)
        {
            if(!tailMesh)return;const int rings=48,sides=16;var v=new Vector3[(rings+1)*(sides+1)];
            for(int i=0;i<=rings;i++){float u=i/(float)rings,angle=u*2.15f;var centre=new Vector3(.12f*Mathf.Cos(angle)+Mathf.Sin(time*.9f-u*3.3f)*.018f*u,0,-.08f-u*.37f);var tangent=new Vector3(-.258f*Mathf.Sin(angle),0,-.37f).normalized;var side=Vector3.Cross(Vector3.up,tangent).normalized;float radius=Mathf.Lerp(.055f,.008f,Mathf.Pow(u,2.2f));for(int j=0;j<=sides;j++){float a=j*Mathf.PI*2/sides;v[i*(sides+1)+j]=centre+radius*(Mathf.Cos(a)*side+Mathf.Sin(a)*Vector3.up);}}
            tailMesh.vertices=v;tailMesh.RecalculateNormals();tailMesh.RecalculateBounds();
        }
        Transform Ear(Transform parent,Material m)
        {
            var o=new GameObject("soft triangular ear",typeof(MeshFilter),typeof(MeshRenderer));o.transform.SetParent(parent,false);
            var mesh=new Mesh();mesh.vertices=new[]{new Vector3(-.07f,0,-.035f),new Vector3(.07f,0,-.035f),new Vector3(0,.16f,.006f),new Vector3(0,0,.055f)};mesh.triangles=new[]{0,2,1,0,3,2,1,2,3,0,1,3};mesh.RecalculateNormals();o.GetComponent<MeshFilter>().sharedMesh=mesh;o.GetComponent<Renderer>().sharedMaterial=m;return o.transform;
        }
        void Calico(Transform t,Material white,bool head)
        {
            // A few anatomical coat patches, with a white belly and face.
            // Sample in 3D so the sphere's UV seam does not become a stripe.
            const int w=1024,h=512;var texture=new Texture2D(w,h,TextureFormat.RGB24,true);var px=new Color[w*h];
            float Patch(Vector3 p,Vector3 centre,Vector3 radii){var q=p-centre;q=new Vector3(q.x/radii.x,q.y/radii.y,q.z/radii.z);float edge=q.magnitude+(Mathf.PerlinNoise(p.x*9+12,p.z*9+p.y*3+8)-.5f)*.065f;return 1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(.94f,1.02f,edge));}
            for(int y=0;y<h;y++)for(int x=0;x<w;x++)
            {
                float a=x/(float)(w-1)*Mathf.PI*2,p=y/(float)(h-1)*Mathf.PI;var q=new Vector3(Mathf.Sin(p)*Mathf.Sin(a),-Mathf.Cos(p),Mathf.Sin(p)*Mathf.Cos(a));
                float amber=head?Patch(q,new Vector3(-.64f,.69f,.12f),new Vector3(.73f,.70f,.86f)):Mathf.Max(Patch(q,new Vector3(.23f,.87f,.24f),new Vector3(.90f,.70f,.91f)),Patch(q,new Vector3(-.68f,.35f,.48f),new Vector3(.59f,.68f,.63f)));
                float dark=head?0:Patch(q,new Vector3(.76f,.70f,-.30f),new Vector3(.48f,.42f,.60f));
                Color colour=Color.Lerp(new Color(.92f,.89f,.82f),new Color(.67f,.37f,.17f),amber);colour=Color.Lerp(colour,new Color(.15f,.135f,.12f),dark);
                float grain=(Mathf.PerlinNoise(x*.73f,y*.15f)-.5f)*.035f;px[y*w+x]=colour*(1+grain);
            }
            texture.SetPixels(px);texture.Apply(true);var m=new Material(white){name=head?"calico soft face coat":"calico natural saddle patches",mainTexture=texture,color=Color.white};m.SetFloat("_Smoothness",.035f);m.SetFloat("_Metallic",0);m.SetFloat("_SpecularHighlights",0);t.GetComponent<Renderer>().sharedMaterial=m;
        }
        void Line(string name,Transform p,List<Vector3> points,float width,Material m)
        {
            var o=new GameObject(name);o.transform.SetParent(p,false);var l=o.AddComponent<LineRenderer>();l.useWorldSpace=false;l.positionCount=points.Count;l.SetPositions(points.ToArray());l.widthMultiplier=width;l.numCapVertices=3;l.numCornerVertices=3;l.sharedMaterial=m;
        }
        void MakeRain()
        {
            if(room.rain)room.rain.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);
            var o=GameObject.CreatePrimitive(PrimitiveType.Quad);o.name="Visible window rain and glass drops";Destroy(o.GetComponent<Collider>());o.transform.position=new Vector3(-1.8f,1.78f,2.30f);o.transform.localScale=new Vector3(1.88f,1.92f,1);
            rainMaterial=rainTemplate?new Material(rainTemplate):new Material(Shader.Find("Yamyam/Window Rain"));o.GetComponent<Renderer>().sharedMaterial=rainMaterial;o.GetComponent<Renderer>().shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;SetRain(false);
        }
        public void SetRain(bool value){raining=value;if(rainMaterial)rainMaterial.SetFloat("_Rain",value?1:0);}
        public void SwitchWindowRain()=>SetRain(!raining);
        void MakeScreen()
        {
            var display=GameObject.Find("iMac quiet display");if(!display)return;
            foreach(var r in FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))if(r.name=="quiet work line")r.enabled=false;
            screen=new Texture2D(384,224,TextureFormat.RGB24,false){filterMode=FilterMode.Point};
            var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));m.color=Color.white;m.mainTexture=screen;m.EnableKeyword("_EMISSION");m.SetTexture("_EmissionMap",screen);m.SetColor("_EmissionColor",Color.white*.7f);display.GetComponent<Renderer>().enabled=false;
            var face=GameObject.CreatePrimitive(PrimitiveType.Quad);face.name="animated code display";Destroy(face.GetComponent<Collider>());face.transform.position=display.transform.position+new Vector3(0,0,-.006f);face.transform.localScale=new Vector3(.55f,.322f,1);face.GetComponent<Renderer>().sharedMaterial=m;DrawScreen();
        }
        void DrawScreen()
        {
            if(!screen)return;var dark=new Color32(17,28,36,255);var px=new Color32[384*224];for(int i=0;i<px.Length;i++)px[i]=dark;
            void Rect(int x,int y,int w,int h,Color32 c){for(int yy=Mathf.Max(0,y);yy<Mathf.Min(224,y+h);yy++)for(int xx=Mathf.Max(0,x);xx<Mathf.Min(384,x+w);xx++)px[(223-yy)*384+xx]=c;}
            Rect(0,0,384,19,new Color32(30,43,52,255));Rect(0,19,62,205,new Color32(22,34,43,255));
            string[] code=screenFrame%3==0?new[]{"FOCUSROOM.CS","VOID UPDATE() {","  IF (ISREADING) {","    TURNPAGE();","  }","  CAT.SLEEP();","  RAIN.SET(WEATHER);","}","// TAKE IT SLOW"}:screenFrame%3==1?new[]{"AMBIENCE.CS","VOID SETNIGHT() {","  MOON.SHOW();","  FIRE.GLOW();","  MUSIC.PLAY();","}","// ONE SMALL ROOM","// A QUIET EVENING"}:new[]{"PLAYLIST.CS","VOID NEXTSONG() {","  TRACK = NEXT();","  RECORD.SPIN();","}","IF (RAINING) {","  WINDOW.DROPS();","}"};
            for(int row=0;row<code.Length;row++){var colour=row==0?new Color32(208,188,131,255):row%3==0?new Color32(142,184,151,255):new Color32(175,202,218,255);DrawText(px,code[row],row==0?10:79,row==0?5:31+row*18,colour);}
            for(int i=0;i<6;i++)Rect(9,37+i*17,20+(i%3)*8,3,new Color32(80,110,120,255));Rect(82+(screenFrame%7)*21,199,2,10,new Color32(215,202,156,255));screen.SetPixels32(px);screen.Apply(false);
        }
        static readonly Dictionary<char,string> Glyphs=new(){
            ['A']="0111010001111111000110001",['B']="1111010001111101000111110",['C']="0111110000100001000001111",['D']="1111010001100011000111110",['E']="1111110000111101000011111",['F']="1111110000111101000010000",['G']="0111110000101111000101111",['H']="1000110001111111000110001",['I']="1111100100001000010011111",['J']="0011100010000101001001100",['K']="1000110010111001001010001",['L']="1000010000100001000011111",['M']="1000111011101011000110001",['N']="1000111001101011001110001",['O']="0111010001100011000101110",['P']="1111010001111101000010000",['Q']="0111010001100011001101111",['R']="1111010001111101001010001",['S']="0111110000011100000111110",['T']="1111100100001000010000100",['U']="1000110001100011000101110",['V']="1000110001100010101000100",['W']="1000110001101011101110001",['X']="1000101010001000101010001",['Y']="1000101010001000010000100",['Z']="1111100010001000100011111",['.']="0000000000000000010000100",['(']="0001000100001000010000010",[')']="0100000100001000010001000",['{']="0001100010001100001000011",['}']="1100001000110000100011000",[';']="0000000100000000010001000",['/']="0000100010001000100010000",['=']="0000011111000001111100000"};
        static void DrawText(Color32[] px,string s,int x,int y,Color32 c){foreach(char a in s){if(Glyphs.TryGetValue(a,out var g))for(int row=0;row<5;row++)for(int col=0;col<5;col++)if(g[row*5+col]=='1')for(int yy=0;yy<2;yy++)for(int xx=0;xx<1;xx++){int py=y+row*2+yy,pxx=x+col+xx;if(pxx<384&&py<224)px[(223-py)*384+pxx]=c;}x+=7;}}
        void EnhanceRecord()
        {
            var tt=FindAnyObjectByType<LofiTurntable>();if(!tt||!tt.record)return;
            var label=Mat("vinyl visible cream sector",Cream);var ring=new GameObject("asymmetric record rotation marker").transform;ring.SetParent(tt.record,false);
            Form("record cream rotation dot",ring,new Vector3(.28f,.67f,.09f),new Vector3(.08f,.15f,.08f),label,PrimitiveType.Cylinder);
        }
        void Update()
        {
            float t=Time.time;if(catBody){catBody.localScale=new Vector3(1,1+Mathf.Sin(t*1.25f)*.022f,1+Mathf.Sin(t*1.25f)*.008f);float pulse=Mathf.Pow(Mathf.Max(0,Mathf.Sin(t*.75f)),22);earL.localRotation=Quaternion.Euler(pulse*13,0,12+pulse*10);earR.localRotation=Quaternion.Euler(0,pulse*-12,-12-pulse*6);tail.localRotation=Quaternion.Euler(0,Mathf.Sin(t*.67f)*9,Mathf.Sin(t*.5f)*2);UpdateTail(t);}
            if(t>nextScreen){nextScreen=t+1.1f;screenFrame++;DrawScreen();}
        }
        public IEnumerator EnterLounge()
        {
            if(sofaReading){yield return sofaReading.Enter();yield break;}
            var a=room.activities;var actor=room.actor;room.HoldNativeMotion();a.phase="빈백으로 걸어가는 중";actor.speed=.74f;room.moving=true;actor.CrossFadeInFixedTime("Walk",.3f);
            var target=lounge.TransformPoint(new Vector3(0,0,1.08f));target.y=room.groundY;room.SetMotionTarget(target);
            while(Vector3.Distance(actor.transform.position,target)>.06f){var d=target-actor.transform.position;d.y=0;if(d.sqrMagnitude>.001f)actor.transform.rotation=Quaternion.RotateTowards(actor.transform.rotation,Quaternion.LookRotation(d),140*Time.deltaTime);yield return null;}
            room.moving=false;actor.speed=1;actor.CrossFadeInFixedTime("Idle",.25f);var from=actor.transform.rotation;var pos=actor.transform.position;var destination=target;
            // Align on the cushion before playing the original lie-down motion.
            for(float t=0;t<.8f;t+=Time.deltaTime){float u=Mathf.SmoothStep(0,1,t/.8f);actor.transform.rotation=Quaternion.Slerp(from,lounge.rotation,u);actor.transform.position=Vector3.Lerp(pos,destination,u);yield return null;}
            actor.transform.SetPositionAndRotation(destination,lounge.rotation);reclined=true;a.seated=true;a.phase="빈백에 천천히 기대기";actor.CrossFadeInFixedTime("LoungeDown",.45f);
            var rest=lounge.TransformPoint(new Vector3(0,0,.35f));rest.y=room.groundY;
            for(float t=0;t<lieDuration;t+=Time.deltaTime){float u=t/lieDuration;cushionWeight=Mathf.SmoothStep(0,1,u);actor.transform.position=Vector3.Lerp(destination,rest,Mathf.SmoothStep(0,1,Mathf.InverseLerp(.2f,.8f,u)));yield return null;}actor.transform.position=rest;cushionWeight=1;actor.CrossFadeInFixedTime("LoungeIdle",.5f);
            a.phase="책을 펼쳐 들기";for(float t=0;t<1.2f;t+=Time.deltaTime){bookWeight=Mathf.SmoothStep(0,1,t/1.2f);yield return null;}bookWeight=1;a.phase="빈백에 기대어 책 읽는 중";
        }
        public IEnumerator LeaveLounge()
        {
            if(sofaReading){yield return sofaReading.Leave();yield break;}
            var a=room.activities;var actor=room.actor;a.phase="책을 정리하고 일어나기";for(float t=0;t<.6f;t+=Time.deltaTime){bookWeight=1-Mathf.SmoothStep(0,1,t/.6f);yield return null;}bookWeight=0;actor.CrossFadeInFixedTime("LoungeUp",.4f);
            var rest=actor.transform.position;var stand=lounge.TransformPoint(new Vector3(0,0,1.08f));stand.y=room.groundY;
            for(float t=0;t<getUpDuration;t+=Time.deltaTime){float u=t/getUpDuration;cushionWeight=1-Mathf.SmoothStep(0,1,u);actor.transform.position=Vector3.Lerp(rest,stand,Mathf.SmoothStep(0,1,Mathf.InverseLerp(.3f,.9f,u)));yield return null;}actor.transform.position=stand;cushionWeight=0;reclined=false;a.seated=false;actor.speed=1;actor.CrossFadeInFixedTime("Idle",.4f);a.phase="쉬는 중";yield return new WaitForSeconds(.4f);
        }
        public void FitLounge()
        {
            if(sofaReading){sofaReading.Fit();return;}
            var actor=room.actor;var a=room.activities;
            var bodyShift=Vector3.up*(.22f*cushionWeight);actor.bodyPosition+=bodyShift;
            if(a.book)
            {
                var chest=actor.GetBoneTransform(HumanBodyBones.Chest);var head=actor.GetBoneTransform(HumanBodyBones.Head);var hips=actor.GetBoneTransform(HumanBodyBones.Hips);
                var leftShoulder=actor.GetBoneTransform(HumanBodyBones.LeftUpperArm);var rightShoulder=actor.GetBoneTransform(HumanBodyBones.RightUpperArm);
                var towardHips=Vector3.ProjectOnPlane(hips.position-head.position,Vector3.up).normalized;
                var centre=chest.position+bodyShift+Vector3.up*.30f+towardHips*.10f;
                var across=Vector3.ProjectOnPlane(rightShoulder.position-leftShoulder.position,Vector3.up).normalized;
                var normal=Vector3.ProjectOnPlane(head.position+bodyShift+Vector3.up*.035f-centre,across).normalized;
                a.book.position=centre;a.book.rotation=Quaternion.LookRotation(Vector3.Cross(across,normal),normal);a.book.localScale=Vector3.one*.88f;a.book.gameObject.SetActive(bookWeight>.03f);
                if(a.closedBook)a.closedBook.SetActive(bookWeight<=.03f);
                FitBookHand(AvatarIKGoal.LeftHand,AvatarIKHint.LeftElbow,HumanBodyBones.LeftHand,HumanBodyBones.LeftMiddleProximal,HumanBodyBones.LeftIndexProximal,HumanBodyBones.LeftLittleProximal,leftShoulder,-1,across,towardHips);
                FitBookHand(AvatarIKGoal.RightHand,AvatarIKHint.RightElbow,HumanBodyBones.RightHand,HumanBodyBones.RightMiddleProximal,HumanBodyBones.RightIndexProximal,HumanBodyBones.RightLittleProximal,rightShoulder,1,across,towardHips);
                actor.SetLookAtWeight(bookWeight*.4f,.1f,.45f,.3f,.6f);actor.SetLookAtPosition(centre);
            }
        }
        void FitBookHand(AvatarIKGoal goal,AvatarIKHint hint,HumanBodyBones handBone,HumanBodyBones middleBone,HumanBodyBones indexBone,HumanBodyBones littleBone,Transform shoulder,float side,Vector3 across,Vector3 towardHips)
        {
            var actor=room.actor;var book=room.activities.book;var hand=actor.GetBoneTransform(handBone);var middle=actor.GetBoneTransform(middleBone);var index=actor.GetBoneTransform(indexBone);var little=actor.GetBoneTransform(littleBone);
            string prefix=side<0?"mixamorig:LeftHand":"mixamorig:RightHand";foreach(var bone in actor.GetComponentsInChildren<Transform>()){if(!middle&&bone.name==prefix+"Middle1")middle=bone;if(!index&&bone.name==prefix+"Index1")index=bone;if(!little&&bone.name==prefix+"Pinky1")little=bone;}
            // Wrists stay outside the covers. Fingers point inward; elbows stay
            // out of the torso and away from the two page surfaces.
            var wrist=book.TransformPoint(new Vector3(side*.20f,-.025f,-.09f));
            actor.SetIKPositionWeight(goal,bookWeight);actor.SetIKPosition(goal,wrist);
            if(middle && index && little)
            {
                var forward=(middle.position-hand.position).normalized;var palm=Vector3.Cross(forward,index.position-little.position).normalized*(side<0?1:-1);
                var frame=Quaternion.LookRotation(forward,palm);var target=Quaternion.LookRotation(book.forward,side*book.right);
                // Humanoid IK goal axes include the Avatar's wrist offset.
                // Rotate that goal by the measured palm-frame delta.
                var nativeGoal=actor.GetIKRotation(goal);actor.SetIKRotationWeight(goal,bookWeight);actor.SetIKRotation(goal,target*Quaternion.Inverse(frame)*nativeGoal);
            }
            actor.SetIKHintPositionWeight(hint,bookWeight);actor.SetIKHintPosition(hint,shoulder.position+Vector3.up*(.22f*cushionWeight)+across*(side*.32f)+Vector3.up*.14f+towardHips*.19f);
        }
    }
}
