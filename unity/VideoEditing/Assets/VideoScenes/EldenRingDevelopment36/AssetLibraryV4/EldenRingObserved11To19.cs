using System;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        static readonly Color PathStone11 = new Color32(154, 144, 117, 255);
        static readonly Color WallStone11 = new Color32(94, 112, 110, 255);
        static readonly Color FieldGrass11 = new Color32(67, 91, 63, 255);
        static readonly Color ClearSky11 = new Color32(126, 153, 157, 255);

        Action<float> BuildObserved11To19()
        {
            switch (episode)
            {
                case 11: return ObservedNavMesh11();
                case 12: return ObservedProbes12();
                case 13: return ObservedAtmosphere13();
                case 14: return ObservedTelegraph14();
                case 15: return ObservedFlowers15();
                case 16: return ObservedLandmark16();
                case 17: return ObservedDungeon17();
                case 18: return ObservedHistory18();
                case 19: return ObservedBoss19();
                default: throw new ArgumentOutOfRangeException(nameof(episode));
            }
        }

        void ObserverCamera11(Vector3 position, Vector3 focus, float fov)
        {
            view.orthographic = false;
            view.fieldOfView = fov;
            view.transform.SetPositionAndRotation(position, Quaternion.LookRotation(focus - position));
        }

        void FollowObserver11(Vector3 player, Vector3 offset, Vector3 focus, float fov)
        {
            ObserverCamera11(player + offset, new Vector3(focus.x, player.y + focus.y, focus.z), fov);
        }

        static Vector3 Travel11(Vector3 a, Vector3 b, Vector3 c, float t, float turn)
        {
            return t < turn ? Vector3.Lerp(a, b, Range(t, .04f, turn)) :
                Vector3.Lerp(b, c, Range(t, turn, .94f));
        }

        void Arch11(string label, Vector3 at, float gap, float pier, Color stone)
        {
            float half = gap * .5f;
            for (int side = -1; side <= 1; side += 2)
                Block(label + " upright", at + V(side * half, pier * .5f, 0), V(.36f, pier, .69f), stone);
            for (int i = 0; i <= 8; i++)
            {
                float angle = i * Mathf.PI / 8;
                var piece = Block(label + " arch stone", at + V(Mathf.Cos(angle) * half,
                    pier + Mathf.Sin(angle) * half, 0), V(.36f, .33f, .69f),
                    i % 2 == 0 ? stone : PathStone11);
                piece.localRotation = Quaternion.Euler(0, 0, angle * Mathf.Rad2Deg);
            }
        }

        void Paving11(float center, float from, float to, float width, float top)
        {
            Floor("Original walkway", center, (from + to) / 2, width, to - from, top, PathStone11);
            for (float z = from + .27f; z < to; z += .47f)
                Block("Paving seam", V(center, top + .008f, z), V(width, .016f, .025f), WallStone11);
        }

        void Stone11(string role, Vector3 position, Vector3 fit)
        {
            Attach(role, Group("Shared " + role + " silhouette", position), fit, true);
        }

        Action<float> ObservedNavMesh11()
        {
            view.backgroundColor = ClearSky11;
            Floor("Continuous field around separate walkable lanes", 0, .8f, 12, 10, 0, FieldGrass11);
            Paving11(-2.05f, -3.8f, 5.1f, 1.25f, .028f);
            Paving11(2.13f, -3.8f, 5.1f, 2.85f, .028f);
            Stone11("cliff", V(-3.8f, 0, .55f), V(2.45f, 2.1f, 2.8f));
            Stone11("cliff", V(-.61f, 0, .77f), V(1.55f, 2.25f, 3.4f));
            Stone11("rock", V(3.85f, 0, .5f), V(1.35f, .95f, 1.3f));
            Stone11("rock", V(1.51f, 0, 4.4f), V(1.38f, .83f, 1.75f));
            Floor("Low climbable landing", -2.05f, 2.63f, 1.24f, .86f, .25f, WallStone11);
            var startRamp = V(-2.05f, .028f, 1.77f);
            var endRamp = V(-2.05f, .25f, 2.20f);
            var ramp = Group("Sloped connection to a higher nav surface", (startRamp + endRamp) * .5f);
            ramp.localRotation = Quaternion.FromToRotation(Vector3.forward, (endRamp - startRamp).normalized);
            Block("Visible sloped walk surface", V(0, -.09f, 0),
                V(1.24f, .18f, Vector3.Distance(startRamp, endRamp)), WallStone11, ramp);
            var shortRoute = Ring("Small walker passage width", V(-2.05f, .046f, .6f), .40f, Aqua);
            var wideRoute = Ring("Wide agent footprint", V(2.13f, .046f, .6f), .78f, Gold);
            var narrowDoor = Ring("Narrow lane rejected for the large agent", V(-2.05f, .05f, -.54f), .68f, Red);
            var landing = Ring("Upper landing marked separately", V(-2.05f, .27f, 2.38f), .42f, Paper);
            Route(Aqua, V(-2.05f, .044f, -3.15f), V(-2.05f, .044f, 1.78f));
            Route(Gold, V(2.13f, .044f, -3.15f), V(2.13f, .044f, 4.1f));
            var walker = Pawn(Second ? "Wide clearance demonstration agent" : "Narrow clearance demonstration agent",
                V(-2.05f, .028f, -3.15f), Second ? Gold : Aqua);
            float Ground(float z) => Mathf.Lerp(.028f, .25f, Mathf.InverseLerp(1.77f, 2.20f, z));
            walker.localScale *= Second ? 1.40f : .72f;
            if (!Second) walkthroughActors[walkthroughActors.Count - 1].GroundHeight = p => Ground(p.z);
            return t =>
            {
                if (Second)
                    walker.localPosition = t < .30f ? V(-2.05f, .028f, Mathf.Lerp(-3.15f, -1.37f, Range(t, .04f, .30f))) :
                        Travel11(V(-2.05f, .028f, -1.37f), V(2.13f, .028f, -1.15f),
                            V(2.13f, .028f, 4f), Range(t, .36f, .98f), .45f);
                else
                {
                    float z = Mathf.Lerp(-3.15f, 2.57f, Range(t, .02f, .96f));
                    walker.localPosition = V(-2.05f, Ground(z), z);
                }
                narrowDoor.gameObject.SetActive(Second && t > .22f && t < .63f);
                shortRoute.gameObject.SetActive(!Second);
                wideRoute.gameObject.SetActive(Second);
                landing.gameObject.SetActive(!Second && t > .55f);
                float pan = Range(t, .06f, .87f);
                ObserverCamera11(V(Mathf.Lerp(-4.4f, 5.3f, pan), Mathf.Lerp(6.65f, 5.0f, pan), -8.3f),
                    V(0, .5f, 1.0f), Mathf.Lerp(51, 47, pan));
            };
        }

        Action<float> ObservedProbes12()
        {
            view.backgroundColor = ClearSky11;
            Floor("Open field to door sample", 0, 1, 13, 13, 0, FieldGrass11);
            Paving11(0, -4.05f, 6.4f, 2.16f, .03f);
            Stone11("rock", V(-1.75f, 0, -.65f), V(1.23f, .84f, 1.23f));
            Stone11("cliff", V(-3.3f, 0, 2.42f), V(2.65f, 2.15f, 2.71f));
            Tree(V(2.8f, 0, -1.48f), 1.06f);
            Arch11("Interior entry viewpoint", V(0, .03f, 2.18f), 2.17f, 1.72f, WallStone11);
            for (int side = -1; side <= 1; side += 2)
                Block("Hall wall", V(side * 1.27f, .94f, 4.45f), V(.27f, 1.85f, 4.55f), WallStone11);
            var checkpoints = new[] { V(0, .036f, -2.25f), V(0, .037f, .55f), V(0, .037f, 2.95f) };
            var scanned = new Transform[3];
            for (int i = 0; i < checkpoints.Length; i++)
                scanned[i] = Ring("Visited check coordinate", checkpoints[i], .42f, i == 1 ? Gold : Aqua);
            var walker = Pawn("Automatic route example", V(0, .03f, -4), Aqua);
            var marker = Orb("Observation attached to the chosen coordinate", checkpoints[1] + V(0, .5f, 0), .23f, Gold);
            var link = Bar("Coordinate stem", checkpoints[1], checkpoints[1] + V(0, .53f, 0), .07f, Gold);
            return t =>
            {
                float z = Mathf.Lerp(-4, 4.95f, Range(t, .03f, .87f));
                walker.localPosition = V(0, .03f, z);
                for (int i = 0; i < scanned.Length; i++) scanned[i].gameObject.SetActive(z >= checkpoints[i].z);
                bool reported = z > .55f;
                marker.gameObject.SetActive(reported);
                link.gameObject.SetActive(reported);
                float rise = Range(t, Second ? .38f : .73f, .99f);
                Vector3 follow = walker.localPosition + V(.79f, 1.95f, -3.05f);
                Vector3 plan = V(5.85f, 8.65f, -6.6f);
                ObserverCamera11(Vector3.Lerp(follow, plan, rise), Vector3.Lerp(V(0, .93f, z + 2.25f),
                    V(0, .18f, 1.55f), rise), 53);
            };
        }

        Action<float> ObservedAtmosphere13()
        {
            view.backgroundColor = new Color32(104, 134, 162, 255);
            Floor("Ground shared by each light test", 0, .7f, 11, 13, 0, FieldGrass11);
            Paving11(0, -4.2f, 5.9f, 1.90f, .028f);
            Stone11("cliff", V(3.9f, 0, 5.1f), V(4.5f, 2.6f, 2.65f));
            Stone11("cliff", V(-4.15f, 0, 5.55f), V(4.8f, 3.35f, 3.0f));
            Stone11("rock", V(1.18f, 0, 1.53f), V(1.46f, 1.04f, 1.39f));
            Stone11("rock", V(-1.29f, 0, 1.53f), V(1.46f, 1.04f, 1.39f));
            Arch11("Shade boundary", V(0, .027f, -.45f), 2.5f, 1.85f, WallStone11);
            var canopy = Block("Overhanging shaded bank", V(-2.65f, 2.25f, -.95f), V(3.7f, .38f, 3.90f), WallStone11);
            canopy.localRotation = Quaternion.Euler(0, 0, 3);
            for (int i = 0; i < 4; i++) Tree(V((i % 2 == 0 ? -1 : 1) * (2.45f + .37f * i),
                0, 3.05f + i * .94f), .75f + i * .14f);
            var viewer = Pawn("Traveler from environmental shade to open field", V(0, .028f, -3.55f), Gold);
            var light = stage.Find("Key light").GetComponent<Light>();
            var sun = Orb("Direct light control", V(2.6f, 4.4f, 6.1f), .36f, Gold);
            var shaded = Ring("Same shaded reference rock", V(-1.29f, .03f, 1.53f), .63f, Aqua);
            var lit = Ring("Same lit reference rock", V(1.18f, .03f, 1.53f), .63f, Gold);
            return t =>
            {
                float z = Mathf.Lerp(-3.55f, .57f, Range(t, .02f, .53f));
                viewer.localPosition = V(.3f * Range(t, .22f, .58f), .028f, z);
                float state = Range(t, .24f, .90f);
                float sweep = Second ? .57f + .23f * state : state;
                light.color = Color.Lerp(new Color(1f, .74f, .52f), new Color(.72f, .86f, 1), sweep);
                light.intensity = Mathf.Lerp(1.8f, 1.10f, sweep);
                light.transform.rotation = Quaternion.Euler(39 - 13 * sweep, -46 + 81 * sweep, 0);
                RenderSettings.ambientLight = Color.Lerp(new Color(.28f, .32f, .43f), new Color(.34f, .36f, .53f),
                    Second ? state : .52f * state);
                view.backgroundColor = Color.Lerp(new Color(.36f, .27f, .26f), new Color(.44f, .55f, .69f), state);
                sun.localPosition = V(Mathf.Lerp(2.82f, 1.4f, sweep), 4.15f + sweep, 6.1f);
                shaded.gameObject.SetActive(Second);
                lit.gameObject.SetActive(Second);
                ObserverCamera11(V(Mathf.Lerp(.4f, 1.3f, state), 1.92f + .36f * state, z - 3.35f),
                    V(0, 1.49f, z + 3.2f), 56);
            };
        }

        Action<float> ObservedTelegraph14()
        {
            view.backgroundColor = new Color32(112, 75, 63, 255);
            Floor("Neutral training court", 0, .15f, 11, 8.0f, 0, new Color32(115, 106, 86, 255));
            Stone11("cliff", V(2.9f, 0, 3.35f), V(4.1f, 2.55f, 2.19f));
            Stone11("rock", V(-3.8f, 0, .22f), V(1.25f, .85f, 1.35f));
            var fighter = Pawn("Original larger opponent", V(-.62f, 0, 1.0f), Gold);
            var attacker = walkthroughActors[walkthroughActors.Count - 1];
            fighter.localScale *= 1.55f;
            attacker.FixedFacing = true;
            var player = Pawn("Original reacting player", V(.6f, 0, -1.33f), Aqua);
            var defender = walkthroughActors[walkthroughActors.Count - 1];
            var weapon = Block("Original wrist-bound practice club", Vector3.zero, V(.08f, 1.8f, .08f), Paper);
            var end = Orb("Practice club striking end", Vector3.zero, .31f, Gold);
            var windup = Ring("Cue before swing", V(-.62f, .045f, 1), .79f, Gold);
            var impact = Ring("Swing passing the approach route", V(.22f, .045f, -.7f), .77f, Red);
            float bladeArc = 0f;
            attacker.AfterPose = () =>
            {
                var wrist = stage.InverseTransformPoint(attacker.Arms[1].End.position);
                var angle = Mathf.Lerp(-.87f, 1.3f, bladeArc);
                Vector3 direction = V(Mathf.Sin(angle), Mathf.Lerp(.96f, .18f, bladeArc), -.51f).normalized;
                Segment(weapon, wrist - direction * .13f, wrist + direction * 1.39f, .092f);
                end.localPosition = wrist + direction * 1.29f;
            };
            return t =>
            {
                float load = Range(t, .21f, .55f);
                float strike = Range(t, .60f, .74f);
                float settle = Range(t, .78f, .97f);
                bladeArc = Mathf.Clamp01(.22f + .20f * load + .57f * strike - .75f * settle);
                fighter.localRotation = Quaternion.Euler(0, 154 - 34 * load + 93 * strike - 56 * settle, 0);
                attacker.Cast = .08f + .81f * load - .67f * strike - .15f * settle;
                float evade = Range(t, Second ? .54f : .66f, .87f);
                player.localPosition = V(.60f + 1.63f * evade, .0f, -1.33f - .72f * evade);
                defender.Cast = .32f * Range(t, .46f, .60f) * (1 - Range(t, .78f, .92f));
                windup.gameObject.SetActive(t > .22f && t < .61f);
                impact.gameObject.SetActive(t >= .615f && t < .83f);
                float close = Range(t, .10f, .56f);
                ObserverCamera11(V(Mathf.Lerp(4.0f, 3.0f, close + .20f * evade), 3.38f + .56f * evade, -6.9f),
                    V(.0f + 1.01f * evade, 1.24f, 0), Mathf.Lerp(48, 45, close));
            };
        }

        void Bloom11(Vector3 position, float size, Color petals)
        {
            Block("Visible flower stalk beside the path", position + V(0, .16f * size, 0),
                V(.045f, .33f, .045f) * size, new Color32(57, 99, 98, 255));
            var center = position + V(0, .34f * size, 0);
            Orb("Flower light center", center, .15f * size, Paper);
            for (int i = 0; i < 4; i++)
            {
                float a = i * Mathf.PI * .5f;
                Shape(PrimitiveType.Sphere, "Flower petal",
                    center + V(Mathf.Cos(a), .04f, Mathf.Sin(a)) * (.10f * size),
                    V(.19f, .092f, .19f) * size, petals);
            }
        }

        Action<float> ObservedFlowers15()
        {
            view.backgroundColor = new Color32(49, 76, 119, 255);
            var soil = new Color32(45, 72, 83, 255);
            Floor("Sloping meadow appearance laid flat for the route study", 0, 2.7f, 13, 16, 0, soil);
            Paving11(0, -4.1f, 6.85f, 1.57f, .023f);
            var large = V(2.7f, 0, 5.83f);
            Stone11("cliff", large, V(3.82f, 2.63f, 2.65f));
            Tree(V(-2.2f, 0, .6f), 1.32f);
            Tree(V(2.54f, 0, 3.46f), .95f);
            var traveller = Pawn("Traveler among nearby flowers", V(0, .023f, -3.64f), Gold);
            var seed = new System.Random(152023);
            var farCover = new Texture2D(64, 40) { filterMode = FilterMode.Bilinear };
            owned.Add(farCover);
            for (int z = 0; z < farCover.height; z++)
                for (int x = 0; x < farCover.width; x++)
                    farCover.SetPixel(x, z, seed.NextDouble() < .31 ?
                        Color.Lerp(Blue, Paper, (float)seed.NextDouble() * .55f) : soil);
            farCover.Apply();
            var band = Block("Distant texture representing a blue meadow", V(-.97f, .016f, 7.02f),
                V(8.80f, .03f, 6.50f), Blue);
            var material = new Material(Paint(Color.white)) { mainTexture = farCover };
            owned.Add(material);
            band.GetComponent<Renderer>().sharedMaterial = material;
            for (int i = 0; i < 12; i++)
            {
                float z = -.87f + .44f * i + .18f * Mathf.Sin(i * 1.53f);
                float x = (i % 2 == 0 ? -1 : 1) * (.94f + .43f * Mathf.Sin(i * .78f) * Mathf.Sin(i * .78f));
                Bloom11(V(x, .025f, z), .74f + .61f * (i % 5) / 4, Color.Lerp(Blue, Aqua, (i % 3) * .18f));
            }
            for (int i = 0; i < 29; i++)
            {
                float x = -4.95f + 9.25f * (float)seed.NextDouble();
                float z = 4.28f + 4.95f * (float)seed.NextDouble();
                if (Mathf.Abs(x) > 1.05f)
                    Orb("Distant flower cluster", V(x, .02f, z), .18f + .25f * (float)seed.NextDouble(), Blue);
            }
            return t =>
            {
                float z = Mathf.Lerp(-3.64f, 4.58f, Range(t, .03f, .94f));
                float x = .27f * Mathf.Sin(z * .82f);
                traveller.localPosition = V(x, .023f, z);
                float change = Range(t, .15f, .89f);
                Vector3 offset = Second ? V(.58f, 1.62f + .58f * change, -2.78f) : V(1.41f - .59f * change, 2.38f, -3.25f);
                FollowObserver11(traveller.localPosition, offset, V(0, .74f + .53f * change, z + 2.47f), 55);
            };
        }

        Action<float> ObservedLandmark16()
        {
            view.backgroundColor = ClearSky11;
            Floor("Broad plain with close and distant silhouettes", 0, 2.35f, 13.5f, 15.5f, 0, FieldGrass11);
            Floor("Curved lookout path surrogate", 0, .5f, 4.0f, 10.4f, .02f, new Color32(124, 129, 88, 255));
            for (int i = 0; i < 9; i++) Stone11("rock", V(-3.72f + (i % 2) * 7.27f, 0, -3.55f + i * .81f),
                V(.33f + i % 3 * .12f, .28f + i % 4 * .09f, .32f));
            Arch11("Original distant destination", V(.43f, 0, 7.69f), 2.20f, 2.25f, WallStone11);
            Stone11("tower", V(-1.52f, 0, 8.55f), V(1.4f, 3.24f, 1.33f));
            var close = Block("Near pillar masking distant outline", V(.12f, 1.0f, 1.28f), V(.68f, 2.0f, .56f), WallStone11);
            var player = Pawn("Survey traveler", V(-.88f, .02f, -3.43f), Aqua);
            var first = Ring("First critical viewpoint", V(-.88f, .039f, -3.43f), .60f, Aqua);
            var next = Ring("Second critical viewpoint after the turn", V(1.25f, .039f, -.57f), .60f, Gold);
            return t =>
            {
                float p = Range(t, .05f, .84f);
                player.localPosition = V(Mathf.Lerp(-.88f, 1.25f, p), .02f, Mathf.Lerp(-3.43f, -.57f, p));
                float adjust = Second ? Range(t, .57f, .83f) : 0;
                close.localPosition = V(.12f - 1.08f * adjust, 1f, 1.28f);
                first.gameObject.SetActive(t < .59f);
                next.gameObject.SetActive(t >= .59f);
                ObserverCamera11(player.localPosition + V(.62f, 1.84f, -2.92f),
                    V(Mathf.Lerp(-.58f, .43f, p), 1.3f, 7.69f), 51);
            };
        }

        static float DungeonHeight17(float z) =>
            Mathf.Lerp(0, .97f, Mathf.InverseLerp(-.7f, 2.56f, z));

        Action<float> ObservedDungeon17()
        {
            view.backgroundColor = Second ? (Color)new Color32(105, 126, 134, 255) : ClearSky11;
            Color ground = Second ? PathStone11 : FieldGrass11;
            if (Second)
            {
                Paving11(0, -4.61f, -.70f, 3.15f, 0);
                Paving11(0, 2.56f, 6.75f, 4.58f, .97f);
                var a = V(0, 0, -.70f);
                var b = V(0, .97f, 2.56f);
                var ramp = Group("Continuous ramp from lower to upper dungeon path", (a + b) * .5f);
                ramp.localRotation = Quaternion.FromToRotation(Vector3.forward, (b - a).normalized);
                Block("Ramp actual walk surface", V(0, -.12f, 0), V(2.39f, .24f, Vector3.Distance(a, b)), ground, ramp);
                for (int i = 0; i < 8; i++)
                    Block("Ramp stone joint", V(0, .009f, (i - 3.5f) * .42f), V(2.39f, .018f, .025f), WallStone11, ramp);
                for (int side = -1; side <= 1; side += 2)
                    for (int i = 0; i < 9; i++)
                    {
                        float z = -3.53f + i * .72f;
                        Block("Close masonry shaping the upper route", V(side * 1.39f, DungeonHeight17(z) + .81f, z),
                            V(.42f, 1.62f, .75f), WallStone11);
                    }
                Arch11("Threshold reveals the upper court", V(0, .97f, 2.56f), 2.22f, 1.69f, WallStone11);
                Stone11("tower", V(2.34f, .10f, 6.46f), V(2.22f, 3.75f, 1.91f));
                Stone11("cliff", V(-3.35f, 0, 3.52f), V(2.93f, 2.12f, 4.17f));
            }
            else
            {
                Floor("Broad terrain with lateral choices", 0, 1.15f, 13.0f, 12.7f, 0, ground);
                Arch11("Exit to the field", V(0, 0, -1.35f), 2.5f, 1.70f, WallStone11);
                Paving11(0, -4.48f, .63f, 1.65f, .02f);
                Route(Gold, V(0, .035f, .6f), V(-3.12f, .035f, 4.7f));
                Route(Aqua, V(0, .035f, .6f), V(3.39f, .035f, 4.7f));
                Stone11("tower", V(-3.32f, 0, 5.85f), V(2.37f, 3.95f, 2.40f));
                Stone11("cliff", V(3.73f, 0, 5.32f), V(3.56f, 2.0f, 2.60f));
                Tree(V(-2.07f, 0, 2.7f), 1.04f);
                Tree(V(2.5f, 0, 1.97f), .76f);
            }
            var player = Pawn("Traveler showing field and dungeon rhythms", V(0, Second ? 0 : .02f, -4.1f), Gold);
            if (Second) walkthroughActors[walkthroughActors.Count - 1].GroundHeight = p => DungeonHeight17(p.z);
            return t =>
            {
                Vector3 p;
                if (Second)
                {
                    float z = Mathf.Lerp(-4.1f, 5.12f, Range(t, .04f, .95f));
                    p = V(1.04f * Range(t, .73f, .99f), DungeonHeight17(z), z);
                }
                else
                {
                    p = Travel11(V(0, .02f, -4.1f), V(0, .02f, .4f), V(-2.87f, 0, 4.10f), t, .42f);
                }
                player.localPosition = p;
                FollowObserver11(p, V(Second ? .39f : .75f, 1.94f, -3.2f), V(p.x * .96f, .96f, p.z + 2.52f),
                    Second ? 51 : Mathf.Lerp(48, 61, Range(t, .33f, .86f)));
            };
        }

        void Relief18(Vector3 point, bool old)
        {
            var stone = Block("Original heraldry tablet", point + V(0, .86f, 0), V(1.39f, 1.72f, .28f), WallStone11);
            Color shade = old ? Gold : (Color)new Color32(175, 129, 86, 255);
            Orb("Same relief visible in both eras", point + V(0, 1.16f, -.15f), .36f, shade);
            for (int i = 0; i < 3; i++)
                Block("Relief mark", point + V((i - 1) * .25f, .84f - i * .12f, -.157f), V(.16f, .10f, .04f), shade);
            if (!old) stone.localRotation = Quaternion.Euler(0, 0, -9);
        }

        Action<float> ObservedHistory18()
        {
            view.backgroundColor = new Color32(120, 119, 114, 255);
            Floor("Past example place", -3.35f, .0f, 4.7f, 6.4f, 0, new Color32(116, 107, 93, 255));
            Floor("Current example place", 2.71f, .0f, 6.35f, 6.4f, 0, FieldGrass11);
            Relief18(V(-3.04f, 0, .28f), true);
            Relief18(V(2.42f, 0, .28f), false);
            Arch11("Intact place in the historical model", V(-3.04f, 0, 1.98f), 2.36f, 1.72f, WallStone11);
            Block("Surviving lower stone of broken old arch", V(1.54f, .73f, 2.02f), V(.52f, 1.46f, .56f), WallStone11);
            Block("Surviving upper stone of broken old arch", V(3.34f, 1.06f, 2.02f), V(.53f, 2.12f, .56f), WallStone11);
            Stone11("rock", V(3.76f, 0, 1.23f), V(1.01f, .48f, .69f));
            Stone11("rock", V(1.03f, 0, 1.28f), V(.93f, .46f, .59f));
            var person = Pawn("Person in the present-day area", V(3.91f, 0, 1.78f), Gold);
            var traveller = Pawn("Traveler observing the same surviving motif", V(2.43f, 0, -2.58f), Aqua);
            var mark = Ring("Same place cue preserved in present", V(2.42f, .029f, .04f), .70f, Gold);
            return t =>
            {
                float bridge = Range(t, .19f, .72f);
                traveller.localPosition = V(2.43f + .51f * Range(t, .52f, .95f), 0,
                    Mathf.Lerp(-2.58f, -.64f, Range(t, .36f, .94f)));
                person.localPosition = V(3.91f - .58f * Range(t, .61f, .95f), 0, 1.78f - .51f * Range(t, .61f, .95f));
                mark.gameObject.SetActive(t > .48f);
                float x = Second ? Mathf.Lerp(.10f, 2.74f, bridge) : Mathf.Lerp(-2.70f, 1.73f, bridge);
                ObserverCamera11(V(x + 1.32f, 3.26f - .95f * bridge, -7.48f + 3.03f * bridge),
                    V(x, 1.03f, .55f), Mathf.Lerp(46, 53, bridge));
            };
        }

        Action<float> ObservedBoss19()
        {
            view.backgroundColor = Second ? (Color)new Color32(98, 120, 126, 255) : ClearSky11;
            Floor("Encounter setting", 0, .9f, 12.75f, 13.25f, 0, Second ? WallStone11 : FieldGrass11);
            if (Second)
            {
                Paving11(0, -3.9f, 6.64f, 2.86f, .035f);
                Arch11("Entrance frames the encounter", V(0, .035f, .43f), 2.82f, 1.79f, WallStone11);
                for (int side = -1; side <= 1; side += 2)
                {
                    Block("Wall limits approach direction", V(side * 1.71f, 1.15f, -.92f), V(.41f, 2.30f, 3.01f), WallStone11);
                    Block("Low courtyard edge", V(side * 2.10f, .36f, 3.74f), V(.40f, .72f, 4.35f), PathStone11);
                }
                Stone11("tower", V(-2.02f, 0, 5.65f), V(2.06f, 3.72f, 2.33f));
                Route(Gold, V(0, .043f, -3.59f), V(0, .043f, .45f), V(0, .043f, 3.55f));
            }
            else
            {
                Stone11("rock", V(.0f, 0, -.18f), V(1.56f, .83f, 1.51f));
                Stone11("cliff", V(3.88f, 0, 3.24f), V(3.38f, 1.85f, 2.13f));
                for (int i = 0; i < 4; i++) Tree(V(-3.45f + i * 2.05f, 0, 5.62f + i % 2 * .46f), .84f + i * .12f);
                Route(Aqua, V(0, .036f, -3.58f), V(-2.55f, .036f, .50f), V(-2.79f, .036f, 3.78f));
                Route(Gold, V(0, .037f, -3.58f), V(2.31f, .037f, .14f), V(1.72f, .037f, 3.54f));
            }
            float height = Second ? .035f : 0;
            var enemy = Pawn("Original encounter marker character", V(.08f, height, 4.32f), Red);
            enemy.localScale *= 1.49f;
            var player = Pawn("Traveler choosing approach", V(0, height, -3.59f), Aqua);
            var focus = Ring("Point of encounter", V(.08f, height + .03f, 3.45f), .80f, Red);
            return t =>
            {
                Vector3 p = Second ? V(0, height, Mathf.Lerp(-3.59f, 2.55f, Range(t, .04f, .95f))) :
                    Travel11(V(0, height, -3.59f), V(-2.57f, height, .23f), V(-2.85f, height, 3.91f), t, .50f);
                player.localPosition = p;
                float react = Range(t, .66f, .93f);
                enemy.localPosition = V(.08f - (Second ? .02f : .8f) * react, height, 4.32f - .52f * react);
                focus.gameObject.SetActive(t > .41f);
                FollowObserver11(p, V(Second ? .58f : 1.33f, Second ? 1.99f : 2.67f, -3.45f),
                    V(Second ? 0 : Mathf.Lerp(.25f, -1.06f, react), 1.24f, 4.32f), Second ? 52 : 57);
            };
        }
    }
}
