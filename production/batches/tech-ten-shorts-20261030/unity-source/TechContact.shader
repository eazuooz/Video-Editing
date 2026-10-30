Shader "Yamyam/TechTen/ContactCapture" {
 SubShader { Pass {Cull Off ZWrite On
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 float4 vert(appdata_base v):SV_POSITION{return UnityObjectToClipPos(v.vertex);}
 fixed4 frag():SV_Target{return fixed4(1,1,1,1);}
 ENDCG
 } }
}
