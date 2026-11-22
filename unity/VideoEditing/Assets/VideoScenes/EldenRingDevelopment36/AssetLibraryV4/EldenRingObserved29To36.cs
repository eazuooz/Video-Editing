using System;
using System.Linq;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        static readonly Color Field29To36 = new Color32(75, 95, 76, 255);
        static readonly Color Stone29To36 = new Color32(105, 124, 123, 255);

        Action<float> BuildObserved29To36()
        {
            switch (episode)
            {
                case 29: return ObservedProjection();
                case 30: return ObservedFramePacing();
                case 31: return ObservedComparison();
                case 32: return ObservedTargetModifier();
                case 33: return ObservedVisibilityOption();
                case 34: return ObservedProgressCurve();
                case 35: return ObservedRetry();
                case 36: return ObservedCooperation();
                default: throw new ArgumentOutOfRangeException(nameof(episode));
            }
        }

        WalkthroughActor ObservedRig(string name, Vector3 position, Color color)
        {
            var root = Group(name, position);
            AddWalkthroughActor(root, color);
            return walkthroughActors[walkthroughActors.Count - 1];
        }

        Action<float> ObservedProjection()
        {
            Floor("Stone courtyard", 0, .1f, 9.3f, 6.2f, 0, Stone29To36);
            var surface = Block("Ground target for test ray", V(0, -.08f, 0), V(8.5f, .19f, 5.7f), Stone29To36);
            surface.gameObject.layer = SurfaceLayer;
            var wall = Block("Wall target for test ray", V(2.1f, .95f, 1.6f), V(3.6f, 1.9f, .24f), Blue);
            wall.gameObject.layer = SurfaceLayer;
            for (int i = 0; i < 7; i++)
                Block("Stone seam along the observed path", V(0, .024f, -2.24f + .67f * i),
                    V(8.5f, .017f, .023f), Slate);
            Attach("paving", Group("Paving texture at foot level", V(-3.2f, .024f, 1.18f)),
                V(2.1f, .13f, 1.8f), true);
            GroundGate("Exit beside the wall", V(-1.25f, 0, 2.56f), 1.78f, 1.90f, Stone29To36);

            var walker = ObservedRig("Walk over stone across the changing view", V(-3.2f, .020f, -.64f), Gold);
            var marks = new Transform[3];
            for (int i = 0; i < marks.Length; i++)
            {
                marks[i] = Footprint(V(-2.6f + 1.11f * i, .036f, -.64f + (i % 2) * .19f));
                marks[i].localRotation = Quaternion.Euler(0, 90, 0);
            }
            Vector3 floorPoint = V(1.42f, .015f, -.68f);
            Vector3 wallPoint = V(2.13f, .96f, 1.48f);
            var reconstructed = Orb("Reconstructed point on test surface", floorPoint, .20f, Aqua);
            var normal = Bar("Direction of receiving surface", floorPoint, floorPoint + Vector3.up, .05f, Paper);
            var raySegment = Bar("Visible part of camera ray", floorPoint, floorPoint + Vector3.up, .042f, Gold);
            var accepted = Footprint(floorPoint + V(0, .025f, 0));
            var indicator = Ring("Footprint bounds on the floor", floorPoint + V(0, .014f, 0), .70f, Aqua);
            Physics.SyncTransforms();

            return t =>
            {
                walker.Root.localPosition = V(Mathf.Lerp(-3.2f, .85f, Range(t, .04f, .66f)), .020f, -.64f);
                for (int i = 0; i < marks.Length; i++)
                    marks[i].gameObject.SetActive(!Second && t >= .17f + .12f * i);
                if (!Second)
                {
                    float turn = Range(t, .10f, .89f);
                    FrameCamera(V(Mathf.Lerp(-4.5f, 5.6f, turn), 4.70f, -8.8f), V(-.42f, .25f, .02f), 3.27f);
                }
                else
                    FrameCamera(V(Mathf.Lerp(-2.4f, 2.6f, Range(t, .08f, .88f)), 4.45f, -9.3f),
                        V(.7f, .40f, .22f), 3.62f);

                Vector3 chosen = Second && t < .62f ? wallPoint : floorPoint;
                Vector3 viewport = view.WorldToViewportPoint(chosen);
                Ray ray = view.ViewportPointToRay(viewport);
                bool found = Physics.Raycast(ray, out var hit, 80, 1 << SurfaceLayer);
                bool showTest = found && (Second || t > .44f);
                reconstructed.gameObject.SetActive(showTest);
                normal.gameObject.SetActive(showTest);
                raySegment.gameObject.SetActive(showTest);
                indicator.gameObject.SetActive(Second && t > .27f);
                accepted.gameObject.SetActive(false);
                if (!showTest) return;
                float depth = Vector3.Dot(hit.point - view.transform.position, view.transform.forward);
                Vector3 location = view.ViewportToWorldPoint(V(viewport.x, viewport.y, depth));
                bool valid = Vector3.Dot(hit.normal, Vector3.up) > .75f &&
                    Vector3.Distance(location, floorPoint) < .74f;
                reconstructed.localPosition = location + hit.normal * .11f;
                Segment(raySegment, location - ray.direction * 2.6f, location, .045f);
                Segment(normal, location, location + hit.normal * .57f, .051f);
                Tint(reconstructed, valid ? Aqua : Red);
                Tint(normal, valid ? Aqua : Red);
                accepted.gameObject.SetActive(valid);
            };
        }

        Action<float> ObservedHeldWalk(WalkthroughActor actor, bool steady, float[] timing, float lane)
        {
            var pieces = actor.Parts.ToArray();
            var held = new Mesh[pieces.Length];
            for (int i = 0; i < pieces.Length; i++)
            {
                var part = pieces[i];
                held[i] = new Mesh { name = "Same pose until the next scheduled display update" };
                owned.Add(held[i]);
                part.Source.BakeMesh(held[i], false);
                var renderer = part.Source.GetComponentsInChildren<MeshFilter>(true)
                    .First(filter => filter.sharedMesh == part.PosedMesh);
                renderer.sharedMesh = held[i];
            }
            int previousIndex = -1, index = 0;
            Vector3 holdPosition = actor.BaseAnchor;
            actor.FixedFacing = true;
            actor.Root.localRotation = Quaternion.Euler(0, 90, 0);
            actor.AfterPose = () =>
            {
                if (index != previousIndex)
                {
                    for (int i = 0; i < pieces.Length; i++) pieces[i].Source.BakeMesh(held[i], false);
                    holdPosition = actor.RigAnchor.localPosition;
                    previousIndex = index;
                }
                actor.RigAnchor.localPosition = holdPosition;
            };
            return clock =>
            {
                index = 0;
                while (index + 1 < timing.Length && timing[index + 1] <= clock) index++;
                float sample = steady ? index / (float)(timing.Length - 1) : timing[index];
                actor.Root.localPosition = V(Mathf.Lerp(-4.05f, 4.05f, sample), .038f, lane);
            };
        }

        Action<float> ObservedFramePacing()
        {
            Floor("Matched hillside courses", 0, .1f, 10.4f, 6.3f, 0, Field29To36);
            var stable = ObservedRig("Regularly spaced frame display", V(-4.05f, .038f, 1.20f), Aqua);
            var burst = ObservedRig("Uneven frame display", V(-4.05f, .038f, -.92f), Gold);
            float[] regular = { 0, .125f, .25f, .375f, .5f, .625f, .75f, .875f, 1 };
            float[] irregular = { 0, .075f, .20f, .45f, .50f, .56f, .755f, .895f, 1 };
            var playStable = ObservedHeldWalk(stable, true, regular, 1.2f);
            var playBurst = ObservedHeldWalk(burst, false, irregular, -.92f);
            var bars = new Transform[2, 8];
            for (int row = 0; row < 2; row++)
            {
                float z = row == 0 ? 1.2f : -.92f;
                Floor("Walk on corresponding ground strip", 0, z, 9.9f, .92f, .03f, Stone29To36);
                Attach("rock", Group("Same bend beside lane", V(.95f, 0, z + .66f)), V(1.1f, .89f, .68f), true);
                for (int i = 0; i < 8; i++)
                {
                    float height = (row == 0 ? regular[i + 1] - regular[i] : irregular[i + 1] - irregular[i]) * 2.15f;
                    bars[row, i] = Block("Elapsed time of a frame interval", V(-3.55f + i * 1.01f, height * .5f,
                        -2.55f + .55f * row), V(.45f, height, .29f), Slate);
                }
            }
            Tree(V(-3.1f, 0, 2.35f), .85f);
            Tree(V(3.5f, 0, 2.55f), .86f);
            return t =>
            {
                float time = Mathf.InverseLerp(.10f, .91f, t);
                playStable(time);
                playBurst(time);
                float turn = Range(t, .0f, .10f) - .3f * Range(t, .91f, 1);
                FrameCamera(V(Mathf.Lerp(3.35f, .20f, turn), 6.05f, -10.6f),
                    V(0, .38f, .07f), Second ? 3.63f : 3.78f);
                for (int i = 0; i < 8; i++)
                {
                    Tint(bars[0, i], time >= regular[i + 1] ? Aqua : Slate);
                    Tint(bars[1, i], time >= irregular[i + 1] ?
                        (irregular[i + 1] - irregular[i] > .17f ? Red : Gold) : Slate);
                }
            };
        }

        Action<float> ObservedComparison()
        {
            Floor("Common hill test scene", 0, .1f, 10.5f, 6.6f, 0, Field29To36);
            Floor("Walkable stone track", -.2f, -.64f, 7.85f, 1.18f, .035f, Stone29To36);
            Attach("cliff", Group("Tall rock behind the test route", V(.40f, 0, 1.25f)), V(3.10f, 2.13f, 1.15f), true);
            GroundGate("Distant arch at the end", V(3.25f, .03f, .44f), 1.34f, 2.17f, Stone29To36);
            Tree(V(-2.44f, 0, 1.5f), 1.25f);
            Tree(V(.65f, 0, 2.58f), .85f);
            var walker = ObservedRig("Same route for both test takes", V(-3.42f, .036f, -.64f), Gold);
            var one = Ring("First measurement condition", V(-3.6f, .05f, -1.95f), .38f, Aqua);
            var two = Ring("Second measurement condition", V(3.65f, .05f, -1.95f), .38f, Gold);
            var control = Block("Only one comparison option is highlighted", V(0, .11f, -2.28f),
                V(.63f, .16f, .35f), Slate);
            bool previousTake = false;
            return t =>
            {
                bool secondTake = t >= .50f;
                if (previousTake != secondTake)
                {
                    walker.PreviousTime = -1;
                    walker.Distance = 0;
                    previousTake = secondTake;
                }
                float inTake = Mathf.Repeat(t * 2f, 1);
                if (t > .998f) inTake = 1;
                float advance = Range(inTake, .06f, .94f);
                float x = Mathf.Lerp(-3.42f, 3.03f, advance);
                walker.Root.localPosition = V(x, .036f, -.64f);
                var from = V(x * .36f - 2.2f, 3.48f, -8.2f);
                var at = V(x * .28f, .68f, .24f);
                if (!Second && secondTake)
                {
                    from = V(x * .38f + 4.42f, 5.15f, -7.2f);
                    at = V(x * .28f + .54f, .84f, .28f);
                }
                FrameCamera(from, at, 3.52f);
                one.gameObject.SetActive(!secondTake);
                two.gameObject.SetActive(secondTake);
                Tint(control, Second && secondTake ? Gold : Slate);
            };
        }

        void ObservedHandTool(WalkthroughActor actor, Color color, float extension, bool staff = false)
        {
            var handle = Bar("Tool grip remains in the right hand", Vector3.zero, Vector3.up, .074f, Slate);
            var head = Bar("Visible tool held by the rig", Vector3.zero, Vector3.up, staff ? .058f : .125f, color);
            var wrist = actor.Arms[1].End;
            actor.AfterPose = () =>
            {
                Vector3 grip = stage.InverseTransformPoint(wrist.position);
                float angle = (actor.PosePhase * 105f - 69f) * Mathf.Deg2Rad;
                Vector3 axis = (actor.Root.forward * Mathf.Cos(angle) + Vector3.up * Mathf.Sin(angle)
                    + actor.Root.right * .19f).normalized;
                Segment(handle, grip - axis * .17f, grip + axis * .23f, .075f);
                Segment(head, grip + axis * .20f, grip + axis * extension, staff ? .062f : .132f);
            };
        }

        Action<float> ObservedTargetModifier()
        {
            Floor("Controllable arena and practice path", 0, 0, 9.6f, 6.0f, 0, Stone29To36);
            Ring("Practice arena boundary", V(.25f, .035f, .15f), 2.47f, Slate);
            GroundGate("Gate behind both target types", V(2.0f, 0, 2.47f), 1.60f, 2.13f, Slate);
            var player = ObservedRig("Same move and distance across both cases", V(-3.57f, 0, .03f), Gold);
            player.FixedFacing = true;
            player.Root.localRotation = Quaternion.Euler(0, 90, 0);
            ObservedHandTool(player, Paper, .90f);
            var opponent = ObservedRig("Player target", V(.82f, 0, .06f), Aqua);
            opponent.FixedFacing = true;
            opponent.Root.localRotation = Quaternion.Euler(0, -90, 0);
            var other = Group("Training opponent for PvE illustration", V(.82f, 0, .06f));
            Attach("shield", other, V(.66f, 1.55f, .60f), true);
            var otherMark = Ring("Separate non-player target", other.localPosition + V(0, .045f, 0), .40f, Gold);
            var bars = new [] {
                Block("Illustrative unchanged PvE result", V(1.1f, .11f, -2.15f), V(.48f, .22f, .38f), Paper),
                Block("Illustrative PvP adjustment", V(2.2f, .11f, -2.15f), V(.48f, .22f, .38f), Aqua)
            };
            var hit = Orb("Moment of impact", V(.65f, 1, .15f), .32f, Gold);
            bool lastCase = !Second;
            return t =>
            {
                bool pvp = Second ? t >= .50f : t < .50f;
                if (pvp != lastCase)
                {
                    player.PreviousTime = -1;
                    player.Distance = 0;
                    lastCase = pvp;
                }
                float move = t > .998f ? 1 : Mathf.Repeat(t * 2f, 1);
                player.Root.localPosition = V(Mathf.Lerp(-3.57f, -.49f, Range(move, .03f, .42f)), 0, .03f);
                player.Cast = Range(move, .29f, .52f) * (1 - Range(move, .66f, .89f));
                player.PosePhase = Range(move, .30f, .52f) * (1 - Range(move, .57f, .77f));
                opponent.Root.localPosition = V(.82f + .44f * Range(move, .58f, .76f), 0, .06f);
                opponent.Cast = .38f * Range(move, .43f, .56f) * (1 - Range(move, .72f, .97f));
                opponent.Root.gameObject.SetActive(pvp);
                other.gameObject.SetActive(!pvp);
                otherMark.gameObject.SetActive(!pvp);
                hit.gameObject.SetActive(move >= .57f && move < .68f);
                for (int i = 0; i < bars.Length; i++)
                {
                    bool shown = move > .57f && ((i == 1) == pvp || t > .69f);
                    float height = shown ? (i == 0 ? .80f : 1.18f) : .17f;
                    bars[i].localScale = V(.48f, height, .38f);
                    bars[i].localPosition = V(1.1f + i * 1.1f, .04f + height * .5f, -2.15f);
                    Tint(bars[i], shown ? (i == 0 ? Paper : Aqua) : Slate);
                }
                FrameCamera(V(Mathf.Lerp(-1.3f, 1.15f, Range(move, .07f, .80f)), 4.1f, -9.8f),
                    V(-.25f, .7f, .04f), 3.45f);
            };
        }

        Action<float> ObservedVisibilityOption()
        {
            var snow = new Color32(193, 208, 203, 255);
            Floor("Snowy practice ground", 0, .20f, 9.95f, 6.5f, 0, snow);
            Attach("rock", Group("Boulder at the end of the snowy lane", V(.35f, 0, .72f)), V(1.38f, 1.15f, 1.15f), true);
            GroundGate("Wall opening in snow", V(2.9f, 0, 2.53f), 1.53f, 2.20f, Stone29To36);
            var blocker = Block("Ray-test stone volume", V(.35f, .53f, .72f), V(1.03f, 1.07f, .91f), Stone29To36);
            blocker.gameObject.layer = SurfaceLayer;
            blocker.GetComponent<Renderer>().enabled = false;
            const int columns = 7, rows = 5;
            var tiles = new Transform[columns, rows];
            var visible = new bool[columns, rows];
            Vector3 light = V(-1.05f, 2.0f, -.43f).normalized;
            Physics.SyncTransforms();
            for (int x = 0; x < columns; x++)
            for (int z = 0; z < rows; z++)
            {
                Vector3 at = V(.20f + x * .27f, .019f, .17f + z * .27f);
                tiles[x, z] = Block("Checked visibility of a sample on snow", at, V(.252f, .024f, .252f), snow);
                visible[x, z] = !Physics.Raycast(at + Vector3.up * .015f, light, 4.0f, 1 << SurfaceLayer);
            }
            var walker = ObservedRig("Arrive at a fixed view", V(-3.65f, 0, -.98f), Gold);
            var option = Block("Switch the illustration overlay only", V(3.65f, .12f, -1.95f), V(.83f, .22f, .36f), Slate);
            var scan = Bar("Visibility test towards light source", V(.92f, .02f, .74f), V(-.35f, 2.10f, .11f), .046f, Gold);
            return t =>
            {
                var progress = Range(t, .05f, .40f);
                walker.Root.localPosition = V(Mathf.Lerp(-3.65f, -1.04f, progress), 0, -.98f);
                var settle = Range(t, .03f, .43f);
                FrameCamera(V(Mathf.Lerp(-4.40f, .03f, settle), 4.61f, -8.75f),
                    V(.12f, .44f, .27f), 3.23f);
                bool show = t >= (Second ? .59f : .49f);
                scan.gameObject.SetActive(!Second && show);
                Tint(option, show ? Aqua : Slate);
                for (int x = 0; x < columns; x++)
                for (int z = 0; z < rows; z++)
                    Tint(tiles[x, z], show && !visible[x, z] ? Slate : snow);
            };
        }

        Action<float> ObservedProgressCurve()
        {
            Floor("Grassy path like the visible fragment approach", 0, 0, 10.3f, 6.0f, 0, Field29To36);
            var seeker = ObservedRig("Walk toward a fragment marker", V(-4.2f, 0, -1.36f), Gold);
            var pickup = Orb("Concept illustration marker", V(-2.10f, .29f, -1.36f), .28f, Gold);
            var glow = Bar("Location before examining the marker", V(-2.1f, .3f, -1.36f),
                V(-2.1f, 1.31f, -1.36f), .048f, Gold);
            Attach("grass", Group("Taller grass beside both routes", V(-3.2f, 0, .95f)), V(2.1f, .9f, .58f), true);
            var before = new Transform[7];
            var after = new Transform[7];
            for (int i = 0; i < before.Length; i++)
            {
                float x = -3.44f + i * 1.12f;
                before[i] = Block("Schematic earlier balance", V(x, .02f, .46f), V(.46f, .04f, .41f), Paper);
                after[i] = Block("Schematic adjusted balance", V(x, .02f, 1.27f), V(.46f, .04f, .41f), Aqua);
            }
            return t =>
            {
                float pace = .32f * Range(t, .02f, .24f) + .68f * Range(t, .32f, .96f);
                seeker.Root.localPosition = V(Mathf.Lerp(-4.2f, 2.58f, pace), 0, -1.36f);
                pickup.gameObject.SetActive(t < .28f);
                glow.gameObject.SetActive(t < .28f);
                for (int i = 0; i < before.Length; i++)
                {
                    float reveal = Range(t, .20f + .076f * i, .32f + .086f * i);
                    float level = (i + 1f) / before.Length;
                    float hA = Mathf.Lerp(.04f, 2.12f * level, reveal);
                    float hB = Mathf.Lerp(.04f, 2.12f * Mathf.Sqrt(level), reveal);
                    before[i].localScale = V(.46f, hA, .41f);
                    after[i].localScale = V(.46f, hB, .41f);
                    before[i].localPosition = V(-3.44f + i * 1.12f, hA / 2, .46f);
                    after[i].localPosition = V(-3.44f + i * 1.12f, hB / 2, 1.27f);
                    Tint(after[i], (Second && i < 3 && reveal > .25f) ? Gold : Aqua);
                }
                float angle = Range(t, .12f, .78f);
                FrameCamera(V(Mathf.Lerp(-3.9f, .6f, angle), 4.5f + .62f * angle, -8.5f),
                    V(Mathf.Lerp(-1.65f, .15f, angle), .74f, .21f), 3.52f);
            };
        }

        Action<float> ObservedRetry()
        {
            Floor("Open ground usable for either approach", 0, .1f, 10.2f, 6.4f, 0, Field29To36);
            Tree(V(-2.45f, 0, 2.46f), 1.12f);
            Attach("rock", Group("Side outcrop to read the change in distance", V(2.84f, 0, 2.63f)),
                V(1.82f, 1.43f, .8f), true);
            var mount = Group("Original shared horse for the practice rider", V(1.12f, 0, .52f));
            Attach("horse", mount, V(1.95f, 1.32f, 1.31f), true, 90);
            var rider = ObservedRig("Mounted practice opponent", V(1.04f, .80f, .52f), Red);
            rider.Root.localScale = Vector3.one * .92f;
            rider.FixedFacing = true;
            rider.Root.localRotation = Quaternion.Euler(0, -103, 0);
            rider.Root.Find("Current player position").gameObject.SetActive(false);
            ObservedHandTool(rider, Paper, 1.17f);
            var player = ObservedRig("Practice player chooses approach", V(-4.27f, 0, -.55f), Gold);
            var danger = Ring("Previous approach and swing area", V(-.27f, .034f, .14f), 1.22f, Red);
            var side = Ring("Open escape space", V(.26f, .037f, -2.04f), .47f, Aqua);
            if (Second)
                Route(Aqua, V(-1.75f, .055f, -.55f), V(-1.31f, .055f, -1.85f), V(.28f, .055f, -2.04f));
            else
                Route(Gold, V(-4.27f, .055f, -.55f), V(-.77f, .055f, -.55f));
            return t =>
            {
                float approaching = Range(t, .05f, .45f);
                float avoid = Range(t, .47f, .75f);
                var approach = Vector3.Lerp(V(-4.27f, 0, -.55f), V(-.98f, 0, -.55f), approaching);
                player.Root.localPosition = Second
                    ? approach + V(1.13f * Range(t, .72f, .97f), 0, -1.49f * avoid)
                    : approach - V(.94f * avoid, 0, 0);
                float raised = Range(t, .27f, .48f), fall = Range(t, .51f, .68f);
                rider.Cast = raised * (1 - .69f * fall) * (1 - Range(t, .72f, .90f));
                rider.PosePhase = raised * (1 - fall);
                Quaternion body = Quaternion.Euler(0, -5 * raised + 18 * fall, -3 * raised + 3 * fall);
                mount.localRotation = body;
                mount.localPosition = V(1.12f - .26f * fall, 0, .52f);
                rider.Root.localPosition = V(1.04f - .26f * fall, .80f + .09f * raised, .52f);
                danger.gameObject.SetActive(t >= (Second ? .20f : .43f));
                side.gameObject.SetActive(Second && t > .51f);
                float cameraTurn = Range(t, .13f, .77f);
                FrameCamera(V(Mathf.Lerp(-3.4f, 2.1f, cameraTurn), 4.57f, -9.85f),
                    V(Mathf.Lerp(-.96f, -.01f, cameraTurn), .62f, -.23f), 3.64f);
            };
        }

        Action<float> ObservedCooperation()
        {
            Floor("Open practice ground framed by a gate", 0, 0, 10.5f, 6.2f, 0, Field29To36);
            Floor("Path through the same arch", .4f, -.65f, 8.9f, 1.45f, .046f, Stone29To36);
            GroundGate("Shared objective opening", V(3.2f, 0, 1.57f), 1.66f, 2.31f, Stone29To36);
            Tree(V(-3.7f, 0, 1.77f), 1.11f);
            Tree(V(.1f, 0, 2.40f), .69f);
            Attach("rock", Group("Low cover beside the position behind the front player", V(-.08f, 0, -2.22f)),
                V(1.55f, .56f, .77f), true);
            var host = ObservedRig("Front player", V(-3.60f, .047f, -.64f), Gold);
            var partner = ObservedRig("Ally prepares from a separate position", V(-2.2f, 0, -1.95f), Aqua);
            var sign = Ring("Only our demo shows this willing-to-help marker", V(-1.61f, .061f, -.51f), .60f, Paper);
            var mark = Ring("Meeting location at the gate", V(3.18f, .064f, 1.46f), .89f, Aqua);
            var threat = Group("Generic obstacle for a shared encounter", V(3.28f, 0, .25f));
            Attach("shield", threat, V(1.1f, 1.56f, .75f), true);
            var spell = Orb("Visible cooperation cue", V(-.08f, 1.20f, -1.16f), .19f, Aqua);
            var endpoint = Ring("Both positions address one target", V(3.20f, .062f, .28f), .54f, Red);
            Transform wrist = partner.Arms[1].End;
            if (Second)
            {
                partner.FixedFacing = true;
                partner.Root.localRotation = Quaternion.Euler(0, 64, 0);
                ObservedHandTool(partner, Aqua, .77f, true);
            }
            return t =>
            {
                float meet = Range(t, .06f, .42f), proceed = Range(t, .47f, .94f);
                host.Root.localPosition = Vector3.Lerp(Vector3.Lerp(V(-3.60f, .047f, -.64f),
                    V(-1.35f, .047f, -.64f), meet), Second ? V(2.16f, .047f, -.21f) : V(2.76f, .047f, -.34f), proceed);
                partner.Root.localPosition = Vector3.Lerp(Vector3.Lerp(V(-2.2f, 0, -1.95f), V(-1.64f, 0, -1.22f),
                    meet), Second ? V(-.05f, 0, -1.60f) : V(2.35f, .047f, -.95f), proceed);
                if (!Second)
                {
                    float turnThrough = Range(t, .74f, .97f);
                    host.Root.localPosition += V(.55f, -.042f, 2.18f) * turnThrough;
                    partner.Root.localPosition += V(.46f, -.042f, 2.24f) * turnThrough;
                }
                host.Cast = Second ? .46f * Range(t, .57f, .73f) * (1 - Range(t, .79f, .96f)) : 0;
                partner.Cast = Second ? Range(t, .58f, .73f) * (1 - Range(t, .83f, .97f)) : 0;
                partner.PosePhase = partner.Cast;
                sign.gameObject.SetActive(!Second && t < .52f);
                mark.gameObject.SetActive(!Second && t > .62f);
                threat.gameObject.SetActive(Second);
                endpoint.gameObject.SetActive(Second && t > .48f);
                spell.gameObject.SetActive(Second && t >= .72f && t <= .95f);
                spell.localPosition = Vector3.Lerp(stage.InverseTransformPoint(wrist.position),
                    V(3.20f, .81f, .28f), Range(t, .70f, .95f));
                float cameraTurn = Range(t, .13f, .90f);
                FrameCamera(V(Mathf.Lerp(-3.65f, 2.58f, cameraTurn), 4.10f + .55f * cameraTurn, -9.48f),
                    V(Mathf.Lerp(-1.01f, .65f, cameraTurn), .67f, -.21f), 3.58f);
            };
        }
    }
}
