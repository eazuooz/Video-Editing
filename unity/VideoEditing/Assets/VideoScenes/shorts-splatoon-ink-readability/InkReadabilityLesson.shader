Shader "Yamyam/Shorts/InkReadabilityLesson"
{
    Properties
    {
        _BaseColor ("Solid object colour", Color) = (0.5,0.5,0.5,1)
        _TeamA ("Illustrative ink A", Color) = (0.16,0.65,0.65,1)
        _TeamB ("Illustrative ink B", Color) = (0.8,0.32,0.15,1)
        [Toggle] _InkPattern ("Two-colour teaching surface", Float) = 1
        _ShadingStrength ("Our shade contribution", Range(0,1)) = 1
        _SpecularStrength ("Our specular contribution", Range(0,4)) = 0.3
        _Roughness ("Our roughness (fixed during comparisons)", Range(0.08,1)) = 0.23
        _Ambient ("Our ambient term (fixed)", Range(0,1)) = 0.025
        _LightDirection ("Surface toward fixed light", Vector) = (0.65,0.32,-0.69,0)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" "RenderPipeline"="UniversalPipeline" }
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        CBUFFER_START(UnityPerMaterial)
        float4 _BaseColor, _TeamA, _TeamB, _LightDirection;
        float _InkPattern, _ShadingStrength, _SpecularStrength, _Roughness, _Ambient;
        CBUFFER_END
        ENDHLSL
        Pass
        {
            Name "ForwardLesson"
            Tags { "LightMode"="UniversalForwardOnly" }
            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            struct Attributes
            {
                float4 position : POSITION;
                float3 normal : NORMAL;
                float2 uv : TEXCOORD0;
            };
            struct Varyings
            {
                float4 position : SV_POSITION;
                float3 worldPosition : TEXCOORD0;
                float3 worldNormal : TEXCOORD1;
                float2 uv : TEXCOORD2;
            };
            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.position = TransformObjectToHClip(input.position.xyz);
                output.worldPosition = TransformObjectToWorld(input.position.xyz);
                output.worldNormal = TransformObjectToWorldNormal(input.normal);
                output.uv = input.uv;
                return output;
            }

            // An authored direct-light GGX teaching model, not Nintendo's BRDF.
            // Shade/specular multipliers intentionally permit artistic A/B
            // comparisons; this is not a complete light-transport simulation.
            float DistributionGGX(float nDotH, float alpha)
            {
                float a2 = alpha * alpha;
                float denominator = nDotH * nDotH * (a2 - 1.0) + 1.0;
                return a2 / max(0.0001, PI * denominator * denominator);
            }
            float GeometrySchlick(float nDotDirection, float roughness)
            {
                float k = (roughness + 1.0) * (roughness + 1.0) / 8.0;
                return nDotDirection / max(0.0001, nDotDirection * (1.0 - k) + k);
            }
            float4 Frag(Varyings input) : SV_Target
            {
                float boundary = 0.5 + 0.10 * sin(input.uv.y * 17.0)
                    + 0.035 * sin(input.uv.y * 43.0);
                float team = smoothstep(boundary - 0.003, boundary + 0.003, input.uv.x);
                float3 albedo = lerp(_BaseColor.rgb, lerp(_TeamA.rgb, _TeamB.rgb, team), _InkPattern);
                float3 normal = normalize(input.worldNormal);
                float3 light = normalize(_LightDirection.xyz);
                float3 view = GetWorldSpaceNormalizeViewDir(input.worldPosition);
                float3 halfway = normalize(light + view);
                float nl = saturate(dot(normal, light));
                float nv = max(0.001, saturate(dot(normal, view)));
                float nh = saturate(dot(normal, halfway));
                float vh = saturate(dot(view, halfway));
                float roughness = max(0.08, _Roughness);
                float alpha = roughness * roughness;
                float fresnel = 0.04 + 0.96 * pow(1.0 - vh, 5.0);
                float distribution = DistributionGGX(nh, alpha);
                float geometry = GeometrySchlick(nl, roughness) * GeometrySchlick(nv, roughness);
                float specular = distribution * geometry * fresnel / max(0.001, 4.0 * nl * nv);
                float3 shaded = albedo * (_Ambient + (1.0 - _Ambient) * nl);
                float3 diffuse = lerp(albedo, shaded, _ShadingStrength);
                float3 reflected = _SpecularStrength * specular * nl;
                return float4(diffuse + reflected, 1.0);
            }
            ENDHLSL
        }
        // The current PC URP asset requests depth. This supplies the same opaque
        // geometry to a depth prepass without changing the teaching illumination.
        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            ZWrite On
            ColorMask R
            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex DepthVert
            #pragma fragment DepthFrag
            float4 DepthVert(float3 positionOS : POSITION) : SV_POSITION
            {
                return TransformObjectToHClip(positionOS);
            }
            half DepthFrag(float4 positionCS : SV_POSITION) : SV_Target
            {
                return positionCS.z;
            }
            ENDHLSL
        }
        // PC's deferred renderer has SSAO enabled with a depth-normal source.
        // Use URP's opaque normal encoding; no copied game buffers or extra light.
        Pass
        {
            Name "DepthNormalsOnly"
            Tags { "LightMode"="DepthNormalsOnly" }
            ZWrite On
            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex DepthNormalsVertex
            #pragma fragment DepthNormalsFragment
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            #include "Packages/com.unity.render-pipelines.universal/Shaders/UnlitDepthNormalsPass.hlsl"
            ENDHLSL
        }
    }
    Fallback Off
}
