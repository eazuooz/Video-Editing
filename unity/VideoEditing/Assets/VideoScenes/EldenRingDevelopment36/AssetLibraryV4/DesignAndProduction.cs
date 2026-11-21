using System;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        Action<float> BuildDesignAndProduction()
        {
            switch (episode)
            {
                case 13: return SkyBlend();
                case 14: return MotionSignal();
                case 15: return FlowerPlacement();
                case 16: return Viewpoint();
                case 17: return FieldAndDungeon();
                case 18: return PastToWorld();
                case 19: return BossApproach();
                case 20: return Traversal();
                case 21: return BuildChoices();
                case 22: return DiscoveryOrder();
                case 23: return Coordination(false);
                case 24: return DifficultyRoute();
                default: throw new ArgumentOutOfRangeException(nameof(episode));
            }
        }

        Action<float> SkyBlend()
        {
            FrameCamera(V(0, 3, -13), V(0, 1.7f, 0), 3.4f);
            for (int i = 0; i < 7; i++)
            {
                float h = 1.3f + .6f * Mathf.Sin(i * .75f);
                var peak = Block("Mountain silhouette", V((i - 3) * 1.54f, h / 2, 1.0f + i * .34f), V(1.45f, h, 1.1f), Slate);
                peak.localRotation = Quaternion.Euler(0, 34, 15);
            }
            for (int i = 0; i < 5; i++) Tree(V((i - 2) * 1.44f, 0, -1.25f), .85f);
            var light = stage.Find("Key light").GetComponent<Light>();
            var sun = Orb("Direct light", V(-3.5f, 3.6f, 2), .55f, Gold);
            return t =>
            {
                float a = Ease(t);
                light.color = Color.Lerp(Gold, Blue, a);
                light.transform.rotation = Quaternion.Euler(32 - a * 19, -44 + a * 99, 0);
                if (Second) RenderSettings.ambientLight = Color.Lerp(new Color(.39f, .31f, .21f), new Color(.19f, .31f, .49f), a);
                view.backgroundColor = Color.Lerp(new Color(.20f, .29f, .35f), new Color(.39f, .23f, .37f), a);
                sun.localPosition = V(Mathf.Lerp(-3.7f, 3.8f, a), 2.6f + .91f * Mathf.Sin(a * Mathf.PI), 2.6f);
            };
        }

        Action<float> MotionSignal()
        {
            FrameCamera(V(0, 3.5f, -12), V(0, 1.1f, 0), 3.6f);
            var fighter = Pawn("Neutral opponent", V(-1.8f, 0, .7f), Gold);
            fighter.localScale = Vector3.one * 1.48f;
            var arm = fighter.Find("Right sleeve");
            Block("Training blade", V(.02f, -.48f, 0), V(.08f, .75f, .075f), Paper, arm);
            var observer = Pawn("Responding character", V(1.3f, 0, -.4f), Aqua);
            var tell = Ring("Telegraph window", V(-1.8f, .05f, .7f), .95f, Gold);
            var area = Ring("Contact extent", V(0, .04f, -.35f), 1.15f, Red);
            return t =>
            {
                float wait = Second ? .26f : .40f;
                float anticipation = Range(t, wait, .64f), swing = Range(t, .65f, .79f);
                arm.localRotation = Quaternion.Euler(-132 * anticipation + 155 * swing, -28 * anticipation, 29);
                fighter.localRotation = Quaternion.Euler(0, -14 + 10 * Pulse(t * 3) + 26 * swing, -8 * anticipation);
                tell.gameObject.SetActive(t >= wait && t < .65f);
                area.gameObject.SetActive(t >= .66f && t < .84f);
                observer.localPosition = V(1.26f + 1.46f * Range(t, .44f, .70f), 0, -.4f);
            };
        }

        Action<float> FlowerPlacement()
        {
            FrameCamera(V(4, 8, -10), V(0, 0, 0), 4.15f);
            var random = new System.Random(152);
            var distant = new Transform[38];
            for (int i = 0; i < distant.Length; i++)
            {
                var p = V((float)random.NextDouble() * 8.9f - 4.45f, .09f, (float)random.NextDouble() * 3.1f + .16f);
                distant[i] = Orb("Procedurally placed plant", p, .12f + (float)random.NextDouble() * .12f, Aqua);
            }
            var blossoms = new Transform[7];
            for (int i = 0; i < blossoms.Length; i++)
            {
                var p = V(-3.5f + .96f * i, .30f, -.9f + Mathf.Sin(i * .82f) * .65f);
                blossoms[i] = Orb("Individually positioned bloom", p, .28f, Gold);
                Block("Stem", p - V(0, .16f, 0), V(.055f, .32f, .055f), Aqua);
            }
            var farProxy = Block("Distant cover proxy", V(0, .012f, 2.08f), V(8.9f, .11f, 2.15f), Blue);
            var cover = new Texture2D(32, 32) { filterMode = FilterMode.Point };
            owned.Add(cover);
            for (int y = 0; y < 32; y++)
                for (int x = 0; x < 32; x++)
                    cover.SetPixel(x, y, (x + y * 7) % 11 < 2 ? Aqua : Blue * .5f);
            cover.Apply();
            var coverMaterial = new Material(Shader.Find("Standard")) { mainTexture = cover };
            owned.Add(coverMaterial);
            farProxy.GetComponent<Renderer>().sharedMaterial = coverMaterial;
            return t =>
            {
                for (int i = 0; i < distant.Length; i++)
                    distant[i].gameObject.SetActive((Second || t > .06f + (i % 8) * .052f) && (!Second || t < .54f));
                for (int i = 0; i < blossoms.Length; i++) blossoms[i].gameObject.SetActive(Second || t > .43f + i * .052f);
                farProxy.gameObject.SetActive(Second && t >= .53f);
            };
        }

        Action<float> Viewpoint()
        {
            Landmark("Destination", V(.15f, 0, 2.75f), 2.15f, Gold);
            for (int i = 0; i < 5; i++)
            {
                Landmark("Left wall", V(-3.8f + .12f * i, 0, -2f + i * 1.13f), 1.45f, Slate);
                Landmark("Right wall", V(3.55f, 0, -1.8f + i * 1.04f), 1.65f, Blue);
            }
            var obstruction = Block("Repeated silhouette in front of goal", V(.1f, 1.08f, .15f), V(1.69f, 2.16f, 1.0f), Slate);
            var survey = Pawn("Representative viewpoint", V(-2.8f, 0, -2.75f), Aqua);
            return t =>
            {
                float shift = Range(t, .11f, .84f);
                if (Second) obstruction.localPosition = V(.1f + 2.0f * shift, 1.08f, .15f);
                survey.localPosition = V(Mathf.Lerp(-2.8f, .7f, shift), 0, -2.75f);
                FrameCamera(V(Mathf.Lerp(-3.2f, 2.3f, shift), 2.4f, -10.3f), V(0, 1.16f, .6f), 3.75f);
            };
        }

        Action<float> FieldAndDungeon()
        {
            Block("Open field surface", V(-2.5f, .015f, 0), V(4.8f, .18f, 5.55f), Slate);
            Block("Interior ground floor", V(2.6f, .054f, 0), V(4.2f, .28f, 5.55f), Slate);
            Block("Upper passage", V(3.5f, .89f, .7f), V(1.55f, .23f, 3.4f), Paper);
            for (int i = 0; i < 5; i++)
                Block("Stairs", V(2.86f, .15f + i * .12f, -2.09f + .34f * i), V(1.05f, .22f + i * .08f, .45f), Slate);
            Route(Aqua, V(-4.6f, .14f, -1.85f), V(-3, .14f, 0), V(-.9f, .14f, 1.7f));
            Route(Gold, V(-4.6f, .15f, -1.85f), V(-1.0f, .15f, -.75f), V(2.9f, .15f, -1.75f));
            Route(Paper, V(2.86f, .27f, -1.9f), V(2.86f, 1.02f, -.50f), V(3.5f, 1.03f, 1.98f));
            var pawn = Pawn("Moving from field to passage", V(-4.6f, .12f, -1.9f), Gold);
            return t =>
            {
                float a = Range(t, 0, .60f), b = Range(t, .52f, .94f);
                pawn.localPosition = Second ? V(2.86f + .65f * b, .25f + .78f * b, Mathf.Lerp(-1.9f, 1.7f, Ease(t))) :
                    V(Mathf.Lerp(-4.6f, 2.9f, a), .16f, -1.79f + .89f * Mathf.Sin(a * Mathf.PI));
            };
        }

        Action<float> PastToWorld()
        {
            var past = Landmark("Invented historical foundation", V(-3.65f, 0, .1f), 2.1f, Gold);
            var path = Bar("Foundation carried forward", V(-3.2f, .22f, .1f), V(-3.1f, .22f, .1f), .09f, Gold);
            var ruins = Landmark("Present environment", V(.65f, 0, 1.35f), 1.5f, Aqua);
            var person = Pawn("Present-day character", V(3.4f, 0, .3f), Aqua);
            var encounter = Ring("Present-day encounter", V(3.4f, .04f, -1.4f), .65f, Paper);
            return t =>
            {
                past.localRotation = Quaternion.Euler(0, 18 * Range(t, 0, .48f), 0);
                Segment(path, V(-3.2f, .23f, .1f), V(Mathf.Lerp(-3.16f, 3.5f, Ease(t)), .23f, .1f), .085f);
                ruins.localScale = V(1.08f, .35f + Range(t, .30f, .74f) * 1.16f, .97f);
                person.gameObject.SetActive(t > (Second ? .26f : .64f));
                person.localPosition = V(3.4f, 0, Mathf.Lerp(.9f, -1.4f, Range(t, .50f, .95f)));
                encounter.gameObject.SetActive(t > .73f);
            };
        }

        Action<float> BossApproach()
        {
            var left = Pawn("Open-field encounter", V(-2.8f, 0, 1.3f), Red);
            var right = Pawn("Gate encounter", V(2.8f, 0, 1.3f), Red);
            left.localScale = right.localScale = Vector3.one * 1.55f;
            Block("Gate left wall", V(1.2f, .95f, -.1f), V(.6f, 1.9f, 3f), Slate);
            Block("Gate right wall", V(4.25f, .95f, -.1f), V(.6f, 1.9f, 3f), Slate);
            Route(Aqua, V(-4.38f, .07f, -2.3f), V(-3.15f, .07f, -.62f), V(-2.78f, .07f, 1.0f));
            Route(Paper, V(-1.39f, .07f, -2.3f), V(-1.8f, .07f, .0f), V(-2.77f, .07f, 1.0f));
            Route(Gold, V(2.78f, .07f, -2.7f), V(2.78f, .07f, 1));
            var a = Pawn("Open approach", V(-4.38f, 0, -2.3f), Aqua);
            var b = Pawn("Gate approach", V(2.78f, 0, -2.7f), Gold);
            return t =>
            {
                float s = Ease(t);
                a.localPosition = V(Mathf.Lerp(Second ? -1.39f : -4.38f, -2.8f, s), 0, Mathf.Lerp(-2.3f, .7f, s));
                b.localPosition = V(2.78f, 0, Mathf.Lerp(-2.7f, .7f, s));
                left.localRotation = Quaternion.Euler(0, Second ? 26 * s : -25 * s, 0);
            };
        }

        Action<float> Traversal()
        {
            Landmark("Distant destination", V(4.0f, 0, 1.35f), 1.7f, Gold);
            Block("Step", V(.9f, .32f, -.8f), V(1.13f, .62f, 1.4f), Slate);
            var walking = Pawn("On foot", V(-4.3f, 0, .75f), Paper);
            var quick = Pawn("Mounted equivalent", V(-4.3f, 0, -.8f), Aqua);
            var mount = Mount(V(-4.3f, .26f, -.8f));
            Route(Slate, V(-4.5f, .05f, .75f), V(4.3f, .05f, .75f));
            Route(Slate, V(-4.5f, .05f, -.8f), V(4.3f, .05f, -.8f));
            return t =>
            {
                float walk = Ease(t);
                float fast = Mathf.Min(1, t * 1.68f);
                walking.localPosition = V(-4.3f + 5.2f * walk, 0, .75f);
                float jump = Mathf.Sin(Mathf.PI * Range(t, .40f, .68f));
                quick.localPosition = V(-4.3f + 8.2f * (Second ? walk : fast), Second ? .86f * jump : .48f, -.8f);
                mount.gameObject.SetActive(!Second);
                mount.localPosition = V(quick.localPosition.x, .27f, -.8f);
            };
        }

        Action<float> BuildChoices()
        {
            var player = Pawn("Choice maker", V(-4.0f, 0, 0), Gold);
            var routes = new[] { V(-.85f, .12f, -2.35f), V(-.85f, .12f, 0), V(-.85f, .12f, 2.35f) };
            var outputs = new[] { V(3.10f, .12f, -2.35f), V(3.10f, .12f, 0), V(3.10f, .12f, 2.35f) };
            for (int i = 0; i < routes.Length; i++)
            {
                Block("Development choice", routes[i], V(.72f, .27f, .75f), Slate);
                Landmark("Distinct outcome", outputs[i], 1.12f, i == 1 ? Gold : Aqua);
                Route(Slate, V(-4.0f, .06f, 0), routes[i], outputs[i]);
            }
            var approval = Ring("Current selection", routes[0], .63f, Gold);
            return t =>
            {
                int selected = Second ? 2 : t < .55f ? 0 : 1;
                approval.localPosition = routes[selected] + V(0, .20f, 0);
                Vector3 p = Vector3.Lerp(V(-4, .03f, 0), routes[selected], Range(t, .05f, .48f));
                player.localPosition = Vector3.Lerp(p, outputs[selected] - V(.56f, .05f, 0), Range(t, .50f, .95f));
            };
        }

        Action<float> DiscoveryOrder()
        {
            var sites = new[] { V(-3.4f, 0, 1.5f), V(0, 0, 2.5f), V(3.4f, 0, 1.1f) };
            for (int i = 0; i < sites.Length; i++) Landmark("Shared world evidence", sites[i], 1.3f + i * .25f, Aqua);
            var a = Pawn("Explorer A", V(-3, 0, -2.6f), Gold);
            var b = Pawn("Explorer B", V(3, 0, -2.6f), Blue);
            var discovered = new Transform[2, 3];
            for (int j = 0; j < 2; j++)
                for (int i = 0; i < 3; i++)
                    discovered[j, i] = Ring("Discovered world clue", sites[i] + V(0, .12f + .08f * j, 0), .6f + .18f * j, j == 0 ? Gold : Blue);
            return t =>
            {
                int[] first = Second ? new[]{1, 0, 2} : new[]{0, 1, 2};
                int[] other = Second ? new[]{0, 2, 1} : new[]{2, 0, 1};
                float step = t * 2.99f;
                int leg = Mathf.FloorToInt(step);
                a.localPosition = Vector3.Lerp(leg == 0 ? V(-3, 0, -2.6f) : sites[first[leg - 1]], sites[first[leg]], Ease(step - leg));
                b.localPosition = Vector3.Lerp(leg == 0 ? V(3, 0, -2.6f) : sites[other[leg - 1]], sites[other[leg]], Ease(step - leg));
                for (int i = 0; i < 3; i++)
                {
                    discovered[0, first[i]].gameObject.SetActive(t >= (i + .8f) / 3);
                    discovered[1, other[i]].gameObject.SetActive(t >= (i + .92f) / 3);
                }
            };
        }

        Action<float> Coordination(bool expansion)
        {
            var stations = new[] { V(-3.6f, 0, -1.65f), V(-.4f, 0, 1.65f), V(3.2f, 0, -1.65f) };
            for (int i = 0; i < stations.Length; i++)
            {
                Pawn("Illustrative development role", stations[i] + V(0, 0, .6f), i == 1 ? Paper : Aqua);
                Block("Workstation", stations[i] + V(0, .22f, -.2f), V(1.75f, .42f, .82f), Slate);
            }
            Route(Slate, stations[0] + V(0, .12f, 0), stations[1] + V(0, .12f, 0), stations[2] + V(0, .12f, 0));
            var parcel = Block("Work handoff", stations[0] + V(0, .45f, 0), V(.47f, .36f, .48f), Gold);
            var board = Landmark(expansion ? "Reusable development base" : "Shared status checkpoint", V(.05f, 0, -.75f), 1.25f, Blue);
            var results = new Transform[5];
            for (int i = 0; i < results.Length; i++)
                results[i] = Block("Completed example task", V(3.2f - .42f * i, .20f, -2.6f), V(.32f, .3f, .55f), Aqua);
            return t =>
            {
                int leg = t < .5f ? 0 : 1;
                var p = Vector3.Lerp(stations[leg], stations[leg + 1], Ease(t * 2 - leg));
                parcel.localPosition = p + V(0, .5f, 0);
                if (Second || expansion) board.localScale = V(.8f, .25f + 1.4f * Range(t, .11f, .49f), .65f);
                else board.gameObject.SetActive(t > .55f);
                for (int i = 0; i < results.Length; i++) results[i].gameObject.SetActive(t > .45f + .1f * i);
            };
        }

        Action<float> DifficultyRoute()
        {
            var barrier = Pawn("Challenging encounter", V(1.15f, 0, .0f), Red);
            barrier.localScale = Vector3.one * 2;
            var optional = Landmark("Side-path opportunity", V(-.75f, 0, 2.35f), 1.1f, Aqua);
            Route(Red, V(-4.2f, .08f, 0), V(.45f, .08f, 0));
            Route(Aqua, V(-1.1f, .08f, 0), V(-.75f, .08f, 2.35f), V(3.9f, .08f, 2.35f));
            Route(Gold, V(3.9f, .07f, 2.35f), V(2.3f, .07f, .25f));
            var pawn = Pawn("Player testing another route", V(-4.2f, 0, 0), Gold);
            return t =>
            {
                Vector3 first = Vector3.Lerp(V(-4.2f, 0, 0), V(-.75f, 0, 0), Range(t, 0, .27f));
                Vector3 side = Vector3.Lerp(first, V(-.75f, 0, 2.35f), Range(t, .28f, .53f));
                Vector3 beyond = Vector3.Lerp(side, V(3.9f, 0, 2.35f), Range(t, .52f, .79f));
                pawn.localPosition = Second ? Vector3.Lerp(beyond, V(2.55f, 0, .18f), Range(t, .78f, .97f)) : beyond;
                Tint(optional, t > .50f ? Gold : Aqua);
            };
        }
    }
}
