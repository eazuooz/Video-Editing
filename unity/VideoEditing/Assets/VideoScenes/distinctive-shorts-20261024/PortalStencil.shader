Shader "Yamyam/DistinctivePortalStencil" {Properties{_MainTex("Recursive camera view",2D)="black"{} _MaskOnly("Inspect mask",Float)=0}
 SubShader{Tags{"Queue"="Geometry+20"} Cull Off
 Pass{ColorMask 0 ZWrite Off Stencil{Ref 1 Comp Always Pass Replace}
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 struct v2f{float4 p:SV_POSITION;float2 uv:TEXCOORD0;};v2f vert(appdata_base v){v2f o;o.p=UnityObjectToClipPos(v.vertex);o.uv=v.texcoord;return o;}fixed4 frag(v2f i):SV_Target{clip(1-dot(i.uv*2-1,i.uv*2-1));return 0;}
 ENDCG}
 Pass{ZWrite On Stencil{Ref 1 Comp Equal Pass Keep}
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 struct v2f{float4 p:SV_POSITION;float2 uv:TEXCOORD0;float4 screen:TEXCOORD1;};sampler2D _MainTex;float _MaskOnly;
 v2f vert(appdata_base v){v2f o;o.p=UnityObjectToClipPos(v.vertex);o.uv=v.texcoord;o.screen=ComputeScreenPos(o.p);return o;}
 fixed4 frag(v2f i):SV_Target{clip(1-dot(i.uv*2-1,i.uv*2-1));return lerp(tex2Dproj(_MainTex,UNITY_PROJ_COORD(i.screen)),fixed4(.45,.84,.80,1),_MaskOnly);}
 ENDCG}}
}
