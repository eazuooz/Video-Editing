using System;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        Action<float> BuildPresentationAndTesting()
        {
            switch (episode)
            {
                case 25: return Coordination(true);
                case 26: return Weight();
                case 27: return Acoustics();
                case 28: return Choir();
                case 29: return Projection();
                case 30: return FramePacing();
                case 31: return Comparison();
                case 32: return TargetModifier();
                case 33: return RayOption();
                case 34: return ProgressCurve();
                case 35: return Retry();
                case 36: return Cooperation();
                default: throw new ArgumentOutOfRangeException(nameof(episode));
            }
        }

        Action<float> Weight()
        {
            FrameCamera(V(0, 3.3f, -12), V(0, 1.25f, 0), 3.8f);
            Transform light = Pawn("Light practice weapon", V(-2.4f, 0, .35f), Aqua);
            Transform heavy = Pawn("Heavy practice weapon", V(2.4f, 0, .35f), Gold);
            light.localScale = heavy.localScale = Vector3.one * 1.45f;
            var lightHand = light.Find("Right sleeve");
            var heavyHand = heavy.Find("Right sleeve");
            Block("Light tool", V(0, -.36f, 0), V(.11f, .62f, .08f), Paper, lightHand);
            Block("Heavy tool", V(0, -.59f, 0), V(.24f, 1.12f, .18f), Paper, heavyHand);
            var phases = new Transform[3];
            for (int i = 0; i < phases.Length; i++)
                phases[i] = Block("Motion phase", V(-2.4f + i * 2.4f, .10f, -1.6f), V(1.98f, .22f, .44f), Slate);
            return t =>
            {
                float a = Range(t, .08f, .20f), b = Range(t, .20f, .38f), c = Range(t, .40f, .63f);
                lightHand.localRotation = Quaternion.Euler(-78 * a + 138 * b - 60 * c, 0, 9);
                a = Range(t, .11f, .45f); b = Range(t, .46f, .61f); c = Range(t, .63f, .98f);
                heavyHand.localRotation = Quaternion.Euler(-129 * a + 202 * b - 73 * c, -25 * a + 31 * b, 19);
                heavy.localRotation = Quaternion.Euler(13 * b - 13 * c, -19 * a + 48 * b - 29 * c, 0);
                for (int i = 0; i < 3; i++) Tint(phases[i], i == (t < .46f ? 0 : t < .62f ? 1 : 2) ? Gold : Slate);
                if (Second) FrameCamera(V(1.25f + .42f * t, 3.15f, -12), V(1.0f, 1.24f, 0), 3.65f);
            };
        }

        Action<float> Acoustics()
        {
            Block("Cave back", V(-2.7f, .95f, 1.7f), V(4.05f, 1.9f, .27f), Slate);
            Block("Cave side", V(-4.8f, .95f, .03f), V(.25f, 1.9f, 3.45f), Slate);
            Block("Cave side", V(-.66f, .95f, .03f), V(.25f, 1.9f, 3.45f), Slate);
            var listener = Pawn("Listener entering acoustic zone", V(3.3f, 0, -.65f), Gold);
            var echo = new Transform[4];
            for (int i = 0; i < echo.Length; i++) echo[i] = Ring("Illustrated echo arrival", V(-2.55f, .07f, -.19f), .83f, Aqua);
            var outside = Ring("Direct arrival outside", V(2.6f, .07f, -.19f), .82f, Gold);
            return t =>
            {
                float moving = Range(t, .10f, .80f);
                listener.localPosition = V(Mathf.Lerp(3.15f, -2.7f, moving), 0, -.65f);
                float beat = Mathf.Repeat(t * (Second ? 2.7f : 2.1f), 1);
                outside.localScale = Vector3.one * (.22f + 1.68f * beat);
                outside.gameObject.SetActive(beat < .54f && (Second || moving < .49f));
                for (int i = 0; i < echo.Length; i++)
                {
                    float phase = beat - i * .13f;
                    echo[i].gameObject.SetActive((Second || moving > .39f) && phase > 0 && phase < .72f);
                    echo[i].localScale = Vector3.one * (.35f + 1.67f * Mathf.Clamp01(phase));
                }
            };
        }

        Action<float> Choir()
        {
            FrameCamera(V(0, 3, -14), V(0, 1.55f, 0), 3.9f);
            var mouths = new Transform[6];
            var singers = new Transform[6];
            var voices = new Transform[6];
            for (int i = 0; i < singers.Length; i++)
            {
                float x = -3.9f + i * 1.56f;
                singers[i] = Pawn("Own model ensemble member", V(x, 0, .4f), i % 2 == 0 ? Gold : Slate);
                singers[i].localScale = Vector3.one * 1.43f;
                mouths[i] = Orb("Articulation", V(0, .98f, -.15f), .115f, Ink, singers[i]);
                voices[i] = Block("Voice envelope icon", V(x, .15f, -1.45f), V(.22f, .28f, .23f), Aqua);
            }
            return t =>
            {
                for (int i = 0; i < singers.Length; i++)
                {
                    float pulse = Pulse(t * 4.4f + (Second ? i * i * .075f : 0));
                    if (Second) singers[i].localRotation = Quaternion.Euler((i % 3 - 1) * pulse * 9, 0, (i - 2.5f) * pulse * 3);
                    mouths[i].localScale = V(.10f, .041f + .11f * pulse, .105f);
                    voices[i].localScale = V(.22f, .14f + .61f * pulse, .23f);
                    voices[i].localPosition = V(-3.9f + i * 1.56f, .10f + .32f * pulse, -1.45f);
                }
            };
        }

        const int SurfaceLayer = 8;
        Transform Footprint(Vector3 p)
        {
            var footprint = Group("Projected test footprint", p);
            var pad = Orb("Footprint sole", V(0, 0, 0), .72f, Gold, footprint);
            pad.localScale = V(.32f, .025f, .64f);
            for (int i = -1; i <= 1; i++)
                Orb("Footprint toe", V(i * .088f, .012f, .31f), .082f, Gold, footprint).localScale = V(.082f, .016f, .11f);
            return footprint;
        }

        Action<float> Projection()
        {
            var ground = Block("Receiving surface", V(0, .02f, .0f), V(7.4f, .22f, 4.7f), Slate);
            ground.gameObject.layer = SurfaceLayer;
            var wall = Block("Rejected wall", V(1.45f, 1.05f, 1.55f), V(2.4f, 2.1f, .28f), Blue);
            wall.gameObject.layer = SurfaceLayer;
            var testFloor = V(-1.3f, .13f, -.35f);
            var extent = Ring("Projection bounds", testFloor + V(0, .03f, 0), .95f, Aqua);
            var target = Orb("Reconstructed world position", testFloor, .25f, Red);
            var path = Bar("Camera ray", V(0, 2, -3), testFloor, .035f, Paper);
            var footprint = Footprint(testFloor + V(0, .02f, 0));
            Physics.SyncTransforms();
            return t =>
            {
                float angle = Mathf.Lerp(-.4f, .5f, Ease(t)) + (Second ? .18f : 0);
                FrameCamera(V(Mathf.Sin(angle) * 12, 6.4f, -Mathf.Cos(angle) * 12), V(.1f, .52f, 0), 3.75f);
                Vector3 candidate = Second && t > .55f ? V(1.45f, 1.03f, 1.41f) : testFloor;
                Vector3 viewport = view.WorldToViewportPoint(candidate);
                var ray = view.ViewportPointToRay(viewport);
                if (!Physics.Raycast(ray, out var hit, 80, 1 << SurfaceLayer)) return;
                float depth = Vector3.Dot(hit.point - view.transform.position, view.transform.forward);
                Vector3 fixedPosition = view.ViewportToWorldPoint(V(viewport.x, viewport.y, depth));
                target.localPosition = fixedPosition + hit.normal * .13f;
                bool valid = Vector3.Dot(hit.normal, Vector3.up) > .75f &&
                    (fixedPosition - testFloor).sqrMagnitude < .95f * .95f;
                Tint(target, valid ? Aqua : Red);
                Segment(path, fixedPosition - ray.direction * 3.2f, fixedPosition, .039f);
                extent.gameObject.SetActive(Second || t > .28f);
                footprint.gameObject.SetActive(Second || t > .39f);
            };
        }

        Action<float> FramePacing()
        {
            FrameCamera(V(0, 5, -12), V(0, .5f, 0), 4.15f);
            var stable = Orb("Even frame arrival", V(-4, .45f, 1.35f), .54f, Aqua);
            var irregular = Orb("Uneven frame arrival", V(-4, .45f, -.85f), .54f, Gold);
            Route(Aqua, V(-4, .07f, 1.35f), V(4, .07f, 1.35f));
            Route(Slate, V(-4, .07f, -.85f), V(4, .07f, -.85f));
            float[] schedule = {0, .083f, .17f, .254f, .48f, .51f, .55f, .61f, .73f, .81f, .90f, .975f};
            var marks = new Transform[schedule.Length];
            for (int i = 0; i < marks.Length; i++)
                marks[i] = Block("Frame interval sample", V(-4 + i * .69f, .1f, -2.05f), V(.4f, .2f, .37f), Slate);
            return t =>
            {
                int index = 0;
                while (index + 1 < schedule.Length && schedule[index + 1] <= t) index++;
                stable.localPosition = V(-4 + 8 * t, .40f, 1.35f);
                irregular.localPosition = V(-4 + 8 * schedule[index], .40f, -.85f);
                for (int i = 0; i < marks.Length; i++)
                {
                    float delta = i == 0 ? .08f : schedule[i] - schedule[i - 1];
                    marks[i].localScale = V(.40f, delta * (Second ? 7 : 3.5f), .44f);
                    marks[i].localPosition = V(-4 + i * .69f, marks[i].localScale.y * .5f + .04f, -2.15f);
                    Tint(marks[i], i <= index ? delta > .15f ? Red : Aqua : Slate);
                }
            };
        }

        Action<float> Comparison()
        {
            var boxes = new Transform[2, 6];
            for (int side = 0; side < 2; side++)
            {
                float offset = side == 0 ? -2.6f : 2.6f;
                Block("Controlled scene platform", V(offset, .01f, 0), V(4.45f, .15f, 4.4f), Slate);
                for (int i = 0; i < 6; i++)
                    boxes[side, i] = Block("Common render test objects",
                        V(offset + (i % 3 - 1) * 1.10f, .5f, (i / 3 - .5f) * 1.28f),
                        V(.66f, 1.0f, .69f), i == 2 ? Gold : Aqua);
            }
            var focus = Ring("Controlled camera position", V(-2.6f, .15f, 0), 1.6f, Paper);
            return t =>
            {
                bool controlled = Second || t > .48f;
                focus.localPosition = V(Mathf.Lerp(-2.6f, 2.6f, Range(t, .25f, .72f)), .17f, 0);
                for (int i = 0; i < 6; i++)
                {
                    float motion = 32 * t + 14 * i;
                    boxes[0, i].localRotation = Quaternion.Euler(0, motion, 0);
                    boxes[1, i].localRotation = Quaternion.Euler(0, controlled ? motion : -54 + motion, 0);
                    if (!controlled) Tint(boxes[1, i], i == 2 ? Gold : Red);
                    else Tint(boxes[1, i], i == 2 ? Gold : Second && i == 4 && t > .58f ? Blue : Aqua);
                }
            };
        }

        Action<float> TargetModifier()
        {
            var strike = Pawn("Same attacker and move", V(-3.2f, 0, 0), Gold);
            Pawn("Non-player target", V(2.3f, 0, 1.7f), Slate);
            Pawn("Player target", V(2.3f, 0, -1.7f), Aqua);
            var shots = new[] { V(2.3f, .1f, 1.7f), V(2.3f, .1f, -1.7f) };
            var traces = new Transform[2];
            var bars = new Transform[2];
            for (int j = 0; j < 2; j++)
            {
                traces[j] = Bar("Same action toward two target types", V(-3.2f, .12f, 0), shots[j], .075f, Slate);
                bars[j] = Block("Illustrative result", shots[j] + V(1.02f, .18f, 0), V(.38f, .38f, .39f), j == 0 ? Paper : Aqua);
            }
            return t =>
            {
                float hit = Range(t, .30f, .69f);
                strike.Find("Right sleeve").localRotation = Quaternion.Euler(-75 * Range(t, .15f, .43f), 0, 15);
                for (int j = 0; j < 2; j++)
                {
                    Tint(traces[j], hit > .22f ? j == 0 ? Paper : Aqua : Slate);
                    float h = .36f + hit * (j == 1 && Second ? 1.12f : .53f);
                    bars[j].localPosition = shots[j] + V(1.02f, h / 2, 0);
                    bars[j].localScale = V(.38f, h, .39f);
                }
            };
        }

        Action<float> RayOption()
        {
            var sample = Orb("Ray target", V(3.4f, .45f, 1.55f), .93f, Blue);
            sample.gameObject.layer = SurfaceLayer;
            var pad = Block("Reflecting plane", V(0, .025f, 0), V(6.8f, .20f, 3.5f), Slate);
            var first = Bar("Incident ray", V(-3.6f, 2.18f, -.3f), V(0, .13f, .29f), .065f, Gold);
            var second = Bar("Reflected ray", V(0, .13f, .29f), V(3.4f, .45f, 1.55f), .065f, Aqua);
            var toggle = Block("Enabled option", V(1.1f, .31f, -2.13f), V(1.1f, .5f, .53f), Blue);
            Physics.SyncTransforms();
            return t =>
            {
                Vector3 from = V(-3.6f, 2.15f, -.70f + .45f * t), bounce = V(0, .13f, .28f);
                Vector3 direction = Vector3.Reflect((bounce - from).normalized, Vector3.up);
                var endpoint = Physics.Raycast(bounce + direction * .02f, direction, out var hit, 4.2f, 1 << SurfaceLayer)
                    ? hit.point : bounce + direction * 4.2f;
                Segment(first, from, bounce, .066f);
                Segment(second, bounce, Vector3.Lerp(bounce, endpoint, Range(t, .49f, .88f)), .066f);
                second.gameObject.SetActive(t > (Second ? .36f : .52f));
                Tint(pad, t > .49f ? Blue : Slate);
                Tint(toggle, t > .49f ? Aqua : Slate);
            };
        }

        Action<float> ProgressCurve()
        {
            FrameCamera(V(0, 3.3f, -13), V(0, 1.4f, 0), 3.7f);
            var before = new Transform[8];
            var after = new Transform[8];
            for (int i = 0; i < before.Length; i++)
            {
                float x = -4.05f + 1.15f * i;
                before[i] = Block("Earlier schematic progression", V(x, .05f, .8f), V(.49f, .1f, .5f), Slate);
                after[i] = Block("Rebalanced schematic progression", V(x, .05f, -.20f), V(.49f, .1f, .5f), Aqua);
            }
            return t =>
            {
                for (int i = 0; i < before.Length; i++)
                {
                    float x = (i + 1) / 8f;
                    float shown = Range(t, .055f * i, .38f + i * .056f);
                    float a = Mathf.Max(.05f, x * 2.65f * shown), b = Mathf.Max(.05f, Mathf.Sqrt(x) * 2.65f * shown);
                    before[i].localScale = V(.49f, a, .50f);
                    after[i].localScale = V(.49f, b, .50f);
                    before[i].localPosition = V(before[i].localPosition.x, a / 2, .8f);
                    after[i].localPosition = V(after[i].localPosition.x, b / 2, -.20f);
                    Tint(after[i], Second && i < 3 ? Gold : Aqua);
                }
            };
        }

        Action<float> Retry()
        {
            var enemy = Pawn("Visible challenge", V(1.1f, 0, .6f), Red);
            enemy.localScale = Vector3.one * 1.8f;
            var player = Pawn("Retried action", V(-4.1f, 0, -.5f), Gold);
            var mark = Ring("Observed danger zone", V(.25f, .04f, -.08f), 1.03f, Red);
            Route(Slate, V(-4.1f, .075f, -.55f), V(.6f, .075f, -.55f));
            if (Second) Route(Aqua, V(-3.6f, .07f, -.55f), V(-.8f, .07f, -1.95f), V(2.3f, .07f, -1.95f));
            return t =>
            {
                float a = Range(t, .06f, .39f), b = Range(t, .51f, .66f), c = Range(t, .67f, .94f);
                Vector3 p = Vector3.Lerp(V(-4.1f, 0, -.53f), V(.40f, 0, -.53f), a);
                p = Vector3.Lerp(p, V(-3.45f, 0, -.53f), b);
                p = Vector3.Lerp(p, Second ? V(2.55f, 0, -1.95f) : V(-.52f, 0, -.53f), c);
                player.localPosition = p;
                enemy.Find("Right sleeve").localRotation = Quaternion.Euler(-85 * Range(t, .25f, .40f) + 109 * Range(t, .41f, .65f), 0, 15);
                mark.gameObject.SetActive(t > .36f && (Second || t < .58f));
            };
        }

        Action<float> Cooperation()
        {
            var host = Pawn("Host", V(-4.1f, 0, -1.05f), Gold);
            var partner = Pawn("Joining player", V(-1.45f, 0, -2.15f), Aqua);
            var indicator = Ring("Invitation interaction", V(-1.39f, .08f, -.72f), .56f, Paper);
            var gate = Landmark("Shared challenge", V(3.4f, 0, 1.2f), 2.1f, Blue);
            var common = Ring("Shared goal", V(3, .07f, .8f), 1.4f, Aqua);
            Route(Slate, V(-4.1f, .07f, -1.05f), V(-1.39f, .07f, -.72f), V(3.12f, .07f, .8f));
            return t =>
            {
                var meet = V(-1.42f, 0, -.72f);
                float a = Range(t, .10f, .48f), b = Range(t, .51f, .94f);
                indicator.gameObject.SetActive(t > .08f && (Second || t < .62f));
                host.localPosition = Vector3.Lerp(Vector3.Lerp(V(-4.1f, 0, -1.05f), meet, a), V(2.0f, 0, .56f), b);
                partner.gameObject.SetActive(t > .38f);
                partner.localPosition = Vector3.Lerp(V(-1.45f, 0, -2.15f), V(2.17f, 0, -.16f), b);
                common.gameObject.SetActive(t > .62f);
                Tint(gate, t > .85f ? Aqua : Blue);
            };
        }
    }
}
