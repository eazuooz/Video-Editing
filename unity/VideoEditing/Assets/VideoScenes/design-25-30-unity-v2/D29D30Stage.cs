using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.DesignVisualV2
{
    // D29/D30 preserve the frozen narrative clock. All motion is derived from
    // cut-relative seconds; no wall-clock simulation or random state is used.
    public class D29D30Stage : DesignLessonStage
    {
        string mode;
        bool d29;
        readonly List<GameObject> objects = new List<GameObject>();
        readonly List<Text> words = new List<Text>();
        readonly List<Image> ui = new List<Image>();
        GameObject a, b, vehicle, prop, pointer, routeA, routeB, gate, special, clockHand, spray;
        readonly List<GameObject> timeTokens = new List<GameObject>();
        Image inputButton, evidenceImage; Text inputText, evidenceLabel;
        Text status, detail, formula, actionLabel, choiceLabel;
        Image progress, secondary;
        float duration;
        Vector3 a0, b0;

        static readonly Dictionary<string,string> D29 = new Dictionary<string,string> {
            {"01-02","race-start"},{"01-04","try"},{"02-01","arcade"},
            {"02-03","intent"},{"02-05","pressure"},{"02-07","read-person"},
            {"03-02","agreement"},{"03-04","block-goal"},{"03-06","block-feedback"},
            {"04-02","overload"},{"04-04","step"},{"04-06","race-burden"},
            {"05-01","race-steering"},{"05-02","race-acceleration"},{"05-04","race-turbo"},
            {"06-02","distance"},{"06-04","distance-flow"},{"06-06","handoff"},
            {"07-02","orders"},{"07-04","discovery"},{"07-06","release"},
            {"08-02","try"},{"08-04","discovery"}
        };
        static readonly Dictionary<string,string> D30 = new Dictionary<string,string> {
            {"01-02","commitment"},{"01-04","value"},{"02-01","commitment"},
            {"02-03","calendar"},{"02-05","opportunity"},{"03-02","return"},
            {"03-04","knockback"},{"03-06","result"},{"04-02","cost"},
            {"04-04","alternatives"},{"05-02","pleasures"},{"05-04","wash"},
            {"05-06","opportunity"},{"06-01","phone"},{"06-03","barriers"},
            {"07-03","place"},{"08-01","timeline-before"},{"08-02","timeline-after"},
            {"08-04","menu"},{"08-06","waiting"},{"09-02","comparison"},
            {"09-04","value"}
        };

        GameObject Keep(GameObject go) { objects.Add(go); return go; }
        Text Word(string s,float x,float y,int size=48,Color? color=null,float width=760) {
            var text=Label(s,x,y,size,color,width,90); words.Add(text); return text;
        }
        Image Bar(float x,float y,float w,float h,Color c) {
            var im=RectUI(x,y,w,h,c);ui.Add(im);return im;
        }
        float Phase(float t,float begin,float end) { return Mathf.SmoothStep(0,1,Mathf.InverseLerp(begin,end,t)); }
        float Part(float t) { return Mathf.Clamp01(t/Mathf.Max(.1f,duration)); }
        void Show(GameObject go,bool value) { if(go)go.SetActive(value); }
        void Show(Text go,bool value) { if(go)go.gameObject.SetActive(value); }
        void Show(Image go,bool value) { if(go)go.gameObject.SetActive(value); }

        public override void Build()
        {
            d29=slug=="kind-to-beginners";
            duration=frames/60f;
            var map=d29?D29:D30;
            if(!map.TryGetValue(cutId,out mode))throw new InvalidOperationException("Unplanned cut "+slug+"/"+cutId);
            if(mode.StartsWith("race")) BuildRace();
            else if(mode=="arcade") BuildArcade();
            else if(mode=="intent"||mode=="pressure"||mode=="read-person"||mode=="agreement"||mode.StartsWith("block")||mode.StartsWith("distance")||mode=="knockback"||mode=="return")BuildDuel();
            else if(mode=="orders"||mode=="discovery"||mode=="release"||mode=="handoff"||mode=="try"||mode=="step"||mode=="overload")BuildPath();
            else if(mode=="calendar")BuildCalendar();
            else if(mode=="timeline-before"||mode=="timeline-after")BuildTimeline();
            else if(mode=="place"||mode=="menu"||mode=="waiting"||mode=="wash"||mode=="pleasures"||mode=="result")BuildRoomAction();
            else BuildEvening();
            Apply(0);
            // One short action label below the scene; narration carries prose.
            if(detail && mode!="calendar" && mode!="timeline-before" && mode!="timeline-after" && mode!="race-turbo") detail.gameObject.SetActive(false);
        }

        void BuildRace()
        {
            string heading=mode=="race-start"?"내 손으로 레이스를 이어 가는 첫 성공":
                mode=="race-burden"?"동시에 해야 할 일을 나눠 준다":
                mode=="race-steering"?"핸들 어시스트 · Smart Steering":
                mode=="race-acceleration"?"자동 가속 · Auto-Accelerate":"보조를 켜도, 배울 선택은 남는다";
            Title(heading);
            var outer=new List<Vector3>();var inner=new List<Vector3>();
            for(int i=0;i<=80;i++) {
                float theta=Mathf.Lerp(-2.6f,.6f,i/80f);
                outer.Add(new Vector3(Mathf.Cos(theta)*5f,0,Mathf.Sin(theta)*2.7f+1.0f));
                inner.Add(new Vector3(Mathf.Cos(theta)*3.3f,0,Mathf.Sin(theta)*1.1f+1.0f));
            }
            Keep(Line("outer-road",outer.ToArray(),Grey,.09f));
            Keep(Line("inner-road",inner.ToArray(),Grey,.09f));
            vehicle=Keep(Asset("car",Vector3.zero,1.8f,0));
            routeA=Keep(Line("assist-path",new[]{new Vector3(.5f,.08f,-.8f),new Vector3(1.7f,.08f,-.4f),new Vector3(2.7f,.08f,.35f),new Vector3(3.5f,.08f,1.25f)},Teal,.08f));
            routeB=Keep(Line("outward-path",new[]{new Vector3(.5f,.09f,-.8f),new Vector3(2.7f,.09f,-1.2f),new Vector3(5.4f,.09f,-1.4f)},Red,.07f));
            pointer=Keep(Box("assist-antenna",new Vector3(0,2.2f,0),new Vector3(.04f,1,.04f),Yellow));
            prop=Keep(Sphere("antenna-light",new Vector3(0,2.8f,0),.18f,Yellow));
            status=Word("",960,790,50,Teal,1600);
            detail=Word("",960,840,42,White,1600);
            if(mode=="race-burden") {
                Word("방향",350,280,50,White,360);
                Word("가속",960,280,50,Yellow,360);
                Word("아이템",1570,280,50,Green,360);
                for(int i=0;i<3;i++)ui.Add(RectUI(350+610*i,335,330,8,i==1?Yellow:Grey));
            }
            if(mode=="race-acceleration" || mode=="race-burden") {
                inputButton=Bar(950,350,320,76,Yellow);
                inputText=Word("가속 누름",950,350,44,Color.black,310);
            }
            if(mode=="race-turbo") {
                Word("1단계",550,270,45,Teal,300);
                Word("2단계",960,270,45,Yellow,300);
                Word("3단계",1370,270,45,Grey,300);
                secondary=Bar(1370,310,300,8,Red);
            }
            if(mode=="race-steering") {
                evidenceImage=Picture("D:/Github/VideoEditing/projects/kind-to-beginners/production/local/batch-v1/sources/mk8-official-035.jpg",440,330,520,293);
                evidenceLabel=Word("실제 게임의 안테나",440,155,42,White,650);
            }
        }

        Vector3 RacePosition(float t)
        {
            float q=Phase(t,.25f,duration-.2f);
            float theta=Mathf.Lerp(-2.6f,.6f,q);
            Vector3 pos=new Vector3(Mathf.Cos(theta)*4.1f,0,Mathf.Sin(theta)*1.9f+1.0f);
            if(mode=="race-steering") {
                // During the narrated outward movement the vehicle actually
                // approaches the outside edge, then steering brings it back.
                float outside=Phase(t,3.05f,4.25f)*(1-Phase(t,4.25f,6.35f));
                pos += new Vector3(1.1f,0,-1.3f)*outside;
            }
            return pos;
        }
        void ApplyRace(float t)
        {
            float p=Part(t);Vector3 position=RacePosition(t);
            vehicle.transform.position=position;
            Vector3 tangent=RacePosition(Mathf.Min(duration-.01f,t+.03f))-RacePosition(Mathf.Max(0,t-.03f));
            if(tangent.sqrMagnitude>.000001f)vehicle.transform.rotation=Quaternion.LookRotation(tangent.normalized,Vector3.up);
            bool assist=mode=="race-steering"||mode=="race-turbo";
            pointer.transform.position=position+new Vector3(0,1.7f,0);
            prop.transform.position=position+new Vector3(0,2.23f,0);
            Show(pointer,assist&&(mode!="race-steering"||t>=6.65f));Show(prop,assist&&(mode!="race-steering"||t>=6.65f));
            Show(routeA,mode=="race-steering"&&t>=4.2f);Show(routeB,mode=="race-steering"&&t>=3&&t<5.8f);
            Show(evidenceImage,mode=="race-steering"&&t>=6.65f);Show(evidenceLabel,mode=="race-steering"&&t>=6.65f);
            if(mode=="race-start") {status.text=p<.6f?"코너 통과":"내 손으로 이어 가는 레이스";}
            if(mode=="race-burden") {status.text=p<.45f?"방향 + 가속 + 아이템":"가속 부담을 나눠 준다";inputButton.color=p<.45f?Yellow:Grey;inputText.text=p<.45f?"가속 누름":"가속 보조";}
            if(mode=="race-steering") {status.text=t<3?"방향 조절을 돕는다":t<4.3f?"코스 바깥으로 향함":t<6.65f?"안쪽으로 방향 보조":"켜진 보조를 알리는 안테나";}
            if(mode=="race-acceleration") {bool released=t>=2.4f;status.text=released?"손을 놓아도 전진 유지":"가속 버튼을 계속 누름";inputButton.color=released?Grey:Yellow;inputText.text=released?"입력 해제":"가속 누름";}
            if(mode=="race-turbo") {status.text=p<.5f?"보조를 끄는 선택도 가능":"Smart Steering ON";detail.text="울트라 미니 터보 사용 불가";}
        }

        void BuildArcade()
        {
            Title("같은 게임 화면, 보이지 않는 상대");
            a=Actor("experienced",new Vector3(-4,0,-.2f),false,2.7f,0);
            b=Actor("newcomer",new Vector3(4,0,-.2f),true,2.7f,180);
            camera.transform.position=new Vector3(-9,6,-13);camera.transform.LookAt(new Vector3(0,1.2f,0));
            // Recognizable cabinet housing is authored geometry; chairs, players
            // and desk bodies remain actual imported library models.
            Keep(Asset("chair",new Vector3(-4.9f,0,1.2f),1.4f,90));
            Keep(Asset("chair",new Vector3(4.9f,0,1.2f),1.4f,-90));
            for(int side=-1;side<=1;side+=2) {
                Keep(Box("cabinet",new Vector3(side*.85f,1.45f,0),new Vector3(.9f,2.9f,1.7f),Hex("243239")));
                Keep(Box("screen",new Vector3(side*1.32f,2.2f,-.03f),new Vector3(.04f,1.05f,1.35f),Hex("0A1118")));
                Keep(Box("control-deck",new Vector3(side*1.65f,1.35f,-.03f),new Vector3(.95f,.17f,1.6f),White));
                Keep(Sphere("joystick",new Vector3(side*1.65f,1.65f,-.25f),.18f,Yellow));
                Keep(Box("screen-health",new Vector3(side*1.35f,2.55f,0),new Vector3(.05f,.06f,.95f),Green));
                Keep(Box("screen-player",new Vector3(side*1.35f,2.05f,-.25f),new Vector3(.05f,.45f,.18f),Teal));
                Keep(Box("screen-opponent",new Vector3(side*1.35f,2.05f,.3f),new Vector3(.05f,.45f,.18f),Red));
            }
            Word("숙련자",420,270,52,Teal,430);Word("처음 온 사람",1500,270,52,Green,500);
            status=Word("두 화면이 등을 맞댄 배치",960,760,50,White,1500);
            Keep(Line("occluded-sightline",new[]{new Vector3(-3,2,0),new Vector3(-1.2f,2,0)},Teal,.055f));
            Keep(Line("other-sightline",new[]{new Vector3(3,2,0),new Vector3(1.2f,2,0)},Green,.055f));
        }

        void BuildDuel()
        {
            string heading= mode=="intent"?"화면의 승패와 상대의 기대는 다르다":
                mode=="pressure"?"초보자에게는 계속 맞는 시간":
                mode=="read-person"?"기술보다 먼저 상대의 상황을 읽는다":
                mode=="agreement"?"서로 원할 때의 전력 승부":
                mode.StartsWith("block")?"알려 준 조작으로 직접 막아 본다":
                mode.StartsWith("distance")?"입력을 줄여도 거리 판단은 남는다":
                mode=="knockback"?"피해가 쌓일수록 더 멀리 밀려난다":"재미있어서 고른 다음 한 판";
            Title(heading);
            Keep(Box("shared-arena",new Vector3(0,-.18f,.15f),new Vector3(12,.18f,3.8f),new Color(.12f,.15f,.17f)));
            a0=new Vector3(-2.4f,0,-.2f);b0=new Vector3(2.3f,0,-.2f);
            a=Actor("player-one",a0,false,2.9f,0);b=Actor("player-two",b0,true,2.9f,180);
            routeA=Keep(Line("distance",new[]{new Vector3(-2.4f,.04f,-1.7f),new Vector3(2.3f,.04f,-1.7f)},Teal,.07f));
            pointer=Keep(Sphere("input-pulse",new Vector3(-2.4f,.3f,-1.7f),.23f,Yellow));
            prop=Keep(Line("block-arc",new[]{new Vector3(.8f,.5f,-.3f),new Vector3(.5f,1.1f,-.3f),new Vector3(.5f,2.1f,-.3f),new Vector3(.8f,2.6f,-.3f)},Green,.10f));
            status=Word("",960,735,50,White,1600);detail=Word("",960,805,44,Teal,1600);
            special=Keep(Sphere("ranged-action",new Vector3(-1.2f,1.5f,-.2f),.23f,Teal));
            if(mode=="intent"||mode=="read-person") {
                Word("전력 승부?",480,270,52,Teal,600);
                Word("잠깐 해 보기?",1440,270,52,Green,650);
            }
            if(mode=="pressure") {
                Word("연속 공격",500,270,50,Red,600);
                Word("아직 방어를 모름",1430,270,50,White,700);
            }
            if(mode=="knockback")Word("원리 설명용 · 실제 게임 수치 아님",960,250,40,Grey,1500);
            if(mode=="agreement") {
                Word("겨뤄 보자",480,270,52,Teal,600);
                Word("좋아",1440,270,52,Green,600);
            }
        }

        void ApplyDuel(float t)
        {
            float p=Part(t);
            a.transform.position=a0;b.transform.position=b0;
            Pose(a,"Idle_A",t);Pose(b,"Idle_A",t+.4f);
            Show(prop,false);Show(pointer,false);Show(special,false);Show(routeA,mode.StartsWith("distance"));
            if(mode=="intent") {status.text=p<.5f?"같은 경기에 들어왔어도":"들어온 목적까지 같지는 않다";detail.text="먼저 상대가 기대한 경험을 확인";}
            if(mode=="read-person") {a.transform.position=a0+Vector3.right*Phase(t,0,1)*.7f;status.text="아무 반응 없이 무너지는 상대";detail.text="다음 공격 전에 상황을 살핀다";}
            if(mode=="pressure") {
                a.transform.position=new Vector3(-1.2f,0,-.2f);
                Pose(a,"Fight_Punch_A",t%1.7f);Pose(b,"Fight_Hit_A",t%1.7f);
                b.transform.position=new Vector3(.8f,0,-.2f)+Vector3.right*(.15f*Mathf.Abs(Mathf.Sin(t*3)));
                status.text="내가 할 수 있는 행동이 없다";detail.text="승패와 첫 경험은 다르게 느껴진다";
            }
            if(mode=="agreement") {float approach=Phase(t,.7f,2.2f);a.transform.position=a0+Vector3.right*approach*.7f;b.transform.position=b0-Vector3.right*approach*.7f;Pose(a,t<2.2f?"Walk_A":"FightM_Pose",t);Pose(b,t<2.2f?"Walk_A":"FightM_Pose",t);status.text="같은 승부에 동의";}
            if(mode.StartsWith("block")) {
                float action=Phase(t,.7f,2.1f);
                a.transform.position=Vector3.Lerp(a0,new Vector3(-.6f,0,-.2f),action);
                b.transform.position=new Vector3(1.3f,0,-.2f);
                Pose(a,"Fight_Punch_A",Mathf.Clamp(t-1.4f,0,1.1f));
                Pose(b,"FightM_Pose",0);
                Show(pointer,p>.1f&&p<.35f);Show(prop,p>.32f&&p<.85f);
                status.text=p<.3f?"방어 입력을 알려 준다":p<.7f?"한 번의 공격을 막는다":"다음 행동을 직접 선택";
                detail.text=p<.7f?"내 입력 → 눈앞의 결과":"배운 것이 남는 한 판";
            }
            if(mode.StartsWith("distance")) {
                bool far=p>.5f;
                b.transform.position=new Vector3(far?3.5f:-.5f,0,-.2f);
                Show(pointer,true);pointer.transform.localScale=Vector3.one*.23f*(1+.15f*Mathf.Sin(t*6));
                Show(special,far);special.transform.position=Vector3.Lerp(new Vector3(-1.1f,1.6f,-.2f),new Vector3(3.4f,1.6f,-.2f),Mathf.Repeat((t-duration*.5f)*1.2f,1));
                Pose(a,"Fight_Punch_A",(t%2f)*.7f);
                status.text=far?"먼 거리 → 원거리 행동":"가까운 거리 → 짧은 공격";
                detail.text=mode=="distance"?"입력은 같아도 상황에 맞는 공격":"공격이 닿는 거리와 흐름을 먼저 경험";
            }
            if(mode=="knockback") {
                float cycle=t%duration;bool high=p>.5f;
                float phase=high?(p-.5f)*2:p*2;
                float launch=Mathf.Sin(Mathf.Clamp01((phase-.2f)/.7f)*Mathf.PI*.5f);
                a.transform.position=new Vector3(-2.8f,0,-.2f);
                b.transform.position=new Vector3(.2f+launch*(high?5.1f:1.7f),Mathf.Sin(launch*Mathf.PI)*(high?1.2f:.6f),-.2f);
                Pose(a,"Fight_Punch_A",phase);Pose(b,"Fight_Hit_A",phase);
                status.text=high?"더 많이 쌓인 피해":"적게 쌓인 피해";
                detail.text=high?"같은 공격에도 더 멀리":"짧게 밀려나는 모습";
            }
            if(mode=="return") {
                a.transform.position=new Vector3(-1.2f,0,-.2f);b.transform.position=new Vector3(.8f,0,-.2f);
                Pose(a,"Fight_Punch_A",t%2);Pose(b,"Fight_Hit_A",t%2);
                status.text=p<.5f?"이번 한 판이 즐거웠다":"한 판 더 하기로 선택";
                detail.text="시간은 그 선택 뒤에 쌓인다";
            }
        }

        void BuildPath()
        {
            Title(mode=="orders"?"지시대로만 움직이면 발견이 줄어든다":mode=="overload"?"낯선 조작은 하나씩 경험하게":mode=="handoff"?"부담은 나누고 판단은 남긴다":mode=="try"?"작은 성공을 다음 시도로":"다음 행동은 본인이 고르게");
            a0=new Vector3(-4.3f,0,-1);b0=new Vector3(-5.4f,0,1.5f);
            a=Actor("newcomer",a0,true,2.6f,0);b=Actor("guide",b0,false,2.6f,0);
            Keep(Asset("chest",new Vector3(4.2f,0,-1.8f),1.4f,-20));
            Keep(Asset("crystal",new Vector3(4.0f,0,2),1.9f,0));
            Keep(Asset("tree",new Vector3(5.7f,0,2),2.7f,0));
            Keep(Asset("tree",new Vector3(-3.9f,0,3),2.5f,30));
            routeA=Keep(Line("chosen-route",new[]{new Vector3(-4.3f,.04f,-1),new Vector3(0,.04f,-1),new Vector3(4.2f,.04f,-1.8f)},Teal,.09f));
            routeB=Keep(Line("other-route",new[]{new Vector3(0,.04f,-1),new Vector3(1,.04f,.5f),new Vector3(4.0f,.04f,2)},Yellow,.08f));
            prop=Keep(Sphere("selection-marker",new Vector3(4.2f,2.1f,-1.8f),.32f,Yellow));
            status=Word("",960,740,50,White,1500);detail=Word("",960,810,42,Teal,1600);
            if(mode=="overload") {
                for(int i=0;i<3;i++)Word(new[]{"어느 버튼?","표시는 무슨 뜻?","지금 할 일?"}[i],360+i*600,215,45,i==0?Yellow:Grey,560);
            }
        }

        void ApplyPath(float t)
        {
            float p=Part(t),q=Phase(t,.5f,duration-.3f);
            bool branch=mode=="discovery"||mode=="release"||mode=="handoff";
            Vector3 target=branch?new Vector3(3.3f,0,1.8f):new Vector3(3.3f,0,-1.5f);
            Vector3 mid=new Vector3(-.3f,0,-1);
            a.transform.position=q<.5f?Vector3.Lerp(a0,mid,q*2):Vector3.Lerp(mid,target,(q-.5f)*2);
            a.transform.rotation=Quaternion.Euler(0,branch&&q>.5f?-35:0,0);
            Pose(a,q<.97f?"Walk_A":"Idle_A",t);
            Pose(b,mode=="orders"?"Walk_A":"Idle_A",t);b.transform.position=mode=="orders"?a.transform.position+new Vector3(.7f,0,1.2f):b0;
            Show(b,mode=="orders"||mode=="release"||mode=="handoff"||mode=="try");
            Show(routeB,mode!="orders"&&mode!="step"&&mode!="try");
            prop.transform.position=(branch?new Vector3(4,2.6f,2):new Vector3(4.2f,2.1f,-1.8f))+Vector3.up*(Mathf.Sin(t*2)*.08f);
            if(mode=="orders") {status.text="다음 길도, 다음 행동도 지시대로";detail.text="실수와 함께 선택의 순간도 줄어든다";}
            if(mode=="discovery") {status.text=p<.45f?"눈에 들어온 다른 장소":"내가 고른 길에서 발견";detail.text="선택 → 이동 → 결과 확인";}
            if(mode=="release") {status.text=p<.4f?"필요한 조작만 알려 준다":"다음 행동은 본인이 고른다";detail.text="안내자는 뒤에 남는다";}
            if(mode=="handoff") {status.text="입력 부담 하나를 덜어 준다";detail.text=p<.5f?"거리와 다음 행동을 볼 여유":"판단까지 대신 가져가지 않는다";}
            if(mode=="step"||mode=="overload") {status.text=p<.5f?"우선 한 가지를 해 본다":"내 행동의 결과가 보인다";detail.text=p<.5f?"온보딩 · Onboarding":"다음 행동은 그 뒤에";}
            if(mode=="try") {status.text=p<.5f?"한 번 해 볼 마음":"내가 알아낸 결과";detail.text=p<.5f?"첫 시도를 지켜 준다":"다음 시도를 스스로 고른다";}
        }

        void BuildCalendar()
        {
            Title("300시간을 시작 전에 약속한다면");
            a=Actor("player",new Vector3(-5.1f,0,0),true,3.4f,30);
            Keep(Asset("chair",new Vector3(-5.2f,0,1.5f),1.9f,0));
            for(int row=0;row<15;row++)for(int col=0;col<20;col++) {
                var cell=Bar(835+col*40,310+row*25,29,15,Grey);cell.name="day-"+(row*20+col);
            }
            Word("가정 예시",1340,240,44,Grey,800);
            status=Word("하루 1시간",480,750,54,Teal,780);
            formula=Word("300시간 ÷ 1시간/일 = 300일",1280,750,48,Yellow,1120);
        }

        void ApplyCalendar(float t)
        {
            float p=Phase(t,.3f,duration-1.1f);
            int count=Mathf.RoundToInt(p*300);
            for(int i=0;i<ui.Count;i++)ui[i].color=i<count?Yellow:Grey*.45f;
            Pose(a,"Idle_A",t);
            formula.text=count<300?"하루씩 비워야 할 자리 "+count+"일":"300시간 ÷ 1시간/일 = 300일";
        }

        void MakeClock(Vector3 center)
        {
            var ring=new List<Vector3>();
            for(int i=0;i<=60;i++){float angle=i*Mathf.PI*2/60;ring.Add(center+new Vector3(Mathf.Cos(angle)*.72f,Mathf.Sin(angle)*.72f,0));}
            Keep(Line("one-hour-clock",ring.ToArray(),Yellow,.055f));
            for(int i=0;i<12;i++){float angle=i*Mathf.PI*2/12;var unit=new Vector3(Mathf.Cos(angle),Mathf.Sin(angle),0);Keep(Line("clock-tick",new[]{center+unit*.59f,center+unit*.69f},White,.035f));}
            clockHand=Keep(Line("clock-minute-hand",new[]{Vector3.zero,new Vector3(0,.53f,0)},Yellow,.055f));clockHand.transform.position=center;
            Keep(Line("clock-hour-hand",new[]{center,center+new Vector3(-.25f,.15f,0)},White,.065f));
        }
        void BuildEvening()
        {
            string heading=mode=="commitment"?"시작 전에 보이는 긴 시간":mode=="comparison"?"같은 숫자, 다른 출발점":mode=="phone"?"다른 선택지는 손 닿는 곳에":mode=="barriers"?"시작 전에 필요한 준비를 살핀다":mode=="cost"?"분량만 늘린다고 가치가 늘지는 않는다":mode=="value"?"그 시간을 쓰길 잘했다고 느끼게":"오늘 저녁 한 시간에도 선택지는 많다";
            Title(heading);
            a0=new Vector3(0,0,-.8f);a=Actor("choosing-player",a0,true,3.0f,0);
            Keep(Asset("chair",new Vector3(-4.7f,0,1.2f),1.8f,0));
            Keep(Asset("table",new Vector3(3.8f,0,1.7f),1.15f,0));
            b=Actor("friend",new Vector3(5.6f,0,.7f),false,2.6f,180);
            Keep(Asset("cup",new Vector3(3.8f,1.18f,1.7f),.4f,0));
            // The display and simple controller identify a game/film activity;
            // these are original props, not screenshots of any real product.
            if(mode!="barriers") {
                Keep(Box("display-frame",new Vector3(-4.7f,2.7f,2.2f),new Vector3(2.6f,1.55f,.16f),Grey));
                Keep(Box("display-screen",new Vector3(-4.7f,2.7f,2.08f),new Vector3(2.4f,1.35f,.035f),Hex("14333B")));
            }
            prop=Keep(Box("handheld-device",new Vector3(-.8f,2.05f,-1),new Vector3(.63f,.95f,.07f),Grey));
            pointer=Keep(Box("device-screen",new Vector3(-.8f,2.05f,-1.05f),new Vector3(.53f,.74f,.025f),Teal));
            Show(prop,mode=="phone");Show(pointer,mode=="phone");
            if(mode!="barriers")MakeClock(new Vector3(0,3.6f,1.3f));
            status=Word("",960,790,50,White,1640);detail=Word("",960,840,42,Teal,1650);
            if(mode=="commitment"||mode=="cost"||mode=="comparison") {
                int n=mode=="cost"?10:30;
                for(int i=0;i<n;i++)timeTokens.Add(Keep(Box("time-unit-"+i,new Vector3(-5.5f+(i%15)*.75f,.3f+(i/15)*.38f,3.5f),new Vector3(.6f,.28f,.45f),Yellow)));
                formula=Word(mode=="cost"?"분량 +100시간":"가정: 300시간",1330,270,58,Yellow,940);
                if(mode=="cost")formula.text="분량 +100시간";
            }
            if(mode=="comparison") {Word("먼저 요구한 시간",410,215,44,Yellow,780);Word("즐긴 뒤의 기록",1500,215,44,Teal,780);}
            if(mode=="opportunity"||mode=="alternatives"||mode=="pleasures"||mode=="value") {
                Word("게임 / 영상",390,200,48,Teal,650);Word("친구 / 휴식",1530,200,48,Green,650);
            }
            if(mode=="barriers") {
                Word("시간 확보",350,230,48,Yellow,550);Word("플레이 환경",960,230,48,Teal,550);Word("집중",1570,230,48,Green,550);
                for(int i=0;i<3;i++)Bar(350+i*610,290,440,9,Grey);
            }
        }
        void ApplyEvening(float t)
        {
            float p=Part(t),walk=Phase(t,.6f,duration-1.2f);
            bool chooseRight=mode=="pleasures"||mode=="opportunity"||mode=="value";
            Vector3 destination=chooseRight?new Vector3(3.5f,0,-.7f):new Vector3(-3.6f,0,-.7f);
            a.transform.position=Vector3.Lerp(a0,destination,walk);
            a.transform.rotation=Quaternion.Euler(0,chooseRight?0:180,0);
            Pose(a,walk>.01f&&walk<.99f?"Walk_A":"Idle_A",t);Pose(b,"Idle_A",t+.5f);
            if(clockHand)clockHand.transform.localRotation=Quaternion.Euler(0,0,-Mathf.Lerp(0,300,p));
            for(int i=0;i<timeTokens.Count;i++) {
                bool visible=i<Mathf.CeilToInt(Phase(t,.2f,duration*.7f)*timeTokens.Count);
                timeTokens[i].SetActive(visible);
            }
            if(mode=="commitment") {
                // The same newcomer stops rather than starting the long commitment.
                a.transform.position=Vector3.Lerp(a0,new Vector3(-1.2f,0,-.7f),Phase(t,.4f,1.6f));
                Pose(a,t<1.6f?"Walk_A":"Idle_A",t);
                status.text=p<.55f?"시작 전부터 비워 둬야 할 시간":"가정 예시: 긴 시간을 먼저 약속";
            }
            if(mode=="comparison") {status.text=p<.5f?"먼저 요구하는 시간":"즐거운 선택 뒤에 쌓인 시간";formula.text=p<.5f?"시작 전: 300시간":"즐긴 뒤: 300시간";for(int i=0;i<timeTokens.Count;i++)Tint(timeTokens[i],p<.5f?Yellow:Teal);}
            if(mode=="opportunity") {status.text="한쪽을 고르면 다른 기회는 포기";}
            if(mode=="alternatives") {status.text="게임 밖의 활동과도 나란히 경쟁";}
            if(mode=="pleasures") {status.text=p<.5f?"대전 한 판의 집중":"친구와 시간을 보내는 선택";}
            if(mode=="cost") {status.text="분량 증가 ≠ 경험의 가치";}
            if(mode=="value") {status.text=p<.5f?"내가 고른 활동":"시간을 쓰길 잘했다고 느끼는 경험";}
            if(mode=="phone") {
                a.transform.position=a0;a.transform.rotation=Quaternion.Euler(0,-20,0);Pose(a,"Idle_A",t);
                prop.transform.position=new Vector3(-.8f,2.05f+.06f*Mathf.Sin(t*2),-1);
                pointer.transform.position=prop.transform.position+new Vector3(0,0,-.05f);
                Tint(pointer,p<.33f?Teal:p<.66f?Green:Yellow);
                status.text=p<.33f?"손 닿는 화면에서 글 보기":p<.66f?"사진 보기":"영상 보기";
            }
            if(mode=="barriers") {
                int active=Mathf.Min(2,(int)(p*3));
                for(int i=0;i<ui.Count;i++)ui[i].color=i<=active?new[]{Yellow,Teal,Green}[Mathf.Min(2,i)]:Grey;
                status.text=new[]{"시간을 비운다","기기와 자리를 준비한다","조작과 상황에 집중한다"}[active];
            }
        }

        void BuildRoomAction()
        {
            Title(mode=="wash"?"내 행동이 눈앞의 변화를 만든다":mode=="pleasures"?"같은 시간에도 다른 재미를 고른다":mode=="menu"?"메뉴의 의미 있는 선택도 개입이다":mode=="waiting"?"기다리는 동안 필요한 선택을 허용한다":mode=="result"?"재미가 먼저, 플레이 시간은 결과":"선택하고 놓으면, 방이 달라진다");
            Keep(Asset("table",new Vector3(2.2f,0,.2f),2f,0));
            Keep(Asset("chair",new Vector3(4.5f,0,1),2.2f,-35));
            Keep(Asset("chest",new Vector3(-3.8f,0,.1f),1.5f,20));
            a=Actor("player",new Vector3(-1.5f,0,1.4f),true,2.7f,100);
            prop=Keep(Asset("cup",new Vector3(-3.8f,1.6f,.1f),.9f,0));
            b=Keep(Asset("crystal",new Vector3(-3.4f,1.5f,.2f),.9f,0));
            pointer=Keep(Sphere("selection-cursor",new Vector3(-3.8f,2.35f,.1f),.2f,Yellow));
            gate=Keep(Box("dirt-overlay",new Vector3(2.2f,2.03f,.2f),new Vector3(2,.035f,1.2f),new Color(.26f,.20f,.13f)));
            spray=Keep(Line("water-stream",new[]{new Vector3(-.4f,1.6f,.5f),new Vector3(1.2f,2.08f,.2f)},Teal,.09f));
            special=Keep(Box("hose-nozzle",new Vector3(-.4f,1.6f,.5f),new Vector3(.45f,.12f,.15f),Grey));
            routeA=Keep(Line("object-route",new[]{new Vector3(-3.5f,.05f,-1.5f),new Vector3(0,.05f,-1.5f),new Vector3(2.3f,.05f,-1.5f)},Teal,.07f));
            status=Word("",960,790,50,White,1650);detail=Word("",960,840,44,Teal,1650);
            Show(gate,mode=="wash"||mode=="pleasures");Show(spray,mode=="wash"||mode=="pleasures");Show(special,mode=="wash"||mode=="pleasures");
            if(mode=="menu"||mode=="waiting") {
                Word("컵",610,260,50,White,440);Word("장식",1310,260,50,White,440);
                progress=Bar(610,320,450,8,Yellow);secondary=Bar(1310,320,450,8,Grey);
                choiceLabel=Word("",960,195,44,Teal,1300);
            }
        }

        void ApplyRoomAction(float t)
        {
            float p=Part(t),q=Phase(t,.6f,duration-1);
            Pose(a,"Idle_A",t);a.transform.rotation=Quaternion.Euler(0,Mathf.Lerp(-50,65,q),0);
            Vector3 start=new Vector3(-3.8f,1.6f,.1f),end=new Vector3(2.2f,2.05f,.2f);
            prop.transform.position=Vector3.Lerp(start,end,q)+Vector3.up*Mathf.Sin(q*Mathf.PI)*1.4f;
            b.transform.position=new Vector3(-3.4f,1.6f,.2f);
            pointer.transform.position=prop.transform.position+Vector3.up*.7f;
            Show(b,p>.65f||mode=="menu");Show(pointer,p<.65f||mode=="menu");
            if(mode=="wash"||mode=="pleasures") {
                Show(prop,false);Show(b,false);Show(pointer,true);Show(routeA,false);
                float remaining=1-q;
                gate.transform.localScale=new Vector3(2*remaining,.035f,1.2f);
                gate.transform.position=new Vector3(2.2f+q,2.03f,.2f);
                pointer.transform.position=new Vector3(1.2f+q*2,2.2f,-.5f);
                spray.GetComponent<LineRenderer>().SetPositions(new[]{new Vector3(-.4f,1.6f,.5f),new Vector3(1.2f+q*2,2.08f,.2f)});
                a.transform.rotation=Quaternion.Euler(0,0,0);Pose(a,"FightM_Pose",0);
                status.text=p<.7f?"지나간 자리의 때가 사라진다":"깨끗해진 표면이 결과로 남는다";
                if(mode=="pleasures")status.text="전투와 다른, 정리에 집중하는 즐거움";
                detail.text="눈앞의 변화가 다음 행동을 부른다";
            } else if(mode=="waiting") {
                Show(gate,false);Show(b,true);Show(routeA,false);
                bool selected=p>.32f;progress.color=selected?Grey:Yellow;secondary.color=selected?Yellow:Grey;
                float arrive=Phase(t,duration*.56f,duration*.9f);
                prop.transform.position=end;b.transform.position=Vector3.Lerp(new Vector3(-3.4f,1.6f,.2f),new Vector3(3.0f,2.05f,.2f),arrive)+Vector3.up*Mathf.Sin(arrive*Mathf.PI)*.7f;
                pointer.transform.position=(selected?b:prop).transform.position+Vector3.up*.7f;
                choiceLabel.text=arrive<.95f?"전환 중 · 다음 물건 선택 가능":"선택한 물건 배치";
                status.text=selected?"기다리는 동안 다음 선택":"컵을 놓은 뒤 이어질 선택";
                detail.text="의미 없는 대기를 개입할 시간으로";
            } else if(mode=="menu") {
                bool selected=p>.35f;progress.color=selected?Grey:Yellow;secondary.color=selected?Yellow:Grey;
                float place=Phase(t,duration*.52f,duration*.88f);
                prop.transform.position=start;b.transform.position=Vector3.Lerp(new Vector3(-3.4f,1.6f,.2f),end,place)+Vector3.up*Mathf.Sin(place*Mathf.PI)*.8f;
                pointer.transform.position=(selected?b:prop).transform.position+Vector3.up*.7f;Show(b,true);Show(routeA,false);
                choiceLabel.text=selected?"장식을 선택 → 방에 배치":"컵을 살펴본다";
                status.text=p<.45f?"캐릭터는 멈춰 있어도":"입력이 선택과 결과로 이어진다";
                detail.text="메뉴에서의 의미 있는 선택";
            } else if(mode=="result") {status.text="할 만한 행동이 다음 행동을 부른다";detail.text="플레이 시간은 뒤따라온 결과";}
            else {status.text=p<.3f?"물건을 고른다":p<.75f?"놓을 자리를 선택한다":"방이 달라진 것을 확인한다";detail.text="선택 → 행동 → 확인";}
        }

        void BuildTimeline()
        {
            bool after=mode=="timeline-after";
            Title(after?"놀이 40초는 지키고, 대기만 줄인다":"직접 개입하는 시간과 대기를 나눠 본다");
            Keep(Asset("table",new Vector3(2.6f,0,.6f),1.75f,0));
            Keep(Asset("chest",new Vector3(-4.2f,0,.6f),1.3f,0));
            a=Actor("player",new Vector3(-2.8f,0,.2f),true,2.7f,0);
            prop=Keep(Asset("cup",new Vector3(-4.2f,1.35f,.6f),.75f,0));
            a0=a.transform.position;
            Word("가정 예시 · 실제 게임 측정값 아님",960,230,40,Grey,1700);
            Bar(960,660,1440,44,new Color(.17f,.18f,.20f));
            progress=Bar(720,660,960,44,Teal);
            secondary=Bar(after?1320:1440,660,after?240:480,44,Yellow);
            actionLabel=Word("조작 40초",650,725,50,Teal,800);
            detail=Word(after?"대기 10초":"대기 20초",1460,725,46,Yellow,600);
            formula=Word(after?"40 / 50 = 80%":"40 / 60 = 2/3",960,810,58,White,1600);
            status=Word("",960,300,45,White,1400);
        }

        void ApplyTimeline(float t)
        {
            bool after=mode=="timeline-after";float p=Part(t);
            // Illustrative clock is accelerated and explicitly hypothetical; it
            // is never presented as a timing measurement of the actual game.
            float action=after?Phase(t,.3f,6.4f):Phase(t,6.8f,9.35f);
            bool waiting=action>=1;
            a.transform.position=Vector3.Lerp(a0,new Vector3(1.4f,0,.2f),action);
            prop.transform.position=Vector3.Lerp(new Vector3(-4.2f,1.35f,.6f),new Vector3(2.6f,1.8f,.6f),action)+Vector3.up*Mathf.Sin(action*Mathf.PI)*.8f;
            Pose(a,waiting?"Idle_A":"Walk_A",t);
            status.text=waiting?"대기":"선택 · 조작";
            if(after) {
                float trim=Phase(t,.4f,3.3f);
                secondary.rectTransform.sizeDelta=new Vector2(Mathf.Lerp(480,240,trim),44);
                secondary.rectTransform.anchoredPosition=new Vector2(Mathf.Lerp(1440,1320,trim)-960,540-660);
                detail.text=trim>.95f?"대기 10초":"대기 20초 → 10초";
                actionLabel.text=t<6.48f?"조작 40초":"조작 40초 · 그대로";
                Show(formula,t>=8.56f);
                status.text=t>=4.2f&&t<6.48f?"전체 50초":t>=11.46f?"불필요한 대기 10초 감소":"같은 놀이를 유지";
            } else {
                Show(progress,t>=6.8f);Show(actionLabel,t>=6.8f);
                Show(secondary,t>=9.36f);Show(detail,t>=9.36f);
                Show(formula,t>=13.36f);
                if(t<6.8f)status.text="설계를 비교하는 1분 예시";
            }
        }

        public override void Apply(float t)
        {
            if(mode==null)return;
            t=Mathf.Clamp(t,0,Mathf.Max(0,duration-1/60f));
            if(mode.StartsWith("race"))ApplyRace(t);
            else if(mode=="arcade") {Pose(a,"Idle_A",t);Pose(b,"Idle_A",t+.4f);status.text=Part(t)<.55f?"두 화면이 등을 맞댄 배치":"건너편에서 누가 하는지 보이지 않는다";}
            else if(mode=="intent"||mode=="pressure"||mode=="read-person"||mode=="agreement"||mode.StartsWith("block")||mode.StartsWith("distance")||mode=="knockback"||mode=="return")ApplyDuel(t);
            else if(mode=="orders"||mode=="discovery"||mode=="release"||mode=="handoff"||mode=="try"||mode=="step"||mode=="overload")ApplyPath(t);
            else if(mode=="calendar")ApplyCalendar(t);
            else if(mode=="timeline-before"||mode=="timeline-after")ApplyTimeline(t);
            else if(mode=="place"||mode=="menu"||mode=="waiting"||mode=="wash"||mode=="pleasures"||mode=="result")ApplyRoomAction(t);
            else ApplyEvening(t);
        }
    }
}
