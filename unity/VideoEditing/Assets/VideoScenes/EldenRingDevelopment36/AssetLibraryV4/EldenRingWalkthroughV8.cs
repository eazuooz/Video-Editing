using System;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        Action<float> BuildWalkthroughV8()
        {
            switch (episode)
            {
                case 2: return TowerWalkV8();
                case 3: return FaceLayersV8();
                case 5: return VistaV8();
                case 6: return PrototypeWalkV8();
                case 7: return TerrainV8();
                case 9: return PassageV8();
                case 10: return CastV8();
                default: return BuildRenderingAndWorld();
            }
        }

        void Floor(string label, float x, float z, float width, float length, float top, Color color,
            Transform parent = null)
        {
            Block(label, V(x, top - .16f, z), V(width, .32f, length), color, parent);
        }

        void GroundGate(string label, Vector3 at, float width, float height, Color stone)
        {
            float edge = width / 2;
            Block(label + " left pier", at + V(-edge, height / 2, 0), V(.40f, height, .72f), stone);
            Block(label + " right pier", at + V(edge, height / 2, 0), V(.40f, height, .72f), stone);
            Block(label + " lintel", at + V(0, height, 0), V(width + .4f, .32f, .72f), stone);
        }

        Action<float> TowerWalkV8()
        {
            const float lane = -.95f;
            var turf = new Color32(52, 79, 64, 255);
            var clay = new Color32(159, 120, 84, 255);
            var stone = new Color32(91, 112, 118, 255);
            Floor("Solid meadow", 0, 1.4f, 9, 12, 0, turf);
            Floor("Walk between start and tower", lane, 1.05f, 1.18f, 9.02f, .035f, clay);
            Vector3 start = V(lane, .035f, -3.22f), end = V(lane, .035f, 5.12f);
            var player = Pawn("Traveler crossing the fog", start, Gold);
            var actor = walkthroughActors[walkthroughActors.Count - 1];
            actor.FixedFacing = true;
            var near = Ring("Start at camera side", start + V(0, .022f, 0), .59f, Aqua);
            var far = Ring("Finish at tower gate", end + V(0, .022f, 0), .62f, Gold);
            GroundGate("End gate", V(lane, .035f, 5.56f), 1.70f, 2.35f, clay);
            Attach("tower", Group("Far tower behind gate", V(-1.75f, 0, 6.35f)), V(2.70f, 4.10f, 2.30f), true);
            Attach("tower", Group("Middle distance tower", V(2.02f, 0, 1.72f)), V(2.05f, 3.0f, 1.8f), true);
            Attach("tower", Group("Near tower", V(2.60f, 0, -2.38f)), V(1.90f, 2.45f, 1.8f), true);
            var medium = Shape(PrimitiveType.Quad, "Camera ray integrated through fog", V(1.9f, 2.1f, .82f),
                V(6.4f, 3.6f, 1), Paper);
            var fog = new Material(Shader.Find("Yamyam/EldenLibraryLessonFog"));
            owned.Add(fog);
            medium.GetComponent<Renderer>().sharedMaterial = fog;
            var points = new Transform[12];
            for (int i = 0; i < points.Length; i++)
            {
                float distance = i < 7 ? .39f * i : 2.75f + (i - 7) * 1.15f;
                points[i] = Orb("Sample locations along viewing direction", V(.13f, .16f, start.z + distance),
                    .15f, i < 7 ? Aqua : Gold);
                Tint(points[i], i < 7 ? Aqua : Gold);
            }
            var line = Bar("Camera viewing direction", V(.13f, .09f, -3.22f), V(.13f, .09f, 5.12f), .06f, stone);
            return t =>
            {
                player.localPosition = Vector3.Lerp(start, end, Range(t, .07f, .91f));
                float center = Mathf.Lerp(.5f, 1.47f, Range(t, .20f, .85f));
                FrameCamera(V(8.65f, 7.75f, -12.8f), V(0, .96f, center), 4.57f);
                medium.rotation = cameraFacing(medium.position);
                fog.SetFloat("_Progress", .56f + .42f * Range(t, .07f, .9f));
                fog.SetFloat("_Layered", Second ? 1 : 0);
                line.gameObject.SetActive(Second);
                for (int i = 0; i < points.Length; i++)
                    points[i].gameObject.SetActive(Second && t > .1f + i * .043f);
                near.localScale = Vector3.one * (t < .17f ? 1.08f : 1);
                far.localScale = Vector3.one * (t > .85f ? 1.08f : 1);
            };
        }

        Action<float> PrototypeWalkV8()
        {
            var grass = new Color32(74, 98, 68, 255);
            var tan = new Color32(143, 113, 83, 255);
            var stone = new Color32(106, 120, 123, 255);
            Floor("Shared full-size graybox and art pass ground", 0, 0, 10.4f, 6.7f, 0, grass);
            Floor("Walkable path retained in both versions", 0, -.35f, 10.3f, 1.42f, .045f, tan);
            var rough = Group("Simplified prior assets", Vector3.zero);
            for (int i = 0; i < 3; i++)
            {
                float x = -3.65f + i * 1.1f;
                Block("Wall made from reusable stone sections", V(x, .59f, 1.07f), V(1.07f, 1.18f, .55f), stone, rough);
                Block("Reusable stone coping", V(x, 1.15f, 1.07f), V(1.10f, .17f, .67f), Slate, rough);
            }
            Shape(PrimitiveType.Capsule, "Volumetric basic boulder", V(1.22f, .52f, 1.52f),
                V(1.65f, .57f, 1.06f), Slate, rough).localRotation = Quaternion.Euler(0, -24, 17);
            AddPrototypeDetail(rough, "cliff", V(3.22f, 0, 1.62f), V(1.45f, 1.7f, .95f));
            var detailed = Group("Production detail at the same dimensions", Vector3.zero);
            for (int i = 0; i < 3; i++)
            {
                var wall = Block("Same wall footprint", V(-3.65f + i * 1.1f, .55f, 1.07f),
                    V(1.07f, 1.10f, .55f), stone, detailed);
                for (int row = 0; row < 3; row++)
                    for (int col = 0; col < 2; col++)
                        Block("Stone joint and face", V((col - .5f) * .49f + (row % 2) * .06f,
                            (row - 1) * .29f, -.53f), V(.44f, .25f, .14f),
                            (row + col) % 2 == 0 ? new Color32(131, 128, 113, 255) : stone, wall);
                Block("Weathered cap stone", V(-3.65f + i * 1.1f, 1.15f, 1.07f),
                    V(1.10f, .17f, .67f), new Color32(151, 142, 114, 255), detailed);
            }
            AddPrototypeDetail(detailed, "rock", V(1.22f, 0, 1.52f), V(1.65f, 1.1f, 1.06f));
            AddPrototypeDetail(detailed, "cliff", V(3.22f, 0, 1.62f), V(1.45f, 1.7f, .95f));
            AddPrototypeDetail(detailed, "grass", V(.95f, 0, .72f), V(.95f, .37f, .65f));
            var traveler = Pawn("Verify the route before making final art", V(-4.45f, .045f, -.35f), Gold);
            Action<float> play = t =>
            {
                float travel = .52f * Range(t, .04f, .43f) + .48f * Range(t, .57f, .93f);
                traveler.localPosition = V(Mathf.Lerp(-4.45f, 4.35f, travel), .045f, -.35f);
                rough.gameObject.SetActive(t < .50f);
                detailed.gameObject.SetActive(t >= .50f);
                FrameCamera(V(2.9f, 5.05f, -10.2f), V(0, .59f, .33f), 3.55f);
            };
            return play;
        }

        void AddPrototypeDetail(Transform set, string role, Vector3 position, Vector3 fit)
        {
            var stand = Group("Shared " + role, position);
            stand.SetParent(set, false);
            Attach(role, stand, fit, true);
        }

        const float PassageTop = 1.44f;
        const float RampStart = -1.38f;
        const float RampEnd = 2.46f;

        static float PassageY(float z) => Mathf.Lerp(0, PassageTop, Mathf.InverseLerp(RampStart, RampEnd, z));

        void PassageRamp(Color stone)
        {
            var a = V(0, 0, RampStart);
            var b = V(0, PassageTop, RampEnd);
            var level = Group("Continuous walkable stone incline", (a + b) * .5f);
            level.localRotation = Quaternion.FromToRotation(Vector3.forward, (b - a).normalized);
            Block("Incline top matches the character support calculation", V(0, -.15f, 0),
                V(2.72f, .30f, Vector3.Distance(a, b)), stone, level);
            for (int i = 0; i < 12; i++)
                Block("Paving seam across incline", V(0, .004f, (i - 5.5f) * .33f), V(2.7f, .018f, .024f), Slate, level);
        }

        Action<float> PassageV8()
        {
            var limestone = new Color32(147, 138, 117, 255);
            var lower = new Color32(111, 121, 114, 255);
            var wall = new Color32(96, 110, 109, 255);
            var grass = new Color32(73, 98, 72, 255);
            view.backgroundColor = new Color32(126, 155, 161, 255);
            Floor("Landscape below the structure", 2.7f, 7.3f, 17.5f, 16.3f, -.48f, grass);
            Floor("Lower enclosed approach", 0, -3.07f, causalV11 ? 9f : 4.16f, 3.38f, 0, lower);
            PassageRamp(limestone);
            Floor("Upper terrace with distant view", 0, 4.78f, 7.8f, 4.64f, PassageTop, limestone);
            Floor("Connected upper side path", 3.74f, 5.83f, 2.3f, 2.52f, PassageTop, grass);
            for (int side = -1; side <= 1; side += 2)
            {
                Block("Approach courtyard retaining wall", V(side * (causalV11 ? 4.45f : 2.04f), .84f, -3.08f), V(.32f, 1.68f, 3.34f), wall);
                for (int i = 0; i < 6; i++)
                {
                    float z = Mathf.Lerp(-1.2f, 2.35f, i / 5f);
                    Block("Ascending side wall follows paving", V(side * 1.48f, PassageY(z) + .63f, z),
                        V(.26f, 1.26f, .70f), wall);
                }
                Block("Open lookout parapet", V(side * 2.67f, PassageTop + .32f, 6.8f),
                    V(2.44f, .64f, .25f), wall);
            }
            for (int side = -1; side <= 1; side += 2)
                Block("Stone arch pier", V(side * 1.10f, PassageTop + .76f, 2.47f), V(.42f, 1.52f, .64f), wall);
            for (int i = 0; i <= 10; i++)
            {
                float angle = i * Mathf.PI / 10;
                var block = Block("Individual arch stone", V(Mathf.Cos(angle) * 1.12f,
                    PassageTop + 1.51f + Mathf.Sin(angle) * 1.12f, 2.47f), V(.40f, .35f, .66f),
                    i % 2 == 0 ? wall : limestone);
                block.localRotation = Quaternion.Euler(0, 0, angle * Mathf.Rad2Deg);
            }
            Attach("house", Group("Distant building silhouette revealed from the terrace", V(4.8f, -.48f, 11.2f)),
                V(4.55f, 4.52f, 3.35f), true);
            Attach("cliff", Group("Below the raised terrace", V(-3.9f, -1f, 7.9f)), V(5.4f, 2.1f, 2.32f), true);
            Attach("cliff", Group("Far rock silhouette", V(-6.7f, -.48f, 12.6f)), V(8.4f, 3.3f, 3.8f), true);
            for (int i = 0; i < 7; i++)
            {
                float x = i < 4 ? -3.1f - .54f * i : 4.8f + .43f * (i - 4);
                Tree(V(x, -.48f, 7.3f + (i * 1.47f) % 5), .72f + .33f * (i % 3));
            }
            var player = Pawn("Grounded walkthrough actor", V(0, 0, -4.22f), Gold);
            var actor = walkthroughActors[walkthroughActors.Count - 1];
            actor.GroundHeight = point => PassageY(point.z);
            return t =>
            {
                float z = Mathf.Lerp(-4.22f, 6.26f, Range(t, .03f, .94f));
                float side = (Second ? 2.5f : .52f) * Range(t, .73f, .97f);
                var p = V(side, PassageY(z), z);
                player.localPosition = p;
                var rear = p + V(Second ? .76f : .58f, 1.79f, -3.16f);
                var look = V(p.x * .89f + .08f, p.y + .98f, z + 2.47f);
                if(causalV11) look.y=Mathf.Lerp(look.y,-.15f,Range(t,.83f,.97f));
                view.fieldOfView = Mathf.Lerp(55, 58, Range(t, .62f, .9f));
                view.orthographic = false;
                view.transform.SetPositionAndRotation(rear, Quaternion.LookRotation(look - rear));
            };
        }

        Action<float> CastV8()
        {
            Floor("Training ground", 0, .5f, 8.8f, 5.7f, 0, new Color32(76, 94, 79, 255));
            var caster = Pawn("Caster with skinned arm, elbow, hip and knee motion", V(-1.43f, 0, .46f), Aqua);
            var actor = walkthroughActors[walkthroughActors.Count - 1];
            actor.FixedFacing = true;
            caster.localRotation = Quaternion.Euler(0, 75, 0);
            var wrist = actor.Arms[1].End;
            var staff = Block("Live right-hand staff", Vector3.zero, Vector3.one, new Color32(143, 109, 67, 255));
            var tip = Orb("Staff tip", Vector3.zero, .18f, Aqua);
            var projectile = Orb("Effect after annotated release", Vector3.zero, .24f, Aqua);
            var target = Ring("Training target", V(2.89f, .032f, .76f), .49f, Gold);
            Attach("rock", Group("Training target boulder", V(2.89f, 0, .76f)), V(.64f, .71f, .55f), true);
            Bar("Animation timeline", V(-3.25f, .09f, -1.54f), V(3.25f, .09f, -1.54f), .085f, Slate);
            for (int i = 0; i <= 10; i++)
                Block("Animation frame", V(-3.25f + i * .65f, .11f, -1.54f), V(.04f, .17f, .22f), Paper);
            float CastMarker(float phase) => Mathf.Lerp(-3.25f, 3.25f, phase);
            const float motionRelease = .51f;
            float keyAt = Second ? motionRelease : .37f;
            var key = Block("Effect trigger key", V(CastMarker(keyAt), .23f, -1.54f), V(.16f, .36f, .19f),
                Second ? Aqua : Red);
            var playhead = Orb("Playhead", Vector3.zero, .20f, Gold);
            FrameCamera(V(1.1f, 3.48f, -7.54f), V(0, .73f, .30f), 2.64f);
            actor.AfterPose = () =>
            {
                float t = actor.PosePhase;
                var origin = stage.InverseTransformPoint(wrist.position);
                var wandDirection = V(.10f + .67f * actor.Cast, .25f + .91f * actor.Cast, .18f).normalized;
                Segment(staff, origin - .23f * wandDirection, origin + .64f * wandDirection, .062f);
                tip.localPosition = origin + .64f * wandDirection;
                float travel = Range(t, keyAt, keyAt + .24f);
                projectile.localPosition = Vector3.Lerp(tip.localPosition, V(2.89f, .84f, .76f), travel);
                projectile.gameObject.SetActive(t >= keyAt && t <= keyAt + .24f);
                Tint(tip, t > .30f && t < .69f ? Aqua : Paper);
            };
            return t =>
            {
                if(causalV11)
                {
                    if(Second)keyAt=Mathf.Lerp(.37f,motionRelease,Range(t,0,.22f));
                    else
                    {
                        bool aligned=t>=.52f;
                        keyAt=aligned?motionRelease:.37f;
                        t=aligned?Range(t,.52f,1):Range(t,0,.52f);
                    }
                    key.localPosition=V(CastMarker(keyAt),.23f,-1.54f);
                }
                actor.PosePhase = t;
                actor.Cast = Range(t, .08f, motionRelease) * (1 - Range(t, .69f, .95f));
                playhead.localPosition = V(CastMarker(t), .39f, -1.54f);
                key.localScale = V(.16f, t >= keyAt && t < keyAt + .12f ? .49f : .36f, .19f);
                target.localScale = Vector3.one * (1 + .19f * Range(t, keyAt + .20f, keyAt + .32f));
            };
        }
    }
}
