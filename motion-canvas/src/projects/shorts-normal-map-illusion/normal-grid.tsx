import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {Vector2} from '@motion-canvas/core';

type GridOptions={record:()=>any;elapsed:()=>number;enabled:()=>boolean;point:(p:any)=>Vector2;};
const WHITE='#FFFFFF',GREEN='#92DF9C',MUTED='#B8C3BC';
export function createNormalGrid({record,elapsed,enabled,point}:GridOptions){
 const root=new Node({opacity:()=>enabled()?1:0});
 const samples=()=>record()?.normalGrid??[];
 const colour=()=>Number(record()?.normalStrength??1)<.5?WHITE:GREEN;
 for(let i=0;i<63;i++){
  const sample=()=>samples()[i];
  const positions=()=>sample()?[point(sample().screenPoint),point(sample().gridNormalScreenEnd)]:[new Vector2(0,0),new Vector2(0,0)];
  const length=()=>positions()[1].sub(positions()[0]).magnitude;
  const shown=()=>enabled()&&!!sample()&&elapsed()>(Math.floor(i/9)*.07)?1:0;
  // A near-camera-facing vector really projects to a short mark. Keep that
  // measured projection; show a dot instead of inventing a longer direction.
  root.add(<Line points={positions} stroke="#000000" lineWidth={8} endArrow arrowSize={14} opacity={()=>shown()&&length()>=7?1:0}/>);
  root.add(<Line points={positions} stroke={colour} lineWidth={4} endArrow arrowSize={10} opacity={()=>shown()&&length()>=7?1:0}/>);
  root.add(<Circle position={()=>positions()[0]} width={9} height={9} fill={colour} stroke="#000000" lineWidth={3} opacity={()=>shown()&&length()<7?1:0}/>);
 }
 root.add(<Txt text="대표 픽셀 63곳의 방향" position={[-190,-390]} fontFamily="Malgun Gothic" fontSize={34} fontWeight={700} fill={colour}/>);
  root.add(<Txt text="일부 지점만 표시 · 화살표 길이는 보기용" position={[-100,-355]} fontFamily="Malgun Gothic" fontSize={28} fill={MUTED}/>);
 return root;
}
