Shader "Yamyam/NormalMapLesson" {
 Properties {
  _MainTex("Colour / alpha",2D)="white"{} _BumpMap("Tangent-space normal data",2D)="bump"{}
  _Color("Colour multiplier",Color)=(1,1,1,1) _NormalStrength("Normal mapping",Range(0,1))=1
  [Toggle] _RawNormalRGB("Our uncompressed full RGB normal data",Float)=0
  _LightDir("Surface to directional light",Vector)=(.7,.3,-.6,0) _Ambient("Ambient",Range(0,1))=.13
  _OutputMode("0 lit;1 normal RGB view;2 float verification;3 normal bake;4 colour bake",Float)=0
  _BakeRight("Bake camera right",Vector)=(1,0,0,0) _BakeUp("Bake camera up",Vector)=(0,1,0,0) _BakeOut("Bake camera outward",Vector)=(0,0,-1,0)
 }
 SubShader { Tags{"RenderType"="TransparentCutout" "Queue"="AlphaTest"} Cull Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 sampler2D _MainTex,_BumpMap;float4 _MainTex_ST,_Color,_LightDir,_BakeRight,_BakeUp,_BakeOut;float _NormalStrength,_Ambient,_OutputMode,_RawNormalRGB;
 struct appdata {float4 vertex:POSITION;float3 normal:NORMAL;float4 tangent:TANGENT;float2 uv:TEXCOORD0;};
 struct v2f {float4 position:SV_POSITION;float2 uv:TEXCOORD0;float3 n:TEXCOORD1;float3 t:TEXCOORD2;float3 b:TEXCOORD3;};
 v2f vert(appdata v){v2f o;o.position=UnityObjectToClipPos(v.vertex);o.uv=TRANSFORM_TEX(v.uv,_MainTex);o.n=UnityObjectToWorldNormal(v.normal);o.t=UnityObjectToWorldDir(v.tangent.xyz);o.b=cross(o.n,o.t)*v.tangent.w*unity_WorldTransformParams.w;return o;}
 float4 frag(v2f i):SV_Target {
  float4 colour=tex2D(_MainTex,i.uv)*_Color;clip(colour.a-.5);
  // Unity-imported tangent maps use platform unpacking. Our uncompressed sprite
  // bake preserves all three signed RGB components, including negative Z.
  float4 packed=tex2D(_BumpMap,i.uv);
  float3 geometryN=normalize(i.n),ts=_RawNormalRGB>.5?normalize(packed.xyz*2-1):UnpackNormal(packed);
  ts=normalize(lerp(float3(0,0,1),ts,saturate(_NormalStrength)));
  float3 n=normalize(normalize(i.t)*ts.x+normalize(i.b)*ts.y+geometryN*ts.z);
  float nDotL=max(0,dot(n,normalize(_LightDir.xyz)));
  if(_OutputMode>3.5)return colour;
  if(_OutputMode>2.5){float3 bakeN=normalize(float3(dot(geometryN,_BakeRight.xyz),dot(geometryN,_BakeUp.xyz),dot(geometryN,_BakeOut.xyz)));return float4(bakeN*.5+.5,colour.a);}
  if(_OutputMode>1.5)return float4(n,nDotL);
  // Display encoded data as colours; lighting never applies this conversion.
  if(_OutputMode>.5)return float4(GammaToLinearSpace(ts*.5+.5),colour.a);
  return float4(colour.rgb*(_Ambient+(1-_Ambient)*nDotL),colour.a);
 }
 ENDCG }
 }
}
