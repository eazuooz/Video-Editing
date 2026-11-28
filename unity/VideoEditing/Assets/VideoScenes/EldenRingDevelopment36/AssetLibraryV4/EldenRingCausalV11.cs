using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        // A separate revision: unfinished lessons fail rather than silently using an old demonstration.
        Action<float> BuildCausalV11()
        {
            RenderSettings.fog = false;
            switch (episode)
            {
                case 1: return Streaming();
                case 2: return CausalFog();
                case 3: return FaceLayersV8();
                case 4: return Landmarks();
                case 5: return VistaV8();
                case 6: return CausalPrototype();
                case 7: return CausalTerrain();
                case 8: return CausalVertexTexture();
                case 9: return CausalCornerWalk();
                case 10: return CastV8();
                case 11: return CausalNavigation();
                case 12: return CausalPlaytest();
                case 13: return CausalAtmosphere();
                case 14: return ObservedTelegraph14();
                case 15: return CausalFlowers();
                case 16: return CausalLandmark();
                case 17: return ObservedDungeon17();
                case 18: return CausalHistory();
                case 19: return ObservedBoss19();
                case 20: return ObservedTraversal20();
                case 21: return ObservedTactics21();
                case 22: return ObservedDiscovery22();
                case 23: return CausalHandoff(false);
                case 24: return CausalDetour();
                case 25: return CausalExperience();
                case 26: return CausalWeight();
                case 27: return ObservedAcoustics27();
                case 28: return CausalChoir();
                case 29: return CausalProjection();
                case 30: return ObservedFramePacing();
                case 31: return ObservedComparison();
                case 32: return ObservedTargetModifier();
                case 33: return ObservedVisibilityOption();
                case 34: return ObservedProgressCurve();
                case 35: return ObservedRetry();
                case 36: return CausalCooperation();
                default: throw new InvalidOperationException("Causal scene not yet authored: " + episode);
            }
        }

        Action<float> CausalFog()
        {
            FrameCamera(V(7, 8, -12), V(0, .6f, 0), 4.1f);
            Floor("Ground", 0, 0, 10, 6, 0, Slate);
            var camera = Orb("View origin", V(-4, .8f, 0), .38f, Gold);
            var rock = Shape(PrimitiveType.Capsule, "Observed rock", V(3.7f, .8f, 0), V(1.1f, 1.6f, 1), Slate);
            var player = Pawn("Walking observer", V(-3.8f, .02f, -1.8f), Gold);
            var samples = new Transform[12];
            for (int i = 0; i < samples.Length; i++)
            {
                float x = -3.45f + i * .59f;
                samples[i] = Orb("Density sample " + i, V(x, .8f, 0), .21f, Paper);
                Bar("Ray segment " + i, V(x, .8f, 0), V(x + .43f, .8f, 0), .035f, Aqua);
            }
            var sum = Block("Accumulated opacity illustrative", V(-2, .18f, 2.3f), V(.01f, .25f, .35f), Aqua);
            var cursor = Ring("Current sample", V(-3.45f, .83f, 0), .28f, Gold);
            return t =>
            {
                int count = Mathf.Clamp(Mathf.FloorToInt(Range(t, .12f, .77f) * 12), 0, 12);
                float transmission = 1;
                for (int i = 0; i < samples.Length; i++)
                {
                    bool reached = i < count;
                    Tint(samples[i], reached ? Aqua : Slate);
                    if (reached) transmission *= Mathf.Exp(-(i >= 4 && i <= 7 ? .27f : .07f));
                }
                cursor.position = V(-3.45f + Mathf.Min(11, count) * .59f, .83f, 0);
                float opacity = 1 - transmission;
                sum.localScale = V(Mathf.Max(.01f, opacity * 5), .25f, .35f);
                sum.localPosition = V(-2.5f + opacity * 2.5f, .18f, 2.3f);
                Tint(rock, Color.Lerp(Slate, Paper, opacity));
                player.position = V(-3.8f + Range(t, .04f, .92f) * 1.7f, .02f, -1.8f);
                // The second shot contrasts near samples with a single illustrative far interval.
                if (Second)
                    for (int i = 8; i < samples.Length; i++)
                        samples[i].gameObject.SetActive(t < .45f || i == 10);
            };
        }

        Action<float> CausalTerrain()
        {
            Floor("Takeoff ground", -3, 0, 3.5f, 4.5f, 0, Slate);
            FrameCamera(V(7, 7, -11), V(0, .4f, 0), 4.15f);
            var player = Pawn("Landing test character", V(-3.8f, .02f, 0), Gold);
            var grid = new Vector3[25];
            for (int z = 0; z < 5; z++)
            for (int x = 0; x < 5; x++) grid[z * 5 + x] = V(.5f + x * .6f, .45f, -1.2f + z * .6f);
            var mesh = StudySurfaceV8("Editable landing mesh", grid, 5, Aqua);
            var dots = new Transform[25];
            for (int i = 0; i < 25; i++) dots[i] = Orb("Editable point " + i, grid[i] + V(0, .03f, 0), .09f, Gold);
            Ring("Fixed desired landing position", V(.20f, .51f, 0), .25f, Gold);
            var outline = new Transform[4];
            Vector3[] edges = {V(.1f,.49f,-.9f),V(2.7f,.49f,-.9f),V(2.7f,.49f,.9f),V(.1f,.49f,.9f)};
            for (int i = 0; i < 4; i++) outline[i] = Bar("Desired surface edge", edges[i], edges[(i+1)%4], .045f, Paper);
            var landing = Ring("Foot landing cue", V(.20f, .52f, 0), .18f, Aqua);
            return t =>
            {
                float edit = Second ? Range(t, .40f, .57f) : Range(t, .12f, .46f);
                for (int z = 0; z < 5; z++)
                for (int x = 0; x < 5; x++)
                {
                    int i = z * 5 + x;
                    float px = .5f + x * .6f;
                    // Shot 1: height edits retain grid x/z. Shot 2: edit the edge and face positions.
                    grid[i] = Second ? V(Mathf.Lerp(px, .1f + x * .65f, edit), .45f, Mathf.Lerp(-1.2f + z*.6f, -.9f+z*.45f, edit)) :
                        V(px, .45f + .23f * edit * (x == 0 ? 1 : 0), -1.2f + z * .6f);
                    dots[i].position = grid[i] + V(0, .03f, 0);
                }
                mesh.vertices = grid; mesh.RecalculateNormals(); mesh.RecalculateBounds();
                bool afterEdit = !Second || t >= .5f;
                float u = Second ? (afterEdit ? Range(t, .61f, .92f) : Range(t, .04f, .34f)) : Range(t, .54f, .88f);
                float xPos = Mathf.Lerp(-3.8f, .20f, u);
                float flight = Mathf.Clamp01((u - .36f) / .64f);
                float y = u < .36f ? .02f : .02f + .45f * flight + Mathf.Sin(flight * Mathf.PI) * 1.35f;
                if ((!Second || !afterEdit) && u > .96f) y -= .4f * Mathf.Clamp01((u-.96f)/.04f);
                player.position = V(xPos, y, 0);
                landing.gameObject.SetActive(Second && afterEdit && t > .90f);
            };
        }

        Action<float> CausalVertexTexture()
        {
            FrameCamera(V(2, 5, -10), V(-.2f, 1.1f, 0), 2.9f);
            var mesh = new Mesh { name = "Three-pose vertex texture demonstration" };
            owned.Add(mesh);
            const int arms = 5, points = 12, sides = 8, frames = 3;
            int vertices = arms * points * sides;
            var data = new Texture2D(vertices, frames, TextureFormat.RGBAFloat, false, true);
            data.name = "Actual stored xyz by vertex and time"; data.filterMode = FilterMode.Point;
            owned.Add(data);
            for (int f = 0; f < frames; f++)
            for (int arm = 0; arm < arms; arm++)
            for (int p = 0; p < points; p++)
            {
                float h = p / (float)(points - 1);
                float phase = f * Mathf.PI * .66f;
                float x = -3.3f + arm * .62f + Mathf.Sin(phase + arm * .8f + h) * h * .36f;
                float y = .3f + h * 2.2f;
                float radius = p >= 9 ? .16f : Mathf.Lerp(.18f,.105f,h);
                for (int side = 0; side < sides; side++)
                {
                    float angle = side * Mathf.PI * 2 / sides;
                    data.SetPixel(arm * points * sides + p * sides + side, f,
                        new Color(x + Mathf.Cos(angle)*radius, y,
                            Mathf.Cos(phase+h)*h*.22f + Mathf.Sin(angle)*radius*(p>=9?.5f:1),1));
                }
            }
            data.Apply();
            var tris = new List<int>();
            for (int arm=0;arm<arms;arm++) for(int p=0;p<points-1;p++) for(int side=0;side<sides;side++)
            {
                int i=arm*points*sides+p*sides+side;
                int j=arm*points*sides+p*sides+(side+1)%sides;
                tris.AddRange(new[]{i,j,i+sides,j,j+sides,i+sides});
            }
            var obj=Group("Reconstructed arms",Vector3.zero);
            obj.gameObject.AddComponent<MeshFilter>().sharedMesh=mesh;
            obj.gameObject.AddComponent<MeshRenderer>().sharedMaterial=Paint(new Color(.72f,.43f,.34f));
            var positions=new Vector3[vertices]; mesh.vertices=positions;mesh.triangles=tris.ToArray();
            var cells=new Transform[3,8];
            int[] representedVertices={88,0,160,248,320,408,440,479};
            for(int row=0;row<3;row++) for(int col=0;col<8;col++)
                cells[row,col]=Block("Data cell " + row + " " + col,V(.75f+col*.35f,.25f,1.25f-row*.5f),V(.28f,.18f,.35f),Slate);
            var tracked=Orb("One reconstructed vertex",Vector3.zero,.16f,Gold);
            var readLink=Bar("Read selected point position from current texture row",Vector3.zero,Vector3.one,.035f,Gold);
            var rowMarker=Ring("Currently read texture position",V(.75f,.4f,1.25f),.23f,Gold);
            var fingers=new Transform[arms,5];
            for(int a=0;a<arms;a++)for(int f=0;f<5;f++)
                fingers[a,f]=Shape(PrimitiveType.Capsule,"Hand finger",Vector3.zero,V(.055f,.16f,.055f),new Color(.72f,.43f,.34f));
            var boneBars=new Transform[arms*3];
            for(int a=0;a<arms;a++) for(int j=0;j<3;j++)
                boneBars[a*3+j]=Bar("Bone setup comparison",V(-3.3f+a*.62f,.3f+j*.7f,0),V(-3.3f+a*.62f,1+j*.7f,0),.055f,Gold);
            return t=>
            {
                float clock=Range(t,.18f,.9f)*(frames-1);
                int frame=Mathf.Min(frames-1,Mathf.FloorToInt(clock));
                int next=Mathf.Min(frames-1,frame+1);
                for(int i=0;i<vertices;i++){
                    Color v=Color.Lerp(data.GetPixel(i,frame),data.GetPixel(i,next),clock-frame);
                    positions[i]=V(v.r,v.g,v.b);
                }
                mesh.triangles=(!Second && t<.18f)?tris.GetRange(0,tris.Count/arms).ToArray():tris.ToArray();
                mesh.vertices=positions;mesh.RecalculateNormals();mesh.RecalculateBounds();
                tracked.position=positions[(points-1)*sides];
                for(int a=0;a<arms;a++)for(int f=0;f<5;f++)
                {
                    int v=a*points*sides+(points-1)*sides;
                    Vector3 palm=(positions[v]+positions[v+4])*.5f;
                    fingers[a,f].position=palm+V((f-2)*.065f,.16f-(f==0?.09f:0),0);
                    fingers[a,f].rotation=Quaternion.Euler(0,0,(2-f)*6);
                    fingers[a,f].gameObject.SetActive(Second || t>=.18f || a==0);
                }
                int active=Mathf.Min(2,frame*3/frames);
                for(int row=0;row<3;row++)for(int col=0;col<8;col++){
                    Color value=data.GetPixel(representedVertices[col],row);
                    Color encoded=new Color((value.r+4)/8,value.g/3,(value.b+1)/2);
                    Tint(cells[row,col],row==active?encoded:Color.Lerp(Slate,encoded,.25f));
                }
                rowMarker.position=V(.75f,.4f,1.25f-active*.5f);
                bool reading=Second&&t>=.18f;
                readLink.gameObject.SetActive(reading);rowMarker.gameObject.SetActive(reading);
                Segment(readLink,rowMarker.position,tracked.position,.035f);
                for(int i=0;i<boneBars.Length;i++)boneBars[i].gameObject.SetActive(!Second && t<.48f && (t>.18f||i<3));
            };
        }

        static List<Vector3> CausalRoute(Vector2Int from, Vector2Int to)
        {
            var queue=new Queue<Vector2Int>(); var parent=new Dictionary<Vector2Int,Vector2Int>();
            queue.Enqueue(from);parent[from]=from;
            Vector2Int[] steps={Vector2Int.up,Vector2Int.right,Vector2Int.down,Vector2Int.left};
            while(queue.Count>0)
            {
                var here=queue.Dequeue();if(here==to)break;
                foreach(var d in steps)
                {
                    var next=here+d;
                    if(Mathf.Abs(next.x)>4||Mathf.Abs(next.y)>3|| (Mathf.Abs(next.x)<=1&&Mathf.Abs(next.y)<=1)||parent.ContainsKey(next))continue;
                    parent[next]=here;queue.Enqueue(next);
                }
            }
            if(!parent.ContainsKey(to))throw new InvalidOperationException("No model route");
            var result=new List<Vector3>();var node=to;
            while(node!=from){result.Add(V(node.x,.03f,node.y));node=parent[node];}
            result.Add(V(from.x,.03f,from.y));result.Reverse();return result;
        }

        Action<float> CausalNavigation()
        {
            Floor("Walkable field",0,0,10,7,0,Slate);
            var rock=Group("Actual path obstacle",V(0,0,0));Attach("rock",rock,V(2.7f,1.9f,2.7f),true);
            var player=Pawn("Current target",V(3,.03f,-2),Gold);
            var enemy=Pawn("Following enemy",V(-4,.03f,0),Red);
            var tiles=new List<Transform>();
            for(int x=-4;x<=4;x++)for(int z=-3;z<=3;z++)
                if(!(Mathf.Abs(x)<=1&&Mathf.Abs(z)<=1))tiles.Add(Block("Walkable cell",V(x,.015f,z),V(.85f,.025f,.85f),Aqua));
            var a=CausalRoute(new Vector2Int(-4,0),new Vector2Int(3,-2));
            var b=CausalRoute(new Vector2Int(-4,0),new Vector2Int(3,2));
            var lines=new Transform[20];for(int i=0;i<lines.Length;i++)lines[i]=Bar("Computed connection",Vector3.zero,Vector3.one,.07f,Gold);
            return t=>
            {
                bool routed=Second||t>.44f;bool changed=Second&&t>.5f;
                player.position=V(3,.03f,changed?2:-2);
                foreach(var tile in tiles)tile.gameObject.SetActive(routed);
                var path=changed?b:a;
                for(int i=0;i<lines.Length;i++)
                {
                    lines[i].gameObject.SetActive(routed&&i<path.Count-1);
                    if(i<path.Count-1)Segment(lines[i],path[i]+V(0,.09f,0),path[i+1]+V(0,.09f,0),.07f);
                }
                if(!routed)enemy.position=Vector3.Lerp(V(-4,.03f,0),V(-1.6f,.03f,-.68f),Range(t,.04f,.34f));
                else
                {
                    float u=Second?Range(t,changed?.54f:.04f,changed?.96f:.46f):Range(t,.5f,.96f);
                    float f=u*(path.Count-1);int i=Mathf.Min(path.Count-2,Mathf.FloorToInt(f));
                    enemy.position=Vector3.Lerp(path[i],path[i+1],f-i);
                }
            };
        }

        Action<float> CausalCornerWalk()
        {
            var stone=new Color32(151,143,121,255);
            Floor("Open approach courtyard",0,-4.2f,8,4.4f,0,Slate);
            Floor("First narrow corridor",0,-.5f,2.2f,3.3f,0,stone);
            Floor("Corner and ascending corridor",2,1,4.4f,2.2f,0,stone);
            for(int i=0;i<20;i++)
                Block("Ascending corner paving",V(.1f+i*.2f,(i+1)*.045f,1),V(.22f,(i+1)*.09f,2.2f),stone);
            Floor("High viewing terrace",5.2f,1,2.8f,4,1.8f,stone);
            Floor("Visible lower landing",7.7f,1,2,3,-.25f,Aqua);
            Floor("Ground below",3,1,14,12,-1,Slate);
            Block("Left opaque corridor wall",V(-1.22f,1.3f,-.45f),V(.24f,2.6f,3.8f),stone);
            Block("Right approach wall",V(1.22f,1.3f,-1.55f),V(.24f,2.6f,1.5f),stone);
            Block("Blind corner wall hides next space",V(1.35f,1.8f,2.22f),V(5.4f,3.6f,.24f),stone);
            Block("Inner wall after right turn",V(2.6f,1.8f,-.22f),V(2.8f,3.6f,.24f),stone);
            Attach("house",Group("Distant destination visible in courtyard",V(-3.8f,0,-.5f)),V(2,2.7f,2),true);
            var player=Pawn("Grounded actor following a ninety degree corner",V(0,0,-5.5f),Gold);
            var actor=walkthroughActors[walkthroughActors.Count-1];
            actor.GroundHeight=point=>Mathf.Clamp(point.x,0,4)*.45f;
            Vector3 At(float t)
            {
                if(t<.55f)return V(0,0,Mathf.Lerp(-5.5f,1,Range(t,0,.55f)));
                float x=Mathf.Lerp(0,6,Range(t,.55f,.96f));
                return V(x,Mathf.Clamp(x,0,4)*.45f,1);
            }
            return t=>
            {
                var p=At(t);player.position=p;
                var behind=At(Mathf.Max(0,t-.12f));
                if((p-behind).sqrMagnitude<.05f)behind=p+V(0,0,-1.6f);
                var look=At(Mathf.Min(.96f,t+.10f))+V(0,.85f,0);
                look=Vector3.Lerp(look,V(7.7f,-.25f,1),Range(t,.85f,.99f));
                var cameraPoint=behind+V(0,1.8f,0);
                view.orthographic=false;view.fieldOfView=62;
                view.transform.SetPositionAndRotation(cameraPoint,Quaternion.LookRotation(look-cameraPoint));
            };
        }

        Action<float> CausalPlaytest()
        {
            Floor("Courtyard",0,0,10,7,0,Slate);
            for(int i=0;i<2;i++){var tower=Group("Test tower " + i,V(i==0?-2.8f:2.8f,0,1));Attach("tower",tower,V(2,2,2),true);}
            var bridge=Block("Proposed playable connection",V(0,1.65f,1),V(4,.24f,1),Aqua);
            var player=Pawn("Human test-play actor",V(-2.8f,1.8f,1),Gold);
            for(int i=0;i<9;i++)
                Block("Visible tower approach step " + i,V(-4.7f+i*.22f,(i+1)*.10f,1),V(.24f,(i+1)*.20f,1),Slate);
            var desire=Bar("Proposed destination",V(-2.8f,2.2f,1),V(2.8f,2.2f,1),.07f,Gold);
            var problem=Ring("Recorded problem location",V(2.8f,.05f,-1.5f),.4f,Red);
            return t=>
            {
                if(!Second)
                {
                    bridge.gameObject.SetActive(t>.48f);desire.gameObject.SetActive(t>.16f&&t<.55f);problem.gameObject.SetActive(false);
                    float climb=Range(t,0,.16f);
                    player.position=t<.16f ? V(Mathf.Lerp(-4.8f,-2.8f,climb),Mathf.Ceil(climb*9)*.2f,1) :
                        V(Mathf.Lerp(-2.8f,2.8f,Range(t,.57f,.92f)),1.8f,1);
                }
                else
                {
                    bridge.gameObject.SetActive(true);desire.gameObject.SetActive(false);
                    player.position=V(Mathf.Lerp(-3.8f,2.8f,Range(t,.04f,.72f)),.03f,-1.5f);
                    problem.gameObject.SetActive(t>.72f);
                }
            };
        }
    }
}
