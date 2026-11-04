Shader "Yamyam/SkinNormalTeachingSurface" {
 Properties {
  _BaseMap("Base map",2D)="white"{} _BaseColor("Base color",Color)=(.52,.6,.64,1)
  _NormalRGB("Linear XYZ normal data",2D)="bump"{}
  _UseNormal("Apply normal data",Range(0,1))=1
  _WrongObjectSpace("Counterexample: ignore TBN",Float)=0
  _GreenSign("Y convention",Float)=1
  _ShowData("Show encoded data",Float)=0
  _WeightTint("Use vertex weight colors",Float)=0
  _LightDirectionWS("Direction TO light",Vector)=(.6,.6,-1,0)
 }
 SubShader {Tags{"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque"} Cull Back
  Pass {Name "TeachingForward" Tags{"LightMode"="UniversalForward"}
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
   TEXTURE2D(_NormalRGB);SAMPLER(sampler_NormalRGB);
   CBUFFER_START(UnityPerMaterial)
   float4 _BaseMap_ST,_BaseColor,_LightDirectionWS;
   float _UseNormal,_WrongObjectSpace,_GreenSign,_ShowData,_WeightTint;
   CBUFFER_END
   struct A{float4 positionOS:POSITION;float3 normalOS:NORMAL;float4 tangentOS:TANGENT;float2 uv:TEXCOORD0;float4 color:COLOR;};
   struct V{float4 positionCS:SV_POSITION;float3 positionWS:TEXCOORD0;float3 n:TEXCOORD1;float4 t:TEXCOORD2;float2 uv:TEXCOORD3;float4 color:COLOR;};
   V vert(A i){V o;VertexPositionInputs p=GetVertexPositionInputs(i.positionOS.xyz);o.positionCS=p.positionCS;o.positionWS=p.positionWS;o.n=TransformObjectToWorldNormal(i.normalOS);o.t=float4(TransformObjectToWorldDir(i.tangentOS.xyz),i.tangentOS.w*GetOddNegativeScale());o.uv=i.uv;o.color=i.color;return o;}
   float4 frag(V i):SV_Target {
    float3 n=normalize(i.n);float3 rawT=i.t.xyz-n*dot(n,i.t.xyz);
    if(dot(rawT,rawT)<1e-10)return float4(1,.1,.7,1); // Invalid frame is visible, never silently repaired.
    float3 t=normalize(rawT);float3 b=cross(n,t)*(i.t.w<0?-1:1);
    float3 packed=SAMPLE_TEXTURE2D(_NormalRGB,sampler_NormalRGB,i.uv).rgb;
    if(_ShowData>.5)return float4(packed,1);
    float3 local=packed*2-1;local.y*=_GreenSign;
    if(dot(local,local)<1e-10)return float4(1,.1,.7,1);
    local=normalize(local);local=normalize(lerp(float3(0,0,1),local,_UseNormal));
    float3 shadedNormal=_WrongObjectSpace>.5?TransformObjectToWorldDir(local):normalize(local.x*t+local.y*b+local.z*n);
    float3 l=normalize(_LightDirectionWS.xyz);
    float3 v=unity_OrthoParams.w>.5?normalize(UNITY_MATRIX_V[2].xyz):GetWorldSpaceNormalizeViewDir(i.positionWS);
    // Directional-response illustration, not Unity Lit/PBR or measured game radiance.
    float diffuse=saturate(dot(shadedNormal,l));float3 hv=l+v;
    float spec=diffuse>0&&dot(hv,hv)>1e-8?pow(saturate(dot(shadedNormal,normalize(hv))),48):0;
    float3 base=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv*_BaseMap_ST.xy+_BaseMap_ST.zw).rgb*_BaseColor.rgb;
    base=lerp(base,i.color.rgb,_WeightTint);
    return float4(base*(.12+.80*diffuse)+.32*spec,1);
   }
   ENDHLSL
  }
 }
}
