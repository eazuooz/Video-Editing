Shader "Yamyam/SurfaceInkLesson"
{
    Properties
    {
        _PaintTex("Actual paint image",2D)="black"{}
        _BaseColor("Wall color",Color)=(.18,.21,.24,1)
        _FlatView("Texture sheet",Float)=0
        _ShowSeam("Coplanar patch boundary",Float)=0
    }
    SubShader
    {
        Tags {"RenderType"="Opaque" "RenderPipeline"="UniversalPipeline"}
        Cull Off
        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            TEXTURE2D(_PaintTex); SAMPLER(sampler_PaintTex);
            CBUFFER_START(UnityPerMaterial)
            float4 _BaseColor; float _FlatView; float _ShowSeam;
            CBUFFER_END
            struct A {float4 positionOS:POSITION;float3 normalOS:NORMAL;float2 uv:TEXCOORD0;};
            struct V {float4 positionCS:SV_POSITION;float3 normalWS:TEXCOORD0;float2 uv:TEXCOORD1;};
            V vert(A i){V o;o.positionCS=TransformObjectToHClip(i.positionOS.xyz);o.normalWS=TransformObjectToWorldNormal(i.normalOS);o.uv=i.uv;return o;}
            half4 frag(V i):SV_Target
            {
                half4 paint=SAMPLE_TEXTURE2D(_PaintTex,sampler_PaintTex,i.uv);
                float2 cells=frac(i.uv*8);
                float gridLine=1-step(.018,min(min(cells.x,1-cells.x),min(cells.y,1-cells.y)));
                half3 base=lerp(_BaseColor.rgb,_BaseColor.rgb+.12,gridLine);
                half light=.45+.55*saturate(dot(normalize(i.normalWS),normalize(float3(-.4,.8,-.6))));
                if(_FlatView>.5){base=lerp(half3(.09,.10,.11),half3(.17,.18,.19),fmod(floor(i.uv.x*8)+floor(i.uv.y*8),2));light=1;}
                half3 result=lerp(base,paint.rgb,paint.a)*light;
                if(_ShowSeam>.5 && abs(i.uv.x-.5)<.003) result=half3(1,.76,.12);
                return half4(result,1);
            }
            ENDHLSL
        }
    }
}
