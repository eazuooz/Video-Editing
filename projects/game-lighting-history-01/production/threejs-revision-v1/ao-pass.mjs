import * as T from '../local/threejs-revision-v1/vendor/three.module.js';
// Teaching SSAO implementation: 16 deterministic hemisphere samples in view
// space, projected into the current depth buffer. No off-screen geometry.
export class AoPass {
 constructor(){
  this.target=new T.WebGLRenderTarget(512,512);
  this.beauty=new T.WebGLRenderTarget(1100,650);
  const samples=[];for(let i=0;i<16;i++){const z=(i+.5)/16,a=i*2.39996323,r=Math.sqrt(1-z*z),scale=.1+.9*((i+1)/16)**2;samples.push(new T.Vector3(Math.cos(a)*r,Math.sin(a)*r,z).multiplyScalar(scale));}
  this.material=new T.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{depth:{value:null},normals:{value:null},projection:{value:new T.Matrix4()},inverseProjection:{value:new T.Matrix4()},samples:{value:samples},radius:{value:1},amount:{value:1},blur:{value:0}},vertexShader:'varying vec2 uv0; void main(){uv0=uv;gl_Position=vec4(position.xy,0.,1.);}',fragmentShader:`
varying vec2 uv0; uniform sampler2D depth,normals; uniform mat4 projection,inverseProjection;uniform vec3 samples[16];uniform float radius,amount,blur;
vec3 positionAt(vec2 uv){float z=texture2D(depth,uv).r;vec4 p=inverseProjection*vec4(uv*2.-1.,z*2.-1.,1.);return p.xyz/p.w;}
float aoAt(vec2 uv){if(texture2D(depth,uv).r>.99999)return 1.;vec3 p=positionAt(uv),n=normalize(texture2D(normals,uv).xyz*2.-1.);vec3 tangent=normalize(cross(abs(n.z)<.9?vec3(0,0,1):vec3(0,1,0),n));mat3 basis=mat3(tangent,cross(n,tangent),n);float blocked=0.,valid=0.;for(int i=0;i<16;i++){vec3 s=p+basis*samples[i]*radius;vec4 clip=projection*vec4(s,1.);vec2 v=clip.xy/clip.w*.5+.5;if(v.x<0.||v.y<0.||v.x>1.||v.y>1.)continue;valid+=1.;vec3 actual=positionAt(v);float range=smoothstep(0.,1.,radius/max(.001,abs(p.z-actual.z)));blocked+=(actual.z>=s.z+.025?1.:0.)*range;}return 1.-amount*blocked/max(1.,valid);}
void main(){float a=aoAt(uv0);if(blur>.01){float z=positionAt(uv0).z,sum=a,w=1.;for(int i=0;i<4;i++){vec2 d=i==0?vec2(1,0):i==1?vec2(-1,0):i==2?vec2(0,1):vec2(0,-1);vec2 v=uv0+d/256.;float weight=exp(-abs(positionAt(v).z-z)*8.);sum+=aoAt(v)*weight;w+=weight;}a=mix(a,sum/w,blur);}gl_FragColor=vec4(vec3(a),1.);}`});
  this.scene=new T.Scene();this.camera=new T.Camera();this.scene.add(new T.Mesh(new T.PlaneGeometry(2,2),this.material));
  this.composite=new T.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{beauty:{value:this.beauty.texture},ao:{value:this.target.texture}},vertexShader:'varying vec2 uv0;void main(){uv0=uv;gl_Position=vec4(position.xy,0,1);}',fragmentShader:'varying vec2 uv0;uniform sampler2D beauty,ao;void main(){vec3 c=texture2D(beauty,uv0).rgb;float a=texture2D(ao,uv0).r;gl_FragColor=vec4(c*a,1.);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}'});
  this.compositeScene=new T.Scene();this.compositeScene.add(new T.Mesh(new T.PlaneGeometry(2,2),this.composite));
 }
 render(r,scene,camera,depth,normals,q){const u=this.material.uniforms;u.depth.value=depth;u.normals.value=normals;u.projection.value.copy(camera.projectionMatrix);u.inverseProjection.value.copy(camera.projectionMatrixInverse);u.radius.value=(q.radius??120)/100;u.amount.value=q.amount??.85;u.blur.value=q.filter??0;r.setScissorTest(false);r.setRenderTarget(this.target);r.setViewport(0,0,512,512);r.render(this.scene,this.camera);r.setRenderTarget(this.beauty);r.setViewport(0,0,1100,650);r.render(scene,camera);r.setRenderTarget(null);r.setScissorTest(true);r.setViewport(0,0,1100,650);r.setScissor(0,0,1100,650);r.render(this.compositeScene,this.camera);}
}
