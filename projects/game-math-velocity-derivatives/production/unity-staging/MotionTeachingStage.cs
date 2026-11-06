using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.MathMotion {
    [Serializable] public class MotionShot {
        public string beatId="UNBOUND",englishTerm="Velocity",koreanTerm="속도",meaning="위치가 시간에 따라 변하는 비율";
        public MotionParameters parameters=new MotionParameters();
        public double startTime=0,endTime=3,secantH=.5;
        public string timeUnit="min",positionUnit="fur";
        public string inputLabel="시간 t",valueLabel="위치",derivativeLabel="속도",secondDerivativeLabel="가속도";
        public bool scalarFunction=false,showGraphs=true;
        public bool showComparison=false;
        public string subjectKind="";
        public bool fixedSecant=false;
        public double secantStartTime;
        public MotionParameters comparisonParameters=new MotionParameters{kind=MotionKind.ConstantVelocity};
        public string comparisonLabel="";
        public string axisConvention="x 오른쪽 / y 위 / +z 화면 밖 (오른손 도식)";
        public bool positiveYIsDown=false,termExpanded=true;
        public float worldUnitsPerModelUnit=.65f,velocityArrowScale=.3f,accelerationArrowScale=.15f;
        public Vector3 worldOrigin=new Vector3(-6,0,0);
        public Vector3 displayEuler=Vector3.zero;
        public bool showVelocity=true,showAcceleration=false,showRadius=false,showSecant=false,showTangent=false;
        public bool showVelocityGraph=true,showAccelerationGraph=false;
        public bool showRiemann=false;
        public bool riemannFromModel=false;
        public bool riemannMovingEnd=false;
        public double riemannSample=0;
        public int riemannCount=6;
        public double riemannDuration=2.4,riemannAcceleration=32,riemannV0=0;
        public bool graphY=false;
        public double positionMin=-2,positionMax=9,velocityMin=-3,velocityMax=7,accelerationMin=-5,accelerationMax=2;
    }
    // No Update, wall-clock time, looping, physics stepping, rendering or file writes.
    // The parent renderer must call Evaluate with an approved, speech-bound cue time.
    public sealed class MotionTeachingStage:MonoBehaviour {
        public MotionShot shot=new MotionShot();
        public GameObject subjectPrefab;
        public Font koreanFont; // Load from local OS dynamically; never vendor a font file.
        public Camera stageCamera;
        public Transform subjectAnchor;
        Transform comparisonAnimal;
        public bool built;
        readonly List<GameObject> generated=new List<GameObject>();
        readonly List<LineRenderer> lines=new List<LineRenderer>();
        int lineCursor,motionGuideCount;
        float motionFitScale=1;
        double maxVectorSpeed,maxVectorAcceleration;
        Vector3 motionFitOffset;
        Text term,kind,values,details,coordinateLabel,positionTitle,velocityTitle,accelerationTitle,velocityCallout,accelerationCallout,radiusCallout;
        Text timeStart,timeEnd,timeAxis;
        Text formulaBoard,formulaMeaning,comparisonLegend;
        Text hareName,tortoiseName,secantStart,secantFinish,graphMark,triangleBase;
        readonly List<Text> graphRangeLabels=new List<Text>();
        // All graph sizes derive from the fixed 1080p camera, with room for
        // range values, units and the fixed caption below the three plots.
        const float PositionBase=3.7708333f,VelocityBase=1.9479167f,AccelerationBase=.125f,PlotHeight=1.0416667f;
        Canvas canvas;
        Material lineMaterial;
        public Material GuideMaterial=>lineMaterial;
        static readonly Color White=new Color(.961f,.961f,.961f),Yellow=new Color(.910f,.812f,.514f),Teal=new Color(.451f,.780f,.761f),Red=new Color(.937f,.522f,.522f),Green=new Color(.643f,.776f,.627f),Muted=new Color(.722f,.722f,.722f);
        public void Build() {
            if(built)return;
            if(subjectPrefab==null)throw new InvalidOperationException("Assign a rights-verified recognizable prefab. No generic cube or silent substitute is created.");
            if(koreanFont==null)throw new InvalidOperationException("Supply a local dynamic Korean font; do not distribute its original font file.");
            if(stageCamera==null) {
                GameObject c=Own(new GameObject("MotionLabCamera"));stageCamera=c.AddComponent<Camera>();
                stageCamera.transform.position=new Vector3(0,2,-20);stageCamera.transform.rotation=Quaternion.identity;
                stageCamera.orthographic=true;stageCamera.orthographicSize=5.625f;stageCamera.clearFlags=CameraClearFlags.SolidColor;stageCamera.backgroundColor=Color.black;
                stageCamera.nearClipPlane=.1f;stageCamera.farClipPlane=80;
            }
            var shader=Shader.Find("Universal Render Pipeline/Unlit")??Shader.Find("Unlit/Color");
            if(shader==null)throw new InvalidOperationException("No compatible unlit shader; preserve pipeline and supply one explicitly.");
            lineMaterial=new Material(shader){name="YamyamMotionLines"};
            GameObject anchor=Own(new GameObject("TrackedObjectAnchor"));subjectAnchor=anchor.transform;
            if(shot.subjectKind=="hare") {
                var animal=new MotionAnimalSubjects();
                animal.Hare(subjectAnchor);
                if(shot.showComparison) {
                    comparisonAnimal=Own(new GameObject("TortoiseOnParallelTrack")).transform;
                    animal.Tortoise(comparisonAnimal);
                }
            }else {
                var subject=Instantiate(subjectPrefab,subjectAnchor);subject.name="LicensedSubject_Instance";
                subject.transform.localPosition=Vector3.zero;
                Bounds bounds=new Bounds(subject.transform.position,Vector3.zero);bool first=true;
                foreach(var renderer in subject.GetComponentsInChildren<Renderer>()) { if(first){bounds=renderer.bounds;first=false;}else bounds.Encapsulate(renderer.bounds); }
                if(first||bounds.size.magnitude<1e-6f)throw new InvalidOperationException("The selected prefab has no visible renderer bounds.");
                float scale=1.4f/Mathf.Max(bounds.size.x,bounds.size.y,bounds.size.z);subject.transform.localScale*=scale;
                subject.transform.localPosition-=bounds.center*scale;
            }
            var light=Own(new GameObject("MotionLabKey")).AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.3f;light.transform.rotation=Quaternion.Euler(35,-25,0);
            GameObject ui=Own(new GameObject("MotionLabLabels"));canvas=ui.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=stageCamera;canvas.planeDistance=1;
            var scaler=ui.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);
            term=Label("Term",new Rect(88,45,1050,145),40,Yellow);
            kind=Label("SourceKind",new Rect(1200,55,620,100),32,Muted);
            values=Label("ModelValues",new Rect(92,797,945,120),36,White);
            details=Label("LiveCalculation",new Rect(1090,795,750,112),36,White);
            coordinateLabel=Label("CoordinateConvention",new Rect(92,195,930,88),34,Muted);
            positionTitle=Label("GraphPosition",new Rect(1130,225,665,46),36,Yellow);
            velocityTitle=Label("GraphVelocity",new Rect(1130,400,665,46),36,Teal);
            accelerationTitle=Label("GraphAcceleration",new Rect(1130,575,665,46),36,Red);
            for(int row=0;row<3;row++)for(int end=0;end<2;end++)
                graphRangeLabels.Add(Label("GraphRange"+row+"_"+end,new Rect(1020,253+175*row+100*end,102,44),34,Muted));
            timeStart=Label("TimeStart",new Rect(1125,0,150,44),34,Muted);
            timeEnd=Label("TimeEnd",new Rect(1690,0,150,44),34,Muted);
            timeAxis=Label("TimeAxis",new Rect(1350,0,330,44),34,Muted);
            velocityCallout=Label("VelocityArrowLabel",new Rect(0,0,430,48),36,Teal);
            accelerationCallout=Label("AccelerationArrowLabel",new Rect(0,0,430,48),36,Red);
            radiusCallout=Label("RadiusArrowLabel",new Rect(0,0,350,48),36,Yellow);
            graphMark=Label("PointOnGraph",new Rect(0,0,330,54),42,Yellow);
            graphMark.gameObject.SetActive(false);
            if(shot.beatId=="M25-009")triangleBase=Label("TriangleBase",new Rect(0,0,100,50),42,Yellow);
            if(shot.subjectKind=="hare") {
                hareName=Label("HareLabel",new Rect(0,0,130,46),36,Yellow);
                if(comparisonAnimal)tortoiseName=Label("TortoiseLabel",new Rect(0,0,140,46),36,Teal);
                secantStart=Label("FirstSecantTime",new Rect(0,0,96,44),34,Green);
                secantFinish=Label("SecondSecantTime",new Rect(0,0,150,44),34,Green);
            }
            formulaBoard=Label("SpeechBoundCalculation",new Rect(92,290,930,180),38,White);formulaBoard.supportRichText=true;
            formulaMeaning=Label("CalculationMeaning",new Rect(92,475,930,90),34,White);
            comparisonLegend=Label("ComparisonLegend",new Rect(1130,400,720,90),36,White);
            built=true;
        }
        GameObject Own(GameObject go){go.transform.SetParent(transform,false);generated.Add(go);return go;}
        Text Label(string id,Rect pixelRect,int size,Color color) {
            GameObject go=new GameObject(id);go.transform.SetParent(canvas.transform,false);var rt=go.AddComponent<RectTransform>();rt.anchorMin=rt.anchorMax=new Vector2(0,1);rt.pivot=new Vector2(0,1);rt.anchoredPosition=new Vector2(pixelRect.x,-pixelRect.y);rt.sizeDelta=new Vector2(pixelRect.width,pixelRect.height);
            Text t=go.AddComponent<Text>();t.font=koreanFont;t.fontSize=size;t.color=color;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;t.supportRichText=false;return t;
        }
        // Reflection from mathematical RH coordinates to the Unity display's z direction.
        public static Vector3 ToUnity(DVec v)=>new Vector3((float)v.x,(float)v.y,(float)-v.z);
        static Vector3 RawVector(MotionShot s,DVec p){Vector3 v=ToUnity(p);if(s.positiveYIsDown)v.y=-v.y;return Quaternion.Euler(s.displayEuler)*v;}
        Vector3 DisplayVector(DVec p)=>RawVector(shot,p)*motionFitScale;
        Vector3 Position(DVec p)=>(shot.worldOrigin+RawVector(shot,p)*shot.worldUnitsPerModelUnit)*motionFitScale+motionFitOffset;
        public void FitMotionSubjects(IEnumerable<MotionShot> models){
            // One uniform scale for the whole paragraph, including all changed
            // parameters. Formula, moving object and values own separate regions.
            Bounds bounds=default;bool first=true;
            foreach(var model in models)for(int i=0;i<=160;i++){
                double t=model.startTime+(model.endTime-model.startTime)*i/160.0;
                var state=MotionMathModel.Sample(model.parameters,t);
                if(state.velocityDefined)maxVectorSpeed=Math.Max(maxVectorSpeed,state.velocity.Length);
                if(state.accelerationDefined)maxVectorAcceleration=Math.Max(maxVectorAcceleration,state.acceleration.Length);
                var at=model.worldOrigin+RawVector(model,state.position)*model.worldUnitsPerModelUnit;
                var points=new List<Vector3>{at};
                if(model.showVelocity&&state.velocityDefined)points.Add(at+RawVector(model,state.velocity)*model.velocityArrowScale);
                if(model.showAcceleration&&state.accelerationDefined)points.Add(at+RawVector(model,state.acceleration)*model.accelerationArrowScale);
                if(model.showRadius)points.Add(model.worldOrigin+RawVector(model,model.parameters.origin)*model.worldUnitsPerModelUnit);
                foreach(var p in points){if(first){bounds=new Bounds(p,Vector3.zero);first=false;}else bounds.Encapsulate(p);}
            }
            if(first)return;
            motionFitScale=Mathf.Min(1,Mathf.Min(6.8f/Mathf.Max(.001f,bounds.size.x),1.1f/Mathf.Max(.001f,bounds.size.y)));
            motionFitOffset=new Vector3(-4.55f,.75f,0)-bounds.center*motionFitScale;
        }
        LineRenderer Line(Color color,float width) {
            LineRenderer r;
            if(lineCursor<lines.Count)r=lines[lineCursor];else {var go=Own(new GameObject("MotionGuide_"+lines.Count));r=go.AddComponent<LineRenderer>();r.useWorldSpace=true;r.sharedMaterial=lineMaterial;r.numCapVertices=4;r.numCornerVertices=4;lines.Add(r);}
            lineCursor++;r.gameObject.SetActive(true);r.numCapVertices=4;r.startColor=r.endColor=Color.white;r.startWidth=r.endWidth=width;r.alignment=LineAlignment.View;
            var props=new MaterialPropertyBlock();props.SetColor("_BaseColor",color);props.SetColor("_Color",color);r.SetPropertyBlock(props);return r;
        }
        void Poly(IList<Vector3> points,Color color,float width=.025f) {if(points.Count<2)return;var l=Line(color,width);l.positionCount=points.Count;for(int i=0;i<points.Count;i++)l.SetPosition(i,points[i]);}
        void Arrow(Vector3 from,Vector3 delta,Color color) {
            if(delta.sqrMagnitude<1e-10f)return;
            Vector3 end=from+delta;Poly(new[]{from,end},color,.045f);
            Vector3 d=delta.normalized,s=Vector3.Cross(d,stageCamera.transform.forward);if(s.sqrMagnitude<1e-8f)s=stageCamera.transform.right;s.Normalize();
            float head=Mathf.Min(.22f,delta.magnitude*.28f);Poly(new[]{end-d*head+s*head*.5f,end,end-d*head-s*head*.5f},color,.045f);
        }
        void PlaceCallout(Text label,Vector3 world,string text,bool visible) {
            Vector3 v=stageCamera.WorldToViewportPoint(world);float px=v.x*1920,py=(1-v.y)*1080;
            bool safe=visible&&v.z>0&&px>=85&&px<=700&&py>=245&&py<=680;
            label.gameObject.SetActive(safe);if(!safe)return;
            label.rectTransform.anchoredPosition=new Vector2(px+14,-py);label.text=text;
        }
        void PlaceDiagramText(Text label,Vector3 point,string text,Vector2 offset) {
            Vector3 v=stageCamera.WorldToViewportPoint(point);
            label.rectTransform.anchoredPosition=new Vector2(v.x*1920+offset.x,-(1-v.y)*1080+offset.y);
            label.text=text;
        }
        Vector3 GuidePoint(Vector2 pixel) {
            return stageCamera.ViewportToWorldPoint(new Vector3(pixel.x/1920,1-pixel.y/1080,17));
        }
        void AccelerationUnitGuide(Vector3 at,DVec value,bool isVelocity) {
            // This scene compares two collinear vectors of different units. Use
            // parallel tails attached to the object, with one fixed scale per
            // quantity and unit system, so gaining speed is visible in mobile.
            Vector3 projected=stageCamera.WorldToViewportPoint(at);
            Vector2 objectPixel=new Vector2(projected.x*1920,(1-projected.y)*1080);
            float side=isVelocity?-1:1;
            Vector2 start=shot.graphY
                ? new Vector2(objectPixel.x+side*56,Mathf.Clamp(objectPixel.y,578,650))
                : new Vector2(Mathf.Clamp(objectPixel.x+32,180,770),Mathf.Clamp(objectPixel.y+side*33,600,708));
            Vector3 dir=RawVector(shot,value);
            double limit=isVelocity?Math.Max(Math.Abs(shot.velocityMin),Math.Abs(shot.velocityMax))
                                   :Math.Max(Math.Abs(shot.accelerationMin),Math.Abs(shot.accelerationMax));
            if(shot.beatId!="M25-002"&&shot.beatId!="M25-012"&&shot.beatId!="M25-013")
                limit=isVelocity?maxVectorSpeed:maxVectorAcceleration;
            limit=Math.Max(limit,1e-8);
            float extent=shot.graphY?100:134;
            Vector2 tip=start+new Vector2(dir.x,-dir.y)*extent/(float)limit;
            Color color=isVelocity?Teal:Red;
            Poly(new[]{GuidePoint(objectPixel),GuidePoint(start)},Color.Lerp(Muted,color,.5f),.026f);
            Arrow(GuidePoint(start),GuidePoint(tip)-GuidePoint(start),color);
            Text label=isVelocity?velocityCallout:accelerationCallout;
            float x=Mathf.Clamp(tip.x+(isVelocity?-65:10),110,793);
            float y=isVelocity?563:741;
            Poly(new[]{GuidePoint(tip),GuidePoint(new Vector2(x+20,isVelocity?y+43:y-2))},color*.7f,.022f);
            label.gameObject.SetActive(true);
            label.rectTransform.anchoredPosition=new Vector2(x,-y);
            label.fontSize=44;
            label.text=isVelocity?"v · 속도":"a · 가속도";
        }
        void SecantMarker(Vector3 center) {
            var ring=new List<Vector3>();
            for(int i=0;i<=24;i++){
                float angle=i*Mathf.PI/12;
                ring.Add(center+new Vector3(.085f*Mathf.Cos(angle),.085f*Mathf.Sin(angle),-.04f));
            }
            Poly(ring,Green,.025f);
        }
        Vector3 Plot(double t,double value,double lo,double hi,float yBase) {
            double u=(t-shot.startTime)/(shot.endTime-shot.startTime);float x=1.8f+(float)u*6.5f;
            float y=yBase+(float)((value-lo)/(hi-lo))*PlotHeight;return new Vector3(x,y,-2);
        }
        void Graph(Func<MotionState,double> value,double lo,double hi,float yBase,Color color,double current,bool derivative,MotionParameters parameters=null,bool secondDerivative=false) {
            var model=parameters??shot.parameters;
            if(hi<=lo||shot.endTime<=shot.startTime)throw new InvalidOperationException("Graph range must increase.");
            Poly(new[]{new Vector3(1.8f,yBase+PlotHeight,-2),new Vector3(1.8f,yBase,-2),new Vector3(8.3f,yBase,-2)},Muted*.6f,.018f);
            if(lo<0&&hi>0)Poly(new[]{Plot(shot.startTime,0,lo,hi,yBase),Plot(shot.endTime,0,lo,hi,yBase)},Muted*.45f,.012f);
            List<Vector3> part=new List<Vector3>();
            for(int i=0;i<=180;i++) {
                double t=shot.startTime+(shot.endTime-shot.startTime)*i/180.0;
                if(i>0&&derivative&&(model.kind==MotionKind.PiecewiseExercise||model.kind==MotionKind.RoundTrip||model.kind==MotionKind.RacePath||(secondDerivative&&model.kind==MotionKind.AccelerationStep))){double previous=shot.startTime+(shot.endTime-shot.startTime)*(i-1)/180.0;var joins=model.kind==MotionKind.AccelerationStep?new[]{1.0}:model.kind==MotionKind.RoundTrip?new[]{2.0}:model.kind==MotionKind.RacePath?new[]{1.0,2.0,4.0}:new[]{2.0,4.0,7.0};foreach(double join in joins)if(previous<join&&t>=join){Poly(part,color);part.Clear();}}
                var s=MotionMathModel.Sample(model,t);double v=value(s);
                bool valid=(!derivative||(secondDerivative?s.accelerationDefined:s.velocityDefined))&&v>=lo&&v<=hi;
                // Never clamp out-of-range values into a false plateau or connect undefined joins.
                if(!valid) {Poly(part,color);part.Clear();continue;}
                part.Add(Plot(t,v,lo,hi,yBase));
            }
            Poly(part,color);
            float cursorX=Plot(current,lo,lo,hi,yBase).x;
            Poly(new[]{new Vector3(cursorX,yBase,-2.05f),new Vector3(cursorX,yBase+PlotHeight,-2.05f)},White*.65f,.018f);
            var currentState=MotionMathModel.Sample(model,current);double y=value(currentState);
            if((!derivative||(secondDerivative?currentState.accelerationDefined:currentState.velocityDefined))&&y>=lo&&y<=hi){Vector3 centre=Plot(current,y,lo,hi,yBase);var ring=new Vector3[33];for(int i=0;i<ring.Length;i++){float angle=i*Mathf.PI*2/32;ring[i]=centre+new Vector3(Mathf.Cos(angle)*.07f,Mathf.Sin(angle)*.07f,-.04f);}Poly(ring,color,.03f);}
        }
        public void Evaluate(double normalizedCue) {
            if(!built)Build();
            if(normalizedCue<0||normalizedCue>1)throw new ArgumentOutOfRangeException(nameof(normalizedCue),"No modulo looping or silent clamping.");
            subjectAnchor.gameObject.SetActive(true);
            foreach(var label in new[]{positionTitle,timeStart,timeEnd,timeAxis,values,details})label.gameObject.SetActive(true);
            formulaMeaning.rectTransform.anchoredPosition=new Vector2(92,-475);
            lineCursor=0;double t=shot.startTime+(shot.endTime-shot.startTime)*normalizedCue;var state=MotionMathModel.Sample(shot.parameters,t);Vector3 at=Position(state.position);subjectAnchor.position=at;
            if(comparisonAnimal) {
                var other=MotionMathModel.Sample(shot.comparisonParameters,t);
                comparisonAnimal.position=Position(other.position)+Vector3.down*.95f;
                PlaceDiagramText(tortoiseName,comparisonAnimal.position,"거북이",new Vector2(-145,10));
            }
            if(hareName)PlaceDiagramText(hareName,at,"토끼",new Vector2(-126,12));
            term.fontSize=shot.termExpanded?40:34;
            term.text=shot.termExpanded?shot.englishTerm+"\n"+shot.koreanTerm+"\n"+shot.meaning:shot.englishTerm+" · "+shot.koreanTerm+"\n"+shot.meaning;
            coordinateLabel.text=shot.subjectKind=="hare"?"오른쪽으로 갈수록 위치 x가 커집니다":"해설용 운동 모형 · "+shot.axisConvention;
            string component=shot.graphY?"y":"x";
            positionTitle.text=shot.valueLabel+" "+(shot.scalarFunction?"f(x)":component+"(t)")+" ["+shot.positionUnit+"]";velocityTitle.text=shot.derivativeLabel+" "+(shot.scalarFunction?"f′(x)":"v"+component+"(t)")+" ["+shot.positionUnit+"/"+shot.timeUnit+"]";accelerationTitle.text=shot.secondDerivativeLabel+" "+(shot.scalarFunction?"f″(x)":"a"+component+"(t)")+" ["+shot.positionUnit+"/"+shot.timeUnit+"²]";
            velocityTitle.gameObject.SetActive(shot.showVelocityGraph);accelerationTitle.gameObject.SetActive(shot.showAccelerationGraph);
            kind.text="현재 화면: 우리 구현\n해설용 해석 운동 모형 · 게임 실측 아님";
            var path=new List<Vector3>();for(int i=0;i<=160;i++){double pt=shot.startTime+(shot.endTime-shot.startTime)*i/160.0;path.Add(Position(MotionMathModel.Sample(shot.parameters,pt).position));}Poly(path,Muted*.45f,.018f);
            if((shot.beatId.StartsWith("M25-")||shot.beatId.StartsWith("M26-"))&&shot.showVelocity&&shot.showAcceleration&&state.velocityDefined&&state.accelerationDefined&&!shot.scalarFunction){
                AccelerationUnitGuide(at,state.velocity,true);
                AccelerationUnitGuide(at,state.acceleration,false);
            }else{
                if(shot.showVelocity&&state.velocityDefined)Arrow(at,DisplayVector(state.velocity)*shot.velocityArrowScale,Teal);
                if(shot.showAcceleration&&state.accelerationDefined)Arrow(at,DisplayVector(state.acceleration)*shot.accelerationArrowScale,Red);
                PlaceCallout(velocityCallout,at+DisplayVector(state.velocity)*shot.velocityArrowScale,"v  |v|="+state.velocity.Length.ToString("0.00"),shot.showVelocity&&state.velocityDefined);
                PlaceCallout(accelerationCallout,at+DisplayVector(state.acceleration)*shot.accelerationArrowScale,"a  |a|="+state.acceleration.Length.ToString("0.00"),shot.showAcceleration&&state.accelerationDefined);
            }
            if(shot.showRadius)Arrow(Position(shot.parameters.origin),at-Position(shot.parameters.origin),Yellow);
            PlaceCallout(radiusCallout,Vector3.Lerp(Position(shot.parameters.origin),at,.5f),"r = "+(state.position-shot.parameters.origin).Length.ToString("0.00"),shot.showRadius);
            if(shot.showSecant){var q=MotionMathModel.Sample(shot.parameters,t+shot.secantH);Poly(new[]{at,Position(q.position)},Green,.035f);}
            motionGuideCount=lineCursor;
            Func<MotionState,double> p=s=>shot.graphY?s.position.y:s.position.x,v=s=>shot.graphY?s.velocity.y:s.velocity.x,a=s=>shot.graphY?s.acceleration.y:s.acceleration.x;
            Graph(p,shot.positionMin,shot.positionMax,PositionBase,Yellow,t,false);
            comparisonLegend.gameObject.SetActive(shot.showComparison);comparisonLegend.text=shot.comparisonLabel;
            if(shot.showComparison)Graph(p,shot.positionMin,shot.positionMax,PositionBase,Teal,t,false,shot.comparisonParameters);
            if(shot.showVelocityGraph)Graph(v,shot.velocityMin,shot.velocityMax,VelocityBase,Teal,t,true);
            if(shot.showAccelerationGraph)Graph(a,shot.accelerationMin,shot.accelerationMax,AccelerationBase,Red,t,true,null,true);
            double[] range={shot.positionMax,shot.positionMin,shot.velocityMax,shot.velocityMin,shot.accelerationMax,shot.accelerationMin};
            for(int i=0;i<range.Length;i++){graphRangeLabels[i].gameObject.SetActive(i<2||(i<4?shot.showVelocityGraph:shot.showAccelerationGraph));graphRangeLabels[i].text=range[i].ToString("0.##");}
            float axisY=shot.showAccelerationGraph?727:shot.showVelocityGraph?552:377;
            foreach(var label in new[]{timeStart,timeEnd,timeAxis}){var pos=label.rectTransform.anchoredPosition;pos.y=-axisY;label.rectTransform.anchoredPosition=pos;}
            timeStart.text=shot.startTime.ToString("0.##");timeEnd.text=shot.endTime.ToString("0.##");timeAxis.text=shot.inputLabel+" ["+shot.timeUnit+"]";
            if(secantStart){secantStart.gameObject.SetActive(false);secantFinish.gameObject.SetActive(false);}
            if(shot.showSecant||shot.showTangent){
                double referenceTime=shot.showSecant&&shot.fixedSecant?shot.secantStartTime:t;
                double right=shot.showSecant?referenceTime+shot.secantH:Math.Min(shot.endTime,t+.3*(shot.endTime-shot.startTime));
                double left=shot.showSecant?referenceTime:Math.Max(shot.startTime,t-.3*(shot.endTime-shot.startTime));
                double referenceValue=p(MotionMathModel.Sample(shot.parameters,referenceTime));
                double slope=shot.showSecant?(p(MotionMathModel.Sample(shot.parameters,right))-referenceValue)/shot.secantH:v(state);
                var tangent=new List<Vector3>();
                for(int i=0;i<=40;i++){double x=left+(right-left)*i/40.0,y=referenceValue+slope*(x-referenceTime);if(x>=shot.startTime&&x<=shot.endTime&&y>=shot.positionMin&&y<=shot.positionMax)tangent.Add(Plot(x,y,shot.positionMin,shot.positionMax,PositionBase));}
                if(shot.showSecant||state.velocityDefined)Poly(tangent,shot.showSecant?Green:Teal,.045f);
                if(secantStart&&shot.showSecant&&left>=shot.startTime&&right<=shot.endTime&&tangent.Count>=2) {
                    var first=tangent[0];var last=tangent[tangent.Count-1];
                    secantStart.gameObject.SetActive(true);secantFinish.gameObject.SetActive(true);
                    SecantMarker(first);SecantMarker(last);
                    PlaceDiagramText(secantStart,first,"t",new Vector2(4,-10));
                    PlaceDiagramText(secantFinish,last,"t + h",new Vector2(-55,-10));
                }
            }
            values.text="t = "+t.ToString("0.000")+" "+shot.timeUnit+"   "+component+" = "+p(state).ToString("0.000")+" "+shot.positionUnit;
            if(shot.showVelocityGraph)values.text+="\n"+(state.velocityDefined?"v"+component+" = "+v(state).ToString("0.000")+" "+shot.positionUnit+"/"+shot.timeUnit:"v = 정의되지 않음 (구간 경계)");
            if(shot.showAccelerationGraph)values.text+="\n"+(state.accelerationDefined?"a"+component+" = "+a(state).ToString("0.000")+" "+shot.positionUnit+"/"+shot.timeUnit+"²":"a = 정의되지 않음");
            if(shot.showSecant){
                double left=shot.fixedSecant?shot.secantStartTime:t;
                var mean=MotionMathModel.SecantVelocity(shot.parameters,left,shot.secantH);
                details.text="Δt = "+shot.secantH.ToString("0.###")+" "+shot.timeUnit+"\n평균 속도 = "+
                    (shot.graphY?mean.y:mean.x).ToString("0.###")+" "+shot.positionUnit+"/"+shot.timeUnit;
            }else{
                details.text=shot.parameters.kind==MotionKind.Circle?"r = "+shot.parameters.radius.ToString("0.00")+"   ω = "+shot.parameters.omega.ToString("0.00")+" rad/s\n|v| = "+state.velocity.Length.ToString("0.000")+"   |a| = "+state.acceleration.Length.ToString("0.000"):"값은 현재 해설 모형에서 직접 계산\n화살표 축척은 장면 안에서 고정";
            }
            if(shot.showRiemann)RiemannOverlay(t);
            GraphLandmark(t);
            for(int i=lineCursor;i<lines.Count;i++)lines[i].gameObject.SetActive(false);
        }
        void GraphLandmark(double currentTime){
            if(triangleBase){
                var v=MotionMathModel.Sample(shot.parameters,currentTime).velocity.y;
                var tip=Plot(currentTime,v,shot.velocityMin,shot.velocityMax,VelocityBase);
                var foot=Plot(currentTime,0,shot.velocityMin,shot.velocityMax,VelocityBase);
                Poly(new[]{foot,tip},Teal,.042f);
                graphMark.gameObject.SetActive(true);
                PlaceDiagramText(graphMark,tip,"at",new Vector2(-55,-3));
                PlaceDiagramText(triangleBase,foot,"t",new Vector2(4,-5));
                return;
            }
            bool floor=shot.beatId=="M25-012"||shot.beatId=="M25-013";
            bool apex=shot.beatId=="M25-023";
            bool tangent=shot.beatId=="M26-025";
            graphMark.gameObject.SetActive(floor||apex||tangent);
            if(tangent){
                var s=MotionMathModel.Sample(shot.parameters,currentTime);
                var point=Plot(currentTime,s.position.x,shot.positionMin,shot.positionMax,PositionBase);
                string sign=Math.Abs(s.velocity.x)<1e-5?"v = 0":s.velocity.x>0?"v > 0":"v < 0";
                PlaceDiagramText(graphMark,point,sign,new Vector2(currentTime>(shot.startTime+shot.endTime)/2?-141:12,-9));
                return;
            }
            if(!floor&&!apex)return;
            double when=floor?shot.endTime:shot.parameters.timeToApex;
            var endpoint=MotionMathModel.Sample(shot.parameters,when);
            var at=Plot(when,endpoint.position.y,shot.positionMin,shot.positionMax,PositionBase);
            var initial=Plot(shot.startTime,endpoint.position.y,shot.positionMin,shot.positionMax,PositionBase);
            Poly(new[]{initial,at},Teal,.036f);
            SecantMarker(at);
            PlaceDiagramText(graphMark,at,floor?"바닥 · 도착":"정점 H, T",new Vector2(floor?-202:14,-8));
        }
        public void FocusOnRightDiagram(){
            subjectAnchor.gameObject.SetActive(false);
            foreach(var t in new[]{velocityCallout,accelerationCallout,radiusCallout})t.gameObject.SetActive(false);
            for(int i=0;i<motionGuideCount;i++)lines[i].gameObject.SetActive(false);
        }
        public void UseIndependentDiagram(bool hideConvention=true){
            FocusOnRightDiagram();
            if(hideConvention)coordinateLabel.gameObject.SetActive(false);
            for(int i=motionGuideCount;i<lineCursor;i++)lines[i].gameObject.SetActive(false);
            foreach(var label in new[]{positionTitle,velocityTitle,accelerationTitle,timeStart,timeEnd,timeAxis,values,details,comparisonLegend,graphMark})
                label.gameObject.SetActive(false);
            foreach(var label in graphRangeLabels)label.gameObject.SetActive(false);
        }
        public void SetExplanation(string formula,string meaning){
            formulaBoard.text=formula??"";formulaMeaning.text=meaning??"";
            bool board=!string.IsNullOrEmpty(formula);formulaBoard.gameObject.SetActive(board);formulaMeaning.gameObject.SetActive(!string.IsNullOrEmpty(meaning));
            foreach(var r in subjectAnchor.GetComponentsInChildren<Renderer>()){
                var block=new MaterialPropertyBlock();r.GetPropertyBlock(block);block.SetColor("_BaseColor",Color.white*(board?.75f:1));r.SetPropertyBlock(block);
            }
            if(!shot.showGraphs){
                foreach(var t in new[]{positionTitle,velocityTitle,accelerationTitle,timeStart,timeEnd,timeAxis,values,details,comparisonLegend})t.gameObject.SetActive(false);
                foreach(var t in graphRangeLabels)t.gameObject.SetActive(false);
                for(int i=motionGuideCount;i<lines.Count;i++)lines[i].gameObject.SetActive(false);
                bool meaningful=shot.showVelocity||shot.showAcceleration||shot.showRadius||shot.showSecant;
                subjectAnchor.gameObject.SetActive(meaningful);if(!meaningful)for(int i=0;i<motionGuideCount;i++)lines[i].gameObject.SetActive(false);
            }
            if(shot.scalarFunction){subjectAnchor.gameObject.SetActive(false);for(int i=0;i<motionGuideCount;i++)lines[i].gameObject.SetActive(false);foreach(var t in new[]{velocityCallout,accelerationCallout,radiusCallout})t.gameObject.SetActive(false);}
        }
        void RiemannOverlay(double currentTime) {
            if(shot.riemannFromModel){
                if(shot.riemannCount<1||shot.riemannCount>128||shot.riemannSample<0||shot.riemannSample>1)throw new InvalidOperationException("Invalid displayed rectangle count or sample fraction.");
                bool growingTriangle=shot.beatId=="M25-009";
                double upper=shot.riemannMovingEnd||growingTriangle?currentTime:shot.endTime;
                if(upper<=shot.startTime){details.text="아직 쌓인 넓이 = 0";return;}
                double stepWidth=(upper-shot.startTime)/shot.riemannCount;
                for(int i=0;i<shot.riemannCount;i++){
                    double begin=shot.startTime+i*stepWidth;var sampled=MotionMathModel.Sample(shot.parameters,begin+shot.riemannSample*stepWidth);double height=shot.graphY?sampled.velocity.y:sampled.velocity.x;
                    if(height<shot.velocityMin||height>shot.velocityMax)continue;
                    // Line width equals the interval's physical plot width. The fill
                    // is behind both the velocity curve and its rectangle outline.
                    if(Math.Abs(height)>1e-8){
                        double mid=begin+stepWidth*.5;
                        var z=Vector3.forward*.12f;
                        var l=Line(height>=0?new Color(.17f,.32f,.29f):new Color(.40f,.19f,.18f),
                                   Plot(begin+stepWidth,0,shot.velocityMin,shot.velocityMax,VelocityBase).x-Plot(begin,0,shot.velocityMin,shot.velocityMax,VelocityBase).x);
                        l.numCapVertices=0;l.positionCount=2;
                        l.SetPosition(0,Plot(mid,0,shot.velocityMin,shot.velocityMax,VelocityBase)+z);
                        l.SetPosition(1,Plot(mid,height,shot.velocityMin,shot.velocityMax,VelocityBase)+z);
                    }
                    Poly(new[]{Plot(begin,0,shot.velocityMin,shot.velocityMax,VelocityBase),Plot(begin,height,shot.velocityMin,shot.velocityMax,VelocityBase),Plot(begin+stepWidth,height,shot.velocityMin,shot.velocityMax,VelocityBase),Plot(begin+stepWidth,0,shot.velocityMin,shot.velocityMax,VelocityBase)},height>=0?Yellow:Red,.022f);
                }
                var delta=MotionMathModel.Sample(shot.parameters,upper).position-MotionMathModel.Sample(shot.parameters,shot.startTime).position;
                double exactIntegral=shot.graphY?delta.y:delta.x,rectangleSum=MotionMathModel.RiemannDisplacement(shot.parameters,shot.startTime,upper,shot.riemannCount,shot.riemannSample,shot.graphY);
                details.text=(shot.riemannSample==0?"왼쪽 끝":shot.riemannSample==1?"오른쪽 끝":"중간 표본")+" "+shot.riemannCount+"분할 · Δt="+stepWidth.ToString("0.00")+"\n합="+rectangleSum.ToString("0.00")+" · 정확한 변위="+exactIntegral.ToString("0.00");return;
            }
            if(shot.riemannCount<=0||shot.riemannDuration<=0)throw new InvalidOperationException("Riemann settings must be positive.");
            double sourceV=shot.graphY?shot.parameters.velocity.y:shot.parameters.velocity.x,sourceA=shot.graphY?shot.parameters.acceleration.y:shot.parameters.acceleration.x;
            if(shot.parameters.kind!=MotionKind.ConstantAcceleration||Math.Abs(sourceV-shot.riemannV0)>1e-9||Math.Abs(sourceA-shot.riemannAcceleration)>1e-9||Math.Abs(shot.startTime)>1e-9||Math.Abs(shot.endTime-shot.riemannDuration)>1e-9)
                throw new InvalidOperationException("Rectangle values must describe the same analytic velocity, time domain and component as the graph.");
            double dt=shot.riemannDuration/shot.riemannCount;
            for(int k=0;k<shot.riemannCount;k++) {
                double time=k*dt,height=shot.riemannV0+shot.riemannAcceleration*time;
                // Overlay belongs to the velocity plot, using the same real axes and units.
                if(height<shot.velocityMin||height>shot.velocityMax)continue;
                Poly(new[]{Plot(time,0,shot.velocityMin,shot.velocityMax,VelocityBase),Plot(time,height,shot.velocityMin,shot.velocityMax,VelocityBase),Plot(time+dt,height,shot.velocityMin,shot.velocityMax,VelocityBase),Plot(time+dt,0,shot.velocityMin,shot.velocityMax,VelocityBase)},Yellow,.022f);
            }
            double sum=MotionMathModel.LeftRiemannLinear(shot.riemannV0,shot.riemannAcceleration,shot.riemannDuration,shot.riemannCount);
            double exact=shot.riemannV0*shot.riemannDuration+.5*shot.riemannAcceleration*shot.riemannDuration*shot.riemannDuration;
            details.text="왼쪽 끝 "+shot.riemannCount+"분할 · Δt = "+dt.ToString("0.00")+"\n합 = "+sum.ToString("0.00")+"   정확한 변위 = "+exact.ToString("0.00");
        }
    }
}
