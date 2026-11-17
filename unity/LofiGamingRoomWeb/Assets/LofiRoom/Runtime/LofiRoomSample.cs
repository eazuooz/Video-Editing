using System.Collections;
using UnityEngine;

namespace Yamyam.LofiRoom
{
    // The actor must be a real rigged asset. Missing clips are never replaced by
    // hand-authored limb rotations or a stand-in character.
    public sealed class LofiRoomSample : MonoBehaviour
    {
        public Animator actor;
        public Light deskLight;
        public Light fillLight;
        public Camera roomCamera;
        public AudioSource music;
        public ParticleSystem rain;
        public float calibratedWalkSpeed = 1.05f;
        public bool hasIdle;
        public bool hasWalk;
        public bool hasSit;
        public string assetVersion = "Tripo H3.1 · Atmosphere / Motion v3";
        private Coroutine action;
        private bool night = true;
        private string state = "Ready";
        private float distanceTravelled;
        private Vector3 previousPosition;
        public int observedFrame;
        public float groundY;
        public bool showControls=true;
        public bool moving;
        public LofiAtmosphere atmosphere;
        public LofiActivities activities;
        public LofiHearth hearth;
        public LofiMemo memo;
        public float turnSpeed=145f;
        private Vector3 motionTarget;
        private Font uiFont;

        IEnumerator Start()
        {
            Application.targetFrameRate = 60;
            Application.runInBackground = true;
            uiFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",18);
            if (actor) { actor.applyRootMotion = true; previousPosition = actor.transform.position; }
            SetNight(PlayerPrefs.GetInt("ai3d-lofi-room-v1-night", 1) == 1);
            Idle();
            yield return null;yield return null;
            CalibrateFloor();
        }

        void CalibrateFloor()
        {
            if(!actor)return;
            float min=float.PositiveInfinity;
            foreach(var skin in actor.GetComponentsInChildren<SkinnedMeshRenderer>())
            {
                var mesh=new Mesh();skin.BakeMesh(mesh);
                foreach(var vertex in mesh.vertices)min=Mathf.Min(min,skin.transform.TransformPoint(vertex).y);
                Destroy(mesh);
            }
            if(!float.IsInfinity(min))
            {
                var p=actor.transform.position;p.y+=.08f-min;actor.transform.position=p;groundY=p.y;previousPosition=p;
            }
        }

        void Update()
        {
            observedFrame++;
#if ENABLE_LEGACY_INPUT_MANAGER
            if(Input.GetKeyDown(KeyCode.Alpha1))Walk();
            if(Input.GetKeyDown(KeyCode.Alpha2))Idle();
#endif
#if ENABLE_INPUT_SYSTEM
            var keyboard=UnityEngine.InputSystem.Keyboard.current;
            if(keyboard!=null && (!memo || !memo.isOpen))
            {
                if(keyboard.digit1Key.wasPressedThisFrame)Walk();
                if(keyboard.digit2Key.wasPressedThisFrame)Idle();
                if(keyboard.digit3Key.wasPressedThisFrame)ToggleNight();
                if(keyboard.digit4Key.wasPressedThisFrame)ToggleRain();
                if(keyboard.digit5Key.wasPressedThisFrame)ToggleMusic();
                if(keyboard.digit6Key.wasPressedThisFrame)CameraDesk();
                if(keyboard.digit7Key.wasPressedThisFrame)CameraRoom();
                if(keyboard.digit8Key.wasPressedThisFrame && atmosphere)atmosphere.ToggleBreeze();
                if(keyboard.digit9Key.wasPressedThisFrame && atmosphere)atmosphere.ToggleShafts();
                if(keyboard.digit0Key.wasPressedThisFrame)ToggleHair();
                if(keyboard.cKey.wasPressedThisFrame && activities)activities.Request("computer");
                if(keyboard.bKey.wasPressedThisFrame && activities)activities.Request("read");
                if(keyboard.vKey.wasPressedThisFrame)Idle();
                if(keyboard.nKey.wasPressedThisFrame && memo)memo.Toggle();
            }
#endif
            if (!actor) return;
            distanceTravelled += Vector3.Distance(previousPosition, actor.transform.position);
            previousPosition = actor.transform.position;
        }

