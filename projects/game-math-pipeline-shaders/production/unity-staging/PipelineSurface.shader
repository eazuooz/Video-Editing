Shader "Yamyam/PipelineTeachingSurface" {
 Properties {
  _BaseMap("Authored colour",2D)="white"{} _NormalRGB("Linear XYZ normal",2D)="bump"{}
  _BaseColor("Diffuse coefficient",Color)=(0.55,0.6,0.65,1) _SpecColor("Specular coefficient",Color)=(0.3,0.3,0.3,1)
  _Exponent("Blinn exponent",Float)=32 _Ambient("Constant ambient",Float)=0.1
  _Mode("0 unlit 1 pixel 2 Gouraud 3 normal",Float)=1
  _LightPosition("Point light",Vector)=(0,3,-4,1) _LightRange("Linear range",Float)=8
  _ThreeLights("3 directional lights",Float)=0 _UseSkin("Own two-bone skin",Float)=0
 }
 SubShader {Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque"} Pass {
 HLSLPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
 TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);TEXTURE2D(_NormalRGB);SAMPLER(sampler_NormalRGB);
 CBUFFER_START(UnityPerMaterial)
 float4 _BaseMap_ST,_BaseColor,_SpecColor,_LightPosition;float _Exponent,_Ambient,_Mode,_LightRange,_ThreeLights,_UseSkin;
 float4x4 _Bone0,_Bone1;
 CBUFFER_END
 struct Input {float4 position:POSITION;float3 normal:NORMAL;float4 tangent:TANGENT;float2 uv:TEXCOORD0;float2 weights:TEXCOORD1;};
 struct Varying {float4 position:SV_Position;float2 uv:TEXCOORD0;float3 ws:TEXCOORD1;float3 n:TEXCOORD2;float4 t:TEXCOORD3;float3 diffuse:TEXCOORD4;float3 specular:TEXCOORD5;};
 float3 SafeUnit(float3 x){return x*rsqrt(max(dot(x,x),1e-12));}
 void OneLight(float3 n,float3 v,float3 l,float3 color,inout float3 d,inout float3 s){l=SafeUnit(l);float nl=max(dot(n,l),0);d+=color*nl;float3 h=SafeUnit(l+v);s+=nl>0?color*pow(max(dot(n,h),0),max(_Exponent,0)):0;}
 void Lighting(float3 ws,float3 n,out float3 d,out float3 s){
  n=SafeUnit(n);float3 v=unity_OrthoParams.w>0?SafeUnit(UNITY_MATRIX_V[2].xyz):SafeUnit(_WorldSpaceCameraPos-ws);d=_Ambient.xxx;s=0;
  if(_ThreeLights>.5){OneLight(n,v,float3(-.6,.7,-1),float3(.55,.6,.65),d,s);OneLight(n,v,float3(1,.2,-.5),float3(.35,.24,.15),d,s);OneLight(n,v,float3(0,-.5,1),float3(.15,.2,.32),d,s);}
  else {float3 l=_LightPosition.xyz-ws;float attenuation=max(1-length(l)/max(_LightRange,1e-6),0);OneLight(n,v,l,attenuation.xxx,d,s);}
 }
 Varying vert(Input i){
  Varying o;float4 p=i.position;float3 n=i.normal,t=i.tangent.xyz;
  // The shader uses Unity column matrices; source HLSL row matrices are displayed transposed.
  if(_UseSkin>.5){float sum=max(i.weights.x+i.weights.y,1e-6);float2 w=i.weights/sum;float4x4 b=_Bone0*w.x+_Bone1*w.y;p=mul(b,p);n=mul((float3x3)b,n);t=mul((float3x3)b,t);}
  o.ws=TransformObjectToWorld(p.xyz);o.position=TransformWorldToHClip(o.ws);o.n=TransformObjectToWorldNormal(n);o.t=float4(TransformObjectToWorldDir(t),i.tangent.w*GetOddNegativeScale());o.uv=TRANSFORM_TEX(i.uv,_BaseMap);Lighting(o.ws,o.n,o.diffuse,o.specular);return o;
 }
 float4 frag(Varying i):SV_Target{
  float4 texel=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv);float3 base=texel.rgb*_BaseColor.rgb;if(_Mode<.5)return float4(base,texel.a*_BaseColor.a);
  float3 d=i.diffuse,s=i.specular;
  if(_Mode<1.5||_Mode>2.5){float3 n=SafeUnit(i.n);
   if(_Mode>2.5){float3 t=SafeUnit(i.t.xyz-n*dot(n,i.t.xyz)),b=SafeUnit(cross(n,t))*sign(i.t.w);float3 nt=SafeUnit(SAMPLE_TEXTURE2D(_NormalRGB,sampler_NormalRGB,i.uv).rgb*2-1);n=SafeUnit(t*nt.x+b*nt.y+n*nt.z);}
   Lighting(i.ws,n,d,s);
  }
  return float4(base*d+_SpecColor.rgb*s,texel.a*_BaseColor.a);
 }
 ENDHLSL
 }}
}
