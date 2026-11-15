Shader "Yamyam/OriginalTechTwelve/SandLesson" {
    Properties {
        _GrainTex("Authored grain-direction field",2D)="gray"{}
        _Grain("Grain layer",Float)=0
        _Glitter("Glitter layer",Float)=0
        _ViewGlitter("View-based heuristic",Float)=0
        _GrazingMask("Grazing mask",Float)=0
        _Broad("Broad highlight",Float)=0
    }
    SubShader {Tags{"RenderType"="Opaque"} Pass {
        CGPROGRAM
        #pragma vertex vert
        #pragma fragment frag
        #pragma target 3.0
        #include "UnityCG.cginc"
        sampler2D _GrainTex;float _Grain,_Glitter,_ViewGlitter,_GrazingMask,_Broad;
        struct Input{float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0;};
        struct Varying{float4 position:SV_POSITION;float3 world:TEXCOORD0;float3 normal:TEXCOORD1;float2 uv:TEXCOORD2;};
        Varying vert(Input i){Varying o;o.position=UnityObjectToClipPos(i.vertex);o.world=mul(unity_ObjectToWorld,i.vertex).xyz;o.normal=UnityObjectToWorldNormal(i.normal);o.uv=i.uv;return o;}
        float4 frag(Varying i):SV_Target {
            float3 geometric=normalize(i.normal),V=normalize(_WorldSpaceCameraPos-i.world),L=normalize(float3(2,4,-3)),H=normalize(V+L);
            float3 grain=normalize(tex2D(_GrainTex,i.uv*12).xyz*2-1);
            float3 N=normalize(lerp(geometric,geometric*.35+grain,_Grain));
            float diffuse=.35+.65*saturate(dot(N,L));
            float directional=lerp(saturate(dot(N,H)),saturate(dot(N,V)),_ViewGlitter);
            float glint=pow(directional,80)*_Glitter;
            // An authored illustration of reducing a glitter layer at grazing
            // views, not the original Journey shader or its exact parameters.
            float mask=lerp(1,smoothstep(.12,.35,saturate(dot(geometric,V))),_GrazingMask);
            float broad=pow(saturate(dot(geometric,H)),12)*.32*_Broad;
            float3 sand=float3(.64,.39,.22)*diffuse+glint*mask*float3(1,.9,.65)*1.6+broad*float3(1,.78,.5);
            return float4(sand,1);
        }
        ENDCG
    }}
}
