// Beginner scaffolding. Diagrams below describe work order, not measured GPU internals.
const C={ink:'#f5f5f5',gold:'#e8cf83',teal:'#73c7c2',orange:'#f39a4b',muted:'#aaa'};
export function label(ctx,t,x,y,size=32,color=C.ink,align='center'){
 ctx.font=`500 ${size}px 'Noto Sans KR','Malgun Gothic',sans-serif`;ctx.textAlign=align;ctx.fillStyle=color;ctx.fillText(t,x,y);
}
function card(ctx,x,y,w,h,title,body,color=C.teal){ctx.fillStyle='#141a1c';ctx.fillRect(x,y,w,h);ctx.strokeStyle=color;ctx.lineWidth=3;ctx.strokeRect(x,y,w,h);label(ctx,title,x+w/2,y+55,34,color);body.forEach((s,i)=>label(ctx,s,x+w/2,y+115+i*51,30));}
function arrow(ctx,x1,y1,x2,y2,color=C.gold){const a=Math.atan2(y2-y1,x2-x1);ctx.strokeStyle=color;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x2,y2);ctx.lineTo(x2-18*Math.cos(a-.5),y2-18*Math.sin(a-.5));ctx.lineTo(x2-18*Math.cos(a+.5),y2-18*Math.sin(a+.5));ctx.fill();}
export const diagramKeys=new Set(['03-p2','04t-p3','04t-p4','04t-p6','09-p9','09b-p4']);
export function drawDiagram(ctx,key,u){
 if(key==='03-p2'){
  label(ctx,'벽 무늬는 유지 · 골라 읽는 색 목록을 바꿈',960,210,42,C.gold);
  for(let side=0;side<2;side++){let cx=240+side*850;label(ctx,side?'밝은 색상표':'어두운 색상표',cx+295,280,38,side?C.gold:C.teal);for(let y=0;y<6;y++)for(let x=0;x<8;x++){ctx.fillStyle=(x+y)%2?(side?'#c1a879':'#524534'):(side?'#e5cf9b':'#73614a');ctx.fillRect(cx+x*73,320+y*50,69,46);}label(ctx,'같은 무늬, 다른 색 목록',cx+295,685,31);}
  arrow(ctx,850,475,1020,475);label(ctx,'구역 밝기 → 단계 번호 → 색상표 선택',960,798,40,C.teal);
  label(ctx,'교육용 색상표 비교 · DOOM 원본 팔레트 자체는 아님',960,860,25,C.muted);
 }else if(key==='04t-p3'){
  card(ctx,120,280,500,310,'멀리 있는 메모리',['큰 장면의 자료','접근할 때 이동 비용']);card(ctx,795,280,420,310,'칩 안 가까운 공간',['지금 타일의 자료','이곳에서 집중 처리']);card(ctx,1390,280,410,310,'완성 타일',['작은 영역 결과','마지막에 내보냄']);
  arrow(ctx,640,445,770,445,u<.55?C.gold:C.muted);arrow(ctx,1235,445,1365,445,u>=.55?C.gold:C.muted);
  label(ctx,'타일 = 화면을 나눈 작은 구역',960,720,42,C.teal);label(ctx,'자료 이동의 원리 도식 · GPU 전송량 실측 아님',960,853,27,C.muted);
 }else if(key==='04t-p4'||key==='04t-p6'){
  card(ctx,140,240,700,340,'1 · 무엇이 보이나?',['앞쪽의 불투명 벽','완전히 가려진 뒤쪽 물체']);card(ctx,1080,240,700,340,'2 · 필요한 표면의 색 계산',['색과 밝기를 계산 = 셰이딩','가려진 불투명 면은 생략 가능']);arrow(ctx,870,415,1040,415);
  label(ctx,key==='04t-p4'?'TBDR: 보이는 면을 먼저 고른 뒤 셰이딩':'유리·구멍이 있는 재질은 별도 처리 필요',960,690,41,C.gold);
  label(ctx,key==='04t-p4'?'뒤에서 배울 Deferred Shading과 미루는 작업이 다릅니다.':'타일 여부 하나만으로 성능을 단정할 수 없습니다.',960,780,34,C.teal);
  label(ctx,'작업 순서를 설명하는 도식 · 특정 GPU 구현의 측정 화면 아님',960,858,25,C.muted);
 }else if(key==='09b-p4'){
  label(ctx,'같은 벽 · 같은 픽셀 · 같은 두 조명',960,207,42,C.gold);
  card(ctx,170,265,690,210,'조명 A',['재질을 반영한 몫 0.25'],C.teal);card(ctx,1060,265,690,210,'조명 B',['재질을 반영한 몫 0.35'],C.orange);
  label(ctx,u<.25?'두 조명의 몫을 더합니다.':'0.25 + 0.35 = 0.60',960,545,54,C.ink);
  card(ctx,170,615,690,174,'Forward',['표면을 그리면서 합산'],C.teal);card(ctx,1060,615,690,174,'Deferred',['표면 정보를 쓴 뒤 합산'],C.orange);
  label(ctx,'설명용 수치 · 최종 표시 색에는 톤매핑 등 후속 처리가 있음',960,858,25,C.muted);
 }else if(key==='09-p9'){
  card(ctx,140,250,760,390,'PCSS',['막는 물체를 먼저 찾음','받는 면과의 관계로 필터 범위 조절','넓은 범위는 부드럽지만 비용 증가'],C.teal);
  card(ctx,1020,250,760,390,'Variance Shadow Map',['깊이의 평균과 제곱 평균 저장','통계값으로 가림을 어림','필터링 가능 · 빛샘에 주의'],C.orange);
  label(ctx,'각 기법이 저장하는 정보와 근사 방식이 다릅니다.',960,750,38,C.gold);label(ctx,'원리 비교 도식 · 실제 PCSS / VSM 렌더 결과 아님',960,854,27,C.muted);
 }
}
export function drawCaption(ctx,text){
 ctx.font="500 48px 'Noto Sans KR','Malgun Gothic'";let lines=[],line='';for(const word of text.split(' ')){const next=(line+' '+word).trim();if(line&&ctx.measureText(next).width>1570){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);if(lines.length>2)throw Error('Split this caption at an actual speech boundary');
 const w=Math.ceil(Math.max(...lines.map(l=>ctx.measureText(l).width)))+44,h=62*lines.length+22,x=960-w/2,y=970-h/2;
 ctx.fillStyle='#073c32';ctx.fillRect(x+14,y+14,w,h);ctx.fillStyle='#161b18';ctx.fillRect(x-1.5,y-1.5,w+3,h+3);ctx.fillStyle='white';ctx.fillRect(x,y,w,h);
 ctx.textBaseline='middle';lines.forEach((l,i)=>label(ctx,l,960,970+(i-(lines.length-1)/2)*62,48,'#080b09'));ctx.textBaseline='alphabetic';
}
