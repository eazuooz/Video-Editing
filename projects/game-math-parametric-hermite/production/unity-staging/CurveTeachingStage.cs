using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.MathCurves {
    [Serializable] public class CurveShot {
        public string beatId="UNBOUND",episodeId="M31",mode="Bezier",animation="Travel",basis="Bernstein";
        public string englishTerm="Parametric curve",koreanTerm="매개변수 곡선",meaning="진행도 하나로 경로 위 위치를 구합니다";
        public string[] steps=new string[0];
        public string code="";
        public CVec[] controls=new[]{new CVec(0,0),new CVec(1,2),new CVec(3,2),new CVec(4,0)};
        public CVec[] coefficients=new[]{new CVec(0,0),new CVec(0,3),new CVec(6,-3),new CVec(-4,0)};
        public CVec[] knots=new[]{new CVec(0,0),new CVec(1,2),new CVec(3,-1),new CVec(5,1)};
        public double[] parameterNodes=new[]{0.0,1.0/3,2.0/3,1.0};
        public CVec[] interpolationPoints=new[]{new CVec(0,2),new CVec(1,3),new CVec(2,2),new CVec(3,3)};
        public double radius=1,splitAt=.5,extractA=.2,extractB=.5,tension=0,continuity=0,bias=0;
        public double leftDuration=1,rightDuration=1;
        public double domainMin=0,domainMax=1,displayT=.5;
        public bool useTravelInterval=false;
        public double travelFrom,travelTo=1;
        public float modelScale=1.25f;
        public Vector3 worldOffset=new Vector3(-7,-1,0);
        public bool tangent=true,acceleration=false,triangle=false,basisGraph=false,equalTimeMarkers=false,codeVisible=false;
        public bool termExpanded=true,stopAtEnds=false,parameterFixed=false;
        public bool showDerivative=false,showCurvature=false,convexHull=false;
        public string endpointRule="linear"; public double[] blossomParameters=new[]{.2,.2,.5};
        public float arrowScale=.23f;
        public Vector3 modelEuler=Vector3.zero;
        public int stepIndex=0;
        public string sourceParagraphs="",screenIntent="";
    }
    // A pedagogical curve is the object itself. No game character or asset is replaced by a cube.
    // There is no Update, playback loop, wall clock, screenshot/write or Unity launch here.
    public sealed partial class CurveTeachingStage:MonoBehaviour {
        public CurveShot shot=new CurveShot();
        public Camera stageCamera;
        public Material sharedLineMaterial;
        public Font koreanFont;
        [SerializeField] bool built;
        [SerializeField] Canvas canvas;
        [SerializeField] Text term,sourceKind,stepText,values,basisCaption,axisCaption;
        [SerializeField] List<LineRenderer> lines=new List<LineRenderer>();
        [SerializeField] List<Text> pointLabels=new List<Text>();
        int lineCursor,labelCursor;
        static readonly Color White=new Color(.961f,.961f,.961f),Yellow=new Color(.910f,.812f,.514f),Teal=new Color(.451f,.780f,.761f),Red=new Color(.937f,.522f,.522f),Green=new Color(.643f,.776f,.627f),Muted=new Color(.722f,.722f,.722f),Violet=new Color(.765f,.667f,.859f);
        static readonly Color[] Roles={Yellow,Teal,Green,Violet};
        public void Build(){
            if(built&&canvas!=null){EnsureFont();return;}
            if(stageCamera==null){var go=Own("CurveLabCamera");stageCamera=go.AddComponent<Camera>();stageCamera.transform.position=new Vector3(0,2,-20);stageCamera.transform.rotation=Quaternion.identity;stageCamera.orthographic=true;stageCamera.orthographicSize=5.625f;stageCamera.nearClipPlane=.1f;stageCamera.farClipPlane=80;stageCamera.clearFlags=CameraClearFlags.SolidColor;stageCamera.backgroundColor=Color.black;}
            if(sharedLineMaterial==null){var shader=Shader.Find("Universal Render Pipeline/Unlit")??Shader.Find("Unlit/Color");if(shader==null)throw new InvalidOperationException("Explicit compatible unlit shader required.");sharedLineMaterial=new Material(shader){name="YamyamCurvesUnlit"};}
            if(koreanFont==null)koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",44);
            var ui=Own("CurveLabLabels");canvas=ui.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=stageCamera;canvas.planeDistance=1;
            var scaler=ui.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);
            term=Label("CanonicalTerm",new Rect(88,45,1000,150),40,Yellow);
            sourceKind=Label("PictureKind",new Rect(1230,55,600,95),32,Muted);
            axisCaption=Label("ModelCoordinates",new Rect(90,200,930,70),30,Muted);
            stepText=Label("WorkedStep",new Rect(1090,245,740,430),36,White);stepText.supportRichText=true;
            values=Label("ActualModelValues",new Rect(90,755,930,135),34,White);
            basisCaption=Label("BasisLabels",new Rect(1090,680,740,190),30,White);
            built=true;
        }
        void EnsureFont(){if(koreanFont==null)koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",44);if(canvas!=null)foreach(var label in canvas.GetComponentsInChildren<Text>(true))label.font=koreanFont;}
        GameObject Own(string name){var go=new GameObject(name);go.transform.SetParent(transform,false);return go;}
        Text Label(string name,Rect r,int size,Color color){var go=new GameObject(name);go.transform.SetParent(canvas.transform,false);var rt=go.AddComponent<RectTransform>();rt.anchorMin=rt.anchorMax=new Vector2(0,1);rt.pivot=new Vector2(0,1);rt.anchoredPosition=new Vector2(r.x,-r.y);rt.sizeDelta=new Vector2(r.width,r.height);var t=go.AddComponent<Text>();t.font=koreanFont;t.fontSize=size;t.color=color;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;t.supportRichText=false;return t;}
        public static Vector3 ToUnity(CVec v)=>new Vector3((float)v.x,(float)v.y,(float)-v.z);
        Vector3 W(CVec p)=>shot.worldOffset+Quaternion.Euler(shot.modelEuler)*ToUnity(p)*shot.modelScale;
        LineRenderer GetLine(Color color,float width){LineRenderer l;if(lineCursor<lines.Count)l=lines[lineCursor];else{l=Own("CurveGuide_"+lines.Count).AddComponent<LineRenderer>();l.useWorldSpace=true;l.numCapVertices=4;l.numCornerVertices=4;lines.Add(l);}lineCursor++;l.gameObject.SetActive(true);l.sharedMaterial=sharedLineMaterial;l.startWidth=l.endWidth=width;l.startColor=l.endColor=Color.white;l.alignment=LineAlignment.View;var block=new MaterialPropertyBlock();block.SetColor("_Color",color);block.SetColor("_BaseColor",color);l.SetPropertyBlock(block);return l;}
        void Poly(IList<Vector3> p,Color color,float width=.028f){if(p.Count<2)return;var l=GetLine(color,width);l.positionCount=p.Count;for(int i=0;i<p.Count;i++)l.SetPosition(i,p[i]);}
        void Curve(Func<double,CVec> evaluate,Color color,float width=.04f){var p=new List<Vector3>();for(int i=0;i<=160;i++){double t=shot.domainMin+(shot.domainMax-shot.domainMin)*i/160.0;p.Add(W(evaluate(t)));}Poly(p,color,width);}
        void Arrow(CVec from,CVec vector,Color color,float scale=.23f){var a=W(from);var delta=Quaternion.Euler(shot.modelEuler)*ToUnity(vector)*scale;if(delta.sqrMagnitude<1e-10)return;var end=a+delta;var d=delta.normalized;var s=Vector3.Cross(d,stageCamera.transform.forward);if(s.sqrMagnitude<1e-8)s=stageCamera.transform.right;s.Normalize();float h=Mathf.Min(.19f,delta.magnitude*.3f);Poly(new[]{a,end},color,.05f);Poly(new[]{end-d*h+s*h*.5f,end,end-d*h-s*h*.5f},color,.05f);}
        void Dot(CVec p,Color color,string text="",float radius=.07f){Vector3 center=W(p);var ring=new Vector3[25];for(int i=0;i<ring.Length;i++){double a=i*2*Math.PI/(ring.Length-1);ring[i]=center+stageCamera.transform.right*(float)(radius*Math.Cos(a))+stageCamera.transform.up*(float)(radius*Math.Sin(a));}Poly(ring,color,.035f);if(text.Length>0)PointLabel(center,text,color);}
        void PointLabel(Vector3 point,string text,Color color){Vector3 v=stageCamera.WorldToViewportPoint(point);float x=v.x*1920,y=(1-v.y)*1080;if(v.z<=0||x<70||x>940||y<275||y>700)return;Text label;if(labelCursor<pointLabels.Count)label=pointLabels[labelCursor];else{label=Label("ObjectLabel_"+pointLabels.Count,new Rect(0,0,320,50),30,color);pointLabels.Add(label);}labelCursor++;label.gameObject.SetActive(true);label.color=color;label.text=text;label.rectTransform.anchoredPosition=new Vector2(x+12,-y-6);}
        void Controls(CVec[] b,string prefix="b"){var p=new List<Vector3>();for(int i=0;i<b.Length;i++){p.Add(W(b[i]));Dot(b[i],Roles[i%Roles.Length],prefix+i);}Poly(p,Muted*.65f,.018f);}
        static string V(CVec p)=>"("+p.x.ToString("0.###")+", "+p.y.ToString("0.###")+", "+p.z.ToString("0.###")+")";
        static string Number(double x)=>double.IsNaN(x)?"정의되지 않음":x.ToString("0.###");
        double[] Weights(double t){if(shot.basis=="Hermite")return CurveMathModel.HermiteWeights(t);if(shot.basis=="Lagrange")return CurveMathModel.LagrangeWeights(shot.parameterNodes,t);return CurveMathModel.Bernstein(shot.controls.Length-1,t);}
        void BasisPlot(double current){
            const float x0=1.7f,y0=.1f,ww=6.5f,hh=1.2f;int n=Weights(.5).Length;
            Poly(new[]{new Vector3(x0,y0,-2),new Vector3(x0+ww,y0,-2)},Muted*.5f,.014f);
            var names=new List<string>();var w=Weights(current);
            for(int k=0;k<n;k++){var p=new List<Vector3>();for(int i=0;i<=100;i++){double u=i/100.0,t=shot.domainMin+(shot.domainMax-shot.domainMin)*u;p.Add(new Vector3(x0+(float)u*ww,y0+(float)Weights(t)[k]*hh,-2));}Poly(p,Roles[k%4],.026f);names.Add((shot.basis=="Hermite"?"H":shot.basis=="Lagrange"?"L":"B")+k+" = "+w[k].ToString("0.###"));}
            Poly(new[]{new Vector3(x0+(float)((current-shot.domainMin)/(shot.domainMax-shot.domainMin))*ww,y0-.45f,-2.05f),new Vector3(x0+(float)((current-shot.domainMin)/(shot.domainMax-shot.domainMin))*ww,y0+1.4f,-2.05f)},White*.6f,.014f);
            basisCaption.text=string.Join("    ",names.ToArray());
        }
        CurveSample Render(double t,double phase){
            CVec[] b=(CVec[])shot.controls.Clone();
            if(shot.animation=="HandleY"&&b.Length>1)b[1].y=1+2*phase;
            if(shot.animation=="HandleRotate"&&b.Length>1){double a=(90-60*phase)*Math.PI/180;b[1]=b[0]+new CVec(Math.Cos(a),Math.Sin(a));}
            if(shot.mode=="Pascal"){PascalPicture(phase);return CurveMathModel.BezierSample(b,t);}
            if(shot.mode=="Blossom")return BlossomPicture(b,t);
            if(shot.mode=="Circle"){double r=shot.animation=="Radius"?2-phase:shot.radius;Curve(u=>CurveMathModel.Circle(r,u).p,Yellow);return CurveMathModel.Circle(r,t);}
            if(shot.mode=="Power"){Curve(u=>CurveMathModel.Power(shot.coefficients,u),Yellow);return CurveMathModel.PowerSample(shot.coefficients,t);}
            if(shot.mode=="LineSpeed"){
                Curve(u=>new CVec(4*u,0),Muted);Curve(u=>new CVec(4*u,-1.1),Muted);
                Dot(new CVec(4*t,0),Teal,"같은 t 간격");Dot(new CVec(4*t*t,-1.1),Green,"t²");
                for(int i=0;i<=8;i++){double u=i/8.0;Dot(new CVec(4*u,0),Teal,"",.035f);Dot(new CVec(4*u*u,-1.1),Green,"",.035f);}return CurveMathModel.Sample(new CVec(4*t*t,-1.1),new CVec(8*t,0),new CVec(8,0));
            }
            if(shot.mode=="Smoothstep"){
                Curve(u=>new CVec(4*u,0),Muted);Curve(u=>new CVec(4*u,-1.1),Muted);Dot(new CVec(4*t,0),Teal,"선형");double s=CurveMathModel.Smoothstep(t);Dot(new CVec(4*s,-1.1),Green,"smoothstep");return CurveMathModel.Sample(new CVec(4*s,-1.1),new CVec(t<0||t>1?0:24*t*(1-t),0),new CVec(t<0||t>1?0:24-48*t,0));
            }
            if(shot.mode=="Lagrange"||shot.mode=="Aitken"){
                Curve(u=>CurveMathModel.Lagrange(shot.parameterNodes,shot.interpolationPoints,u),Yellow);
                for(int i=0;i<shot.interpolationPoints.Length;i++)Dot(shot.interpolationPoints[i],Roles[i%4],"p"+i);
                if(shot.mode=="Aitken"&&shot.triangle){var rows=CurveMathModel.Aitken(shot.parameterNodes,shot.interpolationPoints,t);for(int j=1;j<rows.Length;j++){var p=new List<Vector3>();foreach(var at in rows[j]){Dot(at,Roles[j%4],"",.04f);p.Add(W(at));}Poly(p,Roles[j%4],.022f);}}
                // Direction is an explicitly displayed numerical derivative only in interpolation mode.
                double h=1e-5;CVec p0=CurveMathModel.Lagrange(shot.parameterNodes,shot.interpolationPoints,t),pm=CurveMathModel.Lagrange(shot.parameterNodes,shot.interpolationPoints,t-h),pp=CurveMathModel.Lagrange(shot.parameterNodes,shot.interpolationPoints,t+h);
                return CurveMathModel.Sample(p0,(pp-pm)/(2*h),(pp-2*p0+pm)/(h*h));
            }
            if(shot.mode=="Spline"||shot.mode=="TCB"){
                double T=shot.tension,C=shot.continuity,B=shot.bias;
                if(shot.animation=="Tension")T=-2+4*phase;if(shot.animation=="Continuity")C=-1+2*phase;if(shot.animation=="Bias")B=-1+2*phase;
                var pieces=CurveMathModel.TCBPieces(shot.knots,T,C,B,shot.stopAtEnds);
                if(shot.endpointRule=="quadratic"&&shot.knots.Length>=3){var a=pieces[0];a[1]=a[0]+CurveMathModel.QuadraticStart(shot.knots[0],shot.knots[1],shot.knots[2])/3;var z=pieces[pieces.Length-1];int n=shot.knots.Length;z[z.Length-2]=z[z.Length-1]-(-CurveMathModel.QuadraticStart(shot.knots[n-1],shot.knots[n-2],shot.knots[n-3]))/3;}
                for(int i=0;i<pieces.Length;i++){var piece=pieces[i];Curve(u=>CurveMathModel.Bezier(piece,u),Roles[i%4]);}
                for(int i=0;i<shot.knots.Length;i++)Dot(shot.knots[i],White,"k"+i);
                var address=CurveMathModel.Address(t*pieces.Length,pieces.Length);
                basisCaption.text="s = "+(t*pieces.Length).ToString("0.###")+"   구간 i = "+address.index+"   u = "+address.local.ToString("0.###")+"\nT = "+T.ToString("0.##")+"   C = "+C.ToString("0.##")+"   B = "+B.ToString("0.##");
                var local=CurveMathModel.BezierSample(pieces[address.index],address.local);
                return CurveMathModel.Sample(local.p,local.d1*pieces.Length,local.d2*(pieces.Length*pieces.Length));
            }
            if(shot.mode=="Join"){
                CVec[] left={new CVec(0,0),new CVec(1,0),new CVec(1,2),new CVec(2,2)};
                CVec[] right={new CVec(2,2),new CVec(3,2),new CVec(3,0),new CVec(4,0)};
                if(shot.animation=="UnequalHandles")right[1]=new CVec(2.5,2);
                if(shot.animation=="BrokenDirection")right[1]=new CVec(2,3);
                if(shot.animation=="StoppedCorner"){left=CurveMathModel.HermiteBezier(new CVec(0,0),new CVec(),new CVec(),new CVec(2,0));right=CurveMathModel.HermiteBezier(new CVec(2,0),new CVec(),new CVec(),new CVec(2,2));}
                if(shot.animation=="C2Match"){right[2]=2*right[1]-(2*left[2]-left[1]);}
                if(shot.animation=="DifferentBendPlanes"){left=CurveMathModel.PowerBezier(new[]{new CVec(0,.5),new CVec(1,-1),new CVec(0,.5),new CVec()});right=CurveMathModel.PowerBezier(new[]{new CVec(1,0),new CVec(1,0),new CVec(0,0,.5),new CVec()});}
                Curve(u=>CurveMathModel.Bezier(left,u),Teal);Curve(u=>CurveMathModel.Bezier(right,u),Green);Controls(left,"L");Controls(right,"R");
                var j=CurveMathModel.Join(left,right,shot.leftDuration,shot.rightDuration);
                basisCaption.text="위치 차이 "+Number(j.positionGap)+"\n속도 차이 "+Number(j.firstDerivativeGap)+"   가속도 차이 "+Number(j.secondDerivativeGap)+"\nC0 "+j.c0+"   C1 "+j.c1+"   C2 "+j.c2+"   G1 "+j.g1+"   G2 "+j.g2;
                double total=shot.leftDuration+shot.rightDuration,elapsed=t*total;
                bool onLeft=elapsed<=shot.leftDuration;double duration=onLeft?shot.leftDuration:shot.rightDuration;
                double u=onLeft?elapsed/duration:(elapsed-shot.leftDuration)/duration;
                var local=CurveMathModel.BezierSample(onLeft?left:right,u);double scale=total/duration;
                return CurveMathModel.Sample(local.p,local.d1*scale,local.d2*(scale*scale));
            }
            Curve(u=>CurveMathModel.Bezier(b,u),Yellow);Controls(b);if(shot.convexHull)Hull(b);
            if(shot.animation=="BuildCasteljau"){
                var rows=CurveMathModel.Casteljau(b,t);
                double clock=phase*(rows.Length-.2);
                int lastRow=0;
                for(int level=1;level<rows.Length;level++){
                    double fraction=Math.Max(0,Math.Min(1,clock-level+1));
                    if(fraction<=0)break;
                    var polygon=new List<Vector3>();
                    for(int k=0;k<rows[level].Length;k++){
                        CVec from=rows[level-1][k],to=rows[level][k];
                        CVec moving=from+(to-from)*fraction;
                        Poly(new[]{W(from),W(moving)},Roles[level%4],.046f);
                        Dot(moving,Roles[level%4],"",.095f);polygon.Add(W(moving));
                    }
                    Poly(polygon,Roles[level%4],.044f);
                    lastRow=level;
                }
                basisCaption.text=lastRow==rows.Length-1?"마지막 두 점에서 곡선 위의 점을 찾습니다":"이웃한 점끼리 보간 · "+lastRow+"단계";
                if(shot.mode=="Split"&&clock>=rows.Length-1){
                    var pieces=CurveMathModel.Split(b,shot.splitAt);
                    double reveal=Math.Min(1,(clock-rows.Length+1)/.8);
                    for(int i=0;i<2;i++){
                        var part=pieces[i];Color color=i==0?Teal:Green;
                        Curve(u=>CurveMathModel.Bezier(part,i==0?1-u*reveal:u*reveal),color,.08f);
                        Poly(Array.ConvertAll(part,W),color,.042f);
                    }
                    basisCaption.text="두 조각은 같은 분할점 p(t)를 공유합니다";
                }
                return CurveMathModel.BezierSample(b,t);
            }
            if(shot.mode=="Split"){
                var pieces=CurveMathModel.Split(b,shot.splitAt);Curve(u=>CurveMathModel.Bezier(pieces[0],u),Teal,.06f);Curve(u=>CurveMathModel.Bezier(pieces[1],u),Green,.06f);Controls(pieces[0],"L");Controls(pieces[1],"R");
            }else if(shot.mode=="Extract"){
                var extracted=CurveMathModel.Subcurve(b,shot.extractA,shot.extractB);Curve(u=>CurveMathModel.Bezier(extracted,u),Teal,.07f);Controls(extracted,"q");
            }else if(shot.mode=="Elevation"){var elevated=CurveMathModel.Elevate(b);Controls(elevated,"q");Curve(u=>CurveMathModel.Bezier(elevated,u),Teal,.025f);}
            if(shot.triangle){var rows=CurveMathModel.Casteljau(b,t);for(int j=1;j<rows.Length;j++){var points=new List<Vector3>();for(int i=0;i<rows[j].Length;i++){Dot(rows[j][i],Roles[j%4],j==rows.Length-1?"p(t)":"",.055f);points.Add(W(rows[j][i]));}Poly(points,Roles[j%4],.025f);}}
            if(shot.equalTimeMarkers)for(int i=0;i<=10;i++)Dot(CurveMathModel.Bezier(b,i/10.0),White,"",.035f);
            return CurveMathModel.BezierSample(b,t);
        }
        public void Evaluate(double motionProgress,int spokenStep=-1){
            if(motionProgress<0||motionProgress>1||double.IsNaN(motionProgress))throw new ArgumentOutOfRangeException(nameof(motionProgress),"No looping, freeze padding or silent clamping.");
            Build();lineCursor=labelCursor=0;double t=shot.parameterFixed?shot.displayT:
                shot.useTravelInterval?shot.travelFrom+(shot.travelTo-shot.travelFrom)*motionProgress:
                shot.domainMin+(shot.domainMax-shot.domainMin)*motionProgress;
            if(spokenStep>=0)shot.stepIndex=spokenStep;
            if(shot.steps.Length>0&&(shot.stepIndex<0||shot.stepIndex>=shot.steps.Length))throw new ArgumentOutOfRangeException("Spoken formula step has no binding.");
            term.text=shot.termExpanded?shot.englishTerm+"\n"+shot.koreanTerm+"\n"+shot.meaning:shot.englishTerm+" · "+shot.koreanTerm+"\n"+shot.meaning;
            sourceKind.text="현재 화면: 우리 구현\n수학 모형 · 상용 게임 내부 분석 아님";
            axisCaption.text=shot.modelEuler.sqrMagnitude>0?"수학 좌표를 비스듬히 본 3D 모형 · 점 p(t), 화살표 도함수":"해설용 좌표 · x 오른쪽 / y 위 / +z 화면 밖\n점은 p(t), 화살표는 도함수";
            stepText.rectTransform.sizeDelta=new Vector2(740,shot.basisGraph?225:430);
            basisCaption.rectTransform.anchoredPosition=new Vector2(1090,shot.basisGraph?-795:-680);
            basisCaption.rectTransform.sizeDelta=new Vector2(740,shot.basisGraph?95:190);
            stepText.text=shot.codeVisible?shot.code:shot.steps.Length>0?shot.steps[shot.stepIndex]:"";
            basisCaption.text="";var state=Render(t,motionProgress);
            bool forming=shot.animation=="BuildCasteljau"&&motionProgress*(shot.controls.Length-.2)<shot.controls.Length-1;
            if(shot.mode!="Pascal"&&!forming)Dot(state.p,White,shot.mode=="Blossom"?"blossom":"p(t)",.105f);
            if(shot.tangent&&state.regular)Arrow(state.p,state.d1,Teal,shot.arrowScale);
            if(shot.acceleration)Arrow(state.p,state.d2,Red,.12f);
            values.text="t = "+t.ToString("0.000")+"   p = "+V(state.p);
            if(forming)values.text="공통 보간 비율 t = "+t.ToString("0.##");
            if(shot.showDerivative)values.text+="\np′ = "+V(state.d1)+"   |p′| = "+Number(state.d1.Length);
            if(shot.showCurvature)values.text+="\n곡률 κ = "+Number(state.curvature);
            if(shot.showDerivative&&(shot.mode=="Lagrange"||shot.mode=="Aitken"))values.text+="  (도함수: 수치 근사)";
            if(shot.mode=="Pascal")values.text="바깥 1 · 안쪽은 바로 위 두 수의 합";
            if(shot.mode=="Blossom")values.text="보간 결과 = "+V(state.p);
            if(shot.basisGraph)BasisPlot(t);
            for(int i=lineCursor;i<lines.Count;i++)lines[i].gameObject.SetActive(false);
            for(int i=labelCursor;i<pointLabels.Count;i++)pointLabels[i].gameObject.SetActive(false);
        }
    }
}
