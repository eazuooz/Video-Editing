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
            switch (episode)
            {
                case 2: return CausalFog();
                case 7: return CausalTerrain();
                case 8: return CausalVertexTexture();
                case 11: return CausalNavigation();
                case 12: return CausalPlaytest();
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
            FrameCamera(V(7, 7, -11), V(0, .5f, 0), 4.15f);
            var mesh = new Mesh { name = "Three-pose vertex texture demonstration" };
            owned.Add(mesh);
            const int arms = 5, points = 12, sides = 8, frames = 32;
            int vertices = arms * points * sides;
            var data = new Texture2D(vertices, frames, TextureFormat.RGBAFloat, false, true);
            data.name = "Actual stored xyz by vertex and time"; data.filterMode = FilterMode.Point;
            owned.Add(data);
            for (int f = 0; f < frames; f++)
            for (int arm = 0; arm < arms; arm++)
            for (int p = 0; p < points; p++)
            {
                float h = p / (float)(points - 1);
                float phase = f / (float)(frames - 1) * Mathf.PI * 2;
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
            for(int row=0;row<3;row++) for(int col=0;col<8;col++)
                cells[row,col]=Block("Data cell " + row + " " + col,V(.75f+col*.35f,.25f,1.25f-row*.5f),V(.28f,.18f,.35f),Slate);
            var tracked=Orb("One reconstructed vertex",Vector3.zero,.16f,Gold);
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
                for(int i=0;i<vertices;i++){Color v=data.GetPixel(i,frame);positions[i]=V(v.r,v.g,v.b);}
                mesh.vertices=positions;mesh.RecalculateNormals();mesh.RecalculateBounds();
                tracked.position=positions[(points-1)*sides];
                for(int a=0;a<arms;a++)for(int f=0;f<5;f++)
                {
                    int v=a*points*sides+(points-1)*sides;
                    Vector3 palm=(positions[v]+positions[v+4])*.5f;
                    fingers[a,f].position=palm+V((f-2)*.065f,.16f-(f==0?.09f:0),0);
                    fingers[a,f].rotation=Quaternion.Euler(0,0,(2-f)*6);
                }
                int active=Mathf.Min(2,frame*3/frames);
                for(int row=0;row<3;row++)for(int col=0;col<8;col++)Tint(cells[row,col],row==active?Aqua:Slate);
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

        Action<float> CausalPlaytest()
        {
            Floor("Courtyard",0,0,10,7,0,Slate);
            for(int i=0;i<2;i++){var tower=Group("Test tower " + i,V(i==0?-2.8f:2.8f,0,1));Attach("tower",tower,V(2,2,2),true);}
            var bridge=Block("Proposed playable connection",V(0,1.65f,1),V(4,.24f,1),Aqua);
            var player=Pawn("Human test-play actor",V(-2.8f,1.8f,1),Gold);
            var desire=Bar("Proposed destination",V(-2.8f,2.2f,1),V(2.8f,2.2f,1),.07f,Gold);
            var problem=Ring("Recorded problem location",V(2.8f,.05f,-1.5f),.4f,Red);
            return t=>
            {
                if(!Second)
                {
                    bridge.gameObject.SetActive(t>.48f);desire.gameObject.SetActive(t>.16f&&t<.55f);problem.gameObject.SetActive(false);
                    player.position=V(Mathf.Lerp(-2.8f,2.8f,Range(t,.57f,.92f)),1.8f,1);
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
