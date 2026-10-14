import {SpatialModel} from '../threejs-revision-v1/spatial-models.mjs';
import {overlay} from '../threejs-revision-v1/teaching-overlay.mjs';
import {addTeachingMotion} from '../threejs-revision-v1/spatial-annotations.mjs';
import {diagramKeys,drawDiagram,drawCaption,label} from './lesson-overlays.mjs';
export class BeginnerLesson {
 constructor(output,spatial){this.output=output;this.ctx=output.getContext('2d');this.model=new SpatialModel(spatial);}
 draw(p,row,frame,block,caption=null){
  const ctx=this.ctx,m=this.model,t=frame/Math.max(1,block.frames-1);
  const a=block.actionStartFrame,z=block.actionEndFrame;
  const u=Math.max(0,Math.min(1,(frame-a)/Math.max(1,z-a))),q={...p.from};
  for(const [k,v] of Object.entries(p.to))q[k]=(p.from[k]??0)+(v-(p.from[k]??0))*u;
  ctx.fillStyle='black';ctx.fillRect(0,0,1920,1080);
  const text=(s,x,y,size=32,color='#f5f5f5',align='left')=>label(ctx,s,x,y,size,color,align);
  const fit=(s,x,y,w,size,color)=>{ctx.font=`500 ${size}px 'Noto Sans KR','Malgun Gothic'`;while(ctx.measureText(s).width>w&&size>24)ctx.font=`500 ${--size}px 'Noto Sans KR','Malgun Gothic'`;label(ctx,s,x,y,size,color);};
  fit(row.screenLabel,960,65,1730,46,'#e8cf83');
  if(diagramKeys.has(p.key)){
   label(ctx,'원리와 작업 순서를 풀어 쓴 설명 도식',960,108,25,'#aaa');drawDiagram(ctx,p.key,u);
  }else{
   m.setPose(p.model,q,p);m.scene.updateMatrixWorld(true);
   if(p.key==='02-p5')addTeachingMotion(m,q,p);
   const result=m.render();
   label(ctx,'직접 만든 3D 설명 · 실제 출력과 설명용 표식을 구별',960,108,25,'#aaa');
   ctx.drawImage(m.r.domElement,90,140,1728,650);
   if(p.model==='pipeline'){
    const forward=p.key==='09b-p1';
    const stage=block.stageFrames?block.stageFrames.filter(x=>x<=frame).length-1:Math.min(2,Math.floor(t*3));
    // A shared NDC position links the full scene to its three real buffers.
    // This marker identifies a sample location; it is not a performance counter.
    const wall=m.extra.children[0];
    const sample=wall.localToWorld(wall.position.clone().set(1.04,1.1,-.04)).project(m.camera);
    const su=(sample.x+1)/2,sv=(1-sample.y)/2;
    const marks=[[90+su*1100,140+sv*650],[1278+su*240,258+sv*142],[1533+su*240,258+sv*142],[1278+su*240,448+sv*142]];
    for(const [x,y] of (forward?marks.slice(0,1):marks)){
     ctx.strokeStyle='#fff';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(x-9,y);ctx.lineTo(x+9,y);ctx.moveTo(x,y-9);ctx.lineTo(x,y+9);ctx.stroke();
    }
    label(ctx,'같은 화면 위치를 따라갑니다',655,751,29,'#e8cf83');
    if(forward){
     // Forward shading must not appear to write a G-buffer. These boxes
     // describe work performed for the marked surface, not measured buffers.
     ctx.fillStyle='black';ctx.fillRect(1274,140,544,650);
     label(ctx,'표시한 표면에서 이어서 계산',1540,193,28,'#e8cf83');
     for(const [i,s] of ['표면의 재질','관련 조명의 빛','현재 픽셀의 색'].entries()){
      ctx.fillStyle=i===stage?'#203c39':'#161616';ctx.fillRect(1304,240+i*145,464,88);
      label(ctx,s,1536,294+i*145,34,i===stage?'#fff':'#aaa');
      if(i<2)label(ctx,'↓',1536,367+i*145,32,'#e8cf83');
     }
     label(ctx,'작업 순서 도식 · 저장 버퍼 그림 아님',1540,728,23,'#aaa');
    }else{
     label(ctx,'기본색',1404,427,25,'#e8cf83');label(ctx,'표면 방향',1658,427,25,'#73c7c2');label(ctx,'깊이',1404,627,25,'#f39a4b');
     ctx.fillStyle='black';ctx.fillRect(1274,140,544,80);label(ctx,'같은 장면의 표면 정보',1540,181,30,'#e8cf83');
    }
    const stepSets={
     '09b-p1':['① 보이는 표면','② 재질 + 관련 조명','③ 픽셀 색'],
     '09b-p2':['① 보이는 표면','② 정보 메모 (G-buffer)','③ 조명이 메모 읽기'],
     '09b-p3':['① 재료의 기본색','② 방향과 거칠기','③ 저장하는 기준 구별'],
     '09b-p5':['① 조명의 영향 범위','② 닿지 않는 곳 제외','③ 두 방식에 모두 적용'],
     '09b-p7':['① 표면 정보 쓰기','② 다음 작업에서 읽기','③ 한 겹만 기록하는 한계'],
     '09b-p9':['① 패스 = 작업 한 차례','② 불투명 + 별도 유리','③ 다른 절충도 존재'],
    };
    const steps=stepSets[p.key]??['① 보이는 표면','② 정보 메모 (G-buffer)','③ 조명이 메모 읽기'];
    for(let i=0;i<3;i++){const x=110+i*575,active=i===stage;ctx.fillStyle=active?'#203c39':'#171717';ctx.fillRect(x,798,535,59);fit(steps[i],x+267,839,515,30,active?'#fff':'#bbb');if(i<2)label(ctx,'→',x+547,839,29,'#e8cf83');}
    label(ctx,forward?'이 표면의 재질과 빛을 함께 계산하는 순서':'작업 순서 도식 · 버퍼 이미지는 이 3D 모형에서 생성',960,887,24,'#aaa');
   }else{
    overlay(ctx,m,p,q,text);
    if(p.key==='02-p5')label(ctx,result.labels[1],960,765,32,'#e8cf83');
    fit(p.expression,960,829,1710,34,'#eee');fit(p.limit,960,873,1730,25,'#aaa');
   }
  }
  if(caption)drawCaption(ctx,caption);
  return {key:p.key,frame,frames:block.frames,pose:q,actionProgress:u,implementation:diagramKeys.has(p.key)?'educational-diagram':'actual-three-model-with-labeled-illustration'};
 }
}