        public void Walk()
        {
            if(activities && (activities.seated||activities.busy)){activities.Request("idle");StartCoroutine(WalkAfterStanding());return;}
            if (!actor || !hasWalk) { state = "Native walk clip not loaded"; return; }
            if (action != null) StopCoroutine(action);
            action = StartCoroutine(WalkRoute());
        }
        IEnumerator WalkAfterStanding(){while(activities.busy||activities.seated)yield return null;Walk();}
        public void HoldNativeMotion(){moving=false;if(action!=null){StopCoroutine(action);action=null;}}
        public void SetMotionTarget(Vector3 target){motionTarget=target;}

        IEnumerator WalkRoute()
        {
            state = "Walking - native clip";
            // Continuous rounded route: do not stop in Idle and swivel on the
            // same planted feet at each corner. Native root stride drives it.
            var points=new Vector3[96];int i=0;float nearest=float.MaxValue;
            for(int j=0;j<points.Length;j++)
            {
                float a=j*Mathf.PI*2/points.Length;
                points[j]=new Vector3(-.25f+1.35f*Mathf.Cos(a),groundY,-.72f+.43f*Mathf.Sin(a));
                float d=Vector3.Distance(actor.transform.position,points[j]);if(d<nearest){nearest=d;i=j;}
            }
            actor.speed=.82f;moving=true;actor.CrossFadeInFixedTime("Walk",.38f);
            while (true)
            {
                Vector3 target = points[i];
                motionTarget=target;
                while (Vector3.Distance(actor.transform.position, target) > .085f)
                {
                    var direction=target-actor.transform.position;direction.y=0;
                    if(direction.sqrMagnitude>.0001f)
                    {
                        Quaternion facing=Quaternion.LookRotation(direction);
                        float angle=Quaternion.Angle(actor.transform.rotation,facing);
                        actor.transform.rotation=Quaternion.RotateTowards(actor.transform.rotation,facing,turnSpeed*Time.deltaTime);
                        actor.speed=Mathf.Lerp(.58f,.82f,Mathf.InverseLerp(85,8,angle));
                    }
                    yield return null;
                }
                i = (i + 1) % points.Length;
            }
        }

        public void Idle()
        {
            if(activities && (activities.seated||activities.busy)){activities.Request("idle");return;}
            moving=false;
            if (action != null) { StopCoroutine(action); action = null; }
            if (actor && hasIdle){actor.speed=1;actor.CrossFadeInFixedTime("Idle", .38f);}
            state = actor ? (hasIdle ? "Resting - native clip" : "Native idle clip not loaded") : "Character asset pending";
        }

        public void ApplyNativeRootMotion(Animator source)
        {
            if(!moving)return;
            Vector3 delta=source.deltaPosition;delta.y=0;
            // Follow the route using the clip's measured stride distance. Clamp
            // to the waypoint so tiny lateral mocap drift cannot miss a corner.
            source.transform.position=Vector3.MoveTowards(source.transform.position,motionTarget,delta.magnitude);
        }

        public void Sit()
        {
            if(activities){activities.Request("computer");return;}
            if (!actor || !hasSit) { state = "Native sitting clip not loaded"; return; }
            if (action != null) { StopCoroutine(action); action = null; }
            actor.transform.SetPositionAndRotation(new Vector3(.8f, 0, .48f), Quaternion.identity);
            actor.CrossFade("Sit", .2f);
            state = "Sitting - native clip; fit review";
        }

        public void ToggleNight() => SetNight(!night);
        public void SetNight(bool value)
        {
            night = value;
            if (deskLight) deskLight.intensity = night ? 5.0f : 1.5f;
            if (fillLight) { fillLight.intensity = night ? .32f : .58f; fillLight.color = night ? new Color(.65f, .75f, 1f) : new Color(1f, .92f, .78f); }
            RenderSettings.ambientLight = night ? new Color(.30f, .31f, .36f) : new Color(.43f, .45f, .49f);
            if (roomCamera) roomCamera.backgroundColor = night ? new Color(.055f, .075f, .11f) : new Color(.31f, .40f, .48f);
            if(atmosphere)atmosphere.SetNight(night);
            PlayerPrefs.SetInt("ai3d-lofi-room-v1-night", night ? 1 : 0);
            PlayerPrefs.Save();
        }

        public void ToggleRain()
        {
            if (!rain) return;
            if (rain.isEmitting) rain.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear); else rain.Play();
        }

