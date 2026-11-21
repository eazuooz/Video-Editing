using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        Action<float> BuildRenderingAndWorld()
        {
            switch (episode)
            {
                case 1: return Streaming();
                case 2: return Fog();
                case 3: return Surface();
                case 4: return Landmarks();
                case 5: return Vista();
                case 6: return Prototype();
                case 7: return Terrain();
                case 8: return VertexPlayback();
                case 9: return Blockout();
                case 10: return EventTimeline();
                case 11: return Navigation();
                case 12: return MapTrace();
                default: throw new ArgumentOutOfRangeException(nameof(episode));
            }
        }

        Action<float> Streaming()
        {
            FrameCamera(V(5, 10, -13), V(0, 0, 0), 4.45f);
            var cells = new Transform[5, 3];
            for (int x = 0; x < 5; x++)
                for (int z = 0; z < 3; z++)
                    cells[x, z] = Block("Streaming cell", V((x - 2) * 1.8f, .02f, (z - 1) * 1.8f),
                        V(1.69f, .11f, 1.69f), Slate);
            var player = Pawn("Player", V(-4, .12f, 0), Gold);
            var bounds = Ring("Neighbourhood", V(-4, .15f, 0), 1.65f, Aqua);
            Route(Paper, V(-4.1f, .10f, -.35f), V(4.1f, .10f, -.35f));
            return t =>
            {
                float x = Mathf.Lerp(-3.8f, 3.8f, Ease(t));
                player.localPosition = V(x, .12f, .32f * Mathf.Sin(t * 5));
                bounds.localPosition = V(x, .16f, 0);
                int cell = Mathf.Clamp(Mathf.RoundToInt(x / 1.8f) + 2, 0, 4);
                for (int i = 0; i < 5; i++)
                    for (int z = 0; z < 3; z++)
                        Tint(cells[i, z], i == cell && z == 1 ? Gold : Mathf.Abs(i - cell) <= 1 ? Aqua : Slate);
                if (Second) FrameCamera(V(5 + x * .8f, 6.4f, -13), V(x * .25f, .05f, 0), 4.45f);
            };
        }

        Action<float> Fog()
        {
            FrameCamera(V(5, 5, -14), V(0, 1.15f, .2f), 4.25f);
            for (int i = 0; i < 7; i++)
                Landmark("Depth landmark", V(-4.2f + i * 1.4f, 0, i * .67f - 2), 1 + .22f * i, Slate);
            var fog = Shape(PrimitiveType.Quad, "Raymarched test medium", V(0, 1.5f, -2), V(8.8f, 4.2f, 1), Paper);
            var fogMaterial = new Material(Shader.Find("Yamyam/EldenLibraryLessonFog"));
            owned.Add(fogMaterial);
            fog.GetComponent<Renderer>().sharedMaterial = fogMaterial;
            var ray = Bar("Sample ray", V(-4, .27f, -2.8f), V(4, .27f, -2.8f), .058f, Gold);
            var points = new Transform[14];
            for (int i = 0; i < points.Length; i++)
                points[i] = Orb("Density sample", V(-3.9f + i * .6f, .3f, -2.8f), .25f, i < 8 ? Aqua : Gold);
            return t =>
            {
                fogMaterial.SetFloat("_Progress", t);
                fogMaterial.SetFloat("_Layered", Second ? 1 : 0);
                var facing = cameraFacing(fog.position);
                fog.rotation = facing;
                Segment(ray, V(-4, .3f, -2.8f), V(Mathf.Lerp(-3.95f, 4.25f, t), .3f, -2.8f), .058f);
                for (int i = 0; i < points.Length; i++)
                    points[i].gameObject.SetActive(i <= t * points.Length && (!Second || i < 8 || i == 13));
            };
        }

        Quaternion cameraFacing(Vector3 p) => Quaternion.LookRotation(p - view.transform.position);

        Action<float> Surface()
        {
            FrameCamera(V(0, 2.8f, -15), V(0, 1.42f, 0), 4.1f);
            var left = Orb("Reference surface", V(-2.3f, 1.6f, 0), 3.25f, Paper);
            var right = Orb("Masked normal", V(2.3f, 1.6f, 0), 3.25f, Paper);
            var material = new Material(Shader.Find("Yamyam/EldenLibraryLessonSurface"));
            var reference = new Material(material);
            owned.Add(material);
            owned.Add(reference);
            left.GetComponent<Renderer>().sharedMaterial = reference;
            right.GetComponent<Renderer>().sharedMaterial = material;
            var beacon = Orb("Moving light direction", V(-2.8f, 4, -1.3f), .35f, Gold);
            return t =>
            {
                float x = Mathf.Lerp(-3.6f, 3.6f, Ease(t));
                beacon.localPosition = V(x, 3.7f, -1.4f);
                reference.SetFloat("_LightSide", x);
                reference.SetFloat("_Mode", Second ? 2 : 0);
                material.SetFloat("_LightSide", x);
                material.SetFloat("_Mode", 1);
            };
        }

        Action<float> Landmarks()
        {
            var player = Pawn("Traveler", V(0, 0, -3.1f), Gold);
            Landmark("Distant castle", V(.4f, 0, 3.05f), 2.42f, Aqua);
            Landmark("Mid-distance chapel", V(-3, 0, .9f), 1.55f, Gold);
            Landmark("Close doorway", V(2.6f, 0, -.1f), .92f, Paper);
            var arrow = Bar("Current goal ray", V(0, .10f, -3.1f), V(.4f, .1f, 3.05f), .09f, Gold);
            Route(Aqua, V(0, .07f, -3.1f), V(.2f, .07f, .2f), V(.4f, .07f, 3));
            if (Second) Route(Paper, V(.2f, .08f, -.6f), V(1.3f, .08f, -.42f), V(2.7f, .08f, 0));
            return t =>
            {
                var p = Vector3.Lerp(V(0, 0, -3.1f), V(.15f, 0, -.54f), Range(t, 0, .49f));
                Vector3 goal = t < .48f ? V(.4f, .1f, 3) : Second ? V(2.6f, .1f, -.1f) : V(-3, .1f, .9f);
                player.localPosition = Vector3.Lerp(p, V(goal.x, 0, goal.z), .77f * Range(t, .50f, .90f));
                Segment(arrow, player.localPosition + V(0, .16f, 0), goal, .085f);
            };
        }

        Action<float> Vista()
        {
            FrameCamera(V(0, 2.2f, -11), V(0, 1.3f, 1), 3.25f);
            Landmark("Distant outline", V(.72f, 0, 2.6f), 2.65f, Gold);
            for (int i = 0; i < 6; i++)
                Block("Open field line", V(0, .022f, i - 3), V(9.8f, .035f, .07f), Slate);
            var cover = Group("Foreground tree set", V(0, 0, -1.6f));
            for (int i = 0; i < 5; i++)
            {
                var tree = Group("Near tree", V((i - 2) * 1.38f, 0, -1.9f));
                tree.SetParent(cover, true);
                Block("Trunk", V(0, .85f, 0), V(.21f, 1.7f, .19f), Slate, tree);
                Orb("Canopy", V(0, 1.73f, 0), 1.65f, Aqua, tree);
            }
            var viewer = Pawn("Viewpoint", V(0, 0, -3.2f), Paper);
            return t =>
            {
                float clear = Second ? Range(t, .08f, .66f) : Range(t, .13f, .65f);
                cover.localPosition = V(0, Second ? -2.8f * clear : -2.5f * (1 - clear), -1.6f);
                viewer.localPosition = V(.45f * t, 0, -3.2f);
                if (Second) FrameCamera(V(-.26f + .6f * t, 2.2f, -11), V(.3f, 1.28f, 1), 3.25f);
            };
        }

        Action<float> Prototype()
        {
            var tiles = new Transform[3];
            for (int i = 0; i < 3; i++)
                tiles[i] = Block("Reusable greybox tile", V(-3.5f + i * 3.5f, .12f, 0), V(3.32f, .28f, 4.8f), i == 1 ? Slate : Paper);
            var rider = Pawn("Prototype traversal character", V(-4.4f, .27f, 0), Gold);
            var horse = Mount(V(-3.8f, .32f, 0));
            var memory = new Transform[3];
            for (int i = 0; i < 3; i++) memory[i] = Block("Tile data active", V(-3.5f + i * 3.5f, .22f, 1.9f), V(1.02f, .20f, .34f), Blue);
            return t =>
            {
                float x = Mathf.Lerp(-4.6f, 4.6f, Ease(t));
                float hop = !Second && t > .29f && t < .65f ? .75f * Mathf.Sin((t - .29f) / .36f * Mathf.PI) : 0;
                bool mounted = !Second && t > .71f;
                rider.localPosition = V(x, .29f + hop + (mounted ? .38f : 0), -.18f);
                horse.localPosition = V(x, .48f, -.18f);
                horse.gameObject.SetActive(mounted);
                for (int i = 0; i < 3; i++)
                {
                    memory[i].gameObject.SetActive(Second);
                    Tint(memory[i], Mathf.Abs(x - tiles[i].localPosition.x) < 2.29f ? Aqua : Slate);
                }
            };
        }

        MeshGrid MakeTerrain(string name, float offset, bool meshTool)
        {
            const int n = 12;
            var go = Group(name, V(offset, .24f, 0));
            var mesh = new Mesh { name = name };
            owned.Add(mesh);
            var grid = new MeshGrid(mesh, n);
            go.gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.gameObject.AddComponent<MeshRenderer>().sharedMaterial = Paint(meshTool ? Aqua : Gold);
            return grid;
        }

        sealed class MeshGrid
        {
            readonly Mesh target;
            readonly Vector3[] points;
            readonly int n;
            public MeshGrid(Mesh target, int n)
            {
                this.target = target;
                this.n = n;
                points = new Vector3[n * n];
                var indices = new List<int>();
                for (int z = 0; z < n - 1; z++)
                    for (int x = 0; x < n - 1; x++)
                    {
                        int p = x + z * n;
                        indices.AddRange(new[]{p, p + n, p + 1, p + 1, p + n, p + n + 1});
                    }
                target.vertices = points;
                target.triangles = indices.ToArray();
                target.MarkDynamic();
            }
            public void Shape(float t, bool directEdge)
            {
                for (int z = 0; z < n; z++)
                    for (int x = 0; x < n; x++)
                    {
                        float a = (float)x / (n - 1), b = (float)z / (n - 1);
                        float ridge = directEdge ? (a > .52f ? .9f : 0) :
                            .92f * Mathf.Exp(-7 * ((a - .64f) * (a - .64f) + (b - .5f) * (b - .5f)));
                        float edge = directEdge && x == n / 2 ? -.22f * t * Mathf.Sin(b * Mathf.PI) : 0;
                        points[x + z * n] = V(a * 4 - 2 + edge, t * ridge, b * 4.8f - 2.4f);
                    }
                target.vertices = points;
                target.RecalculateNormals();
                target.RecalculateBounds();
            }
        }

        Action<float> Terrain()
        {
            FrameCamera(V(5, 8.25f, -12.6f), V(0, .15f, 0), 4.25f);
            var left = MakeTerrain("Height values on a regular grid", -2.48f, false);
            var right = MakeTerrain("Edited polygon surface", 2.48f, true);
            var point = Orb("Editable mesh control point", V(2.48f, .36f, 0), .33f, Paper);
            return t =>
            {
                left.Shape(Range(t, .05f, .64f), false);
                right.Shape(Range(t, Second ? .12f : .54f, .91f), true);
                point.localPosition = V(2.62f - .22f * t, .36f + .78f * Range(t, .40f, .82f), 0);
                point.gameObject.SetActive(Second || t > .53f);
            };
        }

        Action<float> VertexPlayback()
        {
            const int width = 10, rows = 8;
            var pixels = new Texture2D(width, rows, TextureFormat.RGBAFloat, false, true) { filterMode = FilterMode.Point };
            owned.Add(pixels);
            var joints = new Transform[width];
            var links = new Transform[width - 1];
            var normalArrows = new Transform[width];
            for (int i = 0; i < width; i++)
            {
                joints[i] = Orb("Vertex", Vector3.zero, .26f, Aqua);
                normalArrows[i] = Bar("Decoded vertex normal", Vector3.zero, Vector3.up, .035f, Paper);
                if (i > 0) links[i - 1] = Bar("Deforming edge", Vector3.zero, Vector3.right, .10f, Aqua);
            }
            var texels = new Transform[rows];
            for (int row = 0; row < rows; row++)
            {
                texels[row] = Block("Stored texture row", V(2.9f, .16f, (row - 3.5f) * .5f), V(3.3f, .15f, .41f), Slate);
                for (int i = 0; i < width; i++)
                {
                    float phase = i * .78f + row * .7f;
                    pixels.SetPixel(i, row, new Color(-.42f * .78f * Mathf.Cos(phase), .42f * Mathf.Sin(phase),
                        .25f * Mathf.Cos(i + row), 1));
                }
            }
            pixels.Apply();
            return t =>
            {
                int frame = Mathf.Clamp(Mathf.FloorToInt(t * rows * 1.8f), 0, 13) % rows;
                for (int r = 0; r < rows; r++) Tint(texels[r], r == frame ? Gold : Slate);
                for (int i = 0; i < width; i++)
                {
                    Color data = pixels.GetPixel(i, frame);
                    joints[i].localPosition = V(-4.7f + i * .48f, 1.2f + data.g, -.7f + data.b);
                    normalArrows[i].gameObject.SetActive(Second);
                    Segment(normalArrows[i], joints[i].localPosition, joints[i].localPosition + V(data.r, data.a, 0).normalized * .42f, .038f);
                    if (i > 0) Segment(links[i - 1], joints[i - 1].localPosition, joints[i].localPosition, .10f);
                }
            };
        }

        Action<float> Blockout()
        {
            var bases = new Transform[8];
            var detailed = new Transform[8];
            for (int i = 0; i < 8; i++)
            {
                var p = V(-4.4f + i * 1.24f, 0, Mathf.Sin(i * .8f) * 2);
                float height = .55f + .25f * (i % 3);
                bases[i] = Block("Planning block", p + V(0, height * .5f, 0), V(1.12f, height, 2.0f), Slate);
                detailed[i] = Block("Local facade", p + V(0, height, 0), V(.85f, .52f, .25f), i % 2 == 0 ? Aqua : Gold);
            }
            var player = Pawn("Route reader", V(-4, 0, -2.7f), Paper);
            return t =>
            {
                for (int i = 0; i < bases.Length; i++)
                {
                    float y = Range(t, i * .041f, .34f + i * .041f);
                    var loc = bases[i].localPosition;
                    bases[i].localPosition = V(loc.x, .2f + y * .36f, loc.z);
                    detailed[i].gameObject.SetActive(t > (Second ? .15f : .49f) + i * .046f);
                }
                player.localPosition = V(Mathf.Lerp(-4.2f, 4.2f, Ease(t)), 0, -2.45f + .55f * Mathf.Sin(t * 6));
            };
        }

        Action<float> EventTimeline()
        {
            var caster = Pawn("Caster", V(-1.6f, 0, .8f), Aqua);
            var hand = caster.Find("Right sleeve");
            var flash = Orb("Particle burst at event", V(1, 1.15f, .8f), .4f, Gold);
            var destination = Ring("Effect area", V(2, .08f, .8f), .78f, Gold);
            Route(Slate, V(-4.3f, .15f, -1.8f), V(4.3f, .15f, -1.8f));
            for (int i = 0; i < 9; i++) Block("Frame marker", V(-4.1f + i * 1.02f, .18f, -1.8f), V(.05f, .16f, .29f), Paper);
            var key = Block("Event cue", V(0, .3f, -1.8f), V(.22f, .6f, .26f), Aqua);
            var playback = Orb("Timeline playhead", V(-4.1f, .38f, -1.8f), .32f, Gold);
            return t =>
            {
                float point = Second ? Mathf.Lerp(.40f, .56f, Range(t, 0, .24f)) : .50f;
                var launch = Range(t, point, point + .16f);
                hand.localRotation = Quaternion.Euler(-115 * Ease(t / point), 0, 14);
                key.localPosition = V(Mathf.Lerp(-4.1f, 4.1f, point), .3f, -1.8f);
                playback.localPosition = V(Mathf.Lerp(-4.1f, 4.1f, t), .38f, -1.8f);
                flash.localPosition = V(Mathf.Lerp(-1.15f, 1.9f, launch), 1.35f, .8f);
                flash.gameObject.SetActive(t >= point && t < point + .21f);
                destination.gameObject.SetActive(t >= point + .13f);
            };
        }

        Action<float> Navigation()
        {
            Block("Walkable west", V(-3.1f, .04f, 0), V(3.8f, .17f, 4.65f), Aqua);
            Block("Walkable east", V(2.9f, .42f, 0), V(3.7f, .8f, 4.65f), Aqua);
            Block("Sidewalk alternative", V(0, .03f, 2.15f), V(2.5f, .2f, .55f), Slate);
            var pawn = Pawn("Agent", V(-4, .18f, -.75f), Gold);
            if (!Second) Route(Gold, V(-4, .17f, -.75f), V(-1.14f, .17f, -.75f), V(1.1f, .87f, -.75f), V(4, .87f, -.75f));
            else Route(Gold, V(-4, .18f, -.75f), V(-1.6f, .18f, 2.15f), V(1.1f, .86f, 2.15f), V(4, .86f, -.75f));
            return t =>
            {
                var x = Mathf.Lerp(-4.1f, 4.1f, Ease(t));
                float rise = Range(t, .36f, .64f);
                float y = .18f + .68f * rise + (Second ? 0 : .86f * Mathf.Sin(rise * Mathf.PI));
                float z = Second ? -.75f + 2.9f * Mathf.Sin(Mathf.PI * Range(t, .10f, .90f)) : -.75f;
                pawn.localPosition = V(x, y, z);
            };
        }

        Action<float> MapTrace()
        {
            var probes = new[] { V(-3.9f, .11f, -2), V(2, .11f, -2), V(2, .11f, 1.4f), V(-3, .11f, 1.4f) };
            Route(Slate, probes);
            var rover = Orb("Data collection probe", probes[0], .38f, Gold);
            var pin = Ring("Coordinate recorded with event", probes[2], .54f, Red);
            for (int x = -4; x <= 4; x++)
                for (int z = -2; z <= 2; z++)
                    Block("World map cell", V(x, .012f, z), V(.84f, .10f, .84f), Slate);
            return t =>
            {
                float phase = t * 3;
                int leg = Mathf.Min(2, (int)phase);
                rover.localPosition = Vector3.Lerp(probes[leg], probes[leg + 1], phase - leg) + V(0, .23f, 0);
                pin.gameObject.SetActive(Second || t > .58f);
                pin.localScale = Vector3.one * (1 + .21f * Pulse(t * 3));
                if (Second)
                {
                    Vector3 target = probes[2] * Range(t, .38f, .88f);
                    FrameCamera(V(5, 10, -13) + target, target, Mathf.Lerp(4.35f, 2.1f, Range(t, .40f, .90f)));
                }
            };
        }
    }
}
