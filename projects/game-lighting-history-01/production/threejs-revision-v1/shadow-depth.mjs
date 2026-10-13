import * as T from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';

// True 3D representative scene. The right panel is a real orthographic depth
// pass; numeric values are read back from its float framebuffer, not invented.
const canvas=document.getElementById('render');
const stage=document.getElementById('stage');
const wrap=document.getElementById('wrap');
const range=document.getElementById('occluder');
const mode=document.getElementById('mode');
const play=document.getElementById('play');
const fit=()=>{stage.style.transform=`scale(${wrap.clientWidth/1920})`;};
new ResizeObserver(fit).observe(wrap);fit();
try {
 const r=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
 r.setPixelRatio(1);r.setSize(1740,570,false);
 r.shadowMap.enabled=true;r.shadowMap.type=T.PCFShadowMap;
 r.outputColorSpace=T.SRGBColorSpace;r.toneMapping=T.NoToneMapping;
 if(!r.extensions.has('EXT_color_buffer_float'))throw Error('실제 깊이 읽기를 위한 float framebuffer를 지원하지 않습니다.');
 const scene=new T.Scene();scene.background=new T.Color(0x000000);
 const camera=new T.PerspectiveCamera(40,1160/570,.1,60);
 camera.position.set(9,7,-10);camera.lookAt(0,.5,0);
 const sun=new T.DirectionalLight(0xfff1c5,3);sun.position.set(-3,7,4);sun.target.position.set(0,0,0);sun.castShadow=true;
 const sc=sun.shadow.camera;Object.assign(sc,{left:-5,right:5,top:5,bottom:-5,near:.5,far:20});sc.updateProjectionMatrix();sun.shadow.mapSize.set(1024,1024);sun.shadow.bias=-.0003;
 scene.add(sun,sun.target,new T.AmbientLight(0xffffff,.2));
 const objects=new T.Group();scene.add(objects);
 const material=color=>new T.MeshStandardMaterial({color,roughness:.9,metalness:0});
 const floor=new T.Mesh(new T.PlaneGeometry(10,9),material(0x84999e));floor.rotation.x=-Math.PI/2;floor.receiveShadow=true;objects.add(floor);
 const occluder=new T.Group();objects.add(occluder);
 // A recognizable masonry arch, rather than an anonymous cube labeled a person.
 const arch=new T.Shape();arch.moveTo(-1.3,0);arch.lineTo(-1.3,2.9);arch.lineTo(1.3,2.9);arch.lineTo(1.3,0);arch.lineTo(.78,0);arch.lineTo(.78,1.45);arch.absarc(0,1.45,.78,0,Math.PI,false);arch.lineTo(-.78,0);arch.closePath();
 const mesh=new T.Mesh(new T.ExtrudeGeometry(arch,{depth:.55,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:.04,bevelThickness:.04}),material(0xbba479));mesh.position.z=-.25;mesh.castShadow=true;mesh.receiveShadow=true;occluder.add(mesh);
 for(const x of [-1.05,1.05])for(let y=.15;y<2.8;y+=.48){const seam=new T.Mesh(new T.BoxGeometry(.5,.025,.59),material(0x665b46));seam.position.set(x,y,.025);occluder.add(seam);}
 const lightCamera=new T.OrthographicCamera(-5,5,5,-5,.5,20);lightCamera.position.copy(sun.position);lightCamera.lookAt(0,0,0);lightCamera.updateMatrixWorld(true);
 const point=new T.Vector3(.65,.018,-1.15);
 const marker=new T.Mesh(new T.SphereGeometry(.10,20,12),new T.MeshBasicMaterial({color:0xffd666}));marker.position.copy(point);scene.add(marker);
 const lightRayEnd=point.clone().add(sun.position.clone().normalize().multiplyScalar(5.2));
 const lamp=new T.Mesh(new T.SphereGeometry(.15,16,10),new T.MeshBasicMaterial({color:0xffd666}));lamp.position.copy(lightRayEnd);scene.add(lamp);
 const ray=new T.Line(new T.BufferGeometry().setFromPoints([lightRayEnd,point]),new T.LineDashedMaterial({color:0xe8cf83,dashSize:.17,gapSize:.11,transparent:true,opacity:.65}));ray.computeLineDistances();scene.add(ray);
 const depthTarget=new T.WebGLRenderTarget(512,512,{type:T.FloatType,minFilter:T.NearestFilter,magFilter:T.NearestFilter,depthBuffer:true});
 const depthMaterial=new T.ShaderMaterial({vertexShader:'void main(){gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'void main(){gl_FragColor=vec4(vec3(gl_FragCoord.z),1.0);}',toneMapped:false});
 const normalMaterial=new T.MeshNormalMaterial();
 const depthScene=new T.Scene();depthScene.background=new T.Color(0xffffff);
 const displayScene=new T.Scene();
 const displayMaterial=new T.ShaderMaterial({uniforms:{map:{value:depthTarget.texture},uvPoint:{value:new T.Vector2()}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.0,1.0);}',fragmentShader:'uniform sampler2D map;uniform vec2 uvPoint;varying vec2 vUv;void main(){float z=texture2D(map,vUv).r;vec3 c=vec3(z);vec2 d=abs(vUv-uvPoint);if((d.x<.003&&d.y<.025)||(d.y<.003&&d.x<.025))c=vec3(1.0,.65,.12);gl_FragColor=vec4(c,1.0);}',toneMapped:false});
 displayScene.add(new T.Mesh(new T.PlaneGeometry(2,2),displayMaterial));
 const displayCamera=new T.Camera();
 const pixels=new Float32Array(4);let frameCount=0;let playing=false,start=0;
 function render(){
  occluder.position.x=Number(range.value);objects.updateMatrixWorld(true);
  depthScene.add(objects);depthScene.overrideMaterial=depthMaterial;
  r.setScissorTest(false);r.setRenderTarget(depthTarget);r.setViewport(0,0,512,512);r.render(depthScene,lightCamera);
  const p=point.clone().project(lightCamera);const u=p.x*.5+.5,v=p.y*.5+.5,z=p.z*.5+.5;
  r.readRenderTargetPixels(depthTarget,Math.max(0,Math.min(511,Math.floor(u*512))),Math.max(0,Math.min(511,Math.floor(v*512))),1,1,pixels);
  if(!Number.isFinite(pixels[0]))throw Error('깊이 패스 읽기 실패');
  scene.add(objects);
  const originals=[];if(mode.value==='normal')objects.traverse(o=>{if(o.isMesh){originals.push([o,o.material]);o.material=normalMaterial;}});
  document.querySelector('.label.left').textContent=mode.value==='normal'?'관찰자 시점 · 실제 뷰 공간 법선 색':'관찰자 시점 · 노란 점 P가 빛을 받는가?';
  r.setRenderTarget(null);r.setScissorTest(true);r.setViewport(0,0,1160,570);r.setScissor(0,0,1160,570);r.render(scene,camera);
  for(const [o,material]of originals)o.material=material;
  displayMaterial.uniforms.uvPoint.value.set(u,v);r.setViewport(1220,30,510,510);r.setScissor(1220,30,510,510);r.render(displayScene,displayCamera);
  r.setScissorTest(false);
  const screenPoint=point.clone().project(camera);
  const label=document.getElementById('point-label');label.style.left=`${90+(screenPoint.x*.5+.5)*1160+14}px`;label.style.top=`${210+(1-(screenPoint.y*.5+.5))*570-28}px`;
  const blocked=z>pixels[0]+.001;
  document.getElementById('readout').textContent=`P 깊이 ${z.toFixed(3)}  ${blocked?'>':'≤'}  저장 깊이 ${pixels[0].toFixed(3)} + 보정 0.001   →   ${blocked?'가려짐':'빛을 받음'}`;
  canvas.dataset.renderer=`Three.js r${T.REVISION}`;canvas.dataset.frame=String(++frameCount);canvas.dataset.depthResult=blocked?'shadow':'lit';canvas.dataset.storedDepth=String(pixels[0]);canvas.dataset.pointDepth=String(z);
 }
 function tick(t){if(!playing)return;range.value=String(2*Math.sin((t-start)/2200));render();requestAnimationFrame(tick);}
 range.addEventListener('input',render);mode.addEventListener('change',render);
 play.onclick=()=>{playing=!playing;play.textContent=playing?'동작 멈춤':'동작 재생';if(playing){start=performance.now();requestAnimationFrame(tick);}};
 document.getElementById('reset').onclick=()=>{playing=false;play.textContent='동작 재생';range.value='0';mode.value='shadow';render();};
 document.addEventListener('visibilitychange',()=>{if(document.hidden){playing=false;play.textContent='동작 재생';}});
 render();
}catch(e){document.getElementById('error').hidden=false;document.getElementById('error').textContent=String(e);throw e;}