        public void ToggleMusic()
        {
            if (!music || !music.clip) { state = "Music asset pending"; return; }
            if (music.isPlaying) music.Pause(); else music.Play();
        }
        public void ToggleHair()
        {
            if(!actor)return;var hair=actor.GetComponent<LofiHairMotion>();
            if(hair)hair.enabledMotion=!hair.enabledMotion;
        }

        public void SetMemo(string value) { if(memo)memo.SetText(value);else{PlayerPrefs.SetString("ai3d-lofi-room-v1-memo",value);PlayerPrefs.Save();} }
        public string GetMemo() => memo?memo.text:PlayerPrefs.GetString("ai3d-lofi-room-v1-memo", "");
        public void CameraDesk() { roomCamera.transform.SetPositionAndRotation(new Vector3(3.7f, 2.35f, -3.9f), Quaternion.LookRotation(new Vector3(.65f, 1.0f, .95f) - new Vector3(3.7f, 2.35f, -3.9f))); roomCamera.orthographicSize = 2.45f; }
        public void CameraRoom() { roomCamera.transform.SetPositionAndRotation(new Vector3(6.8f, 4.9f, -8.5f), Quaternion.LookRotation(new Vector3(0, 1.05f, .3f) - new Vector3(6.8f, 4.9f, -8.5f))); roomCamera.orthographicSize = 3.55f; }
        public string GetStateJson() => JsonUtility.ToJson(new SampleState { frame = observedFrame, state = state, actorLoaded = actor != null, idleLoaded = hasIdle, walkLoaded = hasWalk, sitLoaded = hasSit, distance = distanceTravelled, nativeWalkSpeed = calibratedWalkSpeed, night = night });

        [System.Serializable] private sealed class SampleState { public int frame; public string state; public bool actorLoaded, idleLoaded, walkLoaded, sitLoaded, night; public float distance, nativeWalkSpeed; }

        void OnGUI()
        {
            // Also usable in Editor/native capture; the Web template provides
            // accessible Korean HTML controls over the same Unity scene.
            if (!showControls || Application.platform == RuntimePlatform.WebGLPlayer) return;
            float scale = Mathf.Max(1, Screen.width / 1400f);
            GUI.matrix = Matrix4x4.Scale(Vector3.one * scale);
            GUI.skin.font=uiFont;
            GUI.skin.button.fontSize=15;GUI.skin.label.fontSize=15;GUI.skin.box.fontSize=18;
            GUI.backgroundColor=new Color(.13f,.21f,.22f,.92f);
            GUI.Box(new Rect(20, 20, 350, 94), "얌얌코딩 · LOFI ROOM");
            GUI.Label(new Rect(36, 54, 320, 30), activities && (activities.busy||activities.seated)?activities.phase:moving?"산책 중":"잠깐 쉬어가기");
            GUI.Label(new Rect(36, 82, 320, 25), "C 아이맥 · B 독서 · V 일어나기");
            string[] labels = { "산책", "일어나기", "아이맥", "독서", "낮 / 밤", "비", "책상 보기", "방 전체", "음악", "장작 소리", "메모" };
            System.Action[] actions = { Walk, Idle, ()=>{if(activities)activities.Request("computer");}, ()=>{if(activities)activities.Request("read");}, ToggleNight, ToggleRain, CameraDesk, CameraRoom, ToggleMusic, ()=>{if(hearth)hearth.ToggleSound();},()=>{if(memo)memo.Toggle();} };
            for (int i = 0; i < labels.Length; i++) if (GUI.Button(new Rect(22 + i * 108, Screen.height / scale - 60, 102, 38), labels[i])) actions[i]();
            if(hearth)
            {
                GUI.Box(new Rect(Screen.width/scale-250,20,230,118),"방 안의 소리");
                GUI.Label(new Rect(Screen.width/scale-236,54,60,25),"로파이");
                if(music)music.volume=GUI.HorizontalSlider(new Rect(Screen.width/scale-165,64,126,22),music.volume,0,.6f);
                GUI.Label(new Rect(Screen.width/scale-236,88,60,25),"장작");
                if(hearth.crackle)hearth.crackle.volume=GUI.HorizontalSlider(new Rect(Screen.width/scale-165,98,126,22),hearth.crackle.volume,0,.7f);
            }
        }
    }
}
