Shader "Yamyam/EldenLibraryLessonFog"
{
    Properties
    {
        _Progress ("Progress", Range(0,1)) = 0
        _Layered ("Use distant approximation", Float) = 0
    }
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Blend SrcAlpha OneMinusSrcAlpha
        Cull Off
        ZWrite Off
        Pass
        {
            Tags { "LightMode"="SRPDefaultUnlit" }
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            float _Progress, _Layered;
            struct Interpolators { float4 position : SV_POSITION; float2 uv : TEXCOORD0; };
            Interpolators vert(appdata_base input)
            {
                Interpolators output;
                output.position = UnityObjectToClipPos(input.vertex);
                output.uv = input.texcoord.xy;
                return output;
            }
            fixed4 frag(Interpolators input) : SV_Target
            {
                float2 uv = input.uv;
                float nearDepth = 0;
                [unroll] for (int sample = 0; sample < 12; sample++)
                {
                    float z = (sample + .5) / 12.0;
                    float y = uv.y - .22 - .12 * sin(uv.x * 10 + z * 7 + _Progress * 2);
                    float density = exp(-17 * y * y) * (.6 + .4 * sin(6 * uv.x + z * 9));
                    nearDepth += max(0, density) * (z <= _Progress);
                }
                float nearAlpha = 1 - exp(-nearDepth * .17);
                float farAlpha = saturate((uv.x - .47) * 1.2) * .72 * (1 - uv.y) * _Progress;
                float alpha = lerp(nearAlpha, lerp(nearAlpha, farAlpha, smoothstep(.49,.80,uv.x)), _Layered);
                float edge = smoothstep(0,.09,uv.x) * smoothstep(0,.09,1-uv.x) * smoothstep(0,.13,uv.y) * smoothstep(0,.25,1-uv.y);
                return fixed4(lerp(float3(.21,.68,.71),float3(.43,.48,.85),uv.x * _Layered),alpha * edge * .75);
            }
            ENDCG
        }
    }
}
