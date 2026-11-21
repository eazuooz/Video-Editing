Shader "Yamyam/EldenLessonSurface"
{
    Properties
    {
        _LightSide ("Light X", Float) = 0
        _Mode ("Plain, perturbed normal, or mask", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            float _LightSide, _Mode;
            struct Interpolators { float4 pos : SV_POSITION; float3 local : TEXCOORD0; float3 normal : TEXCOORD1; };
            Interpolators vert(appdata_base input)
            {
                Interpolators output;
                output.pos = UnityObjectToClipPos(input.vertex);
                output.local = input.vertex.xyz;
                output.normal = UnityObjectToWorldNormal(input.normal);
                return output;
            }
            fixed4 frag(Interpolators input) : SV_Target
            {
                float side = input.local.x + .42 * input.local.y + .07 * sin(input.local.y * 25);
                float lengthMask = 1 - smoothstep(.22,.34,abs(input.local.y));
                float mask = lengthMask * (1 - smoothstep(.025,.105,abs(side))) * (input.local.z < 0);
                float3 normal = normalize(input.normal);
                if (_Mode > .5 && _Mode < 1.5)
                    normal = normalize(normal + float3(-5.5 * side * mask, -1.1 * side * mask, 0));
                float lit = .21 + .69 * saturate(dot(normal, normalize(float3(_LightSide * .4, .95, -1.2))));
                float3 stone = lerp(float3(.84,.62,.43),float3(.9,.28,.14),mask * step(1.5,_Mode));
                return fixed4(stone * lit, 1);
            }
            ENDCG
        }
    }
}
