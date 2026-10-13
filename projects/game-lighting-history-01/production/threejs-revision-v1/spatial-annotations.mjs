import * as T from '../local/threejs-revision-v1/vendor/three.module.js';
const colors=[0x73c7c2,0xe8cf83,0xf39a4b];
const V=(x,y,z)=>new T.Vector3(x,y,z);
function line(points,color){return new T.Line(new T.BufferGeometry().setFromPoints(points),new T.LineBasicMaterial({color,transparent:true,opacity:.85}));}
function arrow(a,b,color){const d=b.clone().sub(a);return new T.ArrowHelper(d.clone().normalize(),a,d.length(),color,.15,.08);}
function dot(p,color,r=.06){const m=new T.Mesh(new T.SphereGeometry(r,12,8),new T.MeshBasicMaterial({color,depthTest:false}));m.position.copy(p);return m;}
function clear(group){for(const o of [...group.children]){group.remove(o);o.traverse(x=>{x.geometry?.dispose();for(const m of [].concat(x.material??[]))m.dispose();});}}
export function addTeachingMotion(m,q,p){
 if(!m.teaching){m.teaching=new T.Group();m.annotations.add(m.teaching);}clear(m.teaching);
 const g=m.teaching,key=p.key;
 if(m.kind==='visibility'){
  const origin=V(0,.05,-1),light=origin.clone().add(m.light.position.clone().normalize().multiplyScalar(3));
  if(key==='02-p6'){
   for(let i=0;i<5;i++){const a=i*Math.PI/5;const from=origin.clone().add(V(2.5*Math.cos(a),2,2.5*Math.sin(a)));if((q.directions??1)*5>=i+.5)g.add(arrow(from,origin,colors[i%3]));}g.add(arrow(origin,origin.clone().add(V(0,1,-3)),0xffffff));m.info=['방향별 입사광 → 재질의 반사 규칙','화살표: 계산할 방향의 설명용 표식','여러 방향의 기여를 합해 출사광 평가'];
  }else if(key==='02-p8'){
   const phase=Math.min(2,Math.floor(q.rayKind??0));const chains=[[V(4,3,-5),origin],[origin,light],[origin,V(-2,1.5,2)]];chains.forEach((c,i)=>{const a=arrow(c[0],c[1],i===phase?colors[i]:0x39484d);g.add(a);});m.info=['청록: 카메라 → 표면','노랑: 표면 → 광원','주황: 표면 → 반사 방향'];
  }else if(key==='02-p5'){
   const a=origin.clone(),b=light.clone();g.add(line([a,b],0xe8cf83));const ray=new T.Raycaster(a,b.clone().sub(a).normalize(),.02,a.distanceTo(b));const hit=ray.intersectObject(m.gate)[0];if(hit)g.add(dot(hit.point,0xf39a4b,.12));m.info=['두 벡터의 길이 = 1',`실제 검사 경로: ${hit?'광원 전에 가림체를 만남':'광원까지 통과'}`,'가림 검사는 방향 항과 별도'];
  }else if(key==='02-p2'){
   const pts=[V(-1.5,.1,-2),V(1.4,.1,-2),V(0,2,-2)];g.add(line([...pts,pts[0]],0x73c7c2));m.info=['3D 삼각형 → 카메라 화면','오른쪽: 현재 카메라의 깊이','투영/깊이 선택과 조명은 별도'];
  }else {g.add(dot(light,0xe8cf83,.12));}
 }
 if(m.kind==='depth'&&key!=='09-p2'){
  g.add(dot(m.light.position,0xe8cf83,.12));const direction=m.light.position.clone().normalize();g.add(line([m.point,m.point.clone().add(direction.multiplyScalar(7))],0xe8cf83));
 }
 if(m.kind==='sector'){
  const axis=q.axis??1;for(const walls of m.sectorWalls){walls[0].material.color.multiplyScalar(.82+.18*(1-axis));}
  if(key==='03-p6'){g.add(dot(V((q.lamp??-300)/80,3,0),0xe8cf83,.15));m.info=['표식 광원을 움직여도 구역 값은 고정','구역 값과 축 보정만 사용하는 모형','가림 검사를 수행하지 않는 구조'];}
  if(key==='03-p5'){const factor=1/(1+.15*((q.distance??1)-1));for(const ws of m.sectorWalls)for(const w of ws)w.material.color.multiplyScalar(factor);m.info=['멀어질수록 투영 크기 감소','단계적 색상표 선택을 설명하는 모형','DOOM 코드의 정확한 표 자체는 별도 자료'];}
  if(key==='03-p7')m.info=['1993: 공개 코드의 조명 구조','2024: 별도 확보한 재발매 화면','현대 추가 조명을 원본 기능으로 추정 금지'];
 }
 if(m.kind==='bake'||m.kind==='store'){
  g.add(dot(m.light.position,0xe8cf83,.13));
  if(key==='04-p2'||key==='04-p3'){
   const t=q.transfer??q.bake??0;const completed=Math.round(t*1024);for(let i=0;i<1024;i++){const v=i<completed?m.savedBytes[i*4]:40;const j=i*4;m.savedLighting.image.data[j]=m.savedLighting.image.data[j+1]=m.savedLighting.image.data[j+2]=v;}m.savedLighting.needsUpdate=true;const x=-3+6*t,point=V(x,.025,-1.5);g.add(dot(point,0xe8cf83,.1));const to=point.clone().add(V(-3,7,4).normalize().multiplyScalar(8));g.add(line([point,to],0xe8cf83));const hit=new T.Raycaster(point,to.clone().sub(point).normalize()).intersectObject(m.gate)[0];if(hit)g.add(dot(hit.point,0xf39a4b,.12));m.info=[`현재 표본의 경로: ${hit?'가려짐':'통과'}`,'밝기와 가림을 표면 격자에 기록','오른쪽: 실제 32×32 저장 결과'];
  }
  if(key==='04-p11'){
   const point=V(m.actor.position.x,.03,m.actor.position.z);g.add(arrow(m.actor.position.clone().add(V(0,1,0)),point,0xe8cf83));const x=Math.max(0,Math.min(31,Math.floor((point.x/11+.5)*32))),y=Math.max(0,Math.min(31,Math.floor((.5-point.z/11)*32)));const value=m.savedLighting.image.data[(y*32+x)*4]/255;m.actor.traverse(o=>{if(o.isMesh){o.material.color.setScalar(.25+.65*value);}});m.info=['이동 물체 아래의 저장 표본 조회',`교육용 표면 표본 = ${value.toFixed(2)}`,'Quake 원본의 공간 탐색을 단순화한 모형'];
  }
 }
 if(m.kind==='normal'&&key.startsWith('08-')&&Number(key.split('p')[1])<=5){
  const bases=[V(.816497,0,.57735),V(-.408248,.707107,.57735),V(-.408248,-.707107,.57735)];const angle=(q.angle??0)*Math.PI/180,n=V(Math.sin(angle),0,Math.cos(angle));const weights=bases.map(b=>Math.max(0,n.dot(b)));m.rnmWeights=weights;m.panels[0].position.x=-1.7;m.panels[0].scale.set(1.25,1.25,1);m.panels[1].visible=false;
  for(let i=0;i<3;i++)if((q.basis??1)*3>=i+.5)g.add(arrow(V(1.5,1.4,2),V(1.5,1.4,2).add(bases[i].clone().multiplyScalar(2)),colors[i]));g.add(arrow(V(1.5,1.4,2),V(1.5,1.4,2).add(n.clone().multiplyScalar(2.6)),0xffffff));
  m.normalArrow.visible=m.lightArrow.visible=false;m.info=weights.map((w,i)=>`대표 법선·기저 ${i+1}: max(0, n·b${i+1}) = ${w.toFixed(2)}`);
  for(const panel of m.panels){if(!panel.material.uniforms?.tilt){panel.material=new T.ShaderMaterial({side:T.DoubleSide,uniforms:{normalMap:{value:m.normalTex},tilt:{value:0}},vertexShader:'varying vec2 uv0;void main(){uv0=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:`varying vec2 uv0;uniform sampler2D normalMap;uniform float tilt;void main(){vec3 n=normalize(texture2D(normalMap,uv0).xyz*2.-1.);n=mat3(cos(tilt),0.,-sin(tilt),0.,1.,0.,sin(tilt),0.,cos(tilt))*n;float w0=max(0.,dot(n,vec3(.816497,0.,.57735))),w1=max(0.,dot(n,vec3(-.408248,.707107,.57735))),w2=max(0.,dot(n,vec3(-.408248,-.707107,.57735)));vec3 c=.5*(w0*vec3(.451,.78,.761)+w1*vec3(.91,.812,.514)+w2*vec3(.953,.604,.294));gl_FragColor=vec4(c,1.);\n#include <colorspace_fragment>\n}`});}panel.material.uniforms.tilt.value=angle;}
 }
 if(m.kind==='normal'&&key==='08-p10'){m.info=['동적 직접광: 켬 → 끔','남아 있는 환경 항: 고정된 교육용 값','정적 간접광 저장의 갱신 문제를 분리'];}
 if(m.kind==='cascade'){
  m.splits.visible=false;const split=q.split??1;const count=split<.5?1:Math.max(0,Math.min(3,Math.round(q.maps??3)));const z=[-5,0,7,17],origin=V(0,2,-8);
  for(let k=0;k<count;k++){const near=count===1?z[0]:z[k],far=count===1||k===count-1?z[3]:z[k+1],corners=[];for(const d of [near,far]){const distance=d+8,half=distance*.32;corners.push(V(-half,.03,d),V(half,.03,d),V(half,2+distance*.25,d),V(-half,2+distance*.25,d));}const vertices=[];for(const[a,b]of[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]])vertices.push(corners[a],corners[b]);g.add(new T.LineSegments(new T.BufferGeometry().setFromPoints(vertices),new T.LineBasicMaterial({color:colors[k]})));}
  g.add(dot(origin,0xffffff,.16));const sampleZ=3+(q.sample??-330)/35;g.add(dot(V(0,.1,sampleZ),0xe8cf83,.13));const which=sampleZ<0?1:sampleZ<7?2:3;m.info=[`같은 광원 / 카메라 구간 ${count}개`,`노란 검사점 → 구간 ${which}의 맵 선택`,'색 프러스텀은 원리 설명 · 실측 CSM 아님'];
 }
 if(m.kind==='volume'){
  const receiver=V(.4,.1,-1.6+(q.receiverY??0)/80);g.add(dot(receiver,0xe8cf83,.1));const camera=V(4,3,-5).lerp(V(0,1.8,-2),q.cameraInside??0);g.add(dot(camera,0xffffff,.1),line([camera,receiver],0xffffff));m.volumeGroup.updateMatrixWorld(true);const d=receiver.clone().sub(camera),hits=new T.Raycaster(camera,d.clone().normalize(),.001,d.length()).intersectObject(m.volumeGroup);m.volumeIntersections=hits.filter((h,i)=>!i||Math.abs(h.distance-hits[i-1].distance)>.001).map(h=>({distance:h.distance,point:h.point.toArray()}));m.volumePathLength=d.length();for(const h of m.volumeIntersections)g.add(dot(new T.Vector3(...h.point),0xf39a4b,.09));if(key==='07-p7')m.info=['흰 선: 카메라 → 표면 검사 경로',`닫힌 모형과의 실제 경계 교차 ${m.volumeIntersections.length}회`,'스텐실 알고리즘 설명 · 스텐실 버퍼 실측 아님'];
 }
 if(m.kind==='pipeline'){
  if(!m.pointLights){m.pointLights=[];for(let i=0;i<3;i++){const l=new T.PointLight(colors[i],18,7,2);l.position.set(-3+i*3,3,-1);m.scene.add(l);m.pointLights.push(l);}}
  m.light.intensity=0;const count=q.lights??2;m.pointLights.forEach((l,i)=>{l.intensity=i<count?18:0;if(l.intensity)g.add(dot(l.position,colors[i],.12));});
  m.info=q.path===1?['기하 패스: 깊이 · 법선 · 기본색','그다음 조명 기여를 평가하는 순서','버퍼는 실제 출력 / 처리 순서는 교육 도식']:['표면을 그리는 중 재질·광원 평가',`현재 모형의 활성 광원 ${Math.ceil(count)}개`,'투명체는 별도 합성이 필요'];
 }
 if(m.kind==='ao'){
  const radius=(q.radius??120)/100,center=V(-.4,.05,-.5);for(let i=0;i<16;i++){const a=i*2.39996,z=(i+.5)/16,r=Math.sqrt(1-z*z),v=V(Math.cos(a)*r,z,Math.sin(a)*r).multiplyScalar(radius).add(center);g.add(dot(v,0x73c7c2,.035));}m.marker.visible=false;
 }
}
