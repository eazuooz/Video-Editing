Shader "Yamyam/Teaching/LocalIllumination"
{
 Properties
 {
  _BaseColor("Diffuse reflectance", Color)=(0.55,0.55,0.55,1)
  _SpecColor("Specular reflectance",Color)=(0.9,0.9,0.9,1)
  _AmbientColor("Ambient term",Color)=(0.03,0.03,0.03,1)
  _EmissionColor("Emission term",Color)=(0,0,0,1)
  _LightColor("Light colour and intensity",Color)=(1,1,1,1)
  _SecondLightColor("Second directional light colour",Color)=(0.3,0.4,0.6,1)
  _SecondLightDirection("Second directional light direction",Vector)=(1,-1,0,0)
  _SecondLightStrength("Second directional light strength",Float)=0
  _Components("Diffuse, specular, ambient, emission",Vector)=(1,1,1,1)
  _LightPosition("Position",Vector)=(2,3,-2,1)
  _LightDirection("Direction from source",Vector)=(-0.5,-1,0.3,0)
  _ViewPosition("Teaching viewer position",Vector)=(0,2,-5,1)
  _OrthographicViewDirection("Orthographic direction toward viewer",Vector)=(0,0,-1,0)
  _UseOrthographicView("Orthographic camera",Float)=1
  _Exponent("Gloss exponent",Float)=24
  _DiffuseScale("1 legacy coefficient; 1/pi reflectance BRDF",Float)=1
  _SpecularModel("0 Phong; 1 Blinn-Phong",Float)=0
  _ShadingMode("0 per pixel; 1 face; 2 Gouraud",Float)=0
  _MaterialMapEnabled("Per-pixel material texture",Float)=0
  _MaterialMap("Original diffuse texture",2D)="white"{}
  _SpecularMap("Original specular texture",2D)="white"{}
  _LightType("0 directional; 1 point; 2 conical; 3 rectangular",Float)=0
  _Attenuation("0 none; 1 inverse square; 2 finite linear",Float)=0
  _Range("Finite range",Float)=6
  _InnerRange("Full-intensity distance",Float)=0
  _DiffuseModel("0 Lambert; 1 stylized Half-Lambert",Float)=0
  _ReferenceDistance("Inverse square reference",Float)=2
  _SpotCosines("Inner cosine, outer cosine",Vector)=(0.95,0.85,0,0)
  _UseCookie("Use projected cookie",Float)=0
  _Cookie("Gobo",2D)="white"{}
  _Falloff("One dimensional falloff map",2D)="white"{}
  _VolumeMode("0 disabled; 1 ortho; 2 perspective",Float)=0
 }
 SubShader
 {
  Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry"}
  Pass
  {
   Name "TeachingForward"
   Tags {"LightMode"="UniversalForward"}
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma target 3.5
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   CBUFFER_START(UnityPerMaterial)
    float4 _BaseColor, _SpecColor, _AmbientColor, _EmissionColor, _LightColor, _Components;
    float4 _LightPosition, _LightDirection, _ViewPosition, _SpotCosines, _SecondLightColor, _SecondLightDirection, _OrthographicViewDirection;
    float _SecondLightStrength, _UseOrthographicView, _MaterialMapEnabled;
    float _Exponent, _DiffuseScale, _DiffuseModel, _SpecularModel, _ShadingMode, _LightType, _Attenuation, _Range, _InnerRange, _ReferenceDistance, _UseCookie, _VolumeMode;
    float4x4 _WorldToLight, _LightToTexture;
   CBUFFER_END
   TEXTURE2D(_Cookie); SAMPLER(sampler_Cookie);
   TEXTURE2D(_Falloff); SAMPLER(sampler_Falloff);
   TEXTURE2D(_MaterialMap); SAMPLER(sampler_MaterialMap);
   TEXTURE2D(_SpecularMap); SAMPLER(sampler_SpecularMap);
   struct Attributes {float4 positionOS:POSITION;float3 normalOS:NORMAL;float4 color:COLOR;float2 uv:TEXCOORD0;float3 faceCentreOS:TEXCOORD2;float3 faceNormalOS:TEXCOORD3;};
   struct Varyings {float4 positionCS:SV_POSITION;float3 positionWS:TEXCOORD0;float3 normalWS:TEXCOORD1;float3 vertexColour:TEXCOORD2;nointerpolation float3 faceColour:TEXCOORD3;float2 uv:TEXCOORD4;float3 diffuseFactor:TEXCOORD5;float3 specularFactor:TEXCOORD6;};

   // This is the explicitly labelled pedagogical local model, not URP Lit/PBR.
   // Light visibility/shadows, Fresnel, anisotropy and interreflection are absent.
   void EvaluateFactors(float3 p,float3 n,out float3 diffuseFactor,out float3 specularFactor)
   {
    n=normalize(n);
    float3 delta=_LightPosition.xyz-p;
    float distanceToLight=max(length(delta),0.0001);
    float3 l=_LightType<0.5?normalize(-_LightDirection.xyz):delta/distanceToLight;
    float3 v=_UseOrthographicView>0.5?normalize(_OrthographicViewDirection.xyz):normalize(_ViewPosition.xyz-p);
    float ndotl=dot(n,l);
    float diffuse=max(0,ndotl);
    if(_DiffuseModel>0.5) diffuse=pow(saturate(0.5*ndotl+0.5),2);
    float3 r=2*ndotl*n-l;
    float3 halfSum=l+v;
    float halfLength=length(halfSum);
    float3 h=halfLength>0.0001?halfSum/halfLength:float3(0,0,0);
    float specBase=_SpecularModel<0.5?max(0,dot(r,v)):max(0,dot(n,h));
    float specular=ndotl>0?pow(specBase,max(0.0001,_Exponent)):0;
    float attenuation=1;
    if(_LightType>0.5 && _Attenuation>0.5 && _Attenuation<1.5)
      attenuation=(_ReferenceDistance*_ReferenceDistance)/max(distanceToLight*distanceToLight,0.0001);
    else if(_LightType>0.5 && _Attenuation>=1.5)
      attenuation=saturate((_Range-distanceToLight)/max(_Range-_InnerRange,0.0001));
    if(_LightType>1.5 && _LightType<2.5)
    {
      float cosTheta=dot(-l,normalize(_LightDirection.xyz));
      attenuation*=smoothstep(_SpotCosines.y,_SpotCosines.x,cosTheta);
    }
    float4 lightSpace=mul(_WorldToLight,float4(p,1));
    float4 tex=mul(_LightToTexture,lightSpace);
    // Test the projection denominator before division. Outside points still
    // retain ambient/emission, but contribute no projected direct light.
    bool projectable=tex.w>0.0001;
    float2 uv=projectable?tex.xy/tex.w:float2(-1,-1);
    if(_UseCookie>0.5 || _LightType>2.5 || _VolumeMode>0.5)
    {
      float inside=projectable?step(0,uv.x)*step(uv.x,1)*step(0,uv.y)*step(uv.y,1):0;
      if(_LightType>1.5 || _VolumeMode>1.5) inside*=step(0.0001,lightSpace.z);
      attenuation*=inside*SAMPLE_TEXTURE2D_LOD(_Cookie,sampler_Cookie,uv,0).r;
    }
    if(_VolumeMode>0.5)
    {
      // z is intentionally NOT divided by perspective w. It is the separate
      // one-dimensional falloff coordinate from the selected light volume.
      float z=tex.z;
      attenuation*=step(0,z)*step(z,1)*SAMPLE_TEXTURE2D_LOD(_Falloff,sampler_Falloff,float2(z,0.5),0).r;
    }
    // The extra source is explicitly directional. Add its direct contribution;
    // material ambient and emission are not added again for each light.
    float3 l2=normalize(-_SecondLightDirection.xyz);
    float ndotl2=dot(n,l2);
    float d2=max(0,ndotl2);
    if(_DiffuseModel>0.5)d2=pow(saturate(0.5*ndotl2+0.5),2);
    float3 r2=2*ndotl2*n-l2;
    float3 hv2=l2+v;
    float3 h2=length(hv2)>0.0001?normalize(hv2):float3(0,0,0);
    float s2=ndotl2>0?pow(max(0,_SpecularModel<0.5?dot(r2,v):dot(n,h2)),max(0.0001,_Exponent)):0;
    float3 diffuseSum=_LightColor.rgb*diffuse*attenuation+_SecondLightStrength*_SecondLightColor.rgb*d2;
    float3 specularSum=_LightColor.rgb*specular*attenuation+_SecondLightStrength*_SecondLightColor.rgb*s2;
    diffuseFactor=_Components.x*_DiffuseScale*diffuseSum+_Components.z*_AmbientColor.rgb;
    specularFactor=_Components.y*specularSum;
   }
   float3 Evaluate(float3 p,float3 n)
   {
    float3 d,s;EvaluateFactors(p,n,d,s);
    return _BaseColor.rgb*d+_SpecColor.rgb*s+_Components.w*_EmissionColor.rgb;
   }
   Varyings vert(Attributes i)
   {
    Varyings o;
    o.positionWS=TransformObjectToWorld(i.positionOS.xyz);
    o.positionCS=TransformWorldToHClip(o.positionWS);
    o.normalWS=TransformObjectToWorldNormal(i.normalOS);
    o.uv=i.uv;
    EvaluateFactors(o.positionWS,o.normalWS,o.diffuseFactor,o.specularFactor);
    o.vertexColour=Evaluate(o.positionWS,o.normalWS);
    if(_ShadingMode>3.5)o.vertexColour=i.color.rgb;
    float3 centre=TransformObjectToWorld(i.faceCentreOS);
    float3 faceNormal=TransformObjectToWorldNormal(i.faceNormalOS);
    o.faceColour=Evaluate(centre,faceNormal);
    return o;
   }
   float4 frag(Varyings i):SV_Target
   {
    float3 c;
    if(_ShadingMode>3.5)c=i.vertexColour;
    else if(_ShadingMode>2.5){
     float3 diffuseMaterial=_BaseColor.rgb*SAMPLE_TEXTURE2D(_MaterialMap,sampler_MaterialMap,i.uv).rgb;
     float3 specularMaterial=_SpecColor.rgb*SAMPLE_TEXTURE2D(_SpecularMap,sampler_SpecularMap,i.uv).rgb;
     c=diffuseMaterial*i.diffuseFactor+specularMaterial*i.specularFactor+_Components.w*_EmissionColor.rgb;
    }else if(_MaterialMapEnabled>0.5&&_ShadingMode<0.5){
     float3 d,s;EvaluateFactors(i.positionWS,i.normalWS,d,s);
     c=_BaseColor.rgb*SAMPLE_TEXTURE2D(_MaterialMap,sampler_MaterialMap,i.uv).rgb*d
       +_SpecColor.rgb*SAMPLE_TEXTURE2D(_SpecularMap,sampler_SpecularMap,i.uv).rgb*s+_Components.w*_EmissionColor.rgb;
    }else c=_ShadingMode<0.5?Evaluate(i.positionWS,i.normalWS):(_ShadingMode<1.5?i.faceColour:i.vertexColour);
    return float4(c,1);
   }
   ENDHLSL
  }
 }
}
