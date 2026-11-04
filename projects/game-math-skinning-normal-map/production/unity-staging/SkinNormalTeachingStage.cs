using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.SkinNormal {
    [Serializable] public class SkinNormalShot {
        public string beatId="UNBOUND",englishTerm="Skeletal Animation",koreanTerm="골격 애니메이션",meaning="움직이는 본의 좌표계로 정점을 옮깁니다";
        public int beatIndex=1;
        public double durationSeconds; // Bind to the approved audio; no invented lecture duration.
        public double[] stepSeconds=Array.Empty<double>();
        public double[] stepPositions=Array.Empty<double>(); // Matching normalized visual positions, mapped from real spoken anchors.
        public bool expandedTerm=true,useObservedClip=false;
        public string clip="Interact";public float clipIn=0,clipOut=1;
        public float bendFrom=0,bendTo=105;
    }
    // A scene instance per beat can reuse these modules and imported assets.
    // There is no Update, wall clock, looping, renderer capture or file mutation here.
    public sealed partial class SkinNormalTeachingStage:MonoBehaviour {
        public SkinNormalShot shot=new SkinNormalShot();
        public GameObject knightPrefab;public AnimationClip[] knightClips;
        public Texture2D knightColorTexture;public Font koreanFont;public Camera stageCamera;
        public Material knightMaterialOverride;
        [NonSerialized] public bool built;public RigProbe lastProbe;
        public Vector3[] exportedTargets=Array.Empty<Vector3>();
        GameObject hero,armGroup,plateGroup;KnightRigAdapter rig;
        Vector3 heroRest,heroScale;Quaternion heroRotation;
        Mesh armMesh,plateMesh,highPatchMesh;Vector3[] armBind;float[] armWeights;
        Material surface,armMaterial,lineMaterial,heroMaterial;
        Texture2D normalData,heightData,constantNormalData;
        Canvas canvas;Text term,sourceKind,readout,explanation,code,objectLabel;
        readonly List<LineRenderer> lines=new List<LineRenderer>();int lineCursor;
        readonly List<GameObject> dots=new List<GameObject>();int dotCursor;
        readonly List<Text> tags=new List<Text>();int tagCursor;
        readonly List<UnityEngine.Object> owned=new List<UnityEngine.Object>();
        static readonly Color White=new Color(.96f,.96f,.96f),Yellow=new Color(.91f,.812f,.514f),Teal=new Color(.451f,.78f,.761f),Green=new Color(.643f,.776f,.627f),Red=new Color(.937f,.522f,.522f),Blue=new Color(.55f,.72f,.95f),Muted=new Color(.68f,.7f,.71f);
        static string Hex(Color c)=>ColorUtility.ToHtmlStringRGB(c);
        public void Build(){
            if(built)return;if(knightPrefab==null||koreanFont==null)throw new InvalidOperationException("Assign licensed Knight prefab and local dynamic Korean font.");
            // This component owns its child hierarchy. Reloaded saved scenes rebuild from the serialized shot.
            while(transform.childCount>0)DestroyImmediate(transform.GetChild(0).gameObject);
            var shader=Shader.Find("Yamyam/SkinNormalTeachingSurface");if(shader==null)throw new InvalidOperationException("Teaching surface shader not imported.");
            var unlit=Shader.Find("Universal Render Pipeline/Unlit");if(unlit==null)throw new InvalidOperationException("URP Unlit is required.");
            lineMaterial=Own(new Material(unlit){name="SkinNormal_Guides"});lineMaterial.SetColor("_BaseColor",Color.white);
            if(stageCamera==null){stageCamera=GO("M22_Camera").AddComponent<Camera>();stageCamera.transform.position=new Vector3(0,1.6f,-20);stageCamera.transform.rotation=Quaternion.identity;stageCamera.orthographic=true;stageCamera.orthographicSize=5.4f;stageCamera.nearClipPlane=.1f;stageCamera.farClipPlane=50;stageCamera.backgroundColor=Color.black;stageCamera.clearFlags=CameraClearFlags.SolidColor;stageCamera.allowHDR=false;}
            hero=Instantiate(knightPrefab,transform);hero.name="KayKit_Knight_Instance";owned.Add(hero);
            foreach(var t in hero.GetComponentsInChildren<Transform>(true))if(t.name.Contains("Sword")||t.name.Contains("Shield"))t.gameObject.SetActive(false);
            Bounds bounds=new Bounds();bool first=true;foreach(var r in hero.GetComponentsInChildren<Renderer>()){if(first){bounds=r.bounds;first=false;}else bounds.Encapsulate(r.bounds);}
            if(first||bounds.size.y<=0)throw new InvalidOperationException("No visible Knight bounds.");
            float scale=3.8f/bounds.size.y;hero.transform.localScale*=scale;
            hero.transform.position=new Vector3(-4.5f,-.3f,0)-new Vector3(bounds.center.x,bounds.min.y,bounds.center.z)*scale;
            hero.transform.rotation=Quaternion.Euler(0,160,0);heroRest=hero.transform.position;heroScale=hero.transform.localScale;heroRotation=hero.transform.rotation;
            if(knightMaterialOverride!=null)heroMaterial=knightMaterialOverride;else {var lit=Shader.Find("Universal Render Pipeline/Lit");if(lit==null)throw new InvalidOperationException("URP Lit required for Knight.");heroMaterial=Own(new Material(lit){name="Knight_InstanceMaterial"});heroMaterial.SetColor("_BaseColor",Color.white);heroMaterial.SetFloat("_Smoothness",.35f);if(knightColorTexture!=null)heroMaterial.SetTexture("_BaseMap",knightColorTexture);}
            foreach(var r in hero.GetComponentsInChildren<Renderer>(true))r.sharedMaterial=heroMaterial;
            rig=new KnightRigAdapter(hero,knightClips);rig.SelectActualArmProbe();
            var key=GO("M22_Key").AddComponent<Light>();key.type=LightType.Directional;key.intensity=1.7f;key.transform.rotation=Quaternion.Euler(35,-30,0);
            var fill=GO("M22_Fill").AddComponent<Light>();fill.type=LightType.Directional;fill.intensity=.45f;fill.transform.rotation=Quaternion.Euler(20,140,0);
            constantNormalData=Own(new Texture2D(1,1,TextureFormat.RGBA32,false,true){name="Own_RGB37_128_218_Linear",filterMode=FilterMode.Point});constantNormalData.SetPixels32(new[]{new Color32(37,128,218,255)});constantNormalData.Apply();
            normalData=Own(new Texture2D(256,256,TextureFormat.RGBA32,false,true){name="Own_AnalyticNormalXYZ_Linear",wrapMode=TextureWrapMode.Repeat,filterMode=FilterMode.Bilinear});
            heightData=Own(new Texture2D(256,256,TextureFormat.RGBA32,false,true){name="Own_AnalyticHeight_Linear",wrapMode=TextureWrapMode.Repeat});
            var colors=new Color[256*256];var heights=new Color[colors.Length];for(int y=0;y<256;y++)for(int x=0;x<256;x++){var n=SkinNormalMath.Encode(SkinNormalMath.HeightNormal((x+.5)/256,(y+.5)/256));colors[y*256+x]=new Color((float)n.x,(float)n.y,(float)n.z,1);float h=(float)(.5+SkinNormalMath.Height((x+.5)/256,(y+.5)/256)*10);heights[y*256+x]=new Color(h,h,h,1);}normalData.SetPixels(colors);normalData.Apply();heightData.SetPixels(heights);heightData.Apply();
            surface=Own(new Material(shader){name="Own_NormalMappingImplementation"});surface.SetTexture("_NormalRGB",normalData);surface.SetColor("_BaseColor",new Color(.48f,.57f,.62f));
            armMaterial=Own(new Material(shader){name="Own_TwoBoneSleeve"});armMaterial.SetTexture("_NormalRGB",normalData);armMaterial.SetFloat("_UseNormal",0);
            armGroup=GO("ExplicitTwoBoneSleeve");armGroup.transform.position=new Vector3(2,1.15f,0);armMesh=BuildSleeve();Attach(armGroup,armMesh,armMaterial);
            plateGroup=GO("SameArmorSurface_TestPatch");plateGroup.transform.position=new Vector3(2.1f,1.6f,0);plateMesh=BuildPatch();highPatchMesh=BuildHighPatch();Attach(plateGroup,plateMesh,surface);
            var ui=GO("M22_Labels");canvas=ui.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=stageCamera;canvas.planeDistance=1;
            var scaler=ui.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);
            term=Label("CanonicalTerm",new Rect(75,42,1200,152),42,Yellow);
            sourceKind=Label("CurrentPicture",new Rect(1320,45,535,104),40,Muted);
            readout=Label("CurrentValues",new Rect(75,748,1790,63),44,Teal);
            explanation=Label("Meaning",new Rect(75,817,1790,65),42,White);
            code=Label("CodeAndFormula",new Rect(80,292,850,365),40,White);code.supportRichText=true;
            objectLabel=Label("SameObject",new Rect(85,205,860,58),40,White);
            built=true;
        }
        T Own<T>(T o) where T:UnityEngine.Object {owned.Add(o);return o;}
        GameObject GO(string name){var g=new GameObject(name);g.transform.SetParent(transform,false);owned.Add(g);return g;}
        void Attach(GameObject go,Mesh mesh,Material material){go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=material;}
        Text Label(string name,Rect r,int size,Color color){var g=new GameObject(name);g.transform.SetParent(canvas.transform,false);var rt=g.AddComponent<RectTransform>();rt.anchorMin=rt.anchorMax=rt.pivot=new Vector2(0,1);rt.anchoredPosition=new Vector2(r.x,-r.y);rt.sizeDelta=new Vector2(r.width,r.height);var t=g.AddComponent<Text>();t.font=koreanFont;t.fontSize=size;t.color=color;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;return t;}
        // Math uses a right-handed display frame. Reflection maps +z toward our front camera.
        static Vector3 U(Vec p)=>new Vector3((float)p.x,(float)p.y,(float)-p.z);
        Vector3 At(Vec p)=>new Vector3(2.0f,.4f,-.7f)+U(p)*1.15f;
        LineRenderer Line(Color color,float width=.035f){LineRenderer r;if(lineCursor==lines.Count){var g=GO("Guide"+lines.Count);r=g.AddComponent<LineRenderer>();r.sharedMaterial=lineMaterial;r.useWorldSpace=true;r.numCapVertices=5;r.numCornerVertices=4;lines.Add(r);}else r=lines[lineCursor];lineCursor++;r.enabled=true;r.startWidth=r.endWidth=width;var p=new MaterialPropertyBlock();p.SetColor("_BaseColor",color);r.SetPropertyBlock(p);return r;}
        void Path(Color c,params Vector3[] points){var r=Line(c);r.positionCount=points.Length;r.SetPositions(points);}
        void Arrow(Vector3 from,Vector3 to,Color c){if((to-from).sqrMagnitude<1e-8f)return;Vector3 d=(to-from).normalized;Vector3 side=Vector3.Cross(d,stageCamera.transform.forward).normalized;if(side.sqrMagnitude<.1f)side=stageCamera.transform.right;Path(c,from,to);Path(c,to-d*.16f+side*.09f,to,to-d*.16f-side*.09f);}
        void Dot(Vector3 p,Color c,float size=.10f){GameObject g;if(dotCursor==dots.Count){g=GameObject.CreatePrimitive(PrimitiveType.Sphere);g.name="VertexMarker"+dots.Count;g.transform.SetParent(transform,false);DestroyImmediate(g.GetComponent<Collider>());g.GetComponent<Renderer>().sharedMaterial=lineMaterial;dots.Add(g);owned.Add(g);}else g=dots[dotCursor];dotCursor++;g.SetActive(true);g.transform.position=p;g.transform.localScale=Vector3.one*size;var block=new MaterialPropertyBlock();block.SetColor("_BaseColor",c);g.GetComponent<Renderer>().SetPropertyBlock(block);}
        void Tag(Vector3 point,string text,Color c,Vector2 offset){Text t;if(tagCursor==tags.Count){t=Label("TargetTag"+tags.Count,new Rect(0,0,780,105),40,c);tags.Add(t);}else t=tags[tagCursor];tagCursor++;t.gameObject.SetActive(true);t.text=text;t.color=c;Vector3 v=stageCamera.WorldToViewportPoint(point);float estimated=24;foreach(char ch in text)estimated+=ch>255?40:24;float width=Mathf.Clamp(estimated,240,700);t.rectTransform.sizeDelta=new Vector2(width,105);t.rectTransform.anchoredPosition=new Vector2(Mathf.Clamp(v.x*1920+offset.x,75,1845-width),-Mathf.Clamp((1-v.y)*1080+offset.y,210,640));}
        void Axes(Vector3 origin,Vector3 t,Vector3 b,Vector3 n,float length=.85f){Arrow(origin,origin+t*length,Teal);Arrow(origin,origin+b*length,Green);Arrow(origin,origin+n*length,Blue);Tag(origin+t*length,"T · +u",Teal,new Vector2(8,0));Tag(origin+b*length,"B · +v",Green,new Vector2(8,-65));Tag(origin+n*length,"N · 표면 밖",Blue,new Vector2(-260,0));}
        void ResetPools(){lineCursor=dotCursor=tagCursor=0;code.text="";readout.text="";explanation.text="";objectLabel.text="같은 캐릭터 · 같은 표면";armGroup.SetActive(false);plateGroup.SetActive(false);hero.SetActive(true);hero.transform.position=heroRest;hero.transform.localScale=heroScale;hero.transform.rotation=heroRotation;rig.Restore();surface.SetTexture("_NormalRGB",normalData);surface.SetFloat("_UseNormal",1);surface.SetFloat("_ShowData",0);surface.SetFloat("_WrongObjectSpace",0);surface.SetFloat("_GreenSign",1);plateGroup.transform.rotation=Quaternion.identity;plateGroup.transform.localScale=Vector3.one;plateGroup.GetComponent<MeshFilter>().sharedMesh=plateMesh;SetPatchUV(false);armMaterial.SetFloat("_WeightTint",0);}
        void FinishPools(){for(int i=lineCursor;i<lines.Count;i++)lines[i].enabled=false;for(int i=dotCursor;i<dots.Count;i++)dots[i].SetActive(false);for(int i=tagCursor;i<tags.Count;i++)tags[i].gameObject.SetActive(false);}
        public void Evaluate(double cueSeconds){
            if(shot.durationSeconds<=0)throw new InvalidOperationException("Bind actual speech duration first.");
            double u=SkinNormalMath.Clamp01(cueSeconds/shot.durationSeconds);
            if(shot.stepSeconds!=null&&shot.stepSeconds.Length>0){
                if(shot.stepPositions==null||shot.stepPositions.Length!=shot.stepSeconds.Length||shot.stepSeconds.Length<2)throw new InvalidOperationException("Each real speech anchor needs an explicit visual position.");
                var times=shot.stepSeconds;var positions=shot.stepPositions;
                if(Math.Abs(times[0])>1e-8||Math.Abs(times[times.Length-1]-shot.durationSeconds)>.001||Math.Abs(positions[0])>1e-8||Math.Abs(positions[positions.Length-1]-1)>1e-8)throw new InvalidOperationException("Speech/visual maps must span the complete cue.");
                u=positions[0];
                for(int i=1;i<times.Length;i++){
                    if(times[i]<=times[i-1]||positions[i]<positions[i-1]||double.IsNaN(times[i])||double.IsNaN(positions[i]))throw new InvalidOperationException("Non-monotone or invalid speech map.");
                    if(cueSeconds>=times[i-1])u=positions[i-1]+(positions[i]-positions[i-1])*SkinNormalMath.Clamp01((cueSeconds-times[i-1])/(times[i]-times[i-1]));
                }
            }
            EvaluateNormalized((float)u);
        }
        // All transitions, numeric stages and mesh animation share the same
        // remapped progress; no branch silently continues on a uniform clock.
        float Phase(float u,int index,int count){return Mathf.Clamp01(u*count-index);}
        public void EvaluateNormalized(float u){
            if(!built)throw new InvalidOperationException("Build first.");u=Mathf.Clamp01(u);ResetPools();term.text=shot.expandedTerm?shot.englishTerm+"\n"+shot.koreanTerm+"\n"+shot.meaning:shot.englishTerm+" · "+shot.koreanTerm;
            sourceKind.text="현재 화면\n우리 구현 · Unity";int b=shot.beatIndex;if(b==0)throw new InvalidOperationException("M22 abstract requires independent gameplay in the parent timeline, not this explanation module.");
            if(shot.useObservedClip){float end=Mathf.Min(shot.clipOut,rig.ClipLength(shot.clip));rig.Sample(shot.clip,Mathf.Lerp(shot.clipIn,end,u));}else if(b<=14||b==35){
                // Bend across the observer's image plane. The imported bone's
                // local forward axis points along the limb and mainly twists it.
                Transform elbow=rig.Bone("lowerarm.l");
                Vector3 axis=elbow.InverseTransformDirection(-stageCamera.transform.forward);
                rig.RotateLocalBone("lowerarm.l",axis,Mathf.Lerp(shot.bendFrom,shot.bendTo,u));
            }
            if(b<=14)ApplySkinning(b,u);else ApplyNormals(b,u);
            foreach(var r in hero.GetComponentsInChildren<Renderer>(true)){var block=new MaterialPropertyBlock();block.SetColor("_BaseColor",Color.white*(b==6?.65f:code.text.Length>0?.12f:1));r.SetPropertyBlock(block);}
            FinishPools();
        }
        Mesh BuildSleeve(){const int rings=25,sides=16;var m=Own(new Mesh{name="TwoBoneSleeve_KnownWeights"});armBind=new Vector3[rings*sides];armWeights=new float[armBind.Length];var uv=new Vector2[armBind.Length];var colors=new Color[armBind.Length];var indices=new List<int>();
            for(int r=0;r<rings;r++){float x=Mathf.Lerp(-1.8f,1.8f,r/(float)(rings-1));float radius=Mathf.Lerp(.35f,.24f,r/(float)(rings-1));float w=Mathf.SmoothStep(0,1,Mathf.InverseLerp(-.6f,.6f,x));for(int j=0;j<sides;j++){int i=r*sides+j;float a=j*Mathf.PI*2/sides;armBind[i]=new Vector3(x,Mathf.Cos(a)*radius,Mathf.Sin(a)*radius);armWeights[i]=w;uv[i]=new Vector2(r/(float)(rings-1),j/(float)sides);colors[i]=Color.Lerp(Blue,Green,w);if(r<rings-1){int k=(j+1)%sides;indices.AddRange(new[]{i,r*sides+k,(r+1)*sides+j,r*sides+k,(r+1)*sides+k,(r+1)*sides+j});}}}
            m.vertices=armBind;m.uv=uv;m.colors=colors;m.triangles=indices.ToArray();m.RecalculateNormals();m.RecalculateTangents();m.RecalculateBounds();return m;
        }
        void DeformSleeve(float degrees,bool rigid=false,bool twist=false){var vertices=new Vector3[armBind.Length];Quaternion q=Quaternion.AngleAxis(degrees,twist?Vector3.right:Vector3.forward);for(int i=0;i<vertices.Length;i++){float w=rigid?(armWeights[i]>=.5f?1:0):armWeights[i];vertices[i]=Vector3.Lerp(armBind[i],q*armBind[i],w);}armMesh.vertices=vertices;armMesh.RecalculateNormals();armMesh.RecalculateTangents();armMesh.RecalculateBounds();}
        Mesh BuildPatch(){var m=Own(new Mesh{name="ArmorPatch_FixedFourVertices"});m.vertices=new[]{new Vector3(-1.65f,-1.55f,0),new Vector3(1.65f,-1.55f,0),new Vector3(-1.65f,1.55f,0),new Vector3(1.65f,1.55f,0)};m.uv=new[]{Vector2.zero,Vector2.right,Vector2.up,Vector2.one};m.triangles=new[]{0,2,1,2,3,1};m.normals=new[]{Vector3.back,Vector3.back,Vector3.back,Vector3.back};m.tangents=new[]{new Vector4(1,0,0,-1),new Vector4(1,0,0,-1),new Vector4(1,0,0,-1),new Vector4(1,0,0,-1)};return m;}
        void ActualBoneGizmos(bool probe){
            string[] chain={"chest","upperarm.l","lowerarm.l","wrist.l","hand.l"};for(int i=0;i<chain.Length-1;i++){Transform a=rig.Bone(chain[i]),b=rig.Bone(chain[i+1]);Path(i==1?Blue:Green,a.position,b.position);Dot(a.position,Yellow,.075f);if(i==2){Arrow(a.position,a.position+a.right*.4f,Red);Arrow(a.position,a.position+a.up*.4f,Green);}}
            if(probe){lastProbe=rig.Probe(false);Dot(lastProbe.weightedWorld,Teal,.13f);for(int i=0;i<lastProbe.weights.Length;i++){Path(Muted,lastProbe.proposalsWorld[i],lastProbe.weightedWorld);Dot(lastProbe.proposalsWorld[i],i==0?Blue:Green,.07f);}Tag(lastProbe.weightedWorld,"실제 메시 정점",Teal,new Vector2(-390,-90));}
        }
        string N(double x,string format="0.###")=>x.ToString(format,System.Globalization.CultureInfo.InvariantCulture);
        string C(string text,Color color)=>"<color=#"+Hex(color)+">"+text+"</color>";
        void ApplySkinning(int b,float u){
            armGroup.SetActive(true);float angle=Mathf.Lerp(shot.bendFrom,shot.bendTo,u);DeformSleeve(angle,b==1&&u<.5f,b==13);if(b==1){hero.transform.position=heroRest+Vector3.right*(Phase(u,0,2)*.6f);if(u<.5f)rig.Restore();}if(b==9)rig.Restore();if(b!=6&&b!=7&&b!=12)ActualBoneGizmos(b>=3&&b<=8);
            objectLabel.text=b>=4&&b<=7?"기사의 실제 정점 ↔ 수치 실험 팔":"같은 본 계층 · 굽힘 "+N(angle,"0")+"°";
            if(b==1){hero.transform.position=heroRest+Vector3.right*(Phase(u,0,2)*.6f);if(u<.5f)rig.Restore();readout.text=u<.5f?"전체 행렬 하나: 조각상처럼 이동":"관절 계층: 아래팔만 굽힘";explanation.text="단단한 부품과 부드러운 연결을 비교합니다.";}
            else if(b==2){readout.text="본 = 위치와 방향을 가진 좌표계";explanation.text=u<.7f?"본의 축을 옮기면 연결된 정점도 따라갑니다.":"표식을 숨겨도 같은 메시 변형은 계속됩니다.";if(u>.7f){lineCursor=dotCursor=tagCursor=0;} }
            else if(b==3){armMaterial.SetFloat("_WeightTint",1);readout.text="파랑: 위팔 가중치     초록: 아래팔 가중치";explanation.text="보이는 색은 이 설명용 팔에 지정한 가중치입니다.";}
            else if(b==4||b==5||b==6||b==7){armGroup.SetActive(false);Vec a=new Vec(0,2),d=new Vec(2,0);double lower=b==5?.4+.4*Phase(u,1,2):.4;Vec p=SkinNormalMath.Blend(new[]{a,d},new[]{1-lower,lower});Path(Muted,At(a),At(d));Dot(At(a),Blue);Tag(At(a),"위팔 (0, 2)",Blue,new Vector2(-210,-65));if(Phase(u,1,3)>0||b!=4){Dot(At(d),Green);Tag(At(d),"아래팔 (2, 0)",Green,new Vector2(12,-45));}if(Phase(u,2,3)>0||b!=4){Dot(At(p),Teal,.16f);Tag(At(p),"결과 "+N(p.x)+", "+N(p.y),Teal,new Vector2(-240,-65));}
                readout.text=N(1-lower)+" × (0, 2) + "+N(lower)+" × (2, 0) = ("+N(p.x)+", "+N(p.y)+")";explanation.text="회전각을 섞는 것이 아니라 옮긴 위치를 섞습니다.";
                if(b==6){hero.transform.position=heroRest+Vector3.right*2.4f;hero.transform.localScale=heroScale*.7f;code.text=C("boneIndex",Teal)+" = [위팔, 아래팔]\n"+C("boneWeight",Teal)+" = [0.6, 0.4]\n"+C("sum",Blue)+" = "+C("1.0",Yellow)+"\n\n4개 제한: 구현 설정";}
                if(b==7){int step=Mathf.Min(3,(int)(u*4));string[] rows={"result = 0","for each bone:","  p = matrix × bindPoint","  result += weight × p"};for(int i=0;i<rows.Length;i++)code.text+=(i==step?"▶ ":"   ")+C(rows[i],i==step?Yellow:i==1?Blue:White)+"\n";}
            }
            else if(b==8){Vec n=new Vec(1,1,0).Unit();Affine m=Affine.Identity;m.x=new Vec(2,0,0);Vec wrong=m.Direction(n).Unit(),correct=m.Normal(n);var o=At(new Vec());Arrow(o,o+U(wrong)*1.8f,Red);Arrow(o,o+U(correct)*1.8f,Green);readout.text="비균일 확대: 잘못된 방향 "+wrong+" → 법선 "+correct;explanation.text="방향에는 평행이동 0 · 비균일 확대에는 역전치";}
            else if(b==9){rig.Restore();DeformSleeve(0);readout.text="Bind Pose · 연결 당시의 기준 자세";explanation.text="현재 자세도 매번 이 기준에서 다시 계산합니다.";}
            else if(b==10||b==11){armGroup.SetActive(false);float q=Phase(u,1,2);Vector3 origin=At(new Vec(-1,0));Path(Muted,origin,At(new Vec(4,0)));Vec bind=new Vec(2,0),local=new Vec(1,0),current=new Vec(3,0);Dot(At(bind),Blue);Dot(At(new Vec(1,0)),Yellow);Dot(At(new Vec(3,0)),Green);Vec visible=u<.5?bind*(1-Phase(u,0,2))+local*Phase(u,0,2):local+current*q;Dot(At(visible),Teal,.16f);Tag(At(visible),"정점 "+N(visible.x),Teal,new Vector2(-75,-65));readout.text="모델 2 − 바인드 원점 1 = 본 좌표 1 → 현재 원점 3 + 1 = 4";explanation.text="p현재 = J현재 × B바인드⁻¹ × p바인드";}
            else if(b==12){code.text=C("M[j]",Teal)+" = J[j] × inverse(B[j])\n\n"+C("blended",Blue)+" = Σ weight[j] × M[j]\n\n"+C("pCurrent",Green)+" = blended × pBind";readout.text="정점 위치는 1벌 · 본 변환은 미리 결합";explanation.text="본마다 위치를 따로 저장하던 중복을 줄입니다.";}
            else if(b==13){objectLabel.text="같은 팔 · 비틀기 "+N(180*u,"0")+"°";DeformSleeve(180*u,false,true);double radius=Math.Abs(Math.Cos(Math.PI*u/2));readout.text="0°와 "+N(180*u,"0")+"° · w=0.5인 중앙의 반지름 비율 = "+N(radius);explanation.text="행렬의 선형 혼합은 항상 순수 회전이 되지는 않습니다.";}
            else if(b==14){DeformSleeve(135*u);readout.text="큰 굽힘에서 가중치와 형태를 함께 확인";explanation.text="이제 같은 형태의 표면 방향으로 작은 요철을 만듭니다.";}
        }
        void PatchBoundary(){var t=plateGroup.transform;Path(Muted,t.TransformPoint(new Vector3(-1.65f,-1.55f,-.015f)),t.TransformPoint(new Vector3(1.65f,-1.55f,-.015f)),t.TransformPoint(new Vector3(1.65f,1.55f,-.015f)),t.TransformPoint(new Vector3(-1.65f,1.55f,-.015f)),t.TransformPoint(new Vector3(-1.65f,-1.55f,-.015f)));}
        void SetPatchUV(bool mirror){plateMesh.uv=mirror?new[]{Vector2.right,Vector2.zero,Vector2.one,Vector2.up}:new[]{Vector2.zero,Vector2.right,Vector2.up,Vector2.one};Vector4 t=mirror?new Vector4(-1,0,0,1):new Vector4(1,0,0,-1);plateMesh.tangents=new[]{t,t,t,t};}
        void PatchFrame(float turn,Vec tangentNormal,bool mirror=false){surface.SetTexture("_NormalRGB",constantNormalData);plateGroup.transform.rotation=Quaternion.Euler(0,turn,0);Transform t=plateGroup.transform;Vector3 p=t.position+t.forward*-.05f;Vector3 tangent=t.right*(mirror?-1:1);Axes(p,tangent,t.up,-t.forward);Vector3 result=tangent*(float)tangentNormal.x+t.up*(float)tangentNormal.y-t.forward*(float)tangentNormal.z;Arrow(p,p+result*1.35f,Yellow);Path(Yellow,p+result*1.35f,p+result*1.35f+new Vector3(3,1,0));Tag(p+result*1.35f,"복원한 법선",Yellow,new Vector2(330,-150));exportedTargets=new[]{p,p+result*1.35f};}
        void ApplyNormals(int b,float u){
            plateGroup.SetActive(true);var light=new Vector3(Mathf.Lerp(-.8f,.8f,u),.45f,-1).normalized;surface.SetVector("_LightDirectionWS",light);PatchBoundary();objectLabel.text="같은 갑옷 표면 · 고정된 외곽선";Vec decoded=SkinNormalMath.Decode8(37,128,218);if(b==20)surface.SetTexture("_NormalRGB",constantNormalData);
            if(b==15){surface.SetFloat("_UseNormal",Phase(u,1,2));readout.text=u<.5f?"높이 변화 → 기울기 → 법선":"노멀 맵 → 표면 법선 → 조명";explanation.text="4개 정점과 외곽선은 그대로 유지됩니다.";HeightDiagram(u);}
            else if(b==16||b==17||b==20){surface.SetFloat("_ShowData",1);var raw=SkinNormalMath.Decode8(37,128,218,false);readout.text=b==20?"RGB (37, 128, 218) → "+raw:"저장: c = 0.5n + 0.5     복원: n = 2c − 1";explanation.text=b==20?"정규화 → ("+N(decoded.x,"0.000000")+", "+N(decoded.y,"0.000000")+", "+N(decoded.z,"0.000000")+")":b==17?"선형 데이터 · 색 보정 대신 방향을 복원하고 정규화":"평평한 법선 (0, 0, 1) → 색 (0.5, 0.5, 1)";if(b==17){sourceKind.text="현재 화면\n해설용 베이크 흐름";int phase=u<.5f?-1:Mathf.Min(2,(int)((u-.5f)*6));plateGroup.GetComponent<MeshFilter>().sharedMesh=phase==0?highPatchMesh:plateMesh;surface.SetFloat("_ShowData",phase==-1||phase==1?1:0);surface.SetFloat("_UseNormal",phase==0?0:1);readout.text=phase==-1?"색 보정 없이 방향 복원 → 정규화":phase==0?"고밀도 표면의 방향":phase==1?"방향을 담은 텍스처":"저밀도 표면에 방향 데이터 적용";code.text=C("Linear data",Green)+"\nDecode XYZ\nNormalize\nTBN → Lighting";}}
            else if(b==18){plateGroup.SetActive(false);ReuseFaces(u);}
            else if(b==19||b==21||b==24){bool mirror=b==24&&u>=.5f;SetPatchUV(mirror);PatchFrame(b==21?Mathf.Lerp(0,65,u):35,decoded,mirror);readout.text=b==24?"B = h × (N × T),   h = "+(mirror?"+1":"−1")+" (현재 표면 축)":"n모델 = xT + yB + zN";explanation.text=b==21?"마이너스 x는 화면 왼쪽이 아니라 표면의 −u 방향":b==24?"UV를 거울 대칭하면 접선과 방향 부호가 함께 바뀝니다.":"T: +u 방향 · B: +v 방향 · N: 표면 바깥";}
            else if(b==22){plateGroup.transform.rotation=Quaternion.Euler(0,Mathf.Lerp(-25,25,u),0);FrameVariation(u);readout.text="곡면과 UV 배치에 따라 기저가 달라집니다.";explanation.text="보간 뒤 정규화 · 필요한 경우 직교화";}
            else if(b==23){SpaceComparison(u);}
            else if(b>=25&&b<=33){ApplyTriangle(b,u);}
            else if(b==34){PatchFrame(25,decoded);int step=Mathf.Min(3,(int)(u*4));string[] rows={"UV · 접선 · 부호 검증","노멀 데이터 읽기","TBN으로 같은 공간에 맞추기","빛과 내적해 표면 표시"};for(int i=0;i<4;i++)code.text+=(i==step?"▶ ":"   ")+C(rows[i],i==step?Yellow:White)+"\n\n";readout.text="제작 도구와 런타임의 좌표 약속을 일치시킵니다.";}
            else if(b==35){ActualBoneGizmos(false);PatchFrame(25,decoded);readout.text="큰 움직임: 본 좌표계     작은 요철: 표면 좌표계";explanation.text="위치와 방향을 같은 약속으로 옮깁니다.";}
        }
        void HeightDiagram(float u){Vector3 o=new Vector3(.5f,3.6f,-.15f);var pts=new Vector3[61];for(int i=0;i<pts.Length;i++){double x=i/(double)(pts.Length-1);pts[i]=o+new Vector3((float)x*3,(float)SkinNormalMath.Height(x,.25)*9,0);}Path(Yellow,pts);double s=u;var n=SkinNormalMath.HeightNormal(s,.25);Vector3 p=o+new Vector3((float)s*3,(float)SkinNormalMath.Height(s,.25)*9,0);Arrow(p,p+new Vector3((float)n.x,(float)n.z,0)*.55f,Blue);Tag(o,"높이 단면 · 해설 그림",Yellow,new Vector2(0,-130));}
        void ReuseFaces(float u){Vector3 top=new Vector3(1.5f,2.5f,0),bottom=new Vector3(1.5f,.1f,0);Path(Muted,top+Vector3.left,top+Vector3.right);Path(Muted,bottom+Vector3.left,bottom+Vector3.right);Arrow(top,top+Vector3.up,Blue);Arrow(bottom,bottom+(u<.5f?Vector3.up:Vector3.down),u<.5f?Red:Green);Tag(top,"윗면",White,new Vector2(-120,0));Tag(bottom,"아랫면",White,new Vector2(-120,0));readout.text=u<.5f?"같은 RGB를 물체 공간으로 해석 → 두 법선이 같은 방향":"각 면의 TBN으로 해석 → 각자 바깥쪽";explanation.text="같은 텍스처를 쓰더라도 표면의 기준축은 다릅니다.";}
        void FrameVariation(float u){Vector3 o=new Vector3(.5f,3.5f,0);for(int i=0;i<4;i++){float a=Mathf.Lerp(-35,35,i/3f)*Mathf.Deg2Rad;Vector3 p=o+new Vector3(i*.9f,-.4f*Mathf.Cos(a),0);Vector3 n=new Vector3(Mathf.Sin(a),Mathf.Cos(a),0);Arrow(p,p+n*.7f,Blue);Arrow(p,p+new Vector3(n.y,-n.x,0)*.65f,Teal);}Vector3 q=new Vector3(2,.2f,-.1f);Arrow(q,q+Vector3.right,Teal);Arrow(q,q+new Vector3(.8f*u,1,0),Green);Tag(q,"UV 기저는 비스듬할 수 있음",White,new Vector2(150,-100));}
        void SpaceComparison(float u){var n=new Vec(0,0,1);var t=new Vec(1,0,0);var b=new Vec(.65*u,1,0);Affine frame=new Affine(t,b,n,new Vec());Vec v=new Vec(1,1,1);Vec exact=frame.Inverse().Direction(v),transpose=new Vec(Vec.Dot(t,v),Vec.Dot(b,v),Vec.Dot(n,v));PatchFrame(0,decodedForSpace());readout.text="기저 역변환 "+exact+"   /   전치 "+transpose;explanation.text=u<.05f?"정규직교 기저에서는 역행렬 = 전치행렬":"기저가 비스듬하면 전치는 역변환이 아닙니다.";}
        Vec decodedForSpace()=>SkinNormalMath.Decode8(37,128,218);
        void ApplyTriangle(int b,float u){
            plateGroup.SetActive(false);Vector3 o=new Vector3(.3f,.4f,-.1f);Vec q1=new Vec(2,0),q2=new Vec(0,1);double s1=b==29?-1:1,t2=b==30?1-u:1;var sol=SkinNormalMath.Solve(q1,q2,s1,0,0,t2);Path(Muted,o,o+U(q1),o+U(q2),o);Dot(o,White);Arrow(o,o+U(q1),Blue);Arrow(o,o+U(q2),Green);
            Tag(o,"p0",White,new Vector2(-80,5));Tag(o+U(q1),"p1 · q1=(2,0,0)",Blue,new Vector2(-160,30));Tag(o+U(q2),"p2 · q2=(0,1,0)",Green,new Vector2(-90,-75));
            Vector3 uvOrigin=new Vector3(4.1f,.5f,-.1f);Vector3 uv1=uvOrigin+new Vector3((float)s1,0,0),uv2=uvOrigin+new Vector3(0,(float)t2,0);Path(Yellow,uvOrigin,uv1,uv2,uvOrigin);Tag(uvOrigin,"UV 삼각형",Yellow,new Vector2(30,-130));
            readout.text="D = s1×t2 − s2×t1 = "+N(sol.determinant);explanation.text=sol.valid?"T = "+sol.tangent+"     B = "+sol.bitangent:"D = 0: 나누기 전에 멈추고 UV를 수정합니다.";
            if(b==25)code.text="q1 = p1 − p0\nq2 = p2 − p0\n\n(s1,t1) = uv1 − uv0\n(s2,t2) = uv2 − uv0";
            else if(b==26){code.text="q1 = s1 T + t1 B\nq2 = s2 T + t2 B";if(sol.valid){Arrow(o,o+U(sol.tangent)*(float)(s1*Phase(u,0,2)),Teal);Arrow(o,o+U(sol.bitangent)*(float)(t2*Phase(u,1,2)),Green);}}
            else if(b==27||b==28||b==29){code.text="T = (t2 q1 − t1 q2) / D\n\nB = (−s2 q1 + s1 q2) / D";if(sol.valid){Arrow(o,o+U(sol.tangent.Unit()),Teal);Arrow(o,o+U(sol.bitangent.Unit()),Green);}if(b==29)explanation.text="D의 음수 부호가 T 방향을 바꿉니다. 정규화로 없어지지 않습니다.";}
            else if(b==30){code.text=C("if",Blue)+" abs(D) ≤ epsilon:\n  "+C("invalid UV",Red)+"\n\n역행렬 계산 금지";}
            else if(b==31){Vec a=new Vec(1,0),d=new Vec(.7,.3);Arrow(o,o+U(a),Teal);Arrow(o+U(a),o+U(a)+U(d)*Phase(u,1,2),Green);readout.text="면마다 구한 T와 B를 인접 정점에 누적";explanation.text="입력 법선 N은 별도로 두고 다음 단계에서 사용합니다.";}
            else if(b==32){Vec n=new Vec(0,1,0),raw=new Vec(1,.8,0),projection=n*Vec.Dot(n,raw),remaining=raw-projection;Arrow(o,o+U(raw),Red);Arrow(o+U(remaining),o+U(raw),Blue);Arrow(o,o+U(remaining),Teal);code.text="T' = normalize(T − N·dot(N,T))\n\nh = sign(dot(cross(N,T'), B))";readout.text="원래 T "+raw+" − N방향 성분 "+projection+" = "+remaining;explanation.text="N에 수직인 T와 방향 부호를 저장합니다.";}
            else if(b==33){Vector3 seam=new Vector3(2,2.4f,-.1f);Dot(seam,Yellow,.13f);Arrow(seam,seam+Vector3.left,Teal);Arrow(seam,seam+Vector3.right,Green);if(u>.5f){Dot(seam+Vector3.left*.18f,Teal);Dot(seam+Vector3.right*.18f,Green);}readout.text=u<.5f?"서로 반대인 접선: (1,0,0) + (−1,0,0) = 0":"같은 위치의 정점을 분리해 양쪽 기저 보존";explanation.text="이음선 양쪽에서 서로 다른 tangent.w와 접선을 유지합니다.";}
        }
        Mesh BuildHighPatch(){const int cells=48;var vertices=new Vector3[(cells+1)*(cells+1)];var uv=new Vector2[vertices.Length];var indices=new List<int>();for(int y=0;y<=cells;y++)for(int x=0;x<=cells;x++){int i=y*(cells+1)+x;double u=x/(double)cells,v=y/(double)cells;vertices[i]=new Vector3((float)(u*3.3-1.65),(float)(v*3.1-1.55),(float)(-SkinNormalMath.Height(u,v)*3.3));uv[i]=new Vector2((float)u,(float)v);if(x<cells&&y<cells){int j=i+cells+1;indices.AddRange(new[]{i,j,i+1,j,j+1,i+1});}}var m=Own(new Mesh{name="OwnAnalyticHighSurface_Illustration"});m.vertices=vertices;m.uv=uv;m.triangles=indices.ToArray();m.RecalculateNormals();m.RecalculateTangents();m.RecalculateBounds();return m;}
        public void DisposeGenerated(){if(rig!=null)rig.Dispose();for(int i=owned.Count-1;i>=0;i--)if(owned[i]!=null)DestroyImmediate(owned[i]);owned.Clear();built=false;}
    }
}
